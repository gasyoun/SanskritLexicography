# H2675 — W1 Flash PREP `--live` 5k drain-head (first-200 gate)

_Created: 14-08-2026 · Last updated: 14-08-2026_

**Verdict: first-200 PASS; 5k honest stop.** Drain-head worklist of 5 000 live-DE keys. First 200 `--live` sidecars: **200/200** written, skeleton JSON parse **200/200 (100 %)**, `finish_reason=length` **0**, `store_write` never, `tm_fence.may_write` never. Cap **32768** via the [H2674 (Grok 4.6) — W0 OpenAI SDK stream + 32k cap + PRICE after-1608](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2674-Grok_SanskritLexicography_deepseek-w0-openai-stream-price_13.08.26.md) client. Scale-out started after D15 (43 extra sidecars) then stopped: a full 5 000 is ~4 h wall at this card time and this session cannot hang.

Spend-auth: H2675 first-party DeepSeek, no USD cap. Every call in JSONL. Thinking effort was **not** set (`reasoning_effort=null`); Flash still emitted reasoning tokens. `$/card` **$0.000873** (first 200, `pre-1608` Flash table) — well under the $0.04 cost-stop.

## Drain-head

| Item | Value |
|---|---|
| Order | [`pwg_freq_order.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_freq_order.tsv) |
| Live DE | `assembled_cards.jsonl` non-empty `de_skeleton` (106 082 keys) |
| Filter | no existing PREP sidecar |
| `--manifest-authoritative` | yes |
| Worklist | [`H2675_drain_head_5k.worklist.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2675_w1_prep/H2675_drain_head_5k.worklist.json) |
| n / monsters | 5 000 / 59 (25 in first 200) |
| Existing sidecars skipped | 13 |
| First 20 | `ca tad na mad eva yad iti idam api BU sarva vac as etad taTA tatas hi vA rAjan iva` |

Inventory: [`H2675_drain_head.inventory.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2675_w1_prep/H2675_drain_head.inventory.json).

## First 200 (logged before any scale-out)

| Metric | Value |
|---:|---:|
| Sidecars | **200 / 200 (100 %)** |
| Parse ok (not `length`) | **200 / 200 (100 %)** |
| `finish_reason=length` | 0 |
| Null transport | 0 |
| `store_write=true` | **0** |
| `tm_fence.may_write=true` | **0** |
| Route `park` / `full_worker` | 102 / 98 |
| USD (sidecar `live_call`) | **$0.1746** |
| USD / card | **$0.000873** |
| Reasoning tokens (model default) | 568 486 |
| `max_tokens` | 32768 |
| Model | `deepseek-v4-flash` |
| Price card | `pre-1608` |
| Transport | `openai-sdk-stream` |

Stats: [`first200.stats.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2675_w1_prep/first200.stats.json).  
JSONL (one row per key, last successful call): [`calls.first200.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2675_w1_prep/calls.first200.jsonl).

D15 holds on the first 200. D22 therefore **allowed** scale-out.

## Sample sidecar paths (20)

Bulk dir is gitignored ([`RussianTranslation/prep/`](https://github.com/gasyoun/SanskritLexicography/blob/master/.gitignore)). Paths on the H2675 worktree:

- `RussianTranslation/prep/h2675/ca.json`
- `RussianTranslation/prep/h2675/tad.json`
- `RussianTranslation/prep/h2675/na.json`
- `RussianTranslation/prep/h2675/mad.json`
- `RussianTranslation/prep/h2675/eva.json`
- `RussianTranslation/prep/h2675/yad.json`
- `RussianTranslation/prep/h2675/iti.json`
- `RussianTranslation/prep/h2675/idam.json`
- `RussianTranslation/prep/h2675/api.json`
- `RussianTranslation/prep/h2675/_b_u.json`
- `RussianTranslation/prep/h2675/sarva.json`
- `RussianTranslation/prep/h2675/vac.json`
- `RussianTranslation/prep/h2675/as.json`
- `RussianTranslation/prep/h2675/etad.json`
- `RussianTranslation/prep/h2675/ta_t_a.json`
- `RussianTranslation/prep/h2675/tatas.json`
- `RussianTranslation/prep/h2675/hi.json`
- `RussianTranslation/prep/h2675/v_a.json`
- `RussianTranslation/prep/h2675/r_ajan.json`
- `RussianTranslation/prep/h2675/iva.json`

Committed samples (fence + `parse_ok` only): [`samples/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2675_w1_prep/samples/).

## Scale-out and honest stop

After the gate, `fill_one` was fixed so an execution-manifest DE skeleton (no `--- masked German ---` wrapper) builds real `de_anchor`s instead of `null`. First-200 Flash parked 102/200 complaining of empty DE — that was the wrapper gap, not a 32k length-death. The first 200 were **not** re-spent.

Scale-out wrote **43** more incremental sidecars (total **243 / 5 000** on disk) with `skeleton=yes` on most keys, then this session stopped. Remaining ~4 757 `--live` calls are ~4 h / ~$4 at the measured card time and are a later off-peak resume, not a D22 fail.

## Tooling landed

- [`prep_pack.py --live`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/prep_pack.py) threads `--manifest-authoritative`, refuses `--live` below 32768, writes sidecars atomically (temp + `os.replace`), appends `--journal` JSONL, stops on 401/402, skips existing sidecars.
- [`build_drain_head.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2675_w1_prep/build_drain_head.py) / [`run_prep_live.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2675_w1_prep/run_prep_live.py).

`prep_pack.py --selftest` PASS after the changes.

## Non-claims

- Not a production draft-lane. Not E1. Not TM. Not auto-promote.
- First-200 `route_hint` is not a quality claim (empty-DE prompt on that batch).
- Flash default reasoning tokens were observed; PREP did not set `reasoning_effort`.

_Dr. Mārcis Gasūns_
