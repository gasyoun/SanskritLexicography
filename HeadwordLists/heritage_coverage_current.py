"""Phase 1 of HERITAGE_INRIA_ROADMAP.md: rerun huet_coverage.py's validated
VH->IAST->SLP1 pipeline on the CURRENT Heritage/DICO stem inventory
(heritage_current_stems.txt, from heritage_stem_extract.py) and diff against the
2014 export (then-2014/21562-huet-velthius.txt) in the NOW_VS_THEN.md manner.

Reuses huet_coverage.py's transcoder + CDSL/DCS loaders — no new normalisation
logic is written here.
"""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import huet_coverage as hc

CURRENT = os.path.join(HERE, "heritage_current_stems.txt")

def load_current():
    keys, n = set(), 0
    for line in open(CURRENT, encoding='utf-8'):
        k = hc.norm_huet(line.rstrip('\n'))
        if k:
            keys.add(k); n += 1
    return keys, n

def coverage(keys, dsets):
    covered, remaining, order = set(), set(dsets), []
    while remaining:
        best = max(remaining, key=lambda d: len((keys & dsets[d]) - covered))
        add = len((keys & dsets[best]) - covered)
        if add == 0:
            break
        covered |= keys & dsets[best]; remaining.discard(best)
        order.append((best, add, len(covered), 100 * len(covered) / len(keys)))
    return covered, order

if __name__ == "__main__":
    current, n_raw = load_current()
    then2014 = set()
    for line in open(hc.HUET, encoding='utf-8-sig'):
        k = hc.norm_huet(line.rstrip('\n'))
        if k:
            then2014.add(k)

    print(f"Current DICO stems: {n_raw} raw lines -> {len(current)} unique normalised keys")
    print(f"2014 export: {len(then2014)} unique normalised keys")

    added = current - then2014
    removed = then2014 - current
    kept = current & then2014
    print(f"\n2014 -> current delta:")
    print(f"  kept:    {len(kept)}")
    print(f"  added:   {len(added)}  (new since the 2014 export)")
    print(f"  removed: {len(removed)}  (in 2014, absent from the current mirror)")

    dsets = {d: hc.load_k1(d) for d in hc.DICTS}
    dsets = {d: s for d, s in dsets.items() if s}
    dcs = set()
    for k in json.load(open(hc.DCS, encoding='utf-8'))['lemmas']:
        nk = hc.norm_key(k)
        if nk:
            dcs.add(nk)

    print("\n=== CDSL + DCS coverage: current mirror ===")
    covered, order = coverage(current, dsets)
    for d, a, c, p in order:
        print(f"  {d:<5} +{a:<6} cum {c:<6} {p:5.1f}%")
    att = current & dcs
    print(f"  any CDSL dict:        {len(covered):6} ({100*len(covered)/len(current):5.1f}%)")
    print(f"  DCS corpus-attested:  {len(att):6} ({100*len(att)/len(current):5.1f}%)")
    print(f"  DCS-attested, no CDSL:{len(att - covered):6} ({100*len(att - covered)/len(current):5.1f}%)")

    print("\n=== CDSL + DCS coverage: 2014 export (recomputed for a same-run comparison) ===")
    covered14, order14 = coverage(then2014, dsets)
    att14 = then2014 & dcs
    for d, a, c, p in order14:
        print(f"  {d:<5} +{a:<6} cum {c:<6} {p:5.1f}%")
    print(f"  any CDSL dict:        {len(covered14):6} ({100*len(covered14)/len(then2014):5.1f}%)")
    print(f"  DCS corpus-attested:  {len(att14):6} ({100*len(att14)/len(then2014):5.1f}%)")

    print(f"\n=== Added stems (current minus 2014): CDSL/DCS status ===")
    add_covered = added & covered
    add_dcs = added & dcs
    print(f"  added total: {len(added)}")
    print(f"  added, in a CDSL dict: {len(add_covered)} ({100*len(add_covered)/max(1,len(added)):5.1f}%)")
    print(f"  added, DCS-attested:   {len(add_dcs)} ({100*len(add_dcs)/max(1,len(added)):5.1f}%)")
    print(f"  added, corpus-attested but in NO CDSL dict (candidates for COVERAGE_ADDITIONS.md): {len(add_dcs - covered)}")

    cand_path = os.path.join(HERE, "heritage_current_candidates_no_cdsl.txt")
    with open(cand_path, 'w', encoding='utf-8', newline='\n') as f:
        for k in sorted(add_dcs - covered):
            f.write(k + '\n')
    print(f"  written candidate list: {cand_path}")
