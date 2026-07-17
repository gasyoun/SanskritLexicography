// H960 behavioral test for the accept() SAN-LOSS shortfall guard (H920's deferred deepest fix)
// AND (H1152) the translation-field fidelity guard closing the countOf()-reads-only-`german`
// gap (H1070 r102: a {#uc#} span inside a <F> footnote survived the `german` echo but was
// silently dropped from `english`, invisible to a guard that never inspected the translation).
// Extracts the REAL accept() + countOf + countOfField emitted by gen_opt_harness2.py (so this
// can't drift from the generator) and asserts, with restoreCard mocked to identity and fixtures
// that are already "restored" cards:
//   - the NEW translation-fidelity check rejects when the target-language field's <ls>/{#..#}
//     counts don't match the source, even though the `german` echo is fully faithful (the
//     exact r102 shape) — and it fires BEFORE the SAN-LOSS/{Tn}-multiset guards below it;
//   - a card whose translation field faithfully mirrors `german` is unaffected (no new FPs);
//   - SOFT (default SANLOSS_HARD_REJECT=false): a darvI 2/3 shortfall is COUNTED but the card is
//     KEPT (not rejected), the ls/sk fidelity gates having passed;
//   - a complete card and a surplus (emitted>expected) split are never flagged;
//   - FP-regression: a cross-reference card whose hardened source_senses==0 is skipped entirely;
//   - the ls/sk fidelity-reject still fires FIRST, before the sanloss guard;
//   - HARD (owner-gated flip SANLOSS_HARD_REJECT=true): the same shortfall now REJECTS + requeues.
//   node src/pilot/accept_sensecount_test.js <path-to-a-generated-harness.js>
const fs = require('fs')

const harnessPath = process.argv[2]
if (!harnessPath) { console.error('FAIL: usage: node accept_sensecount_test.js <harness.js>'); process.exit(1) }
const src = fs.readFileSync(harnessPath, 'utf8')

// Pull countOf/countOfField/tokensOf/cardTokens/TARGET_FIELD (one-liners) and accept (brace
// block to the first column-0 `\n}`) verbatim from the generated harness so this can't drift.
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
const countOfField = eval('(' + one('countOfField') + ')')
const TARGET_FIELD = eval(one('TARGET_FIELD'))
const tokensOf = eval('(' + one('tokensOf') + ')')
const cardTokens = eval('(' + one('cardTokens') + ')')
const accept = eval('(' + am[0].replace(/^const accept = /, '') + ')')

let failed = 0
const check = (name, cond, extra) => { if (cond) { console.log('PASS: ' + name) } else { console.error('FAIL: ' + name + (extra ? ' -- ' + extra : '')); failed++ } }
// `sense(german, translation)` builds a sense object with `german` AND the harness's actual
// target-language field populated — defaulting the translation to an identical copy of
// `german` (matching {#..#}/<ls> counts) unless a fixture explicitly wants them to diverge
// (the guard-2 shape). Every pre-H1152 fixture below used `{ german }` alone, which the new
// translation-fidelity check would now reject wholesale (translation field absent -> 0 counts
// != source expectation) -- `sense()` keeps those fixtures' original intent (test some OTHER
// guard) by making the translation field trivially faithful, and only the new guard-2 fixtures
// pass a distinct, deliberately-lossy `translation` argument.
const sense = (german, translation) => ({ german, [TARGET_FIELD]: translation !== undefined ? translation : german })
const card = senses => ({ records: [{ senses }] })
const reset = () => {
  SANLOSS_SHORTFALLS = 0; SANLOSS_DETAIL.length = 0
  TNMASK_MISMATCHES = 0; TNMASK_DETAIL.length = 0
  for (const k in FAIL) delete FAIL[k]
}
let r

// ==== H1152 guard 2: translation-field fidelity ====================================
// r102 shape: `german` is fully faithful (matches INPUTS[k].sk/ls exactly) but the
// TARGET_FIELD translation drops one {#..#} span. Must REJECT with 'translation-fidelity-reject',
// even though the pre-existing `german`-echo check (ls/sk) passes clean.
// (only ONE of two {#..#} spans is missing from the translation — mirrors r102 exactly:
// a partial, single-span drop, not a wholesale loss of every span.)
INPUTS = { r102: { ls: 0, sk: 2, source_senses: 1 } }
reset()
r = accept(card([sense('{#Ucize#} {#uc#} ziehen zu müssen',
                        '{#Ucize#} must be drawn in')]), 'r102')
check('guard 2: translation-only {#uc#} drop is REJECTED (german echo was clean)',
  r === null && /translation-fidelity-reject/.test(FAIL.r102 || ''), JSON.stringify(FAIL))
check('guard 2: rejected BEFORE the SAN-LOSS guard ever counts it', SANLOSS_SHORTFALLS === 0)

