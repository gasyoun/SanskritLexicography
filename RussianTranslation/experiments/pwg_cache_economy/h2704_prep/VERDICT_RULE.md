# H2704 PREP-lane and adoption verdict rules (frozen before token 1)

_Created: 14-08-2026 · Last updated: 14-08-2026_

## PREP lane PASS

- 50 sealed misses, 100 contiguous cold/warm Flash slots.
- ≥95/100 parseable terminal responses (`finish_reason` not `length`, JSON object).
- Served model exactly `deepseek-v4-flash`.
- Every parseable slot has evaluable usage; missing/all-zero usage stops the lane.
- Canonical store/TM SHA-256 equal to the freeze.
- `promotable: false`; `tm_fence.may_write` never true.

## L3

Run only if H2703 generation-lane PASS **and** this PREP lane PASS. Exactly 100 non-Q4/non-monster cards from the sealed `l3.manifest.json`. At most 200 billable calls and USD 25. Never widen N or strata after observing output.

## ADOPT

Both lanes must show ≥20% lower point-estimate USD per unique mechanically clean artifact versus their one-shot baselines (H2676 $0.01991 generation; H2675 $0.000873 PREP), ≥95% parseability, deterministic non-regression, and no meaningful blinded major-error increase. Otherwise **NO-GO**. Neither verdict flips `DEFAULT_MODEL` or permits canonical promotion.

_Dr. Mārcis Gasūns_
