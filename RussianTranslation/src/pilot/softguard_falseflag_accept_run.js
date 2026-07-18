// H1150 W1-B: run the REAL accept()/countOf/countOfField/tokensOf/cardTokens extracted
// VERBATIM out of a generated harness against a batch of cases -- the exact extraction
// technique accept_sensecount_test.js uses (so this cannot drift from, or hand-copy, the
// production guard; Uprava FINDINGS Section 82 names hand-copying as the anti-pattern this
// avoids). Driven by softguard_falseflag_measure.py; not a standalone test file.
//
//   node softguard_falseflag_accept_run.js <harness.js> <cases.json> <out.json>
//
// cases.json: [{ key, ls, sk, source_senses, senses: [{german, russian}, ...] }, ...]
//
// INPUTS[k] deliberately carries NO `skeleton` field. These cases are RESTORED store rows
// (post-restore text pulled from the promoted store), not pre-restore generation output --
// there is no masked skeleton to compare a {Tn} multiset against for them (see the .py
// module docstring's TNMASK section). tokensOf(undefined) and cardTokens(a token-free
// restored card) both reduce to '', so the extracted TNMASK check is a no-op '' === '' here
// by construction. This runner measures SANLOSS only; TNMASK's own true-positive behavior
// is already pinned by accept_sensecount_test.js's `gram` fixture, and no frozen evidence
// exists to measure its false-flag rate (see the memo).
const fs = require('fs')

const [harnessPath, casesPath, outPath] = process.argv.slice(2)
if (!harnessPath || !casesPath || !outPath) {
  console.error('usage: node softguard_falseflag_accept_run.js <harness.js> <cases.json> <out.json>')
  process.exit(1)
}
const src = fs.readFileSync(harnessPath, 'utf8')
const cases = JSON.parse(fs.readFileSync(casesPath, 'utf8'))

const one = name => {
  const m = src.match(new RegExp('const ' + name + ' = [^\\n]*'))
  if (!m) { console.error('FAIL: ' + name + ' not found in ' + harnessPath); process.exit(1) }
  return m[0].replace(new RegExp('^const ' + name + ' = '), '')
}
const am = src.match(/const accept = \(c, k\) => \{[\s\S]*?\n\}/)
if (!am) { console.error('FAIL: accept not found in ' + harnessPath); process.exit(1) }

let INPUTS = {}
const FAIL = {}
const noteFail = (k, why) => { FAIL[k] = String(why).slice(0, 500) }
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
const accept = eval('(' + am[0].replace(/^const accept = /, '') + ')')

const results = []
for (const c of cases) {
  INPUTS = { [c.key]: { ls: c.ls, sk: c.sk, source_senses: c.source_senses } }
  SANLOSS_SHORTFALLS = 0; SANLOSS_DETAIL.length = 0
  TNMASK_MISMATCHES = 0; TNMASK_DETAIL.length = 0
  for (const k in FAIL) delete FAIL[k]
  const card = { records: [{ senses: c.senses.map(s => ({ german: s.german, [TARGET_FIELD]: s.russian })) }] }
  const r = accept(card, c.key)
  results.push({
    key: c.key,
    accepted: r !== null,
    fail: FAIL[c.key] || null,
    sanloss_shortfalls: SANLOSS_SHORTFALLS,
    sanloss_detail: SANLOSS_DETAIL.slice(),
    tnmask_mismatches: TNMASK_MISMATCHES,
  })
}
fs.writeFileSync(outPath, JSON.stringify(results, null, 1))
console.log('wrote', results.length, 'results to', outPath)
