#!/usr/bin/env python3
"""H4837 adjudicator: mechanical verdicts + DCS corpus join over the frozen list.

Reads MW-missing-PW-Nachtrag-candidates-14-09-2026.tsv (builder output),
joins DCS-conllu lemma/form attestation (env DCS_CONLLU), assigns the
mechanical verdict layer, and writes:

  MW-NACHTRAG-ADJUDICATION-14-09-2026.tsv   one row per candidate, verdict cols
  (LLM review overlay MW-NACHTRAG-REVIEW-OVERLAY-14-09-2026.tsv, if present,
   is applied last - review_verdict/review_note override the mechanical layer)

Mechanical verdicts (explicit semantics, frozen - class rules derived in the
H4837 review pass 14-09-2026):

  variant-form-in-MW    MW carries a headword with the IDENTICAL stem minus the
                        final vowel (the PWK headword is a stem/citation-form
                        doublet, e.g. aScary <-> aScarya). Whether the exact PWK
                        form deserves a separate MW entry is an editorial call,
                        so this is NOT counted as a clean omission.
  confirmed-missing     absent from MW in verbatim AND stemkey space.
Risk notes recorded (flags, never auto-verdicts - SLP1 case is phonemic, so a
case-fold twin may be a distinct word, e.g. Anumati gaNa-entry vs anumati):
  vowel-length variant of MW headword X (fold-twin, needs eyes)
  probable orthographic doublet of MW X (difflib >= 0.95: metathesis, single/
  double consonant, sandhi form)
  pratyayhara/short-form class (PWK lists grammatical elements MW does not)
  false-friend near form X (difflib >= 0.92, different word - the kAritra class)
Flags:
  mahavy (Mahavyutpatti citation), corr tier, dcs lemma/form attestation.

Stdlib only. Usage: python -u pw_nachtrag_adjudicate.py
"""
import os
import csv
import sys
import time
from pathlib import Path

t0 = time.time()
OUT = Path(__file__).parent
DATE = "14-09-2026"
CAND = OUT / f"MW-missing-PW-Nachtrag-candidates-{DATE}.tsv"
OVERLAY = OUT / f"MW-NACHTRAG-REVIEW-OVERLAY-{DATE}.tsv"
ADJ = OUT / f"MW-NACHTRAG-ADJUDICATION-{DATE}.tsv"
STUBS = OUT / f"MW-NACHTRAG-TIERA-STUBS-{DATE}.md"

SLP1_IAST = {
    "A": "ā", "I": "ī", "U": "ū", "f": "ṛ", "F": "ṝ", "x": "ḷ", "X": "ḹ",
    "E": "ai", "O": "au", "M": "ṃ", "H": "ḥ", "N": "ṅ", "Y": "ñ", "w": "ṭ",
    "W": "ṭh", "q": "ḍ", "Q": "ḍh", "R": "ṇ", "T": "th", "D": "dh", "L": "ḻ",
    "S": "ś", "z": "ṣ", "K": "kh", "G": "gh", "C": "ch", "J": "jh", "P": "ph", "B": "bh",
}


def iast(s):
    return "".join(SLP1_IAST.get(c, c) for c in s)


