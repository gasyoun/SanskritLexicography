export const meta = {
  name: 'h1210-shared-opus-controller',
  description: 'H1210 shared control stage: the SAME Opus controller review both A/B arms pass through — run standalone over cards that cleared the free deterministic gate',
  phases: [{ title: 'Control' }],
}

// WHY a standalone control stage exists at all:
// arm A runs the controller INSIDE its Workflow (wf_template_ab.js). Arm B generates from
// Python (DeepSeek) and cannot call Opus from there — no ANTHROPIC_API_KEY, standing rule.
// So arm B's cards come back here in rounds. The controller prompt, model and verdict
// schema below are COPIED VERBATIM from wf_template_ab.js `controllerReview()`: the whole
// point of the A/B is that only the generator differs, so the control stage must be the
// same stage, not a lookalike.
const PAYLOAD = /*__PAYLOAD__*/ null /*__END__*/
if (!PAYLOAD || PAYLOAD.schema !== 'h1210.control.v1') {
  throw new Error('payload schema mismatch: expected h1210.control.v1, got '
    + (PAYLOAD && PAYLOAD.schema))
}
const CARDS = PAYLOAD.cards

const VERDICT_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['ok', 'issues'],
  properties: {
    ok: { type: 'boolean' },
    issues: { type: 'array', items: { type: 'string' } },
    severity: { enum: ['none', 'minor', 'major'] },
  },
}

// Must match `wf_template_ab.js` — arm A's inline controller runs with a 900 s deadline, so
// a 300 s deadline here would silently score arm B's controller stage under a stricter clock
// than arm A's (round 1 lost 11 of 42 verdicts to exactly that asymmetry before it was
// caught). The A/B only holds if the shared stage is shared in its timeouts too.
const AGENT_DEADLINE_MS = 900000
const withDeadline = (p, ms) => Promise.race([p, new Promise(res => setTimeout(() => res(null), ms))])

async function controllerReview(c) {
  const prompt = 'You are the QUALITY CONTROLLER for a PWG German->Russian scholarly dictionary translation. '
    + 'For headword ' + c.key1 + ', check each sense: (a) the Russian faithfully renders the German gloss '
    + '(no invented, dropped, or merged meaning), (b) every {Tn} placeholder present in the German is a real '
    + 'masked span (not invented), (c) scholarly-philological register. Set ok=false with specific, actionable '
    + 'issues ONLY for genuine fidelity defects; do NOT nitpick style or wording preference. Senses JSON:\n'
    + JSON.stringify(c.senses)
  return await withDeadline(
    agent(prompt, { label: 'control:' + c.key1, phase: 'Control', model: 'opus', schema: VERDICT_SCHEMA }),
    AGENT_DEADLINE_MS)
}

phase('Control')
const verdicts = await parallel(CARDS.map(c => () => controllerReview(c).then(v => ({ key1: c.key1, verdict: v }))))
return {
  arm: PAYLOAD.arm,
  round: PAYLOAD.round,
  // A null verdict (deadline or thunk failure) is reported as such and NEVER read as
  // approval — the caller escalates it, exactly as the inline arm-A path does.
  verdicts: verdicts.map((v, i) => v || { key1: CARDS[i].key1, verdict: null }),
}
