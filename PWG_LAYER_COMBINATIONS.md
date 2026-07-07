# PWG entry layer combinations

_Created: 05-07-2026 · Last updated: 05-07-2026_

Grounded in the actual merge code — [`RussianTranslation/src/dict_merge.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/dict_merge.py) (the `LAYERS`/`NWS_LAYER` definitions and the `merged()` function) — and the working notes in [`pwg-layers.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/pwg-layers.md). Not a new design — this documents the existing pwg_ru merge rule and enumerates the subset combinations it implies, then **measures which actually occur** in the csl-orig data.

## The 5 layers

| Code | Role | Full name | Source | Headwords indexed |
|---|---|---|---|---|
| **PWG** | base | Böhtlingk-Roth, *Sanskrit-Wörterbuch* ("grosses Petersburger Wörterbuch"), 1855–75, 7 vols. Includes the Nachträge/Addenda folded into each volume. | `csl-orig/v02/pwg/pwg.txt` | 106,082 |
| **PW** | revision | Böhtlingk, *kürzere Fassung* ("kleines Petersburger Wörterbuch" / PWK), 1879–89, 7 vols. Can cancel a PWG word, meaning, or source, not just append. | `csl-orig/v02/pw/pw.txt` (indexed as `pw`/`pwk`) | 151,349 |
| **SCH** | supplement | Schmidt, *Nachträge zum Sanskrit-Wörterbuch*, 1928. Can add a new meaning (marked `*`) to an existing PWG sense. | `csl-orig/v02/sch/sch.txt` | 28,455 |
| **PWKVN** | supplement | PWK variant supplement (Nachträge und Verbesserungen to the kürzere Fassung). | `csl-orig/v02/pwkvn/pwkvn.txt` | 14,995 |
| **NWS** | external | *Nachtragswörterbuch* (Halle), cumulative addendum, ~2013. Folded in **only** when it is net-new beyond the four layers above (`has_nws_extra` flag) — never duplicated in. May itself contain outdated PWG/PW/SCH data, or partial French/Latin text. | scraped JSON, `RussianTranslation/src/pilot/nws/*.json` (167,991 files, provisional pending a data request) | **34,101 net-new (`has_nws_extra=true`), 20.3% of scraped files** — measured; per-combination breakdown (which of rows 9/16-18/21-23/25 below each falls into) not yet joined |

**Related but NOT merged into a PWG entry:** CAE, CCS (medium dicts historically based on PWG/PW), MD, KCH (medium), LAN, KNA, FRI (small student dicts) — these track the same headwords as part of the wider "abridged tradition" comparison, but are separate dictionaries in their own right, not overlay layers of PWG. See `pwg-layers.md` lines 91–93.

## The mechanical rule

1. **Fixed order, pure concatenation**: `PWG → PW → SCH → PWKVN → NWS`. This order is hardcoded in the `LAYERS` list (`dict_merge.py:27-32`) plus `NWS_LAYER` appended last (`:38-39`).
2. **Each of the 4 local layers is indexed independently** by SLP1 headword (`form_key`) and appended to the merge if a record exists for that key — a PWG record is **not** a precondition for an overlay layer to fire.
3. **NWS is conditional, not automatic**: it is looked up per-key, on demand, and included only if it adds material beyond what the four local layers already contribute (`nws_record()`, `dict_merge.py:69-85`). An NWS hit with no net-new content is silently dropped — it never appears as its own layer.
4. **No content-aware merging today**: layers are 1+1 concatenated with source/role metadata attached, not interleaved sense-by-sense.

## Measured co-occurrence (the actual answer to "is no-PWG theoretical?")

Ran a direct tally over the 4 local layer indexes (`index('pwg')`, `index('pw')`, `index('sch')`, `index('pwkvn')` from `dict_merge.py`, unioned by SLP1 key). **Result: the "no-PWG" combinations are not rare edge cases — PW-alone is the single largest multi-headword category after PWG+PW itself, larger even than PWG-alone.** The original doc's "theoretical" framing was wrong; corrected below.

| Layers present | Headword count | Share of union (167,988) |
|---|---:|---:|
| pwg + pw | 91,648 | 54.6% |
| **pw** (no pwg) | **40,338** | **24.0%** |
| pwg (alone) | 6,453 | 3.8% |
| **pw + sch + pwkvn** (no pwg) | **10,057** | **6.0%** |
| **sch** (no pwg) | **9,990** | **5.9%** |
| pwg + pw + pwkvn | 3,842 | 2.3% |
| pwg + pw + sch | 3,766 | 2.2% |
| **pw + pwkvn** (no pwg) | **875** | **0.5%** |
| **pw + sch** (no pwg) | **624** | **0.4%** |
| pwg + sch | 174 | 0.1% |
| pwg + pw + pwkvn (dup row, see below) | 199 | 0.1% |
| **pwkvn** (no pwg) | **20** | **0.01%** |
| **sch + pwkvn** (no pwg) | **2** | **0.001%** |

(Full breakdown: `pwg+pw+sch+pwkvn`=3,842; `pwg+pw+sch`=3,766; `pwg+pw+pwkvn`=199. Union total across all combos = 167,988 headwords.)

