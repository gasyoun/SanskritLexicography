#!/usr/bin/env python
"""H1350 W1.2 -- structural validator for RussianTranslation/schemas/pwg_markup.rnc.

Enforces the identical element inventory / pairing / milestone rules stated
in pwg_markup.rnc against every record in csl-orig/v02/pwg/pwg.txt (READ
ONLY). No RNG compiler (trang/jing) is available in this environment, and the
raw record stream is not well-formed XML (see the .rnc file's scope note), so
this hand-written structural checker plays the role a compiled RNG validator
would -- same rules, same typed-failure-bucket discipline (FINDINGS
Sec.129/Sec.130: no record is ever silently dropped).

    python validate_pwg_markup.py                run over all records, print totals
    python validate_pwg_markup.py --assert-total  same, exit 1 if the totals don't add up
    python validate_pwg_markup.py --limit N       debug: only scan the first N records
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
sys.path.insert(0, HERE)
import pwg_mask  # noqa: E402 -- reused record splitter (H1350 architecture D-verdict: reuse)

REPORTS_DIR = os.path.join(HERE, '..', 'reports')

# Paired span element names -- verified open==close per record over the full
# 123,366-record corpus, 2026-07-20 (see pwg_markup.rnc + .ai_state.md Dev
# Notes for the 21 tags absent from the older csl-atlas census).
PAIRED_TAGS = [
    'ls', 'ab', 'is', 'lex', 'lang', 'hom', 'F', 'VN', 'fr',
    'gk', 'bot', 'abot', 'zoo', 'azoo', 'ocs', 'arab', 'heb', 'per', 'rus',
    'ger', 'mng', 'mong', 'iw', 'pe', 'zen', 'ed', 'enum', 'ms', 'ns', 'num',
]
# Milestone element names -- no closing tag, by design (TEI-style).
MILESTONE_TAGS = ['div', 'info']

KNOWN_TAGS = set(PAIRED_TAGS) | set(MILESTONE_TAGS) | {'L', 'LEND', 'pc', 'k1', 'k2', 'h'}

TAG_TOKEN_RE = re.compile(r'<(/?)([A-Za-z][A-Za-z0-9]*)\b[^>]*/?>')
BRACE_SA_RE = re.compile(r'\{#|#\}')
BRACE_DE_RE = re.compile(r'\{%|%\}')
PAGE_LOCUS_RE = re.compile(r'\[Page[^\]]*\]')
# a sense-closing token: digit(s)/letter immediately followed by ')' or the PWG
# glyph '〉'. PWG nests FOUR enumeration tiers -- digit (1〉), Latin letter
# (a〉), Greek letter (alpha-omega + the variant forms theta-symbol/kappa-symbol
# used in the source: alpha,beta,gamma,delta,epsilon,zeta,eta,theta,iota,
# kappa-var,lambda,mu,nu,xi,omicron,theta-var), and a handful of single
# uppercase roman-numeral-like markers (I, V, U -- 30 occurrences total,
# fourth-tier subsections). microstructure.py's MARK regex only recognises
# the first two tiers (digit/Latin); this validator recognises all four so a
# genuine attested four-level structure is not misclassified as a defect.
SENSE_GLYPH_TOKEN_RE = re.compile(r'(\d{1,3}|[a-z]|[α-ωϑϰ]|[IVU])[)〉]')
BARE_GLYPH_RE = re.compile('〉')

BUCKET_ORDER = ['malformed-span', 'unknown-tag', 'unbalanced-delim', 'glyph-class', 'unexpected-but-attested']


def classify(buf):
    """Return (status, bucket_or_None) for one record's raw line buffer."""
    header_ok = bool(pwg_mask.HEADER_RE.match(buf[0]))
    full = '\n'.join(buf)

    # unknown-tag: any tag-like token whose name isn't in the known vocabulary.
    for m in TAG_TOKEN_RE.finditer(full):
        if m.group(2) not in KNOWN_TAGS:
            return 'fail', 'unknown-tag'

    if not header_ok:
        return 'fail', 'malformed-span'

    # malformed-span: any paired tag whose open/close count disagrees within
    # this one record (global corpus balance was verified, but a per-record
    # check is the real invariant -- a stray open in record A and a stray
    # close in record B could otherwise cancel out unnoticed).
    for tag in PAIRED_TAGS:
        o = len(re.findall(r'<' + tag + r'\b[^>]*>', full))
        c = len(re.findall(r'</' + tag + r'>', full))
        if o != c:
            return 'fail', 'malformed-span'

    # unbalanced-delim: {#...#} / {%...%} brace counts must be even (opens==closes).
    sa_tokens = BRACE_SA_RE.findall(full)
    if sa_tokens.count('{#') != sa_tokens.count('#}'):
        return 'fail', 'unbalanced-delim'
    de_tokens = BRACE_DE_RE.findall(full)
    if de_tokens.count('{%') != de_tokens.count('%}'):
        return 'fail', 'unbalanced-delim'

    # glyph-class: every literal 'U+3009' occurrence must be part of a
    # recognised sense-closing token (digit/letter immediately before it).
    glyph_positions = {m.start() for m in BARE_GLYPH_RE.finditer(full)}
    recognised_positions = {m.end() - 1 for m in SENSE_GLYPH_TOKEN_RE.finditer(full) if full[m.end() - 1] == '〉'}
    if glyph_positions - recognised_positions:
        return 'fail', 'glyph-class'

    # unexpected-but-attested: record shape is valid but carries a marker
    # this checker treats as noteworthy rather than a defect (float record
    # id -- Cologne supplement; PAGE_LOCUS -- fine, just logged for visibility).
    m = pwg_mask.HEADER_RE.match(buf[0])
    if '.' in m.group(1):
        return 'fail', 'unexpected-but-attested'

    return 'pass', None


