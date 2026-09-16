# -*- coding: utf-8 -*-
"""mw_unabsorbed_census.py — H5011: widened "what remains unabsorbed by MW?"
census with a part-of-speech cross-cut (csl-corrections#119 follow-up).

MG ruling 16-09-2026: widen the MW-unabsorbed census to ALL parts of speech and
ALL supplement layers, and answer "what else remains unabsorbed by MW?".

Deterministic, stdlib-only, re-runnable in ~2 min. Every count the companion
doc (MW-UNABSORBED-CENSUS-WIDENED-16-09-2026.md) states is regenerated here.

Method notes (locked):
  * pw volume-7 base = entries whose <pc> begins "7-" (the Nachträge volume),
    NOT the sup_7 <info> tag layer (1,920 <hom> rows vs 541 sup_7-tagged).
  * MW max homonym per k1 = the highest <h>N attribute among MW99 entries whose
    k1 matches, EXCLUDING the MW99 annexure (<info n="sup"/>) — a main-body
    homonym count. Annexure-inclusive counts are reported as a sensitivity
    variant. Canary: kArin -> MW main max 2 (h1 + variant k2=kAri/n h2);
    the annexure h3 (fr. √kF "scattering") is a different derivation.
  * POS = <lex> values in the entry body, normalised to m./n./f./adj./mfn./
    part./ind./pron. (+adv./other); <info lex="m:f:n"/> read as a fallback.
  * same-tradition corroboration (sch, pwg) excluded, per the typology doc §4.

Inputs (read-only): csl-orig/v02/{pw,mw,mw72}/... ; VisualDCS/dcs_lemma_summary.json ;
this folder's adjudication TSVs.
Outputs: MW-UNABSORBED-CENSUS-POS-CLASS-16-09-2026.tsv,
         MW-UNABSORBED-CENSUS-HOMONYM-EXTENSIONS-16-09-2026.tsv,
         MW-UNABSORBED-CENSUS-ALL-LAYERS-16-09-2026.tsv
"""
import sys, os, io, re, json, collections

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ORIG = os.environ.get("CSL_ORIG_V02", r"C:/Users/user/Documents/GitHub/csl-orig/v02")
DCS_JSON = os.environ.get("DCS_LEMMA_JSON", r"C:/Users/user/Documents/GitHub/VisualDCS/dcs_lemma_summary.json")
HERE = os.path.dirname(os.path.abspath(__file__))

SAME_TRADITION = {'sch', 'pwg'}

L_RE = re.compile(r"^<L>")
K1 = re.compile(r"<k1>([^<]+)")
K2 = re.compile(r"<k2>([^<]+)")
PC = re.compile(r"<pc>([^<]*)")
H_ATTR = re.compile(r"<h>(\d+)")
SUP = re.compile(r'<info n="sup_(\d)"/>')
MWSUP = re.compile(r'<info n="sup"/>')
HOM = re.compile(r"<hom>(\d+)\.</hom>")
LEX = re.compile(r"<lex>([^<]*)</lex>")
INFOLEX = re.compile(r'<info lex="([^"]+)"')

POS_TOKENS = {'m.', 'n.', 'f.', 'adj.', 'mfn.', 'part.', 'ind.', 'pron.',
              'adv.', 'prep.', 'conj.', 'interj.', 'num.', 'inf.', 'mf.'}


