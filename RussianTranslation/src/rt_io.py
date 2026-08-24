#!/usr/bin/env python
"""rt_io — canonical UTF-8 JSON/JSONL file helpers for RussianTranslation/src.

One implementation of the read/write boilerplate that had been re-defined in
a dozen top-level modules. Contract: JSONL is one compact JSON object per
line, ``ensure_ascii=False`` (Cyrillic stays literal), LF newlines, writes
create missing parent directories, reads are strict UTF-8.

Consumers:
  * ``pwg_tm_canonical`` re-exports ``read_jsonl``/``write_jsonl``/
    ``write_json`` so every existing ``import pwg_tm_canonical as C``
    consumer keeps its surface (H-wave refactor, PR-A).
  * pilot/ keeps its own atomic writers (window_common) — out of scope here.

  python src/rt_io.py --selftest
"""
from __future__ import annotations

import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def read_jsonl(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def iter_jsonl(path, limit=None):
    """Yield parsed rows; silently yields nothing for a missing/empty path."""
    if not path or not os.path.exists(path):
        return
    n = 0
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)
            n += 1
            if limit and n >= limit:
                break


def append_jsonl(path, rows):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'a', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_json(path, obj):
    write_json(path, obj)


def write_json(path, obj):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        jl = os.path.join(td, 'nested', 'dir', 'rows.jsonl')
        rows = [{'k1': 'arTay', 'ru': 'поручать', 'n': 1},
                {'k1': 'krand', 'ru': 'плакать', 'quote': '«кто-л.»'}]
        write_jsonl(jl, rows)
        raw = open(jl, 'rb').read()
        assert b'\r\n' not in raw and raw.endswith(b'\n'), raw[-40:]
        assert 'поручать'.encode('utf-8') in raw
        assert read_jsonl(jl) == rows
        assert list(iter_jsonl(jl)) == rows
        assert list(iter_jsonl(os.path.join(td, 'missing.jsonl'))) == []
        append_jsonl(jl, [{'k1': 'saYj', 'ru': 'учить'}])
        assert len(read_jsonl(jl)) == 3
        j = os.path.join(td, 'deep', 'obj.json')
        save_json(j, {'б': 1, 'list': [2, 3]})
        assert load_json(j)['б'] == 1
        raw_j = open(j, 'rb').read()
        assert raw_j.endswith(b'\n') and b'"\\u0431"' not in raw_j
    print('rt_io selftest OK — round-trip, makedirs, utf-8 literal, LF')
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == '--selftest':
        return selftest()
    print('usage: rt_io.py --selftest')
    return 2


if __name__ == '__main__':
    sys.exit(main())