// Same shape for <ls>: the citation survives in `german` but is dropped from the translation.
INPUTS = { r102b: { ls: 1, sk: 0, source_senses: 1 } }
reset()
r = accept(card([sense('gloss <ls>ṚV. 1,1</ls>', 'gloss, citation dropped')]), 'r102b')
check('guard 2: translation-only <ls> drop is REJECTED',
  r === null && /translation-fidelity-reject/.test(FAIL.r102b || ''), JSON.stringify(FAIL))

// CONTROL: a faithful translation (spans preserved, prose differs) is NOT flagged.
INPUTS = { faithful: { ls: 1, sk: 1, source_senses: 1 } }
reset()
r = accept(card([sense('gloss {#kar#} <ls>ṚV. 1,1</ls>', 'gloss {#kar#} <ls>ṚV. 1,1</ls>, reworded')]), 'faithful')
check('guard 2: a faithful translation (same spans, different prose) is not flagged', r !== null)

// CONTROL: a card whose `german` echo is ALREADY broken still rejects on the pre-existing
// echo check first (unchanged ordering/message), never masked by the new guard.
INPUTS = { echoBroken: { ls: 0, sk: 1, source_senses: 1 } }
reset()
r = accept(card([sense('no citation here', 'no citation here')]), 'echoBroken')   // german sk 0 != 1
check('pre-existing german-echo fidelity-reject still fires (unchanged)',
  r === null && /^fidelity-reject/.test(FAIL.echoBroken || ''), JSON.stringify(FAIL))

// ==== SOFT (default): shortfall recorded, card KEPT ====================================
// darvI 2/3: source declares 3 senses, model emits 2; ls 0==0 and sk 3==3 (the two {#..#}-carrying
// senses survive, in BOTH german and the translation), so the <ls>/{# fidelity gates pass and
// only the sense-count guard can see it.
INPUTS = { darvI: { ls: 0, sk: 3, source_senses: 3 } }
reset()
r = accept(card([sense('{#a#} {#b#}'), sense('{#c#}')]), 'darvI')
check('soft: darvI 2/3 shortfall is KEPT (not rejected)', r !== null)
check('soft: darvI shortfall counted with dropped=1',
  SANLOSS_SHORTFALLS === 1 && SANLOSS_DETAIL[0] && SANLOSS_DETAIL[0].dropped === 1, JSON.stringify(SANLOSS_DETAIL))
check('soft: no FAIL recorded for a kept shortfall', FAIL.darvI === undefined)

// complete 3/3: no shortfall.
INPUTS = { ok: { ls: 0, sk: 0, source_senses: 3 } }
reset()
r = accept(card([sense('a'), sense('b'), sense('c')]), 'ok')
check('complete card passes with no shortfall', r !== null && SANLOSS_SHORTFALLS === 0)

// surplus 3 > 2: a faithful split that yields MORE senses is never flagged.
INPUTS = { sur: { ls: 0, sk: 0, source_senses: 2 } }
reset()
r = accept(card([sense('a'), sense('b'), sense('c')]), 'sur')
check('surplus (emitted>expected) is not flagged', r !== null && SANLOSS_SHORTFALLS === 0)

// ---- FP-regression: a cross-reference card (hardened source_senses==0) never fires ----
// gam~~h2_31_pari / _a_srayatva shape: the source's only ordinals are cross-references, so the
// H960-hardened counter stamps source_senses=0 and the exp<1 skip keeps the guard silent.
INPUTS = { xref: { ls: 0, sk: 0, source_senses: 0 } }
reset()
r = accept(card([sense('single unnumbered sense')]), 'xref')
check('FP-regression: exp=0 cross-ref card is skipped (never flagged)', r !== null && SANLOSS_SHORTFALLS === 0)

// ---- ls/sk fidelity-reject still fires FIRST, before the sanloss guard ----
INPUTS = { mis: { ls: 1, sk: 0, source_senses: 1 } }
reset()
r = accept(card([sense('no citation here')]), 'mis')   // ls 0 != expected 1 (both fields)
check('ls/sk fidelity-reject still fires first',
  r === null && /fidelity-reject/.test(FAIL.mis || '') && SANLOSS_SHORTFALLS === 0)

// ---- HARD (owner-gated flip): the same shortfall now REJECTS + requeues ----
SANLOSS_HARD_REJECT = true
INPUTS = { darvI: { ls: 0, sk: 3, source_senses: 3 } }
reset()
r = accept(card([sense('{#a#} {#b#}'), sense('{#c#}')]), 'darvI')
check('hard: darvI 2/3 shortfall REJECTED when armed',
  r === null && /sanloss-reject/.test(FAIL.darvI || ''))
SANLOSS_HARD_REJECT = false

