#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""reglue_delta.py — *in what way* is a supplement a restatement? (H3152 B2/B3).

MG review point 4, on the ``gā`` card::

    ≈ переформулировкаrestatePW · переформулирует
    — 1〉 приходить.

*«значение "приходить" и так было в PWG, в чем же тогда переформулировка именно?
Или это дополнение? Добавился новый источник NAIGH. 2,14 или новая глагольная
форма (\\*jagāyāt)?»*

The complaint is exact. ``restate`` is not a measurement — per
[`ADDENDA_TYPOLOGY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/ADDENDA_TYPOLOGY.md) §5
it is the **default**, assigned when no gender conflict was found. It carries
90.2 % of all supplements and says nothing.

This module answers MG's own question by computing what actually changed, and it
computes it between the **German** original of the PWG sense and the **German**
original of the supplement — the relation holds between the sources, not between
their Russian translations.

Four deltas, four signs
-----------------------
=========  ====  ==============================  ==========================
delta      sign  what it measures                 example from ``gā``
=========  ====  ==============================  ==========================
оттенок    ＋    the gloss shares no content      a genuinely new shade
                 word with the PWG sense
управление →     case government the PWG sense    ``+Acc.``, ``+Loc.``
                 did not state
форма      ʰ     a Sanskrit form the PWG sense    ``+*jagāyāt``
                 did not carry
источник   §     a work the PWG sense did not     ``+NAIGH. 2,14``
                 cite
=========  ====  ==============================  ==========================

A supplement with none of the four is a **pure abridgement**, ``≈`` — PW saying
the same thing more briefly, which is what ``restate`` meant to claim all along.
When several deltas fire the most contentful sign wins (``＋ → ʰ §``); the full
list travels in the tooltip, so nothing is lost by showing one sign.

The refusal that shapes the design
----------------------------------
Word-overlap as a *similarity* score was already measured and **does not
separate the classes**: median Jaccard 0.000 on both sides, because the median
PWG sense body is three content words and 16 % have none at all. The measurement
is kept as a reproducible negative result in
[`reglue_overlap.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/reglue_overlap.py).
This module therefore counts **set deltas** — did a source/form/case appear that
was not there before — which is a question about presence, not about degree, and
survives a three-word body.

Where the body is too thin even for that, the answer is ``unresolvable``, not a
guess: with an empty PWG sense every delta is trivially "everything is new", and
saying ``＋`` there would be the same empty default as ``restate``, wearing a new
sign. Those cases get ``≈`` and are counted separately in the report.

Run::

    python src/reglue_delta.py --pilot        # the distribution over the 15-root pilot
    python src/reglue_delta.py --selftest
