#!/usr/bin/env python3
"""NKRYa (ruscorpora.ru) client — thin shim over the shared csl-pyutil module (H5282).

The implementation moved to `csl_pyutil.nkrya` on 24-09-2026 (ruling MG 23-09-2026,
docs/GRILL_NKRYA_USES_ROUND2_DECISIONS_23-09-2026.md) so RuWritingStyles,
CommentaryStrategies and Systema import ONE client instead of copying this file.
What stays here is only what is repo-local:

  DEFAULT_CACHE   RussianTranslation/pwg_ru/nkrya_cache (the pwg_ru run cache)
  FIXTURES        src/fixtures/nkrya (this repo's recorded doc-shaped fixtures)

Everything else — sketch/freq/concordance/pair, the disk cache, the ё-fold, the
token lookup, and since H5282 the 6/min token-bucket throttle with Retry-After
aware 429 backoff — lives upstream. Callers keep importing `nkrya_client`
unchanged (`nkrya_evidence_card.py` does).

CLI, unchanged:
  python src/nkrya_client.py probe
  python src/nkrya_client.py sketch туча S
  python src/nkrya_client.py freq сплочённый A
  python src/nkrya_client.py pair сплочённый туча [--19c]
  python src/nkrya_client.py --selftest        # offline, this repo's fixtures
"""

import os
import sys

try:
    from csl_pyutil import nkrya as _shared
except ImportError as exc:      # fail closed with the fix, never a silent fallback
    raise SystemExit(
        "csl_pyutil.nkrya is missing (H5282 moved the NKRYa client there).\n"
        "Install the pinned shared package:\n"
        "  pip install -r requirements.txt\n"
        "original error: %s" % exc)

# Re-exported so `import nkrya_client as nk` keeps working verbatim.
from csl_pyutil.nkrya import (          # noqa: F401  (re-export surface)
    API, KEYCHAIN_SERVICE, TOKEN_ENV, SEED, SLICE_19C, STORE_HINT,
    MAX_RETRIES, DEFAULT_RATE_PER_MIN, DEFAULT_BURST,
    NkryaError, NkryaAuthError, NkryaOffline, TokenBucket,
    load_token, request_key, parse_retry_after,
    pair_query, snippet_lines, yo_fold, rank_in)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CACHE = os.path.join(HERE, "..", "pwg_ru", "nkrya_cache")
FIXTURES = os.path.join(HERE, "fixtures", "nkrya")


class NkryaClient(_shared.NkryaClient):
    """The shared client with this repo's cache dir as the default."""

    def __init__(self, cache_dir=DEFAULT_CACHE, **kwargs):
        _shared.NkryaClient.__init__(self, cache_dir=cache_dir, **kwargs)


def selftest():
    """The shared offline selftest, run against THIS repo's fixture copy."""
    _shared.selftest(fixtures=FIXTURES, client_class=NkryaClient,
                     label="nkrya_client (shim -> csl_pyutil.nkrya)")


def main(argv=None):
    return _shared.main(argv, default_cache=DEFAULT_CACHE, fixtures=FIXTURES,
                        client_class=NkryaClient,
                        label="nkrya_client (shim -> csl_pyutil.nkrya)")


if __name__ == "__main__":
    sys.exit(main())
