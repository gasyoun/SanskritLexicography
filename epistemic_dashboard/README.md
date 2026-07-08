# epistemic_dashboard — the seven epistemic sibling registries at a glance

_Created: 08-07-2026 · Last updated: 08-07-2026_

A companion to [`findings_dashboard/`](https://github.com/gasyoun/SanskritLexicography/tree/master/findings_dashboard), over the **seven epistemic sibling registries** minted under [H356](https://github.com/gasyoun/Uprava/blob/main/handoffs/H356-Opus_csl-corrections_epistemic-sibling-registries_08.07.26.md): [`ASSUMPTIONS`](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) · [`CONTRADICTIONS`](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) · [`GAPS`](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) · [`DEAD_ENDS`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) · [`RECIPES`](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) · [`STALENESS`](https://github.com/gasyoun/SanskritLexicography/blob/master/STALENESS.md) · [`GLOSSARY`](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md).

**Published (Sanskrit-data side only):** <https://gasyoun.github.io/SanskritLexicography/epistemic/> — refreshed monthly by the [`findings-dashboard`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/findings-dashboard.yml) workflow (3rd of each month). The **infra / process** side lives in the private [Uprava](https://github.com/gasyoun/Uprava) repo and is viewed locally, never published.

## What it shows

- Total rows, layer count, and the **⚙️ auto vs ✍️ human** origin split — the health signal, since the registries are designed to be machine-seeded and hand-confirmed.
- A per-layer table: the epistemic act each holds, row count, importance breakdown (🔴🟠🟡), and an origin bar.
- The STALENESS decay summary (🔴 >6 mo · 🟡 3–6 mo · 🟢 fresh · ⬜ undated).

## Files

- [`index.html`](index.html) — self-contained (no external assets), fetches `epistemic.json`.
- `epistemic.json` — generated; the per-layer parse of the registries.
- [`build_epistemic_dashboard.py`](build_epistemic_dashboard.py) — **vendored, byte-identical** copy of the canonical builder in [`sanskrit-util/tools/epistemic/`](https://github.com/sanskrit-lexicon/sanskrit-util/tree/main/tools/epistemic); re-vendor on version bump via [`/cologne-sanskrit-util-sync`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md). Kept in-repo so CI self-builds without installing the package.

## Regenerate locally

```sh
python epistemic_dashboard/build_epistemic_dashboard.py \
  --dir . --side sanskrit \
  --repo-url https://github.com/gasyoun/SanskritLexicography/blob/master \
  --out epistemic_dashboard/epistemic.json
```

_Dr. Mārcis Gasūns_
