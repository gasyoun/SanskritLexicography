# Print-readiness of the CDSL headword lists (2026)

Can we publish a **printed final list of headwords** now? **Not yet — but the
Monier-Williams / Petersburg spine is close.** Everything outstanding is
human/editorial, except gap **D** (key2 re-extraction), which is now **done**.

This consolidates the checks surfaced by the 2014↔2026 drift study
([NOW_VS_THEN.md](NOW_VS_THEN.md)), the coverage studies
([Catalan-Pujol](Catalan-Pujol/Sanskrit-Catalan-Wordlist-vs-Cologne.md),
[Huet/INRIA](Huet-INRIA-Wordlist-vs-Cologne.md)), and the headword triage in
[`SanskritSpellCheck`](https://github.com/gasyoun/SanskritSpellCheck).

## What 2014 → 2026 tells us

The headword **spine is stable and the changes are additive** (key1 overlap 97–99.9 %
— almost every 2014 headword still exists). Growth is very uneven:

| dict | 2014 → 2026 (key1) | growth | print verdict |
|---|---|--:|---|
| **MW** | 193,978 → 194,084 | **+0.1 %** | **stable — print-ready spine** |
| **PWG** | 106,085 → 106,082 | **−0.0 %** | **stable — print-ready spine** |
| GRA | 10,315 → 11,108 | +7.7 % | minor drift |
| VCP | 47,107 → 48,636 | +3.2 % | minor drift |
| SKD | 40,551 → 40,817 | +0.7 % | minor drift |
| VEI | 3,703 → 3,704 | +0.0 % | stable |
| PWK | 131,918 → 151,349 | **+14.7 %** | **refresh before print** |
| AP | 36,030 → 88,867 | **+146.6 %** | **re-digitised — must use the 2026 set** |

So a **2014 list is already stale** (+21.1 % across the 9 comparable lists,
605,813 → 733,617); a print must be cut from a **dated, versioned 2026 snapshot**
([`now-2026/`](now-2026/)), not "the list".

## The checklist (A–E)

| | Check | Status | Owner |
|---|---|---|---|
| **A** | **Headword correctness** — clear SanskritSpellCheck's **122 fileable suspect typos** across 11 dicts (SHS 37, YAT 27, ACC 22, PWG 12, MCI 10, MW 4, SKD 3, WIL 3, PW 2, VCP 1, GST 1): verify against the scans, flip `n`→`y`, file to CORRECTIONS. *This is the "don't print known typos" pass.* | ⬜ **open — highest value** | **human** (verify vs scan) |
| **B** | **Coverage decision** — whether to add the corpus-attested lexemes absent from CDSL ([177 from Pujol](Catalan-Pujol/DCS-attested-no-CDSL.md), esp. plant/animal names; + Huet's set). | ⬜ open | **human / editorial** |
| **C** | **Accents** — resolve the ~3 % accent-position disagreements (Pujol vs GRA/MW, [§7](Catalan-Pujol/Sanskrit-Catalan-Wordlist-vs-Cologne.md), e.g. *bhága*) if the book prints udātta. | ⬜ open | **human** (canonical = RV/GRA) |
| **D** | **key2 as SLP1** — the print/citation form (accents, compound markers). The 2014 key2 was legacy numeric. | ✅ **done** — clean SLP1 key2 in [`now-2026/`](now-2026/) | agent (done) |
| **E** | **Scope** — single dict (MW or PWG — the ready ones) or a cross-dict **union**? If union, settle dedup/homograph merge across dicts. | ⬜ open | **human / editorial** |
| **F** | **Alternate & feminine headword policy** — how to treat feminine stems and variant/alternate spellings (see below). | ⬜ open | **human policy** (agent can pre-list) |

## F — alternate & feminine headwords (detail)

A printed list must decide *what counts as one headword*, and CDSL itself is
inconsistent here — so this is its own gate.

**Feminines.** In MW (2026) **~14 % of headwords are ā/ī-stems** — 18,186 `-ā`
(9.4 %) + 9,148 `-ī` (4.7 %), largely feminines. CDSL headwords them *unevenly*:
only **24 %** of the `-ā` feminines have their masculine `-a` base as a separate
headword, and of 803 `-inī` feminines only **237 (~30 %)** also headword the `-in`
masculine. Pujol and INRIA-Huet instead give feminines their own line (Pujol
convention §8: `ajitā-`, `vairiṇī-`, `vyāpinī-`), and the DCS corpus attests
feminines CDSL omits ([§5 residue](Catalan-Pujol/DCS-attested-no-CDSL.md)). Decision:
- **(a)** headword every attested feminine separately (comprehensive index), or
- **(b)** fold under the masculine with a `mf(ā/ī)` marker (learner's edition), or
- **(c)** inherit CDSL's as-is inconsistency — *not advisable for print*.

**Alternate spellings / variants.** Orthographic variants (b~v ≈ 397 MW pairs,
ś~ṣ, single~geminate), sandhi variants, and the **same lemma under several `<k2>`
forms** (comma-lists in SKD/VCP/… — the `now-2026/` key2 extraction splits these
into separate lines, so true alternates currently appear as distinct entries; MW
has none, so the MW/PWG spine is unaffected). A print list needs a
lemma→alternates grouping ("see X"), not silent duplication.

**What's agent-doable:** generate the candidate lists — feminine↔masculine pairs,
b~v / ś~ṣ variant pairs, and the multi-`<k2>` alternate groups — for the editor to
rule on. The *policy* (a/b/c, and merge-vs-list) is human. For the **MW/PWG spine**
this is small (MW key2 is one clean form per entry); it bites mainly for a union (E).

## Bottom line

- **MW or PWG alone → near-print-ready now**: stable spine + clean SLP1 key1/key2 in
  `now-2026/`. The one remaining gate is **A** (file the MW/PWG typos: MW 4, PWG 12).
- **A union, or AP/PWK included → more work**: refresh AP/PWK (done — 2026 set), make the
  scope (E), coverage (B), and alternate/feminine (F) calls, resolve accents (C), and clear
  the larger typo queues (SHS 37, YAT 27, ACC 22 …).
- **Only D was agent-doable and is closed.** A, B, C, E, F are human/editorial decisions
  (agent can pre-list candidates for B/C/F) — A being the highest-value (it literally
  prevents printing known errors).

_Tracked: gap-D close + this checklist = `now-2026/` key2 + `PRINT_READINESS.md`._
