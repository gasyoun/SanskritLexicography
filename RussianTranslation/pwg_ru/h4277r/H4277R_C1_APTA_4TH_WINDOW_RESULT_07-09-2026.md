# H4277 residual — the 4th `_apta` c1 window RAN, 07-09-2026: funded EN-span defect FIXED, coverage alone still requeues, one unflagged second EN span found

_Created: 07-09-2026 · Last updated: 07-09-2026_

Executor: Opus 5 (`claude-opus-5`), interactive session. Parent handoff:
[H4277](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H4277-OxAlpha_SanskritLexicography_hapta-4th-window-rule-tightening_07.09.26.md)
(closed 07-09 with its 4th window UNSPENT, "residual to MG"). A human ruled "run" at
~04:20Z and again chose the external-input-dir route at ~06:30Z; this is that window.

**Headline: the window ran and the funded defect is gone.** `{%equation of a degree%}` —
the sense the `{Tn}`-verbatim clause was written for — came back **verbatim** instead of
translated. Every audit gate passes except `coverage`, whose `COVERAGE-OVER(16/7)` flag is
the pre-registered report-class shape H4277 fenced as out of scope. **But the fix is
partial in a way no detector caught:** a *second* English gloss span in the same card,
`*{%equation of degree%}`, is still translated to `*{%уравнение степени%}`, and
`foreign_gloss_translated` did not fire on it.

## 1. What ran

| | value |
|---|---|
| Gate-0 (c1) | **PASS** 04:17Z — warm-up 17 045 ms, measured 17 142 ms, both `success`, ceiling 80 000 ms |
| Canary | **GO** 04:31Z — 1 paid call, 10 200 ms, `null_keys: []`, manifest sha `24f6fd37…` |
| Window | **success** 06:32Z — 294 709 ms, first attempt, `null_keys: []`, 1 paid call, manifest sha `815a7b29…`, result sha `ad38b469…`, run `h4277r-apta-20260907T063232Z` |
| Preflight | `over_ceiling: false`, verdict `ok`, 1 card, est \$0.15, `defer_monster: []` |
| Lease | `defect-repair-oxalpha-defect-repair__apta-20260907T063156Z-7512`, `no_tm: true`, `serial-whole-card` |
| Prompt build | `master` at `41842c569` — carries H4277's `{Tn}`-verbatim clause **and** the H4277-residual probe bridge |