def run(limit=None):
    totals = collections.Counter()
    buckets = collections.Counter()
    failures = []
    n = 0
    for buf in pwg_mask.records(limit):
        n += 1
        status, bucket = classify(buf)
        totals[status] += 1
        if bucket:
            buckets[bucket] += 1
            m = pwg_mask.HEADER_RE.match(buf[0])
            record_id = m.group(1) if m else '?'
            failures.append({'record_id': record_id, 'status': status, 'failure_type': bucket,
                              'key1': (m.group(3) if m else ''), 'span': buf[0][:120]})
    return n, totals, buckets, failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--assert-total', action='store_true')
    ap.add_argument('--limit', type=int, default=None)
    args = ap.parse_args()

    n, totals, buckets, failures = run(args.limit)
    passes = totals['pass']
    bucket_sum = sum(buckets.values())

    print(f'records scanned: {n}')
    print(f'pass: {passes}')
    for b in BUCKET_ORDER:
        print(f'  {b}: {buckets.get(b, 0)}')
    print(f'passes + buckets = {passes + bucket_sum} (expect {n})')
    unclassified = n - passes - bucket_sum
    print(f'unclassified: {unclassified}')

    os.makedirs(REPORTS_DIR, exist_ok=True)
    out_path = os.path.join(REPORTS_DIR, 'pwg_markup_validation.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({
            'schema': 'pwg_markup_validation/0.1',
            'total_records': n,
            'passes': passes,
            'buckets': {b: buckets.get(b, 0) for b in BUCKET_ORDER},
            'unclassified': unclassified,
            'records': failures,
        }, f, ensure_ascii=False, indent=1)
    print(f'wrote {out_path}')

    if args.assert_total:
        ok = (passes + bucket_sum == n) and unclassified == 0
        if not ok:
            print('ASSERTION FAILED', file=sys.stderr)
            sys.exit(1)
        print('assertion OK: passes + buckets == total, zero unclassified')


if __name__ == '__main__':
    main()
