#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h3969_german_latin_sweep.py — German markers OUTSIDE <ab> in the ru field -> Latin.

Why this exists
---------------
H2849 (19-08-2026) swept free-floating German case markers in the ``ru`` field to
their Latin forms across 694 rows, but its pass did not reach the Grassmann/NWS-derived
material. H3959 (02-09-2026) re-ran that class of check and measured what is left:
**120 hits over 65 distinct rows**, tokens ``Akk`` x110, ``Lok`` x8, ``Ausgabe`` x1,
``Praes`` x1 -- see ``RussianTranslation/ABBREVIATIONS_RU.md`` -> "Store-residue verdict".
H3959 deliberately scoped and did not run the sweep; H3969 (this script) runs it.

Direction
---------
All swept tokens are **Bucket B** under MG's 02-09-2026 ruling ("some remain Latin"):
German -> **Latin**, never German -> Russian. That is the same direction H2849 used and
the one the ruling forbids only for Bucket A (editorial/domain labels, which go Russian
via ``pwg_ab_ru.RU_MAP``).

Scope fences
------------
* ``ru`` field only. The ``de`` field is the German source column and is never touched.
* Anything inside an ``<ab>`` tag is render-time and belongs to ``pwg_ab_ru`` -- skipped.
* ``{#...#}`` / ``{%...%}`` Sanskrit spans and ``<ls>`` citations are skipped.
* Bracketed bare-Latin domain tags (``[Gen, unsp]`` class, H2849's known false positive)
  are skipped; kept even though no token in ``GERMAN_TO_LATIN`` can currently collide,
  so a future widening of the token set cannot resurrect that bug.
* The store is resolved through ``store_path.canonical_store()`` -- never the executing
  worktree's copy (SanskritLexicography FINDINGS Sec.600).

Run::

    python src/h3969_german_latin_sweep.py census      # count, change nothing
    python src/h3969_german_latin_sweep.py --apply     # rewrite the store in place
    python src/h3969_german_latin_sweep.py --selftest
"""
import argparse
import collections
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from store_path import canonical_store  # noqa: E402

#: German-only markers and the Latin form each becomes. Bucket B only.
#: ``Akk``/``Lok`` reuse H2849's shipped targets verbatim; ``Praes.`` is the ASCII
#: Latin twin of the umlauted German ``Praes`` spelling already listed in
#: ``pwg_ab_ru.BUCKET_B``.
GERMAN_TO_LATIN = {
    "Akk": "Acc.",
    "Akkus": "Acc.",
    "Lok": "Loc.",
    "Instr": "Ins.",
    "Präs": "Praes.",
}

#: Declared undecided -- detected and reported, never substituted. H3969's ambiguity
#: policy: a named residue row is honest, a guessed substitution is not. ``Ausgabe``
#: ("edition") is not a grammatical category at all, so it has no Latin terminus
#: technicus in the Bucket B sense; routing it to ``Ed.`` would be an editorial
#: decision, not a mechanical marker substitution.
RESIDUE_TOKENS = {
    "Ausgabe": "not a grammatical category -- no Bucket B Latin equivalent; "
               "routing it to 'Ed.' is an editorial call, not a marker substitution",
}

#: Regions that are not Russian prose. Blanked (length-preserving) before matching.
_SKIP = re.compile(r"<ab>.*?</ab>|<ls\b[^>]*>.*?</ls>|\{[#%].*?[#%]\}", re.S)

#: H2849's domain-tag guard: a bracket span holding ONLY bare Latin tag words joined
#: by ',' or ':' -- never Cyrillic, parens or '='. ``[Gen, unsp]`` is a text-period
#: label, not a case.
_DOMAIN_TAG = re.compile(r"\[(?:[A-Za-z]+\.?)(?:\s*[:,]\s*[A-Za-z]+\.?)*\]")

_WORD = r"[^\W\d_]"  # a letter in any script, so 'Akkusativ' and 'Loka' never match

_ALL_TOKENS = sorted(
    list(GERMAN_TO_LATIN) + list(RESIDUE_TOKENS), key=len, reverse=True
)
_HIT = re.compile(
    r"(?<!%s)(%s)\.?(?!%s)" % (_WORD, "|".join(re.escape(t) for t in _ALL_TOKENS), _WORD)
)

_DEFAULT_STORE = canonical_store(os.path.join(HERE, "pwg_ru_translated.jsonl"))


def _mask(text):
    """Blank every non-prose region, preserving offsets so spans stay comparable."""
    masked = _SKIP.sub(lambda m: " " * (m.end() - m.start()), text)
    return _DOMAIN_TAG.sub(lambda m: " " * (m.end() - m.start()), masked)


def scan_body(text):
    """``[(token, start, end, context)]`` for every German marker in Russian prose."""
    if not text:
        return []
    masked = _mask(text)
    out = []
    for m in _HIT.finditer(masked):
        out.append((m.group(1), m.start(), m.end(),
                    text[max(0, m.start() - 40):m.end() + 20].replace("\n", " ")))
    return out


def sweep_body(text):
    """``(new_text, [(token, latin)])`` -- substitute what is mapped, leave residue."""
    hits = scan_body(text)
    if not hits:
        return text, []
    applied, pieces, cursor = [], [], 0
    for token, start, end, _ctx in hits:
        latin = GERMAN_TO_LATIN.get(token)
        if latin is None:  # declared residue: detected, deliberately untouched
            continue
        pieces.append(text[cursor:start])
        pieces.append(latin)
        cursor = end
        applied.append((token, latin))
    pieces.append(text[cursor:])
    return "".join(pieces), applied


def _rows(store_path):
    with io.open(store_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def census(store_path=None, field="ru"):
    """``(by_token, by_layer, rows_hit, rows_total, residue_ctx)``."""
    store_path = store_path or _DEFAULT_STORE
    by_token, by_layer = collections.Counter(), collections.Counter()
    rows_hit = rows_total = 0
    residue_ctx = []
    for row in _rows(store_path):
        rows_total += 1
        hits = scan_body(row.get(field) or "")
        if not hits:
            continue
        rows_hit += 1
        by_layer[row.get("layer") or "?"] += 1
        for token, _s, _e, ctx in hits:
            by_token[token] += 1
            if token in RESIDUE_TOKENS:
                residue_ctx.append((row.get("key1"), row.get("layer"), ctx))
    return by_token, by_layer, rows_hit, rows_total, residue_ctx


def apply_sweep(store_path=None, field="ru"):
    """Rewrite the store in place. Returns ``(rows_changed, subs, by_token, by_layer)``."""
    store_path = store_path or _DEFAULT_STORE
    tmp = store_path + ".h3969.tmp"
    rows_changed = subs = 0
    by_token, by_layer = collections.Counter(), collections.Counter()
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as out:
        for row in _rows(store_path):
            body = row.get(field) or ""
            new, applied = sweep_body(body)
            if applied:
                row[field] = new
                rows_changed += 1
                subs += len(applied)
                by_layer[row.get("layer") or "?"] += 1
                for token, _latin in applied:
                    by_token[token] += 1
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
    os.replace(tmp, store_path)
    return rows_changed, subs, by_token, by_layer


def _print_census(tag, store_path):
    by_token, by_layer, rows_hit, rows_total, residue_ctx = census(store_path)
    print("%s  store=%s" % (tag, store_path))
    print("  rows scanned: %d   rows with a hit: %d   hits: %d"
          % (rows_total, rows_hit, sum(by_token.values())))
    print("  by token: %s" % (", ".join("%s x%d" % (t, c)
                                        for t, c in by_token.most_common()) or "(none)"))
    print("  by layer: %s" % (", ".join("%s %d" % (l, c)
                                        for l, c in by_layer.most_common()) or "(none)"))
    for key1, layer, ctx in residue_ctx:
        print("  RESIDUE key1=%s layer=%s  ...%s..." % (key1, layer, ctx))
    return by_token, by_layer, rows_hit, rows_total


def selftest():
    ok = True

    def check(label, got, want):
        nonlocal ok
        if got != want:
            ok = False
            print("FAIL %s: got %r want %r" % (label, got, want))

    check("plain akk", sweep_body("идти (Akk)")[0],
          "идти (Acc.)")
    check("dotted akk", sweep_body("(Akk.)")[0], "(Acc.)")
    check("lok", sweep_body("(Lok)")[0], "(Loc.)")
    check("inside ab untouched", sweep_body("<ab>Akk</ab>")[0], "<ab>Akk</ab>")
    check("slp1 span untouched", sweep_body("{#Akk#}")[0], "{#Akk#}")
    check("ls untouched", sweep_body('<ls n="x">Akk</ls>')[0], '<ls n="x">Akk</ls>')
    check("domain tag untouched", sweep_body("[Gen, unsp]")[0], "[Gen, unsp]")
    check("word boundary", sweep_body("Akkusativ")[0], "Akkusativ")
    check("residue declared", sweep_body("(Ausgabe)")[0], "(Ausgabe)")
    check("residue detected", [h[0] for h in scan_body("(Ausgabe)")], ["Ausgabe"])
    check("praes", sweep_body("(Präs.)")[0], "(Praes.)")
    check("two hits one row", sweep_body("(Akk, Lok)")[0], "(Acc., Loc.)")
    check("de field never seen here", sweep_body("")[0], "")
    print("SELFTEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", nargs="?", default="census", choices=["census"])
    ap.add_argument("--apply", action="store_true", help="rewrite the store in place")
    ap.add_argument("--store", default=None, help="override the resolved store path")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    store = args.store or _DEFAULT_STORE
    if not args.apply:
        _print_census("CENSUS", store)
        return 0

    _print_census("PRE ", store)
    rows_changed, subs, by_token, by_layer = apply_sweep(store)
    print("APPLIED  rows changed: %d   substitutions: %d" % (rows_changed, subs))
    print("  by token: %s" % ", ".join("%s->%s x%d" % (t, GERMAN_TO_LATIN[t], c)
                                       for t, c in by_token.most_common()))
    print("  by layer: %s" % ", ".join("%s %d" % (l, c) for l, c in by_layer.most_common()))
    _print_census("POST", store)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
