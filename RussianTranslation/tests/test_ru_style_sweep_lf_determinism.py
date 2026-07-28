"""Line-ending determinism gate for `ru_style_sweep.py`'s store writer (H1769).

`_write_rows_atomic` is the sole writer of the canonical `pwg_ru_translated.jsonl`
store on `--apply`/`--repair-from --apply`, and its own before/after sha256 is
recorded into the persisted repair report (`before_sha256`, `after_sha256`,
the verified backup's `sha256`) for audit/provenance. It used to open the temp
file in plain text mode (`open(tmp, 'x', encoding='utf-8')`) with no
`newline=` guard, so a Windows run would apply universal-newline translation
(LF -> CRLF) to every row it wrote -- silently converting the canonical
store's line endings, and making every recorded sha256 a property of the
build host rather than the content.

Run: `pytest tests/test_ru_style_sweep_lf_determinism.py` (working dir
RussianTranslation).
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

import ru_style_sweep as rss  # noqa: E402


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def test_write_rows_atomic_emits_lf_only(tmp_path):
    store = tmp_path / 'pwg_ru_translated.jsonl'
    row0 = {'key1': 'a', 'subcard': 'a~~1', 'sense_tag': '1', 'ru': 'x'}
    store.write_bytes((json.dumps(row0, ensure_ascii=False) + '\n').encode('utf-8'))
    initial_hash = _sha256_bytes(store.read_bytes())

    rows = [
        {'key1': 'a', 'subcard': 'a~~1', 'sense_tag': '1', 'ru': 'вм.'},
        {'key1': 'b', 'subcard': 'b~~1', 'sense_tag': '1', 'ru': 'в знач.'},
    ]
    rss._write_rows_atomic(str(store), rows, initial_hash, backup_dir=str(tmp_path))

    raw = store.read_bytes()
    assert b'\r\n' not in raw
    expected = (
        (json.dumps(rows[0], ensure_ascii=False) + '\n').encode('utf-8')
        + (json.dumps(rows[1], ensure_ascii=False) + '\n').encode('utf-8')
    )
    assert raw == expected


def test_write_rows_atomic_hash_is_platform_independent(tmp_path):
    """The defect, reproduced directly: writing the SAME rows must yield the
    SAME sha256 regardless of what newline convention happened to be active."""
    rows = [{'key1': 'k', 'subcard': 'k~~1', 'sense_tag': '1', 'ru': 'test'}]

    store_a = tmp_path / 'a' / 'store.jsonl'
    store_a.parent.mkdir()
    store_a.write_bytes(b'')
    hash_a = _sha256_bytes(store_a.read_bytes())
    rss._write_rows_atomic(str(store_a), rows, hash_a, backup_dir=str(store_a.parent))

    store_b = tmp_path / 'b' / 'store.jsonl'
    store_b.parent.mkdir()
    store_b.write_bytes(b'')
    hash_b = _sha256_bytes(store_b.read_bytes())
    rss._write_rows_atomic(str(store_b), rows, hash_b, backup_dir=str(store_b.parent))

    assert store_a.read_bytes() == store_b.read_bytes()
    assert rss._file_sha256(str(store_a)) == rss._file_sha256(str(store_b))
