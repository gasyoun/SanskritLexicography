# NOMINAL_W1_100SMALL — first cheap nominal window

_Prepared: 05-07-2026 · Executor: Codex/GPT-5 · No Max/Workflow run performed._

## Selection

- Source core: `src/pilot/lexical_cores/pril5.slp1.txt`.
- Runnable nominal candidates: 4292; scored with generated inputs: 4292; missing inputs: 0.
- Selection rule: lowest deterministic agent count, then <ls>, sense delimiters, raw bytes, original pril5 rank.
- Chosen window: 100 runtime keys; 100 true SLP1 headwords recorded in `NOMINAL_W1_100SMALL.selection.json`.

## Preflight

- Command: `python src/pilot/perf_preflight.py nominal_w1_100small --nominal --keys=<100> --json`.
- Result: 3 batches, 3 expected agents, 0 presplit keys, 0 `defer_monster` keys.
- Cost gate: ok; estimated 745200 tokens / $1.41 total / $0.01 per translated card.
- Harness smoke: `gen_opt_harness2.py ... --out=src/pilot/run_pilot_wf.nominal_w1_100small.js` emitted 274,848 bytes, under the 480 KB cap; `node --check` passed.

## Keys

| # | runtime key | SLP1 headword | agents | <ls> | raw bytes |
|---:|---|---|---:|---:|---:|
| 1 | `n_ar_i` | `nArI` | 0 | 0 | 95 |
| 2 | `_adika` | `Adika` | 0 | 0 | 95 |
| 3 | `Goza` | `Goza` | 0 | 0 | 96 |
| 4 | `tray_i` | `trayI` | 0 | 0 | 97 |
| 5 | `br_ahm_i` | `brAhmI` | 0 | 0 | 99 |
| 6 | `vr_iq_a` | `vrIqA` | 1 | 0 | 210 |
| 7 | `_sulva` | `Sulva` | 1 | 0 | 225 |
| 8 | `ka_rq_u` | `kaRqU` | 1 | 0 | 230 |
| 9 | `pf_tv_i` | `pfTvI` | 1 | 0 | 231 |
| 10 | `yAtu` | `yAtu` | 1 | 0 | 232 |
| 11 | `vitAna` | `vitAna` | 1 | 0 | 233 |
| 12 | `p_ina` | `pIna` | 1 | 0 | 237 |
| 13 | `urv_i` | `urvI` | 1 | 0 | 240 |
| 14 | `Savas` | `Savas` | 1 | 0 | 245 |
| 15 | `vittama` | `vittama` | 1 | 0 | 249 |
| 16 | `mf_rmaya` | `mfRmaya` | 1 | 0 | 253 |
| 17 | `viGna` | `viGna` | 1 | 0 | 259 |
| 18 | `sUri` | `sUri` | 1 | 0 | 260 |
| 19 | `Salya` | `Salya` | 1 | 0 | 270 |
| 20 | `y_avat` | `yAvat` | 1 | 0 | 273 |
| 21 | `satkAra` | `satkAra` | 1 | 0 | 289 |
| 22 | `jarAyu` | `jarAyu` | 1 | 0 | 291 |
| 23 | `rAmaWa` | `rAmaWa` | 1 | 0 | 305 |
| 24 | `aDvan` | `aDvan` | 1 | 0 | 310 |
| 25 | `hUti` | `hUti` | 1 | 0 | 310 |
| 26 | `sattvaka` | `sattvaka` | 1 | 0 | 318 |
| 27 | `j_at_i` | `jAtI` | 1 | 0 | 398 |
| 28 | `pAka` | `pAka` | 1 | 0 | 574 |
| 29 | `tridoza` | `tridoza` | 1 | 0 | 575 |
| 30 | `anukampA` | `anukampA` | 1 | 0 | 821 |
| 31 | `aSru` | `aSru` | 1 | 0 | 932 |
| 32 | `sAnu` | `sAnu` | 1 | 0 | 962 |
| 33 | `sattA` | `sattA` | 1 | 0 | 979 |
| 34 | `utsAha` | `utsAha` | 1 | 0 | 980 |
| 35 | `Apta` | `Apta` | 1 | 0 | 992 |
| 36 | `anaquh` | `anaquh` | 1 | 0 | 996 |
| 37 | `anvita` | `anvita` | 1 | 0 | 1092 |
| 38 | `majjA` | `majjA` | 1 | 0 | 1134 |
| 39 | `ucita` | `ucita` | 1 | 0 | 1155 |
| 40 | `vaSa` | `vaSa` | 1 | 0 | 1187 |
| 41 | `vAsa` | `vAsa` | 1 | 0 | 1187 |
| 42 | `vasA` | `vasA` | 1 | 0 | 1187 |
| 43 | `vaSA` | `vaSA` | 1 | 0 | 1187 |
| 44 | `vAsA` | `vAsA` | 1 | 0 | 1187 |
| 45 | `utTa` | `utTa` | 1 | 0 | 1393 |
| 46 | `ahar` | `ahar` | 1 | 0 | 1509 |
| 47 | `kalaSa` | `kalaSa` | 1 | 0 | 1554 |
| 48 | `pAtra` | `pAtra` | 1 | 0 | 3302 |
| 49 | `catur` | `catur` | 1 | 0 | 7738 |
| 50 | `vedikA` | `vedikA` | 1 | 0 | 1367 |
| 51 | `paTin` | `paTin` | 1 | 0 | 256 |
| 52 | `nibarha_ra` | `nibarhaRa` | 1 | 0 | 417 |
| 53 | `nirb_ija` | `nirbIja` | 1 | 0 | 423 |
| 54 | `prota` | `prota` | 1 | 0 | 1487 |
| 55 | `menA` | `menA` | 1 | 0 | 1708 |
| 56 | `arSas` | `arSas` | 1 | 1 | 119 |
| 57 | `sa_mkalik_a` | `saMkalikA` | 1 | 1 | 124 |
| 58 | `Gawa` | `Gawa` | 1 | 1 | 141 |
| 59 | `vic_ara_r_a` | `vicAraRA` | 1 | 1 | 152 |
| 60 | `kAnana` | `kAnana` | 1 | 1 | 159 |
| 61 | `nIla` | `nIla` | 1 | 1 | 190 |
| 62 | `manoraTa` | `manoraTa` | 1 | 1 | 200 |
| 63 | `mAza` | `mAza` | 1 | 1 | 233 |
| 64 | `SUla` | `SUla` | 1 | 1 | 257 |
| 65 | `kzuDA` | `kzuDA` | 1 | 1 | 258 |
| 66 | `vAsin` | `vAsin` | 1 | 1 | 272 |
| 67 | `vaSin` | `vaSin` | 1 | 1 | 272 |
| 68 | `SrAvaka` | `SrAvaka` | 1 | 1 | 282 |
| 69 | `j_urti` | `jUrti` | 1 | 1 | 283 |
| 70 | `maKa` | `maKa` | 1 | 1 | 287 |
| 71 | `Anana` | `Anana` | 1 | 1 | 288 |
| 72 | `SUlin` | `SUlin` | 1 | 1 | 291 |
| 73 | `n_ilik_a` | `nIlikA` | 1 | 1 | 294 |
| 74 | `havyavAha` | `havyavAha` | 1 | 1 | 299 |
| 75 | `bARa` | `bARa` | 1 | 1 | 300 |
| 76 | `BAra` | `BAra` | 1 | 1 | 300 |
| 77 | `Bara` | `Bara` | 1 | 1 | 300 |
| 78 | `_amar_sa` | `AmarSa` | 1 | 1 | 304 |
| 79 | `a_sokadatta` | `aSokadatta` | 1 | 1 | 307 |
| 80 | `pariGa` | `pariGa` | 1 | 1 | 308 |
| 81 | `_dm_ana` | `DmAna` | 1 | 1 | 309 |
| 82 | `aSani` | `aSani` | 1 | 1 | 313 |
| 83 | `mah_avy_ahfti` | `mahAvyAhfti` | 1 | 1 | 315 |
| 84 | `Soza` | `Soza` | 1 | 1 | 316 |
| 85 | `viSAla` | `viSAla` | 1 | 1 | 321 |
| 86 | `Atura` | `Atura` | 1 | 1 | 323 |
| 87 | `utTApana` | `utTApana` | 1 | 1 | 323 |
| 88 | `vIqu` | `vIqu` | 1 | 1 | 324 |
| 89 | `pramARa` | `pramARa` | 1 | 1 | 325 |
| 90 | `praSna` | `praSna` | 1 | 1 | 327 |
| 91 | `guhacandra` | `guhacandra` | 1 | 1 | 328 |
| 92 | `_k_apara` | `KApara` | 1 | 1 | 330 |
| 93 | `dvi_satatama` | `dviSatatama` | 1 | 1 | 331 |
| 94 | `sAmba` | `sAmba` | 1 | 1 | 333 |
| 95 | `jamb_udv_ipa` | `jambUdvIpa` | 1 | 1 | 335 |
| 96 | `parihAra` | `parihAra` | 1 | 1 | 338 |
| 97 | `k_a_ra_b_uti` | `kARaBUti` | 1 | 1 | 338 |
| 98 | `r_ajav_ahana` | `rAjavAhana` | 1 | 1 | 339 |
| 99 | `vaSya` | `vaSya` | 1 | 1 | 340 |
| 100 | `b_alacandrik_a` | `bAlacandrikA` | 1 | 1 | 340 |

## Downstream Run

Run only in a Sonnet Max/Workflow session using the emitted H### handoff. Do not rerun the top-size `pril10_w1` anti-pattern.

_Dr. Mārcis Gasūns_
