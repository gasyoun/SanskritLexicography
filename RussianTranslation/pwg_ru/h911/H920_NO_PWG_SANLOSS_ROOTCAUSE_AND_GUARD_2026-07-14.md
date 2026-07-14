# H920 — no_pwg SAN-LOSS / missing_senses: root cause + deterministic guard

_Created: 14-07-2026 · Last updated: 14-07-2026_

**Executor:** Opus 4.8 (`claude-opus-4-8[1m]`) in Ultracode mode, under the owner-authorized
higher-tier override recorded in the [H920 handoff](https://github.com/gasyoun/Uprava/blob/main/handoffs/H920-Sonnet_SanskritLexicography_pwg-ru-no-pwg-san-loss-missing-senses-offline-fix_14.07.26.md).
**Offline only** — no translation generation, probe, account login, or store/TM mutation was
performed. Root-cause is drawn from committed H911 evidence plus the immutable H818 fc1 and
`no_pwg_w05_rq1` snapshots; the guard is validated on deterministic fixtures.

Fixes the #1 systemic defect the [H911 LOCAL-READINESS gate](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h911/H911_LOCAL_READINESS_QUALITY_ECONOMY_GATE_2026-07-14.md)
issued **FAIL** on: `missing_senses` (= SAN-LOSS, whole-dropped senses).

## 1. What the label `missing_senses` actually covered — two different classes

The H911 report grouped six keys under `missing_senses`. The frozen evidence shows they are
**two mechanistically distinct classes**, and only one is a genuine model sense-omission:

| Class | Keys | Mechanism | Already caught? |
|---|---|---|---|
| **infra-null** | `_u_das~~h0_zz_pw` (`kill-timeout 84s`), `_sibi`/`a_sud_da`/`aklizwa~~h0_zz_pw` (`selfheal-nothing-resolved`) | the card **never generated** — a null result with no `records`; `prompt_rule_audit.semantic_risks` fires `missing_senses` only because "no translated senses found" | **yes** — null cards, requeued transient; the semantic `missing_senses` risk fires on the zero-sense proxy |
| **genuine SAN-LOSS (a)** | `darv_i~~h0_zz_pw` (H818 fc1: SAN-LOSS(2/3)), `gaRanA` | the card **did** generate but the model **omitted a whole numbered sense** from a multi-sense source | **no** — silent; caught only by an operator eyeballing the fc1 canary |

The `no_pwg_w05_rq1` window's four `missing_senses` keys are ALL infra-null (kill-timeout /
selfheal-nothing-resolved). The genuine, silent SAN-LOSS class is the darvI shape.

## 2. Root cause — which of (a)/(b)/(c) dominates

Per the handoff's decomposition:

- **(a) the model omits a sense from a multi-sense portrait — DOMINATES the silent loss.**
- **(b) self-heal collapses a card to fewer senses — NOT a silent vector.** `selfHeal` skips any
  fragment that never resolves, but records every reduction as `missing_fragments`/`missing_groups`
  and sets `partial:true` (gen_opt_harness2.py). Heal-path drops are always flagged.
- **(c) presplit / merge / stitch drops a fragment — NOT a silent vector.** `autosplit_requeue`
  merge/topup leaves any unresolved `sense_ord` out and records it in `missing_si`/`missing_frags`.
  Split-path drops are always flagged.

### Why (a) is silent — the structural gap (primary evidence, H818 fc1)

darvI's masked source skeleton, verbatim from the run harness:

```
=== LAYER: PW — Böhtlingk kürzere Fassung ===
{T1} und {T2}¦ {T3}
{T6}— 1〉 {%Löffel%}.
{T7}— 2〉 {%die Haube einer Schlange%}.
{T8}— 3〉 {T4} {T5} eines Landes.
```

The per-key inputs recorded `"ls": 0, "sk": 3, "senses": 3`. The output card had **2** senses,
tagged **2** and **3** — sense **1 ("Löffel/spoon") was dropped entirely** (the model kept the
source ordinals, it did not renumber). The `fc1_result` operator event: `SAN-LOSS(2/3): model
dropped sense 1 (Loeffel/spoon)`, invocation **"clean (job done)"**.

Three compounding facts make this loss invisible to every deterministic guard:

1. **The no_pwg portrait declares no expected sense count.** `gen_no_pwg_card` writes
   `senses: []` deliberately (no fabricated PWG sense-tree), so nothing on the input side told
   any consumer that darvI has 3 senses.
2. **The only whole-card completeness guard is `accept()`'s `<ls>`/`{#` token-count match.**
   The dropped "Löffel" sense carried a gloss (`{%Löffel%}`) but **no citation and no masked
   Sanskrit span**, so dropping it left `ls 0==0` and `sk 3==3` unchanged — `accept()` passed the
   card clean. This is exactly the shape of a citation-free PW/SCH/NWS supplement gloss.
