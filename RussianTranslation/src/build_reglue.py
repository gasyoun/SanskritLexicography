#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_reglue.py — Deliverable 3 of H180 (REGLUE_SPEC.md), Arm A.

Content-aware re-glue: interleave the ALREADY-TRANSLATED sub-cards so each
supplement (SCH / NWS / PW / PWKVN) sits at its relevant PWG sense — proving the
re-glue is FREE (zero re-translation). PWG stays the skeleton; everything hangs
off it (MG). This is the canonical after-translation derived presentation; the
layered store remains canonical.

Consumes ONLY:
  * src/pwg_ru_translated.jsonl        (the `ru` bodies — copied verbatim)
  * src/pwg_ru_relationships.jsonl     (insertion points from build_relationships.py)
It NEVER calls the translate workflow. Every `ru` emitted is asserted
byte-identical to the store (success criterion (a) — proof of zero re-translation).

Outputs per pilot headword:
  * pwg_ru/reglue/<key1>.json          (structured, REGLUE_SPEC §4 schema)
  * pwg_ru/reglue/<key1>.md            (rendered print-oriented card, RU)
  * pwg_ru/reglue/<key1>.de.md         (the same card in German — H3152 B5)
  * pwg_ru/reglue/PILOT_SUMMARY.tsv    (per-headword success-criteria table)
  * pwg_ru/reglue/GLOSS_FLAGS.tsv      (disputed glosses, flagged not fixed — B6)

