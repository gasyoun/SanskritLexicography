---
name: c1-profile-routes-to-zai-glm-check-base-url-before-paid-window
description: The pwg_ru c1 slot on MSI routes to z.ai GLM 5.3 since 20-09-2026 13:42Z; read the profile's ANTHROPIC_BASE_URL before any paid window, because transcript model labels are not provenance
metadata:
  type: project
---

Since 2026-09-20T13:42:30Z, `D:\ClaudeTools\profiles\claude1\.claude\settings.json` on MSI sets `ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic` and maps sonnet/opus to `glm-5.3[1m]`. The headless lane (`headless_worker.py`, safe mode) inherits it: the 21-09 canary was rejected by z.ai with `429 [1310] Weekly/Monthly Limit Exhausted`. Transcripts still say `claude-sonnet-5`, because they echo the requested name. So the 20-09 H4527 acceptance card was very likely produced by GLM 5.3.

**Why:** a profile slot name (`c1`, "max") is a route, not proof of which model answers. A paid window on a redirected slot either hits a foreign quota wall or promotes cards under a wrong `gen_model` label.

**How to apply:** before any paid `c1` window, read only the `ANTHROPIC_BASE_URL` line of that settings file (never token values). If it is set, stop and ask a human which route the lane should use. Evidence: [H4527_C1_ZAI_ROUTE_QUOTA_EXHAUSTED_VOLUME_BLOCKED_21-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_C1_ZAI_ROUTE_QUOTA_EXHAUSTED_VOLUME_BLOCKED_21-09-2026.md).
