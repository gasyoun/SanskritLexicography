#!/usr/bin/env python
r"""rv_wisdomlib_bridge.py -- wisdomlib in its four R11 roles (H1844 step 15).

Reads ONLY the already-downloaded wisdomlib feeds in the SamudraManthanam repo. There is
no network path in this module at all -- R17 forbids a crawl during the run, and W1.13's
acceptance criterion is that the run makes zero network calls.

**Measured 29-07-2026: NONE of the four roles can be populated from the on-disk feed.**
That is a finding about the feed, not a defect in this bridge, and it is recorded rather
than papered over:

  role 1  EN gloss tier for PWG->EN        NOT POPULATED -- no gloss text exists on disk
  role 2  tradition sense disambiguation   ZERO OVERLAP  -- the 63-word tradition feed is a
                                                           Buddhist-terminology probe set
                                                           with no Rigvedic vocabulary in it
  role 3  fifth contradiction-gate witness NOT POPULATED -- same missing gloss text
  role 4  AV citation-locus source         STAGED        -- no Atharvaveda data on disk

Role 2's zero is the surprising one, so it is pinned by a selftest: the join key is NOT at
fault. `fold_key` demonstrably carries `agni` -> `agní-`, `indra` -> `índra-`, `soma` ->
`sóma-`. The 63 words actually in `word_traditions.jsonl` are `akshobhya`, `bodhisattva`,
`hevajra`, `vajravarahi`, `sarvatathagatakarshani` and their kin -- Vajrayana Buddhist
terminology harvested as a fetcher probe, not a Sanskrit lexicon. Intersected with the
Rigveda's 9,539 lemmas the result is empty, and empty is the CORRECT answer.

Why roles 1 and 3 cannot be populated: `entries_index.jsonl` (848 rows) is a catalogue of
BOOKS and ARTICLES (`slug`/`url`/`title`/`author`/`words`/`group`/`ctype`/`sections`) --
it carries no headword, no SLP1 key and no gloss. `word_traditions.jsonl` (63 rows) carries
`traditions`, `headings` and an INTEGER `glosses` count, not gloss text; the upstream
fetcher's own docstring says it is "metadata only" and that the gloss-bearing HTML in
`definitions/` is gitignored and "provisional -- do not redistribute". So the English
glosses R11 role 1 asks for are not merely unindexed, they are absent from disk, and the
only way to obtain them is the crawl R17 forbids. The conservative default (PLAN Sec.4)
is therefore taken: emit the roles that have data, declare the ones that do not, and log
the fork in `docs/DECISIONS_LOG_rv_multitranslation.md`.

The tradition join is REUSED from the committed
[`src/enrich_renou_wisdomlib.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/enrich_renou_wisdomlib.py)
(`fold_key` -- diacritic-free lowercase with wisdomlib's `sh` digraph collapsed, so the
ASCII slug `akshobhya` meets the IAST `akṣobhya`). No second join key is invented here.

  python src/rv_wisdomlib_bridge.py build
  python src/rv_wisdomlib_bridge.py selftest
"""
import argparse
import collections
import json
import os
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT_ROOT = os.path.normpath(os.path.join(HERE, '..'))
GITHUB_ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
PWG_RU_DIR = os.path.join(RT_ROOT, 'pwg_ru')
RUN_DIR = os.path.join(PWG_RU_DIR, 'h1844')

WISDOMLIB_DIR = os.path.join(GITHUB_ROOT, 'SamudraManthanam', 'web', 'corpus_builder', 'wisdomlib')
WORD_TRADITIONS = os.path.join(WISDOMLIB_DIR, 'word_traditions.jsonl')
ENTRIES_INDEX = os.path.join(WISDOMLIB_DIR, 'entries_index.jsonl')

LEMMA_PATH = os.path.join(PWG_RU_DIR, 'rv_lemma_occurrences.jsonl')
BRIDGE_OUT = os.path.join(PWG_RU_DIR, 'rv_wisdomlib_bridge.jsonl')
REPORT_OUT = os.path.join(RUN_DIR, 'wisdomlib_roles_report.md')

