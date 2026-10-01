---
name: c1-profile-routes-to-zai-glm-check-base-url-before-paid-window
description: The pwg_ru c1 slot on MSI routed to z.ai GLM 5.3 from 20-09 13:42Z until a human restored Anthropic on 22-09; read the profile's ANTHROPIC_BASE_URL before any paid window, and prove the route by response-id format, never by model label
metadata:
  type: project
---

From 2026-09-20T13:42:30Z to 2026-09-22, `D:\ClaudeTools\profiles\claude1\.claude\settings.json` on MSI set `ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic`, a z.ai `ANTHROPIC_AUTH_TOKEN`, `API_TIMEOUT_MS`, and mapped haiku/sonnet/opus to `glm-5.3-flash[1m]` / `glm-5.3[1m]`. The headless lane (`headless_worker.py`, safe mode) inherits that `env` block: the 21-09 canary was rejected by z.ai with `429 [1310] Weekly/Monthly Limit Exhausted`.

**Restored 22-09-2026** on a human ruling («restore Anthropic», H4527): those six keys were removed; the untouched original is `settings.json.pre-h4527-restore-anthropic-22-09.bak` beside it, so reverting is one copy.

**The route discriminator is the response id, not the model name.** Transcripts under `claude1\.claude\projects\` echo the requested name (`claude-sonnet-5`) on either route. Anthropic answers carry `message.id` `msg_011C…` and a `requestId` `req_011C…`; the z.ai-era transcript of 20-09 ~18:00Z carries `msg_202609…` and no `requestId`. So the 20-09 H4527 acceptance card (`darv_i~~h0_zz_pw`) was produced by GLM 5.3 and promoted under a `claude-sonnet-5` label.

**Why:** a profile slot name (`c1`, "max") is a route, not proof of which model answers. A paid window on a redirected slot either hits a foreign quota wall or promotes cards under a wrong `gen_model` label.

**How to apply:** before any paid `c1` window, read only the `ANTHROPIC_BASE_URL` line of that settings file (never token values). If it is set, stop and ask a human which route the lane should use. After the canary, check the newest transcript's `message.id` prefix. Evidence: [H4527_C1_ZAI_ROUTE_QUOTA_EXHAUSTED_VOLUME_BLOCKED_21-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_C1_ZAI_ROUTE_QUOTA_EXHAUSTED_VOLUME_BLOCKED_21-09-2026.md) · [H4527_C1_ANTHROPIC_ROUTE_RESTORED_VOLUME_LAUNCH_22-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_C1_ANTHROPIC_ROUTE_RESTORED_VOLUME_LAUNCH_22-09-2026.md).
