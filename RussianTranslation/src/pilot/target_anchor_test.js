// H3675 behavioral pin: the target-side twin of the anchored repair — a `{Tn}` span the model
// dropped from the TRANSLATION while echoing `german` faithfully. That is the half of the
// span-drop class `german_anchor` was never built to catch (FINDINGS §605/§608; the live shape
// is `hasita~~h0_zz_pw` on `no_pwg_w09`, german 2/2 · russian 1/2, which german_anchor refuses
// with `nothing-missing`). MG ruled `reanchor` over an explicit requeue on 29-08-2026.
//
// Extracts the REAL taPlan/taReanchor/taStamp AND the REAL accept() emitted by
// gen_opt_harness2.py (FINDINGS §82: never test a hand-written copy of the thing under test),
// so this cannot drift from the generator or from the Python twin it is interpolated from.
// The Python-side twin of these same cases is target_anchor.selftest().
//
//   node src/pilot/target_anchor_test.js <path-to-a-generated-harness.js>
const fs = require('fs')

const harnessPath = process.argv[2]
if (!harnessPath) { console.error('FAIL: usage: node target_anchor_test.js <harness.js>'); process.exit(1) }
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
let GERMAN_ANCHOR_INVOCATIONS = 0
const GERMAN_ANCHOR_NOT_REACHED = []
let TARGET_ANCHOR_REPAIRS = 0
let TARGET_ANCHOR_INVOCATIONS = 0
const TARGET_ANCHOR_DETAIL = []
const GA_TOKEN_RE = eval(one('GA_TOKEN_RE'))
const gaTokens = eval('(' + one('gaTokens') + ')')
const gaSenses = eval('(' + one('gaSenses') + ')')
const gaSpans = eval('(' + one('gaSpans') + ')')
const gaPlan = eval('(' + block('gaPlan') + ')')
const gaReanchor = eval('(' + block('gaReanchor') + ')')
const gaStamp = eval('(' + one('gaStamp') + ')')
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
// Each pair is one sense: [german, target].
const paired = (...pairs) => ({
  key1: 'k', iast: 'k', notes: '',
  records: [{ h: 'k', grammar: '', senses: pairs.map(([g, t], i) => ({ tag: String(i + 1), german: g, [TARGET_FIELD]: t })) }],
})
const targetsOf = c => taSenses(c).map(s => s[TARGET_FIELD])

// ==== unit: the same cases target_anchor.selftest() pins on the Python lane ================
let c, p

c = paired(['{T1} Feuer {T2}', 'огонь {T2}'])
p = taReanchor(c, TARGET_FIELD)
check('head drop: the dropped headword span is re-injected at the sense start',
  p.ok && targetsOf(c)[0] === '{T1} огонь {T2}', JSON.stringify(targetsOf(c)))

c = paired(['{T1} a {T2} Feuer {T3}', '{T1} огонь {T3}'])
p = taReanchor(c, TARGET_FIELD)
check('mid drop: anchored after its nearest surviving predecessor',
  p.ok && targetsOf(c)[0] === '{T1} {T2} огонь {T3}', JSON.stringify(targetsOf(c)))

// The property the german twin cannot offer: the anchor is per SENSE, so a span can never
// migrate between senses. It also pins the virtual-left-anchor rule -- {T3} has no surviving
// predecessor but DOES have prose ahead of it, so it goes before {T4}, not to the sense head.
c = paired(['{T1} {T2} a', '{T1} {T2} а'], ['b {T3} {T4}', 'б {T4}'])
p = taReanchor(c, TARGET_FIELD)
check('multi-sense: the drop stays in ITS sense, and anchors before its successor',
  p.ok && JSON.stringify(targetsOf(c)) === JSON.stringify(['{T1} {T2} а', 'б {T3} {T4}']),
  JSON.stringify(targetsOf(c)))

// The SENSE END is the second virtual anchor: it is nearer than the surviving predecessor,
// so the citation lands after the prose it belongs to. german_anchor, which has no per-sense
// end to measure to, would give `{T1} {T2} огонь` here.
c = paired(['{T1} Feuer {T2}', '{T1} огонь'])
p = taReanchor(c, TARGET_FIELD)
check('tail drop: anchored at the sense END, not after its predecessor',
  p.ok && targetsOf(c)[0] === '{T1} огонь {T2}', JSON.stringify(targetsOf(c)))

c = paired(['{T1} a {T2}', 'а'])
p = taReanchor(c, TARGET_FIELD)
check('a sense with no survivors still splits head/tail by the same measure',
  p.ok && targetsOf(c)[0] === '{T1} а {T2}', JSON.stringify(targetsOf(c)))

for (const [german, target, reason] of [
  ['{T1} {T2}', '{T1} {T9}', 'foreign-token'],
  ['{T1} {T2}', '{T1} {T1}', 'duplicate-token'],
  ['{T1} {T2}', '{T2} {T1}', 'reordered-token'],
  ['{T1} {T2}', '{T1} {T2}', 'nothing-missing'],
  ['{T1} {T1}', '{T1}', 'anchor-token-repeat'],
]) {
  const r = taReanchor(paired([german, target]), TARGET_FIELD)
  check('refused (' + reason + '): anything that is not a pure drop is left to the reject',
    !r.ok && r.reason === reason, JSON.stringify(r))
}
check('refused (no-senses)', !taReanchor({ key1: 'k', records: [] }, TARGET_FIELD).ok)

