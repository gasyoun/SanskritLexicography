#!/usr/bin/env python3
"""H4878 adjudicator: one verdict row per candidate of the deterministic
mw_pwk_nachtraege_missing_entries.py pipeline (the trial list, post-#2206).

Reads the re-derived missing_candidates.tsv (4,151 rows: NO-MATCH / stem /
near-formN.NN tiers + rank A/B/C), joins cross-dictionary corroboration
(36 Cologne dicts), MAHĀVY citations (pw.txt bodies by L), DCS-conllu
lemma/form attestation, and writes:

  MW-NACHTRAG-ADJUDICATION-<DATE>.tsv   canonical verdict TSV (4,151 rows)
  MW-NACHTRAG-TIERA-STUBS-<DATE>.md     stubs for corroborated Tier A (NO-MATCH)

Verdict semantics (frozen, explicit):
  confirmed-missing           NO-MATCH tier: absent from MW verbatim, stem AND
                              near-form space.
  covered-by-MW-stem-form     stem tier: MW carries the same stemkey headword.
  covered-by-fold-twin-flagged  nearform1.00: MW carries a case/vowel-length
                              twin (the Akalita/akalita trap named in H4878) -
                              same lexeme or distinct word needs human eyes.
  near-form-needs-eyes        nearform0.80..0.97: MW near form may be the same
                              word (orthographic variance) or a false friend
                              (kAritra~kArita); corroborated false friends stay
                              missing - the corroboration columns carry that
                              call, never the fuzzy score alone.

H4883 extension (MG ruling 15-09-2026 «Да, авто-подтверждать»): a near-form row
is AUTO-CONFIRMED (verdict confirmed-missing, review_note token
`add-check:auto-confirmed-false-friend`) when the matched MW near form is a
DOCUMENTED false friend - the kArita-class: the near form is itself a separate,
documented pw.txt entry at a DIFFERENT page location than the candidate
(kArita = pw 2-052-c 'causativus' vs kAritra = pw 7-331-d '= cezita'), i.e.
PW documents both as distinct lexemes, so MW carrying the near form does not
cover the candidate. Rows whose near form is MW-only (not a pw entry) or sits
at the candidate's own pw location (orthographic-variant suspects) stay
near-form-needs-eyes. Minimum bar per auto-confirmed row: near-form identity
(mw_forms + friend pw location in the note) + corroboration profile
(corr_n/corr_dicts) recorded.
Stdlib only. Usage: python -u mw_pwk_nachtraege_adjudicate.py [csl-orig-v02]
"""
import os
import re
import sys
import time
import random
from pathlib import Path

t0 = time.time()
OUT = Path(__file__).parent
DATE = "15-09-2026"

V02 = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(os.environ.get("CSL_ORIG_V02", ""))
if not V02 or not V02.exists():
    sys.exit("ERROR: pass csl-orig v02 dir as argv[1] or set CSL_ORIG_V02")

DCS = Path(os.environ.get("DCS_CONLLU", "")) if os.environ.get("DCS_CONLLU") else None

SLP1_IAST = {
    "A": "ā", "I": "ī", "U": "ū", "f": "ṛ", "F": "ṝ", "x": "ḷ", "X": "ḹ",
    "E": "ai", "O": "au", "M": "ṃ", "H": "ḥ", "N": "ṅ", "Y": "ñ", "w": "ṭ",
    "W": "ṭh", "q": "ḍ", "Q": "ḍh", "R": "ṇ", "T": "th", "D": "dh", "L": "ḻ",
    "S": "ś", "z": "ṣ", "K": "kh", "G": "gh", "C": "ch", "J": "jh", "P": "ph", "B": "bh",
}


def iast(s):
    return "".join(SLP1_IAST.get(c, c) for c in s)


def clean(hw):
    return "".join(c for c in hw if c.isalpha())


def norm_braces(txt):
    """H4883: normalise PW {#...#} headword markup (accent '/', '*' etc.) so a
    body equation can be matched against the plain SLP1 headword."""
    return re.sub(r"\{#([^#]*)#\}",
                  lambda m: "{#" + clean(m.group(1)) + "#}", txt)


