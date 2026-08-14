# H2675 — W1 Flash PREP `--live` drain-head

_Created: 14-08-2026 · Last updated: 14-08-2026_

Report: [REPORT.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2675_w1_prep/REPORT.md).

```text
python experiments/H2675_w1_prep/build_drain_head.py --limit 5000
python experiments/H2675_w1_prep/run_prep_live.py --phase first200 --workers 24
python experiments/H2675_w1_prep/run_prep_live.py --phase scale --only-if-gate --max-keys 80 --batch-size 40
```

`--live` requires the H2674 client (`DEFAULT_MAX_TOKENS=32768`) and `ORS-FAQ/.env` `DEEPSEEK_API_KEY`. Sidecars land in gitignored `RussianTranslation/prep/h2675/`.

_Dr. Mārcis Gasūns_
