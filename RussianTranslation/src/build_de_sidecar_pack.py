#!/usr/bin/env python
"""FAIR packaging for the DE edition-graph sidecars (H1635).

``export_de_edition.py`` (H1629) produces the three data artifacts; this script
turns them into a *citable* pack — provenance hashes, a deposit-metadata file,
and the manifest copy that lets a consumer verify a download without rebuilding
the 46 MB of RDF/XML.

Split of responsibilities, deliberately:

* **machine parts (here)** — ``SHA256SUMS``, ``manifest.json``, ``.zenodo.json``.
  Regenerated on every release; never hand-edited.
* **prose parts (authored, committed once)** — ``README.md``, ``DATASHEET.md``,
  ``LICENSE-DATA``, ``CITATION.cff``. Rights posture and datasheet answers are
  editorial judgment, not derivable from a manifest.

The two big artifacts are deliberately **NOT** committed: they are Zenodo
deposit files + GitHub release assets, and the repo keeps the recipe and the
hashes. `pwg_ru_translated.jsonl` (the store) is gitignored and is never an
input to anything published — the export applies a hard DE field allowlist and
a post-serialization byte fence before this script ever sees a file.

**Prior art, and why this is not that.** ``pwg_tm_release.py`` builds the
analogous pack for the *translation memory*, and its ``sha256_file`` is the
same six lines as :func:`sha256` here. It is deliberately not imported: it
reaches the TM pipeline at module scope (``pwg_tm_canonical``,
``pwg_tm_export_core``, ``pwg_tm_export_loss``), so importing it would pull the
Russian side into a DE-only tool whose entire purpose is not to touch it. A
duplicated hash helper is the cheaper of the two couplings — do not "dedupe"
this by importing the TM module.

  python build_de_sidecar_pack.py --selftest
  python build_de_sidecar_pack.py build --art-dir <export out-dir>
  python build_de_sidecar_pack.py build --art-dir <dir> --version v1.0.0
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PACK = os.path.join(HERE, '..', 'release', 'pwg_de_sidecars')

#: The three artifacts `export_de_edition.py export` writes. Order is the
#: SHA256SUMS order and is stable so the file diffs cleanly release-to-release.
ARTIFACTS = ('pwg_de_edition.ttl',
             'pwg_de_edition.tei.xml',
             'pwg_de_edition.manifest.json')

#: Files the pack itself carries. Prose files are authored, not generated; they
#: are listed so `--selftest` can assert the pack is complete before a deposit.
PROSE = ('README.md', 'DATASHEET.md', 'LICENSE-DATA', 'CITATION.cff')
GENERATED = ('SHA256SUMS', 'manifest.json', '.zenodo.json')

DATA_LICENSE = 'cc-by-sa-4.0'
#: Matches release/pwg_tm/CITATION.cff — do not retype the ORCID from memory.
CREATOR = {'name': 'Gasūns, Mārcis',
           'affiliation': 'Институт лингвистических исследований РАН (ИЛИ РАН)',
           'orcid': '0000-0003-4513-884X'}


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def sha256sums(art_dir: str) -> str:
    """`sha256sum`-compatible text over :data:`ARTIFACTS`, in fixed order."""
    lines = []
    for name in ARTIFACTS:
        p = os.path.join(art_dir, name)
        if not os.path.exists(p):
            raise SystemExit('missing artifact: %s' % p)
        lines.append('%s  %s' % (sha256(p), name))
    return '\n'.join(lines) + '\n'


def zenodo_metadata(manifest: dict, version: str | None) -> dict:
    """Deposit metadata for the **dataset** record.

    Deliberately a separate Zenodo record from the repository's own concept DOI
    (10.5281/zenodo.21306715): that one describes the *repository*, this one a
    derived dataset. Do not reuse the repo DOI here (H1635).
    """
    counts = manifest.get('layer_counts', {})
    rows = manifest.get('layer_rows', {})
    desc = (
        '<p>The <strong>German</strong> side of the Petersburger W&ouml;rterbuch '
        'edition graph, serialized for FAIR reuse as OntoLex-Lemon (Turtle) and '
        'TEI Lex-0 (XML).</p>'
        '<p>%d lexical entries / %d edition senses drawn from five editions '
        '(%s). Each sense carries machine-derived structural layers computed '
        'from the German string: government (%d), citation edges (%d), '
        'edition relations (%d), form notes (%d), non-German gloss spans '
        '(%d).</p>'
        '<p><strong>This dataset contains no translation, no review score and '
        'no evidence grade.</strong> A hard field allowlist and a '
        'post-serialization byte fence exclude the project\'s Russian '
        'translation store from the export.</p>'
        '<p>Source editions PWG (1855&ndash;1875), PW (1879&ndash;1889), SCH '
        '(1928) and PWKVN are in the public domain. The NWS layer (%d senses) '
        'is the Cologne Nachtragsw&ouml;rterbuch working layer. The derived '
        'structure is the authors\' own work, released CC-BY-SA-4.0. See '
        'DATASHEET.md in the deposit.</p>'
        % (manifest.get('entries', 0), manifest.get('exported_rows', 0),
           ', '.join(sorted(rows)), counts.get('government', 0),
           counts.get('citation_edges', 0), counts.get('edition_rel', 0),
           counts.get('form_notes', 0), counts.get('gloss_spans', 0),
           rows.get('nws', 0)))
    meta = {
        'title': 'PWG DE edition graph — OntoLex-Lemon + TEI Lex-0 sidecars',
        'upload_type': 'dataset',
        'description': desc,
        'creators': [CREATOR],
        'license': DATA_LICENSE,
        'keywords': ['Sanskrit', 'lexicography', 'OntoLex-Lemon', 'TEI Lex-0',
                     'Petersburger Wörterbuch', 'linked open data',
                     'digital humanities', 'FAIR'],
        'language': 'deu',
        'related_identifiers': [
            {'identifier': 'https://github.com/gasyoun/SanskritLexicography',
             'relation': 'isSupplementTo', 'scheme': 'url'},
        ],
    }
    if version:
        meta['version'] = version
    return {'metadata': meta}


def build(args) -> dict:
    art_dir = os.path.abspath(args.art_dir)
    pack = os.path.abspath(args.pack_dir)
    os.makedirs(pack, exist_ok=True)

    with open(os.path.join(art_dir, 'pwg_de_edition.manifest.json'),
              encoding='utf-8') as f:
        manifest = json.load(f)

    sums = sha256sums(art_dir)
    write(os.path.join(pack, 'SHA256SUMS'), sums)
    write(os.path.join(pack, 'manifest.json'),
          json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True) + '\n')
    write(os.path.join(pack, '.zenodo.json'),
          json.dumps(zenodo_metadata(manifest, args.version),
                     ensure_ascii=False, indent=1, sort_keys=True) + '\n')

    missing = [n for n in PROSE if not os.path.exists(os.path.join(pack, n))]
    print('DE sidecar pack -> %s' % pack)
    print('  artifacts hashed: %d' % len(ARTIFACTS))
    print('  entries %d / senses %d' % (manifest.get('entries', 0),
                                        manifest.get('exported_rows', 0)))
    if missing:
        print('  WARNING: prose files not present (author them): %s'
              % ', '.join(missing))
    return manifest


def write(path: str, text: str) -> None:
    """UTF-8, LF, no BOM (org rule)."""
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


# --------------------------------------------------------------------------- #
def selftest() -> None:
    fails = []

    def check(cond, msg):
        if not cond:
            fails.append(msg)

    with tempfile.TemporaryDirectory() as td:
        for name in ARTIFACTS[:2]:
            write(os.path.join(td, name), 'x')
        manifest = {'entries': 3, 'exported_rows': 9,
                    'layer_counts': {'government': 1, 'citation_edges': 2,
                                     'edition_rel': 3, 'form_notes': 4,
                                     'gloss_spans': 5},
                    'layer_rows': {'pwg': 7, 'nws': 2}}
        write(os.path.join(td, 'pwg_de_edition.manifest.json'),
              json.dumps(manifest))

        sums = sha256sums(td)
        check(len(sums.strip().splitlines()) == 3, 'SHA256SUMS: 3 lines')
        check(sums.endswith('\n'), 'SHA256SUMS ends with a newline')
        # sha256("x"), so the format is verifiable by hand, not just self-consistent
        check(sums.startswith('2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db'),
              'sha256 of "x" is wrong: %r' % sums[:64])
        check('  pwg_de_edition.ttl' in sums, 'two-space sha256sum separator')

        z = zenodo_metadata(manifest, 'v1.0.0')['metadata']
        check(z['upload_type'] == 'dataset', 'upload_type must be dataset')
        check(z['license'] == DATA_LICENSE, 'license: %r' % z['license'])
        check(z['version'] == 'v1.0.0', 'version passthrough')
        check('10.5281/zenodo.21306715' not in json.dumps(z),
              'must NOT reuse the repository concept DOI for a dataset record')
        check('no translation' in z['description'],
              'description must state the DE-only fence')
        check('9 edition senses' in z['description'],
              'description must carry real counts: %r' % z['description'][:200])
        check(zenodo_metadata(manifest, None)['metadata'].get('version') is None,
              'version omitted when not supplied')

    if fails:
        for f in fails:
            print('FAIL: %s' % f)
        raise SystemExit(1)
    print('build_de_sidecar_pack --selftest: OK')


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', nargs='?', choices=['build'])
    ap.add_argument('--art-dir', help='directory holding the exported artifacts')
    ap.add_argument('--pack-dir', default=DEFAULT_PACK)
    ap.add_argument('--version', help='release version stamped into .zenodo.json')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return
    if args.cmd != 'build' or not args.art_dir:
        ap.error('build requires --art-dir (or pass --selftest)')
    build(args)


if __name__ == '__main__':
    main()