3. **`partial`/`missing_senses`/`total_senses` are only ever set in the fragment-heal and
   autosplit lanes** — a no_pwg sub-card translated *whole* (not presplit, not healed) never
   enters them, so those markers are never even computed for it.

The harness had already computed the answer — `inputs[k]['senses'] == 3` (`raw.count('〉')`) — but
**that value has no consumer anywhere in the JS**; it was discarded. The audit's semantic
`missing_senses` risk only fires on a **zero**-sense card, so a 2-of-3 partial drop is invisible to
it. Result: darvI was promotion-eligible with sense 1 silently gone.

## 3. The fix (deterministic, offline, language-neutral)

A single shared primitive, [`src/pilot/sense_count.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/sense_count.py):
`count_source_senses()` (distinct top-level `N〉` / line-anchored `N)` ordinals — high-precision,
the `〉` close-glyph never appears in a citation), `output_sense_count()`, `sense_shortfall()`,
`portrait_source_senses()`, `scan_sense_shortfall()`. Calibrated on the real evidence: darvI → 3,
aklizwa keyed supplement → 1, unnumbered adjective → 0, citation numbers → 0.

Wired at three points, all pre-lang or language-agnostic (verdict **SHARED** in
[LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md),
entry `sense_count_sanloss_guard_h920`):

1. **Enrich the no_pwg portrait** ([`_pilot_gen_merged.gen_no_pwg_card`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py)):
   stamp each sub-card's deterministic `source_senses` count into its portrait sidecar — closing
   the "empty portrait, no expected count" gap.
2. **Generation-prompt rule** (root-cause-(a) mitigation, since (a) dominates): a source with
   ≥2 numbered senses now carries an explicit **sense-completeness rule** telling the model to
   render every numbered sense and never drop one — including a short gloss-only sense.
3. **The audit guard, before promotion**, in BOTH auditors via the shared primitive:
   [`audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py)
   gains a `sense_loss` gate (portrait `source_senses` vs output count → requeue as a content
   **defect**); [`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py)
   gains a `MISSING-SENSE` **HARD** flag (distinct from its existing per-sense `SAN-LOSS`
   gloss-token flag).

**Conservative by construction:** a portrait without `source_senses` (pre-H920) or a null card is
skipped — never a false positive. The counter counts only explicitly-numbered top-level senses, a
lower bound, so a faithfully-merged card is never mis-flagged (e.g. `aklizwa~~h0_zz_pwkvn`, source
1 keyed sense, output 2 → clean).

## 4. Verification (fixtures only — no live generation)

New selftests in [`window_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py),
all green in the aggregate suite (`window selftest OK`):

- `test_h920_sense_count_top_level_ordinals` — the counter on the darvI/aklizwa/a_sakta/citation/
  line-anchored shapes.
- `test_h920_sense_shortfall_gate_flags_dropped_sense` — the RU gate flags darvI 2/3, passes a
  complete card, skips nulls + pre-H920 portraits, respects protected keys.
- `test_h920_no_pwg_portrait_stamps_source_senses` — the portrait carries `source_senses` matching
  `count_source_senses(raw)`, still fabricates no sense tree, and the completeness rule fires only
  for ≥2-sense sources without inflating the count.
- `test_h920_en_missing_sense_hard_flag` — the EN auditor emits a HARD `MISSING-SENSE` on a 2/3
  card, none on a complete card.

`lang_parity_check.py` clean (48 entries, no drift): every entry whose tracked file this change
touched was re-affirmed, and the new SHARED entry added.

## 5. Out of scope (separate handoffs — not minted here)

- **Deepest fix — consume `INPUT[k].senses` in the harness `accept()`** so a SAN-LOSS card is
  rejected at generation and routed to selfheal/requeue rather than caught downstream. This is a
  JS-harness change that can only be validated by a live run, so it is deferred to the
  separately-approved, bounded acceptance run (still gated by H911/H909).
- **NWS-entry-count guard.** `count_source_senses` targets the `〉`/`N)` numbered-sense format
  (the darvI class); NWS owner-map entries use an `N.` format and are governed by their existing
  "emit EXACTLY one card row per numbered entry" directive, not by this count.
- The **infra class** (`kill-timeout` / `selfheal-nothing-resolved`) and
  `untranslated_braced_german_gloss` remain H911 backlog items.

_Auto-generated by Opus 4.8 (`claude-opus-4-8[1m]`) as the H920 executor._

_Dr. Mārcis Gasūns_