def main():
    with open(CAND, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    print(f"frozen candidates: {len(rows)}", flush=True)

    # ---- DCS corpus join ----
    dcs_dir = os.environ.get("DCS_CONLLU", "")
    dcs_lemmas, dcs_forms = set(), set()
    if dcs_dir and Path(dcs_dir).exists():
        n_files = 0
        for conllu in sorted(Path(dcs_dir).glob("files/*/*.conllu")):
            n_files += 1
            with open(conllu, encoding="utf-8") as f:
                for line in f:
                    if line.startswith("#") or "\t" not in line:
                        continue
                    parts = line.rstrip("\n").split("\t")
                    if len(parts) < 4 or "-" in parts[0]:
                        continue
                    if parts[2] != "_":
                        dcs_lemmas.add(parts[2])
                    if parts[1] != "_":
                        dcs_forms.add(parts[1])
        print(f"DCS-conllu: {n_files} files, {len(dcs_lemmas)} lemmas, {len(dcs_forms)} forms", flush=True)
    else:
        print("DCS_CONLLU not set - dcs columns stay from candidates file", flush=True)

    for r in rows:
        if dcs_lemmas:
            ia = iast(r["hw_slp1"])
            r["dcs_lemma"] = 1 if ia in dcs_lemmas else 0
            r["dcs_form"] = 1 if ia in dcs_forms else 0

        # ---- risk notes (mechanical, from the frozen builder columns) ----
        notes = []
        hw = r["hw_slp1"]
        if r["mw_near"]:
            form, ratio = r["mw_near"].rsplit(":", 1)
            if float(ratio) >= 0.999:
                notes.append(f"vowel-length/case variant of MW headword '{form}' (fold-twin - same lexeme or distinct word needs eyes)")
            elif float(ratio) >= 0.95:
                notes.append(f"probable orthographic doublet of MW headword '{form}' ({ratio})")
            else:
                notes.append(f"false-friend near form '{form}' ({ratio}) - different word, omission stands")
        if len(hw) <= 4:
            notes.append("pratyayhara/short-form class (PWK lists grammatical elements MW does not headword)")

        # ---- verdict ----
        corr_n = int(r["corr_n"])
        if r["mw_stem_variant"] == "1":
            r["verdict"] = "variant-form-in-MW"
        else:
            r["verdict"] = "confirmed-missing"
        # recommendation: the add-list ordering signal; stem-variants and
        # fold-twins are never clean adds
        risky = bool(notes) or r["verdict"] != "confirmed-missing"
        score = corr_n * 2 + int(r["mahavy"]) * 2 + int(r["dcs_lemma"]) * 2 \
            + (1 if int(r["body_chars"]) > 60 else 0) - (2 if risky else 0)
        r["rec_score"] = score
        r["recommendation"] = ("add" if corr_n >= 2 and not risky else
                               "add-check" if corr_n >= 2 else
                               "check" if corr_n == 1 else "low-priority")
        r["review_note"] = "; ".join(notes)

    # ---- review overlay (LLM pass, optional at run time) ----
    n_overlay = 0
    if OVERLAY.exists():
        with open(OVERLAY, encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                for r in rows:
                    if r["hw_slp1"] == row["hw_slp1"]:
                        if row.get("review_verdict"):
                            r["verdict"] = row["review_verdict"]
                        if row.get("review_note"):
                            r["review_note"] = row["review_note"]
                        n_overlay += 1
                        break
        print(f"overlay applied: {n_overlay} rows", flush=True)
    for r in rows:
        r.setdefault("review_note", "")

    # ---- write adjudication TSV ----
    cols = list(rows[0].keys())
    with open(ADJ, "w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r[k]) for k in cols) + "\n")

    # ---- Tier-A stubs (confirmed-missing, corr_n >= 2, sorted by rec_score desc) ----
    tier_a = [r for r in rows if int(r["corr_n"]) >= 2 and r["verdict"] == "confirmed-missing"]
    tier_a.sort(key=lambda r: (-int(r["rec_score"]), r["hw_slp1"]))
    with open(STUBS, "w", encoding="utf-8") as f:
        f.write(f"""# MW-entry stubs — PW/PWK Nachtraege Tier A (corroborated >=2 dictionaries), missing from MW

_Created: {DATE} · Last updated: {DATE}_

H4837 adjudication product. Frozen candidate list:
[MW-missing-PW-Nachtrag-candidates-{DATE}.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-missing-PW-Nachtrag-candidates-{DATE}.tsv)
(builder `pw_nachtrag_vs_mw.py`). Stubs below = `confirmed-missing` rows with
cross-dictionary corroboration >= 2 of the 36 Cologne dictionaries, ordered by
recommendation score (corroboration + Mahavyutpatti + DCS attestation - near-form risk).
Glosses are the PWK body verbatim (tag-stripped), not translated. MW-entry stubs
in SLP1 are proposals for the #119 discussion; upstream posting = MG ruling.

""")

        def stub(r):
            sources = [f"pw.txt L{r['pwk_L']} ({r['pwk_pc']})"] if r["src"] == "pw" else []
            if r["also_pwkvn"] == "1" or r["src"] == "pwkvn":
                sources.append("pwkvn.txt")
            dcs = ("DCS lemma attested" if r["dcs_lemma"] == "1" else
                   "DCS form only" if r["dcs_form"] == "1" else "no DCS attestation found")
            mah = f" · MAHĀVY {r['mahavy_refs']}" if r["mahavy"] == "1" else ""
            near = f" · ⚠ near-form in MW: {r['mw_near']}" if r["mw_near"] else ""
            note = f" · ⚠ {r['review_note']}" if r["review_note"] else ""
            return (f"### {r['iast']}\n"
                    f"- SLP1 `{r['hw_slp1']}` · {r['corr_dicts']}{mah}{near}{note} · {dcs}\n"
                    f"- Source: {' + '.join(sources)}\n"
                    f"- Proposed MW headword: `{r['hw_slp1']}`\n")

        for r in tier_a:
            f.write(stub(r))

    n_conf = sum(1 for r in rows if r["verdict"] == "confirmed-missing")
    n_var = sum(1 for r in rows if r["verdict"] == "variant-form-in-MW")
    n_near = sum(1 for r in rows if r["mw_near"])
    n_add = sum(1 for r in rows if r["recommendation"] == "add")
    n_a = len(tier_a)
    print(f"""
== adjudication (mechanical layer) ==
confirmed-missing: {n_conf}
variant-form-in-MW: {n_var}
near-form flags (>=0.92): {n_near}
clean adds (Tier A, no risk flags): {n_add}
Tier-A stubs written: {n_a} -> {STUBS.name}
wrote {ADJ.name} ({len(rows)} rows) in {time.time()-t0:.0f}s""", flush=True)


if __name__ == "__main__":
    main()