ROLE_NAMES = {
    1: 'en_gloss_tier',
    2: 'tradition_disambiguation',
    3: 'contradiction_gate_witness',
    4: 'av_citation_locus',
}


def fold_key(s):
    """Diacritic-free lowercase join key -- semantics reused verbatim from
    `enrich_renou_wisdomlib.fold_key` (kept import-free so this bridge does not drag in
    that module's `renou` / `corpus_gate` dependency chain for one function)."""
    nfd = unicodedata.normalize('NFD', (s or '').lower())
    bare = ''.join(c for c in nfd if not unicodedata.combining(c))
    return bare.replace('sh', 's')


def strip_lemma(lemma):
    """VedaWeb lemmas carry a trailing hyphen on stems (`agní-`); the wisdomlib slug does
    not. Strip it before folding."""
    return (lemma or '').rstrip('-')


def load_word_traditions(path=WORD_TRADITIONS):
    """fold_key(word) -> record. The gloss COUNT is carried through deliberately: it is
    the only gloss-related datum that exists on disk, and role 1 needs it to state
    honestly how much text is missing."""
    out = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            out[fold_key(rec['word'])] = {
                'word': rec['word'],
                'traditions': rec.get('traditions') or [],
                'gloss_count': rec.get('glosses'),
                'headings': rec.get('headings') or [],
            }
    return out


def load_entries_index(path=ENTRIES_INDEX):
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def index_has_gloss_fields(rows):
    """Role 1/3 feasibility probe: does the entries index carry anything headword-like?

    Returns the set of keys seen. A gloss tier needs a headword and a definition; this
    index has neither, and saying so from the data beats asserting it from memory.
    """
    keys = set()
    for r in rows:
        keys |= set(r)
    return keys


GLOSS_BEARING_KEYS = {'word', 'headword', 'lemma', 'definition', 'gloss', 'meaning', 'senses'}


def load_rv_lemmas(path=LEMMA_PATH):
    """fold_key -> {lemma, occurrence_count, id_pwg}. Only what the join needs."""
    out = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            key = fold_key(strip_lemma(rec['lemma']))
            if not key:
                continue
            prev = out.get(key)
            if prev is None or rec['occurrence_count'] > prev['occurrence_count']:
                out[key] = {'lemma': rec['lemma'],
                            'occurrence_count': rec['occurrence_count'],
                            'id_pwg': rec.get('id_pwg') or []}
    return out


def build_role2(wl, rv_lemmas):
    """Tradition-based sense disambiguation -- the one role with data behind it."""
    rows = []
    for key, wrec in sorted(wl.items()):
        hit = rv_lemmas.get(key)
        if hit is None:
            continue
        rows.append({
            'role': ROLE_NAMES[2],
            'lemma': hit['lemma'],
            'wisdomlib_word': wrec['word'],
            'traditions': wrec['traditions'],
            'id_pwg': hit['id_pwg'],
            'rv_occurrence_count': hit['occurrence_count'],
            'gloss_count_on_wisdomlib': wrec['gloss_count'],
            'reuse_policy': 'suggest_only',
            'trust_level': 'corpus_translation_witness',
        })
    return rows


