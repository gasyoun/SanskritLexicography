# H2489 — Flash PREP 200-key spike + Opus token/defect compare

_Created: 08-08-2026 · Last updated: 08-08-2026_

**Status:** measured (offline fill + free det_gate; **no TM write**; **no paid Opus/Flash call** this pass).

**Executor:** Grok 4.5 (`grok-4.5`) · handoff [H2489](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2489-Grok_SanskritLexicography_flash-prep-200-spike_08.08.26.md)

**Map:** [DEEPSEEK_V4_FLASH_0731_ORG_LANE_MAP_2026-08.md](https://github.com/gasyoun/Uprava/blob/main/docs/DEEPSEEK_V4_FLASH_0731_ORG_LANE_MAP_2026-08.md) §3.1 step [2] → free det_gate → router.

---

## What ran

```text
python src/pilot/h1210/prep_pack.py \
  --worklist src/pilot/h1210/H2489_spike200_worklist.08.08.26.json \
  --limit 200 \
  --store <canonical pwg_ru_translated.jsonl> \
  --input-dir <pilot/input> \
  --out-dir prep/spike200
```

- Mode: **fill** (store + DE raw + sense inventory + TM fuzzy rank + hard flags + free det_gate).
- **Not** `--live` Flash draft for all 200 (handoff out-of-scope unless budget residual).
- Worklist: 100 H1210 AB keys + 100 store-extend keys → 200 unique `key1`.
- Bulk dir: local `RussianTranslation/prep/spike200/` (**gitignored**). Stratified samples: [`prep_samples_h2489/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/prep_samples_h2489/).
- Machine stats: [`H2489_SPIKE200_STATS.08.08.26.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1210/H2489_SPIKE200_STATS.08.08.26.json).

`prep_pack.py --selftest` → **PASS** (fill + free det_gate no-Claude + R4.3a fence).

### Filename fix (same pass)

`write_pack` now uses `safe_filename.safe_name` so Windows case-insensitive FS does not clobber `DA` / `dA` (or `viD` / `vid`). First run without the fix left **198** files; after the fix, **200** unique sidecars.

---

## Sidecar census (n = 200)

| Metric | Count | % |
|---|---:|---:|
| sidecars written | 200 | 100 |
| with non-empty `sense_inventory` | 110 | **55.0** |
| free `det.ok` | 110 | **55.0** |
| free `det` fail | 90 | 45.0 |
| route `park` | 90 | **45.0** |
| route `controller_only` | 51 | 25.5 |
| route `full_worker` | 54 | 27.0 |
| route `prep_only` | 5 | 2.5 |
| any `tm_fuzzy_hits` | 135 | 67.5 |
| hard flag `no_pwg` | 90 | 45.0 |
| hard flag `monster_length` | 48 | 24.0 |
| hard flag `polysemy` | 61 | 30.5 |
| `tm_fence.may_write=false` | 200 | **100** |
| `store_write=true` | 0 | 0 |
| `det.claude=true` | 0 | 0 |

Sense inventory: total 2418 · median 2 · mean 12.09 (store multi-row keys pull the mean up).

**Park interpretation:** almost all parks are honest `no_pwg` / empty DE on this pilot store+input slice — not a Flash quality claim. Prep's job is early route, not inventing DE.

---

## Opus window compare (offline proxy — no paid call)

Stratified **n=8** window (2× each of controller_only / full_worker / park / prep_only):

Keys: `Adika`, `AmarSa`, `Ap`, `As`, `BaYj`, `Badramusta`, `Srama`, `dIkzA`.

Token proxy = `chars // 4` (not a billed tokenizer). Defect proxy = free `route_hint` / `det` available **before** Opus vs unknown-all-full-worker baseline.

| Arm | Context chars | tok≈ | tok/card≈ | Defect / route proxy |
|---|---:|---:|---:|---|
| **Baseline (no prep)** | 167 | 41 | **5** | all 8 unknown → assume **8 full_worker** |
| **Compact prep seed** (recommended) | 4942 | 1235 | **154** | 2 controller_only · 2 full_worker · 2 park · 2 prep_only · det.ok 6/8 |
| Full sidecar dump (anti-pattern) | 46151 | 11537 | 1442 | same routes; ~9× compact cost |

### Read of the table

1. **Prep is not free on the Opus context budget.** Compact seed ≈ **+149 tok/card** vs key-only baseline on this window. That is the price of route + sense + TM rank + flags.
2. **Full sidecar inject is the wrong shape** (~1442 tok/card on this sample) — use compact seed (`n_senses`, anchors head, tm_top, flags, det), not the whole JSON.
3. **Defect / spend proxy (window):** baseline sends **8/8** to full worker by default; with prep, **2/8 park early** (no Opus), **2/8 controller_only** (cheap accept path), **2/8 full_worker** still needed, **2/8 prep_only**. That is the product win of step [2] — not lower tokens on the cards Opus still does, but **fewer cards Opus must fully work**.
4. **Not claimed:** E1 production win, shippable%, or paid controller quality. H2488 owns paid bulk; this spike only sizes prep→router inputs.

---

## R4.3a fence (samples)

On all 200 sidecars and on every committed sample under `prep_samples_h2489/`:

- `tm_fence.may_write` = **false**
- `tm_fence.writer` = `promoter_only`
- `store_write` = **false**
- `det.claude` = **false**

Reproduce: `python -c "… assert not p['tm_fence']['may_write'] …"` over `prep/spike200` or the sample dir.

---

## Reproduce

```text
cd RussianTranslation
python src/pilot/h1210/prep_pack.py --selftest
python src/pilot/h1210/prep_pack.py \
  --worklist src/pilot/h1210/H2489_spike200_worklist.08.08.26.json \
  --limit 200 \
  --store ../src/pwg_ru_translated.jsonl \
  --input-dir src/pilot/input \
  --out-dir prep/spike200
# then re-derive stats from prep/spike200 (or trust H2489_SPIKE200_STATS.08.08.26.json)
```

---

## Non-claims / residual

- No Flash `--live` draft for 200 keys (budget residual → H2488 shape).
- No paid Opus controller window; token numbers are **offline proxies**.
- Store is pilot-scale (~254 keys in this jsonl) — park rate is data-slice dependent.
- Compact-seed builder is not yet a first-class `prep_pack` CLI export (manual in this memo/stats); residual if controller wiring needs it as a flag.

_Dr. Mārcis Gasūns_
