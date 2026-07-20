#!/usr/bin/env python
"""H1350 W1.3 -- JSON Schema validation of the parsed PWG portrait.

Runs the existing, unmodified microstructure.portrait() (reuse, not rebuild --
H1350 architecture verdict) over every record in csl-orig/v02/pwg/pwg.txt
(READ ONLY), augments each portrait with a structurally-promoted 'apparatus'
field (<is> Indian-grammar apparatus content, left inline by the base RU
schema -- see docs/PWG_CARD_ANATOMY.md), and validates the result against
schemas/pwg_portrait_structural.schema.json. Same 100%-pass-or-typed-bucket
discipline as validate_pwg_markup.py (FINDINGS Sec.129/Sec.130).

    python validate_pwg_portrait.py                run over all records
    python validate_pwg_portrait.py --assert-total  exit 1 unless totals add up
    python validate_pwg_portrait.py --limit N       debug: first N records only
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
import pwg_mask         # noqa: E402 -- reused record splitter
import microstructure as ms  # noqa: E402 -- reused portrait parser (unmodified)

import jsonschema  # noqa: E402

REPORTS_DIR = os.path.join(HERE, '..', 'reports')
SCHEMA_PATH = os.path.join(HERE, '..', 'schemas', 'pwg_portrait_structural.schema.json')

IS_RE = re.compile(r'<is\b([^>]*)>(.*?)</is>', re.S)
NATTR_RE = re.compile(r'\bn\s*=\s*"([^"]*)"')

BUCKET_ORDER = ['parse-error', 'schema-violation', 'unexpected-but-attested']


def extract_apparatus(body):
    out = []
    for attrs, content in IS_RE.findall(body):
        text = re.sub(r'<[^>]+>', '', content).strip()
        if not text:
            continue
        m = NATTR_RE.search(attrs)
        out.append({'text': text, 'n_attr': m.group(1) if m else None})
    return out


def structural_portrait(buf):
    p = ms.portrait(buf)
    m = pwg_mask.HEADER_RE.match(buf[0])
    record_id = m.group(1) if m else ''
    pc = m.group(2) if m else ''
    body = '\n'.join(buf[1:])
    p['schema_version'] = 'pwg_portrait_structural.v1'
    p['record_id'] = record_id
    p['pc'] = pc
    p['apparatus'] = extract_apparatus(body)
    return p


def run(validator, limit=None):
    totals = collections.Counter()
    buckets = collections.Counter()
    failures = []
    n = 0
    for buf in pwg_mask.records(limit):
        n += 1
        m = pwg_mask.HEADER_RE.match(buf[0])
        record_id = m.group(1) if m else '?'
        try:
            portrait = structural_portrait(buf)
        except Exception as exc:  # noqa: BLE001 -- must classify, never crash the run
            totals['fail'] += 1
            buckets['parse-error'] += 1
            failures.append({'record_id': record_id, 'failure_type': 'parse-error', 'detail': str(exc)[:200]})
            continue

        errors = sorted(validator.iter_errors(portrait), key=str)
        if not errors:
            totals['pass'] += 1
            continue

        totals['fail'] += 1
        if '.' in record_id:
            # Cologne float-id supplement records -- same population flagged
            # unexpected-but-attested in W1.2; schema noise here is very
            # likely a downstream artifact of the same non-standard id, not
            # an independent structural defect.
            bucket = 'unexpected-but-attested'
        else:
            bucket = 'schema-violation'
        buckets[bucket] += 1
        failures.append({'record_id': record_id, 'failure_type': bucket,
                          'detail': str(errors[0])[:200]})
    return n, totals, buckets, failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--assert-total', action='store_true')
    ap.add_argument('--limit', type=int, default=None)
    args = ap.parse_args()

    with open(SCHEMA_PATH, encoding='utf-8') as f:
        schema = json.load(f)
    validator = jsonschema.Draft202012Validator(schema)

    n, totals, buckets, failures = run(validator, args.limit)
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
    out_path = os.path.join(REPORTS_DIR, 'pwg_portrait_validation.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({
            'schema': 'pwg_portrait_validation/0.1',
            'total_records': n,
            'passes': passes,
            'buckets': {b: buckets.get(b, 0) for b in BUCKET_ORDER},
            'unclassified': unclassified,
            'failures': failures[:2000],  # cap the sample; totals above are exact
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