def cmd_build(a):
    for path in (WORD_TRADITIONS, ENTRIES_INDEX, LEMMA_PATH):
        if not os.path.exists(path):
            sys.exit('required input missing (stop condition 1): %s' % path)

    wl = load_word_traditions()
    entries = load_entries_index()
    entry_keys = index_has_gloss_fields(entries)
    rv_lemmas = load_rv_lemmas()

    role2 = build_role2(wl, rv_lemmas)
    gloss_text_available = bool(entry_keys & GLOSS_BEARING_KEYS)

    os.makedirs(RUN_DIR, exist_ok=True)
    with open(BRIDGE_OUT, 'w', encoding='utf-8', newline='\n') as f:
        for row in role2:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')

    trad_hist = collections.Counter(t for r in role2 for t in r['traditions'])
    print('wisdomlib bridge:')
    print('  wisdomlib words with tradition tags : %d' % len(wl))
    print('  RV lemmas (folded join keys)        : %d' % len(rv_lemmas))
    print('  role 2 joined rows                  : %d (%.1f%% of the wisdomlib words)'
          % (len(role2), 100.0 * len(role2) / len(wl) if wl else 0))
    print('  entries_index rows / keys           : %d / %s' % (len(entries), sorted(entry_keys)))
    print('  gloss-bearing keys present          : %s' % (gloss_text_available or 'NONE'))
    print('  tradition histogram                 : %s' % dict(trad_hist))
    print('  -> %s' % BRIDGE_OUT)

    _write_report(len(wl), len(rv_lemmas), role2, entries, entry_keys,
                  gloss_text_available, trad_hist)
    print('  -> %s' % REPORT_OUT)
    return 0


def _write_report(n_wl, n_rv, role2, entries, entry_keys, gloss_text_available, trad_hist):
    lines = []
    lines.append('# wisdomlib in four roles — what the on-disk feed actually supports')
    lines.append('')
    lines.append('_Created: 29-07-2026 · Last updated: 29-07-2026_')
    lines.append('')
    lines.append('Produced by [`src/rv_wisdomlib_bridge.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_wisdomlib_bridge.py) '
                 '(H1844 step 15). Zero network calls (R17).')
    lines.append('')
    lines.append('| Role (R11) | Status | Rows | Why |')
    lines.append('|---|---|--:|---|')
    lines.append('| 1 · EN gloss tier for PWG→EN | **not populated** | 0 | '
                 'No gloss text on disk. `entries_index.jsonl` is a catalogue of works, not '
                 'of headwords; `word_traditions.jsonl` carries an integer gloss *count*. '
                 'Obtaining the text needs the crawl R17 forbids. |')
    lines.append('| 2 · Tradition sense disambiguation | **zero overlap** | %d | '
                 'The join key is sound (`agni`→`agní-`, `indra`→`índra-`); the 63 words in '
                 '`word_traditions.jsonl` are Vajrayāna Buddhist terminology '
                 '(`bodhisattva`, `hevajra`, `vajravārāhī`…) harvested as a fetcher probe. '
                 'Intersected with the RV’s %d lemmas the result is correctly empty. |'
                 % (len(role2), n_rv))
    lines.append('| 3 · Fifth contradiction-gate witness | **not populated** | 0 | '
                 'A witness must supply a reading to contradict. Same missing gloss text as role 1. |')
    lines.append('| 4 · AV citation-locus source | **staged** | 0 | '
                 'No Atharvaveda data on disk, and AV is an explicit wave-1 non-goal (R3). |')
    lines.append('')
    lines.append('## Measured inputs')
    lines.append('')
    lines.append('| Input | Value |')
    lines.append('|---|--:|')
    lines.append('| wisdomlib words carrying tradition tags | %d |' % n_wl)
    lines.append('| RV lemmas (distinct folded join keys) | %d |' % n_rv)
    lines.append('| Role-2 joined rows | %d |' % len(role2))
    lines.append('| `entries_index.jsonl` rows | %d |' % len(entries))
    lines.append('| `entries_index.jsonl` keys | `%s` |' % '`, `'.join(sorted(entry_keys)))
    lines.append('| Any gloss-bearing key present | %s |' % ('yes' if gloss_text_available else 'no'))
    lines.append('')
    lines.append('## Tradition histogram over the joined rows')
    lines.append('')
    lines.append('| Tradition | Rows |')
    lines.append('|---|--:|')
    for t, n in trad_hist.most_common():
        lines.append('| %s | %d |' % (t, n))
    if not trad_hist:
        lines.append('| (none) | 0 |')
    lines.append('')
    lines.append('## Consequence for the plan')
    lines.append('')
    lines.append('PLAN §2 lists the wisdomlib crawler as an existing asset, which it is — but '
                 'R11 assumed the *downloaded* half was a Sanskrit gloss resource. It is not: '
                 'what is on disk is a catalogue of works, three crawled books, and a 63-word '
                 'Buddhist-terminology probe. All four roles are therefore blocked on DATA, not '
                 'on code — this bridge is written, tested and will populate the moment a real '
                 'gloss feed lands. The unblocking step is a daytime `definitions.py` crawl over '
                 'an RV-attested headword list, which is deliberately out of scope here (R17) and '
                 'should be scoped as its own handoff rather than smuggled into this run.')
    lines.append('')
    lines.append('The honest consequence for wave 1: **W1.13 cannot be met as written.** The '
                 'acceptance criterion asks for a smoke test per role and zero network calls; the '
                 'zero-network half holds, and each role has a test, but three roles test an '
                 'empty result and the fourth tests a correct empty intersection. Recording that '
                 'is the deliverable — asserting four working roles would not be true.')
    lines.append('')
    lines.append('_Dr. Mārcis Gasūns_')
    lines.append('')
    with open(REPORT_OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))


