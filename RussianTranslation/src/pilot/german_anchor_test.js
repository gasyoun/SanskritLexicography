// H858 Part B behavioral pin: the anchored repair of a masked span the model dropped from its
// `german` echo — the dominant retry-RESISTANT null class (6 of 7 residual nulls in no_pwg_w10,
// H1283; `asaMskfta` `avyAhata` `avyagra` `darvI` `glAna` `hasita` at `{# 0/1`, `1/2`, `1/3`).
//
// Extracts the REAL gaPlan/gaReanchor/gaStamp AND the REAL accept() emitted by
// gen_opt_harness2.py (FINDINGS §82: never test a hand-written copy of the thing under test),
// so this cannot drift from the generator or from the Python twin it is interpolated from.
// The Python-side twin of these same cases is german_anchor.selftest().
//
//   node src/pilot/german_anchor_test.js <path-to-a-generated-harness.js>
const fs = require('fs')

const harnessPath = process.argv[2]
if (!harnessPath) { console.error('FAIL: usage: node german_anchor_test.js <harness.js>'); process.exit(1) }
const src = fs.readFileSync(harnessPath, 'utf8')

const one = name => {
  const m = src.match(new RegExp('const ' + name + ' = [^\\n]*'))
  if (!m) { console.error('FAIL: ' + name + ' not found in ' + harnessPath); process.exit(1) }
  return m[0].replace(new RegExp('^const ' + name + ' = '), '')
}
const block = name => {
  const m = src.match(new RegExp('const ' + name + ' = \\([^)]*\\) => \\{[\\s\\S]*?\\n\\}'))
  if (!m) { console.error('FAIL: ' + name + ' not found in ' + harnessPath); process.exit(1) }
  return m[0].replace(new RegExp('^const ' + name + ' = '), '')
}
const am = src.match(/const accept = \(c, k\) => \{[\s\S]*?\n\}/)
if (!am) { console.error('FAIL: accept not found in ' + harnessPath); process.exit(1) }

// Runtime globals the extracted functions close over.
let INPUTS = {}
let PH = {}
const FAIL = {}
const noteFail = (k, why) => { FAIL[k] = String(why).slice(0, 300) }
const log = () => {}
let SANLOSS_HARD_REJECT = false
let SANLOSS_SHORTFALLS = 0
const SANLOSS_DETAIL = []
let TNMASK_HARD_REJECT = false
let TNMASK_MISMATCHES = 0
const TNMASK_DETAIL = []
let GERMAN_ANCHOR_REPAIRS = 0
const GERMAN_ANCHOR_DETAIL = []
let TARGET_ANCHOR_REPAIRS = 0            // H3675: accept() now runs a target-side repair too
let TARGET_ANCHOR_INVOCATIONS = 0
const TARGET_ANCHOR_DETAIL = []
let GERMAN_ANCHOR_INVOCATIONS = 0        // H3665: was the repair even reached?
const GERMAN_ANCHOR_NOT_REACHED = []     // H3665: cards nulled by a LATER guard
const GA_TOKEN_RE = eval(one('GA_TOKEN_RE'))
const gaTokens = eval('(' + one('gaTokens') + ')')
const gaSenses = eval('(' + one('gaSenses') + ')')
const gaSpans = eval('(' + one('gaSpans') + ')')
const gaPlan = eval('(' + block('gaPlan') + ')')
const gaReanchor = eval('(' + block('gaReanchor') + ')')
const gaStamp = eval('(' + one('gaStamp') + ')')
// H3675: accept() now also runs the target-side repair, so its twin must be extracted too.
const TA_TOKEN_RE = eval(one('TA_TOKEN_RE'))
const taTokens = eval('(' + one('taTokens') + ')')
const taSenses = eval('(' + one('taSenses') + ')')
const taSpans = eval('(' + one('taSpans') + ')')
const taPlan = eval('(' + block('taPlan') + ')')
const taReanchor = eval('(' + block('taReanchor') + ')')
const taStamp = eval('(' + one('taStamp') + ')')
// The REAL restore machinery, so the accept()-level cases below run the true masked -> restored
// round trip rather than an identity mock (this is what proves the repair lands a real citation).
const RESTORE_SPEC = eval('(' + one('RESTORE_SPEC') + ')')
const restore = eval('(' + one('restore') + ')')
const rcM = src.match(/function restoreCard\([\s\S]*?\n\}/)
if (!rcM) { console.error('FAIL: restoreCard not found in ' + harnessPath); process.exit(1) }
const restoreCard = eval('(' + rcM[0].replace(/^function restoreCard/, 'function ') + ')')
const countOf = eval('(' + one('countOf') + ')')
const countOfField = eval('(' + one('countOfField') + ')')
const TARGET_FIELD = eval(one('TARGET_FIELD'))
const tokensOf = eval('(' + one('tokensOf') + ')')
const TOKEN_FIDELITY_SPEC = eval('(' + one('TOKEN_FIDELITY_SPEC') + ')')
const cardTokens = eval('(' + one('cardTokens') + ')')
const accept = eval('(' + am[0].replace(/^const accept = /, '') + ')')