What H3152 changed here (MG's reglue2 review)
---------------------------------------------
**Point 4 — one sign, not four labels.** ``[PW·restate]`` used to print the class
label, the ASCII subtype, the layer badge and the operation, all four saying the
same nothing: ``restate`` is
[ADDENDA_TYPOLOGY](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/ADDENDA_TYPOLOGY.md) §5's
*default*, carried by 90.2 % of supplements. The card now prints **one** sign
that says in what way the supplement differs — computed from the German by
[`reglue_delta`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/reglue_delta.py) —
plus a legend once at the top.

**Point 5a — a binding label a reader can parse.** ``значение PWG 2`` read as
"PWG's second meaning" *and* as "the meaning called PWG 2". It is now
«привязано к смыслу PWG 2», and an unplaced supplement says «новый смысл, в PWG
соответствия нет» rather than implying a target it does not have.

**Point 3 — the German glue exists.** ``<key1>.de.md`` sits beside ``<key1>.md``,
built from the same skeleton in the same pass, with a parity gate: the two must
agree on their insertion points exactly, because an insertion point is a property
of the structure and not of the language.

**Points 1/5/6a — citations are live.** The card used to copy store bodies as
plain text, so it had no links at all. Bodies now go through the shared renderer
[`build_article_site._render`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py),
the same one the article site and the vote sheet use, so the multi-address split
and the Mahābhārata coordinate triple reach this surface too.

The zero-re-translation invariant is untouched: the **JSON** still holds the store
string byte for byte and is still asserted against the store. Linking happens only
in the rendered ``.md``, which is presentation.

Run: python src/build_reglue.py
     python src/build_reglue.py --selftest
"""
import sys, os, io, json, re, argparse, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "pilot"))

from store_path import canonical_store, main_worktree_root      # noqa: E402

#: Both inputs are gitignored, local-only artefacts belonging to the MAIN
#: checkout — resolving them relative to this file loses them inside a linked
#: worktree (the H255 class of loss this repo already paid for once).
STORE = canonical_store(os.path.join(HERE, "pwg_ru_translated.jsonl"))
_MAIN = main_worktree_root(HERE)
REL = (os.path.join(_MAIN, "RussianTranslation", "src",
                    "pwg_ru_relationships.jsonl") if _MAIN
       else os.path.join(HERE, "pwg_ru_relationships.jsonl"))
OUTDIR = os.path.join(ROOT, "pwg_ru", "reglue")

# Pilot set (REGLUE_SPEC §5) — 5/4/3-layer roots.
PILOT = ["gA", "Cid", "Sam", "jIv", "rakz", "vraj", "yat",          # 5-layer
         "DA", "Ap", "Bid", "Buj", "banD", "Sru",                    # 4-layer
         "viS", "siD"]                                               # 3-layer

LAYER_BADGE = {"pw": "PW", "sch": "SCH", "pwkvn": "PWKVN", "nws": "NWS",
               # H2880: a correction carried on the PWG layer itself
               "pwg": "PWG"}

# H2879: one canonical normaliser, shared with the classifier that wrote the
# sidecar. A local re-implementation here would drift and silently un-place rows.
# H2880: the correction predicate is imported for the same reason — the skeleton
# and the sidecar must agree on which rows are senses.
from edition_rel import normalize_sense_tag, pwg_correction_marker  # noqa: E402
import reglue_delta as rd                                          # noqa: E402
import build_article_site as bas                                   # noqa: E402

#: `placement_reason` in the words a reader sees (H2879 S6).
PLACEMENT_REASON_RU = {
    "no_target_marker": "цель не указана",
    "out_of_range": "номер выше диапазона PWG",
    "not_found": "смысл не найден",
}

#: H3152 B4 (MG review 5a). `значение PWG 2` was ambiguous between "PWG's second
#: meaning" and "the meaning named PWG 2"; these say which relation holds.
BOUND_LABEL = "привязано к смыслу PWG %s"
UNBOUND_LABEL = "новый смысл, в PWG соответствия нет"

#: Per-language card furniture. The insertion points are identical by
#: construction (they are structural); only the wording differs.
LANG_TITLE = {"ru": "Re-glue — %s", "de": "Re-glue (deutsch) — %s"}
LANG_HOM = {"ru": "омоним %s", "de": "Homonym %s"}
LANG_LEGEND_HEAD = {"ru": "Знаки", "de": "Zeichen"}
LANG_LEGEND = {
    "ru": dict(rd.LEGEND),
    "de": {rd.NUANCE: "neue Bedeutungsnuance", rd.GOVERNMENT: "neue Rektion (Kasus)",
           rd.FORM: "neue Form", rd.SOURCE: "neue Quelle",
           rd.ABRIDGE: "dasselbe, nur kürzer"},
}
LANG_BOUND = {"ru": BOUND_LABEL, "de": "an PWG-Bedeutung %s gebunden"}
LANG_UNBOUND = {"ru": UNBOUND_LABEL, "de": "neue Bedeutung, in PWG ohne Entsprechung"}


def lead_int(st):
    m = re.match(r"\s*(\d+)", str(st))
    return m.group(1) if m else None


def homonym_of(subcard):
    m = re.search(r"~~(h\d+)", subcard or "")
    return m.group(1) if m else "h0"


def load():
    store = collections.defaultdict(list)          # key1 -> [record]
    with io.open(STORE, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                d = json.loads(line)
                store[d["key1"]].append(d)
    rel = {}                                        # (subcard, sense_tag) -> relationship
    with io.open(REL, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                r = json.loads(line)
                rel[(r["subcard"], r["sense_tag"])] = r["relationship"]
    return store, rel


def reglue_one(key1, records, rel):
    """Return (json_obj, stats). Never re-translates: `ru` copied verbatim."""
    byte_ok = True
    supplements_placed = 0
    supplements_new = 0
    cancels = 0

    # homonym -> ordered PWG skeleton senses
    homs = collections.OrderedDict()

    def hom_slot(h):
        if h not in homs:
            homs[h] = {"h": h, "senses": collections.OrderedDict(), "new_senses": []}
        return homs[h]

    # 1. skeleton — PWG rows, numeric senses first.
    # H2880: a PWG row carrying a correction marker (`Nachtrag`, `addendum`,
    # `1 (PW)`) is an edit *to* a sense, not a sense. It used to be rendered
    # here as an ordinary skeleton sense — `**Nachtrag)** …` — which is the
    # wave-1 axis defect one layer down. It is attached as a supplement in
    # step 2 instead.
    pwg_rows = [d for d in records
                if d.get("layer") == "pwg"
                and not pwg_correction_marker(d.get("sense_tag"))]

    def sort_key(d):
        si = lead_int(d.get("sense_tag"))
        return (0, int(si)) if si else (1, str(d.get("sense_tag")))

    for d in sorted(pwg_rows, key=sort_key):
        h = hom_slot(homonym_of(d["subcard"]))
        st = str(d.get("sense_tag"))
        # Slotted under the H2879-normalised tag, the same key the sidecar's
        # placement lookup used — otherwise a '1)' skeleton sense could never
        # receive a supplement that the sidecar already reports as placed.
        h["senses"][normalize_sense_tag(st)] = {
            "sense": st, "pwg_ru": d.get("ru", ""),
            # H3152 B5: the German original travels beside the Russian, from the
            # same row, so the two glue renderings cannot come from different
            # skeletons. It is also what the delta classifier compares.
            "pwg_de": d.get("de", ""), "supplements": []}

    # 2/3/4. attach supplements at their insertion point. Since H2880 this
    # includes PWG-internal corrections, which reach the sidecar exactly when
    # they are corrections — so "has a sidecar row" is the whole test.
    for d in records:
        layer = d.get("layer")
        if layer == "pwg" and not pwg_correction_marker(d.get("sense_tag")):
            continue
        st = str(d.get("sense_tag"))
        r = rel.get((d["subcard"], st))
        if not r:
            continue
        ip = r["insertion_point"]
        h = hom_slot(ip.get("homonym", homonym_of(d["subcard"])))
        supp = {
            "layer": layer, "badge": LAYER_BADGE.get(layer, layer.upper()),
            "subtype": r["subtype"], "op": r["op"], "ru": d.get("ru", ""),
            "de": d.get("de", ""),
            "sense_tag": st, "confidence": r.get("confidence", "llm"),
            "placement_reason": r.get("placement_reason"),
        }
        # H3152 B2/B3 (MG review 4): in WHAT WAY does this supplement differ from
        # the PWG sense it restates? Computed between the two GERMAN originals —
        # the relation holds between the sources, not between their translations.
        tgt_norm = normalize_sense_tag(ip.get("target_sense"))
        pwg_de = (h["senses"].get(tgt_norm) or {}).get("pwg_de", "")
        delta = rd.deltas(pwg_de, supp["de"])
        supp["sign"] = delta["sign"]
        supp["delta"] = delta["deltas"]
        supp["delta_tip"] = rd.tooltip(delta)
        supp["delta_resolvable"] = delta["resolvable"]
        if r["subtype"] == "foreign_fragment":
            supp["lang"] = r.get("source_lang", "??")
        if r["op"] in ("correct", "delete"):
            supp["cancels"] = True
            cancels += 1

        # H2879: read the sidecar's placement verdict; do not re-decide it here.
        tgt = normalize_sense_tag(ip.get("target_sense"))
        if r.get("placement") and tgt in h["senses"]:
            h["senses"][tgt]["supplements"].append(supp)
            supplements_placed += 1
        else:
            supp["added_by"] = layer
            h["new_senses"].append(supp)
            supplements_new += 1

    obj = {
        "key1": key1,
        "homonyms": [
            {"h": hv["h"],
             "senses": [
                 {"sense": s["sense"], "pwg_ru": s["pwg_ru"],
                  "pwg_de": s["pwg_de"], "supplements": s["supplements"]}
                 for s in hv["senses"].values()],
             "new_senses": hv["new_senses"]}
            for hv in homs.values()
        ],
    }
    stats = {
        "key1": key1, "homonyms": len(homs),
        "pwg_senses": sum(len(hv["senses"]) for hv in homs.values()),
        "supplements_placed": supplements_placed,
        "supplements_new": supplements_new,
        "cancels": cancels, "byte_ok": byte_ok,
    }
    return obj, stats


def _body(text, lang):
    """One store body, rendered for reading: citations become links.

    Goes through the SHARED renderer, not a local copy — the article site, the
    vote sheet and this card must not be able to disagree about what a citation
    resolves to. The store string itself is untouched; only this rendering links.
    """
    try:
        return bas._render(text or "", "md", lang)
    except Exception:
        return text or ""


def legend_md(lang):
    """The sign key, once at the top of the card (decision 9 + 13).

    MG's complaint was that ``≈ переформулировкаrestatePW · переформулирует`` says
    one thing four times on every single line. One sign per line plus one legend
    per card carries strictly more information in far less space — the sign now
    says *in what way*, which the four labels never did.
    """
    names = LANG_LEGEND[lang]
    parts = " · ".join("**%s** %s" % (s, names[s]) for s in rd.PRECEDENCE)
    return "%s: %s" % (LANG_LEGEND_HEAD[lang], parts)


def _supp_line(sup, lang):
    """One supplement line: sign, badge, then the body. No four-fold chip."""
    field = "ru" if lang == "ru" else "de"
    sign = sup.get("sign", rd.ABRIDGE)
    strike = " ~~(cancels PWG)~~" if sup.get("cancels") else ""
    frag = f" ‹{sup['lang']}›" if sup.get("lang") else ""
    # H2880: a PWG-internal correction carries its own tag, which tells the
    # reader which grammatical branch the correction belongs to. That is context,
    # not a placement claim, and must survive the chip collapse.
    src = (f" ‹{sup['sense_tag']}›"
           if sup.get("subtype") == "pwg_internal_correction"
           and sup.get("sense_tag") else "")
    return "  — %s %s%s%s%s %s" % (sign, sup["badge"], src, frag, strike,
                                   _body(sup.get(field, ""), lang))


def render_md(obj, lang="ru"):
    """The printed card in one language. `lang='de'` is B5's German glue.

    Both languages come from the same ``obj`` and the same loop, so the insertion
    points cannot drift — which is exactly what :func:`insertion_points` then
    verifies rather than assumes.
    """
    field = "ru" if lang == "ru" else "de"
    lines = [LANG_TITLE[lang] % obj["key1"], "", legend_md(lang), ""]
    for hom in obj["homonyms"]:
        lines.append("## " + LANG_HOM[lang] % hom["h"])
        lines.append("")
        for s in hom["senses"]:
            lines.append("**%s)** %s" % (s["sense"], _body(s.get("pwg_" + field, ""),
                                                           lang)))
            for sup in s["supplements"]:
                lines.append(_supp_line(sup, lang))
            lines.append("")
        for sup in hom["new_senses"]:
            # A1: an unplaced supplement must not be rendered as a claim about a
            # PWG sense. Say *why* it is unplaced instead of implying a target.
            why = PLACEMENT_REASON_RU.get(sup.get("placement_reason"))
            head = (LANG_UNBOUND[lang] + (" — %s" % why if why else ""))
            lines.append("**+)** [%s] %s" % (head, _body(sup.get(field, ""), lang)))
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


_MD_HOM = re.compile(r"^## .*?(\S+)\s*$")
_MD_SENSE = re.compile(r"^\*\*(.+?)\)\*\* ")
_MD_SUPP = re.compile(r"^  — (\S+) (\S+)")
_MD_NEW = re.compile(r"^\*\*\+\)\*\* \[")


def insertion_points(md):
    """Every place a supplement attaches, read back out of a RENDERED card (B5).

    Deliberately parsed from the markdown rather than computed from the shared
    ``obj``: both languages come from one object, so an object-level comparison
    would be true by construction and would prove nothing. What can genuinely
    differ is the **rendering** — a supplement whose German field is empty, a body
    the renderer drops — and only the emitted text shows that.

    An insertion point is a property of the structure, not of the language, so the
    two lists must be identical.
    """
    out, hom, sense, idx = [], None, None, 0
    for line in (md or "").splitlines():
        m = _MD_HOM.match(line)
        if m:
            hom, sense, idx = m.group(1), None, 0
            continue
        # `**+)**` must be tested BEFORE `**N)**`: the sense pattern matches it
        # too (with group 1 == '+'), which would swallow every unbound supplement
        # and make the parity gate compare two lists that are both missing them.
        if _MD_NEW.match(line):
            sense, idx = "*new", idx + 1
            out.append((hom, "*new", idx))
            continue
        m = _MD_SENSE.match(line)
        if m:
            sense, idx = normalize_sense_tag(m.group(1)), 0
            continue
        m = _MD_SUPP.match(line)
        if m:
            idx += 1
            out.append((hom, sense, idx))
    return out


#: A gloss chain: the meaning items inside a `{%…%}` span, comma-separated.
_GLOSS = re.compile(r"\{%(.*?)%\}", re.S)


def gloss_items(text):
    """The distinct meaning items a body offers, in order."""
    out = []
    for m in _GLOSS.finditer(text or ""):
        for part in m.group(1).split(","):
            part = part.strip()
            if part:
                out.append(part)
    return out


def gloss_flags(obj):
    """B6 (MG review 6b) — glosses wider than the sense they claim to restate.

    MG, on ``gā`` sense 3: PW gives «преследовать, следовать за» and cites
    ṚV 4,3,13, which supports *преследовать*; so where does *следовать за* come
    from — the Ṛgveda, or German lexicographic latitude?

    What is mechanically decidable is the shape of that question: a supplement
    **bound to** a PWG sense offers more meaning items than that sense does, so
    the surplus rests on the cited locus alone. Those surplus items are named, in
    Russian, so a reader sees «следовать за» itself rather than a row id.

    What is **not** decidable here is MG's actual question — whether ṚV 4,3,13
    supports the surplus. That needs the Ṛgveda text and its Russian translation
    of record; the corpus that would answer it (SamudraManthanam ``corpus.db``) is
    empty on this machine. So this is a flag with its evidence, never a verdict,
    and the text is not touched (PLAN fence 3).
    """
    flags = []
    for hom in obj["homonyms"]:
        for s in hom["senses"]:
            base = gloss_items(s.get("pwg_ru", ""))
            for sup in s["supplements"]:
                extra = [g for g in gloss_items(sup.get("ru", "")) if g not in base]
                if len(gloss_items(sup.get("ru", ""))) > max(len(base), 1) and extra:
                    flags.append({
                        "key1": obj["key1"], "homonym": hom["h"],
                        "sense": s["sense"], "layer": sup["layer"],
                        "surplus": extra,
                        "cited": _cited_addresses(sup.get("ru", "")),
                        "reason": "глосса дополнения шире смысла PWG, к которому "
                                  "оно привязано; излишек опирается только на "
                                  "процитированное место",
                    })
    return flags


_LS_RE = re.compile(r"<ls\b[^>]*>(.*?)</ls>", re.S)


def _cited_addresses(text):
    return [re.sub(r"\s+", " ", m.group(1)).strip()
            for m in _LS_RE.finditer(text or "")]


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    store, rel = load()

    summary = []
    all_flags = []
    signs = collections.Counter()
    parity_fails = 0
    for key1 in PILOT:
        recs = store.get(key1)
        if not recs:
            print(f"  [skip] {key1}: not in translated store")
            summary.append((key1, "ABSENT", 0, 0, 0, 0, "-"))
            continue
        obj, stats = reglue_one(key1, recs, rel)

        # hard byte-identity check (success criterion a): every emitted ru body —
        # skeleton AND supplement — must appear verbatim in this headword's store.
        store_ru = {r.get("ru", "") for r in recs}
        bad = 0
        for hom in obj["homonyms"]:
            for s in hom["senses"]:
                if s["pwg_ru"] not in store_ru:
                    bad += 1
                for sup in s["supplements"]:
                    if sup["ru"] not in store_ru:
                        bad += 1
            for sup in hom["new_senses"]:
                if sup["ru"] not in store_ru:
                    bad += 1
        byte_ok = (bad == 0)

        with io.open(os.path.join(OUTDIR, key1 + ".json"), "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=1)
        ru_md = render_md(obj, "ru")
        de_md = render_md(obj, "de")
        # B5 parity gate: the two glue renderings must attach their supplements at
        # exactly the same places. A difference is a slipped glue, not a language
        # difference, so it fails the build for this headword rather than shipping
        # a German card that quietly says something structurally different.
        ru_ip, de_ip = insertion_points(ru_md), insertion_points(de_md)
        parity = ru_ip == de_ip
        if not parity:
            only_ru = [p for p in ru_ip if p not in de_ip]
            only_de = [p for p in de_ip if p not in ru_ip]
            print(f"  [PARITY FAIL] {key1}: ru-only={only_ru[:4]} de-only={only_de[:4]}")
        with io.open(os.path.join(OUTDIR, key1 + ".md"), "w", encoding="utf-8") as fh:
            fh.write(ru_md)
        with io.open(os.path.join(OUTDIR, key1 + ".de.md"), "w", encoding="utf-8") as fh:
            fh.write(de_md)
        all_flags.extend(gloss_flags(obj))
        signs.update(sup.get("sign", rd.ABRIDGE)
                     for hom in obj["homonyms"] for s in hom["senses"]
                     for sup in s["supplements"])

        if not parity:
            parity_fails += 1
        summary.append((key1, "OK" if (byte_ok and parity) else
                        ("BYTE_FAIL" if not byte_ok else "PARITY_FAIL"),
                        stats["homonyms"], stats["pwg_senses"],
                        stats["supplements_placed"], stats["supplements_new"],
                        stats["cancels"]))
        print(f"  {key1:6s} senses={stats['pwg_senses']:3d} "
              f"placed={stats['supplements_placed']:3d} "
              f"new={stats['supplements_new']:2d} cancels={stats['cancels']} "
              f"byte_ok={byte_ok}")

    with io.open(os.path.join(OUTDIR, "PILOT_SUMMARY.tsv"), "w", encoding="utf-8") as fh:
        fh.write("key1\tstatus\thomonyms\tpwg_senses\tsupp_placed\tsupp_new\tcancels\n")
        for row in summary:
            fh.write("\t".join(str(x) for x in row) + "\n")

    with io.open(os.path.join(OUTDIR, "GLOSS_FLAGS.tsv"), "w", encoding="utf-8") as fh:
        fh.write("key1\thomonym\tsense\tlayer\tsurplus_gloss\tcited\treason\n")
        for f in all_flags:
            fh.write("\t".join([
                f["key1"], f["homonym"], str(f["sense"]), f["layer"],
                " · ".join(f["surplus"]), " · ".join(f["cited"]) or "—",
                f["reason"]]) + "\n")

    built = sum(1 for r in summary if r[1] == "OK")
    print(f"\nreglue pilot: {built}/{len(PILOT)} headwords built (zero re-translation)")
    if parity_fails:
        print(f"  PARITY: {parity_fails} headword(s) failed the ru/de insertion-point gate")
    else:
        print("  parity: ru and de glue agree on every insertion point")
    total = sum(signs.values())
    if total:
        dist = " · ".join("%s %d (%.0f%%)" % (s, signs.get(s, 0),
                                              100.0 * signs.get(s, 0) / total)
                          for s in rd.PRECEDENCE)
        print(f"  signs over placed supplements: {dist}")
    print(f"  gloss flags (B6, flagged not fixed): {len(all_flags)}")
    print(f"wrote {OUTDIR}\\*.json, *.md, *.de.md, PILOT_SUMMARY.tsv, GLOSS_FLAGS.tsv")
    return 0 if parity_fails == 0 else 1


def selftest():
    """Fixture selftest for the H3152 rendering changes — no store, no network."""
    ok = [True]

    def check(cond, msg):
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok[0] = ok[0] and bool(cond)

    obj = {"key1": "gA", "homonyms": [{
        "h": "h0",
        "senses": [{
            "sense": "3", "pwg_ru": "— 3) {%обходить%}: <ls>ṚV. 2,33,14.</ls>",
            "pwg_de": "— 3) {%umgehen%}: <ls>ṚV. 2,33,14.</ls>",
            "supplements": [{
                "layer": "pw", "badge": "PW", "subtype": "restate", "op": "restate",
                "ru": "— 3〉 {%преследовать, следовать за%} <ls>ṚV. 4,3,13. 10,18,4</ls>.",
                "de": "— 3〉 {%verfolgen, nachgehen%} <ls>ṚV. 4,3,13. 10,18,4</ls>.",
                "sense_tag": "3", "sign": rd.NUANCE,
            }]}],
        "new_senses": [{
            "layer": "nws", "badge": "NWS", "subtype": "nws_at_sense",
            "ru": "идти.", "de": "gehen.", "sense_tag": "x",
            "placement_reason": "not_found", "sign": rd.ABRIDGE}]}]}

    ru = render_md(obj, "ru")
    de = render_md(obj, "de")

    # ---- review 4: one sign, and a legend once at the top
    check("[PW·restate]" not in ru, "the four-fold chip is gone")
    check(ru.count("Знаки:") == 1, "the legend appears exactly once, at the top")
    check("  — ＋ PW " in ru, "the supplement line is sign + badge: one mark, not four")
    for sign in rd.PRECEDENCE:
        check(sign in ru.split("\n")[2], "the legend explains %s" % sign)

    # ---- review 5a: the binding label says which relation holds
    check("значение PWG" not in ru, "the ambiguous «значение PWG N» wording is gone")
    check(UNBOUND_LABEL in ru,
          "an unbound supplement says «новый смысл, в PWG соответствия нет»")

    # ---- review 3: the German glue exists and is German
    check(de.startswith("Re-glue (deutsch) — gA"), "the German card is titled as such")
    check("verfolgen" in de and "преследовать" not in de,
          "the German card carries the German bodies")
    check("Zeichen:" in de, "…with its own legend")

    # ---- B5 parity: the two attach their supplements at the same places
    check(insertion_points(ru) == insertion_points(de),
          "ru and de agree on every insertion point: %r vs %r"
          % (insertion_points(ru), insertion_points(de)))
    check(len(insertion_points(ru)) == 2,
          "…and both points are seen (%r)" % (insertion_points(ru),))

    # ---- review 6a/1: citations are live on this surface at last
    check("](" in ru, "the printed card finally carries links")
    check(ru.count("rvlinks") >= 2,
          "the two-address citation is two links here too")

    # ---- review 6b: the disputed gloss is FLAGGED, and the text is untouched
    flags = gloss_flags(obj)
    check(len(flags) == 1 and "следовать за" in flags[0]["surplus"],
          "«следовать за» is flagged as gloss surplus: %r"
          % (flags[0]["surplus"] if flags else None))
    check("ṚV. 4,3,13. 10,18,4" in " ".join(flags[0]["cited"]),
          "…with the locus the surplus would have to rest on")
    check("следовать за" in ru,
          "…and the text itself is NOT edited — flagged, never fixed (fence 3)")

    print("build_reglue selftest:", "OK" if ok[0] else "FAIL")
    return 0 if ok[0] else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    _a = ap.parse_args()
    sys.exit(selftest() if _a.selftest else main())
