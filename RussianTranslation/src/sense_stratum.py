#!/usr/bin/env python
"""sense_stratum.py — deterministic per-sense stratum («страт») feed for pwg_ru cards.

Implements the "optional hardening" of pwg_ru_prompts/6_merged_translate.md: instead of
letting the translator INFER each sense's era badge from its citations (guess-prone), we
precompute it deterministically from ls_source_map.json (every <ls> siglum carries a Renou
state I-V + a date) and feed it to the translator — the same pattern that eliminated the
F12 NWS owner-map error.

For every PWG headword with explicitly numbered senses, emits per top-level sense:
  sense_no, renou_oldest, renou_youngest, stratum_label (Russian), date_min, date_max,
  n_dated_citations.  Senses with only kośa/grammarian (undated) citations -> label «–».

Output: src/pwg_sense_stratum.jsonl  (one JSON object per headword: {key1, senses:[...]}).

  python sense_stratum.py [--head arTa]   # print one headword to stdout, no write
  python sense_stratum.py                 # build the full feed
"""
import json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import renou  # noqa: E402

SMAP = renou.load_map('pwg')
PWG = os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02', 'pwg', 'pwg.txt')

SENSE_RE = re.compile(r'<div n="1">\s*(?:[—-]\s*)?(\d+)\)')
LS_RE = re.compile(r'<ls\b[^>]*>(.*?)</ls>', re.S)

# Renou state -> Russian era label (matches the prompt's vocabulary).
RU_STATE = {'I': 'ведийский', 'II': 'паниниевский', 'III': 'эпический',
            'IV': 'классический', 'V': 'буддийско-джайнский'}
_ORD = {s: i for i, s in enumerate(('I', 'II', 'III', 'IV', 'V'))}


def stratum_label(oldest, youngest):
    """Russian range label, e.g. 'ведийский' or 'ведийский–классический'."""
    if not oldest:
        return '–'
    if oldest == youngest:
        return RU_STATE[oldest]
    return f'{RU_STATE[oldest]}–{RU_STATE[youngest]}'


def entries(path):
    buf, k1 = [], None
    for line in open(path, encoding='utf-8'):
        if line.startswith('<L>'):
            m = re.search(r'<k1>([^<]*)', line)
            k1 = m.group(1) if m else None
            buf = [line]
        elif line.startswith('<LEND>'):
            if k1 is not None:
                yield k1, ''.join(buf)
            buf, k1 = [], None
        else:
            buf.append(line)


def sense_strata(body):
    hits = list(SENSE_RE.finditer(body))
    if len(hits) < 1:
        return []
    out = []
    for i, m in enumerate(hits):
        start = m.start()
        end = hits[i + 1].start() if i + 1 < len(hits) else len(body)
        seg = body[start:end]
        states, dates = set(), []
        for lm in LS_RE.finditer(seg):
            for k in renou.keys_in_text(lm.group(0), 'pwg'):
                rec = SMAP.get(k)
                if rec:
                    states.add(rec['renou'])
                    if rec.get('date') is not None:
                        dates.append(rec['date'])
        if states:
            oldest = min(states, key=_ORD.get)
            youngest = max(states, key=_ORD.get)
        else:
            oldest = youngest = ''
        out.append({
            'sense_no': int(m.group(1)),
            'renou_oldest': oldest,
            'renou_youngest': youngest,
            'stratum_label': stratum_label(oldest, youngest),
            'date_min': min(dates) if dates else None,
            'date_max': max(dates) if dates else None,
            'n_dated_citations': len(dates),
        })
    return out


def main():
    if '--head' in sys.argv:
        target = sys.argv[sys.argv.index('--head') + 1]
        for k1, body in entries(PWG):
            if k1 == target:
                print(json.dumps({'key1': k1, 'senses': sense_strata(body)},
                                 ensure_ascii=False, indent=2))
                return
        print(f'headword {target!r} not found', file=sys.stderr)
        return

    out = os.path.join(HERE, 'pwg_sense_stratum.jsonl')
    n = senses = 0
    with open(out, 'w', encoding='utf-8') as fh:
        for k1, body in entries(PWG):
            ss = sense_strata(body)
            if not ss:
                continue
            fh.write(json.dumps({'key1': k1, 'senses': ss}, ensure_ascii=False) + '\n')
            n += 1
            senses += len(ss)
    print(f'wrote {out}: {n:,} headwords, {senses:,} senses', file=sys.stderr)


if __name__ == '__main__':
    main()
