# VERIFICATION — PWG_RU_UNFREEZE (SanskritLexicography)

_Created: 17-07-2026 · Last updated: 17-07-2026_

How each Wave-1 deliverable is proven, with exact commands. Index + rulings: [PLAN_SanskritLexicography_PWG_RU_UNFREEZE_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_UNFREEZE_2026H2.md) · steps: [IMPLEMENTATION_SanskritLexicography_PWG_RU_UNFREEZE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/IMPLEMENTATION_SanskritLexicography_PWG_RU_UNFREEZE.md).

All commands run from `RussianTranslation/` inside a worktree off `origin/master`.

---

## 0. Baselines — measured 17-07-2026 on `origin/master` [`64054959`](https://github.com/gasyoun/SanskritLexicography/commit/64054959)

These were **run, not assumed**. A deliverable that moves any of them without saying so has regressed.

| Command | Baseline output |
|---|---|
| `python src/pilot/window_selftest.py` | `window selftest: ran 135/135 defined -- 135 passed, 0 failed` → `window selftest OK` |
| `python src/pilot/lang_parity_check.py` | `LANG PARITY LEDGER: 49 entries, all verdicts complete, no drift` |
| store row count | **11,603** |
| `provenance.h_reconstructed == true` | **468** (`iast_reconstructed` 462 · `grammar_defaulted_empty` 468) |
| EN rows in store | **0** |
| `layer` distribution | `pwg` 5,594 · `pw` 5,205 · `nws` 432 · `sch` 210 · `pwkvn` 162 |
| live handoffs (this repo) | **30** (22 🟡 + 8 🔵) |

Universal regression gate, every deliverable, before PR:

```sh
python src/pilot/window_selftest.py          # expect 135/135 (or 135+N with new tests, 0 failed)
python src/pilot/lang_parity_check.py        # expect 49/49 (or 49+N), no drift
git diff --check                             # no whitespace errors
git status --porcelain -- '*.jsonl'          # MUST be empty — the store is read-only this wave
```

---

## 1. Standing invariants — check on every PR in the wave

Each is a rule from the plan's autonomy contract turned into a command.

```sh
# The two hard-rejects stay owner-gated (D-2). Both MUST still read false.
grep -n 'const SANLOSS_HARD_REJECT = false' src/pilot/gen_opt_harness2.py
grep -n 'const TNMASK_HARD_REJECT = false'  src/pilot/gen_opt_harness2.py

# No threshold was touched (Ruling 2 fixes the 30s bar / 180s ceiling / profile count).
git diff origin/master -- src/pilot/ | grep -E '^[-+].*(30000|180|THRESHOLD|CEILING|MAX_AGENTS)' || echo "no threshold drift"

# The store was not mutated (no deliverable this wave may write it).
git status --porcelain -- src/pwg_ru_translated.jsonl   # expect empty

# promote_en.py never ran — the store still carries 0 EN rows.
python -c "import json,sys; sys.stdout.reconfigure(encoding='utf-8'); print(sum(1 for l in open('src/pwg_ru_translated.jsonl',encoding='utf-8') if (json.loads(l).get('provenance') or {}).get('lang')=='en'))"
# expect: 0
```

If any of these four fails, the PR is wrong regardless of its own acceptance criterion.

---

## 2. W1-A — cohort clean-rate report + D-1 debt worklist

**Claim:** a defensible per-cohort clean rate exists, each number carrying its evidence path; the 468-row debt is exported and guarded.

```sh
python src/pilot/cohort_clean_rates.py --out pwg_ru/h1112/cohort_clean_rates.json
```

### 2.1 Partition is complete and exclusion is honest

```sh
python - <<'PY'
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
r = json.load(open('pwg_ru/h1112/cohort_clean_rates.json', encoding='utf-8'))
assert r['store_rows'] == 11603, r['store_rows']
assert r['excluded']['h_reconstructed'] == 468, r['excluded']
assert r['excluded']['unassigned'] == 0, 'unassigned residue must be 0 or enumerated'
tot = sum(c['rows'] for c in r['cohorts'].values())
assert tot + 468 == 11603, f'{tot}+468 != 11603 — rows lost in partition'
assert r['cohorts']['no_pwg']['rows'] == 6009, r['cohorts']['no_pwg']['rows']
for name, c in r['cohorts'].items():
    assert c['verdict'] in ('CLEARS_BAR','BELOW_BAR','INSUFFICIENT_EVIDENCE'), (name, c['verdict'])
    assert c.get('evidence'), f'{name}: a clean_rate with no evidence path is a defect'
assert r['economy'].startswith('NOT_MEASURABLE'), r['economy']
print('W1-A structural checks PASS')
PY
```

