#!/usr/bin/env python
"""analyze_cross_dict.py — extend the PWG sense-order audit to MW, AP90, Koch.

Turns the qualitative cross-dict classification of HANDOFF_sense_ordering.md into
numbers, on each dictionary's own microstructure:

  MW   senses are split across consecutive <L> records sharing k1 + bare k2 (the
       <e>NA continuation records); compounds carry "—" in k2. Dated via
       ls_source_map_mw.json. -> full #1 (sense-1-oldest, tau) + #3 (within-sense
       chronology) + Vedic-citation density.
  AP90 senses are numbered {@N@} inside one <L> record. No date map exists for
       Apte, so we measure Vedic-citation DENSITY (Apte's own sigla) — the
       discriminator for "no historical apparatus". Manu = 'Ms.' is CLASSICAL,
       excluded from the Vedic set on purpose.
  Koch (Kochergina, koch.jsonl) modern Russian learner's dict: confirm it carries
       ZERO citation apparatus -> sense order is logical-semantic by construction.

PWG Vedic density is recomputed here too, so the 3-way density table is apples-to-apples.

Output: research/cross_dict_metrics.{md,json}.  Usage: python analyze_cross_dict.py
"""
import json, os, re, sys, statistics

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'src')
sys.path.insert(0, SRC)
import renou  # noqa: E402

ORIG = os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02')
MW_TXT = os.path.join(ORIG, 'mw', 'mw.txt')
AP90_TXT = os.path.join(ORIG, 'ap90', 'ap90.txt')
PWG_TXT = os.path.join(ORIG, 'pwg', 'pwg.txt')
KOCH = os.path.join(SRC, 'koch.jsonl')

LS_RE = re.compile(r'<ls\b[^>]*>(.*?)</ls>', re.S)

# Vedic source keys (Renou state I) per the existing maps.
PWG_VEDIC = {k for k, v in renou.load_map('pwg').items() if v.get('renou') == 'I'}
MW_VEDIC = {k for k, v in renou.load_map('mw').items() if v.get('renou') == 'I'}
# AP90 has no map; match Apte's own Vedic sigla in raw <ls> text. Manu ('Ms.')
# is classical and deliberately absent.
AP90_VEDIC_RE = re.compile(
    r'\b(Rv|Av|Yv|Sv|Vāj\.?\s*S|Śat\.?\s*Br|Ait\.?\s*Br|Tāṇḍya|Gop\.?\s*Br|'
    r'Taitt|Ts|Maitr|Kāṭh|Bṛ\.?\s*Up|Ch\.?\s*Up|Kaṭh\.?\s*Up|Kena|Muṇḍ|'
    r'Praśna|Māṇḍ|Ait\.?\s*Up|Śvet|Nir|Uṇ)\b')


def kendall_tau(seq):
    n = len(seq)
    if n < 2:
        return None
    conc = disc = 0
    for i in range(n):
        for j in range(i + 1, n):
            if seq[i] < seq[j]:
                conc += 1
            elif seq[i] > seq[j]:
                disc += 1
    tot = conc + disc
    return (conc - disc) / tot if tot else None


def pct(a, b):
    return round(100.0 * a / b, 1) if b else None


# ---------------------------------------------------------------- MW

def mw_records(path):
    """Yield (k1, k2, hom, text) per <L>..<LEND>."""
    buf, hdr = [], None
    for line in open(path, encoding='utf-8'):
        if line.startswith('<L>'):
            k1 = (re.search(r'<k1>([^<]*)', line) or [None, None])[1]
            k2 = (re.search(r'<k2>([^<]*)', line) or [None, None])[1]
            h = re.search(r'<h>(\d+)', line)
            hdr = (k1, k2, h.group(1) if h else '')
            buf = [line]
        elif line.startswith('<LEND>'):
            if hdr:
                yield (*hdr, ''.join(buf))
            buf, hdr = [], None
        else:
            buf.append(line)


def analyze_mw():
    a1 = {'multi': 0, 'sense1_oldest': 0, 'taus': []}
    a3 = {'senses2': 0, 'monotone': 0, 'taus': [], 'pairs': 0, 'nondec': 0}
    vd = {'cited_senses': 0, 'vedic_senses': 0}
    # group consecutive records sharing (k1,k2,hom); skip compounds (— in k2)
    group, key = [], None
    smap = renou.load_map('mw')

    def flush(g):
        senses = []  # (pos, oldest_date, ordered_dates, has_vedic)
        for pos, txt in enumerate(g):
            dates, has_vedic = [], False
            for m in LS_RE.finditer(txt):
                for k in renou.keys_in_text(m.group(0), 'mw'):
                    rec = smap.get(k)
                    if rec:
                        if rec.get('date') is not None:
                            dates.append(rec['date'])
                        if k in MW_VEDIC:
                            has_vedic = True
            if dates or has_vedic:
                vd['cited_senses'] += 1
                if has_vedic:
                    vd['vedic_senses'] += 1
            if len(dates) >= 2:
                a3['senses2'] += 1
                t = kendall_tau(dates)
                if t is not None:
                    a3['taus'].append(t)
                    if t == 1.0:
                        a3['monotone'] += 1
                for x, y in zip(dates, dates[1:]):
                    a3['pairs'] += 1
                    if x <= y:
                        a3['nondec'] += 1
            if dates:
                senses.append((pos, min(dates)))
        if len(senses) >= 2:
            a1['multi'] += 1
            od = [d for _, d in senses]
            if od[0] == min(od):
                a1['sense1_oldest'] += 1
            t = kendall_tau(od)
            if t is not None:
                a1['taus'].append(t)

    for k1, k2, hom, txt in mw_records(MW_TXT):
        if not k1 or not k2 or '—' in (k2 or ''):  # compound or junk
            if group:
                flush(group)
            group, key = [], None
            continue
        this = (k1, k2, hom)
        if this != key:
            if group:
                flush(group)
            group, key = [txt], this
        else:
            group.append(txt)
    if group:
        flush(group)

    return {
        'sense_grouping': 'consecutive <L> records sharing k1+k2(bare)+hom; compounds (—) excluded',
        'entries_multisense_dated': a1['multi'],
        'pct_sense1_is_oldest': pct(a1['sense1_oldest'], a1['multi']),
        'mean_tau_printed_vs_date': round(statistics.mean(a1['taus']), 3) if a1['taus'] else None,
        'within_sense_senses_ge2_dated': a3['senses2'],
        'pct_within_sense_strict_chrono': pct(a3['monotone'], a3['senses2']),
        'pct_adjacent_pairs_nondecreasing': pct(a3['nondec'], a3['pairs']),
        'vedic_density_pct': pct(vd['vedic_senses'], vd['cited_senses']),
        'vedic_density_basis_cited_senses': vd['cited_senses'],
    }


