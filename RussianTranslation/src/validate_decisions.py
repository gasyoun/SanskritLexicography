#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_decisions — the gate in front of every decisions.json ingest (H1404).

Refuses a ``decisions.json`` that cannot be bound to a known review sheet.
This is the enforcement half of the binding standard (voted.md item 8): the
sheet side is ``review_binding.stamp()`` + the committed
``review/locks/<sheet_id>.lock.json``; this side proves a downloaded export
really belongs to the exact sheet generation the reviewer voted in, BEFORE
`/decisions-apply` (repo-side: ``apply_decisions.py``) acts on a single vote.

Checks, in order, each with a named non-zero-exit reason:

1. file parses as JSON;
2. shape matches ``schemas/decisions.schema.json`` — via ``jsonschema`` when
   importable, else a structural stdlib fallback (this repo's requirements.txt
   deliberately does not carry jsonschema);
3. ``sheet_id`` resolves to a committed lock (unknown sheet → reject);
4. ``content_hash`` present and equal to the lock's (missing → UNBOUND reject;
   mismatch → reject: the votes were cast against a different generation);
5. item ids are exactly the lock's ids (no drift, no invention).

Legacy pre-standard exports (e.g. ``review/decisions.json``, sheet_id
``h178_da``, 2026-07-07 — no content_hash) are grandfathered ONLY through
``--allow-legacy``, ONLY when the lock is ``mode: retro-unstamped``, and every
such acceptance is appended to ``review/locks/allow_legacy.log`` so the
exception is an audit trail, not a silent hole. A rights/correctness gate
never fails open: without the flag, unbound input is rejected.

CLI:
  python src/validate_decisions.py <decisions.json> [--locks-dir DIR] [--allow-legacy]
  python src/validate_decisions.py --selftest
