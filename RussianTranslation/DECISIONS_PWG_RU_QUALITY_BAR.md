# PWG→RU Quality-Bar Decisions

_Created: 17-07-2026 · Last updated: 17-07-2026_

Settled user decisions on the pwg_ru audit-clean quality bar and the quality
claim the lane carries. Append-only (`D1..Dn`); a ruling is never edited — a
reversal is a new entry citing and superseding the old one. Do not re-ask these
as open planning questions unless a human explicitly reopens the topic.

Eliciting session: Opus 4.8 (`claude-opus-4-8[1m]`), 17-07-2026, following the
H1149 W1-A cohort clean-rate measurement
([PR #525](https://github.com/gasyoun/SanskritLexicography/pull/525),
[`RussianTranslation/pwg_ru/h1112/cohort_clean_rates.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/cohort_clean_rates.json)).
Decider: a human (MG).

## D1 — Replace the single 80% audit-clean bar with per-cohort bars; no_pwg bar = 60%

**Context.** The pwg_ru lane was gated by a single **80%** audit-clean bar that had
never been calibrated against a real cohort, and the lane sat frozen against it for
days on fatigue rather than on a number. H1149 (ruling R3, narrow-and-measure)
measured per-cohort clean rates against frozen evidence and returned
([H1112_COHORT_CLEAN_RATES_2026-07-17.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/H1112_COHORT_CLEAN_RATES_2026-07-17.md)):
`no_pwg` **62.0%** median (range 41–69%, consumed verbatim from the H911 census) →
**BELOW_BAR**; `root_upasarga` and `nominal` → **INSUFFICIENT_EVIDENCE** (the
root_upasarga sample cites four roots — sTA/BU/as/i — absent from the current store;
nominal's 100/100 is a *promotion* count, not an audit-clean count, because the audit
gates crash on nominal windows). **No cohort clears 80%.**

**Options considered.**
- **Hold 80%** — preserves the aspirational bar, but freezes the lane indefinitely on
  an uncalibrated number; rejected as the fatigue-not-data status quo H1149 exists to end.
- **One global bar lowered to ~60–62%** — simple, but averages three cohorts whose real
  rates differ (one measured, two unmeasurable), so it would set a bar for cohorts we
  have no evidence for; rejected as false precision.
- **Per-cohort bars (RULED).** Set a bar only where there is evidence; leave the rest
  bar-less and human-gated until fresh audited evidence exists.

**Ruling (MG, 17-07-2026).** Replace the single 80% bar with **per-cohort bars.**
- `no_pwg`: **60%** — a round floor just below the measured 62% median, chosen so the
  lane drains without the bar being aspirational (it sits at/under what the cohort
  actually produces, not above it).
- `root_upasarga` and `nominal`: **no bar set.** Both are INSUFFICIENT_EVIDENCE; they
  stay human-gated until fresh audited evidence exists. A bar for an unmeasured cohort
  would be a number invented to look like a gate.

**Consequences.**
- Supersedes the 80% bar wherever it is referenced (H911, H255, H1149).
- **Unblocks the no_pwg drain's QUALITY gate only.** It does **not** unfreeze throughput:
  that stays human-blocked on [GTD:579](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)
  foreign-route provisioning + the c5/c6 logins (both open `@DO`). A cleared quality gate
  names a drainable lane; it does not make the lane drainable today.
- Next concrete action to *measure* the two deferred cohorts: commission fresh audited
  evidence for `root_upasarga` (roots present in the current store) and a nominal audit
  path that does not crash — separate, unclaimed work.

## D2 — The pwg_ru lane output is labelled machine-preview, not production-grade

**Context.** A 60% audit-clean bar cannot honestly back a production-grade claim. The
quality claim the lane carries cascades: it is cited by any paper built on the lane, and
it drives the still-open LOD release-posture `@DECIDE` (the "wait for G5 vs labelled
machine-preview" fork).

**Options considered.**
- **Keep the production-grade claim** — overclaims at 60%; rejected as dishonest.
- **Provisional / production-grade pending a review budget** — coherent only if a
  human-review pass on the sub-bar band were funded; no such budget was chosen
  (per-cohort bars, not a review-budget path), so this would overclaim; rejected.
- **Machine-preview, explicitly (RULED).**

**Ruling (MG, 17-07-2026).** The pwg_ru lane output is labelled **machine-preview /
machine-generated**, explicitly **not** production-grade. This also resolves the open LOD
release-posture `@DECIDE` **in favour of labelled machine-preview** (not "wait for G5").

**Consequences.**
- Any paper citing the pwg_ru lane must carry the machine-preview caveat.
- The LOD release posture follows the machine-preview label; the "wait for G5 vs labelled
  machine-preview" fork is now closed at labelled machine-preview. The two remaining LOD
  `@DECIDE`s (IRI publication domain, license composition) are unaffected by this ruling.
- This is a quality-*claim* decision, not a throughput one — same boundary as D1.

_Dr. Mārcis Gasūns_
