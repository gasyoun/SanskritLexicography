// H1151 behavioral pin for the H858 grammar-field {Tn} stranding class.
//
// HISTORY, stated honestly: the 13-07-2026 diagnosis (RUN_LOG:909, live on gokzuraka)
// found restoreCard restoring german/russian only. The C-01 centralization (H963/H1080,
// card_fields.py) then made BOTH restore lanes read RESTORE_SPEC = js_restore_spec(field),
// whose record level lists ('h', 'grammar') — so by the time H1151 ran (17-07-2026), the
// defect was already absent on origin/master. This test therefore PINS the fixed behaviour
// rather than proving a new fix: it extracts the REAL restore()/restoreCard()/RESTORE_SPEC
// from a generated harness (FINDINGS §82: never test a hand-written copy) and fails loudly
// if any future edit drops `grammar` (or `h`) from the record-level restore again.
//
//   node src/pilot/grammar_restore_test.js <path-to-a-generated-harness.js>
const fs = require('fs')

const harnessPath = process.argv[2]
if (!harnessPath) { console.error('FAIL: usage: node grammar_restore_test.js <harness.js>'); process.exit(1) }
const src = fs.readFileSync(harnessPath, 'utf8')

const specM = src.match(/const RESTORE_SPEC = (\{[^\n]*\})/)
if (!specM) { console.error('FAIL: RESTORE_SPEC not found in ' + harnessPath); process.exit(1) }
const restoreM = src.match(/const restore = [^\n]*/)
if (!restoreM) { console.error('FAIL: restore not found in ' + harnessPath); process.exit(1) }
const cardM = src.match(/function restoreCard\([\s\S]*?\n\}/)
if (!cardM) { console.error('FAIL: restoreCard not found in ' + harnessPath); process.exit(1) }

// Runtime globals restoreCard closes over.
const RESTORE_SPEC = eval('(' + specM[1] + ')')
const PH = { k1: ['ALPHA', 'BETA', 'GAMMA'] }   // {T1}->ALPHA {T2}->BETA {T3}->GAMMA
const restore = eval('(' + restoreM[0].replace(/^const restore = /, '') + ')')
const restoreCard = eval('(' + cardM[0].replace(/^function restoreCard/, 'function ') + ')')

let failed = 0
const check = (name, cond, extra) => {
  if (cond) { console.log('PASS: ' + name) } else { console.error('FAIL: ' + name + (extra ? ' -- ' + extra : '')); failed++ }
}

// ---- spec-level pin: the record level must keep restoring h AND grammar ----
check('RESTORE_SPEC.record includes grammar', (RESTORE_SPEC.record || []).includes('grammar'),
  'record spec = ' + JSON.stringify(RESTORE_SPEC.record))
check('RESTORE_SPEC.record includes h', (RESTORE_SPEC.record || []).includes('h'))

// ---- behavioural pin: the gokzuraka shape — a {T2} echoed into record.grammar ----
const card = {
  iast: 'x {T1}',
  records: [{
    h: '{T3}',
    grammar: '{T2}',
    senses: [{ tag: 't {T1}', german: 'g {T2}', russian: 'r {T3}', differentia: 'd {T1}' }],
  }],
}
const out = restoreCard(JSON.parse(JSON.stringify(card)), 'k1')
check('record.grammar {T2} restored (the gokzuraka class)', out.records[0].grammar === 'BETA',
  'got ' + JSON.stringify(out.records[0].grammar))
check('record.h {T3} restored', out.records[0].h === 'GAMMA')
check('card.iast restored', out.iast === 'x ALPHA')
check('sense fields still restored (no regression)',
  out.records[0].senses[0].german === 'g BETA' && out.records[0].senses[0].russian === 'r GAMMA')
check('no {Tn} survives anywhere in the restored card', !JSON.stringify(out).match(/\{T\d+\}/),
  JSON.stringify(out))

// ---- C-42 boundary unchanged: an out-of-range token stays literal, never invented ----
const oob = restoreCard({ iast: null, records: [{ h: null, grammar: '{T9}', senses: [] }] }, 'k1')
check('out-of-range {T9} stays literal (C-42: never synthesise)', oob.records[0].grammar === '{T9}')

process.exit(failed ? 1 : 0)
