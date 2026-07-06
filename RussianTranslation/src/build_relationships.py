#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_relationships.py — Deliverable 1 of H180 (ADDENDA_TYPOLOGY.md).

Populate the `provenance.relationship` typology for every non-`pwg` sub-card in
the layered translated store, and roll it up by (subtype, layer).

Design choices (honour H180 guardrails):
  * NO re-translation, NO workflow/translate call — pure metadata over the
    already-translated store.
  * NON-DESTRUCTIVE: the canonical store `pwg_ru_translated.jsonl` is left
    byte-identical. Relationships are emitted to a *separate sidecar*
    `src/pwg_ru_relationships.jsonl`, keyed by (subcard, sense_tag), which
    REGLUE_SPEC's build_reglue.py consumes. (The typology's "write the sidecar
    back per sub-card" is realised as an external sidecar so the layered store
    stays canonical — the store is the single source of truth for `ru`.)
  * Every instance is `confidence: "llm"` (first-pass, LLM/heuristic-proposed);
    the human gold standard is a separate, later deliverable — never overwrite
    an llm verdict in place.

Inputs  : src/pwg_ru_translated.jsonl
Outputs : src/pwg_ru_relationships.jsonl   (one row per non-pwg sub-card sense)
          pwg_ru/relationships_rollup.tsv   (aggregate by subtype/op/direction/layer)

