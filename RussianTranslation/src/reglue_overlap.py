#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""reglue_overlap.py — measure whether a supplement RESTATES its PWG sense (H2859).

Why this exists
---------------
The re-glue vote sheet asks a human "is the glue typology right?" and shows a
colour chip — ＋ added meaning / ≈ restatement / ✕ cancels — for each supplement.
**1,534 of the 1,785 chips (86 %) say ≈, and that chip is an unevidenced
default.** Per [ADDENDA_TYPOLOGY](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/ADDENDA_TYPOLOGY.md)
§5, `restate` is simply what a `pw` sub-card gets *when no gender conflict is
detected*; the sidecar's own `evidence` string says only
``"PW abridging restatement; sense_tag='4'"`` — the rule restated, not evidence
for it. Asking a human to ratify that is asking them to re-derive the homework
(the standard's F2 anti-pattern).

This module supplies the missing measurement. For each supplement it compares the
sub-card against **the PWG sense it is attached to** on three deterministic axes:

* ``gloss_overlap`` — Jaccard over content-word stems of the two glosses, on the
  **German**, which is the layer the relationship actually holds between (both
  sides' Russian is a translation, so RU overlap partly measures the translator's
  word choice rather than the sources' relationship).
* ``citation_overlap`` — of the ``<ls>`` sources the PWG sense cites, what share
  does the supplement re-cite? An abridging restatement typically keeps a subset;
  a genuine addition brings its own.
* ``length_ratio`` — supplement chars / PWG-sense chars. An abridgement is
  shorter almost by definition.

None of these decides the typology on its own; together they are evidence a human
can weigh, and — more usefully — they let the sheet **rank by disagreement**:
where the chip says ≈ but the two texts share nothing, or the chip says ＋ but
they are near-duplicates, that is where a human's time actually buys something.

Deliberately NOT a classifier. It never rewrites a chip; it attaches numbers to
one and flags where they point the other way.

Run: python src/reglue_overlap.py            (set PWG_RU_DATA_ROOT)
     python src/reglue_overlap.py --selftest
"""
import sys, os, io, json, re, math, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("PWG_RU_DATA_ROOT", os.path.dirname(HERE))
STORE = os.path.join(DATA, "src", "pwg_ru_translated.jsonl")
REL = os.path.join(DATA, "src", "pwg_ru_relationships.jsonl")
REPORTS = os.path.join(DATA, "reports")

LS_RE = re.compile(r"<ls\b[^>]*>(.*?)</ls>", re.S)
#: `{#…#}` is a SANSKRIT span — dropped, since a shared headword is not evidence
#: that two glosses mean the same thing.
SANSKRIT = re.compile(r"\{#.*?#\}", re.S)
#: `{%…%}` is the MEANING GLOSS — the delimiters go, the words stay. Stripping
#: this span too (the first cut did) deletes exactly the text being compared and
#: drives 95 % of pairs to a spurious 0.000.
GLOSS = re.compile(r"\{%(.*?)%\}", re.S)
TAG = re.compile(r"<[^>]+>")
PAGE = re.compile(r"⌊.*?⌋", re.S)

#: German function words — dropped before overlap so "und/der/die" cannot
#: manufacture similarity between two unrelated glosses.
STOP_DE = {
    "und", "oder", "der", "die", "das", "des", "dem", "den", "ein", "eine",
    "einer", "eines", "einem", "einen", "mit", "von", "vom", "zu", "zum", "zur",
    "in", "im", "auf", "an", "am", "als", "auch", "aus", "bei", "beim", "für",
    "ist", "sind", "war", "sich", "so", "wie", "nach", "nur", "man", "wird",
    "werden", "sein", "seine", "seinem", "seiner", "etwas", "jemand", "jemandes",
    "jemandem", "jemanden", "nicht", "noch", "über", "unter", "vor", "wenn",
    "dass", "daß", "was", "wer", "wo", "sc", "vgl", "ebend", "u", "s", "d", "z",
    "b", "e", "a",
}

MIN_TOKEN = 3

#: below this many content tokens on either side, a Jaccard ratio is noise
MIN_TERMS = 3


def strip_markup(text):
    """Bare prose: markup, page marks, citations and Sanskrit spans removed,
    **meaning glosses kept**.

    The two brace spans are opposites and must be treated as such: `{#…#}` is
    Sanskrit and is dropped (a shared headword is not evidence that two glosses
    say the same thing), while `{%…%}` holds the German meaning and is unwrapped.
    """
    t = PAGE.sub(" ", text or "")
    t = LS_RE.sub(" ", t)
    t = SANSKRIT.sub(" ", t)
    t = GLOSS.sub(lambda m: " %s " % m.group(1), t)
    t = TAG.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip()


def tokens(text):
    """Content-word tokens of a German gloss, lowercased and stop-filtered."""
    words = re.findall(r"[A-Za-zÄÖÜäöüß]+", strip_markup(text).lower())
    return {w for w in words if len(w) >= MIN_TOKEN and w not in STOP_DE}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a | b))


def citations(text):
    """Normalized source sigla cited in a body (work, not exact locus)."""
    out = set()
    for inner in LS_RE.findall(text or ""):
        vis = TAG.sub("", inner).strip()
        head = re.match(r"^([^0-9]{1,28})", vis)
        if head:
            key = re.sub(r"[\s.]+", "", head.group(1)).upper()
            if key:
                out.add(key)
    return out


def compare(pwg_de, supp_de):
    """The three axes, for one (PWG sense, supplement) pair."""
    tp, ts = tokens(pwg_de), tokens(supp_de)
    cp, cs = citations(pwg_de), citations(supp_de)
    lp, ls_ = len(strip_markup(pwg_de)), len(strip_markup(supp_de))
    return {
        "gloss_overlap": round(jaccard(tp, ts), 3),
        "shared_terms": sorted(tp & ts)[:12],
        "citation_overlap": (round(len(cp & cs) / float(len(cp)), 3) if cp else None),
        "shared_citations": sorted(cp & cs)[:8],
        "length_ratio": (round(ls_ / float(lp), 2) if lp else None),
        "pwg_chars": lp, "supp_chars": ls_,
        # Token counts travel with the ratio so a 1-of-1 match is visibly weak
        # rather than reading as "identical": several pairs score 1.000 purely on
        # one shared grammatical abbreviation (`pass.`, `med.`) over two glosses
        # that are otherwise empty. `comparable` is the honest gate — below it,
        # the ratio is noise and must not be shown as evidence.
        "pwg_terms": len(tp), "supp_terms": len(ts),
        "comparable": bool(len(tp) >= MIN_TERMS and len(ts) >= MIN_TERMS),
    }


# ------------------------------------------------------------------ corpus pass
def load():
    store = {}
    for line in io.open(STORE, encoding="utf-8"):
        line = line.strip()
        if line:
            d = json.loads(line)
            store[(d["subcard"], str(d.get("sense_tag")))] = d
    rel = []
    for line in io.open(REL, encoding="utf-8"):
        line = line.strip()
        if line:
            rel.append(json.loads(line))
    return store, rel


def pwg_sense_index(store):
    """(key1, homonym, normalised sense) -> the PWG sub-card row for that sense.

    Keyed on the H2879-normalised tag so the skeleton side and the supplement's
    target go through the same function; ``'1)'`` in the skeleton and ``'1'`` in
    the target are the same sense and must land on the same key.
    """
    from edition_rel import normalize_sense_tag
    idx = {}
    for (sub, st), d in store.items():
        if d.get("layer") != "pwg":
            continue
        m = re.search(r"~~(h\d+)", sub or "")
        idx[(d.get("key1"), m.group(1) if m else "h0",
             normalize_sense_tag(st))] = d
    return idx


def placement_target(idx, r):
    """The PWG row this supplement is placed at, or None if it is not placed.

    Single source of truth for consumers (H2879 S6/A9): the *decision* is read
    from the sidecar's ``placement`` flag — never recomputed here — and the row
    is then fetched for display. A consumer that re-derives "did a target turn
    up" is exactly the drift wave 1 removes.
    """
    from edition_rel import normalize_sense_tag
    rel = r["relationship"]
    if not rel.get("placement"):
        return None
    ip = rel.get("insertion_point") or {}
    return idx.get((r.get("key1"), ip.get("homonym", "h0"),
                    normalize_sense_tag(ip.get("target_sense"))))


#: `placement_reason` in the words a reviewer reads on a card (H2879 S6).
PLACEMENT_REASON_RU = {
    "found": "цель найдена",
    "no_target_marker": "цель не указана",
    "out_of_range": "номер выше диапазона PWG",
    "not_found": "смысл не найден",
}


def measure_all():
    store, rel = load()
    idx = pwg_sense_index(store)
    rows = []
    for r in rel:
        rec = store.get((r["subcard"], str(r["sense_tag"])))
        if not rec or rec.get("layer") == "pwg":
            continue
        ip = r["relationship"]["insertion_point"]
        target = placement_target(idx, r)
        if not target:
            continue          # not placed — nothing to compare against
        m = compare(target.get("de", ""), rec.get("de", ""))
        m.update({
            "key1": r.get("key1"), "subcard": r["subcard"],
            "sense_tag": str(r["sense_tag"]), "layer": r["layer"],
            "subtype": r["relationship"]["subtype"],
            "op": r["relationship"]["op"],
            "target_sense": str(ip.get("target_sense")),
            "placement_reason": r["relationship"].get("placement_reason"),
        })
        rows.append(m)
    return rows


CLASS = {"restate": "restates", "pw_correct": "cancels", "pw_cancels": "cancels"}


def klass(subtype):
    return CLASS.get(subtype, "adds")


def main():
    if not os.path.exists(STORE) or not os.path.exists(REL):
        print("store/sidecar missing under %s — set PWG_RU_DATA_ROOT" % DATA)
        return 1
    rows = measure_all()
    if not rows:
        print("no comparable (supplement, PWG sense) pairs found")
        return 1
    os.makedirs(REPORTS, exist_ok=True)
    out = os.path.join(REPORTS, "reglue_overlap.jsonl")
    with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    by = collections.defaultdict(list)
    for r in rows:
        by[klass(r["subtype"])].append(r)

    def stats(vals):
        vals = sorted(v for v in vals if v is not None)
        if not vals:
            return (0, 0.0, 0.0, 0.0)
        n = len(vals)
        return (n, vals[0], vals[n // 2], vals[-1])

    print("comparable (supplement -> PWG sense) pairs: %d\n" % len(rows))
    print("  %-10s %6s   %-26s %-26s" % ("class", "n", "gloss_overlap (min/med/max)",
                                          "citation_overlap (min/med/max)"))
    for k in ("adds", "restates", "cancels"):
        rs = by.get(k) or []
        n, g0, g1, g2 = stats([r["gloss_overlap"] for r in rs])
        _, c0, c1, c2 = stats([r["citation_overlap"] for r in rs])
        print("  %-10s %6d   %5.3f / %5.3f / %5.3f      %5.3f / %5.3f / %5.3f"
              % (k, n, g0, g1, g2, c0, c1, c2))

    # does the measurement separate the classes at all?
    med = {k: (stats([r["gloss_overlap"] for r in (by.get(k) or [])])[2]) for k in by}
    print("\nmedian gloss overlap — restates %.3f vs adds %.3f"
          % (med.get("restates", 0.0), med.get("adds", 0.0)))
    print("wrote %s" % out)
    return 0


# --------------------------------------------------------------------- selftest
def selftest():
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    a = "{#gA#} gehen, kommen, wandern <ls>ṚV. 1,2,3</ls>."
    b = "{#gA#} gehen und kommen <ls>ṚV. 1,2,3</ls>."
    c = "{#gA#} ein Loblied singen <ls>MBH. 5,6</ls>."

    near = compare(a, b)
    far = compare(a, c)
    check(near["gloss_overlap"] > far["gloss_overlap"],
          "a near-duplicate gloss scores higher than an unrelated one (%.3f > %.3f)"
          % (near["gloss_overlap"], far["gloss_overlap"]))
    check(near["citation_overlap"] == 1.0, "identical citation -> overlap 1.0")
    check(far["citation_overlap"] == 0.0, "different citation -> overlap 0.0")

    # Sanskrit must not manufacture similarity
    s1, s2 = "{#gA#} gehen", "{#gA#} verkaufen"
    check(compare(s1, s2)["gloss_overlap"] == 0.0,
          "a shared {#headword#} alone gives ZERO overlap, not spurious similarity")

    # stopwords must not manufacture similarity
    t1, t2 = "der und die mit von", "der und die mit von"
    check(compare(t1, t2)["gloss_overlap"] == 0.0,
          "two all-stopword glosses give 0.0, not 1.0")

    # citations must not leak into gloss tokens
    check("mbh" not in tokens("gehen <ls>MBH. 5,6</ls>"),
          "citation sigla are stripped before tokenizing")

    # length ratio
    lr = compare("a" * 100, "b" * 25)["length_ratio"]
    check(lr == 0.25, "length_ratio is supplement/pwg (%.2f)" % lr)

    # empty side never divides by zero
    e = compare("", "gehen")
    check(e["gloss_overlap"] == 0.0 and e["citation_overlap"] is None,
          "an empty PWG side yields 0.0 / None, not a crash")

    print("reglue_overlap selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