// ---- H960 grammar-{Tn} multiset guard (soft) ----
// A dropped grammar <lex> {Tn}: the source skeleton masks 3 spans ({T1} grammar, {T2}, {T3}),
// the model keeps {T1} {T3} but drops {T2}. It carries neither an <ls> nor a {#, so the ls/sk
// count check passes (0==0) while the {Tn} multiset differs — the exact gap this guard closes.
INPUTS = { gram: { ls: 0, sk: 0, source_senses: 0, skeleton: '{T1} {T2} {T3}' } }
reset()
r = accept(card([sense('{T1} {T3}')]), 'gram')
check('soft: dropped grammar {Tn} is KEPT but counted', r !== null && TNMASK_MISMATCHES === 1,
  'mismatches=' + TNMASK_MISMATCHES)
check('soft: the ls/sk count check is blind to the dropped {Tn} (no FAIL)', FAIL.gram === undefined)
check('soft: {Tn} mismatch detail records got/want',
  TNMASK_DETAIL[0] && TNMASK_DETAIL[0].got === '{T1} {T3}' && TNMASK_DETAIL[0].want === '{T1} {T2} {T3}',
  JSON.stringify(TNMASK_DETAIL))

// a card that keeps every {Tn} is clean (order-insensitive: tokensOf/cardTokens sort).
INPUTS = { grOk: { ls: 0, sk: 0, source_senses: 0, skeleton: '{T1} {T2}' } }
reset()
r = accept(card([sense('{T2}'), sense('{T1}')]), 'grOk')
check('reordered-but-complete {Tn} multiset is not flagged', r !== null && TNMASK_MISMATCHES === 0)

// armed (owner-gated): the same dropped {Tn} now REJECTS + requeues.
TNMASK_HARD_REJECT = true
INPUTS = { gram: { ls: 0, sk: 0, source_senses: 0, skeleton: '{T1} {T2} {T3}' } }
reset()
r = accept(card([sense('{T1} {T3}')]), 'gram')
check('hard: dropped {Tn} REJECTED when armed', r === null && /tnmask-reject/.test(FAIL.gram || ''))
TNMASK_HARD_REJECT = false

// ---- D-Q (H994): a RELIABLE silent-SAN-LOSS canary — dropping ANY sense stays fidelity-clean ----
// darvI is an UNRELIABLE canary (see the contrast below): only its pure-gloss senses are silently
// droppable, and the model may instead drop its {#-carrying sense -> fidelity-REJECT, not a silent
// loss. The reliable canary rung-3 needs has N pure-gloss senses and ZERO <ls>/{# (INPUTS ls:0 sk:0):
// the ls/sk gate is 0==0 whichever sense is dropped, so the sense-count guard is the ONLY thing that
// can catch the loss. Proven here against the REAL accept(): every drop is silent+counted, faithful
// is clean, and (contrast) the darvI {#-drop rejects.
INPUTS = { canary: { ls: 0, sk: 0, source_senses: 3 } }
reset()
r = accept(card([sense('a'), sense('b'), sense('c')]), 'canary')
check('D-Q canary: faithful 3/3 is clean (no false SANLOSS)', r !== null && SANLOSS_SHORTFALLS === 0)
for (const [label, senses] of [
  ['drop 1st', [sense('b'), sense('c')]],
  ['drop middle', [sense('a'), sense('c')]],
  ['drop last', [sense('a'), sense('b')]],
]) {
  reset()
  r = accept(card(senses), 'canary')
  check('D-Q canary: ' + label + ' sense -> KEPT, fidelity-clean, SANLOSS fires (dropped=1)',
    r !== null && FAIL.canary === undefined && SANLOSS_SHORTFALLS === 1 &&
    SANLOSS_DETAIL[0] && SANLOSS_DETAIL[0].dropped === 1, JSON.stringify(SANLOSS_DETAIL))
}
reset()
r = accept(card([sense('a')]), 'canary')   // drop TWO of three
check('D-Q canary: drop 2 senses -> KEPT, dropped=2',
  r !== null && SANLOSS_SHORTFALLS === 1 && SANLOSS_DETAIL[0] && SANLOSS_DETAIL[0].dropped === 2)

// contrast: darvI is UNRELIABLE. Its raw is ls:0 sk:1 (only sense 3 carries {#darvI#}),
// source_senses:3. If the model drops the {#-bearing sense (not a gloss sense) the emitted {# count
// is 0 != 1 -> fidelity-REJECT fires FIRST, so it is NOT a silent SAN-LOSS. darvI reproduces the
// silent shape only on the specific gloss-sense drops -> exactly why it is a poor rung-3 canary.
INPUTS = { darvIreal: { ls: 0, sk: 1, source_senses: 3 } }
reset()
r = accept(card([sense('a'), sense('b')]), 'darvIreal')   // dropped the {#-bearing sense
check('contrast: darvI dropping its {#-sense fidelity-REJECTS (not a silent loss)',
  r === null && /fidelity-reject/.test(FAIL.darvIreal || '') && SANLOSS_SHORTFALLS === 0)

if (failed) { console.error(failed + ' check(s) failed'); process.exit(1) }
console.log('accept_sensecount_test: PASS')