### 2.2 The consumed `no_pwg` figure matches its source (not recomputed)

```sh
python -c "import json,sys; sys.stdout.reconfigure(encoding='utf-8'); print(json.load(open('pwg_ru/h911/h911_quality_economy_census.json',encoding='utf-8'))['families']['H255_no_pwg_workflow']['population_audit_clean_rate'])"
# expect: per-window 41%-69% (median ~62%); EXCLUDES w1 infra-crippled first run
```

The report's `no_pwg.clean_rate` must be **consistent with this string and cite it**. A different number means the deliverable recomputed what it was told to consume.

### 2.3 The D-1 debt artifacts

```sh
wc -l pwg_ru/h1112/h_reconstructed_worklist.jsonl        # expect 468
python -c "import json,sys,collections; sys.stdout.reconfigure(encoding='utf-8'); print(len(collections.Counter(json.loads(l)['h'] for l in open('pwg_ru/h1112/h_reconstructed_worklist.jsonl',encoding='utf-8'))))"
# expect: 14   — the measured homonym collapse PR #517 documented
```

### 2.4 The regression guard actually catches the failure it exists for

This is the load-bearing test. A guard that passes on a mutated store is not a guard.

```sh
cp src/pwg_ru_translated.jsonl /tmp/store.bak
python - <<'PY'
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
out, dropped = [], 0
for l in open('src/pwg_ru_translated.jsonl', encoding='utf-8'):
    r = json.loads(l); p = r.get('provenance') or {}
    if p.get('h_reconstructed') and not dropped:
        p.pop('h_reconstructed'); dropped = 1      # simulate ONE silent marker loss
    out.append(json.dumps(r, ensure_ascii=False))
open('src/pwg_ru_translated.jsonl','w',encoding='utf-8').write('\n'.join(out)+'\n')
PY
python src/pilot/window_selftest.py ; echo "EXPECT NON-ZERO EXIT: $?"    # the guard MUST fail at 467
cp /tmp/store.bak src/pwg_ru_translated.jsonl
python src/pilot/window_selftest.py ; echo "EXPECT 0: $?"                # green again at 468
```

> **PASS** = structural checks pass · `no_pwg` cites the census · worklist is 468 lines over 14 heads · the guard **fails at 467 and passes at 468**.
> **A report where all three cohorts read `BELOW_BAR` is a PASS.** Ruling 3 commissioned a measurement capable of killing the 80% bar. Verification checks that the number is *defensible*, never that it is *good*.

---

## 3. W1-B — offline false-flag rate

**Claim:** the owner has a defensible false-flag rate per guard, computed against the real `accept()`, and nothing was armed.

```sh
# 0. The frozen evidence is intact BEFORE anything is computed from it.
cd pwg_ru/h963 && sha256sum -c artifact_manifest.sha256 && cd ../..
# expect: every line OK. Any mismatch => stop, report, do not measure.
```

```sh
python - <<'PY'
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
r = json.load(open('pwg_ru/h1112/softguard_falseflag_rate.json', encoding='utf-8'))
for g in ('sanloss', 'tnmask'):
    assert g in r, f'{g} missing — the two classes must be reported separately, never pooled'
    d = r[g]
    for f in ('flagged', 'true_drop', 'false_flag', 'denominator', 'examples'):
        assert f in d, (g, f)
    assert d['true_drop'] + d['false_flag'] == d['flagged'], g
    assert d['examples'], f'{g}: named example keys are required'
assert r['recommendation'] in ('ARM','DO_NOT_ARM','FIX_COUNTER_FIRST'), r['recommendation']
assert 'limit' in r or 'caveat' in r, 'the one-route/one-payload limit must be stated'
print('W1-B structural checks PASS')
PY
```

**Nothing was armed** — the §1 invariant greps must still find both `= false`, and:

```sh
git diff origin/master -- src/pilot/gen_opt_harness2.py | grep -E '^\+.*HARD_REJECT = true' && echo "VIOLATION" || echo "not armed — correct"
```

**The guard was not re-implemented** (the FINDINGS §82 anti-pattern — a hand-written copy validates the measurement against itself):

