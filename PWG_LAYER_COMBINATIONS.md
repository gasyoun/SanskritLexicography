# PWG entry layer combinations

_Created: 05-07-2026 · Last updated: 05-07-2026_

Grounded in the actual merge code — [`RussianTranslation/src/dict_merge.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/dict_merge.py) (the `LAYERS`/`NWS_LAYER` definitions and the `merged()` function) — and the working notes in [`pwg-layers.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/pwg-layers.md). Not a new design — this documents the existing pwg_ru merge rule and enumerates the subset combinations it implies.

## The 5 layers

| Code | Role | Full name | Source |
|---|---|---|---|
| **PWG** | base | Böhtlingk-Roth, *Sanskrit-Wörterbuch* ("grosses Petersburger Wörterbuch"), 1855–75, 7 vols. Includes the Nachträge/Addenda folded into each volume. | `csl-orig/v02/pwg/pwg.txt` |
| **PW** | revision | Böhtlingk, *kürzere Fassung* ("kleines Petersburger Wörterbuch" / PWK), 1879–89, 7 vols. Can cancel a PWG word, meaning, or source, not just append. | `csl-orig/v02/pw/pw.txt` (indexed as `pw`/`pwk`) |
| **SCH** | supplement | Schmidt, *Nachträge zum Sanskrit-Wörterbuch*, 1928. Can add a new meaning (marked `*`) to an existing PWG sense. | `csl-orig/v02/sch/sch.txt` |
| **PWKVN** | supplement | PWK variant supplement (Nachträge und Verbesserungen to the kürzere Fassung). | `csl-orig/v02/pwkvn/pwkvn.txt` |
| **NWS** | external | *Nachtragswörterbuch* (Halle), cumulative addendum, ~2013. Folded in **only** when it is net-new beyond the four layers above (`has_nws_extra` flag) — never duplicated in. May itself contain outdated PWG/PW/SCH data, or partial French/Latin text. | scraped JSON, `RussianTranslation/src/pilot/nws/*.json` (provisional, pending a data request) |

**Related but NOT merged into a PWG entry:** CAE, CCS (medium dicts historically based on PWG/PW), MD, KCH (medium), LAN, KNA, FRI (small student dicts) — these track the same headwords as part of the wider "abridged tradition" comparison, but are separate dictionaries in their own right, not overlay layers of PWG. See `pwg-layers.md` lines 91–93.

## The mechanical rule

1. **Fixed order, pure concatenation**: `PWG → PW → SCH → PWKVN → NWS`. This order is hardcoded in the `LAYERS` list (`dict_merge.py:27-32`) plus `NWS_LAYER` appended last (`:38-39`).
2. **PWG is queried first**; PW, SCH, PWKVN are each independently indexed by SLP1 headword (`form_key`) and appended if a record exists for that key — a PWG record is not required for an overlay layer to fire (each of the four local layers is indexed independently in `records_of`/`index`), though in practice most non-PWG-only combinations have not been separately audited for frequency.
3. **NWS is conditional, not automatic**: it is looked up per-key, on demand, and included only if it adds material beyond what the four local layers already contribute (`nws_record()`, `dict_merge.py:69-85`). An NWS hit with no net-new content is silently dropped — it never appears as its own layer.
4. **No content-aware merging today**: layers are 1+1 concatenated with source/role metadata attached, not interleaved sense-by-sense. Each overlay layer is retrievable by its own key later (subcard suffix `_zz_<layer>`), so a future re-glue into a content-aware combination is possible without re-translating — see `pwg-layers.md` lines 69, 73.

## All combinations, smallest to largest

Every non-empty subset of the 5 layers, grouped by size. "Real" = attested by the merge code as a live, expected case; "theoretical" = structurally possible per the code (an overlay layer firing without PWG) but not confirmed to occur in the actual data.

### 1 layer (5 combinations)

1. **PWG** — the plain base entry, no overlay fires. The overwhelming majority case.
2. **PW** only — a PW-only headword with no matching PWG record. *Theoretical.*
3. **SCH** only — a Schmidt supplement entry with no PWG match. *Theoretical.*
4. **PWKVN** only — *theoretical.*
5. **NWS** only — structurally impossible under the current code: NWS is looked up *by* the local-layer key and never fires without at least one local layer already matching, so this combination cannot occur as coded.

### 2 layers (7 combinations, since PWG+NWS-alone needs NWS conditional on PWG only — listed where plausible)

6. **PWG + PW** — the classic case: Böhtlingk revised his own entry in the shorter edition.
7. **PWG + SCH** — Schmidt added a `*`-marked new meaning to an existing PWG sense.
8. **PWG + PWKVN** — a PWK-supplement correction on top of the PWG base.
9. **PWG + NWS** — Halle added net-new material directly on the PWG base, with no PW/SCH/PWKVN layer present.
10. **PW + SCH** — *theoretical* (no PWG match, but both overlays present).
11. **PW + PWKVN** — *theoretical.*
12. **SCH + PWKVN** — *theoretical.*

### 3 layers (7 combinations, real ones first)

13. **PWG + PW + SCH** — base, revision, and Schmidt supplement all present — a common "real" 3-layer entry.
14. **PWG + PW + PWKVN** — base + revision + its own variant supplement.
15. **PWG + SCH + PWKVN** — base plus both supplement layers, no revision.
16. **PWG + PW + NWS** — base + revision, with Halle contributing net-new material beyond both.
17. **PWG + SCH + NWS** — base + Schmidt, with NWS adding beyond Schmidt.
18. **PWG + PWKVN + NWS** — base + PWK-variant, with NWS net-new on top.
19. **PW + SCH + PWKVN** — *theoretical* (all three secondary layers, no PWG hit).

### 4 layers (5 combinations)

20. **PWG + PW + SCH + PWKVN** — the "full Cologne stack" with no NWS contribution — base plus all three local overlays. Likely the densest *routinely occurring* combination.
21. **PWG + PW + SCH + NWS** — full local stack minus PWKVN, plus Halle net-new.
22. **PWG + PW + PWKVN + NWS** — full local stack minus SCH, plus Halle net-new.
23. **PWG + SCH + PWKVN + NWS** — full local stack minus PW, plus Halle net-new.
24. **PW + SCH + PWKVN + NWS** — *theoretical*, no PWG hit at all.

### 5 layers (1 combination)

25. **PWG + PW + SCH + PWKVN + NWS** — the maximal entry: base, revision, both supplements, and a net-new Halle contribution, all five layers present. The richest possible pwg_ru source card.

## Open question this doesn't answer

Whether the "theoretical" 1–2–3-layer combinations that omit PWG (rows 2–5, 10–12, 19, 24) actually occur in the csl-orig data, or whether PWG in practice defines the entire headword universe and the other three local layers only ever fire alongside it, has not been measured — `dict_merge.py cmd_stats` reports per-layer headword counts but not the co-occurrence matrix across layers. Running `python dict_merge.py stats` plus a small co-occurrence tally would settle it; a human decides whether that measurement is worth doing now versus deferring alongside the other open pwg-layers.md brainstorm items.

_Dr. Mārcis Gasūns_
