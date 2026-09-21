_Created: 21-09-2026 · Last updated: 21-09-2026_

- H4527: **the volume launch on `c1` is blocked, because `c1` now routes to z.ai GLM 5.3 and that
  plan's quota is used up.** A human chose the volume route over parking on 21-09. The pass prepared
  five eligible one-card leases with `--require-senses 1` (`h4527vol09/10/11/14/22`), but the
  canary was rejected with `429 [1310] Weekly/Monthly Limit Exhausted`, resetting
  2026-09-24 02:13:42 (time zone not stated). The cause: the `c1` profile's `settings.json` was
  changed on 20-09 at 13:42Z to `ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic`, with
  sonnet/opus mapped to `glm-5.3[1m]`. The 20-09 acceptance card ran after that change, so its
  model is unverified. The pass also found that `no_pwg_scale_plan.py --headless --dry-run`
  registers leases, and that the dashboard rewrite hazard fires at master HEAD. Both were undone
  or recorded. Packet: `pwg_ru/h4527/H4527_C1_ZAI_ROUTE_QUOTA_EXHAUSTED_VOLUME_BLOCKED_21-09-2026.md`;
  ledger entry `H4527_C1_ZAI_QUOTA_429_CANARY_2026-09-21`. 0 paid tokens.
