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

## Bottom line

- **MW or PWG alone → near-print-ready now**: stable spine + clean SLP1 key1/key2 in
  `now-2026/`. The one remaining gate is **A** (file the MW/PWG typos: MW 4, PWG 12).
- **A union, or AP/PWK included → more work**: refresh AP/PWK (done — 2026 set), make the
  scope (E) and coverage (B) calls, resolve accents (C), and clear the larger typo queues
  (SHS 37, YAT 27, ACC 22 …).
- **Only D was agent-doable and is closed.** A, B, C, E are human/editorial decisions —
  A being the highest-value (it literally prevents printing known errors).

_Tracked: gap-D close + this checklist = `now-2026/` key2 + `PRINT_READINESS.md`._