let failed = 0
const check = (name, cond, extra) => { if (cond) { console.log('PASS: ' + name) } else { console.error('FAIL: ' + name + (extra ? ' -- ' + extra : '')); failed++ } }
const one_sense_card = (...germans) => ({
  key1: 'k', iast: 'k', notes: '',
  records: [{ h: 'k', grammar: '', senses: germans.map((g, i) => ({ tag: String(i + 1), german: g, [TARGET_FIELD]: 'x' })) }],
})
const germansOf = c => gaSenses(c).map(s => s.german)

// ==== unit: the same 8 cases german_anchor.selftest() pins on the Python lane ==============
let c, p

c = one_sense_card('Feuer {T2}')
p = gaReanchor(c, '{T1} Feuer {T2}')
check('head drop: the dropped headword span is re-injected at the card start',
  p.ok && germansOf(c)[0] === '{T1} Feuer {T2}', JSON.stringify(germansOf(c)))

c = one_sense_card('{T1} Feuer {T3}')
p = gaReanchor(c, '{T1} a {T2} Feuer {T3}')
check('mid drop: anchored after its nearest surviving predecessor',
  p.ok && germansOf(c)[0] === '{T1} {T2} Feuer {T3}', JSON.stringify(germansOf(c)))

c = one_sense_card('{T1} a', 'b {T4}')
p = gaReanchor(c, '{T1} {T2} a — b {T3} {T4}')
check('multi-sense: nearest-neighbour keeps each drop in the RIGHT sense',
  p.ok && JSON.stringify(germansOf(c)) === JSON.stringify(['{T1} {T2} a', 'b {T3} {T4}']),
  JSON.stringify(germansOf(c)))

c = one_sense_card('{T1} Feuer')
p = gaReanchor(c, '{T1} Feuer {T2}')
check('tail drop: anchored after the last surviving span',
  p.ok && germansOf(c)[0] === '{T1} {T2} Feuer', JSON.stringify(germansOf(c)))

for (const [german, skeleton, reason] of [
  ['{T1} {T9}', '{T1} {T2}', 'foreign-token'],
  ['{T1} {T1}', '{T1} {T2}', 'duplicate-token'],
  ['{T2} {T1}', '{T1} {T2}', 'reordered-token'],
  ['{T1} {T2}', '{T1} {T2}', 'nothing-missing'],
  ['{T1}', '{T1} {T1}', 'source-token-repeat'],
]) {
  p = gaReanchor(one_sense_card(german), skeleton)
  check('refused (' + reason + '): anything that is not a pure drop is left to the reject',
    !p.ok && p.reason === reason, JSON.stringify(p))
}
p = gaReanchor({ records: [] }, '{T1}')
check('refused (no-senses)', !p.ok && p.reason === 'no-senses', JSON.stringify(p))

c = one_sense_card('Feuer', 'Glut')
p = gaReanchor(c, '{T1} Feuer {T2} Glut')
check('a card that kept NO span: every span goes to the head of the first sense',
  p.ok && JSON.stringify(germansOf(c)) === JSON.stringify(['{T1} {T2} Feuer', 'Glut']),
  JSON.stringify(germansOf(c)))

c = one_sense_card('a {T2} b', 'c')
p = gaReanchor(c, '{T1} a {T2} b {T3} c {T4}')
check('after repair the token multiset equals the source exactly',
  p.ok && gaSenses(c).map(s => gaTokens(s.german)).flat().sort().join(' ') === '{T1} {T2} {T3} {T4}',
  JSON.stringify(germansOf(c)))

check('the stamp never carries braces (it must not read as a {Tn} residue downstream)',
  JSON.stringify(gaStamp(gaPlan(one_sense_card('a'), '{T1} a'))) === JSON.stringify({ reinjected: ['T1'], head: ['T1'] }))

// ==== accept()-level: the real null class, end to end through the real restore ============
// `avyagra` shape: source has one {#..#} span (the headword) and one <ls>; the model's german
// echo drops the {#..#}. Pre-H858 this nulled the card ({# 0/1) and a requeue reproduced it.
const reset = () => { GERMAN_ANCHOR_REPAIRS = 0; GERMAN_ANCHOR_DETAIL.length = 0; GERMAN_ANCHOR_INVOCATIONS = 0; GERMAN_ANCHOR_NOT_REACHED.length = 0; TARGET_ANCHOR_REPAIRS = 0; TARGET_ANCHOR_INVOCATIONS = 0; TARGET_ANCHOR_DETAIL.length = 0; for (const k in FAIL) delete FAIL[k] }
const masked = (german, translation) => ({
  key1: 'av', iast: 'av', notes: '',
  records: [{ h: 'av', grammar: '', senses: [{ tag: '1', german: german, [TARGET_FIELD]: translation }] }],
})
INPUTS = { av: { ls: 1, sk: 1, source_senses: 1, skeleton: '{T1} unverwirrt {T2}' } }
PH = { av: ['{#avyagra#}', '<ls>ṚV. 1,1</ls>'] }

