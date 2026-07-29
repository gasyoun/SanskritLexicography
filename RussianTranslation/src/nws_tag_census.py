#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nws_tag_census — the real vocabulary of NWS sense tags, counted (H1820).

MG, reading a G5 card whose tooltip said «unsp — домен не указан»: «А какие
вообще бывают домены? … По всем аббревиатурам и их комбинациям нужна
статистика.» Fair: a tooltip that names ONE value teaches nothing about the
dimension it belongs to.

The vocabulary cannot be read off our translation store — that holds the ~11k
senses we happened to translate, a biased slice. It is read here off the scraped
NWS corpus (`pilot/nws/*.json`, ~168k lemma cards), which is the whole
dictionary.

An NWS entry is a `>`-separated chain in which a sense costs TWO blocks — its
`<diasystem> , <domain>` header, then its body:

    ādika Ved , unsp > [ifc (Bhvr)] ādi . ityādi : so beginnend. ṚV(Sā) I 165, 11
        . Windisch 1883 : 106 > Śā , Med > [ifc] beginning with. …

(four senses above = four header blocks + four body blocks). Bracketed
positional/grammatical tags — `[ifc]`, `[ifc (Bhvr)]`, `[iic]` — live in the BODY
block, so they are attributed to the diasystem of the header that preceded them.
This script counts, over the whole corpus:

  * diasystem values (slot 1) and domain values (slot 2), separately;
  * the diasystem × domain MATRIX — which combinations actually occur;
  * bracket tags and their inner qualifiers, and their pairings.

Lemma counts are reported beside sense counts on purpose: a tag can be frequent
in senses but concentrated in few words, and a reviewer deciding whether a tag is
worth a facet needs both numbers.

Output: a Markdown report (default) or JSON (`--json`) for a UI to consume.

  python nws_tag_census.py [--dir PATH] [--json OUT.json] [--md OUT.md]
                           [--limit N] [--selftest]
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
DEFAULT_DIR = os.path.join(HERE, "pilot", "nws")

#: A sense-block header: `Ved , unsp` / `Śā , Med` / `Buddh , unsp`. Anchored at
#: the start of a block so a comma inside a gloss cannot masquerade as one.
_HEADER = re.compile(
    r"^\s*(?P<dia>[A-ZĀŚṚṢṬḌÑṄa-z][\wĀāĪīŪūṚṛŚśṢṣṬṭḌḍÑñṄṅ.]{0,12})"
    r"\s*,\s*(?P<dom>[\wĀāĪīŪūṚṛŚśṢṣÑñ.]{1,14})\s*(?=[>\[]|$)")

#: Bracketed tags inside a block: `[ifc]`, `[ifc (Bhvr)]`, `[iic (Tatp)]`.
_BRACKET = re.compile(r"\[(?P<key>[A-Za-z.]{2,10})(?:\s*\((?P<sub>[^)]{1,20})\))?\]")


def iter_cards(root, limit=None):
    n = 0
    for name in sorted(os.listdir(root)):
        if not name.endswith(".json"):
            continue
        try:
            with io.open(os.path.join(root, name), encoding="utf-8") as fh:
                rec = json.load(fh)
        except (OSError, ValueError):
            continue
        if not (rec.get("nws") or "").strip():
            continue
        yield rec
        n += 1
        if limit and n >= limit:
            return


