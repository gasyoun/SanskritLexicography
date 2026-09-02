#!/usr/bin/env python
"""H3948 / FINDINGS §453 — census of PWG's enumeration-marker tiers.

READ-ONLY over csl-orig v02/pwg/pwg.txt. Writes nothing, touches no store.

§453 proposes teaching microstructure.py the pattern H1350's validator uses,
``([0-9]{1,3}|[a-z]|[α-ωϑϰ]|[IVU])[)〉]``.  This census exists to check that
proposal against the corpus BEFORE it goes into the live parser, because a
marker class admitted by mistake does not merely miss a split — it invents
one, in production, on 11.6k already-promoted store rows.

For every candidate class it reports three numbers, narrowing left to right:

  raw            every textual hit
  lookbehind_ok  hits that also satisfy microstructure.MARK's own lookbehind
                 ``(?<![^\\s—])`` — preceded by whitespace / em-dash / start
  genuine        of those, the ones NOT inside a microstructure.protected()
                 span (<ls>, <is>, any tag, {#…#} Sanskrit, {%…%} German)

Only the `genuine` column is a sense marker. Usage:

  python pwg_enum_tier_census.py              full census + roman nesting
  python pwg_enum_tier_census.py --limit 5000 first N records (smoke)
"""
import os, re, sys, collections

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pwg_mask                                   # noqa: E402
from microstructure import protected              # noqa: E402

LOOKBEHIND = re.compile(r'(?<![^\s—])')

# Candidate classes, each as (name, token-regex-source). Closers are applied
# separately so ASCII ')' and the PWG glyph '〉' can be scored apart — that
# separation is the whole point of the census.
CLASSES = [
    ('digit12', r'\d{1,2}'),            # tier 1, already handled (§447)
    ('digit3',  r'\d{3}'),              # §453 widening {1,2} -> {1,3}
    ('latin',   r'[a-z]'),              # tier 2, already handled (§447)
    ('greek',   r'[α-ωϑϰ]'),            # §453 candidate
    ('roman1',  r'[IVU]'),              # §453 candidate, as literally written
    ('romanN',  r'[IV]{2,}'),           # multi-character roman, not in §453
]
CLOSERS = [('ascii', r'\)'), ('glyph', r'〉')]

PATTERNS = [(name, closer, re.compile('(' + tok + ')' + cl))
            for name, tok in CLASSES for closer, cl in CLOSERS]

# A genuine roman marker opens a division; these ask whether digit markers
# nest UNDER it (making roman super-ordinate) or beside it (a fourth sub-tier).
DIGIT_MARK = re.compile(r'(?<![^\s—])(\d{1,2})[)〉]')
ROMAN_MARK = re.compile(r'(?<![^\s—])([IV]+)〉')
DIV_N = re.compile(r'<div\s+n="(\d+)"')


def genuine_spans(body, pat):
    """Yield (start, token) for pat's hits that survive lookbehind + protection."""
    spans = protected(body)
    for m in pat.finditer(body):
        p = m.start()
        if not LOOKBEHIND.match(body, p):
            continue
        if any(a <= p < b for a, b in spans):
            continue
        yield p, m.group(1)


def census(limit=None):
    raw = collections.Counter()
    lb_ok = collections.Counter()
    genuine = collections.Counter()
    examples = collections.defaultdict(list)
    roman_rows = []
    n_rec = 0

    for buf in pwg_mask.records(limit):
        n_rec += 1
        body = '\n'.join(buf[1:])
        spans = protected(body)

        def inside(p):
            return any(a <= p < b for a, b in spans)

        for name, closer, pat in PATTERNS:
            key = '%s/%s' % (name, closer)
            for m in pat.finditer(body):
                p = m.start()
                raw[key] += 1
                if not LOOKBEHIND.match(body, p):
                    continue
                lb_ok[key] += 1
                if inside(p):
                    continue
                genuine[key] += 1
                if len(examples[key]) < 4:
                    examples[key].append(
                        (buf[0].split('<pc>')[0], body[max(0, p - 40):p + 40]
                         .replace('\n', ' ')))

        # roman nesting: is the digit tier under it, or beside it?
        romans = [(p, t) for p, t in genuine_spans(body, ROMAN_MARK)]
        if romans:
            k1 = buf[0].split('<k1>')[1].split('<k2>')[0] if '<k1>' in buf[0] else '?'
            digits = [p for p, _ in genuine_spans(body, DIGIT_MARK)]
            for i, (p, tok) in enumerate(romans):
                end = romans[i + 1][0] if i + 1 < len(romans) else len(body)
                nested = sum(1 for d in digits if p < d < end)
                divs = DIV_N.findall(body[:p])
                roman_rows.append((k1, tok, nested, divs[-1] if divs else '-'))

    return n_rec, raw, lb_ok, genuine, examples, roman_rows


def main():
    limit = None
    if '--limit' in sys.argv:
        limit = int(sys.argv[sys.argv.index('--limit') + 1])

    n_rec, raw, lb_ok, genuine, examples, roman_rows = census(limit)

    print('PWG enumeration-tier census (H3948 / FINDINGS §453)')
    print('corpus: %s' % pwg_mask.PWG)
    print('records scanned: %d' % n_rec)
    print()
    print('%-16s %10s %14s %10s' % ('class/closer', 'raw', 'lookbehind_ok', 'genuine'))
    print('-' * 54)
    for name, tok in CLASSES:
        for closer, _ in CLOSERS:
            key = '%s/%s' % (name, closer)
            if not raw[key]:
                continue
            print('%-16s %10d %14d %10d' % (key, raw[key], lb_ok[key], genuine[key]))

    print()
    print('Genuine hits for the two classes §453 wants to ADD:')
    for key in ('greek/glyph', 'greek/ascii', 'roman1/glyph', 'roman1/ascii',
                'romanN/glyph', 'romanN/ascii', 'digit3/ascii', 'digit3/glyph'):
        if genuine[key]:
            print('  %-14s %5d   e.g. %s' % (key, genuine[key],
                                             examples[key][0][1][:78]))

    print()
    print('Roman-marker nesting — does the digit tier sit UNDER roman?')
    print('%-14s %-6s %8s %10s' % ('key1', 'token', 'digits', '<div n=>'))
    print('-' * 42)
    for k1, tok, nested, div in roman_rows:
        print('%-14s %-6s %8d %10s' % (k1[:14], tok, nested, div))
    if roman_rows:
        with_kids = sum(1 for r in roman_rows if r[2] > 0)
        print()
        print('roman markers: %d   with digit markers nested under them: %d   '
              'leaf-only divisions: %d'
              % (len(roman_rows), with_kids, len(roman_rows) - with_kids))
        divs = collections.Counter(r[3] for r in roman_rows)
        print('preceding <div n=> depth: %s' % dict(divs))

    print()
    print('TOTAL genuine four-tier markers unrecognised by the pre-H3948 parser: %d'
          % (genuine['greek/glyph'] + genuine['roman1/glyph'] + genuine['romanN/glyph']))


if __name__ == '__main__':
    main()