"""
import sys, os, io, json, re, argparse, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from reglue_overlap import tokens, citations, strip_markup, MIN_TERMS  # noqa: E402

#: the five signs, most contentful first — this order IS the precedence
NUANCE = "＋"
GOVERNMENT = "→"
FORM = "ʰ"
SOURCE = "§"
ABRIDGE = "≈"
PRECEDENCE = (NUANCE, GOVERNMENT, FORM, SOURCE, ABRIDGE)

#: what each sign means, once, at the top of a card (decision 9)
LEGEND = [
    (NUANCE, "новый оттенок значения"),
    (GOVERNMENT, "новое управление (падеж)"),
    (FORM, "новая форма"),
    (SOURCE, "новый источник"),
    (ABRIDGE, "то же самое короче"),
]

#: delta name -> sign, for the tooltip
DELTA_SIGN = {"оттенок": NUANCE, "управление": GOVERNMENT,
              "форма": FORM, "источник": SOURCE}

_SANSKRIT = re.compile(r"\{#(.*?)#\}", re.S)
_AB = re.compile(r"<ab>(.*?)</ab>", re.S)

#: Register / domain / provenance labels the MW-derived NWS material carries
#: inside the gloss (``[Ved]``, ``Gen, unsp``, ``[NWS: MW]``). They are metadata
#: about the gloss, not part of it, so a supplement that merely adds ``unsp``
#: must not be reported as a new shade of meaning. Measured on the pilot: without
#: this filter they appear in the ＋ delta of real cards next to genuine content
#: words, which makes the sign untrustworthy exactly where it is most visible.
_META_TOKENS = {
    "unsp", "ved", "mw", "nws", "pw", "pwg", "sch", "opt", "class", "caus",
    "desid", "intens", "pass", "med", "act", "impers", "denom",
}

#: Case abbreviations, in the spellings PWG's German actually prints. Government
#: is the delta MG named first ("Akk, Instr"), so it is read from the source's own
#: <ab> elements rather than guessed from prose.
_CASES = ("Acc", "Akk", "Gen", "Dat", "Abl", "Instr", "Ins", "Loc", "Lok",
          "Nom", "Voc")
_CASE_RE = re.compile(r"^(%s)\.?$" % "|".join(_CASES))


def forms(text):
    """Sanskrit forms cited in a body — the ``{#…#}`` spans, normalised.

    The reconstruction asterisk is kept: ``*jagāyāt`` and ``jagāyāt`` are not the
    same claim, and PW's asterisk is precisely the kind of addition MG asked to
    see named."""
    out = set()
    for m in _SANSKRIT.finditer(text or ""):
        f = re.sub(r"[\\^/~|]", "", m.group(1)).strip()
        f = re.sub(r"\s+", " ", f)
        if f:
            out.add(f)
    return out


def government(text):
    """Case abbreviations stated in the body's own ``<ab>`` elements."""
    out = set()
    for m in _AB.finditer(text or ""):
        token = m.group(1).strip().rstrip(".")
        hit = _CASE_RE.match(token + ".")
        if hit:
            out.add(hit.group(1))
    return out


def deltas(pwg_de, supp_de):
    """What the supplement's German has that the PWG sense's German did not.

    Returns a dict with the four delta sets, the chosen ``sign``, and
    ``resolvable`` — false when the PWG side is too thin for any delta to mean
    anything, in which case the sign is ``≈`` by convention and the case is
    reported rather than counted as a finding.
    """
    tp = tokens(pwg_de) - _META_TOKENS
    ts = tokens(supp_de) - _META_TOKENS
    src = citations(supp_de) - citations(pwg_de)
    frm = forms(supp_de) - forms(pwg_de)
    gov = government(supp_de) - government(pwg_de)
    # A new *shade* is claimed only when the two glosses share no content word at
    # all. Set difference alone would fire on every reworded synonym and put the
    # whole pilot under one sign — the degenerate outcome this classifier exists
    # to avoid.
    #
    # The length floor applies to the **PWG side only**. That is where thinness
    # destroys the comparison: against a one-word sense body, "shares nothing" is
    # nearly guaranteed and means nothing. The supplement side needs no floor —
    # PW is abridging by nature, and requiring three content words there silently
    # demoted the very case MG asked about (``gā`` 3: PWG «обходить … уклоняться»
    # vs PW «verfolgen, nachgehen» — two words, no overlap, plainly a different
    # meaning) to ``≈`` «то же самое короче», which is the opposite of true.
    comparable = len(tp) >= MIN_TERMS and len(ts) >= 1
    nuance = set()
    if comparable and not (tp & ts):
        nuance = ts - tp
    resolvable = bool(tp) or bool(citations(pwg_de)) or bool(forms(pwg_de))
    found = {"оттенок": nuance, "управление": gov, "форма": frm, "источник": src}
    sign = ABRIDGE
    if resolvable:
        for name in ("оттенок", "управление", "форма", "источник"):
            if found[name]:
                sign = DELTA_SIGN[name]
                break
    return {"sign": sign, "deltas": {k: sorted(v)[:8] for k, v in found.items() if v},
            "resolvable": resolvable, "comparable": comparable}


def tooltip(result):
    """The full delta list, for the hover — one sign on screen, everything here."""
    if not result["resolvable"]:
        return ("тело смысла PWG пусто — различить дельты нельзя, "
                "случай помечен как неразрешимый")
    if not result["deltas"]:
        return "PW говорит то же самое короче: ни нового источника, ни формы, ни управления"
    return "; ".join("%s %s: +%s" % (DELTA_SIGN[k], k, ", ".join(v))
                     for k, v in result["deltas"].items())


# ------------------------------------------------------------------ pilot pass
def pilot_distribution(store_path=None, roots=None):
    """Sign distribution over the reglue pilot — the B2 discrimination gate.

    Pairs a supplement with the PWG sense it was placed at, exactly as
    ``build_reglue`` does, and classifies the German originals.
    """
    from store_path import canonical_store, main_worktree_root
    import build_reglue as br

    # Both inputs are gitignored, local-only artefacts that live in the MAIN
    # checkout, not in a linked worktree — the H255 loss this repo already learned
    # about. `build_reglue.REL` resolves relative to its own file, which is right
    # in the main tree and wrong everywhere else, so the sibling is resolved the
    # same way `store_path` resolves the store.
    main = main_worktree_root(HERE)
    rel_path = (os.path.join(main, "RussianTranslation", "src",
                             "pwg_ru_relationships.jsonl") if main else br.REL)

    store = collections.defaultdict(list)
    pair_seen = collections.Counter()
    with io.open(store_path or canonical_store(HERE), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                d = json.loads(line)
                # H3300: same exact-join discipline as build_reglue.load() —
                # occurrence ordinal in file order on both sides of the join.
                pair = (d["subcard"], str(d.get("sense_tag")))
                d["_pair_ordinal"] = pair_seen[pair]
                pair_seen[pair] += 1
                store[d["key1"]].append(d)
    rel = br.RelSidecar(rel_path)

    from edition_rel import normalize_sense_tag, pwg_correction_marker
    signs = collections.Counter()
    unresolvable = 0
    total = 0
    examples = collections.defaultdict(list)
    for key1 in (roots or br.PILOT):
        recs = store.get(key1) or []
        # PWG skeleton: normalised sense tag -> German body
        skeleton = {}
        for d in recs:
            if d.get("layer") == "pwg" and not pwg_correction_marker(d.get("sense_tag")):
                skeleton[normalize_sense_tag(str(d.get("sense_tag")))] = d.get("de", "")
        for d in recs:
            layer = d.get("layer")
            if layer == "pwg" and not pwg_correction_marker(d.get("sense_tag")):
                continue
            r = rel.get(d["subcard"], str(d.get("sense_tag")),
                        d.get("_pair_ordinal"))
            if not r:
                continue
            # Pair on `target_sense`, NOT on the sidecar's `placement` verdict.
            # `placement` is an H2879 field that the committed relationships file
            # does not carry at all, so gating on it classifies exactly zero
            # supplements — a silent empty run that reads as "the gate passed".
            # What this classifier needs is only "which PWG sense does this
            # supplement restate", and `target_sense` is that, independently of
            # whether the renderer decided to place the row there.
            tgt = normalize_sense_tag(r.get("insertion_point", {}).get("target_sense"))
            if tgt not in skeleton:
                continue
            res = deltas(skeleton[tgt], d.get("de", ""))
            total += 1
            signs[res["sign"]] += 1
            if not res["resolvable"]:
                unresolvable += 1
            if len(examples[res["sign"]]) < 3:
                examples[res["sign"]].append((key1, tgt, tooltip(res)))
    if not total:
        # A zero-row classification is a broken join, not a passing gate. Say so
        # loudly rather than printing a table of zeroes that reads like a result.
        raise RuntimeError(
            "classified 0 supplements over %d pilot roots — the store/relationships "
            "join produced no pairs. Check that %s exists and that its "
            "insertion_point.target_sense values match the PWG skeleton's "
            "normalised sense tags." % (len(roots or br.PILOT), rel_path))
    return {"total": total, "signs": dict(signs), "unresolvable": unresolvable,
            "examples": {k: v for k, v in examples.items()}}


def render_pilot(d):
    lines = ["supplements classified: %d" % d["total"], ""]
    lines.append("%-4s %-30s %7s %7s" % ("знак", "значение", "n", "доля"))
    lines.append("-" * 52)
    for sign, label in LEGEND:
        n = d["signs"].get(sign, 0)
        lines.append("%-4s %-30s %7d %6.1f%%"
                     % (sign, label, n, 100.0 * n / max(d["total"], 1)))
    top = max(d["signs"].values()) if d["signs"] else 0
    share = 100.0 * top / max(d["total"], 1)
    lines.append("-" * 52)
    lines.append("крупнейший знак: %.1f%% (гейт B2: не более 70 %%) — %s"
                 % (share, "ПРОЙДЕН" if share <= 70 else "СТОП-УСЛОВИЕ 4"))
    lines.append("неразрешимых (пустое тело смысла PWG): %d (%.1f%%)"
                 % (d["unresolvable"], 100.0 * d["unresolvable"] / max(d["total"], 1)))
    lines.append("")
    for sign, label in LEGEND:
        for key1, tgt, tip in d["examples"].get(sign, [])[:2]:
            lines.append("  %s  %-6s значение %-4s  %s" % (sign, key1, tgt, tip[:90]))
    return "\n".join(lines)


def selftest():
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    # ---- MG's own case: PW sense 1 of gā adds a source and a form, nothing else
    pwg = "<div n=\"1\">— 1) {%kommen%}: <ls>ṚV. 7,84,1.</ls>"
    supp = ("<hom>1.</hom> √{#gA#}, {#ji/gAti#}, *{#jagAti#} (*{#jagAyA/t#}), "
            "*{#gA/ti#} (<ls>NAIGH. 2,14</ls>) und *{#gAte#} — 1〉 {%kommen%}.")
    r = deltas(pwg, supp)
    check("NAIGH" in str(r["deltas"].get("источник")),
          "MG's question 'добавился новый источник NAIGH. 2,14?' is answered: %s"
          % r["deltas"].get("источник"))
    check(any("jag" in f for f in r["deltas"].get("форма", [])),
          "…and 'новая глагольная форма (*jagāyāt)?' too: %s"
          % r["deltas"].get("форма"))
    check(r["sign"] == FORM,
          "the most contentful delta wins: form beats source (%s)" % r["sign"])

    # ---- a pure abridgement gets ≈ and says so
    same = "— 1) {%kommen, gehen, wandern%}: <ls>ṚV. 7,84,1.</ls>"
    shorter = "— 1〉 {%kommen, gehen%} <ls>ṚV. 7,84,1.</ls>"
    r2 = deltas(same, shorter)
    check(r2["sign"] == ABRIDGE,
          "nothing new -> ≈ pure abridgement (%s)" % r2["sign"])
    check("короче" in tooltip(r2), "…and the tooltip says exactly that")

    # ---- government, the delta MG named first
    r3 = deltas("— 1) {%kommen%}", "— 1〉 {%kommen%} mit <ab>Acc.</ab> oder <ab>Loc.</ab>")
    check(r3["sign"] == GOVERNMENT and set(r3["deltas"]["управление"]) == {"Acc", "Loc"},
          "new case government is detected and outranks source/form: %s" % r3)

    # ---- precedence, with everything firing at once
    r4 = deltas("— 1) {%kommen, gehen, wandern%}",
                "— 1〉 {%singen, preisen, rufen%} mit <ab>Acc.</ab> "
                "{#gAyati#} <ls>NAIGH. 2,14</ls>")
    check(r4["sign"] == NUANCE,
          "a compound delta shows the most contentful sign, ＋ (%s)" % r4["sign"])
    check(len(r4["deltas"]) == 4, "…and all four deltas travel in the tooltip")
    check(tooltip(r4).count(";") == 3, "the tooltip lists every one of them")

    # ---- the refusal: an empty PWG body cannot be classified
    r5 = deltas("", "— 1〉 {%kommen%} <ls>NAIGH. 2,14</ls>")
    check(not r5["resolvable"] and r5["sign"] == ABRIDGE,
          "an empty PWG sense body is unresolvable, not a discovery (%s)" % r5["sign"])
    check("неразрешим" in tooltip(r5), "…and the tooltip says why, rather than claiming ＋")

    # ---- a reworded synonym must NOT be promoted to a new shade
    r6 = deltas("— 1) {%kommen, gehen, wandern%}", "— 1〉 {%kommen und wandern%}")
    check(r6["sign"] == ABRIDGE,
          "sharing content words means the shade is NOT new (%s)" % r6["sign"])

    # ---- a thin PWG SENSE body makes the comparison meaningless
    r7 = deltas("— 1) {%kommen%}", "— 1〉 {%singen%}")
    check(not r7["comparable"] and r7["sign"] == ABRIDGE,
          "against a one-word PWG sense, 'shares nothing' means nothing (%s)"
          % r7["sign"])

    # ---- …but a SHORT SUPPLEMENT against a substantive sense still counts.
    # This is MG's own gā sense 3: PWG «обходить … уклоняться» vs PW two words
    # that mean the opposite. Calling that «то же самое короче» would be false.
    r9 = deltas("— 3) {%umgehen%} so <ab>v. a.</ab> {%vermeiden, nicht beachten, "
                "vorbeigehen lassen%}: <ls>ṚV. 2,33,14.</ls>",
                "— 3〉 {%verfolgen, nachgehen%} <ls>ṚV. 4,3,13. 10,18,4</ls>.")
    check(r9["sign"] == NUANCE,
          "a two-word supplement sharing nothing with a substantive sense is ＋ (%s)"
          % r9["sign"])

    # ---- register/domain labels are metadata, not a new shade of meaning
    r8 = deltas("— 1) {%kommen, gehen, wandern%}",
                "— 1〉 [Ved] {%kommen, gehen, wandern%} , unsp")
    check(r8["sign"] == ABRIDGE,
          "adding [Ved]/unsp is metadata, not a new shade (%s)" % r8["sign"])

    check([s for s, _ in LEGEND] == list(PRECEDENCE),
          "the legend is in precedence order, so the card teaches the ranking")

    print("reglue_delta selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pilot", action="store_true", help="distribution over the pilot")
    ap.add_argument("--json", help="write the distribution here")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.pilot or a.json:
        d = pilot_distribution()
        print(render_pilot(d))
        if a.json:
            with io.open(a.json, "w", encoding="utf-8") as fh:
                json.dump(d, fh, ensure_ascii=False, indent=1)
            print("\nwrote %s" % a.json)
        top = max(d["signs"].values()) if d["signs"] else 0
        return 0 if 100.0 * top / max(d["total"], 1) <= 70 else 4
    return selftest()


if __name__ == "__main__":
    sys.exit(main())
