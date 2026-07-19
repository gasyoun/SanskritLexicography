export const meta = {
  name: 'h1209-controller-worker-slice',
  description: 'H1209 controller-worker canary validation slice v2 (canonical-aligned gates): Opus controller + Sonnet workers, HARD multiset fidelity + shortfall-only sense gate, promote-DRY',
  phases: [{ title: 'Translate' }, { title: 'Control' }],
}

// Payload (cards: prompt/skeleton_tokens/expected_senses/complexity, plus worker_schema)
// is injected by inject_payload.py — Workflow scripts have no filesystem access.
const PAYLOAD = /*__PAYLOAD__*/ null /*__END__*/
const CARDS = PAYLOAD.cards
const WORKER_SCHEMA = PAYLOAD.worker_schema

const VERDICT_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['ok', 'issues'],
  properties: {
    ok: { type: 'boolean' },
    issues: { type: 'array', items: { type: 'string' } },
    severity: { enum: ['none', 'minor', 'major'] },
  },
}

function tokenSet(s) { return (String(s || '').match(/\{T\d+\}/g)) || [] }
// {Tn} multiset over the canonical TOKEN_FIDELITY_FIELDS (card_fields.py C-17:
// record.grammar + sense.german) — the mask-level superset of accept()'s post-restore
// <ls>/{# fidelity-reject: multiset equality ⇒ restored counts match (masked spans are
// the only carriers of <ls>/{# in a skeleton; the prompt forbids typing markup).
function fidelityTokens(card) {
  const toks = []
  for (const r of (card.records || [])) {
    toks.push(...tokenSet(r.grammar))
    for (const s of (r.senses || [])) toks.push(...tokenSet(s.german))
  }
  return toks
}
// Same multiset over the TRANSLATION field — the mask-level analogue of accept()'s
// H1152 guard 2 (a span dropped from russian alone must not hide behind a clean echo).
function translationTokens(card) {
  const toks = []
  for (const r of (card.records || [])) for (const s of (r.senses || [])) toks.push(...tokenSet(s.russian))
  return toks
}
function outputSenseCount(card) {
  let n = 0; for (const r of (card.records || [])) n += (r.senses || []).length; return n
}
function multisetDiff(want, got) {
  const need = new Map()
  for (const t of want) need.set(t, (need.get(t) || 0) + 1)
  for (const t of got) if (need.has(t)) { const n = need.get(t) - 1; if (n) need.set(t, n); else need.delete(t) }
  return [...need.keys()]
}

// Deterministic free gates, direction-aligned with the canonical accept() battery
// (gen_opt_harness2.py) — the v1 slice proved a NON-canonical gate here is worse than
// none: a HARD equality check against the naive `senses` glyph count made workers
// displace source spans into card.notes (NOT a restored field -> content silently lost;
// 2/3 canonical fidelity-rejects). v2 gates, all HARD (they trigger the free retry):
//   1. german+grammar {Tn} multiset == skeleton   (canonical TNMASK, armed)
//   2. russian {Tn} multiset == skeleton          (mask-level H1152 guard 2)
//   3. sense SHORTFALL only: emitted < source_senses (canonical SAN-LOSS direction —
//      over-emission is NEVER an issue; a faithful split may yield MORE senses)
//   4. empty russian
// coverage stays reported for telemetry continuity with the v1 run.
function deterministicAudit(card, c) {
  const issues = []
  const want = c.skeleton_tokens
  const gotFid = fidelityTokens(card)
  const missingFid = multisetDiff(want, gotFid)
  const inventedFid = multisetDiff(gotFid, want)
  if (missingFid.length) issues.push(
    'fidelity: masked spans missing from senses\' german: ' + missingFid.slice(0, 20).join(',')
    + ' — EVERY {Tn} from the source must appear in a sense\'s german AND russian, in source order;'
    + ' card.notes must NOT hold source {Tn} spans (notes is never unmasked, so content parked there is LOST)')
  if (inventedFid.length) issues.push('invented-placeholders in german: ' + inventedFid.slice(0, 10).join(','))
  const gotTr = translationTokens(card)
  const missingTr = multisetDiff(want, gotTr)
  const inventedTr = multisetDiff(gotTr, want)
  if (missingTr.length) issues.push(
    'translation-fidelity: masked spans missing from senses\' russian: ' + missingTr.slice(0, 20).join(',')
    + ' — the russian text must carry the same {Tn} spans as the german (citations/Sanskrit are language-independent)')
  if (inventedTr.length) issues.push('invented-placeholders in russian: ' + inventedTr.slice(0, 10).join(','))
  const osc = outputSenseCount(card)
  if (c.source_senses > 1 && osc < c.source_senses)
    issues.push('sense-shortfall: output ' + osc + ' senses < source\'s ' + c.source_senses
      + ' declared top-level senses — a sense was dropped (emitting MORE than ' + c.source_senses + ' is fine)')
  for (const r of (card.records || [])) for (const s of (r.senses || []))
    if (!s.russian || !String(s.russian).trim()) issues.push('empty-russian: sense ' + (s.tag || '?'))
  const gotSet = new Set(gotFid)
  const covered = want.filter(t => gotSet.has(t)).length
  const coverage = want.length ? +(covered / want.length).toFixed(2) : 1
  return { issues, coverage }
}

