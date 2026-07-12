// Behavioral test for the H255/H811 boundedParallel low-width staggered dispatch.
// Extracts the REAL boundedParallel emitted by gen_opt_harness2.py (so this can't drift from
// the generator) and asserts: (A) concurrency is capped at `width`, (B) results stay index-
// aligned, (C) a thrown thunk resolves to null without poisoning the batch, (D) width<=0 falls
// back to parallel(), (E) the first `width` starts are staggered by staggerMs.
//   node src/pilot/boundedparallel_test.js <path-to-a-generated-harness.js>
const fs = require('fs')

const harnessPath = process.argv[2] || 'src/pilot/lowwide_test.js'
const src = fs.readFileSync(harnessPath, 'utf8')

// Pull the function source out of the generated harness verbatim.
const m = src.match(/async function boundedParallel\(thunks, width, staggerMs\) \{[\s\S]*?\n\}/)
if (!m) { console.error('FAIL: boundedParallel not found in ' + harnessPath); process.exit(1) }

// Provide the two runtime globals the harness gets for free: parallel() (all-concurrent, a
// thrown thunk -> null) and setTimeout (real in Node). Then eval the extracted source.
const parallel = thunks => Promise.all(thunks.map(t => Promise.resolve().then(t).catch(() => null)))
// Direct eval (sees local `parallel`); wrap as an expression so the fn name doesn't collide.
const boundedParallel = eval('(' + m[0] + ')')

let failed = 0
const check = (name, cond, extra) => { if (cond) { console.log('PASS: ' + name) } else { console.error('FAIL: ' + name + (extra ? ' -- ' + extra : '')); failed++ } }

const sleep = ms => new Promise(r => setTimeout(r, ms))

async function main() {
  // (A) concurrency cap + (B) order: 8 thunks track a live counter; width 3 -> peak <= 3.
  {
    let live = 0, peak = 0
    const thunks = Array.from({ length: 8 }, (_, i) => async () => {
      live++; peak = Math.max(peak, live)
      await sleep(20)
      live--
      return i
    })
    const res = await boundedParallel(thunks, 3, 0)
    check('concurrency capped at width=3', peak <= 3, 'peak=' + peak)
    check('all 8 ran', live === 0 && res.length === 8)
    check('results index-aligned', res.every((v, i) => v === i), JSON.stringify(res))
  }

  // (C) a thrown thunk -> null, others unaffected.
  {
    const thunks = [async () => 'a', async () => { throw new Error('boom') }, async () => 'c']
    const res = await boundedParallel(thunks, 2, 0)
    check('thrown thunk -> null, batch survives', res[0] === 'a' && res[1] === null && res[2] === 'c', JSON.stringify(res))
  }

  // (D) width<=0 and width>=len fall back to parallel() (all results present).
  {
    const mk = () => [async () => 1, async () => 2]
    const r0 = await boundedParallel(mk(), 0, 0)
    const rBig = await boundedParallel(mk(), 99, 0)
    check('width=0 falls back to parallel()', JSON.stringify(r0) === '[1,2]', JSON.stringify(r0))
    check('width>=len falls back to parallel()', JSON.stringify(rBig) === '[1,2]', JSON.stringify(rBig))
  }

  // (E) stagger: width=3 over 6 thunks, staggerMs=60. Each initial worker starts ~w*60ms
  // apart; thunks sleep 200ms (> width*stagger=180) so no worker races ahead and picks a 4th
  // thunk during the stagger window. The 3 earliest starts are thus the 3 initial workers'
  // first picks and must span >= ~2*stagger.
  {
    const t0 = Date.now()
    const starts = []
    const thunks = Array.from({ length: 6 }, () => async () => { starts.push(Date.now() - t0); await sleep(200) })
    await boundedParallel(thunks, 3, 60)
    const first3 = starts.slice(0, 3).sort((a, b) => a - b)
    const span = first3[2] - first3[0]
    check('first 3 starts staggered by ~2*60ms', span >= 100, 'first3=' + JSON.stringify(first3))
  }

  if (failed) { console.error('\nboundedparallel_test: ' + failed + ' FAILURE(S)'); process.exit(1) }
  console.log('\nboundedparallel_test: all PASS')
}
main().catch(e => { console.error('FAIL: uncaught ' + (e && e.stack || e)); process.exit(1) })
