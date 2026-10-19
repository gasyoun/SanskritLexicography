#!/usr/bin/env python3
"""NKRYa evidence block for the c1 PWG-RU generation prompts (H5263).

Sibling of `nkrya_evidence_card.py` (H5261): that one renders a full Markdown card a
human votes on, this one renders the SAME corpus facts as a compact advisory block
that rides inside the per-card prompt. Both read their facts through
`nkrya_evidence_card.gather()`, so there is exactly one query path and one cache.

Advisory, never an instruction (grill 22-09-2026 ruling 3,
docs/GRILL_NKRYA_SKILL_DECISIONS_22-09-2026.md): the block states corpus facts and one
reading rule; it never tells the model which candidate to pick.

Two halves:

  render_block(evidence)   pure formatter, `evidence` = the dict stored per card in
                           `manifest['inputs'][key]['nkrya']`
  inject()                 pre-fetch through the cached NkryaClient and write that dict
                           into an execution manifest (CLI `inject`)

The prompt half lives in `src/pilot/headless_worker.py::card_block`, which appends
`render_block(...)` when — and only when — a card carries an `nkrya` input. A manifest
without the key produces byte-identical prompt bytes, which `diff` below proves.

CLI:
  python src/nkrya_prompt_evidence.py inject --manifest M.json --out M.nkrya.json \\
      --card agni --heads туча:S --candidates сплошной:A,сгущающийся=сгущаться:V [--offline]
  python src/nkrya_prompt_evidence.py diff --manifest M.json --with M.nkrya.json --card agni
  python src/nkrya_prompt_evidence.py --selftest        # offline, committed cache only
"""

import argparse
import difflib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
PILOT = os.path.join(HERE, "pilot")
if PILOT not in sys.path:
    sys.path.insert(0, PILOT)

import nkrya_client as nk  # noqa: E402
import nkrya_evidence_card as card  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HEADER = ("\n--- advisory NKRYa corpus evidence (FACTS ONLY; НКРЯ, основной корпус; "
          "do not treat as a choice) ---")
READING_RULE = ("reading rule: the API returns only the top 10 collocates per relation, so "
                "\"not in top 10\" never means \"unattested\"; pair = candidate lemma within "
                "3 words of the head lemma, either order; 19c = texts created 1800-1899.")


def _freq(f):
    if not f or f.get("ipm") is None:
        return "ipm n/a"
    return "%.2f ipm (cat %s)" % (f["ipm"], f.get("category"))


def render_block(evidence):
    """The compact per-card advisory block. Empty evidence renders as the empty string."""
    if not evidence:
        return ""
    heads = evidence.get("heads") or []
    candidates = evidence.get("candidates") or []
    if not heads or not candidates:
        return ""
    lines = [HEADER, READING_RULE]
    for head in heads:
        lines.append("head %s:%s %s" % (head["lemma"], head.get("pos") or "?",
                                        _freq(head.get("freq"))))
    for cand in candidates:
        name = cand["surface"]
        if cand["surface"] != cand["lemma"]:
            name = "%s (lemma %s)" % (cand["surface"], cand["lemma"])
        for per_head in cand.get("per_head") or []:
            sketch = "; ".join(
                "%s #%d dice %.2f" % (s["relation"], s["rank"], s["dice"] or 0)
                for s in per_head.get("sketch") or []) or "not in top 10"
            # A missing count is the API returning no number for that pair — "n/a", never 0:
            # printing 0 would turn "we have no reading" into the claim "never co-occurs".
            main = per_head.get("pair_main")
            c19 = per_head.get("pair_19c")
            lines.append("  %s + %s | %s | sketch: %s | pair MAIN %s, 19c %s" % (
                name, per_head["head"], _freq(cand.get("freq")), sketch,
                "n/a" if main is None else main, "n/a" if c19 is None else c19))
    return "\n".join(lines)


def build_evidence(cli, heads, candidates):
    """Corpus facts for one card, through the ONE shared query path (H5261's gather).

    ``n=3`` is not cosmetic: the concordance payload (and therefore the disk-cache key)
    carries ``n``, so asking for fewer lines here would MISS every entry the evidence card
    already paid for and force a fresh live call. We take the same three lines and drop
    them below — the prompt wants counts, the cache wants its key.
    """
    data = card.gather(cli, heads, candidates, n=3)
    for cand in data["candidates"]:
        for per_head in cand["per_head"]:
            per_head.pop("lines", None)      # concordance lines belong to the card, not the prompt
    return data


