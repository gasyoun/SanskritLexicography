#!/usr/bin/env python3
"""H3171 step 4 — hand classification of every disagreement cell.

One row per (gold row x witness) where the witness missed the adjudicated
lemma under strict normalized-set matching. Classes follow the phase-4
taxonomy (HeadwordLists/heritage_forms_oracle.md):
  policy   — internally-consistent lemmatization-policy difference
             (compound-entry granularity, root<->derived stem,
             pronoun/stem conventions)
  convention — spelling-convention variant of the same lexeme
             (nasal class, visarga/s, aspiration notation)
  surplus  — witness emitted extra spurious analyses alongside/instead of
             the target (segmenter shattering fragments)
  error    — genuinely wrong output (incl. Word-mode no-analysis gaps and
             §95-style shattering)
Each entry: (id, witness, class, note). Witness: 'H' or 'D'.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
GOLD_DIR = Path(__file__).resolve().parent.parent / "gold"

# id -> list of (witness, class, note)
CLASSES: dict[int, list[tuple[str, str, str]]] = {
    0:  [("H", "policy", "compound entry vs members sarva+bhUta"),
         ("D", "policy", "compound entry vs members sarva+bhUta")],
    2:  [("H", "policy", "root vR (+preverb ni) vs adjudicated causative stem nivAray — phase-4 kamp/kampay pattern")],
    3:  [("H", "error", "Word-mode no analysis (gerundive marjya)"),
         ("D", "policy", "root mfj vs gerundive-stem marjya")],
    8:  [("H", "policy", "members mahat+kapi (tat-sandhi mahA-) vs entry mahAkapi")],
    9:  [("H", "policy", "members mahat+ratha vs entry mahAraTa"),
         ("D", "error", "mahArata — aspiration h dropped, dental t for retroflex T")],
    10: [("H", "policy", "members sUtikA+agni vs entry sUtikAgni")],
    11: [("H", "policy", "participle sthit / root sthA vs adjudicated ppp sTita; + surplus fragments ASa/BU/Bu/Uta/av"),
         ("D", "error", "final member sTita absent from segmentation (§95 misalignment class)")],
    12: [("H", "policy", "members brahman+nirvARa vs entry brahmanirvARa"),
         ("D", "policy", "members brahman+nirvARa vs entry brahmanirvARa")],
    13: [("H", "policy", "members mokza+kAma vs entry mokzakAma"),
         ("D", "policy", "members mokza+kAma vs entry mokzakAma")],
    15: [("H", "error", "Word-mode no analysis (verbal noun snA)")],
    16: [("H", "error", "Word-mode no analysis (indeclinable evam)")],
    17: [("H", "policy", "members Barata+SrezWa vs entry BarataSrezWa"),
         ("D", "policy", "members Barata+SrezWa vs entry BarataSrezWa")],
    18: [("H", "error", "niSItha — aspirate lexeme variant for niSITa member"),
         ("D", "policy", "members niSITa+dIpa vs entry niSITadIpa")],
    19: [("H", "policy", "members ugra+tejas vs entry ugratejas; + surplus ij/teja/ugratA"),
         ("D", "policy", "members ugra+tejas vs entry ugratejas")],
    20: [("H", "policy", "members para+puraMjaya vs entry parapuraMjaya")],
    23: [("H", "policy", "members brahman+nirvARa vs entry brahmanirvARa"),
         ("D", "policy", "members brahman+nirvARa vs entry brahmanirvARa")],
    25: [("H", "error", "Word-mode no analysis (fjutA)"),
         ("D", "error", "shattered fjU+tA (§95 shatter class)")],
    27: [("H", "policy", "members Atman+yoga vs entry Atmayoga"),
         ("D", "policy", "members Atman+yoga vs entry Atmayoga")],
    28: [("H", "policy", "prefixed root split A+hf as two tokens vs composite Ahf")],
    29: [("H", "policy", "members tad+anantara vs entry tadanantara"),
         ("D", "policy", "members tad+anantaraM (inflection residue -M on lemma)")],
    32: [("H", "policy", "roots pra+hf split vs composite prahf; + surplus"),
         ("D", "policy", "intensive-stem prahara vs root prahf; + surplus fragment dva")],
    34: [("H", "policy", "members mahat+fzi vs entry maharzi"),
         ("D", "policy", "members mahat+fzi vs entry maharzi")],
    35: [("H", "error", "Word-mode no analysis (augmented imperfect aByuvAca)")],
    37: [("H", "policy", "members SaraRa+arthin vs entry SaraRArTin (sandhi spelling)"),
         ("D", "policy", "members SaraRa+artin vs entry; artin loses h (spelling note)")],
    38: [("H", "policy", "three-way split mahat+izu+Asa vs entry mahezvAsa; + surplus"),
         ("D", "policy", "members izvAsa+mahat vs entry mahezvAsa")],
    39: [("H", "error", "Word-mode no analysis (durDA)"),
         ("D", "error", "durdA — dental d for retroflex-aspirate D of gold durDA")],
    41: [("H", "policy", "members jYAna+yoga vs entry jYAnayoga"),
         ("D", "policy", "members jYAna+yoga vs entry jYAnayoga")],
    43: [("H", "convention", "bAndhava — standard dh spelling vs adjudicated D variant; + surplus iBa/iBya")],
    44: [("H", "error", "Word-mode no analysis (noun niDi)"),
         ("D", "policy", "root niD vs noun-stem niDi")],
    45: [("H", "error", "Word-mode no analysis (kaTaM-rUpa)"),
         ("D", "error", "kataMrUpa — garbled kaTaM and missed seam")],
    46: [("H", "error", "Word-mode no analysis (locative mahy)")],
    49: [("H", "policy", "members kAma+rUpa vs entry kAmarUpa")],
    51: [("H", "policy", "members maru+dhanvan vs entry maruDanvan; + surplus asu/dhanu"),
         ("D", "policy", "members maru+danvan vs entry maruDanvan")],
    53: [("H", "policy", "members saha+arjuna vs entry sahArjuna; + surplus ina"),
         ("D", "policy", "members saha+arjuna vs entry sahArjuna")],
    54: [("H", "policy", "members brahman+nirvARa vs entry brahmanirvARa"),
         ("D", "policy", "members brahman+nirvARa vs entry brahmanirvARa")],
    56: [("H", "policy", "pronoun stem asmad vs compound form mad; + surplus BU"),
         ("D", "policy", "member lemmas mad+bAVAa recover entry by join; set-match misses")],
    57: [("H", "policy", "members harza+mARa vs adjudicated root hfz (glossary went to root)")],
    58: [("H", "error", "Word-mode no analysis (ftayug)"),
         ("D", "policy", "members fta+yuj vs entry ftayuj")],
    62: [("H", "error", "Word-mode no analysis (CattraM)")],
    66: [("H", "policy", "members mahat+fddhi vs entry mahardDi"),
         ("D", "error", "maharddi — aspiration of geminate ddh reduced to dd")],
    68: [("H", "policy", "members jIva+BUta vs entry jIvaBUta; + heavy surplus BU/Bu/Uta/av/uta/vA"),
         ("D", "policy", "root BU vs participle BUta; entry jIvaBUta not modeled")],
    70: [("D", "policy", "inflected fem apUrvA given as lemma vs stem apUrva")],
    71: [("H", "policy", "members sthira+buddhi vs entry sTirabudDi"),
         ("D", "error", "shattered bud;di;ra;t (§95 shatter class)")],
    75: [("D", "error", "shattered durlaBa+tva and lost dh (labDh->laBa)")],
    78: [("H", "policy", "members jagat+nivAsa vs entry jagannivAsa (n-assimilation sandhi)")],
    79: [("H", "policy", "members yathA+Ipsita vs entry yaTepsita (t+I->Te sandhi)"),
         ("D", "error", "shattered/mangled Ips+yata (yathA misread)")],
    80: [("D", "policy", "root Baj vs ppp Bakta — phase-4 tyaj/tyakta pattern")],
    83: [("H", "policy", "members kuru+nandana vs entry kurunandana"),
         ("D", "policy", "members kuru+nandana vs entry kurunandana")],
    84: [("H", "policy", "members bAhya+sparSa vs entry bAhyasparSa"),
         ("D", "policy", "members bAhya+sparSa vs entry bAhyasparSa")],
    86: [("H", "error", "Word-mode no analysis (ukTa-ukTa)"),
         ("D", "policy", "root vac vs ppp ukTa — phase-4 suppletive pattern")],
    30: [("H", "error", "Word-mode no analysis (reduplicated perfect cikradad)")],
    50: [("D", "policy", "members agni+ja vs entry agnija")],
    64: [("H", "convention", "viBAgaSas (nominative -s listed as stem) vs adjudicated stem viBAgaSaH — visarga/s notation")],
    92: [("H", "error", "Word-mode no analysis (infinitive sravitave)")],
    108:[("H", "policy", "members karman+antara vs entry karmAntara")],
    90: [("H", "policy", "members bfhat+sAman vs entry bfhatsAman")],
    93: [("H", "error", "rathin — intrusive h (lexeme confusion rathin/raTin)"),
         ("D", "error", "ratin — dental t for retroflex T")],
    94: [("H", "error", "Word-mode no analysis (pronoun oblique tvad)"),
         ("D", "policy", "pronominal stem tva vs tvad (DCS tvad vs PAninian stem — dcs_sh alignment doc)")],
    97: [("H", "policy", "causative root Sru+pati vs entry SrAvayatpati"),
         ("D", "policy", "causative stem SrAvay+pati vs entry SrAvayatpati")],
    99: [("H", "policy", "members sva+dharma(dharman) vs entry svaDarma"),
         ("D", "policy", "member sva recovered; dharma garbled to darman")],
    100:[("H", "policy", "members sva+jana vs entry svajana"),
         ("D", "policy", "members sva+jana vs entry svajana")],
    101:[("H", "error", "Word-mode no analysis (indeclinable vAc)")],
    102:[("H", "error", "Word-mode no analysis (nIcIr)")],
    106:[("H", "error", "Word-mode no analysis (multi-prefix anu-vi-A-cal)"),
         ("D", "policy", "whole compounded anuviAcal vs glossary rightmost-member rule cal")],
    107:[("H", "policy", "members kalpa+anta vs entry kalpAnta; + surplus aM"),
         ("D", "policy", "members kalpa+anta vs entry kalpAnta")],
}


def main():
    results = [json.loads(l) for l in
               (GOLD_DIR / "h3171_results.jsonl").read_text(encoding="utf-8").splitlines()]
    by_id = {r["id"]: r for r in results}

    lines = ["id\tsurface\tgold\twitness\tpanel\tclass\tnote\twitness_output"]
    tally: dict[tuple[str, str], int] = {}
    per_witness_miss = {"H": 0, "D": 0}
    for gid, cells in sorted(CLASSES.items()):
        rec = by_id[gid]
        for wit, cls, note in cells:
            out = (";".join(rec["heritage_stems"]) if wit == "H"
                   else ";".join(rec["dm_lemmas"]))[:120]
            lines.append("\t".join([str(gid), rec["slp1"], rec["gold_lemma"],
                                    wit, rec["panel_lemma"], cls, note, out or "-"]))
            tally[(wit, cls)] = tally.get((wit, cls), 0) + 1
            per_witness_miss[wit] += 1

    (GOLD_DIR / "h3171_disagreements_classified.tsv").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")

    print(f"classified cells: {sum(per_witness_miss.values())} "
          f"(Heritage {per_witness_miss['H']}, Dharmamitra {per_witness_miss['D']})")
    for wit in "HD":
        print(f"-- witness {wit}")
        for cls in ["policy", "convention", "surplus", "error"]:
            print(f"   {cls:<11}{tally.get((wit, cls), 0)}")
        n = per_witness_miss[wit]
        non_err = sum(v for (w, c), v in tally.items() if w == wit and c != "error")
        print(f"   misses {n}; non-contradicting (policy+convention) "
              f"{non_err} ({100*non_err/n:.0f}% of misses)")


if __name__ == "__main__":
    main()
