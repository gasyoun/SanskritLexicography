#!/usr/bin/env python3
"""Verify one release envelope against the bytes it pins (V6 verification).

The envelope (data/manifest/envelopes/*.envelope.json, schema
release-envelope-v1) is the object dashboards and manuscripts pin. This script
is the rerun side of that contract: it re-derives every digest the envelope
declares from the bytes actually on disk / in git, and reports PASS/FAIL/SKIP
per check. It never repairs, never rewrites, never trusts a recorded digest it
could not recompute. Self-contained (stdlib only, Python >= 3.9); the kosha
scripts/envelope_check.py is the reference implementation this adapts.

Checks:
  CHK-1  envelope schema + required fields present
  CHK-2  every pinned artifact's lf-canonical sha256 recomputes from bytes
  CHK-3  per-dataset sha256/rows/size_bytes in output_digests recompute from
         disk and agree with the pinned artifact (double-entry)
  CHK-4  each source pin re-derives per its recorded pin_rule / sha256_form:
         lf-canonical blobs are digested at the pin commit (rev-list
         --before re-derived when the pin_rule states one); set-digest:census
         re-digests the 44 v02 main-text blobs at the pin. SKIP when the
         sibling clone is absent on this box. Unknown sha256_form = FAIL.
  CHK-5  code_revision: release tag resolves to the recorded commit

Exit 0 when every run check passes (SKIP allowed); exit 1 on any FAIL.

Usage:
    python scripts/envelope_check.py --envelope data/manifest/envelopes/v1.144.164.envelope.json
    python scripts/envelope_check.py --envelope ... --source-root /some/GitHub
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# canonical repo name even from inside a claimed worktree (…-h<id>-<pid>)
REPO_BASENAME = re.sub(r"-h\d+-\d+$", "", REPO.name)

SCHEMA = "release-envelope-v1"
REQUIRED = (
    "schema",
    "envelope_id",
    "hub",
    "release_kind",
    "release_tag",
    "created",
    "code_revision",
    "pinned_artifacts",
    "source_pins",
    "output_digests",
    "config",
    "tool_versions",
    "licence",
    "checks",
    "review",
    "citation",
    "publication_state",
)

DATASET_KEYS = ("release_asset", "sha256", "rows", "size_bytes")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def canonical(b):
    """LF-canonical form (CRLF normalised) — the org digest convention."""
    return b.replace(b"\r\n", b"\n")


def git(repo, *args, binary=False):
    out = subprocess.run(["git", "-C", str(repo)] + list(args), capture_output=True)
    if out.returncode != 0:
        return None
    return out.stdout if binary else out.stdout.decode("utf-8", "replace").strip()


def detect_source_root():
    """Cheapest sibling-clone lookup: the org checkout root beside this repo."""
    for cand in (REPO.parent, Path.home() / "Documents" / "GitHub"):
        if cand.is_dir():
            return cand
    return REPO.parent


def local_clone(source_root, repo_url):
    name = repo_url.rstrip("/").rsplit("/", 1)[-1]
    if name.endswith(".git"):
        name = name[:-4]
    if name == REPO_BASENAME:
        return REPO
    cand = source_root / name
    return cand if cand.is_dir() else None


def digest_file(path):
    return sha256_bytes(canonical(path.read_bytes()))


def rows_data(path):
    return len(canonical(path.read_bytes()).decode("utf-8").splitlines()) - 1


def set_digest_census(repo, pin):
    """set-digest:census — path-sorted 'v02/<code>/<code>.tx<tab><sha>' lines."""
    listing = git(repo, "ls-tree", "-r", "--name-only", pin, "v02/", binary=True)
    if listing is None:
        return None
    paths = sorted(
        p for p in listing.decode("utf-8").splitlines()
        if len(p.split("/")) == 3 and p.split("/")[2] == p.split("/")[1] + ".txt"
    )
    lines = []
    for p in paths:
        blob = git(repo, "show", "{}:{}".format(pin, p), binary=True)
        if blob is None:
            return None
        lines.append("{}\t{}".format(p, sha256_bytes(canonical(blob))))
    return sha256_bytes(canonical(("\n".join(lines) + "\n").encode("utf-8")))


def revlist_rule_pin(repo, pin_rule):
    """Re-derive a pin from a 'git rev-list -1 --before=<ts> ... -- <path>' rule.

    The pathspec is the first bare token after ' -- ' (prose may follow it in
    the recorded pin_rule); an empty rev-list result is a failure, not a pass.
    """
    m = re.search(r"--before=(\S+)", pin_rule)
    if not m:
        return None
    args = ["rev-list", "-1", "--before=" + m.group(1), "HEAD"]
    pm = re.search(r"--\s+(\S+)", pin_rule[m.end():])
    if pm:
        args += ["--", pm.group(1)]
    out = git(repo, *args)
    return out or None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--envelope", required=True)
    ap.add_argument("--source-root", default=None,
                    help="root under which sibling clones are looked up (default: beside this repo, then ~/Documents/GitHub)")
    args = ap.parse_args()

    env_path = Path(args.envelope)
    if not env_path.is_absolute():
        env_path = REPO / env_path
    if not env_path.is_file():
        print("FATAL: envelope not found: {}".format(env_path))
        return 1
    env = json.loads(canonical(env_path.read_bytes()))

    source_root = Path(args.source_root) if args.source_root else detect_source_root()
    results = []
    extras = []

    def record(cid, ok, detail, skipped=False):
        results.append((cid, "SKIP" if skipped else ("pass" if ok else "FAIL"), detail))

    # CHK-1 schema + required fields
    missing = [k for k in REQUIRED if k not in env or env[k] in (None, "", [], {})]
    record(
        "CHK-1-schema",
        not missing,
        "schema={}".format(env.get("schema"))
        + ("" if not missing else "; missing/empty: {}".format(", ".join(missing))),
    )
    if env.get("schema") != SCHEMA:
        print(report(results, fatal="schema is {}, expected {}".format(env.get("schema"), SCHEMA)))
        return 1

    # CHK-2 pinned artifacts recompute from bytes
    pin_drift = []
    pinned_by_path = {}
    for p in env["pinned_artifacts"]:
        f = REPO / p["path"]
        if not f.is_file():
            pin_drift.append("{}: file absent".format(p["path"]))
            continue
        pinned_by_path[p["path"]] = p
        dig = digest_file(f)
        if dig != p["sha256"]:
            pin_drift.append("{}: {} != declared {}".format(p["path"], dig[:16], p["sha256"][:16]))
    record("CHK-2-pinned-artifacts", not pin_drift,
           "{} artifact(s)".format(len(env["pinned_artifacts"])))
    extras.extend(pin_drift)

    # CHK-3 output parity (recompute + double-entry against pinned artifacts)
    out_drift = []
    declared = env["output_digests"]["datasets"]
    for ds_id, out in sorted(declared.items()):
        for key in DATASET_KEYS:
            if key not in out:
                out_drift.append("{}: missing key {}".format(ds_id, key))
        asset = out.get("release_asset", "")
        f = REPO / asset
        if not f.is_file():
            out_drift.append("{}: release asset absent: {}".format(ds_id, asset))
            continue
        if asset not in pinned_by_path:
            out_drift.append("{}: release asset is not a pinned artifact: {}".format(ds_id, asset))
            continue
        dig, rows, size = digest_file(f), rows_data(f), f.stat().st_size
        if dig != out.get("sha256"):
            out_drift.append("{}: sha256 {} != declared {}".format(ds_id, dig[:16], str(out.get("sha256"))[:16]))
        if rows != out.get("rows"):
            out_drift.append("{}: rows {} != declared {}".format(ds_id, rows, out.get("rows")))
        if size != out.get("size_bytes"):
            out_drift.append("{}: size_bytes {} != declared {}".format(ds_id, size, out.get("size_bytes")))
        if dig != pinned_by_path[asset]["sha256"]:
            out_drift.append("{}: digest disagrees with its pinned artifact".format(ds_id))
    record("CHK-3-output-parity", not out_drift, "{} dataset(s)".format(len(declared)))
    extras.extend(out_drift)

    # CHK-4 source pins re-derived per their own rules
    pins_ok = True
    pin_msgs = []
    for sp in env["source_pins"]:
        ds_id = sp["dataset"]
        repo = local_clone(source_root, sp["source_repo"])
        if repo is None:
            record("CHK-4-source-pin:{}".format(ds_id), True,
                   "sibling clone absent on this box", skipped=True)
            continue
        if sp["source_repo"].rstrip("/").endswith("/" + REPO_BASENAME):
            repo = REPO
        if git(repo, "cat-file", "-t", sp["pin_commit"]) != "commit":
            pin_msgs.append("{}: pin commit unresolvable in {}".format(ds_id, repo.name))
            record("CHK-4-source-pin:{}".format(ds_id), False, "pin unresolvable")
            pins_ok = False
            continue
        if sp["pin_rule"].startswith("git rev-list"):
            derived = revlist_rule_pin(repo, sp["pin_rule"])
            if derived is None:
                pin_msgs.append("{}: pin_rule not re-derivable".format(ds_id))
                record("CHK-4-source-pin:{}".format(ds_id), False, "not re-derivable")
                pins_ok = False
                continue
            if derived != sp["pin_commit"]:
                pin_msgs.append("{}: pin moved {} -> {}".format(ds_id, sp["pin_commit"][:12], derived[:12]))
                record("CHK-4-source-pin:{}".format(ds_id), False, "pin moved")
                pins_ok = False
                continue
        form = sp.get("sha256_form", "")
        if form == "lf-canonical":
            blob = git(repo, "show", "{}:{}".format(sp["pin_commit"], sp["source_path"]), binary=True)
            if blob is None:
                pin_msgs.append("{}: blob unresolvable at pin".format(ds_id))
                record("CHK-4-source-pin:{}".format(ds_id), False, "blob unresolvable")
                pins_ok = False
                continue
            dig = sha256_bytes(canonical(blob))
        elif form.startswith("set-digest:census"):
            dig = set_digest_census(repo, sp["pin_commit"])
            if dig is None:
                pin_msgs.append("{}: set-digest not re-derivable".format(ds_id))
                record("CHK-4-source-pin:{}".format(ds_id), False, "set-digest failed")
                pins_ok = False
                continue
        else:
            pin_msgs.append("{}: unknown sha256_form {!r} — fail closed".format(ds_id, form))
            record("CHK-4-source-pin:{}".format(ds_id), False, "unknown digest form")
            pins_ok = False
            continue
        ok = dig == sp["sha256"]
        pin_msgs.append("{}: pin {} digests {} ({})".format(
            ds_id, sp["pin_commit"][:12], dig[:16], "match" if ok else "MISMATCH"))
        record("CHK-4-source-pin:{}".format(ds_id), ok, pin_msgs[-1])
        if not ok:
            pins_ok = False
    record("CHK-4-source-pins", pins_ok, "{} pin(s)".format(len(env["source_pins"])))
    extras.extend(pin_msgs)

    # CHK-5 code revision: tag resolves to the recorded commit
    cr = env["code_revision"]
    tag_commit = git(REPO, "rev-parse", "{}^{{commit}}".format(cr.get("tag", "")))
    record("CHK-5-code-revision", tag_commit == cr.get("commit"),
           "{} -> {}{}".format(cr.get("tag"), str(cr.get("commit"))[:12],
                               "" if tag_commit == cr.get("commit") else " (tag resolves to {})".format(str(tag_commit)[:12])))

    print(report(results, extra=extras))
    return 0 if all(r != "FAIL" for _, r, _ in results) else 1


def report(results, fatal=None, extra=None):
    lines = []
    if fatal:
        lines.append("FATAL: " + fatal)
    for cid, res, detail in results:
        lines.append("  [{}] {} — {}".format(res.rjust(4), cid, detail))
    for e in extra or []:
        lines.append("         · " + e)
    passed = sum(1 for _, r, _ in results if r == "pass")
    skipped = sum(1 for _, r, _ in results if r == "SKIP")
    failed = sum(1 for _, r, _ in results if r == "FAIL")
    lines.append(
        "envelope_check: {} pass, {} skip, {} fail — {}".format(
            passed, skipped, failed, "PASS" if failed == 0 else "FAIL"
        )
    )
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
