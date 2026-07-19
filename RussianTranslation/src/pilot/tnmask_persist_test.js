// H1226 behavioral test: accept() PERSISTS the pre-restore {Tn} pairing on the accepted card
// (`c.tnmask = { got, want }`), so a SOFT (un-rejected) TNMASK expansion becomes measurable
// offline from a promoted row. H1150 returned DO_NOT_ARM (denominator 1) precisely because the
// store dropped this transient pairing.
//
// Like accept_sensecount_test.js, this extracts the REAL accept()/tokensOf/cardTokens/
// TOKEN_FIDELITY_SPEC/countOf/countOfField/TARGET_FIELD/RESTORE_SPEC verbatim from a freshly
// generated harness (so it cannot drift from the generator), mocks restoreCard to identity, and
// asserts on the pairing the real accept() stamps.
//   node src/pilot/tnmask_persist_test.js <path-to-a-generated-harness.js>
const fs = require('fs')

const harnessPath = process.argv[2]
if (!harnessPath) { console.error('FAIL: usage: node tnmask_persist_test.js <harness.js>'); process.exit(1) }
const src = fs.readFileSync(harnessPath, 'utf8')

const one = name => {
  const m = src.match(new RegExp('const ' + name + ' = [^\\n]*'))
  if (!m) { console.error('FAIL: ' + name + ' not found in ' + harnessPath); process.exit(1) }
  return m[0].replace(new RegExp('^const ' + name + ' = '), '')
}
const am = src.match(/const accept = \(c, k\) => \{[\s\S]*?\n\}/)
if (!am) { console.error('FAIL: accept not found in ' + harnessPath); process.exit(1) }

// Runtime globals accept() closes over (all mocked). restoreCard = identity because the fixtures
// are already-restored cards; the pairing is stamped BEFORE restore, so identity is faithful here.
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
const countOf = eval('(' + one('countOf') + ')')
const countOfField = eval('(' + one('countOfField') + ')')
const TARGET_FIELD = eval(one('TARGET_FIELD'))
const tokensOf = eval('(' + one('tokensOf') + ')')
const TOKEN_FIDELITY_SPEC = eval('(' + one('TOKEN_FIDELITY_SPEC') + ')')
const cardTokens = eval('(' + one('cardTokens') + ')')
const RESTORE_SPEC = eval('(' + one('RESTORE_SPEC') + ')')
const accept = eval('(' + am[0].replace(/^const accept = /, '') + ')')

let failed = 0
const check = (name, cond, extra) => { if (cond) { console.log('PASS: ' + name) } else { console.error('FAIL: ' + name + (extra ? ' -- ' + extra : '')); failed++ } }
const sense = (german, translation) => ({ german, [TARGET_FIELD]: translation !== undefined ? translation : german })
const card = senses => ({ records: [{ senses }] })
const reset = () => {
  SANLOSS_SHORTFALLS = 0; SANLOSS_DETAIL.length = 0
  TNMASK_MISMATCHES = 0; TNMASK_DETAIL.length = 0
  for (const k in FAIL) delete FAIL[k]
}
let r

// ==== EXPANSION: candidate drops a masked {Tn} (a soft TNMASK flag) ====================
// Skeleton masks {T1} {T2} {T3}; the model self-expands {T2} to literal markup and emits only
// {T1} {T3}. ls/sk are 0 so the fidelity gates pass and the card is KEPT (soft) -- exactly the
// population whose false-flag rate H1150 could not measure. The stamped pairing must record it.
INPUTS = { exp: { ls: 0, sk: 0, source_senses: 0, skeleton: '{T1} {T2} {T3}' } }
reset()
r = accept(card([sense('{T1} {T3}')]), 'exp')
check('expansion card is KEPT (soft, not rejected)', r !== null)
check('accept() stamps c.tnmask on the kept card', r && r.tnmask && typeof r.tnmask === 'object', JSON.stringify(r && r.tnmask))
check('stamped got is the pre-restore candidate multiset (brace-less)', r && r.tnmask && r.tnmask.got === 'T1 T3', JSON.stringify(r && r.tnmask))
check('stamped want is the masked-skeleton multiset (brace-less)', r && r.tnmask && r.tnmask.want === 'T1 T2 T3', JSON.stringify(r && r.tnmask))
check('the pairing records the mismatch (got != want) — offline-detectable', r && r.tnmask && r.tnmask.got !== r.tnmask.want)
check('no braces survive in the persisted pairing (store {Tn}-residue invariant)',
  r && r.tnmask && !/[{}]/.test(r.tnmask.got) && !/[{}]/.test(r.tnmask.want), JSON.stringify(r && r.tnmask))

// ==== CLEAN: every {Tn} kept (order-insensitive) -> got === want ========================
INPUTS = { ok: { ls: 0, sk: 0, source_senses: 0, skeleton: '{T1} {T2}' } }
reset()
r = accept(card([sense('{T2}'), sense('{T1}')]), 'ok')
check('faithful (reordered) card is kept', r !== null)
check('a clean card stamps got === want (the measurement denominator)',
  r && r.tnmask && r.tnmask.got === 'T1 T2' && r.tnmask.want === 'T1 T2', JSON.stringify(r && r.tnmask))

// ==== EMPTY: a card with no masked spans stamps an empty, clean pairing =================
INPUTS = { none: { ls: 0, sk: 0, source_senses: 0, skeleton: 'plain gloss, no masks' } }
reset()
r = accept(card([sense('plain gloss')]), 'none')
check('a card with no {Tn} stamps an empty, measurable, clean pairing',
  r && r.tnmask && r.tnmask.got === '' && r.tnmask.want === '', JSON.stringify(r && r.tnmask))

// ==== restore cannot strip the pairing: RESTORE_SPEC never lists `tnmask` ===============
// (restoreCard iterates RESTORE_SPEC's card/record/sense field lists only; `tnmask` is not a
//  text field, so the real restore path leaves it intact — proven structurally here.)
const restoreFields = [].concat(RESTORE_SPEC.card || [], RESTORE_SPEC.record || [], RESTORE_SPEC.sense || [])
check('RESTORE_SPEC does not list tnmask (real restoreCard cannot strip it)',
  restoreFields.indexOf('tnmask') === -1, JSON.stringify(restoreFields))

if (failed) { console.error(failed + ' check(s) failed'); process.exit(1) }
console.log('tnmask_persist_test: PASS')
