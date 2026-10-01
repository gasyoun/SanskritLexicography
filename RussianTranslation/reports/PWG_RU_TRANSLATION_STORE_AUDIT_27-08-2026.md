# PWG→RU translation store audit — 27-08-2026

_Created: 27-08-2026 · Last updated: 27-08-2026_

**Handoff:** [H3590](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3590-Fable_RussianTranslation_pwg-ru-translation-store-audit_27.08.26.md) · **Tier:** Fable 5 (`claude-fable-5`) · **Generation tokens spent:** 0 · **Store mutated:** no.

A zero-token audit of the *live* Russian translation store — what actually landed, not what any window claimed. Every deterministic gate the pipeline owns was re-run over the whole store; nothing was sampled. Six findings, three of them integrity-grade.

## 1. What was run

| # | Check | Tool | Scope | Verdict |
|---|---|---|---|---:|
| 1 | Per-row markup gates LS-LOSS / SAN-LOSS / NO-RUSSIAN / identical-target DUP (thresholds from [`markup_fidelity_gates.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/markup_fidelity_gates.py), `check_ab=False` as in the RU path) | [`src/audit_store_gates.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_store_gates.py) (new, this handoff) | 11 620 rows (src) + 11 598 rows (mirror) | **5 hard-flagged rows** (§2) |
| 2 | H3500 defect classes (dup-row excess, cross-subcard identical blocks, degenerate tag copies, `<is>` leaks) | [`src/h3500_defect_scan.py --check`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h3500_defect_scan.py) | src store | **OK** — class1a 0 · class1b 42 (informational) · class1c 53 · class3 13 |
| 3 | Provenance completeness (model version, pipeline stamp, input SHAs, staleness) | [`src/audit_translation_provenance.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_translation_provenance.py) | src store | **clean** — 11 620/11 620 stamped `claude-sonnet-5`, 0 stale, 9 rows missing input SHAs, 69 partial-card rows |
| 4 | src store ↔ `pwg-ru-data/tm/` mirror diff | [`src/audit_store_gates.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_store_gates.py) | both stores | **DRIFT** — +18 ids, 289 rows `ru`-changed (§3) |
| 5 | R4.1 daily spot-check surveillance state | `Get-ScheduledTask` · [`pwg-ru-data/telemetry/`](https://github.com/gasyoun/pwg-ru-data/tree/main/telemetry) | this box | **DISABLED**, 0 `spotcheck_*.json` ever written (§4) |
| 6 | Manifest-mode gate [`src/audit_translation.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_translation.py) on all 8 `scale_manifest.*.json` | as named | 43 968 units | **not runnable here** — 43 797 NO-RAW / 161 NO-OUTPUT; only 298 `.raw.txt` on this checkout (§5) |
| 7 | Review-status census | store | src store | 11 615 `ai_translated` · 3 `approved` · 2 `needs_review` — the G5 human gate is still at ~0 (known, [/pwg-review-packet](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-review-packet.md)) |

## 2. Five rows with genuine content loss are in the store, unqueued

Identical in src and mirror, so they pre-date H3500 and survived every window close. All `review_status='ai_translated'`.

| key1 · subcard · sense_tag | flag | what the RU lost | severity |
|---|---|---|---|
| `dA` · `d_a~~h0_02_sec_2` · `1` | LS-LOSS 29/34, SAN 2 spans | the whole **desiderative head-line**: `{#di/tsati#}` `{#ditsate#}` + `P. 7,4,54.` `58.` `VOP. 19,9.` `P. 7,4,54` (RU starts at «желать дать…») | medium |
| `dA` · `d_a~~h0_05_anu` · `1` | SAN-LOSS 4/6, LS 6/7 | the preverb head `{#anu#}` + `(partic. {#anudatta#} Kār. zu P. 7,4,47)` | medium |
| `mA` · `m_a~~h0_zz_pw03` · `main` (hom. 5) | SAN-LOSS 7/9 | root head `√{#mA#} (√{#mI#})` — the `√mI` variant is lexicographic information | minor |
| `pat` · `pat~~h0_zz_pw00` · `1〉` | SAN-LOSS 0/2 | `√{#pat#}, {#pa/tati#} (episch auch Med.)` — the present stem + epic-middle note | minor |
| `asvatantra` · `asvatantra~~h0_zz_pw` · `1` | SAN-LOSS 1/3 | headword + fem. ending `(f. {#A#})` | minor |

Pattern: **head-line omission**. The translator dropped the lemma/root head and everything riding on it. A single dropped head span is tolerated by the abs-drop≥2 guard and is therefore endemic and invisible; these five are the cases where a second span (grammar citation, present stem, feminine ending) rode along. Note also the sense_tag `1〉` on `pat` — a tagger glyph leak.

**Fix path:** requeue the two medium rows `--no-tm` through a bounded window ([/pwg-window-close](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-window-close.md) guardrail 2); the three minor rows are a G5 reviewer's call. Not done here — the store is not mutated by an audit.

## 3. src store and `pwg-ru-data/tm/` mirror have drifted — 289 rows rewritten by nobody in the repo

| | src [`src/pwg_ru_translated.jsonl`](file:///C:/Users/user/Documents/GitHub/SanskritLexicography/RussianTranslation/src/pwg_ru_translated.jsonl) (gitignored, local-only) | mirror [`pwg-ru-data/tm/pwg_ru_translated.jsonl`](https://github.com/gasyoun/pwg-ru-data/blob/main/tm/pwg_ru_translated.jsonl) |
|---|---|---|
| rows | 11 620 | 11 598 (= H3500's repaired count) |
| mtime | 25-08-2026 23:03 | 25-08-2026 17:25 |
| `<ab>Instr.</ab>` / `<ab>Ins.</ab>` | 239 / 239 | 478 / 0 |

- **+18 ids only in src** — the [H3361](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3361-OxAlpha_pwg-ru-data_advisory-inject-bounded-window_23.08.26.md) window promote (22:40, `Satya`, `balikarman`, `dohya`, `pASupAlya`, …). Legitimate; the mirror simply was not refreshed after the promote.
- **289 same-id rows differ only in `ru`** (309 under the finer row identity `audit_store_gates.py` uses, which also splits the homograph `main` blocks): 204 are exactly `<ab>Instr.</ab>`→`<ab>Ins.</ab>`; the other 105 are the same family — `Akk.`→`Acc.`, `Instr.`→`Ins.`, trailing-dot insertions — concentrated in `zz_nws`/`zz_sch`/`zz_pw` sub-cards of `Cid`, `Sam`, `brU`, `gA`, `diS`, `DA`, `Bid`, `Ap`, `Buj`. A **German→Latin case-label normalisation applied to exactly half** of the `Instr.` occurrences.
- **No script in SanskritLexicography, pwg-ru-data or the H3361 window dir writes `Ins.`.** The repo's own canon runs the *other* way: [`pwg_ab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab.py) `RENAME_ALIASES = {'Ins.': 'Instr.'}` and the abbreviation tooltip table is keyed `Instr.` (CHANGELOG, H1308). So 239 occurrences moved **away** from canonical, by an unidentified writer, between 17:25 and 23:03 on 25-08-2026. Render is unaffected (the alias maps back), but the store is no longer uniform and the mirror no longer matches.

Recorded as [GAPS §16](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md). **A human should decide** which label is canonical in the store before either (a) the mirror is refreshed from src (cementing the half-rewrite) or (b) src is re-normalised to `Instr.` from the mirror.

## 4. The R4.1 halt rule has never fired — and could not see §2 anyway

1. Task Scheduler on this box: **`PWG-RU spotcheck pc lane` — Disabled**, `PWG-RU nonstop pc lane` — Disabled. [`pwg-ru-data/telemetry/`](https://github.com/gasyoun/pwg-ru-data/tree/main/telemetry) holds **zero** `spotcheck_*.json`. The control H2264 wired (after H2246 found it never fired) is dead again. Run by hand for 25-08: `population=0 sampled=0` — its sample frame is `*.PROMOTED.json` auto-promotion records, which the supervised H3361 window does not emit, so even enabled it would have audited nothing that day.
2. `store_san_loss_scan()` in [`src/pilot/spot_check_daily.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/spot_check_daily.py) implements "ANY SAN-LOSS reaching the store" as a **regex for a literal `SAN-LOSS`/`UNMAPPED` marker string** in `ru`. It never recomputes `{#…#}` span preservation. The four SAN-LOSS rows of §2 return `san_loss_in_store=False`. The unconditional freeze trigger is a marker grep, not a gate — [FINDINGS §589](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).

## 5. Manifest-mode `audit_translation.py` is a window tool, not a store audit

Default and manifest modes resolve `<stem>.raw.txt` under `src/pilot/input/` (298 present) and `<stem>.merged.md` under `src/pilot/output/`; on this checkout 43 797 of 43 968 manifest units are NO-RAW. A `FAIL: 0/38 units clean` on `scale_manifest.freqtest.json` here is an artefact of missing inputs, not a translation verdict. Use it only with `--wf <wf_output.json>` inside a window; use [`src/audit_store_gates.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_store_gates.py) for the store.

## 6. Reproduce

```powershell
cd C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation
python src\audit_store_gates.py                       # src store gates + mirror diff (exit 1 on any hard flag)
python src\h3500_defect_scan.py --check
python src\audit_translation_provenance.py
python src\pilot\spot_check_daily.py --selftest
```

## 7. What this audit did not do

- No judge / fidelity scoring of *meaning* (that is the G5 sheet, [/pwg-review-packet](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-review-packet.md)); every check here is deterministic.
- No store or mirror mutation, no requeue, no scheduler change.
- The 1 966 soft `MARKUP-LOSS` flags (wrapper tags dropped) were counted, not triaged.

_Dr. Mārcis Gasūns_
