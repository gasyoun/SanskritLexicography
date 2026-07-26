#!/usr/bin/env python
"""export_frame_sense_loci.py — H1632 input builder.

Emits the PWG per-sense `<ls>` loci rows for exactly the headwords in the frozen
H1455 pilot frame (`kosha/data/concordance/sense_pilot_headwords.tsv`).

Why this exists. The committed `RussianTranslation/src/pwg_sense_loci.sample.tsv`
(H1456) is a *sample* — a different 500 headwords from the pilot frame, overlapping
it in only 16 keys. The full `pwg_sense_loci.tsv` H1455 actually consumed is
gitignored and is not on disk. Rather than silently join a 3%-overlapping sample
(which would have reported a near-zero coverage that is an artefact of the wrong
input, not a fact about PWG), this regenerates the frame's rows from the canonical
parser.

REUSES `microstructure.leaf_senses` + `pwg_mask.records` verbatim — the sense-tree
parsing, the Nachträge adjacent-marker fix, and the `<ls>` extraction are all the
existing H1456 code. The only thing patched is `pwg_mask.PWG`, the module-level
path constant, which resolves `../../../csl-orig` relative to the source file and
therefore breaks when the repo is checked out as a git worktree (the worktree sits
one directory shallower than the main clone). Patched in memory, per-process; the
shared module is never edited, and csl-orig is opened read-only.

Usage:
  python export_frame_sense_loci.py [--frame PATH] [--out PATH] [--pwg PATH]
"""
import argparse
import csv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', 'src'))
sys.path.insert(0, SRC)


def find_pwg(explicit=None):
    """Locate csl-orig/v02/pwg/pwg.txt (worktree-safe)."""
    cands = []
    if explicit:
        cands.append(explicit)
    if os.environ.get('CSL_ORIG_ROOT'):
        cands.append(os.path.join(os.environ['CSL_ORIG_ROOT'],
                                  'v02', 'pwg', 'pwg.txt'))
    d = HERE
    for _ in range(6):
        d = os.path.dirname(d)
        cands.append(os.path.join(d, 'csl-orig', 'v02', 'pwg', 'pwg.txt'))
        cands.append(os.path.join(d, 'GitHub', 'csl-orig', 'v02', 'pwg', 'pwg.txt'))
    for c in cands:
        if c and os.path.isfile(c):
            return os.path.normpath(c)
    raise SystemExit('pwg.txt not found. Pass --pwg PATH or set $CSL_ORIG_ROOT.\n'
                     'Tried:\n  ' + '\n  '.join(cands))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--frame', default=None)
    ap.add_argument('--kosha', default=None)
    ap.add_argument('--out', default=os.path.join(HERE, 'pwg_sense_loci.frame500.tsv'))
    ap.add_argument('--pwg', default=None)
    a = ap.parse_args()

    frame_path = a.frame
    if not frame_path:
        from pwg_sense_dcs_attestation_pilot import find_kosha
        frame_path = os.path.join(find_kosha(a.kosha), 'data', 'concordance',
                                  'sense_pilot_headwords.tsv')

    wanted = set()
    with open(frame_path, encoding='utf-8', newline='') as fh:
        for r in csv.DictReader(fh, delimiter='\t'):
            wanted.add((r['slp1'], r.get('hom', '')))
    print('frame: %d (slp1,hom) groups' % len(wanted), file=sys.stderr)

    import pwg_mask
    pwg_path = find_pwg(a.pwg)
    pwg_mask.PWG = pwg_path
    print('pwg.txt: %s (%d bytes)' % (pwg_path, os.path.getsize(pwg_path)),
          file=sys.stderr)

    import microstructure

    n_records = n_rows = 0
    seen = set()
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('slp1\thom\tsense_id\tgloss_de\tls_loci\n')
        for buf in pwg_mask.records():
            n_records += 1
            for slp1, hom, sense_id, gloss_de, ls_loci in microstructure.leaf_senses(buf):
                if (slp1, hom or '') not in wanted:
                    continue
                # keep tabs/newlines out of the TSV cells
                gloss_de = (gloss_de or '').replace('\t', ' ').replace('\n', ' ')
                f.write('%s\t%s\t%s\t%s\t%s\n'
                        % (slp1, hom, sense_id, gloss_de, ls_loci))
                n_rows += 1
                seen.add((slp1, hom or ''))

    print('records scanned : %d' % n_records, file=sys.stderr)
    print('leaf-sense rows : %d' % n_rows, file=sys.stderr)
    print('frame groups hit: %d/%d' % (len(seen), len(wanted)), file=sys.stderr)
    missing = wanted - seen
    if missing:
        print('frame groups with NO leaf-sense row: %d (e.g. %s)'
              % (len(missing), sorted(missing)[:5]), file=sys.stderr)
    print('written: %s' % a.out, file=sys.stderr)


if __name__ == '__main__':
    main()
