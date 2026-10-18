"""Declaration of generated single-writer artifact paths (H3073 contract).

Imported by scripts/pre_push_stale_base_check.py: a path listed in
GENERATED_SINGLE_WRITER_PATHS is replaced WHOLESALE by its own writer, so a
push that deletes fresh-looking lines in it destroys no work and is exempt
from the stale-base heuristic instead of tripping it by construction.

WIDENING RULE: a path enters this set only with a named sole writer below.
Loosening the check in the guard is never the fix — add the path here.

Provenance: SL findings dashboard refresh (Task Scheduler task
"SL findings dashboard refresh") was refused at its final step on 03-09-2026 —
refresh.log shows all build steps OK, then `git push origin HEAD:master`
blocked by the stale-base guard on the wholesale regenerated
findings_dashboard/*.json (diagnosed 20-09-2026 in Uprava H5183; same class
Uprava fixed for its own dashboards by declaring generated_artifact_paths).
"""
from __future__ import annotations

# master branch — written by findings_dashboard/monthly_refresh.py via
# findings_dashboard/build_findings_data.py + probe_platforms.py (sole writer:
# the monthly refresh).
# gh-pages branch — publish step of the same refresh (PUBLISH list), sole
# writer: the monthly refresh.
GENERATED_SINGLE_WRITER_PATHS = frozenset({
    "findings_dashboard/data.json",
    "findings_dashboard/timeseries.json",
    "findings_dashboard/platform_status.json",
    "findings/index.html",
    "findings/data.json",
    "findings/timeseries.json",
    "findings/platform_status.json",
})