STEM_SUFFIXES = ("aH", "aM", "as", "am", "an", "at", "eH", "oH",
                 "A", "a", "I", "i", "U", "u", "F", "f", "o", "e")


def stemkey(hw):
    for suf in STEM_SUFFIXES:
        if hw.endswith(suf) and len(hw) > len(suf):
            return hw[: -len(suf)]
    return hw


HW_LINE = re.compile(r"^<L>([^<]+)<pc>([^<]*)<k1>([^<]*)<k2>([^<]*)")


def dict_set(path):
    ks = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = HW_LINE.match(line)
            if m:
                for k in (clean(m.group(3)), clean(m.group(4))):
                    if k:
                        ks.add(k)
    return ks


MAHVY = re.compile(r"MAHĀVY\.?\s*((?:[0-9]+(?:\s*[.,]\s*)?)+)")


def main():
    cand_path = OUT / "mw_pwk_nachtraege_candidates_14-09-2026.tsv"
    if not cand_path.exists():
        cand_path = OUT / "missing_candidates.tsv"
    if not cand_path.exists():
        sys.exit("candidate list not found: run mw_pwk_nachtraege_missing_entries.py first")
    with open(cand_path, encoding="utf-8") as f:
        lines = f.read().strip("\n").split("\n")
    header = lines[0].split("\t")
    rows = [dict(zip(header, ln.split("\t"))) for ln in lines[1:]]
    n_candidates = len(rows)
    print(f"candidates from deterministic pipeline: {n_candidates}", flush=True)

    # ---- corroboration sets ----
    DICTS = ["mw72", "pwg", "ap90", "bhs", "cae", "mci", "vei", "yat", "sch", "ap",
             "skd", "lan", "md", "pe", "pui", "wil", "bor", "bop", "ben", "gra",
             "gst", "ieg", "inm", "krm", "lrv", "nybj", "shs", "snp", "stc", "vcp",
             "armh", "acc", "ae", "bur", "ccs", "fri"]
    sets = {n: dict_set(V02 / n / f"{n}.txt") for n in DICTS
            if (V02 / n / f"{n}.txt").exists()}
    print(f"corroboration dictionaries: {len(sets)}", flush=True)

    # ---- MW stem map (for covered-by-stem resolution) + folded headword set ----
    mw_stems = {}
    mw_hw_all = set()
    with open(V02 / "mw" / "mw.txt", encoding="utf-8") as f:
        for line in f:
            m = HW_LINE.match(line)
            if m:
                for k in (clean(m.group(3)), clean(m.group(4))):
                    if k:
                        mw_stems.setdefault(stemkey(k), set()).add(k)
                        mw_hw_all.add(k)
    mw_fold = {x.lower() for x in mw_hw_all}
    print(f"MW stemkey groups: {len(mw_stems)}", flush=True)

    # ---- pw.txt bodies by L (MAHĀVY cites) + headword -> first-entry pc ----
    pw_body = {}
    pw_pc_first = {}   # H4883: headword -> pc of its FIRST pw.txt entry
    pw_first_body = {}  # H4883: headword -> that entry's body lines (shared list)
    cur = None
    with open(V02 / "pw" / "pw.txt", encoding="utf-8") as f:
        for line in f:
            m = HW_LINE.match(line)
            if m:
                k1, k2 = clean(m.group(3)), clean(m.group(4))
                cur = (m.group(1), k1, [])
                pw_body[m.group(1)] = cur
                for k in (k1, k2):
                    if k and k not in pw_pc_first:
                        pw_pc_first[k] = m.group(2)
                        pw_first_body[k] = cur[2]
            elif cur is not None:
                cur[2].append(line)
    print(f"pw.txt entries indexed: {len(pw_body)} "
          f"({len(pw_pc_first)} headwords keyed by location)", flush=True)

    # ---- DCS ----
    dcs_lemmas, dcs_forms = set(), set()
    if DCS and DCS.exists():
        for conllu in sorted(DCS.glob("files/*/*.conllu")):
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
        print(f"DCS: {len(dcs_lemmas)} lemmas / {len(dcs_forms)} forms", flush=True)

    # ---- adjudicate ----
    out_rows = []
    for r in rows:
        hw = clean(r["slp1"])
        tier = r["tier"]
        b = pw_body.get(r["pwk_L"], (None, None, [""]))
        body = "".join(b[2])
        mahv = MAHVY.search(body)
        corr = [d for d in sorted(sets) if hw in sets[d]]
        corr_n = len(corr)
        rec = {"pwk_L": r["pwk_L"], "pwk_pc": r["pwk_pc"],
               "hw_slp1": r["slp1"], "iast": r["iast"],
               "pipeline_tier": tier, "rank": r["rank"],
               "mw_fuzzy": r["mw_fuzzy"], "evidence": r["evidence"],
               "corr_n": corr_n, "corr_dicts": ";".join(corr),
               "mahavy": 1 if mahv else 0,
               "mahavy_refs": mahv.group(1).strip() if mahv else "",
               "dcs_lemma": 0, "dcs_form": 0,
               "body_chars": len(body.strip())}
        if dcs_lemmas:
            ia = iast(hw)
            rec["dcs_lemma"] = 1 if ia in dcs_lemmas else 0
            rec["dcs_form"] = 1 if ia in dcs_forms else 0

        notes = []
        if tier == "NO-MATCH":
            rec["verdict"] = "confirmed-missing"
            if r["mw_fuzzy"]:
                notes.append(f"false-friend near form '{r['mw_fuzzy']}' in MW - different word, omission stands")
            if len(hw) <= 4:
                notes.append("pratyayhara/short-form class")
        elif tier == "stem":
            rec["verdict"] = "covered-by-MW-stem-form"
            forms = sorted(mw_stems.get(stemkey(hw), []))[:3]
            rec["mw_forms"] = ";".join(forms)
        elif tier.startswith("nearform1.00"):
            rec["verdict"] = "covered-by-fold-twin-flagged"
            rec["mw_forms"] = r["mw_fuzzy"]
            notes.append("case/vowel-length twin of MW form (Akalita/akalita trap) - same lexeme or distinct word, needs eyes")
        else:
            # H4883 auto-confirm: a near-form row is a DOCUMENTED false friend
            # when the matched MW near form is itself a separate pw.txt entry
            # at a DIFFERENT location than the candidate, carries its OWN sense
            # (not a redirect / see-reference stub), and the candidate's own pw
            # entry does not equate it to the near form (the kArita-class:
            # kArita pw 2-052-c 'causativus' vs kAritra pw 7-331-d '= cezita').
            # Everything else - MW-only near forms, same-location near forms,
            # cross-reference stubs, variant equations - stays needs-eyes.
            friend = r["mw_fuzzy"]
            fpc = pw_pc_first.get(friend)
            rec["mw_forms"] = friend
            withhold = None
            if friend and fpc and fpc != r["pwk_pc"]:
                fbody = norm_braces(" ".join("".join(pw_first_body.get(friend, []))
                                             .replace("<LEND>", "").split()))
                # candidate bodies to test for an equation: the sup_7 Nachtrag
                # entry (pwk_L, often just a sense pointer like '{#X#}¦ 5.')
                # AND the headword's main (first) pw entry, where the equation
                # 'X = near-form' normally lives.
                cand_bodies = []
                if body.strip():
                    cand_bodies.append(norm_braces(" ".join(body.split())))
                fb_hw = pw_first_body.get(hw)
                if fb_hw:
                    cand_bodies.append(norm_braces(
                        " ".join("".join(fb_hw).replace("<LEND>", "").split())))

                def eq_re(h):
                    h = re.escape(h)
                    return (r"(?:=\s*\{#" + h + r"#\})"
                            r"|(?:<ab>s\.</ab>\s*\{#" + h + r"#\})"
                            r"|(?:\{%\s*vgl\.\s*" + h + r"\s*%\})")

                if re.fullmatch(r"\{\{Lbody=\d+\}\}", fbody):
                    withhold = ("near form is a pw cross-reference entry with no "
                                "own sense")
                elif re.fullmatch(r"(?:\*?\{#[^#]+#\}\s*¦?\s*)?"
                                  r"(?:<lex>[^<]*</lex>\s*)?"
                                  r"(?:<ab>(?:s|vgl)\.</ab>)\s*\{#[^#]+#\}\.?\s*",
                                  fbody):
                    withhold = "near form is a bare see-reference with no own sense"
                elif hw.lower() in mw_fold:
                    withhold = ("a case-folded MW headword exists (Akalita/akalita "
                                "trap: SLP1 case is phonemic) - needs eyes")
                elif any(re.search(eq_re(friend), cb) for cb in cand_bodies):
                    withhold = (f"candidate's own pw entry equates it to the near "
                                f"form ({friend}) - variant/editorial call, not a "
                                "clean omission")
                elif re.search(eq_re(hw), fbody):
                    withhold = (f"near form's own pw entry equates it to the "
                                f"candidate ({hw}) - variant/editorial "
                                "call, not a clean omission")
            if withhold is None and friend and fpc and fpc != r["pwk_pc"]:
                rec["verdict"] = "confirmed-missing"
                notes.append(
                    "add-check:auto-confirmed-false-friend: near form "
                    f"'{friend}' is a separate pw.txt entry at {fpc} "
                    f"(candidate at {r['pwk_pc']}) carrying its own distinct "
                    "sense - omission stands")
            else:
                rec["verdict"] = "near-form-needs-eyes"
                if withhold:
                    notes.append(f"auto-confirm withheld: {withhold}")
        rec["review_note"] = "; ".join(notes)
        out_rows.append(rec)

    cols = ["pwk_L", "pwk_pc", "hw_slp1", "iast", "pipeline_tier", "rank",
            "mw_fuzzy", "evidence", "mw_forms", "verdict", "corr_n", "corr_dicts",
            "mahavy", "mahavy_refs", "dcs_lemma", "dcs_form", "body_chars",
            "review_note"]
    adj_path = OUT / f"MW-NACHTRAG-ADJUDICATION-{DATE}.tsv"
    with open(adj_path, "w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for rec in out_rows:
            f.write("\t".join(str(rec.get(c, "")) for c in cols) + "\n")

    # ---- Tier-A stubs: confirmed-missing NO-MATCH rows with corr_n >= 2 ----
    # (H4883: stub semantics stay NO-MATCH-only, so the corroborated-add count
    #  is not inflated by auto-confirmed false-friend rows.)
    tier_a = [r for r in out_rows
              if r["verdict"] == "confirmed-missing"
              and r["pipeline_tier"] == "NO-MATCH" and r["corr_n"] >= 2]
    tier_a.sort(key=lambda r: (-(2 * r["corr_n"] + 2 * r["mahavy"] + 2 * r["dcs_lemma"]
                                 + (1 if r["body_chars"] > 60 else 0)
                                 - (1 if r["mw_fuzzy"] else 0)), r["hw_slp1"]))
    stubs_path = OUT / f"MW-NACHTRAG-TIERA-STUBS-{DATE}.md"
    with open(stubs_path, "w", encoding="utf-8") as f:
        f.write(f"""# MW-entry stubs — PWK Nachtraege Tier A (corroborated >=2 dictionaries, absent from MW)

_Created: {DATE} · Last updated: {DATE}_

H4878 product over the deterministic pipeline list
([`mw_pwk_nachtraege_candidates_14-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_pwk_nachtraege_candidates_14-09-2026.tsv)),
adjudicated in full in
[`MW-NACHTRAG-ADJUDICATION-{DATE}.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-{DATE}.tsv).
Stubs = `confirmed-missing` rows (NO-MATCH tier) with corroboration >= 2 of 36
Cologne dictionaries, ordered by recommendation score. Glosses are the PW body
verbatim (tag-stripped), not translated. Posting anything = MG ruling.

""")
        for r in tier_a:
            mah = f" · MAHĀVY {r['mahavy_refs']}" if r["mahavy"] else ""
            near = f" · ⚠ false friend in MW: {r['mw_fuzzy']}" if r["mw_fuzzy"] else ""
            note = f" · ⚠ {r['review_note']}" if r["review_note"] else ""
            dcs = ("DCS lemma attested" if r["dcs_lemma"] else
                   "DCS form only" if r["dcs_form"] else "no DCS attestation found")
            f.write(f"### {r['iast']}\n"
                    f"- SLP1 `{r['hw_slp1']}` · rank {r['rank']} · {r['corr_dicts']}{mah}{near}{note} · {dcs}\n"
                    f"- Source: pw.txt L{r['pwk_L']} ({r['pwk_pc']})\n"
                    f"- Proposed MW headword: `{r['hw_slp1']}`\n")

    n_conf = sum(1 for r in out_rows if r["verdict"] == "confirmed-missing")
    n_stem = sum(1 for r in out_rows if r["verdict"] == "covered-by-MW-stem-form")
    n_fold = sum(1 for r in out_rows if r["verdict"] == "covered-by-fold-twin-flagged")
    n_near = sum(1 for r in out_rows if r["verdict"] == "near-form-needs-eyes")
    n_auto = sum(1 for r in out_rows
                 if "add-check:auto-confirmed-false-friend" in r["review_note"])
    # H4883 canary: kAritra must come out confirmed-missing in the main pass
    # (false-negative guard for the near-form auto-confirm).
    canary = next((r for r in out_rows if r["hw_slp1"] == "kAritra"), None)
    canary_line = ("canary kAritra: NOT FOUND - FAIL" if canary is None else
                   f"canary kAritra: {canary['pipeline_tier']} -> {canary['verdict']} "
                   + ("PASS (false-negative guard)"
                      if canary["verdict"] == "confirmed-missing" else "FAIL"))
    print(f"""
== canonical adjudication (H4878 + H4883 auto-confirm) ==
rows: {len(out_rows)} (candidate count {n_candidates})
confirmed-missing: {n_conf}   covered-by-MW-stem-form: {n_stem}
covered-by-fold-twin-flagged: {n_fold}   near-form-needs-eyes: {n_near}
  of confirmed-missing, auto-confirmed false-friend: {n_auto}
Tier-A stubs: {len(tier_a)} -> {stubs_path.name}
{canary_line}
wrote {adj_path.name} in {time.time()-t0:.0f}s""", flush=True)

    # ---- spot-check sample (deterministic seed) ----
    random.seed(4878)
    conf = [r for r in out_rows if r["verdict"] == "confirmed-missing"]
    sample = random.sample(conf, min(30, len(conf)))
    sp_path = OUT / f"MW-NACHTRAG-SPOTCHECK-30-{DATE}.tsv"
    mw_hw_set = set()
    with open(V02 / "mw" / "mw.txt", encoding="utf-8") as f:
        for line in f:
            m = HW_LINE.match(line)
            if m:
                for k in (clean(m.group(3)), clean(m.group(4))):
                    if k:
                        mw_hw_set.add(k)
    with open(sp_path, "w", encoding="utf-8") as f:
        f.write("hw_slp1\tiast\tpwk_L\tpwk_pc\tpipeline_tier\tcorr_n\tcorr_dicts\t"
                "mahavy\tdcs_lemma\tmw_fuzzy\tfriend_pw_pc\t"
                "mw_exact_hit\tmw_fold_hit\tmw_stem_hit\n")
        fold_set = set()
        for forms in mw_stems.values():
            fold_set |= forms
        fold_lower = {x.lower() for x in fold_set}
        stem_all = set(mw_stems.keys())
        for r in sample:
            f.write("\t".join([
                r["hw_slp1"], r["iast"], r["pwk_L"], r["pwk_pc"], r["pipeline_tier"],
                str(r["corr_n"]), r["corr_dicts"], str(r["mahavy"]),
                str(r["dcs_lemma"]), r["mw_fuzzy"],
                pw_pc_first.get(r["mw_fuzzy"], ""),
                "1" if r["hw_slp1"] in mw_hw_set else "0",
                "1" if r["hw_slp1"].lower() in fold_lower else "0",
                "1" if stemkey(r["hw_slp1"]) in stem_all else "0"]) + "\n")
    print(f"spot-check sample -> {sp_path.name}", flush=True)


if __name__ == "__main__":
    main()
