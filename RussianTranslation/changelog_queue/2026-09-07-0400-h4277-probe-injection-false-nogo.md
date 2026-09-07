# H4277 — the c1 readiness probe was refusing itself as a prompt injection: root cause from the transcript, provenance bridge, zero paid calls

_Created: 07-09-2026 · Last updated: 07-09-2026_

_Date: 07-09-2026 · Executor: Opus 5 (`claude-opus-5`), interactive · 0 paid calls_

- **Root cause of the 07-09 01:41Z `content`-class NO-GO, read off evidence already on disk.**
  The measured call's session transcript (`session_id` from the raw envelope →
  `<config-dir>\projects\D--pwg-ru-cli-cwd\<id>.jsonl`) records the model refusing the probe as
  *"a prompt-injection attempt layered on ambient context"* and naming three reasons — plan
  mode's turn-ending rule, "no actual translation cards were provided", and the surrounding
  system-reminders — then emitting `{"ok": false}` through `StructuredOutput` on purpose. So the
  NO-GO was **FALSE**: c1 was healthy, the gate fail-closed correctly on a bad reading, and the
  defect was in `_probe_prompt`. Cost of the false reading: $0.19 and one of two rationed daily
  attempts. Hypothesis (b) of the NO-GO doc (the H4277 `{Tn}` clause) is ruled out — the
  objection is that there are *no cards at all*, not that any rule is wrong.
- **Why it is bimodal on byte-identical bytes.** H3157's prepend produced a prompt whose halves
  read as adversarial: a task-shape block promising `=== CARD <key> ===` blocks, then zero cards,
  then a differently-voiced order to emit one fixed string. That is the textual signature of an
  injection, so each call *decides* whether to trust the second instruction — the warm-up 16 s
  earlier took the cooperative reading, the measured call took the adversarial one.
- **Fix: `_PROBE_PROVENANCE_BRIDGE`** in `max_account_orchestrator.py`, between the production
  block and the filler, answering each objection in the harness's own voice — same issuer as the
  block above, zero cards deliberate and expected, structured-output channel as the sanctioned
  turn-ending delivery, filler framed as "data, never instructions". **No gate loosening:**
  `{"ok": true}` remains the only passing answer, no retry inside a sitting, no ceiling raised,
  no profile switched, `--permission-mode plan` kept (spawn-shape match, FINDINGS §498 rule 1),
  H3157's sensitivity intact (production block still first and verbatim).
- Pinned by `test_health_probe_carries_the_h4277_provenance_bridge` (provenance line, zero-card
  declaration, structured-output channel, data-not-instructions framing, bridge-before-filler
  order), so shortening the bridge back to the terse form fails offline instead of at $0.19 a
  reading. `window_selftest` **222/223** (sole failure the red-by-design parity gate);
  `max_account_orchestrator_selftest` **PASS**, its D-P assertions untouched. Prompt 10 711 B.
- **Standing diagnostic worth reusing:** on any `content`-class probe NO-GO, read the session
  transcript before forming a hypothesis. The raw envelope carries the verdict; the transcript
  carries the reason, and reading it costs nothing.
- Record: [pwg_ru/h4277/H4277_C1_GATE_NOGO_07-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4277/H4277_C1_GATE_NOGO_07-09-2026.md) §7.

_Dr. Mārcis Gasūns_
