# -*- coding: utf-8 -*-
"""Regenerate the committed review-overlay extract + pin for pwg_ru (H2891).

The canonical store, ``src/pwg_ru_translated.jsonl``, is 26 MB and gitignored
(``.gitignore`` line 29, ``RussianTranslation/src/*.jsonl``). GitHub CI can
therefore never hash it — which is precisely why the store has been rewritten by
unlocked writers with nobody noticing. ``src/run_batch.py`` alone has three
unguarded write paths to it, and one of them is the code that *creates* every
reviewer stamp it can also erase.

So the tripwire runs on a **committed projection**: the key fields plus the
review stamps of the rows the H2890 census predicate calls human-reviewed, and
nothing else. Five rows today, a few hundred bytes. No German, no Russian, no
translation content — the live bytes never enter git, and this script must never
be changed to make them.

Usage::

    python src/build_integrity_extract.py            # rebuild extract, report drift
    python src/build_integrity_extract.py --pin      # ... and re-pin the new hashes
    python src/build_integrity_extract.py --check    # what CI runs

Any writer that changes a reviewed row must re-run this **in the same commit**
and put one line in the pin's ``reason`` saying what changed. That is the whole
acknowledgement ritual — see
[docs/ARCHITECTURE_UPRAVA_DATA_INTEGRITY_Q7_TRIPWIRES.md](https://github.com/gasyoun/Uprava/blob/main/docs/ARCHITECTURE_UPRAVA_DATA_INTEGRITY_Q7_TRIPWIRES.md).
"""
import argparse
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
RT_ROOT = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(RT_ROOT)

PIN = os.path.join(RT_ROOT, "data", "integrity", "pwg_ru.pin.json")
STORE = os.path.join(HERE, "pwg_ru_translated.jsonl")


def _tripwire():
    try:
        from csl_pyutil import integrity_tripwire
    except ImportError:
        sys.exit(
            "csl_pyutil is not installed. This script is a thin wrapper around the\n"
            "shared checker so three repos cannot drift into three hashers:\n"
            '  pip install "csl-pyutil @ '
            'git+https://github.com/sanskrit-lexicon/csl-pyutil@main"'
        )
    return integrity_tripwire


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="compare the committed extract against the pin (CI mode)")
    parser.add_argument("--pin", action="store_true",
                        help="rewrite the pin with the freshly extracted hashes")
    parser.add_argument("--reason", default=None,
                        help="--pin: one line saying what changed and why")
    parser.add_argument("--updated", default=None, help="--pin: DD-MM-YYYY")
    args = parser.parse_args(argv)

    it = _tripwire()

    if args.check:
        # CI never sees the live store, only the committed projection.
        return it.main(["--check", "--pin", PIN, "--root", REPO_ROOT])

    if not os.path.exists(STORE):
        print(
            "live store absent (%s) — nothing to re-extract.\n"
            "This is expected anywhere but the machine that holds the canonical\n"
            "store; the committed extract and pin are unchanged. Run --check to\n"
            "verify them." % (STORE,)
        )
        return 0

    argv_out = ["--extract", "--pin", PIN, "--root", REPO_ROOT]
    if args.pin:
        argv_out.append("--write-pin")
        if args.reason:
            argv_out += ["--reason", args.reason]
        if args.updated:
            argv_out += ["--updated", args.updated]
    rc = it.main(argv_out)
    if rc == 0 and not args.pin:
        print("\nextract rebuilt from the live store. Now run --check: a red result "
              "means a reviewed row moved and needs --pin --reason in the SAME commit.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