```sh
grep -n "readFileSync\|match(/const accept" src/pilot/<w1b_script>   # must extract accept() from a generated harness
node src/pilot/accept_sensecount_test.js <path-to-generated-harness.js>   # the existing test still passes
```

> **PASS** = manifest verified first · separate rates for `SANLOSS`/`TNMASK` with numerator, denominator, named examples · a recommendation · the one-route limit stated · both flags still `false` · the guard extracted, not copied.

---

## 4. W1-C — H858 `grammar` `{Tn}` stranding fix

**Claim:** a `{Tn}` echoed into `grammar` is restored; the fix is forward-only; nothing else moved.

```sh
# The test must FAIL on master and PASS with the fix — a test that passes on both proves nothing.
git stash && node src/pilot/<grammar_restore_test>.js <harness.js> ; echo "EXPECT FAIL: $?"
git stash pop && node src/pilot/<grammar_restore_test>.js <harness.js> ; echo "EXPECT PASS: $?"

node --check <generated-harness.js>          # the emitted JS is still syntactically valid
python src/pilot/window_selftest.py          # expect 135+N/135+N, 0 failed
```

Blast radius reported, not repaired:

```sh
python -c "import json,re,sys; sys.stdout.reconfigure(encoding='utf-8'); n=[json.loads(l).get('key1') for l in open('src/pwg_ru_translated.jsonl',encoding='utf-8') if re.search(r'\{T\d+\}', json.loads(l).get('grammar') or '')]; print(len(n), n[:10])"
```

```sh
git status --porcelain -- src/pwg_ru_translated.jsonl    # MUST be empty — no repair, no mutation
```

> **PASS** = test red→green across the fix · `node --check` clean · selftest green · blast radius reported with keys · store untouched · the changelog states forward-only and that `gokzuraka` is unreclaimable (no placeholder map was saved).

---

## 5. W1-D — H1070's three EN guards

**Claim:** all three guards exist offline, guard 2 has a **root cause** and not just a patch, parity holds, and the EN lane still has zero rows.

### 5.1 Guard 2 — the only hard one

```sh
# Fixture reproduces r102's dropped {#uc#} inside an <F> footnote: red before, green after.
git stash && node src/pilot/<en_footnote_test>.js <harness.js> ; echo "EXPECT FAIL: $?"
git stash pop && node src/pilot/<en_footnote_test>.js <harness.js> ; echo "EXPECT PASS: $?"
```

**Root cause required in writing.** `accept()` already counts `{#` over the whole restored card (`countOf(c, /\{#/g)`), so a correct-by-inspection counter did not fire on r102 ⇒ the loss is upstream, in how `<F>` content is masked/restored. The PR body must name **where** the footnote content escaped the mask. A counter patch with no such line is rejected: it would be treating a symptom H1070 explicitly flags as the one silent-loss class.

### 5.2 Guards 1 and 3

```sh
grep -n "Vergleich\|braut\|gelten" src/pilot/gen_fidelity_judge_en.py       # polyseme checklist present
grep -n "polysemous\|licenses" src/pilot/tr_en.txt                          # prompt rule present
# guard 3: DE-RESIDUE soft class for pure-cross-ref + NWS {#..#} German
```

### 5.3 Parity and the EN store invariant

```sh
python src/pilot/lang_parity_check.py        # expect 49+N entries, all verdicts complete, no drift
git diff origin/master -- LANG_PARITY.md | grep -E '^\+.*(SHARED|INTENTIONAL-DIVERGENCE|GAP)'   # each change classified
```

```sh
git diff origin/master --stat -- src/pilot/promote_en.py    # expect empty — promote_en.py must not run or change
```

> **PASS** = guard 2 red→green **with a written root cause naming the mask escape** · guards 1 and 3 present with fixtures · parity clean with every change classified · hashes refreshed only via `--update-hash` · store still 0 EN rows.

---

## 6. W1-E — ReverseDictionary recovery + rights ledger

**Claim:** the rights position is stated with an honest bound, and nothing was published.

```sh
git log --all --diff-filter=A --format='%H %ad %an' --date=short -- '*266820*'   # recovery attempt is on record
ls -la ReverseDictionary/.doc.pdf/
wc -l <recovered-266820-file>          # expect 266820, if recovered at all
```

Ledger completeness — the third bucket is the deliverable:

