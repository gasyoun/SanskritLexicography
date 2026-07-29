#!/usr/bin/env python
r"""rv_pipeline_bridge.py -- the judge witness and the contradiction gate (H1844 C5,
IMPLEMENTATION steps 12-13; deliverables W1.10 and W1.11).

Two integration points of ruling R7, implemented as PURE FUNCTIONS over the committed
spine plus a CLI, deliberately NOT spliced into the live judge prompt path in this pass.
Scoping decision, logged in `docs/DECISIONS_LOG_rv_multitranslation.md`: a concurrent
Codex session is active on the pipeline (`codex/rt-pipeline-hardening-speed`, risk K7), and
PLAN Sec.4's rule for an unanticipated fork is to take the option that "writes less,
asserts less, and leaves the existing pipeline unchanged". A tested function plus a named
call site is that option; editing the prompt assembler underneath another live session is
not. `witness_block_for_headword` is the call site the judge path consumes when it lands.

**Layer B is deliberately absent from both.** Its gold precision came in at de 29.2 % /
ru 19.2 % / en 10.5 % against an 85 % bar, so R14's marked default excludes it from the
contradiction gate. Both functions here read spine A only.

  python src/rv_pipeline_bridge.py witness --id-pwg 349
  python src/rv_pipeline_bridge.py gate --id-pwg 349 --gloss "огонь, жертвенный огонь"
  python src/rv_pipeline_bridge.py selftest
"""
import argparse
import collections
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT_ROOT = os.path.normpath(os.path.join(HERE, '..'))
PWG_RU_DIR = os.path.join(RT_ROOT, 'pwg_ru')

STANZA_PATH = os.path.join(PWG_RU_DIR, 'rv_stanza_translations.jsonl')
LEMMA_PATH = os.path.join(PWG_RU_DIR, 'rv_lemma_occurrences.jsonl')

TRANSLATORS = [
    'grassmann_de_1876', 'geldner_de_1951', 'elizarenkova_ru_1989', 'griffith_en_1896',
]

# Marked default, IMPLEMENTATION step 12: N = 3 loci, chosen by descending corpus
# frequency of the lemma.
WITNESS_N = 3

WORD_RE = re.compile(r'[^\W\d_]+', re.UNICODE)
MIN_CONTENT_LEN = 4     # shorter tokens are function words across de/ru/en alike


def content_tokens(text):
    """Lowercased content tokens. Deliberately crude: the gate below must be QUIET, and a
    crude overlap test errs toward finding overlap, i.e. toward NOT firing."""
    return {w.lower() for w in WORD_RE.findall(text or '') if len(w) >= MIN_CONTENT_LEN}