reset()
let r = accept(masked('unverwirrt {T2}', '{T1} невозмутимый {T2}'), 'av')
check('accept(): a {#..#} span dropped from the german echo is REPAIRED, not nulled',
  r !== null && FAIL.av === undefined, JSON.stringify(FAIL))
check('accept(): the repaired german carries the real restored span',
  r && r.records[0].senses[0].german === '{#avyagra#} unverwirrt <ls>ṚV. 1,1</ls>',
  r && JSON.stringify(r.records[0].senses[0].german))
check('accept(): the repair is stamped on the card (never silently patched)',
  r && r.german_anchor && JSON.stringify(r.german_anchor.reinjected) === JSON.stringify(['T1']),
  r && JSON.stringify(r.german_anchor))
check('accept(): the repair is counted in the window telemetry',
  GERMAN_ANCHOR_REPAIRS === 1 && GERMAN_ANCHOR_DETAIL[0] && GERMAN_ANCHOR_DETAIL[0].key === 'av',
  JSON.stringify(GERMAN_ANCHOR_DETAIL))

// CONTROL 1: a faithful card is byte-untouched and never stamped.
reset()
r = accept(masked('{T1} unverwirrt {T2}', '{T1} невозмутимый {T2}'), 'av')
check('accept(): a faithful card is untouched and carries NO repair stamp',
  r !== null && r.german_anchor === undefined && GERMAN_ANCHOR_REPAIRS === 0)

// CONTROL 2: the german repair must not by itself launder a TRANSLATION-side drop. Since
// H3675 the card IS saved -- by the target-side twin, which stamps itself separately -- so
// what this control now pins is that the two repairs stay distinct and both are recorded.
// The target twin's own behavioural pin is target_anchor_test.js.
reset()
r = accept(masked('unverwirrt {T2}', 'невозмутимый {T2}'), 'av')
check('accept(): a german-side repair does not silently cover a translation-side drop',
  r !== null && r.german_anchor && r.target_anchor
    && JSON.stringify(r.german_anchor.reinjected) === JSON.stringify(['T1'])
    && JSON.stringify(r.target_anchor.reinjected) === JSON.stringify(['T1']),
  JSON.stringify({ german: r && r.german_anchor, target: r && r.target_anchor, fail: FAIL.av }))

// CONTROL 2b (H3665): the shape that made `german_anchor_repairs: 0` unfalsifiable. The german
// echo is FAITHFUL and only the translation dropped the span, so accept() never enters the
// repair branch at all -- repairs 0 AND invocations 0, exactly like a clean window. The
// not_reached list is the only thing that tells the two apart. Python twin:
// headless_worker_selftest.test_h3665_german_anchor_counter_is_falsifiable.
reset()
r = accept(masked('{T1} unverwirrt {T2}', '{T1} {T1} невозмутимый {T2}'), 'av')
check('accept(): a translation-side failure is NAMED as never having reached the german repair',
  r === null && /translation-fidelity-reject/.test(FAIL.av || '')
    && GERMAN_ANCHOR_REPAIRS === 0 && GERMAN_ANCHOR_INVOCATIONS === 0
    && JSON.stringify(GERMAN_ANCHOR_NOT_REACHED) === JSON.stringify(['av']),
  JSON.stringify({ fail: FAIL.av, repairs: GERMAN_ANCHOR_REPAIRS,
                   invocations: GERMAN_ANCHOR_INVOCATIONS, notReached: GERMAN_ANCHOR_NOT_REACHED }))

// CONTROL 2c (H3665): a german-side drop that IS repaired counts as an invocation and is
// absent from not_reached -- so invocations can never be read as "something went wrong".
reset()
r = accept(masked('unverwirrt {T2}', '{T1} невозмутимый {T2}'), 'av')
check('accept(): a repaired card counts one invocation and nothing not-reached',
  r !== null && GERMAN_ANCHOR_INVOCATIONS === 1 && GERMAN_ANCHOR_NOT_REACHED.length === 0,
  JSON.stringify({ invocations: GERMAN_ANCHOR_INVOCATIONS, notReached: GERMAN_ANCHOR_NOT_REACHED }))

// CONTROL 3: a card whose german is not a pure drop still rejects, with the reason recorded.
reset()
r = accept(masked('{T2} unverwirrt {T2}', '{T1} невозмутимый {T2}'), 'av')
check('accept(): a duplicated span is refused repair and still rejects, reason recorded',
  r === null && /german-anchor duplicate-token/.test(FAIL.av || ''), JSON.stringify(FAIL))

if (failed) { console.error(failed + ' check(s) failed'); process.exit(1) }
console.log('german_anchor_test: PASS')