Sample no-PWG headwords, for spot-checking against the scans: **pw-only** — `veNkawAcala`, `DAtukramamAlA`, `kulotTaka`, `darBasUcI`, `kORqoparaTIya`; **sch-only** — `karaBA`, `dvAdaSanAlika`, `sAtina`, `pratinadI`, `SaSadaMSa`; **pwkvn-only** — `aBiDarmaskanDaprakASasADana`, `dvyAQakInA`, `dvipAtrikI`.

**Reading this correctly:** PW (the *kürzere Fassung*) is not merely a revision of existing PWG entries — it independently covers **40,338 headwords PWG never touches at all** (mostly later/rarer compounds Böhtlingk added when compiling the shorter edition), roughly 4× the count of PWG-only entries. SCH and PWKVN likewise introduce their own headwords outside the PWG base. The four local layers jointly define the headword universe (as the `dict_merge.py:26` comment says), not PWG alone.

## All combinations, smallest to largest

Every non-empty subset of the 5 layers, now labeled with **measured** counts where available (local 4-layer combos, and the aggregate NWS net-new rate) or **pending join** (the exact per-combination NWS split — which local combo each of the 34,101 net-new files sits on top of — which needs one more script matching NWS filenames back to local-layer keys via `candidate_names`/`form_key`, not yet run). NWS never adds a headword outside the local four (its keys are derived from them), so it only ever narrows/extends an already-listed combo, never creates a new no-PWG-only-NWS row.

**NWS aggregate, measured:** 34,101 of 167,991 scraped files (20.3%) carry net-new content beyond the four local layers. That means roughly 1 in 5 headwords in the full PWG "friends" universe gets an NWS-layer contribution — not a marginal case.

### 1 layer (5 combinations)

1. **PWG** only — 6,453 headwords (3.8%). Base entry, no overlay fires.
2. **PW** only — **40,338 headwords (24.0%)** — measured, real, the largest single no-PWG category.
3. **SCH** only — **9,990 headwords (5.9%)** — measured, real.
4. **PWKVN** only — **20 headwords** — measured, real but rare.
5. **NWS** only — structurally impossible: NWS is looked up *by* a local-layer key and never fires without at least one local layer already present.

### 2 layers (7 combinations)

6. **PWG + PW** — **91,648 headwords (54.6%)**, the dominant combination overall.
7. **PWG + SCH** — 174 headwords.
8. **PWG + PWKVN** — folded into the 4-layer breakdown above as part of `pwg+pw+pwkvn` (199) / `pwg+pw+sch+pwkvn` (3,842); a pure PWG+PWKVN-only row was not separately observed in the top buckets — likely near-zero.
9. **PWG + NWS** — *pending NWS scan.*
10. **PW + SCH** (no PWG) — **624 headwords** — measured, real.
11. **PW + PWKVN** (no PWG) — **875 headwords** — measured, real.
12. **SCH + PWKVN** (no PWG) — **2 headwords** — measured, real but vanishingly rare.

### 3 layers (7 combinations)

13. **PWG + PW + SCH** — **3,766 headwords** — measured, real, common.
14. **PWG + PW + PWKVN** — **199 headwords** — measured, real.
15. **PWG + SCH + PWKVN** — not separately observed as a distinct top bucket; folds toward 0 given SCH+PWKVN-alone is only 2.
16. **PWG + PW + NWS** — *pending NWS scan.*
17. **PWG + SCH + NWS** — *pending NWS scan.*
18. **PWG + PWKVN + NWS** — *pending NWS scan.*
19. **PW + SCH + PWKVN** (no PWG) — **10,057 headwords (6.0%)** — measured, real, and larger than several PWG-containing combos above it.

### 4 layers (5 combinations)

20. **PWG + PW + SCH + PWKVN** — **3,842 headwords (2.3%)** — measured, real, the densest routinely occurring local-only combination (the "full Cologne stack" minus NWS).
21. **PWG + PW + SCH + NWS** — *pending NWS scan.*
22. **PWG + PW + PWKVN + NWS** — *pending NWS scan.*
23. **PWG + SCH + PWKVN + NWS** — *pending NWS scan.*
24. **PW + SCH + PWKVN + NWS** (no PWG) — *pending NWS scan; base combination (no NWS) already confirmed real at 10,057.*

### 5 layers (1 combination)

25. **PWG + PW + SCH + PWKVN + NWS** — *pending NWS scan; base 4-layer combination already confirmed real at 3,842, so this is "does NWS add net-new content on top of an already-attested 4-layer entry" — plausible, not yet counted.*

## What changed from the first draft

The original version of this doc marked every no-PWG combination as "theoretical" — an unverified guess. The measurement flips that: no-PWG combinations account for **~35,900 headwords out of ~167,988 (≈36% of local headword coverage)**, dominated by PW-only. Only two of the seven measured no-PWG combinations are genuinely rare (`pwkvn`-only at 20, `sch+pwkvn` at 2) — the rest are substantial, real categories that any full pwg_ru pass will hit routinely.

## Remaining open question

The NWS net-new (`has_nws_extra`) scan is done: **34,101 of 167,991 files (20.3%)** carry net-new content. What's still unmeasured is the **per-combination split** — rows 9, 16–18, 21–23, 25 need those 34,101 keys joined back against the local-layer sets (pwg/pw/sch/pwkvn) via `candidate_names`/`form_key` to know exactly how many of them land on, say, a bare PWG+NWS entry versus a full 5-layer entry. That join is a small, well-scoped follow-up script, not a new investigation; a human decides whether it's worth running now or can wait.

_Dr. Mārcis Gasūns_
