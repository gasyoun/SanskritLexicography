# H2251 — canary GO on the `--safe-mode` arm, and the ruling on the H2189 §4.2 `tag` divergence

_Created: 06-08-2026 · Last updated: 06-08-2026_

**Handoff:** [H2251](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2251-Opus_SanskritLexicography_pwg-safe-mode-canary-flip-default_03.08.26.md)
(**Opus 5**) — canary GO on the `--safe-mode` arm + rule the n=1 tag-vocabulary divergence,
then flip `execution.cli_safe_mode` default ON.
**Executed by:** Opus 5 (`claude-opus-5`), Claude Code. **Paid calls on** Sonnet 5
(`claude-sonnet-5`) — the model pinned in the manifest.
**Parent:** [H2189 report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2189/PROFILE_SURFACE_AB_SAFE_MODE_VS_MINIMAL_CONFIG_DIR_03-08-2026.md)
§4.2 (the divergence) and §5.1 (what would justify the flip).

**Verdict: FLIP. `execution.cli_safe_mode` now defaults ON** — on a canary GO produced on
the safe-mode arm, plus a 12-draw both-ways comparison showing no arm effect on card content
and no content loss anywhere.

**Two corrections to the parent report, both against the flip's own interest:** H2189's
headline savings were **n=1 and did not replicate** (output −4.4 % at n=6, not −49 %; wall
−12.3 %, not −55 %; cost −22.3 %, not −61 %), and the `tag` divergence is **not pure
sampling noise** — an arm-linked style component survives and is logged as an open residual
(§5.1). The flip rests on the ceiling headroom and the content evidence, not on the retired
numbers.

---

## 1. What was open

H2189 shipped `--safe-mode` **opt-in, default OFF**. Not because the cost case was in
doubt — that was settled at −61 % cost / −55 % wall on a real card, with the baseline
*timing out at the 300 s production ceiling* — but because of one unattributed observation.
The two arms returned different free-text `tag` vocabularies for the same card:

| Arm | `tag` values (H2189, n=1 each) |
|---|---|
| `paid` | `tail` · `name` · `xref` · `sch-name` · `pwkvn-name` |
| `safe` | `cross-ref` · `addendum-1` · `addendum-crossref` · `SCH-Nachtrag` · `PWKVN-crossref` |

The schema types `tag` as a bare non-empty string, so both validate, and every gate the
project actually checks was identical across arms. But at **n=1 per arm** the observation
had two live explanations and no way to choose between them:

* **(A)** `--safe-mode` changes the tag vocabulary — a real behaviour change, and a reason
  not to flip.
* **(B)** tag vocabulary is simply not stable between two independent generations — sampling
  variation, in which case the observation says nothing about the flag.

## 2. The discriminating design — repeats, not more cards

Adding more *cards* to a one-draw-per-arm design cannot separate (A) from (B): every extra
card still contributes one `paid` draw and one `safe` draw, so every difference stays
attributable to either cause. What separates them is **repeats within an arm**. Run the same
card twice on the SAME arm and the flag is held constant by construction, so any vocabulary
difference that appears there is (B) and nothing else.

So the measurement is a comparison of two distance families, not a diff:

```text
within-arm  d(paid#1, paid#2), d(safe#1, safe#2)   flag held CONSTANT
between-arm d(paid#i, safe#j)                      flag VARIED
```

`d` is Jaccard distance over the set of `tag` strings in a card (0.0 identical, 1.0
disjoint). Sets rather than sequences: the question is which vocabulary the model reached
for, and a positional diff would score two identical vocabularies as different for ordering
alone.