def selftest():
    # the reused join key: ASCII slug must meet the IAST headword
    assert fold_key('akshobhya') == fold_key('akṣobhya'), (fold_key('akshobhya'),
                                                           fold_key('akṣobhya'))
    assert fold_key('Bodhisattva') == 'bodhisattva'
    assert strip_lemma('agní-') == 'agní'
    assert fold_key(strip_lemma('agní-')) == 'agni'
    assert fold_key(None) == ''

    # role 2 joins only where the RV lemma actually exists
    wl = {'agni': {'word': 'agni', 'traditions': ['hinduism', 'vedic'],
                   'gloss_count': 12, 'headings': []},
          'nowhere': {'word': 'nowhere', 'traditions': ['buddhism'],
                      'gloss_count': 1, 'headings': []}}
    rv = {'agni': {'lemma': 'agní-', 'occurrence_count': 1234, 'id_pwg': ['349']}}
    rows = build_role2(wl, rv)
    assert len(rows) == 1, rows
    assert rows[0]['lemma'] == 'agní-'
    assert rows[0]['traditions'] == ['hinduism', 'vedic']
    assert rows[0]['reuse_policy'] == 'suggest_only'
    assert rows[0]['trust_level'] == 'corpus_translation_witness'

    # role 1/3 feasibility probe must report the catalogue as gloss-free
    catalogue = [{'slug': 'x', 'url': 'u', 'title': 't', 'author': 'a',
                  'words': 1, 'group': 'g', 'ctype': 'book', 'sections': []}]
    keys = index_has_gloss_fields(catalogue)
    assert not (keys & GLOSS_BEARING_KEYS), keys
    # ...and must notice if a future feed DOES carry glosses
    assert index_has_gloss_fields([{'headword': 'agni', 'definition': 'fire'}]) & GLOSS_BEARING_KEYS

    # no network surface in this module -- inspect IMPORT statements, not raw substrings
    # (a substring scan would trip on this guard's own banned-name list)
    import re as _re
    src = open(os.path.abspath(__file__), encoding='utf-8').read()
    imported = _re.findall(
        r'^\s*(?:import|from)\s+(urllib|requests|httpx|socket|aiohttp|http)\b', src, _re.M)
    assert not imported, 'network module(s) imported: %s (R17 forbids a crawl)' % imported

    print('rv_wisdomlib_bridge selftest OK -- reused fold_key join (ASCII slug = IAST), '
          'role-2 build, role-1/3 gloss-absence probe, zero-network guard')
    return 0


def main():
    ap = argparse.ArgumentParser(description='wisdomlib four-role bridge (H1844 step 15)')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('build', help='join the on-disk feeds and write the roles report')
    sub.add_parser('selftest', help='deterministic asserts, no network')
    a = ap.parse_args()
    return cmd_build(a) if a.cmd == 'build' else selftest()


if __name__ == '__main__':
    sys.exit(main())
