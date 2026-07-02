#!/usr/bin/env bash
# Regenerate the PWG <ls> citation-coverage reports and open an auto-merge PR to
# sanskrit-lexicon/PWG. Run on the machine that HAS the (git-ignored) translation
# data (pwg_ru_translated.jsonl + wf_output.en.*.json) — e.g. from cron or
# Windows Task Scheduler. Safe by construction:
#   * the generator aborts if the data is missing (never writes empty reports);
#   * it works in a throwaway PWG worktree, so it never disturbs your PWG checkout;
#   * no-op (no PR) when the reports are unchanged.
#
# Requires: python (with mako/deps for build_article_site), gh (authenticated),
# and PWG checked out as a sibling of SanskritLexicography.
set -euo pipefail

SL="$(cd "$(dirname "$0")/.." && pwd)"        # SanskritLexicography repo root
PWG="$(cd "$SL/../PWG" && pwd)"               # sibling PWG repo
WT="$SL/../_wt_pwg_refresh"                    # throwaway worktree
BR="chore/refresh-pwg-ru-coverage"

git -C "$PWG" fetch origin main -q
git -C "$PWG" worktree remove --force "$WT" 2>/dev/null || true
rm -rf "$WT"
git -C "$PWG" worktree add -q --detach "$WT" origin/main

# Generate straight into the worktree (generator exits non-zero if data missing).
python "$SL/RussianTranslation/src/build_citation_index.py" \
    --out-dir "$WT/pwg_ls/pwg_ru_coverage"

cd "$WT"
# -I 'Last regenerated' ignores the date-only stamp so a scheduled run does not
# open a PR every day just because the "Last regenerated" line changed.
if git diff --quiet -I 'Last regenerated' -- pwg_ls/pwg_ru_coverage; then
    echo "coverage unchanged (ignoring date stamp) — nothing to publish"
    cd "$SL"; git -C "$PWG" worktree remove --force "$WT"
    exit 0
fi

git checkout -B "$BR"
git add pwg_ls/pwg_ru_coverage
git commit -m "pwg_ru_coverage: scheduled refresh $(date +%F)"
git push -u origin "$BR" --force-with-lease
gh pr create --repo sanskrit-lexicon/PWG --base main --head "$BR" \
    --title "pwg_ru_coverage: scheduled refresh" \
    --body "Automated regeneration of the PWG citation-coverage reports (pwg_ls/pwg_ru_coverage) from the RussianTranslation pipeline." \
    2>/dev/null || echo "PR already open"
gh pr merge "$BR" --repo sanskrit-lexicon/PWG --auto --squash 2>/dev/null || true

cd "$SL"; git -C "$PWG" worktree remove --force "$WT"
echo "refresh done — PR opened/updated with auto-merge"