**3 cards × 2 arms × 2 repeats = 12 paid calls**, sequential with a cooldown, through
[`h2189_profile_ab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2189_profile_ab.py)
— the same rig, manifest ([`h1209_slice3.manifest.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1209_slice3.manifest.json))
and model H2189 used, so the numbers compose. Analysis by
[`h2251_tag_compare.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2251_tag_compare.py),
which reads the committed envelopes and issues no call of its own.

**The rig's `--timeout 600` is not a production ceiling.** `HARD_TIMEOUT_MS` was not touched
and stays 300 000 ms; 600 s exists only inside the measurement harness, exactly as in H2189,
so the `paid` arm can finish a card that production's own ceiling kills.

---

## 3. Live gate — health, then the canary, on the safe-mode arm

`/pwg-live-gate` against profile `c4`, in order, before any measurement spend.

**Step 1 — health: PASS.** Policy `production_v3`, both ceilings independently satisfied:

| Reading | wall `elapsed_ms` | route `duration_api_ms` | ceiling | outcome |
|---|--:|--:|---|---|
| warm-up (advisory) | 67 217 | 21 504 | — | success |
| **measured** | **43 638** | **15 846** | 80 000 wall / 45 000 route | **success** |

Zero connection errors. Rows committed at
[`gate/health_probe_rows.h2251.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2251/gate/health_probe_rows.h2251.jsonl).

**Step 2 — canary: GO, and attributable to the safe-mode arm.** This is the acceptance
artifact H2189 §5.1 named, and it could not be inherited from a baseline run. Two gaps had
to be closed first, because neither the builder nor the receipt could express an arm:

* [`canary_manifest_build.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/canary_manifest_build.py)
  gained `--cli-safe-mode` / `--no-cli-safe-mode`, which pin `execution.cli_safe_mode`
  into the emitted manifest **before** its SHA-256 is taken — so the digest the worker
  verifies covers the arm the receipt claims. Omitted (the default) leaves the key absent
  and the manifest byte-identical to the committed golden artifact.
* [`canary_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/canary_gate.py)
  `judge` now records `cli_safe_mode` in the receipt. Until it did, a receipt could not
  distinguish the two spawn shapes at all — which is what made "produced on the safe-mode
  arm, not inherited from a baseline run" unverifiable from the artifact itself.

The receipt ([`gate/canary_receipt.safemode.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2251/gate/canary_receipt.safemode.json)):

```json
{ "verdict": "GO", "profile_slot": "c4", "cli_safe_mode": true,
  "reasons": [], "facts": { "sense_counts": [["dq_canary_puregloss~~h0_zz_pw", 3]],
                            "tn_hits": [], "marker_hits": [] } }
```

3/3 senses carrying Russian, zero `{Tn}` residue, zero `SAN-LOSS`/`UNMAPPED`, synthetic-key
check passed, manifest SHA `769ffff…` verified by the worker. `gate_reason = LIVE_GO`.

**One honest gap in that chain, stated rather than smoothed over.** The receipt's
`cli_safe_mode: true` is what the manifest **requested**; the `cli_safe_mode_effective`
status field that records what the spawn **did** was added *after* this canary had already
run, so the committed [`gate/status.canary.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2251/gate/status.canary.json)
does not carry it. The request-to-spawn link therefore rests on three things rather than one
field: the manifest was SHA-verified by the worker, `resolve_safe_mode` returns `False` only
on an unsupported CLI, and that path is *loud* — no `H2189: … spawning WITHOUT it` warning
appeared on this run's stderr. The next canary will carry the field directly; this one is
evidenced, not self-describing, and re-firing it purely to improve the artifact was not
worth another paid call.

**The gate evidence is committed, not left in `output/`.** `RussianTranslation/src/pilot/output/`
is gitignored (`.gitignore:67`), so the receipt — the acceptance artifact — would have been
destroyed by the next cleanup. It and the canary envelope/status/manifest/preflight are
copied under [`pwg_ru/h2251/gate/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru/h2251/gate).
This is the H895 evidence-loss class, caught before it fired rather than after.

---

## 4. The measurement — 12 calls, 3 cards, both arms, two draws each

`nakzatra` · `sarvatra` · `sakft` from `h1209_slice3`. Raw envelopes committed under
[`pwg_ru/h2251/raw/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru/h2251/raw).
Total spend **$6.3140** over 12 calls, all cost-evaluable, no timeouts.

### 4.1 The `tag` question — answered, and not in the shape either hypothesis predicted

| Family | mean Jaccard distance | n pairs |
|---|--:|--:|
| within-arm, all tags | 0.286 | 6 |
| between-arm, all tags | 0.515 | 12 |
| **within-arm, free-text tags only** | **0.535** | 6 |
| **between-arm, free-text tags only** | **1.000** | 12 |

Two facts, both real, and they pull in opposite directions:

* **The vocabulary is not reproducible with the flag held constant.** Mean within-arm
  free-text distance is 0.535, and on `nakzatra`/`safe` and `sarvatra`/`safe` it is
  **1.000** — two draws of the same card on the same arm sharing *zero* free-text tags.
  This is exactly the condition H2189 named as closing its own question: *"if tag
  vocabulary turns out to vary run-to-run on the SAME arm, that settles it as sampling
  noise and the divergence is closed."*
* **But every one of the 12 between-arm pairs is completely disjoint (1.000).** That
  uniformity is not what pure noise looks like, and the arms have visibly different
  *styles* — on `sakft`, `paid` produced bare `2a 2b 2c 2d 2e · SCH · note · прим.` while
  `safe` produced siglum-prefixed `PW-2a … PW-2e · SCH-1 · SCH-add`.

So the honest reading is neither (A) nor (B) alone: there is a large random component **and**
an arm-linked style component on top of it. The pre-registered decision rule in
[`h2251_tag_compare.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2251_tag_compare.py)
returns **MIXED** on the full tag set, and its guard — *"do not read this as a licence to
flip"* — is why §4.2 below exists rather than the flip being taken here.

_The rule and the metric were both fixed before any of these numbers existed, and the ruling
stays on the full tag set. The free-text split is reported because it is the sharper view of
the same question (the bare sense numbers are structural and reproduce everywhere, which
makes every full-set distance conservatively small) — but choosing a metric after seeing the
data is how a measurement talks itself into a conclusion, so it corroborates and does not
decide._

### 4.2 The decisive question — is the CARD equivalent? (n=12, vs H2189's n=1)

A difference in a free-text label no gate consumes is acceptable **only** if the translated
content is sound. [`h2251_content_equivalence.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2251_content_equivalence.py)
re-uses the project's own single-sourced checks (`promote_final_cards.TN_RE`,
`canary_gate.LITERAL_MARKERS`), decomposed within-arm vs between-arm:

| card | arm | senses | sense spread | records | within-arm {Tn} distance |
|---|---|---|--:|---|--:|
| nakzatra | paid | 12, 13 | 1 | 7, 7 | 0.103 |
| nakzatra | safe | 12, 12 | 0 | 7, 7 | 0.014 |
| sakft | paid | 12, 13 | 1 | 3, 3 | 0.008 |
| sakft | safe | 12, 11 | 1 | 4, 3 | 0.000 |
| sarvatra | paid | 5, 6 | 1 | 2, 2 | 0.000 |
| sarvatra | safe | 7, 7 | 0 | 2, 2 | 0.000 |

* **Zero content loss in all 12 draws** — every sense carries Russian, and no literal
  `SAN-LOSS`/`UNMAPPED` appears anywhere. This is the property the gates actually check.
* **Sense segmentation is not reproducible on EITHER arm** (spread 1 on four of six
  arm-cards). H2189 §4.1's "7 records / 13 senses identical on both arms" was an n=1
  coincidence, not a stable property.
* **The arms do not separate on content.** Sense-count ranges overlap on 2 of 3 cards, and
  on `nakzatra` the `paid` arm differs from **itself** more than the two arms differ from
  each other on the `{Tn}` set (within-paid 0.103 vs between-arm mean 0.070).

Verdict from the tool: **NOT REPRODUCIBLE ON EITHER ARM** — card content is not a function
of the spawn shape, so a paid-vs-safe difference of this magnitude cannot be attributed to
`--safe-mode`.

### 4.3 Cost and latency — H2189's headline did NOT replicate

| Measure (mean/call, n=6 per arm) | `paid` | `safe` | Δ | H2189 at n=1 |
|---|--:|--:|--:|--:|
| cache create | 46 830 | 28 096 | **−40.0 %** | −69.0 % |
| output tokens | 18 574 | 17 765 | **−4.4 %** | −49.1 % |
| wall ms | 199 669 | 175 144 | **−12.3 %** | −54.7 % |
| api ms | 176 552 | 171 218 | −3.0 % | −45.1 % |
| USD (1 h write) total | 3.5530 | 2.7610 | **−22.3 %** | −60.8 % |

**The output halving was noise.** −49 % at n=1 became −4.4 % at n=6, which also retires
H2189 §4.1's inference that "the halved output is CLI agent-loop overhead disappearing".
Variance is high enough that one `safe` draw (`sarvatra#2`, $0.5606) cost more than either
`paid` draw of the same card.

