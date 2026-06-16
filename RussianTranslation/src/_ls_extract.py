#!/usr/bin/env python
"""Extract <ls> source abbreviations from PWG → frequency table.

The pwg_ru harvest matches each PWG sense's <ls> citation (the work it quotes)
to a corpus text, so a sense cited from the Ṛgveda harvests Vedic Russian. This
is step 1: enumerate every <ls> source key PWG actually uses, with counts, so we
can map the high-frequency ones to corpus_strata.json works.

  python _ls_extract.py [topN]
"""
import os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PWG = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02', 'pwg', 'pwg.txt'))

LS = re.compile(r'<ls\b([^>]*)>(.*?)</ls>', re.S)
NATTR = re.compile(r'\bn\s*=\s*"([^"]*)"')


def source_key(attr, inner):
    """Source name = the leading abbreviation tokens before the numeric reference.
    Keeps multi-part names (ŚAT. BR., BHĀG. P.) but drops the volume/verse refs,
    so MBH / MBH. / 'MBH. 3,13096' all collapse to MBH."""
    m = NATTR.search(attr)
    raw = m.group(1) if (m and m.group(1).strip()) else re.sub(r'<[^>]+>', '', inner)
    out = []
    for t in raw.strip().split():
        if any(ch.isdigit() for ch in t):   # first ref token → stop
            break
        out.append(t)
        if len(out) >= 4:                    # cap source-name length
            break
    key = re.sub(r'\s+', ' ', ' '.join(out)).strip().rstrip('.').strip()
    return key


def main():
    topn = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    if not os.path.exists(PWG):
        sys.exit('PWG source not found: ' + PWG)
    freq = collections.Counter()
    samples = {}
    total = 0
    with open(PWG, encoding='utf-8') as f:
        data = f.read()
    for m in LS.finditer(data):
        attr, inner = m.group(1), m.group(2)
        key = source_key(attr, inner)
        if not key:
            continue
        freq[key] += 1; total += 1
        if key not in samples:
            samples[key] = re.sub(r'<[^>]+>', '', inner).strip()[:50]
    print('PWG <ls> citations: %d total, %d distinct source keys' % (total, len(freq)))
    print('top %d sources (key | count | sample):' % topn)
    for k, c in freq.most_common(topn):
        print('  %-16s %7d   %s' % (k, c, samples.get(k, '')))


if __name__ == '__main__':
    main()
