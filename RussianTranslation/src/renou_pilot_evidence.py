#!/usr/bin/env python
"""renou_pilot_evidence.py — full per-text DCS evidence + PWG register layer
for the Step-0 pilot sample (the remake the 19-07-2026 pilot votes asked for).

MG's three S0 votes (S0-001/002/003, review/decisions.md) all rejected cards
whose "DCS evidence" panel showed lemma-GLOBAL facts — the oldest text overall
and a bare text count — instead of evidence for the contested state itself:
a state-I (Vedic) card headlined by Manusmṛti, a state-II (Pāṇinian) card
headlined by the Ṛgveda, and a 19-text lemma with none of the texts named.

This collector makes the per-card evidence complete. For every sampled lemma
it records the FULL list of DCS texts attesting it — each named, dated, with
its Renou state, text-level confidence and register codes — so the sheet can
show exactly which texts back the contested state, and the whole attestation
surface (per S0-003). One corpus pass; text→state resolution is imported from
build_dcs_renou verbatim, so the evidence can never drift from the index.

It also joins the PWG register/genre layer (SanskritGrammar
data/pwg_register_genre — the <ls>-derived period/genre profile per headword,
homonym-precise, merged 19-07-2026) onto pwg/pw items by SLP1 k1, per
review/decisions.md: for PW the join is labeled as the PWG sibling profile
(PW condenses PWG; the layer reads pwg.txt citations only).

  python renou_pilot_evidence.py [--sample renou_pilot_sample.jsonl]
                                 [--register-tsv PATH]
                                 [--out renou_pilot_evidence.json]

Output shape (renou_pilot_evidence.json):
  { "lemmas": { iast: [ {text, date, state, conf, registers:[...]}, ... ] },
    "pwg_register": { k1: [ {L_id, hom, n_citations, periods, earliest_period,
                             register, lexicon_only, genres, sources}, ... ] },
    "meta": {...} }

Read-only over DCS/csl-orig; deterministic. Computed by Fable 5
(`claude-fable-5`), remake of the Step-0 pilot per review/decisions.md.
"""
import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build_dcs_renou as bdr   # noqa: E402  (text→state resolution + corpus paths)

REGISTER_TSV_DEFAULT = os.path.normpath(os.path.join(
    HERE, '..', '..', '..', 'SanskritGrammar', 'data', 'pwg_register_genre',
    'pwg_register_genre.tsv'))


def sample_targets(sample_path):
    """(iast lemma set, SLP1 k1 set for pwg/pw items) from the pilot sample."""
    lemmas, k1s = set(), set()
    with open(sample_path, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            it = json.loads(line)
            if it.get('headword_iast'):
                lemmas.add(it['headword_iast'])
            if it.get('dict') in ('pwg', 'pw') and it.get('key1'):
                k1s.add(it['key1'])
    return lemmas, k1s


def scan_corpus(targets):
    """lemma → [{text, date, state, conf, registers}] over every DCS text, one
    pass. Only `targets` lemmas are kept; each text contributes at most one row
    per lemma (attestation presence, not token counts)."""
    texts = bdr.build_text_states()
    out = {lem: [] for lem in targets}
    names = sorted(texts)
    for i, name in enumerate(names, 1):
        ts = texts[name]
        d = os.path.join(bdr.FILES, name)
        found = set()
        for fn in os.listdir(d):
            if not fn.endswith('.conllu'):
                continue
            remaining = targets - found
            if not remaining:
                break
            found |= (bdr.lemmas_in_file(os.path.join(d, fn)) & remaining)
        for lem in found:
            out[lem].append({
                'text': name,
                'date': ts['date'],
                'state': ts['renou'],
                'conf': ts['confidence'],
                'registers': sorted(ts['registers']),
            })
        if i % 25 == 0:
            print('  scanned %d/%d texts' % (i, len(names)), file=sys.stderr)
    for lem in out:
        out[lem].sort(key=lambda r: (r['date'] is None,
                                     r['date'] if r['date'] is not None else 0,
                                     r['text']))
    return out


def load_register_layer(tsv_path, k1s):
    """k1 → [register-layer rows] for the sampled pwg/pw headwords."""
    if not os.path.exists(tsv_path):
        print('WARN: register TSV absent (%s) — pwg_register empty' % tsv_path,
              file=sys.stderr)
        return {}
    out = {}
    with open(tsv_path, encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            if row['k1'] in k1s:
                out.setdefault(row['k1'], []).append(row)
    return out


def main():
    args = sys.argv[1:]
    sample = os.path.join(HERE, 'renou_pilot_sample.jsonl')
    tsv = REGISTER_TSV_DEFAULT
    out_path = os.path.join(HERE, 'renou_pilot_evidence.json')
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--sample':
            sample = args[i + 1]; i += 2
        elif a == '--register-tsv':
            tsv = args[i + 1]; i += 2
        elif a == '--out':
            out_path = args[i + 1]; i += 2
        else:
            raise SystemExit('unknown option: %s' % a)

    lemmas, k1s = sample_targets(sample)
    print('targets: %d lemmas, %d pwg/pw k1s' % (len(lemmas), len(k1s)))
    ev = scan_corpus(lemmas)
    reg = load_register_layer(tsv, k1s)
    n_attested = sum(1 for v in ev.values() if v)
    doc = {
        'lemmas': ev,
        'pwg_register': reg,
        'meta': {
            'sample': os.path.basename(sample),
            'n_lemmas': len(lemmas),
            'n_lemmas_attested': n_attested,
            'n_k1_register_rows': sum(len(v) for v in reg.values()),
            'register_tsv': 'SanskritGrammar data/pwg_register_genre (19-07-2026)',
        },
    }
    tmp = out_path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(doc, f, ensure_ascii=False, sort_keys=True, indent=1)
    os.replace(tmp, out_path)
    print('lemmas attested in DCS: %d/%d · register rows: %d → %s'
          % (n_attested, len(lemmas), doc['meta']['n_k1_register_rows'],
             os.path.basename(out_path)))


if __name__ == '__main__':
    main()