# ---------------------------------------------------------------- PWG (Vedic density only; #1/#3 already in analyze_sense_order.py)

PWG_SENSE_RE = re.compile(r'<div n="1">\s*(?:[—-]\s*)?(\d+)\)')


def analyze_pwg_vedic():
    smap = renou.load_map('pwg')
    cited = vedic = 0
    buf = []
    in_entry = False
    for line in open(PWG_TXT, encoding='utf-8'):
        if line.startswith('<L>'):
            buf, in_entry = [line], True
        elif line.startswith('<LEND>'):
            body = ''.join(buf)
            hits = list(PWG_SENSE_RE.finditer(body))
            spans = [(m.start(), (hits[i + 1].start() if i + 1 < len(hits) else len(body)))
                     for i, m in enumerate(hits)] or [(0, len(body))]
            for s, e in spans:
                seg = body[s:e]
                has_cite = has_vedic = False
                for m in LS_RE.finditer(seg):
                    for k in renou.keys_in_text(m.group(0), 'pwg'):
                        if smap.get(k):
                            has_cite = True
                            if k in PWG_VEDIC:
                                has_vedic = True
                if has_cite:
                    cited += 1
                    if has_vedic:
                        vedic += 1
            in_entry = False
        elif in_entry:
            buf.append(line)
    return {'vedic_density_pct': pct(vedic, cited), 'basis_cited_senses': cited}


# ---------------------------------------------------------------- AP90

AP_SENSE_RE = re.compile(r'\{@-*\d+@\}')


def analyze_ap90():
    cited = vedic = 0
    total_senses = total_ls = 0
    buf = []
    in_entry = False
    multi = 0
    for line in open(AP90_TXT, encoding='utf-8'):
        if line.startswith('<L>'):
            buf, in_entry = [line], True
        elif line.startswith('<LEND>'):
            body = ''.join(buf)
            hits = list(AP_SENSE_RE.finditer(body))
            if len(hits) >= 2:
                multi += 1
            spans = [(m.start(), (hits[i + 1].start() if i + 1 < len(hits) else len(body)))
                     for i, m in enumerate(hits)] or [(0, len(body))]
            for s, e in spans:
                seg = body[s:e]
                total_senses += 1
                lss = LS_RE.findall(seg)
                total_ls += len(lss)
                if lss:
                    cited += 1
                    if any(AP90_VEDIC_RE.search(x) for x in lss):
                        vedic += 1
            in_entry = False
        elif in_entry:
            buf.append(line)
    return {
        'sense_marker': '{@N@} within one <L>',
        'multisense_entries': multi,
        'vedic_density_pct': pct(vedic, cited),
        'basis_cited_senses': cited,
        'note': 'Vedic matched on Apte sigla (Rv/Av/Brāhmaṇa/Upaniṣad/Nir); Manu(Ms.)=Classical, excluded.',
    }


# ---------------------------------------------------------------- Koch

def analyze_koch():
    n = 0
    with_ls = 0
    numbered = 0
    NUM = re.compile(r'(^|\s)[1-9]\)')
    for line in open(KOCH, encoding='utf-8'):
        try:
            r = json.loads(line)
        except Exception:
            continue
        n += 1
        g = r.get('gloss', '') or ''
        if '<ls>' in g or re.search(r'\b(1[0-9]{2,3})\b', g):  # any year-like citation
            with_ls += 1
        if NUM.search(g):
            numbered += 1
    return {
        'records': n,
        'records_with_citation_apparatus': with_ls,
        'pct_with_apparatus': pct(with_ls, n),
        'pct_with_numbered_senses_in_gloss': pct(numbered, n),
        'reading': 'modern learner dict: ~0 dated citations -> sense order is logical-semantic by construction',
    }


def main():
    report = {
        'mw': analyze_mw(),
        'pwg_vedic_density': analyze_pwg_vedic(),
        'ap90': analyze_ap90(),
        'koch': analyze_koch(),
    }
    out = os.path.join(HERE, 'cross_dict_metrics.json')
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print('\nwrote', out, file=sys.stderr)


if __name__ == '__main__':
    main()
