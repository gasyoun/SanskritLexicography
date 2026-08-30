"""Sealed, immutable evidence artifacts (H3714 Wave 1, implementation step 2).

Canonical UTF-8/LF JSON, temporary-file write, ``fsync``, atomic replacement,
SHA-256 binding, and byte-different collision refusal.  Sealing is idempotent:
re-sealing identical bytes to the same path is a no-op that returns the same
receipt; re-sealing *different* bytes to a sealed path is a refusal, because an
artifact addressed by its hash may never be silently rewritten.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from typing import Any, Mapping

SCHEMA = 'pwg.pipeline.evidence.v1'


class SealError(RuntimeError):
    """An immutable artifact was about to be overwritten with other bytes."""


def canonical_bytes(value: Any) -> bytes:
    """Deterministic UTF-8/LF JSON bytes: sorted keys, no ASCII escaping."""
    text = json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'))
    return (text + '\n').encode('utf-8')


def jsonl_bytes(rows: Any) -> bytes:
    """Deterministic JSONL bytes: one canonical object per LF-terminated line.

    Stores are JSONL, not one JSON array -- the derived validator streams them
    row by row, and a 24 MB canonical artifact must never be loaded whole.
    """
    out = bytearray()
    for row in rows:
        out += json.dumps(row, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode('utf-8')
        out += b'\n'
    return bytes(out)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def sha256_file(path: str, *, chunk: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        while True:
            block = handle.read(chunk)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def _fsync_directory(path: str) -> None:
    directory = os.path.dirname(os.path.abspath(path)) or '.'
    try:
        fd = os.open(directory, os.O_RDONLY)
    except (OSError, AttributeError):
        # Windows cannot open a directory handle this way; the atomic replace
        # below is still ordered by the filesystem.
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def atomic_write_bytes(path: str, payload: bytes) -> str:
    """Write ``payload`` durably and atomically; return its digest."""
    directory = os.path.dirname(os.path.abspath(path)) or '.'
    os.makedirs(directory, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        dir=directory, prefix='.pwgseal-', suffix='.tmp', delete=False)
    temporary = handle.name
    try:
        with handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
    _fsync_directory(path)
    return sha256_bytes(payload)


def seal(path: str, value: Any) -> dict[str, Any]:
    """Seal ``value`` at ``path`` and return a hash-bound receipt.

    Idempotent for identical bytes; refuses a byte-different collision.
    """
    payload = canonical_bytes(value)
    digest = sha256_bytes(payload)
    if os.path.exists(path):
        with open(path, 'rb') as handle:
            existing = handle.read()
        if existing == payload:
            return receipt(path, digest, len(payload))
        raise SealError(
            'sealed artifact already exists with different bytes: %s '
            '(sealed=%s, incoming=%s)' % (path, sha256_bytes(existing), digest))
    atomic_write_bytes(path, payload)
    return receipt(path, digest, len(payload))


def receipt(path: str, digest: str, size: int,
            media_type: str = 'application/json') -> dict[str, Any]:
    return {
        'schema': SCHEMA,
        'path': path.replace('\\', '/'),
        'sha256': digest,
        'bytes': int(size),
        'media_type': media_type,
    }


def read_sealed(path: str) -> Any:
    """Read a sealed artifact and verify nothing rewrote it in place."""
    with open(path, 'rb') as handle:
        payload = handle.read()
    value = json.loads(payload.decode('utf-8'))
    if canonical_bytes(value) != payload:
        raise SealError('artifact is not in canonical sealed form: %s' % path)
    return value


def verify(path: str, expected_sha256: str) -> bool:
    """True when the on-disk bytes still hash to ``expected_sha256``."""
    if not os.path.exists(path):
        return False
    return sha256_file(path) == expected_sha256


def tree_digest(root: str) -> str:
    """Digest of a directory tree: pins that a pure step changed nothing (V5)."""
    entries: list[str] = []
    for base, dirs, files in os.walk(root):
        dirs.sort()
        for name in sorted(files):
            full = os.path.join(base, name)
            relative = os.path.relpath(full, root).replace('\\', '/')
            entries.append('%s:%s' % (relative, sha256_file(full)))
    return sha256_text('\n'.join(entries))


def bind(receipt_value: Mapping[str, Any]) -> tuple[str, str]:
    """Return ``(path, sha256)`` from a receipt, refusing an unbound one."""
    path = receipt_value.get('path')
    digest = receipt_value.get('sha256')
    if not path or not digest:
        raise SealError('receipt is not hash-bound: %r' % (dict(receipt_value),))
    return str(path), str(digest)


__all__ = [
    'SCHEMA', 'SealError', 'canonical_bytes', 'sha256_bytes', 'sha256_text',
    'canonical_sha256', 'sha256_file', 'atomic_write_bytes', 'seal', 'receipt',
    'jsonl_bytes',
    'read_sealed', 'verify', 'tree_digest', 'bind',
]