**What did replicate is the ceiling headroom, and it is the stronger argument.** On `sakft`
the baseline ran **286 694 ms** and **266 349 ms** against the **300 000 ms** production
kill — twice within ~11 % of dying — where `safe` ran 232 891 and 189 106. H2189 saw the
same phenomenon as an outright timeout. A window that finishes beats a window that is
marginally cheaper.

---

## 5. Ruling and what shipped

**FLIP.** `execution.cli_safe_mode` now defaults **ON**
([`headless_worker.DEFAULT_CLI_SAFE_MODE`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py)).

The grounds, in order of weight:

1. The canary returned **GO on the safe-mode arm** — the precondition H2189 §5.1 named.
2. The `tag` question is **answered by the both-ways comparison**, not by assertion, and the
   answer meets H2189's own stated closing condition (vocabulary varies run-to-run on the
   same arm).
3. Card content shows **no arm effect and no loss** across 12 draws.
4. The baseline arm repeatedly runs within ~11 % of the production kill ceiling; the safe
   arm does not.

**Tri-state, so the flip cannot silence an operator.** Absent ⇒ ON; `true` ⇒ ON; **`false`
⇒ the historical spawn**, still honoured. Implementing this as `bool(...)` over the field
would have swallowed a deliberate opt-out, which is why that half is pinned by its own
assertion.

`test_safe_mode_is_opt_in_and_off_by_default` — the guard H2189 wrote *precisely* to catch an
undocumented flip — is **re-pointed, not deleted**, to
`test_safe_mode_default_is_on_and_an_explicit_false_still_opts_out`. The flip is now the
documented state, and the test asserts both halves of it.

### 5.1 Residuals — stated, not buried

| Item | Status |
|---|---|
| The arm-linked `tag` **style** component (between-arm free-text distance 1.000 across all 12 pairs, uniformly) | **Open.** Not sampling noise; `--safe-mode` does appear to shift label style toward siglum prefixes. It changes no gated property and the field was never stable, so it does not block the flip — but it is a real effect, not a closed question |
| H2189 §4.1's "output halving is agent-loop overhead" inference | **Retired.** The halving itself did not replicate (−4.4 % at n=6) |
| `bare_cli_cwd()` ancestry leak (H2189 §1.1) | **Still open as its own defect** — [H2249](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2249-Opus_SanskritLexicography_pwg-bare-cwd-ancestry-leak-fix_03.08.26.md). Default-ON `--safe-mode` now *masks* it on every lane, which makes H2249 harder to observe, not less real |
| `--exclude-dynamic-system-prompt-sections` | Still unmeasured (H2189 residual, unchanged) |
| `--bare` | Still a reserved human ruling — untouched |

### 5.2 LANG_PARITY

**SHARED.** The flag selects which profile context the CLI child loads, and the status field
records what the spawn did — both properties of the spawn, never of the target language.
Mechanically checked rather than asserted: every added line was grepped for a language-keyed
token (`russian`/`english`/`--lang`/`lang`/`_ru`/`_en`/`CARD_FIELD`/`FIELD[`) and **none**
appears.

---

## 6. Reproduce

```text
python src/pilot/canary_manifest_build.py --profile-slot c4 --config-dir <dir> \
       --outdir src/pilot/output/h2251 --cli-safe-mode
python src/pilot/headless_worker.py <outdir>/execution_manifest.canary.json ...
python src/pilot/canary_gate.py judge <outdir>/out.canary.json --receipt <receipt>
python src/pilot/h2189_profile_ab.py --run --phase card --keys 3 --arms paid,safe \
       --repeats 2 --timeout 600 --out pwg_ru/h2251/raw
python src/pilot/h2251_tag_compare.py --raw pwg_ru/h2251/raw
python src/pilot/h2251_content_equivalence.py --raw pwg_ru/h2251/raw
python src/pilot/h2251_tag_compare.py --selftest          # offline
python src/pilot/h2251_content_equivalence.py --selftest   # offline
```

Spend for everything in this report: **$6.3140** (12 A/B calls) + the health probe and the
one canary call.

---

_Dr. Mārcis Gasūns_
