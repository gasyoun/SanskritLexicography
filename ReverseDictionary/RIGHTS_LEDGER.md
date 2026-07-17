# Reverse Dictionary — rights ledger

_Created: 17-07-2026 · Last updated: 17-07-2026_

**What this is.** A rights *position* for the ~266,820-headword reverse Sanskrit
dictionary — every source dictionary sorted into exactly one of three buckets, so a
human can rule on publication with the evidence in front of them. It is **W1-E** of the
[PWG_RU_UNFREEZE plan](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_UNFREEZE_2026H2.md)
(R4 + §1), built to [`ARCHITECTURE_SanskritLexicography_PWG_RU_UNFREEZE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ARCHITECTURE_SanskritLexicography_PWG_RU_UNFREEZE.md)
§6.2, executed under [H1153](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1153-Opus_SanskritLexicography_revdict-rights-ledger-unresolvable-residue_17.07.26.md).

**What this is NOT.** This ledger **builds** the rights position; it does **not**
**resolve** it. The residue in Bucket 3 below is unresolvable *by measurement* — no
agent, no wider search, no harder reasoning turns it into a certified total. Closing it
needs money and a human decision (fund per-source headword lists for the five silent
sources), not effort. See [§4](#4-the-residue-is-unresolvable-by-agent-effort).

> **The headline claim, stated once and plainly:** the in-copyright contribution that
> *can be identified* is **14,471 / 266,820 = 5.4%** (`H` Edgerton 12,552 + `P` Vettam
> Mani 1,919). **14,471 is a LOWER BOUND, not a total.** Five in-copyright sources
> contribute an unknown, unmeasurable additional amount because they carry no marked
> source-code anywhere in the data. A "PD-only" subset **cannot be certified** on
> available data.

Provenance for every figure and status below: [`ACL_DH_COMPATIBILITY_ANALYSIS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/ACL_DH_COMPATIBILITY_ANALYSIS.md)
§3.1 + §5 (the H270 measurement, 07-07-2026) and [`SCHEMA.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/SCHEMA.md)'s
source-code table. This pass added no new measurement — the canonical list is not on
disk (see [§3](#3-the-canonical-list-is-not-recovered--escalated-as-data-loss)), so no
count could be re-run. It sorts the existing, SHA-anchored evidence into the rights
buckets the licensing ruling turns on.

---

## 1. The three buckets

The bucket that matters is the third. Buckets 1 and 2 are *subtractable* — their
contribution can be identified and, if a human rules "publish a subset", removed or
masked. Bucket 3 is *not subtractable* — its contribution cannot be identified, so it
can neither be published-around nor cleanly removed. Bucket 3 is the reason a "PD-only"
label is a false certification.

### Bucket 1 — PUBLIC DOMAIN (subtractable, safe)

The safely-PD sources. Where a source appears as a marked code in the canonical file,
its line count (from `SCHEMA.md`) is given; the majority of the list is the unmarked
PWK default. All statuses are death-year reasoning, **not legal advice**.

| Bib. key | Source | Marked code / lines in file | PD basis |
|---|---|---|---|
| `pwk` | Böhtlingk & Roth, *Sanskrit-Wörterbuch in kürzerer Fassung* (PWK) + Schmidt *Nachträge* — the implicit default | *(empty)* · 131,916 | 1879–1889; d. long past |
| `mwe` | Monier-Williams, *A Sanskrit–English Dictionary* (1899) | `M` · 57,177 | 1899; Monier-Williams d. 1899 |
| `sch` | Schmidt, *Nachträge zum Sanskrit-Wörterbuch* (1928) | `S` · 10,311 | Schmidt d. 1939; pre-1930 pub. |
| `pwg` | Böhtlingk & Roth, *Sanskrit-Wörterbuch* (large PWG, 1855–75) | `G` · 7,551 | 19th c. |
| `bur` | Burnouf, *Dictionnaire classique sanscrit-français* (1866) | `B` · 6,851 | 1866 |
| `shs` | *Shabda-Sagara Sanskrit-English Dictionary* | `R` · 6,620 | 19th c. |
| `inm` | Sørensen, *Index to the Names in the Mahabharata* (1904–14) | `N` · 3,551 | Sørensen d. 1902; pub. 1904–14 |
| `vac` | Tarkavācaspati, *Vachaspatyam* (1969–70 reprint of 1873–84 orig.) | `V` · 577 | orig. 1873–84; reprint not a new work |
| `wil` | Wilson (1832) | *(unmarked)* | 1832 |
| `yat` | Yates (1846) | *(unmarked)* | 1846 |
| `gst` | Goldstücker (1856) | *(unmarked)* | 1856 |
| `bop` | Bopp, *Glossarium* | *(unmarked)* | 19th c. |
| `cap` | Cappeller (1887) | *(unmarked)* | 1887 |
| `mcd` | Macdonell (1929) | *(unmarked)* | Macdonell d. 1930; pub. 1929 |
| `vei` | *Vedic Index* (1912) | *(unmarked)* | Keith d. 1944; pub. 1912 |
| `skd` | Śabdakalpadruma (orig. 1828–1858; 1967 Chowkhamba reprint) | *(unmarked)* | orig. 19th c.; reprint not a new work |
| `acc` | Aufrecht, *Catalogus Catalogorum* (orig. 1891–1903; 1962 reprint) | *(unmarked)* | orig. pre-1904; reprint not a new work |
| — | Grassmann, *Wörterbuch zum Rig-Veda* | *(unmarked)* | 19th c. |

**Likely PD, verify (2) — held here provisionally, flagged for confirmation.** Not
certified PD; a human should confirm before either is treated as safe.

| Bib. key | Source | Marked code / lines | Open question |
|---|---|---|---|
| `apt` | Apte, *Practical Sanskrit-English Dictionary* (1957–59 rev. ed.) | `A` · 21,081 | 1890 base is PD; the 1957–59 Prasad Prakashan **revision**'s status is murky (widely digitized incl. by Cologne, but no formal clearance) |
| `pui` | Dīkshitar, *The Purana Index* (1951–55) | `I` · 6,714 | Dīkshitar d. 1953 → India life+60 expired 2014; likely PD but unverified |

### Bucket 2 — IN COPYRIGHT, MARKED (subtractable, identified)

The in-copyright contribution that **can be seen** — it carries a marked source-code, so
it can be counted and, on a human ruling, removed or masked. This is the whole of what a
subtraction can reach.

| Bib. key | Source | Marked code | Headwords | Copyright basis |
|---|---|---|--:|---|
| `bhs` | Edgerton, *Buddhist Hybrid Sanskrit Grammar and Dictionary* (1953) | `H` | 12,552 | Edgerton d. 1963; 1953, in copyright |
| `pex` | Vettam Mani, *Puranic Encyclopaedia* (1979, English) | `P` | 1,919 | 1979, in copyright |
| **Total** | | | **14,471** | **= 5.4% of 266,820** |

> **14,471 is a LOWER BOUND.** It is what can be subtracted, not the total in-copyright
> contribution. See Bucket 3 for why the true figure is higher by an unknown amount.

### Bucket 3 — IN COPYRIGHT, UNMARKED — CANNOT BE ISOLATED

**This bucket is the deliverable's point.** All five of these sources are named in
`ACL_DH_COMPATIBILITY_ANALYSIS.md` §3.1 as "in copyright — clear risk", and all five
have a declared letter code in the bibliography — yet **not one of them ever appears as a
marked source-code anywhere in the 266,820-line canonical file** (`SCHEMA.md`: only 12 of
30 declared codes are used; these five are among the 18 declared-but-unused). Because the
scheme marks one letter per line and PWK/higher-priority sources win, any headword unique
to one of these five was silently absorbed under a higher-priority code (or the empty PWK
default) — **its contribution is present in the merged list but not distinguishable from
it.**

| Bib. key | Declared code | Source | Copyright basis | Why it cannot be subtracted |
|---|---|---|---|---|
| `stc` | `F` | Stchoupak–Nitti–Renou, *Dictionnaire sanscrit-français* (1932) | Renou d. 1966 → France ~2036 | No marked line in the file; unique contribution unidentifiable |
| `tur` | `T` | Turner, *Comparative Dictionary of the Indo-Aryan Languages* (CDIAL, 1962–66 + suppl. to 1985) | Turner d. 1983 → UK ~2053 | No marked line in the file; unique contribution unidentifiable |
| `myl` | `Z` | Mylius, *Wörterbuch Sanskrit–Deutsch* (1975) | Mylius d. 2023 | No marked line in the file; unique contribution unidentifiable |
| `kch` | `Q` | Kochergina, *Sanskritsko-russkiy slovar'* (1978) | Kochergina d. 2018 → RF ~2088 | No marked line in the file; unique contribution unidentifiable |
| `puj` | `O` | Pujol, *Diccionari sànscrit-català* (2005) | living author | No marked line in the file; unique contribution unidentifiable |

**Consequence.** You cannot certify "PD-only" by subtracting what you cannot see. A
subset built today would be PD-only **by assertion, not by evidence**. Establishing a
tighter bound would require per-source headword lists for these five sources, to diff
against the canonical list — those lists are not in this repo and cannot be derived from
the single-letter-per-line data. **This is why 14,471 is a lower bound and why a
"PD-only" label is a false certification.**

---

## 2. Why "PD-only" is a FAIL as a label

The label *is the deliverable's subject*. Publishing a subset called "PD-only" claims a
certification the data does not support: that every in-copyright contribution has been
removed. Buckets 2 and 3 together show that only Bucket 2 (14,471) can be removed with
evidence; Bucket 3's contribution stays in the list, unlabelled and unmeasurable. An
honest subset — should a human ever rule "publish" — is **"PD minus a lower bound"**,
shipped *with this ledger* stating exactly what could not be subtracted. It is never
"PD-only".

No such subset is built here. Building `build_pd_subset.py` requires the canonical list,
which is not on disk (§3). Even with the list, the tool would emit "PD-minus-a-lower-bound
+ a rights-residue statement", never a bare "PD-only" artifact.

---

## 3. The canonical list is NOT recovered — escalated as data loss

The rights question turns on the *source-code column*, which is documented in
`SCHEMA.md` and reproduced above — so this ledger stands without the list itself. But the
acceptance clause requires the canonical list be "recovered+backed-up or its absence
escalated as data loss". As of this pass:

- **The canonical `266820-reverse-Gasuns.txt` is absent from the repo.**
  [`ACL_DH_COMPATIBILITY_ANALYSIS.md:124`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/ACL_DH_COMPATIBILITY_ANALYSIS.md)
  cites `.doc.pdf/266820-reverse-Gasuns.txt`, but `.doc.pdf/` contains only four `.mdx`
  files plus `Sorting-Samples/` and `Statistica/` dirs — no 266,820-line source file.
- **Recovery is owned by [H736](https://github.com/gasyoun/Uprava/blob/main/handoffs/H736-Fable_SanskritLexicography_reverse-dictionary-dataset-recovery_11.07.26.md)**
  (locate on disk / git history / `.doc` drafts, back up durably, repoint dead links).
  As of 17-07-2026, H736 is **🟡 QUEUED — not executed, no PR** (per the
  [Uprava handoffs registry](https://github.com/gasyoun/Uprava/blob/main/handoffs/README.md)).
- **This ledger does not reconstruct the list.** The 250,026 / 255,882 `.doc` drafts are
  *not* substituted for the canonical 266,820 — a reconstruction of unknown provenance
  masquerading as canonical is a worse outcome than the loss.

**Escalation:** the canonical list is data-loss-at-risk, and **H736 is the owner of that
escalation.** This ledger consumes H736 by naming it; it does not duplicate H736's search.

---

## 4. The residue is unresolvable by agent effort

State this without hedging: **no amount of agent work closes Bucket 3.** The five silent
sources have no marked source-code anywhere in the data. Retrying, widening the search, or
reasoning harder returns the same lower bound every time — the missing information is not
hidden, it was never recorded in this data shape. What closes the gap is **money and a
human decision**: funding per-source headword lists for Stchoupak–Nitti–Renou, Turner,
Mylius, Kochergina, and Pujol, then diffing them against the canonical list. That is a
decision, not a task, and it is out of scope for any agent.

---

## 5. Live exposure flagged (FLAG ONLY — removal is a human call)

[`ReverseDictionary/.doc.pdf/Reverse-Kochergina.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/.doc.pdf/)
(701 KB on disk; 643 KB blob on `origin/master`) is a reverse index derived from
**Kochergina 1978** — an in-copyright source (Bucket 3; Kochergina d. 2018 → RF life+70
~2088) — and it sits on **public `master`** (world-readable). This is an **H734-class
exposure**, consistent with [PR #481](https://github.com/gasyoun/SanskritLexicography/pull/481).

**This ledger FLAGS it only.** Removing the file or purging it from history is a human
decision, made via [`/publish-safety-check`](https://github.com/gasyoun/claude-config/blob/main/commands/publish-safety-check.md);
no file is moved, renamed, or deleted by W1-E.

---

## 6. The decision this hands the human

The GTD `@DECIDE` is sharpened from "publish full vs PD-only vs restricted" to the
question the ledger actually poses:

> The PD-only subset **cannot be certified** on available data — 5 of the 7 clear-risk
> sources (Stchoupak–Nitti–Renou, Turner, Mylius, Kochergina, Pujol) are unmarked, so
> **14,471 / 266,820 is a lower bound**, not a total. Choose one:
> **(i)** fund per-source headword lists for the five silent sources (money + time, the
> only path to a certified subtraction); **(ii)** publish with a stated lower-bound
> caveat (accept that an unknown residue of in-copyright headwords remains, documented);
> or **(iii)** keep the data restricted-tier and publish only the paper + statistics
> (zero legal risk, weakest FAIR score).

Nothing in this ledger pre-empts that ruling. W1-E delivers the position; the human
rules.

---

_Dr. Mārcis Gasūns_