def census_text(rec, acc):
    """Fold ONE lemma card into the accumulators. Split out from census() so the
    selftest can exercise the parse without touching the corpus."""
    iast = rec.get("iast") or rec.get("key1") or ""
    text = rec.get("nws") or ""
    if iast and text.startswith(iast):
        text = text[len(iast):]          # drop the leading lemma
    cur_dia = None
    for block in text.split(">"):
        block = block.strip()
        if not block:
            continue
        acc["blocks"] += 1
        m = _HEADER.match(block)
        if m:
            d, k = m.group("dia").rstrip("."), m.group("dom").rstrip(".")
            acc["diasystem"][d] += 1
            acc["domain"][k] += 1
            acc["matrix"][(d, k)] += 1
            acc["senses"] += 1
            cur_dia = d
            if iast:
                acc["lem_dia"][d].add(iast)
                acc["lem_dom"][k].add(iast)
        else:
            acc["blocks_without_header"] += 1
        for b in _BRACKET.finditer(block):
            key = b.group("key").rstrip(".")
            acc["bracket"][key] += 1
            if iast:
                acc["lem_bracket"][key].add(iast)
            if b.group("sub"):
                sub = b.group("sub").strip()
                acc["bracket_qualifier"][sub] += 1
                acc["bracket_pairs"][(key, sub)] += 1
                if iast:
                    acc["lem_bracket"][sub].add(iast)
            if cur_dia:
                acc["diasystem_x_bracket"][(cur_dia, key)] += 1


def new_acc():
    return {
        "cards": 0, "blocks": 0, "senses": 0, "blocks_without_header": 0,
        "diasystem": collections.Counter(), "domain": collections.Counter(),
        "matrix": collections.Counter(), "bracket": collections.Counter(),
        "bracket_qualifier": collections.Counter(),
        "bracket_pairs": collections.Counter(),
        "diasystem_x_bracket": collections.Counter(),
        "lem_dia": collections.defaultdict(set),
        "lem_dom": collections.defaultdict(set),
        "lem_bracket": collections.defaultdict(set),
    }


def census(root, limit=None):
    acc = new_acc()
    for rec in iter_cards(root, limit):
        acc["cards"] += 1
        census_text(rec, acc)
    return acc


def _rows(counter, total, lemmas=None, top=None):
    out = []
    for k, v in counter.most_common(top):
        pct = 100.0 * v / total if total else 0.0
        out.append((k, v, pct, len(lemmas[k]) if lemmas and k in lemmas else None))
    return out


def to_markdown(c):
    L = []
    A = L.append
    A("# NWS sense tags — the full vocabulary, counted")
    A("")
    A("_Auto-generated by `src/nws_tag_census.py` — do not hand-edit._")
    A("")
    A("Source: **%d** scraped NWS lemma cards (`src/pilot/nws/*.json`) carrying "
      "**%d** tagged senses across %d `>`-separated blocks. A sense costs two "
      "blocks — its `<diasystem> , <domain>` header and its body — so the %d "
      "header-less blocks are mostly those bodies."
      % (c["cards"], c["senses"], c["blocks"], c["blocks_without_header"]))
    A("")
    tot = sum(c["diasystem"].values())
    A("## Slot 1 — diasystem (tradition / period the sense belongs to)")
    A("")
    A("| tag | senses | % | lemmas |")
    A("|---|---:|---:|---:|")
    for k, v, pct, lem in _rows(c["diasystem"], tot, c["lem_dia"]):
        A("| `%s` | %d | %.1f%% | %s |" % (k, v, pct, lem if lem is not None else "—"))
    A("")
    tot = sum(c["domain"].values())
    A("## Slot 2 — domain (subject field)")
    A("")
    A("| tag | senses | % | lemmas |")
    A("|---|---:|---:|---:|")
    for k, v, pct, lem in _rows(c["domain"], tot, c["lem_dom"]):
        A("| `%s` | %d | %.1f%% | %s |" % (k, v, pct, lem if lem is not None else "—"))
    A("")
    A("## The matrix — which diasystem × domain combinations occur")
    A("")
    dias = [k for k, _ in c["diasystem"].most_common()]
    doms = [k for k, _ in c["domain"].most_common()]
    A("| dia \\\\ dom | " + " | ".join("`%s`" % d for d in doms) + " |")
    A("|---" * (len(doms) + 1) + "|")
    for d in dias:
        cells = [str(c["matrix"][(d, k)]) if c["matrix"].get((d, k)) else "·" for k in doms]
        A("| `%s` | " % d + " | ".join(cells) + " |")
    A("")
    tot = sum(c["bracket"].values())
    A("## Bracket tags — position in the compound / part of speech")
    A("")
    A("| tag | occurrences | % | lemmas |")
    A("|---|---:|---:|---:|")
    for k, v, pct, lem in _rows(c["bracket"], tot, c["lem_bracket"]):
        A("| `%s` | %d | %.1f%% | %s |" % (k, v, pct, lem if lem is not None else "—"))
    A("")
    if c["bracket_pairs"]:
        A("## Bracket combinations — `[key (qualifier)]`")
        A("")
        A("| combination | occurrences |")
        A("|---|---:|")
        for (k, sub), v in c["bracket_pairs"].most_common(40):
            A("| `[%s (%s)]` | %d |" % (k, sub, v))
        A("")
    return "\n".join(L) + "\n"