// B07 (H1339): no agent() call may hang the strictly-serial batch forever. Race every call
// against a relative wall-clock deadline (setTimeout only -- Date.now() is unavailable in
// Workflow scripts); a timed-out call resolves null: the worker lane retries it, the
// controller lane escalates (never auto-approves). The serial card loop itself is the
// MG-locked canary architecture and stays.
const AGENT_DEADLINE_MS = 300000
const withDeadline = (p, ms) => Promise.race([p, new Promise(res => setTimeout(() => res(null), ms))])

async function runWorker(c, feedback) {
  const prompt = c.prompt + (feedback
    ? '\n\n=== CONTROLLER FEEDBACK (fix ONLY these, keep everything else verbatim) ===\n' + feedback : '')
  return await withDeadline(
    agent(prompt, { label: 'worker:' + c.key1, phase: 'Translate', model: 'sonnet', schema: WORKER_SCHEMA }),
    AGENT_DEADLINE_MS)
}

async function controllerReview(c, card) {
  const senses = (card.records || []).flatMap(r => (r.senses || []).map(s => ({ tag: s.tag, german: s.german, russian: s.russian })))
  const prompt = 'You are the QUALITY CONTROLLER for a PWG German->Russian scholarly dictionary translation. '
    + 'For headword ' + c.key1 + ', check each sense: (a) the Russian faithfully renders the German gloss '
    + '(no invented, dropped, or merged meaning), (b) every {Tn} placeholder present in the German is a real '
    + 'masked span (not invented), (c) scholarly-philological register. Set ok=false with specific, actionable '
    + 'issues ONLY for genuine fidelity defects; do NOT nitpick style or wording preference. Senses JSON:\n'
    + JSON.stringify(senses)
  return await withDeadline(
    agent(prompt, { label: 'control:' + c.key1, phase: 'Control', model: 'opus', schema: VERDICT_SCHEMA }),
    AGENT_DEADLINE_MS)
}

phase('Translate')
const results = []
for (const c of CARDS) {
  const rec = {
    key1: c.key1, complexity: c.complexity, attempts: 0, self_report: null,
    det: null, controller: null, controller_calls: 0, final_status: null, card: null,
  }
  let feedback = null
  let controllerRejected = false   // B06 (H1339): rejection memory across attempts
  for (let attempt = 1; attempt <= 3; attempt++) {
    rec.attempts = attempt
    const res = await runWorker(c, feedback)
    // B05 (H1339): a null worker result consumes ONE attempt and RETRIES (was: break ->
    // zero retries, one dead worker killed the card). 'worker-null-death' stands only
    // when every remaining attempt also returns null; any later success overwrites it.
    if (!res) { rec.final_status = 'worker-null-death'; continue }
    rec.self_report = res.self_report; rec.card = res.card
    const det = deterministicAudit(res.card, c); rec.det = det
    const flaggedUnsure = !!(res.self_report && res.self_report.unsure)
    // B06 (H1339): a card the controller REJECTED can never exit 'clean-no-review' on a
    // later attempt -- the rejection is sticky, so the replacement must pass the
    // controller (or the deterministic gate escalates it), never slip out unreviewed.
    const needReview = det.issues.length > 0 || flaggedUnsure || c.complexity.complex || controllerRejected
    if (!needReview) { rec.final_status = 'clean-no-review'; break }
    if (det.issues.length > 0) {                 // hard deterministic fail: retry, no Opus spend
      rec.controller = { ok: false, source: 'deterministic', issues: det.issues }
      feedback = 'Deterministic gate failures:\n- ' + det.issues.join('\n- ')
      if (attempt === 3) rec.final_status = 'escalate-review-sheet'
      continue
    }
    const v = await controllerReview(c, res.card); rec.controller_calls++; rec.controller = v
    if (v && v.ok) { rec.final_status = 'clean-controller-approved'; break }
    controllerRejected = true                    // B06: sticky -- no later clean-no-review
    feedback = 'Controller found issues:\n- ' + ((v && v.issues) || ['unspecified']).join('\n- ')
    if (attempt === 3) rec.final_status = 'escalate-review-sheet'
  }
  if (!rec.final_status) rec.final_status = 'escalate-review-sheet'
  results.push(rec)
}

const CLEAN = new Set(['clean-no-review', 'clean-controller-approved'])
return {
  slice: CARDS.map(c => c.key1),
  results: results.map(r => ({
    key1: r.key1, attempts: r.attempts,
    complexity_score: r.complexity.score, complexity_flag: r.complexity.complex,
    self_report_unsure: r.self_report ? !!r.self_report.unsure : null,
    self_report_note: r.self_report ? (r.self_report.note || '') : null,
    coverage: r.det ? r.det.coverage : null,
    det_issues: r.det ? r.det.issues : null,
    controller_calls: r.controller_calls,
    controller_ok: r.controller ? (r.controller.ok === undefined ? null : r.controller.ok) : null,
    controller_issues: r.controller ? (r.controller.issues || []) : null,
    final_status: r.final_status,
    would_promote: CLEAN.has(r.final_status),
  })),
  cards_out: results.map(r => ({ key1: r.key1, card: r.card })),
}
