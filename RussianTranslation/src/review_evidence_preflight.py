#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""review_evidence_preflight — re-export shim over `csl_pyutil.evidence` (H1889).

The gate this module introduced (H1887, 29-07-2026) now lives in the shared
review-sheet emitter package, so that every generator in every repo is checked by
the same code instead of this repo's copy:

    https://github.com/sanskrit-lexicon/csl-pyutil/blob/main/csl_pyutil/evidence.py

`csl_pyutil.render_review_sheet(..., manifest=...)` runs it as V9 and raises
before returning any HTML — which is the point of the lift: the check used to fire
only where a generator remembered to call it.

Same pattern H1808 used for `cdsl_anatomy`: the original file stays importable at
its old path with its old API, so nothing that imported it has to move. **Do not
add behaviour here** — fix it in `csl_pyutil.evidence` and let every repo get it.
The one thing this shim still owns is the repo-local `REPO_DEFAULT`: a shared
package cannot guess a repo root from its install location (it would scan
site-packages), so the shared class defaults to the cwd and this subclass restores
the historical "parent of src/" default for callers that omit `repo_root`.

    python review_evidence_preflight.py --selftest
"""
import os
import sys

from csl_pyutil.evidence import (  # noqa: F401  (re-exported for old importers)
    CYR,
    IAST,
    MIXED_SCRIPT,
    PANINI_REF,
    PreflightError,
    PreflightWarning,
    find_mixed_script,
    find_slp1,
    preflight,
    selftest,
    sutra_href,
    sutra_is_possible,
    valid_sutras,
)
from csl_pyutil.evidence import EvidenceManifest as _SharedEvidenceManifest

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.path.dirname(HERE)

__all__ = [
    'EvidenceManifest', 'PreflightError', 'PreflightWarning', 'preflight',
    'sutra_is_possible', 'valid_sutras', 'sutra_href',
    'find_mixed_script', 'find_slp1', 'selftest', 'REPO_DEFAULT',
]


class EvidenceManifest(_SharedEvidenceManifest):
    """`csl_pyutil.evidence.EvidenceManifest` with this repo's `repo_root` default."""

    def __init__(self, sheet_id, row_ids, repo_root=REPO_DEFAULT,
                 min_evidence_fields=2):
        super(EvidenceManifest, self).__init__(
            sheet_id, row_ids, repo_root=repo_root,
            min_evidence_fields=min_evidence_fields)


if __name__ == '__main__':
    if '--selftest' in sys.argv[1:]:
        print(selftest())
        # the shim's own contract: the repo-local default survived the lift
        man = EvidenceManifest('t', ['a'])
        assert man.repo_root == REPO_DEFAULT, man.repo_root
        assert isinstance(man, _SharedEvidenceManifest)
        print('shim OK — csl_pyutil.evidence re-exported, REPO_DEFAULT preserved')
    else:
        print(__doc__)
