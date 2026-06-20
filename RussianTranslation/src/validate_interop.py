#!/usr/bin/env python
"""Validate minimal TEI/OntoLex/reverse-index release artifacts."""
import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
DEFAULT_RELEASE = os.path.join(ROOT, 'release')


def fail(msg):
    raise ValueError(msg)


def validate_tei(path):
    if not os.path.exists(path):
        fail('missing TEI file: %s' % path)
    root = ET.parse(path).getroot()
    if not root.tag.endswith('TEI'):
        fail('TEI root is not TEI: %s' % root.tag)
    entries = root.findall('.//{http://www.tei-c.org/ns/1.0}entry')
    if not entries:
        fail('TEI contains no entries')
    return len(entries)


def validate_ontolex(path):
    if not os.path.exists(path):
        fail('missing OntoLex file: %s' % path)
    text = open(path, encoding='utf-8').read()
    if not text.strip():
        fail('OntoLex Turtle is empty')
    n = text.count('ontolex:LexicalEntry')
    if n < 1:
        fail('OntoLex Turtle contains no lexical entries')
    return n


def validate_reverse(path):
    if not os.path.exists(path):
        fail('missing reverse index: %s' % path)
    n = 0
    with open(path, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            for field in ('ru', 'key1'):
                if not row.get(field):
                    fail('reverse index line %d missing %s' % (i, field))
            if 'source' not in row or 'ref' not in row:
                fail('reverse index line %d missing source/ref' % i)
            n += 1
    if not n:
        fail('reverse index is empty')
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default=DEFAULT_RELEASE)
    args = ap.parse_args()
    tei = validate_tei(os.path.join(args.dir, 'tei_lex0.xml'))
    ttl = validate_ontolex(os.path.join(args.dir, 'ontolex.ttl'))
    rev = validate_reverse(os.path.join(args.dir, 'reverse_index.jsonl'))
    print('interop validation OK: TEI entries=%d | OntoLex entries=%d | reverse rows=%d'
          % (tei, ttl, rev))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('INTEROP CHECK FAILED: %s' % e, file=sys.stderr)
        raise SystemExit(1)
