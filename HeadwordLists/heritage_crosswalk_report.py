"""Phase 2 step 9: report how much of MW Heritage covers, and how the covered set
relates to the DCS-attested layer and kosha's corpus frequency layer. Reads the
already-built mw_heritage_crosswalk.tsv (heritage_mw_crosswalk.py) plus the same
DCS lemma index huet_coverage.py uses and kosha's data/frequency/lemma_frequency.tsv.
"""
import sys, os, csv, json
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import huet_coverage as hc

TSV = os.path.join(HERE, "mw_heritage_crosswalk.tsv")
KOSHA_FREQ = os.environ.get("KOSHA_FREQ",
    r"C:/Users/user/Documents/GitHub/kosha/data/frequency/lemma_frequency.tsv")

def main():
    all_keys, covered = set(), set()
    with open(TSV, encoding='utf-8') as f:
        r = csv.reader(f, delimiter='\t')
        next(r)
        for row in r:
            k, flag = row[0], row[1]
            all_keys.add(k)
            if flag == "1":
                covered.add(k)

    dcs = set()
    for k in json.load(open(hc.DCS, encoding='utf-8'))['lemmas']:
        nk = hc.norm_key(k)
        if nk:
            dcs.add(nk)

    kosha = {}
    with open(KOSHA_FREQ, encoding='utf-8') as f:
        r = csv.DictReader(f, delimiter='\t')
        for row in r:
            k = hc.norm_key(row['lemma_slp1'])
            if k:
                kosha[k] = row

    print(f"MW entries total (unique mw_key1): {len(all_keys)}")
    print(f"Heritage-covered: {len(covered)} ({100*len(covered)/len(all_keys):.1f}%)")

    cov_dcs = covered & dcs
    all_dcs = all_keys & dcs
    print(f"\nDCS-attested among covered:   {len(cov_dcs)} ({100*len(cov_dcs)/len(covered):.1f}% of covered)")
    print(f"DCS-attested among all MW:    {len(all_dcs)} ({100*len(all_dcs)/len(all_keys):.1f}% of all MW)")
    print(f"  -> Heritage coverage is {'enriched for' if len(cov_dcs)/len(covered) > len(all_dcs)/len(all_keys) else 'not enriched for'} corpus-attested vocabulary")

    cov_kosha = covered & kosha.keys()
    all_kosha = all_keys & kosha.keys()
    print(f"\nIn kosha frequency layer among covered: {len(cov_kosha)} ({100*len(cov_kosha)/len(covered):.1f}% of covered)")
    print(f"In kosha frequency layer among all MW:  {len(all_kosha)} ({100*len(all_kosha)/len(all_keys):.1f}% of all MW)")

    ranked_covered = sorted(
        (int(kosha[k]['rank_all']) for k in cov_kosha if kosha[k].get('rank_all')),
    )
    if ranked_covered:
        print(f"\nOf the {len(cov_kosha)} covered+ranked lemmas: "
              f"median kosha rank {ranked_covered[len(ranked_covered)//2]}, "
              f"best rank {ranked_covered[0]}, "
              f"{sum(1 for r in ranked_covered if r <= 1000)} are in the kosha top-1000")

if __name__ == "__main__":
    main()
