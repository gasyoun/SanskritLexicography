# PWG delivery report (derived, H4052)

Surface: `pwg-ru-data durable TM mirror` · store sha256 `79d72dbcb4b33fc88d9e907dec9ecaa0e56ebfb72495a5115ce951a623f8ca65`

| measure | value |
|---|---|
| store sense rows | 11519 |
| headwords (distinct key1) | 221 |
| subcards (distinct key1+subcard) | 2449 |
| approved | 3 |
| print-ready (store_flags predicate) | 3 |
| review queue | unknown (surface absent on this box) |
| gold labels | unknown (surface absent on this box) |
| TM fragments | unknown (surface absent on this box) |
| released edition | no (G10 blocked) |
| last row generated_at | 2026-08-29T08:49:35Z |
| last mirror ledger entry | {"handoff": "H3947", "ts": "20260902T202344Z", "action": "mirror refreshed from src store", "src_rows": 11519, "mirror_rows_before": 11519, "mirror_rows_after": 11519, "only_mirror_dropped": 0, "dropped_quarantined": 0, "dropped_id_churn": 0, "dropped_superseded_acked": 0, "dropped_unexplained": 0, "ack_superseded_file": null, "only_src_added": 0, "forced": false, "mirror_sha_before": "58c2172607c34928b417178d50ee80823956c4ccdde5f4d49ab8b0407e06faf0", "mirror_sha_after": "79d72dbcb4b33fc88d9e907dec9ecaa0e56ebfb72495a5115ce951a623f8ca65", "backup": "pwg_ru_translated.jsonl.h3947.20260902T202344Z.bak"} |

## Lane A seven-key chain — one disposition per key

| key | class | in store | disposition | reason code |
|---|---|---|---|---|
| `jar_ayu` | defect | False | residual_unfired | wrapper_never_emitted (FINDINGS §614) |
| `r_ama_wa` | defect | False | residual_unfired | wrappers_intact_other_defect (H3663 §4) |
| `_s_ulin` | defect | False | residual_unfired | wrapper_never_emitted (FINDINGS §614) |
| `ut_ta` | defect | False | residual_unfired | wrappers_intact_other_defect (H3663 §4) |
| `y_atu` | defect | False | residual_unfired | wrappers_intact_other_defect (H3663 §4) |
| `v_as_a` | defect | False | residual_unfired | wrappers_intact_other_defect (H3663 §4) |
| `ut_t_apana` | transient | False | residual_unfired | transient_retry_heal_exhausted (H3663 §3) |

Chain funnel: selected=7 · paid calls=0 (staged only, H3679) · audit-clean new=0 · promoted=0 · approved=0 · released=0 · durable fire inputs=14/7 keys

Receipt classification (delivered-translation assertion): {"H3679": "staged_only", "H3690": "reconciliation"}

Delta: reproduces the 04-09 audit baseline exactly (rows and sha256). The durable mirror has held 11 519 rows since 29-08 11:24Z (H3663 refreshes) and converged byte-exact to the Windows canonical on 02-09 (H3947 refresh, mirror_sha 58c21726... -> 79d72dbc...); the H3690 "11 462 durable base" verdict is superseded by the append-only ledger, and the fire-time (a)/(b) store-base gate is satisfied on durable evidence.

Unknown surfaces (missing evidence is unknown, never zero): review_queue_csv, gold_csv, tm_fragments

Remaining work owner: Uprava GTD `@DO` — Fire H3679 paid c1 window (7 held Lane A keys), active and bounded.

_Dr. Mārcis Gasūns_