def to_json(c):
    p = {k: c[k] for k in ("cards", "blocks", "senses", "blocks_without_header")}
    for key in ("diasystem", "domain", "bracket", "bracket_qualifier"):
        p[key] = dict(c[key])
    for key in ("matrix", "bracket_pairs", "diasystem_x_bracket"):
        p[key] = {"%s\t%s" % k: v for k, v in c[key].items()}
    for src, dst in (("lem_dia", "lemmas_by_diasystem"),
                     ("lem_dom", "lemmas_by_domain"),
                     ("lem_bracket", "lemmas_by_bracket")):
        p[dst] = {k: len(v) for k, v in c[src].items()}
    return p


_FIXTURE = {
    "key1": "Adika", "iast": "ādika",
    "nws": ("ādika Ved , unsp > [ifc (Bhvr)] ādi . ityādi : so beginnend. "
            "ṚV(Sā) I 165, 11 . Windisch 1883 : 106 > Śā , Med > [ifc] beginning "
            "with. Hoernle 1908 : 249 > Buddh , unsp > Adj mfn first, initial. "
            "BHSD : 93 > Reg , unsp > Adj mfn first (?). Ensink 1964 : 24 >"),
}


def _selftest():
    ok = True

    def check(cond, label):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + label)
        ok = ok and bool(cond)

    acc = new_acc()
    census_text(_FIXTURE, acc)
    check(acc["senses"] == 4 and acc["blocks"] == 8,
          "the ādika card = 4 senses across 8 raw blocks (header + body each)")
    check(sorted(acc["diasystem"]) == ["Buddh", "Reg", "Ved", "Śā"],
          "all four diasystems parsed: Ved / Śā / Buddh / Reg")
    check(acc["domain"]["unsp"] == 3 and acc["domain"]["Med"] == 1,
          "domains counted: unsp ×3, Med ×1")
    check(acc["matrix"][("Śā", "Med")] == 1, "the matrix records Śā × Med")
    check(acc["bracket"]["ifc"] == 2, "[ifc] counted in both blocks that carry it")
    check(acc["bracket_pairs"][("ifc", "Bhvr")] == 1, "[ifc (Bhvr)] pairs ifc with Bhvr")
    check("ādika" in acc["lem_bracket"]["Bhvr"], "the qualifier indexes its lemma too")
    check(acc["diasystem_x_bracket"][("Ved", "ifc")] == 1,
          "bracket tags attach to the diasystem of their own block")
    # a gloss comma must not be read as a header
    acc2 = new_acc()
    census_text({"iast": "x", "nws": "x Ved , unsp > Adj mfn first, initial. BHSD : 93 >"}, acc2)
    check(acc2["diasystem"]["Adj"] == 0, "a comma inside a gloss is not a header")
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=DEFAULT_DIR)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--md", dest="md_out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()

    c = census(args.dir, args.limit)
    if args.md_out:
        io.open(args.md_out, "w", encoding="utf-8", newline="\n").write(to_markdown(c))
        print("wrote %s" % args.md_out)
    if args.json_out:
        io.open(args.json_out, "w", encoding="utf-8", newline="\n").write(
            json.dumps(to_json(c), ensure_ascii=False, indent=1))
        print("wrote %s" % args.json_out)
    if not (args.md_out or args.json_out):
        sys.stdout.write(to_markdown(c))
    return 0


if __name__ == "__main__":
    sys.exit(main())