def entries(path):
    """Yield (line_no, k1, k2, pc, lline, body) per dictionary entry."""
    cur = None
    buf = []
    start = 0
    with io.open(path, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if L_RE.match(line):
                if cur is not None:
                    yield _pack(start, cur, buf)
                cur = line
                buf = [line]
                start = i
            elif cur is not None:
                buf.append(line)
    if cur is not None:
        yield _pack(start, cur, buf)


def _pack(lineno, lline, buf):
    body = ''.join(buf)
    g = K1.search(lline)
    k1 = g.group(1).strip().lstrip('*') if g else ''
    g = K2.search(lline)
    k2 = g.group(1).strip() if g else ''
    g = PC.search(lline)
    pc = g.group(1).strip() if g else ''
    return lineno, k1, k2, pc, lline, body


def headword(k1, k2):
    return k2.lstrip('*') if k2.startswith('*') else (k1 or k2)


def pos_of(body):
    """Normalised POS token set + primary, from <lex> tags (fallback <info lex>)."""
    toks = []
    for m in LEX.finditer(body):
        for part in re.split(r'[/:]', m.group(1)):
            p = part.strip().lower()
            if p:
                toks.append(p)
    if not toks:
        for m in INFOLEX.finditer(body):
            for part in re.split(r'[/:]', m.group(1)):
                p = part.strip().lower()
                if p:
                    toks.append(p)
    seen = []
    for t in toks:
        if t not in seen:
            seen.append(t)
    norm = [t if t in POS_TOKENS else 'other' for t in seen]
    primary = norm[0] if norm else ''
    return primary, '+'.join(norm)


def main():
    # ---------- MW99 ----------
    mw_main_max = collections.defaultdict(int)   # k1 -> max <h> in main body
    mw_all_max = collections.defaultdict(int)    # k1 -> max <h> incl. annexure
    mw99_keys = set()
    annex99 = set()
    for _, k1, k2, pc, lline, body in entries(os.path.join(ORIG, "mw", "mw.txt")):
        m = H_ATTR.search(lline)
        h = int(m.group(1)) if m else 0
        is_annex = bool(MWSUP.search(body))
        for key in (k1, k2):
            if not key:
                continue
            mw99_keys.add(key)
            if h:
                mw_all_max[key] = max(mw_all_max[key], h)
                if not is_annex:
                    mw_main_max[key] = max(mw_main_max[key], h)
        if k1 and is_annex:
            annex99.add(k1)
    print(f"MW99: {len(mw99_keys)} keys, annexure k1 {len(annex99)}", file=sys.stderr)

    # ---------- MW72 ----------
    mw72_keys = set()
    for _, k1, k2, pc, lline, body in entries(os.path.join(ORIG, "mw72", "mw72.txt")):
        if k1:
            mw72_keys.add(k1)
        if k2:
            mw72_keys.add(k2)
    print(f"MW72: {len(mw72_keys)} keys", file=sys.stderr)

    # ---------- PW ----------
    pw_main_k1 = set()
    layer_hw = collections.defaultdict(list)
    layer_hom_all = collections.Counter()   # sup layer -> entries with explicit <hom>
    vol7_hom_rows = []          # (lineno, k1, hw, hom, primary, posset, sup_layer)
    n_vol7 = n_vol7_hom = 0
    for lineno, k1, k2, pc, lline, body in entries(os.path.join(ORIG, "pw", "pw.txt")):
        sup = SUP.search(body)
        if sup is None and k1:
            pw_main_k1.add(k1)
        if sup is not None:
            layer = int(sup.group(1))
            hw = headword(k1, k2)
            if hw:
                layer_hw[layer].append(hw)
            if HOM.search(body):
                layer_hom_all[layer] += 1
        # volume-7 Nachträge base = <pc> begins "7-"
        if pc.startswith('7-'):
            n_vol7 += 1
            hm = HOM.search(body)
            if hm:
                n_vol7_hom += 1
                primary, posset = pos_of(body)
                vol7_hom_rows.append((lineno, k1, headword(k1, k2), int(hm.group(1)),
                                      primary, posset, int(sup.group(1)) if sup else 0))
    print(f"pw vol-7 entries {n_vol7}; with <hom> {n_vol7_hom}", file=sys.stderr)

    # ---------- homonym-extension census (vol-7 <hom> vs MW main max) ----------
    # Definition (canary-locked): a pw vol-7 entry with an explicit <hom>N.</hom>,
    # N >= 2 (hom 1 is the base word, never an extension), whose word MW99 already
    # heads, and whose N exceeds MW99's MAIN-BODY maximum homonym for that k1
    # (the annexure's <info n="sup"/> entries excluded; annexure coverage reported
    # as a sensitivity flag). Canary kArin: N=3 > MW main max 2 -> extension.
    ext_rows = []
    n_mw_heads = 0
    for lineno, k1, hw, hom, primary, posset, layer in vol7_hom_rows:
        maxm = mw_main_max.get(k1, 0)
        maxa = mw_all_max.get(k1, 0)
        if k1 in mw99_keys:
            n_mw_heads += 1
        if k1 in mw99_keys and hom >= 2 and hom > maxm:
            ext_rows.append((lineno, k1, hw, hom, maxm, maxa, primary, posset, layer,
                             'yes' if maxa >= hom else 'no'))
    print(f"vol-7 <hom> spelling a word MW heads: {n_mw_heads}; "
          f"EXTENSIONS (hom>=2 & > MW main max): {len(ext_rows)}; "
          f"of which MW annexure would cover this hom: "
          f"{sum(1 for r in ext_rows if r[9] == 'yes')}", file=sys.stderr)

    # ---------- POS cross-cut of the 4,790 sup_7 extensions ----------
    sup7 = sorted(set(layer_hw[7]))
    sup7_ext = [h for h in sup7 if h in pw_main_k1]
    pos_acc = collections.defaultdict(collections.Counter)
    for layer in sorted(layer_hw):
        for h in sorted(set(layer_hw[layer])):
            pos_acc[layer][h] += 1
    # per-entry POS for sup_7 extension headwords
    pos_of_hw = {}
    for lineno, k1, k2, pc, lline, body in entries(os.path.join(ORIG, "pw", "pw.txt")):
        sup = SUP.search(body)
        if sup and int(sup.group(1)) == 7:
            hw = headword(k1, k2)
            if hw:
                primary, posset = pos_of(body)
                pos_of_hw[hw] = (primary, posset)

    # ---------- adjudication corroboration ----------
    adj_corr = {}
    corr_path = os.path.join(HERE, "MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv")
    if os.path.exists(corr_path):
        with io.open(corr_path, encoding='utf-8') as f:
            hdr = f.readline().rstrip('\n').split('\t')
            idx = {c: hdr.index(c) for c in hdr if c in
                   ('hw_slp1', 'verdict', 'corr_dicts', 'mahavy', 'dcs_form', 'dcs_lemma', 'evidence')}
            for line in f:
                r = line.rstrip('\n').split('\t')
                if len(r) < len(hdr):
                    continue
                hw = r[idx['hw_slp1']]
                corrs = [d for d in (r[idx['corr_dicts']] or '').split(';') if d]
                outside = [d for d in corrs if d not in SAME_TRADITION]
                adj_corr[hw] = {
                    'verdict': r[idx['verdict']],
                    'corr_n': len(corrs),
                    'outside': outside,
                    'out_n': len(outside),
                    'mahavy': r[idx['mahavy']],
                    'dcs': '1' if (r[idx['dcs_form']] == '1' or r[idx['dcs_lemma']] == '1') else '0',
                }

    # ---------- DCS bands ----------
    band = {}
    if os.path.exists(DCS_JSON):
        dcs = json.load(io.open(DCS_JSON, encoding='utf-8'))
        lem = dcs.get('lemmas', {})
        band = {h: (lem.get(h) or {}).get('freqBand', 0) for h in lem}

    # ---------- write homonym-extension TSV ----------
    out1 = os.path.join(HERE, "MW-UNABSORBED-CENSUS-HOMONYM-EXTENSIONS-16-09-2026.tsv")
    with io.open(out1, 'w', encoding='utf-8', newline='') as f:
        f.write("pw_line\tk1\thw_slp1\thom_pw\tmw_main_max_hom\tmw_all_max_hom\t"
                "annexure_covers\tpos\tpos_set\tsup_layer\tdcs_band\tcorr_n\tcorr_outside_n\t"
                "corr_outside\tmahavy\tdcs\tverdict\n")
        in_adj = 0
        for lineno, k1, hw, hom, maxm, maxa, primary, posset, layer, annex_cover in sorted(ext_rows):
            a = adj_corr.get(hw, {})
            if a:
                in_adj += 1
            f.write('\t'.join(map(str, [
                lineno, k1, hw, hom, maxm, maxa, annex_cover, primary, posset, layer,
                band.get(hw, 0),
                a.get('corr_n', ''), a.get('out_n', ''),
                ';'.join(a.get('outside', [])), a.get('mahavy', ''),
                a.get('dcs', ''), a.get('verdict', ''),
            ])) + '\n')
        print(f"  extension rows present in the sup_7 adjudication pool: {in_adj}/{len(ext_rows)} "
              f"(corroboration columns are empty where the row is outside that pool)", file=sys.stderr)

    # ---------- write POS x class summary TSV ----------
    out2 = os.path.join(HERE, "MW-UNABSORBED-CENSUS-POS-CLASS-16-09-2026.tsv")
    with io.open(out2, 'w', encoding='utf-8', newline='') as f:
        f.write("class\tpos\tn\tshare_pct\tnote\n")
        # class A: sup_7 homonym extensions (exceeding MW main max)
        posA = collections.Counter(r[6] or '(no lex)' for r in ext_rows)
        totA = sum(posA.values())
        for p, n in sorted(posA.items(), key=lambda kv: -kv[1]):
            f.write(f"homonym-extension(sup_7)\t{p}\t{n}\t{100.0*n/max(totA,1):.1f}\tvol-7 <hom> > MW main max\n")
        # class B: sup_7 extensions of PW main-body words (all)
        posB = collections.Counter((pos_of_hw.get(h, ('', ''))[0] or '(no lex)') for h in sup7_ext)
        totB = sum(posB.values())
        for p, n in sorted(posB.items(), key=lambda kv: -kv[1]):
            f.write(f"extension-of-PW-main-body(sup_7)\t{p}\t{n}\t{100.0*n/max(totB,1):.1f}\t(sup_7 headword present in pw main body)\n")
        # class C: new headwords per layer
        for layer in sorted(layer_hw):
            hws = set(layer_hw[layer])
            new = [h for h in hws if h not in pw_main_k1]
            posC = collections.Counter()
            for h in new:
                posC[h] += 1
            f.write(f"new-headword(sup_{layer})\t(not-tabulated)\t{len(new)}\t\tabsent from pw main body\n")
        # class D: MW72-never-seen (sup_7)
        never = [h for h in sup7 if h not in mw72_keys and h not in mw99_keys]
        f.write(f"never-seen-MW72-and-MW99(sup_7)\t(all)\t{len(never)}\t\tabsent from both MW editions\n")
        dropped = [h for h in sup7 if h in mw72_keys and h not in mw99_keys]
        f.write(f"dropped-between-editions(sup_7)\t(all)\t{len(dropped)}\t\tMW72 had it, MW99 lost it\n")

    # ---------- all-layers widening TSV ----------
    out3 = os.path.join(HERE, "MW-UNABSORBED-CENSUS-ALL-LAYERS-16-09-2026.tsv")
    with io.open(out3, 'w', encoding='utf-8', newline='') as f:
        f.write("layer\tentries_unique\tin_pw_main_body\tnew_headword\thom_tagged\t"
                "in_mw72\tin_mw99\tskipped_by_both\n")
        layer_hom = layer_hom_all
        for layer in sorted(layer_hw):
            hws = sorted(set(layer_hw[layer]))
            n = len(hws)
            if not n:
                continue
            in_main = sum(1 for h in hws if h in pw_main_k1)
            in72 = sum(1 for h in hws if h in mw72_keys)
            in99 = sum(1 for h in hws if h in mw99_keys)
            skip = sum(1 for h in hws if h not in mw72_keys and h not in mw99_keys)
            f.write('\t'.join(map(str, [f"sup_{layer}", n, in_main, n - in_main,
                                       layer_hom.get(layer, 0), in72, in99, skip])) + '\n')

    print(f"\nWROTE {out1} ({len(ext_rows)} rows)")
    print(f"WROTE {out2}, {out3}")

    # ---------- console summary ----------
    print("\n== homonym-extension census (vol-7 <hom> exceeding MW MAIN max) ==")
    print(f"  rows: {len(ext_rows)}")
    print("  by POS:", dict(posA.most_common()))
    print("  annexure-inclusive override (MW annexure covers this hom):",
          sum(1 for r in ext_rows if r[9] == 'no'))
    print("  MAHAVY-cited:", sum(1 for r in ext_rows if adj_corr.get(r[2], {}).get('mahavy') not in ('', '0', None)))
    print("  DCS-attested (adjudication flag):", sum(1 for r in ext_rows if adj_corr.get(r[2], {}).get('dcs') == '1'))
    print("  DCS band >=1 (direct lookup):", sum(1 for r in ext_rows if band.get(r[2], 0) >= 1))
    print("  DCS band >=3 (common+):", sum(1 for r in ext_rows if band.get(r[2], 0) >= 3))
    print("  >=1 outside-PW dict (excl sch,pwg):",
          sum(1 for r in ext_rows if adj_corr.get(r[2], {}).get('out_n', 0) >= 1))
    print("  >=2 outside-PW dicts:",
          sum(1 for r in ext_rows if adj_corr.get(r[2], {}).get('out_n', 0) >= 2))

    print("\n== canaries ==")
    for hw in ('kArin', 'kAritra'):
        hit = [r for r in ext_rows if r[2] == hw or r[1] == hw]
        print(f"  {hw}: {'EXTENSION ' + str([(r[2], r[3], r[4]) for r in hit]) if hit else 'not in extension class'}")
    kAritra = [r for r in vol7_hom_rows if r[2] == 'kAritra']
    print(f"  kAritra: vol-7 <hom> rows: {kAritra}")
    print(f"  kArin MW main max: {mw_main_max.get('kArin')} all max: {mw_all_max.get('kArin')}")

    print("\n== sup_7 extension class POS ==", dict(posB.most_common()))
    print("== sup_7 counts ==", f"unique {len(sup7)}; extensions {len(sup7_ext)}; new {len(sup7)-len(sup7_ext)}")
    never = [h for h in sup7 if h not in mw72_keys and h not in mw99_keys]
    dropped = [h for h in sup7 if h in mw72_keys and h not in mw99_keys]
    print("  never-seen (MW72+MW99):", len(never), "| dropped:", len(dropped))
    print("\n== all-layers table ==")
    for layer in sorted(layer_hw):
        hws = sorted(set(layer_hw[layer]))
        in_main = sum(1 for h in hws if h in pw_main_k1)
        in72 = sum(1 for h in hws if h in mw72_keys)
        in99 = sum(1 for h in hws if h in mw99_keys)
        skip = sum(1 for h in hws if h not in mw72_keys and h not in mw99_keys)
        print(f"  sup_{layer}: n={len(hws)} mainbody={in_main} new={len(hws)-in_main} "
              f"hom={layer_hom_all.get(layer,0)} mw72={in72} mw99={in99} skipped={skip}")


if __name__ == '__main__':
    main()