Two refusals happened before the spend and cost nothing: `--timeout 900` was refused
against the 600 000 ms production hard maximum (H2254 owner ruling — "REFUSED, not
clamped"), and the first lease went to `blocked` after a prepare that failed on the
missing rootmap. Both are recorded here because a reader retracing the run will hit them.

## 2. The blocker that took the whole session: `_apta` had no rootmap anywhere on the box

`coordinator.py prepare` fails with `FAIL: no rootmap for '_apta'`. A full sweep of both
drives found **exactly one** rootmap in existence — `src/pilot/input/d_a.rootmap.json`.
`_apta.portrait.json` and `_apta.raw.txt` were present; the rootmap that `prepare` needs
was not, and H4270's own record cites a "canonical `PWG_INPUT_DIR`" whose contents are not
on this machine.

`_apta` is a **single whole card**, confirmed three independent ways: H4270's window ran
`keys: ["_apta"]`; the coordinator lease resolves `run_keys: ["~005fapta"]` with
`keymap {"~005fapta": "_apta"}`; and the inputs on disk are whole-card. Only `subkey` is
consumed downstream (`gen_opt_harness2.selected_keys`, `window_provenance.root_keys`), so
the rootmap is one entry:

```json
{"root": "_apta", "safe": "~005fapta",
 "sub_cards": [{"subkey": "_apta", "hom": 0, "seg_index": 0, "part": 0,
                "kind": "head", "section": "whole", "upasarga": "", "root_key": "_apta"}]}
```

One subkey, exactly the one the promoted rows already carry — identity-preserving, so the
printed-locus join of [H3751](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3751-Opus_SanskritLexicography_pwg-homonym-index-remap_30.08.26.md)
(FINDINGS §617) cannot fork.

**Where it was written, and why not in the repo.** Writing it to
`RussianTranslation/src/pilot/input/` was refused by the main-tree isolation guard
(`AGENT_SELF_OVERRIDE_REFUSED` — `ALLOW_MAIN_TREE_EDIT` is addressed to a human). That
refusal was reported, not overridden. A human then chose the external route: the input dir
was **mirrored outside the repo** to `C:\Users\user\.pwg_ru_input\h4277r` (953 files,
`_apta.portrait.json` md5 `91ba9ecf…` and `_apta.raw.txt` md5 `3903aeaa…` byte-identical to
source), the rootmap added there, and `PWG_INPUT_DIR` pointed at it. **Nothing was written
into the guarded tree.** This is what H4270 meant by "canonical `PWG_INPUT_DIR`"; that dir
is now reproducible rather than lore.

## 3. Acceptance, measured

H4277 item 5, checked directly against `out.window.json` (16 sense objects):

| criterion | result |
|---|---|
| per-sense RU `{%…%}` count == DE count | **8 == 8** ✅ (H4015: 1/8 · H4270: 8/8) |
| the EN span restored verbatim as `{%equation of a degree%}` | ✅ **verbatim** — sense 12 |
| zero `«…»` on gloss spans | **0** ✅ |
| `{#jawA#}` intact | ✅ present |
| `<ls>` refs intact | ✅ 14 whole-card (7 paired, as H4270) |
| `{#…#}` spans | 19 |
| `markup_wrapper_dropped` | ✅ absent |
| `foreign_gloss_translated` | ✅ absent |
| `requeue.defect.keys.txt` free of `_apta` | ❌ **contains `_apta`** — `coverage` only |

Gate-by-gate: `final_schema` · `nws` · `translation` · `stage2_mechanical` · `sense_dupes` ·
`prompt_semantic` · `sense_loss` · `ru_style` all **PASS**. `prompt_semantic` reports
**high_confidence = 0** (H4270: 1), score 60 (H4270: 170); the 5–6 remaining risks are the
known medium `suspicious_lexicographic_with_text_signal` class, report-only per the handoff.
`coverage` is the sole FAIL: `COVERAGE-OVER(16/7)` (H4270: 17/7).

**Per H4277's own instruction — "if it alone blocks acceptance, STOP and record, do not
widen scope" — this is a STOP.** No fifth window. The store is untouched; no promotion, no
TM refresh, no defect-list removal.

## 4. The finding the gates missed: a SECOND English gloss span, still translated

The card carries two English `{%…%}` glosses, not one. The `{Tn}`-verbatim clause fixed the
first and left the second:

```
sense 12  DE: — b〉 {%equation of a degree%} <ls>WILS.</ls> — Die andern Bedeutungen …
          RU: — б) {%equation of a degree%} <ls>WILS.</ls> — Другие значения слова …     ✅ verbatim

sense 15  DE: — b〉 *{%equation of degree%}.
          RU: — б) *{%уравнение степени%}.                                                ❌ translated
```

They differ in three ways that plausibly explain the split: the leading `*`, the absent
"a", and the missing `<ls>`. If `pwg_mask` classifies sense 12's span as English (→ `{Tn}` →
deterministic verbatim restore) but not sense 15's, then the clause never applied to 15 —
it was visible, and the GLOSS WRAPPERS rule's "every `{%…%}` must reappear around its
translation" is what the model followed. The GAPS §17 convention for non-German `{%…%}`
(Latin/English) is mask + verbatim restore, so the masking classifier, not the prompt, is
the suspect.

**The measurement problem is the important half:** `foreign_gloss_translated` did **not**
fire on sense 15, and `prompt_semantic` reported high-confidence 0. A gate that catches this
class only when the span was masked cannot see the case where the *masking* is what failed.
That is a detector gap, and it is why this window reads "clean" everywhere except a coverage
flag that has nothing to do with it.

H4270's record described its sense-4b defect as `b〉 *{%equation of a degree%}` — asterisked,
*with* the "a". Today's asterisked span reads `*{%equation of degree%}`. Whether H4270 flagged
what is now sense 15 (and sense 12 was always clean) is not resolvable from the surviving
evidence, and it changes what "fixed" means here — so it is recorded as open rather than
assumed either way.

## 5. What a human decides next

1. **Is the masking classifier the fix, or the audit detector?** Sense 15 says one of them is
   wrong; the cheap probe is `pwg_mask` on this card's two spans, offline, zero calls.
2. **Does `COVERAGE-OVER(16/7)` stay report-class?** It has now blocked mechanical acceptance
   on three consecutive `_apta` windows while never once being the real defect.
3. **`_apta` stays on the defect list** and out of the store until 1 and 2 are settled.

## 6. Evidence

- [`status.h4277r.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4277r/status.h4277r.json) · [`window_stdout.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4277r/window_stdout.txt) · [`audit_window.report.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4277r/audit_window.report.md)
- Gate + canary receipts, call reservations and raw envelopes: `src/pilot/output/h4277r/` and `C:\Users\user\.pwg_ru_evidence\` (gitignored, local)
- External input dir: `C:\Users\user\.pwg_ru_input\h4277r` (local, 953 files + the one added rootmap)

_Dr. Mārcis Gasūns_