Run: python src/build_relationships.py
"""
import sys, os, io, json, re, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # RussianTranslation/
STORE = os.path.join(HERE, "pwg_ru_translated.jsonl")
OUT_JSONL = os.path.join(HERE, "pwg_ru_relationships.jsonl")
OUT_TSV = os.path.join(ROOT, "pwg_ru", "relationships_rollup.tsv")

LEX_RE = re.compile(r"<lex>(.*?)</lex>")
GENDER = {"m.", "n.", "f.", "mn.", "nm.", "mf.", "fn.", "mfn."}
# grammar-derivation markers in a sense_tag → a derived sub-sense (caus/desid/preverb)
DERIV_RE = re.compile(r"caus|desid|\bmit\b|\bdes\.\b|\banu\b|_(pat|caus|desid)|\bpra\b", re.I)

# --- light language heuristic for NWS foreign fragments (confidence: llm) -------
DE_MARK = re.compile(r"\b(der|die|das|und|ist|mit|ein|eine|nicht|von|zu|auf|sich|dem|den)\b", re.I)
EN_MARK = re.compile(r"\b(the|to|of|and|in|with|is|for|from|by|as)\b")
FR_MARK = re.compile(r"\b(le|la|les|du|des|une|avec|dans|pour|est|qui)\b")
LA_MARK = re.compile(r"\b(et|cum|ad|vel|non|est|quod|sunt|atque|sive)\b")
TAG_RE = re.compile(r"<[^>]+>")
BRACE_RE = re.compile(r"\{%.*?%\}")


def strip_markup(s):
    s = BRACE_RE.sub(" ", s or "")
    s = TAG_RE.sub(" ", s)
    return s


def guess_lang(de_text):
    """Return 'de' | 'en' | 'fr' | 'la' for an NWS source fragment (heuristic)."""
    t = strip_markup(de_text)
    scores = {
        "de": len(DE_MARK.findall(t)),
        "en": len(EN_MARK.findall(t)),
        "fr": len(FR_MARK.findall(t)),
        "la": len(LA_MARK.findall(t)),
    }
    best = max(scores, key=scores.get)
    # only claim non-German if it clearly beats German AND has real signal
    if best != "de" and scores[best] >= 2 and scores[best] > scores["de"]:
        return best
    return "de"


def lead_int(sense_tag):
    """Leading integer of a sense_tag ('2 (anu, Desid.)' -> '2'), else None."""
    m = re.match(r"\s*(\d+)", str(sense_tag))
    return m.group(1) if m else None


def homonym_of(subcard):
    m = re.search(r"~~(h\d+)", subcard or "")
    return m.group(1) if m else "h0"


def lex_tokens(rec):
    toks = LEX_RE.findall(rec.get("de", "") + " " + rec.get("ru", ""))
    return {t.strip() for t in toks if t.strip()}


def genders(toks):
    return {t for t in toks if t in GENDER}


def main():
    recs = []
    with io.open(STORE, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                recs.append(json.loads(line))

    # PWG skeleton gender map: (key1, homonym, sense_number) -> gender set
    pwg_gender = collections.defaultdict(set)
    for d in recs:
        if d.get("layer") != "pwg":
            continue
        si = lead_int(d.get("sense_tag"))
        if si:
            key = (d["key1"], homonym_of(d["subcard"]), si)
            pwg_gender[key] |= genders(lex_tokens(d))

    out = []
    roll = collections.Counter()
    lang_counter = collections.Counter()
    for d in recs:
        layer = d.get("layer")
        if layer == "pwg":
            continue
        key1 = d["key1"]
        hom = homonym_of(d["subcard"])
        st = str(d.get("sense_tag"))
        si = lead_int(st)
        target_sense = si if si else "*new"
        anchor = "sense"
        op = "add"
        direction = "additive"
        subtype = None
        evidence = ""
        extra = {}

        if layer == "sch":
            subtype = "derived_sense" if DERIV_RE.search(st) else "sch_star"
            evidence = f"SCH additive; sense_tag={st!r}"
        elif layer == "pwkvn":
            if DERIV_RE.search(st):
                subtype = "derived_sense"
                evidence = f"PWKVN grammar-derived; sense_tag={st!r}"
            else:
                subtype = "a2a"
                op = "relocate"
                evidence = f"PWKVN Nachtraege-to-Nachtraege (addenda-to-addenda); sense_tag={st!r}"
        elif layer == "nws":
            lang = guess_lang(d.get("de", ""))
            if lang != "de":
                subtype = "foreign_fragment"
                extra[f"needs_ru_from_{lang}"] = True
                extra["source_lang"] = lang
                evidence = f"NWS fragment in {lang.upper()} (heuristic); sense_tag={st!r}"
                lang_counter[lang] += 1
            else:
                subtype = "nws_at_sense"
                evidence = f"NWS additive at PWG sense {target_sense}; sense_tag={st!r}"
            # NWS-N tags are genuinely new NWS senses
            if re.match(r"\s*nws", st, re.I):
                target_sense = "*new"
        elif layer == "pw":
            direction = "abridging"
            pwg_g = pwg_gender.get((key1, hom, si)) if si else None
            pw_g = genders(lex_tokens(d))
            if pwg_g and pw_g and pwg_g.isdisjoint(pw_g):
                subtype = "pw_correct"
                op = "correct"
                anchor = "grammar"
                evidence = f"gender change PWG {sorted(pwg_g)} -> PW {sorted(pw_g)} at sense {si}"
            else:
                subtype = "restate"
                op = "restate"
                evidence = f"PW abridging restatement; sense_tag={st!r}"
        else:
            subtype = "unknown"

        rel = {
            "op": op,
            "target": "grammar" if anchor == "grammar" else "sense",
            "direction": direction,
            "subtype": subtype,
            "insertion_point": {
                "key1": key1, "homonym": hom,
                "target_sense": target_sense, "anchor": anchor,
            },
            "confidence": "llm",
            "evidence": evidence,
        }
        rel.update(extra)
        out.append({
            "subcard": d["subcard"], "key1": key1, "sense_tag": st,
            "layer": layer, "relationship": rel,
        })
        roll[(subtype, op, direction, layer)] += 1

    with io.open(OUT_JSONL, "w", encoding="utf-8") as fh:
        for r in out:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    with io.open(OUT_TSV, "w", encoding="utf-8") as fh:
        fh.write("subtype\top\tdirection\tlayer\tcount\n")
        for (subtype, op, direction, layer), n in sorted(
                roll.items(), key=lambda kv: (-kv[1], kv[0][0])):
            fh.write(f"{subtype}\t{op}\t{direction}\t{layer}\t{n}\n")

    print(f"non-pwg sub-card senses classified : {len(out)}")
    print(f"foreign-fragment languages         : {dict(lang_counter)}")
    print(f"wrote {OUT_JSONL}")
    print(f"wrote {OUT_TSV}")
    print("\nrollup:")
    for (subtype, op, direction, layer), n in sorted(
            roll.items(), key=lambda kv: (-kv[1], kv[0][0])):
        print(f"  {subtype:16s} {op:9s} {direction:9s} {layer:6s} {n}")


if __name__ == "__main__":
    main()
