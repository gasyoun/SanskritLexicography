- H5402: **`kast_ur_i` still unpromoted — the blocker moved from `c1` auth to the `c1` probe
  ration.** A second unattended pass re-probed the live gates on `msi` at 18:20–18:30Z and
  spent **zero paid calls**. The 06:22Z blocker is retired: the `c1` profile's
  `.credentials.json` was rewritten 14:48:44Z and `claude auth status` now reads `loggedIn
  true` / `firstParty` / `max`; the route is still Anthropic (settings.json unchanged since
  23-09 20:47:52Z, no `ANTHROPIC*` in the User or Machine environment). What refuses now is
  `probe-ration --account c1`: `legal_now false`, `next_legal_utc 2026-09-24T21:20:17Z`
  against `max_per_utc_day 2` / `min_gap_s 21600`, and the subcommand exits 3 when rationed.
  The day's one attempt was spent at 15:20:17Z as a `probe:warmup` by the **sibling H5403**
  session, which prepared four nominal leases (`h5403vol25/35/39/40`) and a canary manifest
  and then stopped without running it — so no card was generated on `c1` today and no 200
  receipt exists to prove the re-login actually took. Lease `h4527vol14` is untouched at
  `requeue_prepared` (`rq02-defect`, `kast_ur_i~~h0_zz_pw`), so the authorized 4-call recipe
  runs unchanged after 21:20:17Z — that is the day's second and last probe attempt, which
  the H5403 lane also wants. Nothing was overridden. Evidence §6:
  [H5402_KASTURI_GATES_PASSED_STOPPED_ON_CALL_CAP_24-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5402/H5402_KASTURI_GATES_PASSED_STOPPED_ON_CALL_CAP_24-09-2026.md).