c = paired(['{T1} Feuer', 'огонь'], ['{T2} Glut', '{T2} жар'])
p = taReanchor(c, TARGET_FIELD)
check('a sense that kept NO span: its spans go to the head of THAT sense, not of the card',
  p.ok && JSON.stringify(targetsOf(c)) === JSON.stringify(['{T1} огонь', '{T2} жар']),
  JSON.stringify(targetsOf(c)))

c = paired(['{T1} Feuer {T2}', 'огонь {T2}'])
const germanBefore = JSON.stringify(taSenses(c).map(s => s.german))
taReanchor(c, TARGET_FIELD)
check('the german field is the anchor and is never written',
  JSON.stringify(taSenses(c).map(s => s.german)) === germanBefore)

check('the stamp never carries braces (it must not read as a {Tn} residue downstream)',
  JSON.stringify(taStamp(taPlan(paired(['{T1} a', 'а']), TARGET_FIELD))) === JSON.stringify({ reinjected: ['T1'], head: ['T1'] }))

// ==== accept()-level: the real class, end to end through the real restore ==================
// `hasita` shape: german echo faithful, translation short one <ls>. Pre-H3675 this nulled the
// card at translation-fidelity-reject and no repair was ever reached.
const reset = () => {
  GERMAN_ANCHOR_REPAIRS = 0; GERMAN_ANCHOR_DETAIL.length = 0
  GERMAN_ANCHOR_INVOCATIONS = 0; GERMAN_ANCHOR_NOT_REACHED.length = 0
  TARGET_ANCHOR_REPAIRS = 0; TARGET_ANCHOR_INVOCATIONS = 0; TARGET_ANCHOR_DETAIL.length = 0
  for (const k in FAIL) delete FAIL[k]
}
const masked = (german, translation) => ({
  key1: 'av', iast: 'av', notes: '',
  records: [{ h: 'av', grammar: '', senses: [{ tag: '1', german: german, [TARGET_FIELD]: translation }] }],
})
INPUTS = { av: { ls: 1, sk: 1, source_senses: 1, skeleton: '{T1} unverwirrt {T2}' } }
PH = { av: ['{#avyagra#}', '<ls>ṚV. 1,1</ls>'] }

reset()
let r = accept(masked('{T1} unverwirrt {T2}', '{T1} невозмутимый'), 'av')
check('accept(): a span dropped from the TRANSLATION is REPAIRED, not nulled',
  r !== null && FAIL.av === undefined, JSON.stringify(FAIL))
check('accept(): the repaired translation carries the real restored span',
  r && r.records[0].senses[0][TARGET_FIELD] === '{#avyagra#} невозмутимый <ls>ṚV. 1,1</ls>',
  r && JSON.stringify(r.records[0].senses[0][TARGET_FIELD]))
check('accept(): the repair is stamped on the card (never silently patched)',
  r && r.target_anchor && JSON.stringify(r.target_anchor.reinjected) === JSON.stringify(['T2']),
  r && JSON.stringify(r.target_anchor))
check('accept(): the repair is counted in the window telemetry',
  TARGET_ANCHOR_REPAIRS === 1 && TARGET_ANCHOR_INVOCATIONS === 1
    && TARGET_ANCHOR_DETAIL[0] && TARGET_ANCHOR_DETAIL[0].key === 'av',
  JSON.stringify(TARGET_ANCHOR_DETAIL))

// CONTROL 1: a faithful card is byte-untouched, never stamped, and never invokes the repair.
reset()
r = accept(masked('{T1} unverwirrt {T2}', '{T1} невозмутимый {T2}'), 'av')
check('accept(): a faithful card is untouched, unstamped, and does not invoke the repair',
  r !== null && r.target_anchor === undefined && TARGET_ANCHOR_INVOCATIONS === 0)

// CONTROL 2: a target that is not a pure drop still rejects, with the reason recorded.
reset()
r = accept(masked('{T1} unverwirrt {T2}', '{T1} {T1} невозмутимый {T2}'), 'av')
check('accept(): a duplicated target span is refused repair and still rejects, reason recorded',
  r === null && /target-anchor duplicate-token/.test(FAIL.av || ''), JSON.stringify(FAIL))
check('accept(): a refused target repair still counts its invocation (0 repairs, 1 invocation)',
  TARGET_ANCHOR_REPAIRS === 0 && TARGET_ANCHOR_INVOCATIONS === 1,
  JSON.stringify({ repairs: TARGET_ANCHOR_REPAIRS, invocations: TARGET_ANCHOR_INVOCATIONS }))

// CONTROL 3: dropped on BOTH sides -- the german repair runs first, the target repair anchors
// against the german it just fixed, and BOTH stamps survive the second restore.
reset()
r = accept(masked('unverwirrt {T2}', 'невозмутимый'), 'av')
check('accept(): a card dropped on both sides is repaired twice and keeps BOTH stamps',
  r !== null && FAIL.av === undefined && r.german_anchor && r.target_anchor
    && GERMAN_ANCHOR_REPAIRS === 1 && TARGET_ANCHOR_REPAIRS === 1,
  JSON.stringify({ fail: FAIL.av, german: r && r.german_anchor, target: r && r.target_anchor }))
check('accept(): both fields carry the real restored spans after the double repair',
  r && r.records[0].senses[0].german === '{#avyagra#} unverwirrt <ls>ṚV. 1,1</ls>'
    && r.records[0].senses[0][TARGET_FIELD] === '{#avyagra#} невозмутимый <ls>ṚV. 1,1</ls>',
  r && JSON.stringify([r.records[0].senses[0].german, r.records[0].senses[0][TARGET_FIELD]]))

if (failed) { console.error(failed + ' check(s) failed'); process.exit(1) }
console.log('target_anchor_test: PASS')