# ------------------------------------------------------------------ loading
def load_spine():
    stanzas = {}
    with open(STANZA_PATH, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rec = json.loads(line)
                stanzas[rec['location']] = rec
    lemmas = []
    with open(LEMMA_PATH, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                lemmas.append(json.loads(line))
    return stanzas, lemmas


def index_by_id_pwg(lemmas):
    idx = collections.defaultdict(list)
    for rec in lemmas:
        for pid in rec.get('id_pwg') or []:
            idx[str(pid)].append(rec)
    return idx


# ------------------------------------------------------- step 12: judge witness
def build_witness(lemma_records, stanzas, n=WITNESS_N):
    """Up to `n` example loci with ALL FOUR renderings, for one PWG headword.

    Advisory context for the judge, never an instruction to copy (IMPLEMENTATION step 12).
    Loci are chosen from the highest-frequency lemma first, then in corpus order, so the
    block is deterministic and reproducible.
    """
    if not lemma_records:
        return None
    ranked = sorted(lemma_records, key=lambda r: (-r['occurrence_count'], r['lemma']))
    loci = []
    for rec in ranked:
        for occ in rec['occurrences']:
            stanza = stanzas.get(occ['location'])
            if stanza is None:
                continue
            renderings = {
                t: stanza['translations'][t]['text']
                for t in TRANSLATORS
                if stanza['translations'][t]['status'] == 'present'
            }
            if len(renderings) < 2:
                continue
            loci.append({'location': occ['location'], 'form': occ['form'],
                         'lemma': rec['lemma'], 'renderings': renderings})
            if len(loci) >= n:
                return {'lemma': ranked[0]['lemma'],
                        'occurrence_count': ranked[0]['occurrence_count'],
                        'loci': loci, 'advisory': True}
    if not loci:
        return None
    return {'lemma': ranked[0]['lemma'], 'occurrence_count': ranked[0]['occurrence_count'],
            'loci': loci, 'advisory': True}


def witness_block_for_headword(id_pwg, idx, stanzas, n=WITNESS_N):
    """The call site the judge prompt path consumes. A headword with an `id_pwg` present
    in the spine gets a witness block; one without gets None (W1.10 acceptance)."""
    return build_witness(idx.get(str(id_pwg)) or [], stanzas, n)


# --------------------------------------------------- step 13: contradiction gate
def contradicts_all(gloss, witness):
    """Does `gloss` contradict ALL FOUR translators at EVERY attested locus?

    "Contradicts" is not mechanically decidable, so the marked default (step 13) is
    obeyed literally: the gate fires ONLY on the unanimous case, and near-misses are
    reported at a lower severity WITHOUT being queued. A noisy gate gets switched off; a
    quiet one gets trusted.

    Operationalised as zero content-token overlap against every rendering at every locus.
    A gloss sharing even one content token with any single rendering does NOT fire.
    """
    if not witness or not witness['loci']:
        return False, {'reason': 'no witness', 'loci_checked': 0, 'loci_with_overlap': 0}
    g = content_tokens(gloss)
    if not g:
        return False, {'reason': 'gloss has no content tokens', 'loci_checked': 0,
                       'loci_with_overlap': 0}
    with_overlap = 0
    for locus in witness['loci']:
        if any(g & content_tokens(text) for text in locus['renderings'].values()):
            with_overlap += 1
    total = len(witness['loci'])
    fires = with_overlap == 0
    return fires, {'reason': 'unanimous contradiction' if fires else 'overlap found',
                   'loci_checked': total, 'loci_with_overlap': with_overlap}


def gate_decision(gloss, witness):
    """-> a queue entry, or a logged near-miss. NEVER a rejection (ARCHITECTURE Sec.5)."""
    fires, detail = contradicts_all(gloss, witness)
    if fires:
        return {'action': 'queue_for_review', 'severity': 'high',
                'reason': detail['reason'], 'detail': detail,
                'lemma': witness['lemma'],
                'loci': [locus['location'] for locus in witness['loci']],
                'layer_b_used': False}
    if detail['loci_checked'] and detail['loci_with_overlap'] < detail['loci_checked']:
        return {'action': 'log_only', 'severity': 'low', 'reason': 'partial disagreement',
                'detail': detail, 'layer_b_used': False}
    return {'action': 'none', 'severity': 'none', 'reason': detail['reason'],
            'detail': detail, 'layer_b_used': False}


# ------------------------------------------------------------------ selftest
def selftest():
    stanzas = {
        '1.1.1': {'location': '1.1.1', 'translations': {
            'grassmann_de_1876': {'status': 'present', 'text': 'Den Priester Agni preise ich'},
            'geldner_de_1951': {'status': 'present', 'text': 'Agni berufe ich als Bevollmächtigten'},
            'elizarenkova_ru_1989': {'status': 'present', 'text': 'Агни призываю я жреца'},
            'griffith_en_1896': {'status': 'present', 'text': 'I Laud Agni the chosen Priest'}}},
        '1.1.2': {'location': '1.1.2', 'translations': {
            'grassmann_de_1876': {'status': 'present', 'text': 'Agni der Rufer der Weisen'},
            'geldner_de_1951': {'status': 'present', 'text': 'Agni ist der Berufene'},
            'elizarenkova_ru_1989': {'status': 'present', 'text': 'Агни достоин призывов'},
            'griffith_en_1896': {'status': 'present', 'text': 'Worthy is Agni to be praised'}}},
        '10.106.5': {'location': '10.106.5', 'translations': {
            'grassmann_de_1876': {'status': 'present', 'text': 'Ein dunkler Vers'},
            'geldner_de_1951': {'status': 'absent_from_source', 'text': None},
            'elizarenkova_ru_1989': {'status': 'present', 'text': 'Тёмный стих'},
            'griffith_en_1896': {'status': 'present', 'text': 'An obscure verse'}}},
    }
    lemma = {'lemma': 'agní-', 'id_pwg': ['349'], 'occurrence_count': 1724,
             'occurrences': [{'location': '1.1.1', 'form': 'agním', 'token_index': 0,
                              'wordlevel': None},
                             {'location': '1.1.2', 'form': 'agníḥ', 'token_index': 1,
                              'wordlevel': None},
                             {'location': '10.106.5', 'form': 'agním', 'token_index': 2,
                              'wordlevel': None}]}
    idx = index_by_id_pwg([lemma])

    # --- W1.10: a headword WITH an id_pwg in the spine gets a block; one without gets none
    w = witness_block_for_headword('349', idx, stanzas)
    assert w is not None and w['lemma'] == 'agní-'
    assert len(w['loci']) == WITNESS_N == 3, w['loci']
    assert w['advisory'] is True
    assert witness_block_for_headword('99999', idx, stanzas) is None

    # all four renderings are carried where present; the Geldner gap is simply absent
    assert set(w['loci'][0]['renderings']) == set(TRANSLATORS)
    gapped = [locus for locus in w['loci'] if locus['location'] == '10.106.5'][0]
    assert 'geldner_de_1951' not in gapped['renderings'], gapped['renderings']
    assert len(gapped['renderings']) == 3

    # N is a cap, not a promise: fewer attested loci yield fewer
    small = dict(lemma, occurrences=lemma['occurrences'][:1])
    assert len(build_witness([small], stanzas)['loci']) == 1

    # --- W1.11: synthetic contradicting card IS queued, agreeing card is NOT
    agreeing = 'Agni, der Priester des Opfers'
    contradicting = 'колесница, боевая повозка'
    d_ok = gate_decision(agreeing, w)
    d_bad = gate_decision(contradicting, w)
    assert d_ok['action'] != 'queue_for_review', d_ok
    assert d_bad['action'] == 'queue_for_review', d_bad
    assert d_bad['severity'] == 'high' and d_bad['reason'] == 'unanimous contradiction'

    # the gate QUEUES, it never rejects -- no code path may emit a rejection
    for decision in (d_ok, d_bad):
        assert decision['action'] in ('queue_for_review', 'log_only', 'none'), decision
        assert decision['layer_b_used'] is False, 'layer B is excluded by R14'

    # a gloss agreeing at only ONE locus must NOT fire (unanimity is required)
    partial = gate_decision('Priester', w)
    assert partial['action'] == 'log_only', partial
    assert partial['severity'] == 'low'

    # degenerate inputs never fire
    assert gate_decision('', w)['action'] == 'none'
    assert gate_decision('огонь', None)['action'] == 'none'

    print('rv_pipeline_bridge selftest OK -- witness present/absent by id_pwg, N=3 cap, '
          'Geldner gap carried as absence, unanimous-only gate queues not rejects, '
          'layer B excluded')
    return 0


# ----------------------------------------------------------------------- cli
def main():
    ap = argparse.ArgumentParser(description='RV judge witness + contradiction gate (H1844)')
    sub = ap.add_subparsers(dest='cmd', required=True)

    wi = sub.add_parser('witness', help='witness block for a PWG headword')
    wi.add_argument('--id-pwg', required=True)
    wi.add_argument('--n', type=int, default=WITNESS_N)

    ga = sub.add_parser('gate', help='contradiction-gate decision for a produced gloss')
    ga.add_argument('--id-pwg', required=True)
    ga.add_argument('--gloss', required=True)

    sub.add_parser('selftest')

    a = ap.parse_args()
    if a.cmd == 'selftest':
        return selftest()
    stanzas, lemmas = load_spine()
    idx = index_by_id_pwg(lemmas)
    witness = witness_block_for_headword(a.id_pwg, idx, stanzas,
                                         getattr(a, 'n', WITNESS_N))
    if a.cmd == 'witness':
        print(json.dumps(witness, ensure_ascii=False, indent=2))
        return 0
    print(json.dumps(gate_decision(a.gloss, witness), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