def inject(manifest, key, evidence):
    """Attach `evidence` to one card of an execution manifest (in place)."""
    inputs = manifest.get("inputs") or {}
    if key not in inputs:
        raise KeyError("manifest has no card %r (cards: %s)"
                       % (key, ", ".join(sorted(inputs)) or "none"))
    inputs[key]["nkrya"] = evidence
    return manifest


def prompt_diff(before, after, keys):
    """Unified diff of the assembled production prompt, 0 paid calls."""
    import headless_worker as hw       # imported late: pilot/ is a heavy module tree

    a = hw.build_prompt(before, keys)
    b = hw.build_prompt(after, keys)
    diff = "\n".join(difflib.unified_diff(a.splitlines(), b.splitlines(),
                                          "prompt.before", "prompt.after", lineterm=""))
    return {"bytes_before": len(a.encode("utf-8")), "bytes_after": len(b.encode("utf-8")),
            "delta_bytes": len(b.encode("utf-8")) - len(a.encode("utf-8")),
            "identical": a == b, "diff": diff}


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _dump(path, payload):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")


def selftest():
    """Offline: the committed C07 cache is the fixture — no token, no network."""
    cli = nk.NkryaClient(cache_dir=os.path.join(HERE, "..", "pwg_ru", "nkrya_cache"),
                         offline=True)
    heads = card.parse_items("туча:S")
    candidates = card.parse_items("сплошной:A,сгущающийся=сгущаться:V")
    ev = build_evidence(cli, heads, candidates)
    assert ev["heads"][0]["lemma"] == "туча", ev["heads"]
    assert not any("lines" in ph for c in ev["candidates"] for ph in c["per_head"])
    block = render_block(ev)
    assert block.startswith(HEADER), block[:80]
    assert "head туча:S" in block, block
    assert "сгущающийся (lemma сгущаться) + туча" in block, block
    assert "pair MAIN" in block, block
    assert render_block({}) == "" and render_block({"heads": [], "candidates": []}) == ""

    import headless_worker as hw
    manifest = {"prompt": {"preamble": "P", "translation": "T", "grammar": "G",
                           "grammars": {}, "nws_rule": ""},
                "inputs": {"c": {"skeleton": "S", "portrait": "{}", "ls": 0, "sk": 0,
                                 "nws": 0}},
                "suggestions": {}}
    plain = hw.build_prompt(manifest, ["c"])
    assert hw.build_prompt(json.loads(json.dumps(manifest)), ["c"]) == plain
    after = inject(json.loads(json.dumps(manifest)), "c", ev)
    report = prompt_diff(manifest, after, ["c"])
    assert not report["identical"] and report["delta_bytes"] == len(block.encode("utf-8"))
    assert hw.build_prompt(after, ["c"]) == plain + block
    try:
        inject(json.loads(json.dumps(manifest)), "missing", ev)
    except KeyError:
        pass
    else:
        raise AssertionError("inject must refuse an unknown card key")
    print("nkrya_prompt_evidence selftest OK (11 checks, offline committed cache)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", nargs="?", choices=("inject", "diff"))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--manifest")
    ap.add_argument("--out")
    ap.add_argument("--with", dest="with_manifest")
    ap.add_argument("--card")
    ap.add_argument("--heads")
    ap.add_argument("--candidates")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--json-out")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest()
        return 0
    if a.mode == "inject":
        if not (a.manifest and a.out and a.card and a.heads and a.candidates):
            ap.error("inject needs --manifest --out --card --heads --candidates")
        cli = nk.NkryaClient(offline=a.offline)
        try:
            ev = build_evidence(cli, card.parse_items(a.heads),
                                card.parse_items(a.candidates))
        except nk.NkryaError as exc:
            print("NKRYa: %s" % exc, file=sys.stderr)
            return 2
        _dump(a.out, inject(_load(a.manifest), a.card, ev))
        print("injected %d head(s) / %d candidate(s) into card %s -> %s"
              % (len(ev["heads"]), len(ev["candidates"]), a.card, a.out))
        return 0
    if a.mode == "diff":
        if not (a.manifest and a.with_manifest and a.card):
            ap.error("diff needs --manifest --with --card")
        report = prompt_diff(_load(a.manifest), _load(a.with_manifest), [a.card])
        print(report["diff"])
        print("\nbytes %d -> %d (delta %+d), identical=%s"
              % (report["bytes_before"], report["bytes_after"], report["delta_bytes"],
                 report["identical"]))
        if a.json_out:
            _dump(a.json_out, report)
        return 0
    ap.error("give a mode (inject|diff) or --selftest")


if __name__ == "__main__":
    sys.exit(main())