```sh
grep -n "Edgerton\|12,552" ReverseDictionary/RIGHTS_LEDGER.md      # marked, subtractable
grep -n "Vettam Mani\|1,919"  ReverseDictionary/RIGHTS_LEDGER.md
grep -n "14,471\|lower bound" ReverseDictionary/RIGHTS_LEDGER.md    # the bound is stated as a bound
for s in Stchoupak Turner Mylius Kochergina Pujol; do
  grep -q "$s" ReverseDictionary/RIGHTS_LEDGER.md && echo "$s: listed" || echo "$s: MISSING — the unmarked bucket is the point";
done
```

Nothing published, nothing deleted:

```sh
git diff origin/master --stat -- ReverseDictionary/ | grep -E '^\s+delete|=> /dev/null' && echo "VIOLATION: file removed" || echo "no deletions — correct"
gh pr view --json files 2>/dev/null | grep -i "266820" && echo "REVIEW: is the canonical list being committed to a PUBLIC repo? escalate" || true
```

> **PASS** = the recovery attempt is on record (found+backed-up, or escalated as data loss) · all five unmarked sources listed in the *cannot-be-isolated* bucket · 14,471 stated as a **lower bound** · no publish · no in-copyright file moved or deleted · `Reverse-Kochergina.mdx` flagged as an H734-class exposure · the GTD `@DECIDE` carries the sharpened question.
> **A subset artifact labelled "PD-only" is a FAIL** even if its contents are right — the label claims a certification the data does not support.

---

## 7. W1-F — backlog triage

```sh
cd C:/Users/user/Documents/GitHub/Uprava
python tools/registry_check.py --strict      # MUST exit 0 — counts/marker are derived, never hand-edited
python tools/handoff_kanban_sync.py --dry-run
```

```sh
# Every one of the 30 live rows has a verdict; none silently left.
python - <<'PY'
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
t = open('handoffs/README.md', encoding='utf-8').read()
rows = [l for l in t.split('\n') if ('SanskritLexicography' in l or 'RussianTranslation' in l) and l.startswith('|')]
live = [l for l in rows if '🟡' in l or '🔵' in l]
print('live now:', len(live), '(was 30 pre-triage)')
print('H963 archived under H1110:', 'H963' not in ' '.join(live))
PY
```

> **PASS** = `registry_check.py --strict` exits 0 · live + newly-archived reconcile to the pre-triage 30 · H963 archived under H1110 · no row left without a verdict.

---

## 8. W1-L — the bounded ladder (H1110's acceptance, restated)

```sh
# Budget: the ruling is <=3 paid calls.
grep -c '"paid_call"' <h1110-run-artifact>.jsonl      # expect <= 3

# Thresholds untouched.
git diff origin/master -- src/pilot/ | grep -E '^[-+].*(30000|180|THRESHOLD|CEILING)' || echo "thresholds untouched — correct"

# The banned vocabulary appears NOWHERE in the report, whatever the outcome.
grep -riE 'PRODUCTION_GO|production-ready|four-profile|scale GO' <h1110-report>.md && echo "VIOLATION — Ruling 2" || echo "vocabulary clean"

# The required labels are present.
grep -E 'CORRECTNESS_PROOF: (PASS|FAIL)' <h1110-report>.md
grep -c 'two-profile' <h1110-report>.md
```

> **PASS** = ≤3 paid calls · no threshold constant changed · the report says `CORRECTNESS_PROOF` and `two-profile` · **zero** occurrences of the banned labels.
> A **FAIL** verdict honestly reported is a PASS of the deliverable. A PASS relabelled as a production go is a failure of the wave, and is the specific error this section exists to catch — the same shape as [PR #510](https://github.com/gasyoun/SanskritLexicography/pull/510)'s true-but-unsupported "468 rows repaired".

---

## 9. Wave-level exit check

```sh
python src/pilot/window_selftest.py            # 135+N, 0 failed
python src/pilot/lang_parity_check.py          # 49+N, no drift
git status --porcelain -- '*.jsonl'            # empty — store untouched all wave
grep -c 'const SANLOSS_HARD_REJECT = false' src/pilot/gen_opt_harness2.py   # 1
grep -c 'const TNMASK_HARD_REJECT = false'  src/pilot/gen_opt_harness2.py   # 1
cd C:/Users/user/Documents/GitHub/Uprava && python tools/registry_check.py --strict
```

Wave 1 exits when **W1-A has reported**. The other five make the lane trustworthy; W1-A decides whether there is a lane to drain. If no cohort clears 80%, the next action is a `/decision-record` re-deciding the bar — **not** another wave of drain preparation.

---

_Dr. Mārcis Gasūns_
