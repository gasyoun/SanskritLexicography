#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""review_binding — the H1404 sheet↔decisions.json binding standard (voted.md item 8).

The reviewer's ask: «Как потом понять, что decisions.JSON относится именно к
h178_da_sheet.html — и мне и агенту?». The emitter
(``csl_pyutil.render_review_sheet`` v0.3.1) stamps a ``sheet_id`` into every
sheet and every export, but a sheet_id alone cannot prove WHICH generation of
the sheet the votes were cast against — sheets get regenerated, and the export
payload is hardcoded in the package with no hash hook. csl-pyutil is external
and pinned, so the binding is implemented REPO-SIDE, by the same additive
string surgery on stable anchors the package's own ``_add_standard()`` uses:

* ``content_hash(html)`` — ``sha256:<hex>`` over the pre-stamp sheet HTML,
  LF-normalized. This is the identity of "the exact content the reviewer saw".
* ``stamp(html)`` — patches the finished sheet so every export payload site
  (``{ sheet_id: SHEET_ID, `` — the emitter's core download, its auto-save
  ``exportPayload()``, its strict-review payload, and h178_eval_bakeoff.py's
  spliced RUBRIC_JS all share that literal) additionally emits
  ``content_hash``, and injects a visible hash chip next to the header's
  sheet_id so the human can eyeball the binding too.
* ``write_lock(...)`` / ``lock_from_html(...)`` — a METADATA-ONLY
  ``<sheet_id>.lock.json`` (sheet_id, hash, card ids, counts — never any card
  BODY text, so the lock is safe to commit in this PUBLIC repo even when the
  sheet HTML itself is gitignored for embedding unpublished translations; card
  ids are echoed verbatim, and a few store sense_tags carry short structural
  labels like «грамматическая рубрика» — rubric names, not translation
  content).
  The lock is the durable anchor: `/decisions-apply` deletes the HTML after
  ingest, and validation must still work afterwards.

``validate_decisions.py`` consumes the locks; generators call ``stamp()`` +
``write_lock()`` right after ``render_review_sheet()``. Voted/closed sheets are
NEVER regenerated in place — for those, ``retro-lock`` derives the lock from
the committed/downloaded source-of-record HTML as-is (mode ``retro-unstamped``).

CLI:
  python src/review_binding.py stamp <sheet.html> [--gate G5] [--locks-dir DIR]
  python src/review_binding.py retro-lock <sheet.html> [--gate G5] [--locks-dir DIR]
  python src/review_binding.py --selftest
"""
import datetime
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LOCKS_DIR = os.path.join(os.path.dirname(HERE), "review", "locks")

LOCK_SCHEMA = "review-lock/v1"

# The one payload literal every export site shares (emitter core download,
# emitter auto-save exportPayload, emitter strict payload, bakeoff RUBRIC_JS).
_PAYLOAD_ANCHOR = "{ sheet_id: SHEET_ID, "
_PAYLOAD_STAMPED = "{ sheet_id: SHEET_ID, content_hash: CONTENT_HASH, "
_SHEET_ID_DECL = re.compile(r"(var SHEET_ID = (\"[^\"\n]*\"|'[^'\n]*'|[^;\n]+);)")
_IDS_DECL = re.compile(r"var ids = (\[[^\n]*\]);")


def content_hash(html_text):
    """sha256:<hex> over the LF-normalized UTF-8 bytes of the sheet HTML.
    Computed BEFORE stamping (the stamp is derived data, not content)."""
    norm = html_text.replace("\r\n", "\n").replace("\r", "\n")
    return "sha256:" + hashlib.sha256(norm.encode("utf-8")).hexdigest()


def extract_sheet_id(html_text):
    m = _SHEET_ID_DECL.search(html_text)
    if not m:
        raise ValueError("no 'var SHEET_ID = ...;' declaration found — not a review sheet?")
    raw = m.group(2).strip()
    if raw.startswith("'") and raw.endswith("'"):
        raw = '"' + raw[1:-1] + '"'
    return json.loads(raw)


def extract_ids(html_text):
    m = _IDS_DECL.search(html_text)
    if not m:
        raise ValueError("no 'var ids = [...];' declaration found — not a review sheet?")
    return json.loads(m.group(1))


def stamp(html_text):
    """Return ``(stamped_html, chash)``. Idempotence is refused loudly: a sheet
    carries exactly one binding generation, and re-stamping stamped HTML would
    hash the stamp into itself."""
    if "var CONTENT_HASH" in html_text:
        raise ValueError("sheet is already stamped (var CONTENT_HASH present) — "
                         "regenerate from the generator instead of re-stamping")
    chash = content_hash(html_text)
    sheet_id = extract_sheet_id(html_text)

    # 1. every IIFE that declares SHEET_ID gets a CONTENT_HASH beside it (the
    #    bakeoff widget splice is a second, separate IIFE with its own decl).
    stamped, n_decl = _SHEET_ID_DECL.subn(
        lambda m: m.group(1) + "\n  var CONTENT_HASH = %s;" % json.dumps(chash),
        html_text)
    # 2. every export payload site now echoes the hash.
    n_sites = stamped.count(_PAYLOAD_ANCHOR)
    if n_sites == 0:
        raise ValueError("no export payload site ('%s') found — emitter layout "
                         "changed, re-check the anchors" % _PAYLOAD_ANCHOR.strip())
    stamped = stamped.replace(_PAYLOAD_ANCHOR, _PAYLOAD_STAMPED)
    # 3. visible chip beside the header's sheet_id (best-effort — the emitter's
    #    core template carries this anchor; a hand-rolled shell may not).
    chip_anchor = "sheet_id <code>%s</code>" % sheet_id
    if chip_anchor in stamped:
        chip = (chip_anchor + ' &middot; bound <code class="bindchip" title="content_hash '
                "— binds this sheet's decisions.json export to exactly this HTML"
                '">%s…</code>' % chash[:19])
        stamped = stamped.replace(chip_anchor, chip, 1)
    return stamped, chash


class LockCollision(Exception):
    """A lock already exists for this sheet_id and binds a DIFFERENT sheet."""


def write_lock(sheet_id, chash, ids, generated, locks_dir=None, gate=None,
               source_html=None, mode="stamped", force=False):
    """Emit the committed, metadata-only lock. ``mode`` is ``stamped`` (sheet
    HTML embeds CONTENT_HASH) or ``retro-unstamped`` (lock derived from a
    pre-standard source-of-record; its exports carry no content_hash and pass
    validation only through --allow-legacy).

    Refuses to overwrite an existing lock that binds a DIFFERENT content hash
    (raises ``LockCollision``), unless ``force`` or ``REVIEW_LOCK_FORCE=1``.
    A sheet generator reads live data, so re-running one after its inputs have
    moved silently re-cuts the sheet — and overwriting the lock is exactly what
    makes votes already cast against the committed generation unapplicable, with
    no signal until `validate_decisions.py` rejects the export AFTER the human
    has spent them. An intentional re-cut is one flag away; an accidental one
    now stops. (H1703: re-running the H1628 generator on a later master re-cut
    its 200 cards and rewrote its live lock, because the upstream extractor
    repairs had moved the queue underneath it.)
    """
    locks_dir = locks_dir or DEFAULT_LOCKS_DIR
    os.makedirs(locks_dir, exist_ok=True)
    existing = read_lock(sheet_id, locks_dir)
    if (existing and existing.get("content_hash") not in (None, chash)
            and not force and os.environ.get("REVIEW_LOCK_FORCE") != "1"):
        raise LockCollision(
            "lock for '%s' already binds %s, this run rendered %s.\n"
            "  Votes cast against the committed generation would stop validating.\n"
            "  Deliberate re-cut: pass force=True or set REVIEW_LOCK_FORCE=1.\n"
            "  To REPRODUCE the committed generation instead, check out the commit\n"
            "  that created the lock — its inputs have since moved — and run there."
            % (sheet_id, existing.get("content_hash"), chash))
    lock = {
        "schema": LOCK_SCHEMA,
        "sheet_id": sheet_id,
        "content_hash": chash,
        "generated": generated,
        "gate": gate,
        "n_items": len(ids),
        "ids": list(ids),
        "source_html": os.path.basename(source_html) if source_html else None,
        "mode": mode,
        "created": datetime.date.today().isoformat(),
        "tool": "review_binding.py (H1404 binding standard)",
    }
    path = os.path.join(locks_dir, sheet_id + ".lock.json")
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(lock, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


def read_lock(sheet_id, locks_dir=None):
    path = os.path.join(locks_dir or DEFAULT_LOCKS_DIR, sheet_id + ".lock.json")
    if not os.path.exists(path):
        return None
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _extract_generated(html_text):
    m = re.search(r"generated: (\"[^\"\n]*\")", html_text)
    if m:
        return json.loads(m.group(1))
    m = re.search(r">Generated ([^<&]+?) *&middot;", html_text)
    return m.group(1).strip() if m else "unknown"


def lock_from_html(html_path, locks_dir=None, gate=None, retro=False):
    """Stamp-time lock (after stamp()) or retro lock from a pre-standard sheet."""
    with io.open(html_path, encoding="utf-8") as fh:
        doc = fh.read()
    if retro:
        if "var CONTENT_HASH" in doc:
            raise ValueError("%s is already stamped — retro-lock is only for "
                             "pre-standard sheets" % html_path)
        chash = content_hash(doc)
        mode = "retro-unstamped"
    else:
        if "var CONTENT_HASH" not in doc:
            raise ValueError("%s is not stamped — run stamp first (or use retro-lock)"
                             % html_path)
        m = re.search(r'var CONTENT_HASH = ("sha256:[0-9a-f]{64}");', doc)
        if not m:
            raise ValueError("stamped CONTENT_HASH declaration not parseable")
        chash = json.loads(m.group(1))
        mode = "stamped"
    return write_lock(extract_sheet_id(doc), chash, extract_ids(doc),
                      _extract_generated(doc), locks_dir=locks_dir, gate=gate,
                      source_html=html_path, mode=mode)



# --------------------------------------------------------------------------- packsets (H3098)
def packset_hash(pack_hashes):
    """sha256 over the ordered pack content hashes.

    One value that changes if ANY pack changed, so "is this the committed
    generation?" stays a single comparison even when the sheet is N+1 files.
    Order is part of the identity: moving a card from pack 2 to pack 3 changes
    which page a reviewer votes it on, so it must not hash the same.
    """
    joined = "\n".join(pack_hashes).encode("utf-8")
    return "sha256:" + hashlib.sha256(joined).hexdigest()


def write_packset_lock(sheet_id, parent_html, pack_htmls, generated,
                       locks_dir=None, gate=None, source_html=None, force=False):
    """Lock a packset: the parent plus its ordered packs, under ONE sheet_id.

    ``parent_html`` is the UNSTAMPED parent index — it has no cards and no export
    payload site, so ``stamp()`` would refuse it and a stamp would bind nothing.
    ``pack_htmls`` is the ordered list of STAMPED pack documents (pack-01 first).
    Each pack contributes its own ``content_hash`` and its own id slice, because
    a ``pack-NN.json`` export names only that slice and must validate against
    that page -- not against the whole instrument.

    The collision rule is the single-sheet rule applied to ``packset_hash``: a
    lock that already binds a DIFFERENT packset refuses to be overwritten, for
    exactly the reason ``write_lock`` gives -- votes cast against the committed
    generation would stop validating with no signal until the human had already
    spent them (H1703).
    """
    locks_dir = locks_dir or DEFAULT_LOCKS_DIR
    os.makedirs(locks_dir, exist_ok=True)

    # The parent is an INDEX: no cards, no export payload site, so stamp() would
    # refuse it and there is nothing for a stamp to bind anyway. Hash it plain.
    parent_hash = content_hash(parent_html)
    packs = []
    all_ids = []
    for n, doc in enumerate(pack_htmls, 1):
        pid = extract_sheet_id(doc)
        if pid != sheet_id:
            raise ValueError(
                "pack %02d declares sheet_id %r but the packset is %r -- packs "
                "MUST share the parent's sheet_id, that is what makes them one "
                "localStorage record" % (n, pid, sheet_id))
        ids = extract_ids(doc)
        packs.append({
            "name": "%02d" % n,
            "content_hash": _stamped_hash(doc),
            "n_items": len(ids),
            "ids": list(ids),
        })
        all_ids.extend(ids)

    if len(set(all_ids)) != len(all_ids):
        raise ValueError("the same id appears in more than one pack -- a card "
                         "must be votable on exactly one page")

    pshash = packset_hash([p["content_hash"] for p in packs])
    existing = read_lock(sheet_id, locks_dir)
    forced = force or os.environ.get("REVIEW_LOCK_FORCE") == "1"
    if existing and not forced:
        prior = existing.get("packset")
        if prior is None:
            # A SHAPE change is still a re-cut. Without this branch the missing
            # `packset` key read as "nothing to compare" and the single-file lock
            # was silently replaced -- the exact rebinding the guard exists to
            # stop (H1703), arriving by a different door.
            raise LockCollision(
                "lock for '%s' binds a SINGLE-FILE sheet (%s); this run rendered a "
                "packset of %d packs (%s).\n"
                "  Converting a locked sheet into packs re-cuts it: any decisions.json "
                "already exported against the single file would stop validating.\n"
                "  Deliberate conversion: pass force=True or set REVIEW_LOCK_FORCE=1, "
                "after proving the card set is unchanged."
                % (sheet_id, existing.get("content_hash"), len(packs), pshash))
        if prior.get("packset_hash") != pshash:
            raise LockCollision(
                "lock for '%s' already binds packset %s, this run rendered %s.\n"
                "  Votes cast against the committed generation would stop validating.\n"
                "  Deliberate re-cut: pass force=True or set REVIEW_LOCK_FORCE=1."
                % (sheet_id, prior.get("packset_hash"), pshash))

    lock = {
        "schema": LOCK_SCHEMA,
        "sheet_id": sheet_id,
        # For a packset the instrument's identity is the PACKSET hash, not any one
        # file: that is the value that changes when any pack changes. The parent's
        # own hash rides inside the block, since nothing is ever exported from it.
        "content_hash": pshash,
        "packset": {
            "pack_size": max((p["n_items"] for p in packs), default=0),
            "n_packs": len(packs),
            "packset_hash": pshash,
            "parent_hash": parent_hash,
            "packs": packs,
        },
        "generated": generated,
        "gate": gate,
        "n_items": len(all_ids),
        "ids": all_ids,
        "source_html": os.path.basename(source_html) if source_html else None,
        "mode": "stamped",
        "created": datetime.date.today().isoformat(),
        "tool": "review_binding.py (H1404 binding standard; packsets H3098)",
    }
    path = os.path.join(locks_dir, sheet_id + ".lock.json")
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(lock, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


def _stamped_hash(doc):
    """The content_hash a stamped document carries."""
    m = re.search(r'var CONTENT_HASH = ("sha256:[0-9a-f]{64}");', doc)
    if not m:
        raise ValueError("document is not stamped -- run stamp() on every pack "
                         "and the parent before locking the packset")
    return json.loads(m.group(1))


def pack_for_export(lock, content_hash_value):
    """Which pack (if any) an export's content_hash belongs to.

    Returns the pack dict, or None when the hash is the whole-sheet binding.
    ``validate_decisions`` uses this so a ``pack-NN.json`` validates against the
    page it was voted on rather than against the whole instrument.
    """
    for pack in (lock.get("packset") or {}).get("packs", []):
        if pack.get("content_hash") == content_hash_value:
            return pack
    return None

# --------------------------------------------------------------------------- selftest
_MINI = '''<!DOCTYPE html><html><head><style>x</style></head><body>
<div class="sub">Generated 2026-07-25 &middot; sheet_id <code>selftest-mini</code> &middot; t</div>
<script>
(function () {
  var SHEET_ID = "selftest-mini";
  var ids = ["a|1","b|2"];
  var payload = { sheet_id: SHEET_ID, generated: "2026-07-25", decided: decided,
    items: [] };
  function exportPayload() {
    return JSON.stringify({ sheet_id: SHEET_ID, generated: new Date().toISOString(), decided: 0, items: [] }, null, 2);
  }
})();
</script>
<script>
(function () {
  var SHEET_ID = "selftest-mini";
  var payload = { sheet_id: SHEET_ID, generated: "2026-07-25", decided: 0, items: [] };
})();
</script>
</body></html>'''


def _selftest():
    import tempfile
    ok = True

    def check(cond, label):
        nonlocal ok
        print(("  ok " if cond else "  FAIL ") + label)
        ok = ok and cond

    h0 = content_hash(_MINI)
    check(h0 == content_hash(_MINI.replace("\n", "\r\n")), "hash is CRLF/LF-stable")
    check(extract_sheet_id(_MINI) == "selftest-mini", "extract_sheet_id")
    check(extract_ids(_MINI) == ["a|1", "b|2"], "extract_ids")

    stamped, chash = stamp(_MINI)
    check(chash == h0, "stamp hashes the pre-stamp document")
    check(stamped.count("var CONTENT_HASH = ") == 2, "CONTENT_HASH injected per IIFE")
    check(stamped.count(_PAYLOAD_STAMPED) == 3, "all 3 payload sites patched")
    check(_PAYLOAD_ANCHOR not in stamped.replace(_PAYLOAD_STAMPED, ""), "no unpatched site left")
    check('class="bindchip"' in stamped, "visible hash chip injected")
    try:
        stamp(stamped)
        check(False, "double-stamp refused")
    except ValueError:
        check(True, "double-stamp refused")

    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "mini_sheet.html")
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(stamped)
        lock_path = lock_from_html(p, locks_dir=td, gate="G5")
        lock = read_lock("selftest-mini", locks_dir=td)
        check(lock is not None and lock["content_hash"] == chash, "lock round-trips the hash")
        check(lock["ids"] == ["a|1", "b|2"] and lock["gate"] == "G5", "lock carries ids + gate")
        check(lock["mode"] == "stamped", "lock mode = stamped")
        blob = io.open(lock_path, encoding="utf-8").read()
        check("Generated 2026-07-25" not in blob and "<div" not in blob,
              "lock is metadata-only (no sheet body)")

        # H1703: re-running a generator whose inputs moved must NOT silently
        # rewrite a live lock — that is what invalidates votes already cast.
        try:
            write_lock("selftest-mini", "sha256:" + "0" * 64, ["a|1"], "2026-07-27",
                       locks_dir=td)
            check(False, "lock collision refused")
        except LockCollision:
            check(True, "lock collision refused")
        again = write_lock("selftest-mini", chash, ["a|1", "b|2"], "2026-07-27",
                           locks_dir=td)
        check(read_lock("selftest-mini", locks_dir=td)["content_hash"] == chash,
              "same-hash rewrite still allowed (idempotent regeneration)")
        forced = write_lock("selftest-mini", "sha256:" + "1" * 64, ["a|1"], "2026-07-27",
                            locks_dir=td, force=True)
        check(read_lock("selftest-mini", locks_dir=td)["content_hash"].endswith("1" * 8),
              "force=True re-cuts deliberately")
        check(bool(again) and bool(forced), "write_lock returns its path")

        p2 = os.path.join(td, "retro_sheet.html")
        with io.open(p2, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(_MINI)
        os.remove(lock_path)
        lock_from_html(p2, locks_dir=td, gate="G5", retro=True)
        lock2 = read_lock("selftest-mini", locks_dir=td)
        check(lock2["mode"] == "retro-unstamped" and lock2["content_hash"] == h0,
              "retro lock from unstamped source-of-record")

    print("review_binding selftest " + ("OK" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    if not argv or argv[0] not in ("stamp", "retro-lock"):
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    gate, locks_dir, paths = None, None, []
    i = 0
    while i < len(rest):
        if rest[i] == "--gate":
            gate = rest[i + 1]; i += 2
        elif rest[i] == "--locks-dir":
            locks_dir = rest[i + 1]; i += 2
        else:
            paths.append(rest[i]); i += 1
    if not paths:
        print("no sheet HTML given"); return 2
    for path in paths:
        if cmd == "stamp":
            with io.open(path, encoding="utf-8") as fh:
                doc = fh.read()
            stamped, chash = stamp(doc)
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(stamped)
            lock_path = lock_from_html(path, locks_dir=locks_dir, gate=gate)
            print("stamped %s\n  %s\n  lock -> %s" % (path, chash, lock_path))
        else:
            lock_path = lock_from_html(path, locks_dir=locks_dir, gate=gate, retro=True)
            print("retro lock for %s -> %s" % (path, lock_path))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main(sys.argv[1:]))
