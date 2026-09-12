_Created: 13-09-2026 · Last updated: 13-09-2026_

# Release tag flow — PR-gated master, tag AFTER the merge

> On-demand companion extracted from [`CLAUDE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md) (H4580 slim). The one-line summary lives there; this file carries the full procedure and the measured history verbatim.

`master` carries the required status check **`RussianTranslation gates`**, so a release
commit only reaches it through a PR. That breaks the one-shot tool route:
`cut_release.py --apply --tag --push` tags the commit that exists *now* — your branch
head — and the squash-merge replaces it, so the tag either points at a commit never
reachable from `master` (the orphan class, [Uprava FINDINGS §646](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md))
or, far more often here, is never pushed at all.

**Measured 09-09-2026:** 22 `## [x.y.z]` headings on `master` carried no tag — including
`1.144.161`, promoted that same morning by [PR #2156](https://github.com/gasyoun/SanskritLexicography/pull/2156)
— against 76 tags carrying no heading. 21 were tagged and released in the backfill; the
22nd (`1.144.102`) was a renumbering artifact and is annotated in
[CHANGELOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CHANGELOG.md) instead.

The flow that actually works here:

1. Promote on a branch — `python ~/Documents/GitHub/Uprava/tools/cut_release.py . --version x.y.z --apply` (**no** `--tag`, **no** `--push`).
2. Open the PR, wait for `RussianTranslation gates`, merge it.
3. `git fetch origin master --tags`, then tag the **merge commit on `origin/master`** — never the branch head:

```sh
git tag -a vx.y.z <merge-sha> -m "vx.y.z" && git push origin vx.y.z
gh release create vx.y.z --repo gasyoun/SanskritLexicography --title "vx.y.z" --notes-file <section-file>
```

4. Prove it landed: `python ~/Documents/GitHub/Uprava/tools/cut_release.py . --verify-tag x.y.z` (exit 1 = orphan).

**Backfilling an older version? add `--latest=false` to `gh release create`.** Without it GitHub hands the Latest badge to whatever release was published most recently — so cutting `v1.0.0` today would advertise a June changelog as this repo's current release. The 09-09-2026 backfill published all 21 with the flag, which is why `v1.144.164` still holds the badge. It is only ever omitted for a genuine new release that really is the newest.

Step 3 is the step that gets dropped: the PR merges, the session reports the release as
cut, and nothing ever tags it. `--verify-releases` is the backstop, not the plan. **Never
`git tag -f` a published tag** to repair drift — tag the right commit under the right
number, or annotate the heading, as the 09-09-2026 backfill did.

The convention the backfill followed, and the one to keep: **`vX.Y.Z` points at the commit
that introduced `## [X.Y.Z]`.** Bare unprefixed tags (`1.144.6`, `1.144.7`, `1.144.84`) exist
from an older habit and are invisible to the census, which reads `refs/tags/vX.Y.Z` only.

_Dr. Mārcis Gasūns_