Exit 0 = accepted; 1 = rejected (reason on stdout); 2 = usage.
"""
import datetime
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
SCHEMA_PATH = os.path.join(RT, "schemas", "decisions.schema.json")
DEFAULT_LOCKS_DIR = os.path.join(RT, "review", "locks")

DECISIONS = ("approve", "reject", "defer")
_HEX = set("0123456789abcdef")


class Reject(Exception):
    """A named validation failure."""


def _structural_check(doc):
    """stdlib fallback mirroring schemas/decisions.schema.json (R7: jsonschema
    is not a repo dependency). Field-for-field with the schema; keep in sync."""
    if not isinstance(doc, dict):
        raise Reject("schema: top level is not an object")
    for field in ("sheet_id", "generated", "decided", "content_hash", "items"):
        if field not in doc:
            raise Reject("schema: required field '%s' missing" % field)
    if not isinstance(doc["sheet_id"], str) or not doc["sheet_id"]:
        raise Reject("schema: sheet_id must be a non-empty string")
    if not isinstance(doc["generated"], str) or not doc["generated"]:
        raise Reject("schema: generated must be a non-empty string")
    if not isinstance(doc["decided"], int) or isinstance(doc["decided"], bool) or doc["decided"] < 0:
        raise Reject("schema: decided must be a non-negative integer")
    ch = doc["content_hash"]
    if (not isinstance(ch, str) or not ch.startswith("sha256:")
            or len(ch) != 71 or set(ch[7:]) - _HEX):
        raise Reject("schema: content_hash must match ^sha256:[0-9a-f]{64}$")
    if not isinstance(doc["items"], list):
        raise Reject("schema: items must be an array")
    for i, item in enumerate(doc["items"]):
        if not isinstance(item, dict):
            raise Reject("schema: items[%d] is not an object" % i)
        if not isinstance(item.get("id"), str) or not item["id"]:
            raise Reject("schema: items[%d].id must be a non-empty string" % i)
        if "decision" not in item:
            raise Reject("schema: items[%d].decision missing" % i)
        if item["decision"] is not None and item["decision"] not in DECISIONS:
            raise Reject("schema: items[%d].decision '%s' not in %s/null"
                         % (i, item["decision"], "|".join(DECISIONS)))
        if "note" in item and not isinstance(item["note"], str):
            raise Reject("schema: items[%d].note must be a string" % i)
        if "rating" in item and item["rating"] is not None \
                and not isinstance(item["rating"], (int, float)):
            raise Reject("schema: items[%d].rating must be a number or null" % i)


def _schema_check(doc, legacy=False):
    """Schema layer. A missing content_hash is deliberately deferred to the
    binding layer (strict there too — it rejects UNBOUND unless --allow-legacy),
    so the operator sees the binding-specific reason, not a generic schema one."""
    probe = dict(doc)
    if isinstance(probe, dict) and "content_hash" not in probe:
        probe["content_hash"] = "sha256:" + "0" * 64
    try:
        import jsonschema
    except ImportError:
        _structural_check(probe)
        return "structural-fallback"
    with io.open(SCHEMA_PATH, encoding="utf-8") as fh:
        schema = json.load(fh)
    try:
        jsonschema.validate(probe, schema)
    except jsonschema.ValidationError as e:
        raise Reject("schema: %s" % e.message)
    return "jsonschema"


def _log_legacy_accept(locks_dir, path, sheet_id):
    log_path = os.path.join(locks_dir, "allow_legacy.log")
    with io.open(log_path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write("%s\t--allow-legacy accepted\t%s\tsheet_id=%s\n"
                 % (datetime.date.today().isoformat(), os.path.basename(path), sheet_id))
    return log_path


def validate(path, locks_dir=None, allow_legacy=False, quiet=False):
    """Validate one decisions.json. Returns the parsed document on acceptance;
    raises Reject with the named reason otherwise."""
    locks_dir = locks_dir or DEFAULT_LOCKS_DIR

    def say(msg):
        if not quiet:
            print(msg)

    try:
        with io.open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except OSError as e:
        raise Reject("io: cannot read %s (%s)" % (path, e))
    except ValueError as e:
        raise Reject("json: %s is not valid JSON (%s)" % (path, e))

    engine = _schema_check(doc, legacy=allow_legacy)

    sheet_id = doc["sheet_id"]
    lock_path = os.path.join(locks_dir, sheet_id + ".lock.json")
    if not os.path.exists(lock_path):
        raise Reject("binding: unknown sheet_id '%s' — no lock at %s (was the sheet "
                     "generated through review_binding, or does a retro-lock need minting?)"
                     % (sheet_id, lock_path))
    with io.open(lock_path, encoding="utf-8") as fh:
        lock = json.load(fh)

    if "content_hash" not in doc:
        if not allow_legacy:
            raise Reject("binding: UNBOUND export — no content_hash. Pre-standard "
                         "files pass only via --allow-legacy (logged), never silently.")
        if lock.get("mode") != "retro-unstamped":
            raise Reject("binding: --allow-legacy refused — lock for '%s' is mode '%s', "
                         "so its sheet DOES stamp content_hash; an export without one "
                         "did not come from that sheet" % (sheet_id, lock.get("mode")))
        log_path = _log_legacy_accept(locks_dir, path, sheet_id)
        say("WARNING: legacy unbound export accepted via --allow-legacy "
            "(logged to %s)" % log_path)
    elif doc["content_hash"] != lock["content_hash"]:
        raise Reject("binding: content_hash mismatch — export carries %s, lock has %s. "
                     "The votes were cast against a different generation of '%s'; "
                     "do not apply them to this one."
                     % (doc["content_hash"], lock["content_hash"], sheet_id))

    export_ids = [it["id"] for it in doc["items"]]
    lock_ids = lock.get("ids", [])
    missing = sorted(set(lock_ids) - set(export_ids))
    extra = sorted(set(export_ids) - set(lock_ids))
    if missing or extra:
        raise Reject("binding: item-id drift vs lock (%d missing, %d unknown)%s%s"
                     % (len(missing), len(extra),
                        " missing e.g. " + ", ".join(missing[:3]) if missing else "",
                        " unknown e.g. " + ", ".join(extra[:3]) if extra else ""))
    if len(export_ids) != len(set(export_ids)):
        raise Reject("binding: duplicate item ids in export")

    say("OK: %s bound to sheet '%s' (%s; %d items, %d decided; schema engine: %s)"
        % (os.path.basename(str(path)), sheet_id, lock["content_hash"][:19] + "…",
           len(export_ids), doc["decided"], engine))
    return doc


# --------------------------------------------------------------------------- selftest
def _selftest():
    import tempfile
    sys.path.insert(0, HERE)
    from review_binding import content_hash, stamp, write_lock, extract_ids, extract_sheet_id
    from review_binding import _MINI  # the shared synthetic sheet fixture

    ok = True

    def check(cond, label):
        nonlocal ok
        print(("  ok " if cond else "  FAIL ") + label)
        ok = ok and cond

    def rejected(path, locks_dir, label, allow_legacy=False, needle=""):
        try:
            validate(path, locks_dir=locks_dir, allow_legacy=allow_legacy, quiet=True)
            check(False, label + " (was accepted!)")
        except Reject as e:
            check(needle in str(e), label + " [" + str(e).split(":")[0] + "]")

    with tempfile.TemporaryDirectory() as td:
        stamped, chash = stamp(_MINI)
        sheet_id = extract_sheet_id(_MINI)
        ids = extract_ids(_MINI)
        write_lock(sheet_id, chash, ids, "2026-07-25", locks_dir=td, gate="G5",
                   force=True)   # fixture: one sheet_id, several generations

        def dump(name, doc):
            p = os.path.join(td, name)
            with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(doc, fh, ensure_ascii=False, indent=2)
            return p

        good = {"sheet_id": sheet_id, "generated": "2026-07-25", "decided": 1,
                "content_hash": chash,
                "items": [{"id": ids[0], "decision": "approve", "note": ""},
                          {"id": ids[1], "decision": None, "note": ""}]}
        try:
            validate(dump("good.json", good), locks_dir=td, quiet=True)
            check(True, "accepts a genuine bound export")
        except Reject as e:
            check(False, "accepts a genuine bound export (%s)" % e)

        bad_sheet = dict(good, sheet_id="hand-corrupted")
        rejected(dump("bad_sheet.json", bad_sheet), td,
                 "rejects a hand-corrupted sheet_id", needle="unknown sheet_id")

        bad_hash = dict(good, content_hash="sha256:" + "f" * 64)
        rejected(dump("bad_hash.json", bad_hash), td,
                 "rejects a mismatched content_hash", needle="content_hash mismatch")

        bad_schema = dict(good, items=[{"id": ids[0], "decision": "maybe", "note": ""}])
        rejected(dump("bad_schema.json", bad_schema), td,
                 "rejects a schema-invalid file (bad decision enum)", needle="schema")

        # R7: exercise the stdlib structural fallback explicitly — the ambient
        # environment may or may not have jsonschema installed.
        try:
            _structural_check(good)
            check(True, "structural fallback accepts the genuine export")
        except Reject as e:
            check(False, "structural fallback accepts the genuine export (%s)" % e)
        try:
            _structural_check(bad_schema)
            check(False, "structural fallback rejects the bad enum (was accepted!)")
        except Reject:
            check(True, "structural fallback rejects the bad enum")

        unbound = {k: v for k, v in good.items() if k != "content_hash"}
        rejected(dump("unbound.json", unbound), td,
                 "rejects an unbound (no content_hash) export", needle="UNBOUND")

        rejected(os.path.join(td, "unbound.json"), td,
                 "refuses --allow-legacy against a stamped-mode lock",
                 allow_legacy=True, needle="--allow-legacy refused")

        write_lock(sheet_id, chash, ids, "2026-07-25", locks_dir=td, gate="G5",
                   mode="retro-unstamped")
        try:
            validate(os.path.join(td, "unbound.json"), locks_dir=td,
                     allow_legacy=True, quiet=True)
            log = io.open(os.path.join(td, "allow_legacy.log"), encoding="utf-8").read()
            check("unbound.json" in log, "--allow-legacy accepts a legacy export against "
                                         "a retro lock AND logs it")
        except Reject as e:
            check(False, "--allow-legacy legacy accept (%s)" % e)

        drift = dict(good, items=good["items"] + [{"id": "invented", "decision": None, "note": ""}])
        rejected(dump("drift.json", drift), td,
                 "rejects item-id drift vs the lock", needle="drift")

    print("validate_decisions selftest " + ("OK" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    allow_legacy = "--allow-legacy" in argv
    locks_dir = None
    paths = []
    i = 0
    args = [a for a in argv if a != "--allow-legacy"]
    while i < len(args):
        if args[i] == "--locks-dir":
            locks_dir = args[i + 1]; i += 2
        else:
            paths.append(args[i]); i += 1
    if not paths:
        print(__doc__)
        return 2
    for path in paths:
        try:
            validate(path, locks_dir=locks_dir, allow_legacy=allow_legacy)
        except Reject as e:
            print("REJECTED %s\n  %s" % (path, e))
            return 1
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main(sys.argv[1:]))
