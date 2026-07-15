// H960 behavioral test for the accept() SAN-LOSS shortfall guard (H920's deferred deepest fix).
// Extracts the REAL accept() + countOf emitted by gen_opt_harness2.py (so this can't drift from
// the generator) and asserts, with restoreCard mocked to identity and fixtures that are already
// "restored" cards:
//   - SOFT (default SANLOSS_HARD_REJECT=false): a darvI 2/3 shortfall is COUNTED but the card is
//     KEPT (not rejected), the ls/sk fidelity gate having passed;
//   - a complete card and a surplus (emitted>expected) split are never flagged;
//   - FP-regression: a cross-reference card whose hardened source_senses==0 is skipped entirely;
//   - the ls/sk fidelity-reject still fires FIRST, before the sanloss guard;
//   - HARD (owner-gated flip SANLOSS_HARD_REJECT=true): the same shortfall now REJECTS + requeues.
//   node src/pilot/accept_sensecount_test.js <path-to-a-generated-harness.js>
const fs = require('fs')

const harnessPath = process.argv[2]
if (!harnessPath) { console.error('FAIL: usage: node accept_sensecount_test.js <harness.js>'); process.exit(1) }
const src = fs.readFileSync(harnessPath, 'utf8')

// Pull countOf/tokensOf/cardTokens (one-liners) and accept (brace block to the first column-0
// `\n}`) verbatim from the generated harness so this can't drift.
const one = name => {
  const m = src.match(new RegExp('const ' + name + ' = [^\\n]*'))
  if (!m) { console.error('FAIL: ' + name + ' not found in ' + harnessPath); process.exit(1) }
  return m[0].replace(new RegExp('^const ' + name + ' = '), '')
}
const am = src.match(/const accept = \(c, k\) => \{[\s\S]*?\n\}/)
if (!am) { console.error('FAIL: accept not found in ' + harnessPath); process.exit(1) }

// Runtime globals accept() closes over (all mocked). restoreCard = identity because the fixtures
// are already-restored cards and the ls/sk counts are computed on them directly.
let INPUTS = {}
const FAIL = {}
const noteFail = (k, why) => { FAIL[k] = String(why).slice(0, 300) }
const restoreCard = (c, k) => c
const log = () => {}
let SANLOSS_HARD_REJECT = false
let SANLOSS_SHORTFALLS = 0
const SANLOSS_DETAIL = []
let TNMASK_HARD_REJECT = false
let TNMASK_MISMATCHES = 0
const TNMASK_DETAIL = []
// Direct eval so the extracted functions close over the locals above.
const countOf = eval('(' + one('countOf') + ')')
const tokensOf = eval('(' + one('tokensOf') + ')')
const cardTokens = eval('(' + one('cardTokens') + ')')
const accept = eval('(' + am[0].replace(/^const accept = /, '') + ')')

let failed = 0
const check = (name, cond, extra) => { if (cond) { console.log('PASS: ' + name) } else { console.error('FAIL: ' + name + (extra ? ' -- ' + extra : '')); failed++ } }
const card = senses => ({ records: [{ senses }] })
const reset = () => {
  SANLOSS_SHORTFALLS = 0; SANLOSS_DETAIL.length = 0
  TNMASK_MISMATCHES = 0; TNMASK_DETAIL.length = 0
  for (const k in FAIL) delete FAIL[k]
}

// ---- SOFT (default): shortfall recorded, card KEPT ----
// darvI 2/3: source declares 3 senses, model emits 2; ls 0==0 and sk 3==3 (the two {#..#}-carrying
// senses survive), so the <ls>/{# fidelity gate passes and only the sense-count guard can see it.
INPUTS = { darvI: { ls: 0, sk: 3, source_senses: 3 } }
reset()
let r = accept(card([{ german: '{#a#} {#b#}' }, { german: '{#c#}' }]), 'darvI')
check('soft: darvI 2/3 shortfall is KEPT (not rejected)', r !== null)
check('soft: darvI shortfall counted with dropped=1',
  SANLOSS_SHORTFALLS === 1 && SANLOSS_DETAIL[0] && SANLOSS_DETAIL[0].dropped === 1, JSON.stringify(SANLOSS_DETAIL))
check('soft: no FAIL recorded for a kept shortfall', FAIL.darvI === undefined)

