"""Line-ending determinism gate for `make_edition_cut.py` (H1769).

`release_manifest.json` pins a sha256 per file it copies into an "immutable"
release edition (assembled_cards.jsonl, the OntoLex/TEI interop exports,
schemas/, roadmap/, CHANGELOG.md, DOI_PLAN.md, CITATION.cff). None of those
paths carry a `.gitattributes eol=lf` pin, so on a Windows checkout with
`core.autocrlf=true` the SOURCE bytes are already CRLF before this script
ever touches them. `copy_file` used to be a bare `shutil.copy2` -- a
byte-for-byte copy of whatever CRLF/LF the checkout produced -- so the
sha256 recorded in the manifest was a property of the build host, not the
content: a Windows-cut edition and a Linux-cut edition of the identical
commit would pin two different hashes for the same logical file.

This module proves the fix (`copy_file` now LF-normalises text assets
before writing, `copy_tree` routes through the same helper) by feeding it
one CRLF "checkout" and one LF "checkout" of the same content and asserting
the resulting sha256 is identical either way.

Run: `pytest tests/test_make_edition_cut_lf_determinism.py` (working dir
RussianTranslation).
"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

import make_edition_cut as mec  # noqa: E402


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def test_copy_file_normalises_crlf(tmp_path):
    """A CRLF source (e.g. CHANGELOG.md checked out with autocrlf) must land
    in the edition as LF."""
    src = tmp_path / 'CHANGELOG.md'
    src.write_bytes(b'# Changelog\r\n\r\n## [Unreleased]\r\n- fix\r\n')
    dst = tmp_path / 'out' / 'CHANGELOG.md'
    mec.copy_file(str(src), str(dst))
    out = dst.read_bytes()
    assert b'\r\n' not in out
    assert out == b'# Changelog\n\n## [Unreleased]\n- fix\n'


def test_copy_file_leaves_binary_verbatim(tmp_path):
    """A genuinely binary asset (contains NUL / non-UTF-8 bytes) must pass
    through byte-for-byte -- normalisation only applies to text."""
    src = tmp_path / 'blob.bin'
    data = bytes([0, 1, 2, 0x0d, 0x0a, 0xff, 0xfe])
    src.write_bytes(data)
    dst = tmp_path / 'out' / 'blob.bin'
    mec.copy_file(str(src), str(dst))
    assert dst.read_bytes() == data


def test_manifest_sha256_is_platform_independent(tmp_path):
    """The defect, reproduced directly: copy the SAME logical content once
    as a CRLF 'Windows checkout' and once as an LF 'Linux checkout', and
    assert manifest_files() pins the identical sha256 either way."""
    logical_content = 'schema: pwg_ru.final_card.v1\nversion: 3\n'

    win_dir = tmp_path / 'edition_win'
    lin_dir = tmp_path / 'edition_lin'
    win_dir.mkdir()
    lin_dir.mkdir()

    win_src = tmp_path / 'src_win.json'
    win_src.write_bytes(logical_content.replace('\n', '\r\n').encode('utf-8'))
    lin_src = tmp_path / 'src_lin.json'
    lin_src.write_bytes(logical_content.encode('utf-8'))

    mec.copy_file(str(win_src), str(win_dir / 'schema.json'))
    mec.copy_file(str(lin_src), str(lin_dir / 'schema.json'))

    win_manifest = mec.manifest_files(str(win_dir))
    lin_manifest = mec.manifest_files(str(lin_dir))

    assert win_manifest['schema.json']['sha256'] == lin_manifest['schema.json']['sha256']
    assert win_manifest['schema.json']['sha256'] == _sha256_bytes(logical_content.encode('utf-8'))


def test_copy_tree_routes_through_the_same_normalisation(tmp_path):
    """`copy_tree` (used for schemas/ and roadmap/) must not bypass the
    normalising `copy_file` via a bare shutil.copytree default."""
    src_dir = tmp_path / 'schemas'
    src_dir.mkdir()
    (src_dir / 'a.schema.json').write_bytes(b'{\r\n  "a": 1\r\n}\r\n')

    dst_dir = tmp_path / 'edition' / 'schemas'
    mec.copy_tree(str(src_dir), str(dst_dir))

    out = (dst_dir / 'a.schema.json').read_bytes()
    assert b'\r\n' not in out
    assert out == b'{\n  "a": 1\n}\n'
