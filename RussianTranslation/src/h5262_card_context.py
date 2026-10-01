#!/usr/bin/env python3
"""H5262 — gloss context for flagged lemmas, read from the PWG-RU store (read-only).

The NKRYa verdicts in reports/H5262_flags.json name a lemma and the cards carrying it;
a reviewer needs the actual gloss line and the German sense it renders. This pulls, per
flagged lemma, up to `--per-lemma` cards: the `{%...%}` gloss span(s) containing one of
the lemma's surface forms, the German meaning spans of the card's `de` text and its review status.

The store lives only on the Windows box (rights-fenced data home), so the usual run is
there; the output is a small JSON the sheet builder joins on the Mac:

  python src/h5262_card_context.py --flags reports/H5262_flags.json \\
      --out reports/H5262_flag_context.json
  python src/h5262_card_context.py --selftest
"""

import argparse
import io
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
GLOSS_SPAN = re.compile(r"\{%(.*?)%\}", re.S)
DE_SPANS = 6


def _default_store():
    sys.path.insert(0, HERE)
    import store_path
    return store_path.canonical_store(os.path.join(HERE, "pwg_ru_translated.jsonl"))


def context(flags, store, per_lemma=3):
    """{lemma: [card context, ...]} for every flagged lemma, store read once."""
    wanted = {}                      # subcard -> [(lemma, forms)]
    for r in flags["flagged"]:
        forms = [f.lower() for f in (r.get("forms") or [])] or [r["lemma"]]
        for card in (r.get("cards") or [])[:per_lemma]:
            wanted.setdefault(card, []).append((r["lemma"], forms))
    out = {r["lemma"]: [] for r in flags["flagged"]}
    with io.open(store, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            hits = wanted.get(rec.get("subcard"))
            if not hits:
                continue
            spans = GLOSS_SPAN.findall(rec.get("ru") or "")
            for lemma, forms in hits:
                pat = re.compile(r"(?<![А-Яа-яЁё])(%s)(?![А-Яа-яЁё])"
                                 % "|".join(re.escape(f) for f in forms), re.I)
                matched = [s.strip() for s in spans if pat.search(s)]
                # `subcard` is not unique in the store — one subcard spans several sense
                # records (live 24-09-2026) — so only a record whose gloss actually carries
                # the form is context; its siblings would show the reviewer the wrong line.
                if not matched or len(out[lemma]) >= per_lemma:
                    continue
                # PWG's German meaning spans only: {%...%} in `de` is German prose by the
                # markup contract; the {#...#} Sanskrit citations around them are not
                # what a reviewer compares with the Russian gloss.
                de = [" ".join(g.split()) for g in GLOSS_SPAN.findall(rec.get("de") or "")]
                out[lemma].append({
                    "subcard": rec.get("subcard"), "key1": rec.get("key1"),
                    "iast": rec.get("iast"), "review_status": rec.get("review_status"),
                    "sense_tag": rec.get("sense_tag"), "ru_spans": matched,
                    "de_gloss": de[:DE_SPANS],
                })
    for lemma in out:
        out[lemma].sort(key=lambda c: c["subcard"] or "")
    return out


def selftest():
    import tempfile
    tmp = tempfile.mkdtemp(prefix="h5262ctx_")
    store = os.path.join(tmp, "store.jsonl")
    with io.open(store, "w", encoding="utf-8") as fh:
        for rec in ({"subcard": "c1", "key1": "yuj", "iast": "yuj",
                     "ru": "1) {%союзить, соединять%}; 2) {%запрягать%}",
                     "de": "{%verbinden,  vereinigen%} {#yuj#}", "review_status": "pending"},
                    {"subcard": "c1", "key1": "yuj", "ru": "{%запрягать%}", "de": "anschirren"},
                    {"subcard": "c2", "key1": "x", "ru": "{%друг%}", "de": "Freund"}):
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    flags = {"flagged": [{"lemma": "союзить", "forms": ["союзить"], "cards": ["c1", "zz"]}]}
    ctx = context(flags, store)
    ok = (len(ctx["союзить"]) == 1
          and ctx["союзить"][0]["ru_spans"] == ["союзить, соединять"]
          and ctx["союзить"][0]["de_gloss"] == ["verbinden, vereinigen"])
    if not ok:
        raise SystemExit("SELFTEST FAIL: %r" % ctx)
    print("h5262_card_context selftest OK (offline)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--flags")
    ap.add_argument("--store")
    ap.add_argument("--out")
    ap.add_argument("--per-lemma", type=int, default=3)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.flags and a.out):
        ap.error("--flags and --out are required")
    with io.open(a.flags, encoding="utf-8") as fh:
        flags = json.load(fh)
    ctx = context(flags, a.store or _default_store(), a.per_lemma)
    with io.open(a.out, "w", encoding="utf-8") as fh:
        json.dump(ctx, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("context: %d lemmas, %d cards -> %s"
          % (len(ctx), sum(len(v) for v in ctx.values()), a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