// complete 3/3: no shortfall.
INPUTS = { ok: { ls: 0, sk: 0, source_senses: 3 } }
reset()
r = accept(card([{ german: 'a' }, { german: 'b' }, { german: 'c' }]), 'ok')
check('complete card passes with no shortfall', r !== null && SANLOSS_SHORTFALLS === 0)

// surplus 3 > 2: a faithful split that yields MORE senses is never flagged.
INPUTS = { sur: { ls: 0, sk: 0, source_senses: 2 } }
reset()
r = accept(card([{ german: 'a' }, { german: 'b' }, { german: 'c' }]), 'sur')
check('surplus (emitted>expected) is not flagged', r !== null && SANLOSS_SHORTFALLS === 0)

// ---- FP-regression: a cross-reference card (hardened source_senses==0) never fires ----
// gam~~h2_31_pari / _a_srayatva shape: the source's only ordinals are cross-references, so the
// H960-hardened counter stamps source_senses=0 and the exp<1 skip keeps the guard silent.
INPUTS = { xref: { ls: 0, sk: 0, source_senses: 0 } }
reset()
r = accept(card([{ german: 'single unnumbered sense' }]), 'xref')
check('FP-regression: exp=0 cross-ref card is skipped (never flagged)', r !== null && SANLOSS_SHORTFALLS === 0)

// ---- ls/sk fidelity-reject still fires FIRST, before the sanloss guard ----
INPUTS = { mis: { ls: 1, sk: 0, source_senses: 1 } }
reset()
r = accept(card([{ german: 'no citation here' }]), 'mis')   // ls 0 != expected 1
check('ls/sk fidelity-reject still fires first',
  r === null && /fidelity-reject/.test(FAIL.mis || '') && SANLOSS_SHORTFALLS === 0)

// ---- HARD (owner-gated flip): the same shortfall now REJECTS + requeues ----
SANLOSS_HARD_REJECT = true
INPUTS = { darvI: { ls: 0, sk: 3, source_senses: 3 } }
reset()
r = accept(card([{ german: '{#a#} {#b#}' }, { german: '{#c#}' }]), 'darvI')
check('hard: darvI 2/3 shortfall REJECTED when armed',
  r === null && /sanloss-reject/.test(FAIL.darvI || ''))
SANLOSS_HARD_REJECT = false

// ---- H960 grammar-{Tn} multiset guard (soft) ----
// A dropped grammar <lex> {Tn}: the source skeleton masks 3 spans ({T1} grammar, {T2}, {T3}),
// the model keeps {T1} {T3} but drops {T2}. It carries neither an <ls> nor a {#, so the ls/sk
// count check passes (0==0) while the {Tn} multiset differs — the exact gap this guard closes.
INPUTS = { gram: { ls: 0, sk: 0, source_senses: 0, skeleton: '{T1} {T2} {T3}' } }
reset()
r = accept(card([{ german: '{T1} {T3}' }]), 'gram')
check('soft: dropped grammar {Tn} is KEPT but counted', r !== null && TNMASK_MISMATCHES === 1,
  'mismatches=' + TNMASK_MISMATCHES)
check('soft: the ls/sk count check is blind to the dropped {Tn} (no FAIL)', FAIL.gram === undefined)
check('soft: {Tn} mismatch detail records got/want',
  TNMASK_DETAIL[0] && TNMASK_DETAIL[0].got === '{T1} {T3}' && TNMASK_DETAIL[0].want === '{T1} {T2} {T3}',
  JSON.stringify(TNMASK_DETAIL))

// a card that keeps every {Tn} is clean (order-insensitive: tokensOf/cardTokens sort).
INPUTS = { grOk: { ls: 0, sk: 0, source_senses: 0, skeleton: '{T1} {T2}' } }
reset()
r = accept(card([{ german: '{T2}' }, { german: '{T1}' }]), 'grOk')
check('reordered-but-complete {Tn} multiset is not flagged', r !== null && TNMASK_MISMATCHES === 0)

// armed (owner-gated): the same dropped {Tn} now REJECTS + requeues.
TNMASK_HARD_REJECT = true
INPUTS = { gram: { ls: 0, sk: 0, source_senses: 0, skeleton: '{T1} {T2} {T3}' } }
reset()
r = accept(card([{ german: '{T1} {T3}' }]), 'gram')
check('hard: dropped {Tn} REJECTED when armed', r === null && /tnmask-reject/.test(FAIL.gram || ''))
TNMASK_HARD_REJECT = false

if (failed) { console.error(failed + ' check(s) failed'); process.exit(1) }
console.log('accept_sensecount_test: PASS')
