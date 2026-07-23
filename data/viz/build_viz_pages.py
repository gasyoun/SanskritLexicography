#!/usr/bin/env python3
"""Embed committed census feeds into offline-usable static HTML viz pages.

Reads (never regenerates) the H683 / H685 derived stats:
  ../markup_tag_census.tsv
  ../../RussianTranslation/glossary/ru_gloss_gap_stats.json

Writes:
  markup_tag_heatmap.html
  ru_gloss_gaps.html

Re-run after those feeds change; do not re-crawl csl-orig or corpus_lexicon.
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
TSV = HERE.parent / "markup_tag_census.tsv"
JSON_PATH = ROOT / "RussianTranslation" / "glossary" / "ru_gloss_gap_stats.json"
GENERATED = date.today().isoformat()

CSS = """
  :root { --fg:#1f2328; --mut:#59636e; --bg:#fff; --card:#f6f8fa; --line:#d1d9e0;
          --accent:#0969da; --done:#1a7f37; --run:#9a6700; --block:#d1242f;
          --hi:#0d47a1; --mid:#64b5f6; --lo:#e3f2fd; }
  @media (prefers-color-scheme: dark) {
    :root { --fg:#e6edf3; --mut:#9198a1; --bg:#0d1117; --card:#161b22; --line:#30363d;
            --accent:#4493f8; --done:#3fb950; --run:#d29922; --block:#f85149;
            --hi:#90caf9; --mid:#1565c0; --lo:#0d2137; }
  }
  body { font: 15px/1.5 system-ui, sans-serif; color:var(--fg); background:var(--bg);
         max-width: 1180px; margin: 0 auto; padding: 1.5rem; }
  h1 { font-size: 1.5rem; margin-bottom:.2rem; }
  h2 { font-size: 1.15rem; margin-top: 2rem; }
  .mut { color: var(--mut); font-size: .85rem; }
  a { color: var(--accent); }
  .cards { display: flex; gap: .8rem; flex-wrap: wrap; margin: 1rem 0; }
  .card { background: var(--card); border: 1px solid var(--line); border-radius: 8px;
          padding: .7rem 1.1rem; min-width: 8.5rem; }
  .card b { font-size: 1.55rem; display: block; line-height:1.1; }
  .card .sub { color: var(--mut); font-size: .8rem; }
  table { border-collapse: collapse; width: 100%; font-size: .88rem; }
  th, td { text-align: left; padding: .35rem .55rem; border-bottom: 1px solid var(--line); }
  th { color: var(--mut); font-weight: 600; }
  td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
  .trust { background:var(--card); border:1px solid var(--line); border-left:3px solid var(--accent);
           border-radius:6px; padding:.7rem 1rem; font-size:.83rem; color:var(--mut); margin:1rem 0; }
  .trust b { color:var(--fg); }
  .controls { display:flex; flex-wrap:wrap; gap:.9rem 1.4rem; align-items:center;
              background:var(--card); border:1px solid var(--line); border-radius:8px;
              padding:.7rem 1rem; margin:1rem 0; font-size:.9rem; }
  .controls label { display:inline-flex; align-items:center; gap:.35rem; cursor:pointer; }
  .controls input[type=number] { width:4rem; }
  .bar-wrap { background: var(--card); border:1px solid var(--line); border-radius:8px;
              padding:.9rem 1.1rem; margin:.6rem 0; }
  .bar-row { display:flex; align-items:center; gap:.7rem; margin:.3rem 0; }
  .bar-row .lbl { flex: 0 0 5.5rem; font-variant-numeric:tabular-nums; }
  .bar-row .lbl small { color:var(--mut); }
  .track { flex:1; background:rgba(127,127,127,.14); border-radius:5px; height:1.35rem; overflow:hidden; }
  .fill { height:100%; border-radius:5px 0 0 5px; background:var(--accent); }
  .bar-row .val { flex:0 0 7rem; text-align:right; font-variant-numeric:tabular-nums; font-size:.9rem; }
  .heat-scroll { overflow:auto; max-width:100%; border:1px solid var(--line); border-radius:8px; }
  table.heat { font-size: .72rem; border-collapse: separate; border-spacing: 0; }
  table.heat th, table.heat td { border-bottom:1px solid var(--line); border-right:1px solid var(--line);
                                  padding: .2rem .28rem; white-space:nowrap; }
  table.heat th.corner { position:sticky; left:0; background:var(--card); z-index:2; }
  table.heat th.rowh { position:sticky; left:0; background:var(--card); z-index:1; text-align:left; }
  table.heat th.colh { writing-mode: vertical-rl; transform: rotate(180deg); height:7.5rem;
                       vertical-align:bottom; font-weight:600; color:var(--mut); }
  table.heat td.cell { text-align:center; font-variant-numeric:tabular-nums; min-width:2.2rem; }
  footer { margin-top:2.5rem; color:var(--mut); font-size:.8rem; }
  .nav { font-size:.9rem; margin-bottom:1rem; }
  .nav a { margin-right:1rem; }
"""


def load_tsv() -> list[dict]:
    if not TSV.is_file():
        sys.exit(f"STOP: missing feed {TSV} — do not re-run H683 pipeline from this builder")
    with TSV.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    if not rows:
        sys.exit(f"STOP: empty TSV {TSV}")
    for r in rows:
        r["entries"] = int(r["entries"])
        r["count"] = int(r["count"])
        r["per_1000_entries"] = float(r["per_1000_entries"])
    return rows


def load_json() -> dict:
    if not JSON_PATH.is_file():
        sys.exit(f"STOP: missing feed {JSON_PATH} — do not re-run H685 pipeline from this builder")
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def write_markup(rows: list[dict]) -> None:
    payload = {
        "generated_at": GENERATED,
        "source": "data/markup_tag_census.tsv",
        "rows": [
            {
                "dict": r["dict"],
                "entries": r["entries"],
                "tag": r["tag"],
                "count": r["count"],
                "per_1000": r["per_1000_entries"],
            }
            for r in rows
        ],
    }
    data_js = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Markup-tag census heatmap — SanskritLexicography</title>
<style>{CSS}</style>
</head>
<body>
<p class="nav">
  <a href="ru_gloss_gaps.html">RU-gloss gaps →</a>
  <a href="https://github.com/gasyoun/SanskritLexicography/blob/master/data/MARKUP_TAG_CENSUS_CSLORIG_2026.md">census report</a>
  <a href="https://github.com/gasyoun/SanskritLexicography/blob/master/data/markup_tag_census.tsv">raw TSV</a>
</p>
<h1>Markup-tag census heatmap</h1>
<p class="mut">Per-dictionary × tag frequencies from the FAIR Release #1 / E39 census
  (H683). Cell plot over the committed TSV — no re-crawl of csl-orig.
  Generated <span id="stamp"></span>.</p>

<div class="cards" id="cards"></div>

<div class="controls">
  <label>Metric
    <select id="metric">
      <option value="per_1000" selected>per 1,000 entries</option>
      <option value="count">raw count</option>
    </select>
  </label>
  <label>Top tags
    <input type="number" id="topn" min="5" max="96" value="20">
  </label>
  <label><input type="checkbox" id="struct" checked> hide structural record tags</label>
  <label><input type="checkbox" id="log"> log colour scale</label>
</div>

<h2>Dict × tag (top tags by total count)</h2>
<p class="mut">Rows = dictionaries (entry order). Columns = top-N tags org-wide.
  Hover a cell for the exact value. Structural tags (<code>&lt;L&gt;</code>,
  <code>&lt;LEND&gt;</code>, <code>&lt;pc&gt;</code>, <code>&lt;k1&gt;</code>,
  <code>&lt;k2&gt;</code>, …) sit near 1000/1000 by construction and are hidden by default.</p>
<div class="heat-scroll" id="heat"></div>

<h2>Under-marked dictionaries</h2>
<p class="mut">Lowest non-structural tag density (total non-structural tag hits ÷ entries).
  A sparse markup palette, not a quality score of the lexicon content.</p>
<div class="bar-wrap" id="under"></div>

<h2>Full row table (filterable summary)</h2>
<p class="mut">One row per dictionary: entries, distinct tags in the census, total tag hits,
  non-structural density. Download the long-format TSV for per-tag rows.</p>
<table id="summary">
  <thead><tr>
    <th>dict</th><th class="num">entries</th><th class="num">distinct tags</th>
    <th class="num">total hits</th><th class="num">density (non-struct)</th>
  </tr></thead>
  <tbody></tbody>
</table>

<div class="trust" id="trust"></div>
<footer>
  Offline single-file page; data embedded from
  <a href="https://github.com/gasyoun/SanskritLexicography/blob/master/data/markup_tag_census.tsv">markup_tag_census.tsv</a>
  (CC-BY-4.0). Rebuild: <code>python data/viz/build_viz_pages.py</code>.
  Sibling: headword Jaccard heatmap lives on
  <a href="https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/dictionary-overlap.md">csl-atlas dictionary-overlap</a>
  — not rebuilt here.
</footer>
<script>
'use strict';
const DATA = {data_js};
const STRUCT = new Set(['<L>','<LEND>','<pc>','<k1>','<k2>','<h>','<e>','<info>','<eid>','<syns>']);
const esc = s => String(s).replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
const fmt = n => (n == null ? '—' : Number(n).toLocaleString('en-US'));
const fmtN = (n, d) => (n == null ? '—' : Number(n).toLocaleString('en-US', {{maximumFractionDigits: d}}));

function isStruct(tag) {{ return STRUCT.has(tag); }}

function color(t, log) {{
  // t in [0,1]
  if (t <= 0) return 'transparent';
  const u = log ? Math.log1p(t * 9) / Math.log(10) : t;
  const r0=227,g0=242,b0=253, r1=13,g1=71,b1=161;
  const r = Math.round(r0 + (r1-r0)*u);
  const g = Math.round(g0 + (g1-g0)*u);
  const b = Math.round(b0 + (b1-b0)*u);
  return `rgb(${{r}},${{g}},${{b}})`;
}}
// dark mode: flip low end — use CSS var via opacity on accent instead when prefers dark
function cellBg(t, log) {{
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {{
    if (t <= 0) return 'transparent';
    const u = log ? Math.log1p(t * 9) / Math.log(10) : t;
    const a = 0.12 + 0.78 * u;
    return `rgba(144,202,249,${{a.toFixed(3)}})`;
  }}
  return color(t, log);
}}

function buildIndex() {{
  const dicts = [];
  const seen = new Set();
  const entries = {{}};
  const tagTotals = {{}};
  const by = {{}}; // dict|tag -> row
  for (const r of DATA.rows) {{
    if (!seen.has(r.dict)) {{ seen.add(r.dict); dicts.push(r.dict); entries[r.dict] = r.entries; }}
    tagTotals[r.tag] = (tagTotals[r.tag] || 0) + r.count;
    by[r.dict + '\\0' + r.tag] = r;
  }}
  return {{ dicts, entries, tagTotals, by }};
}}

const IX = buildIndex();

function topTags(n, hideStruct) {{
  return Object.entries(IX.tagTotals)
    .filter(([t]) => !hideStruct || !isStruct(t))
    .sort((a, b) => b[1] - a[1])
    .slice(0, n)
    .map(([t]) => t);
}}

function density(dict, hideStruct) {{
  let hits = 0;
  for (const r of DATA.rows) {{
    if (r.dict !== dict) continue;
    if (hideStruct && isStruct(r.tag)) continue;
    hits += r.count;
  }}
  return hits / IX.entries[dict];
}}

function renderCards() {{
  const nDict = IX.dicts.length;
  const nTag = Object.keys(IX.tagTotals).length;
  const nRows = DATA.rows.length;
  const totalHits = Object.values(IX.tagTotals).reduce((a, b) => a + b, 0);
  document.getElementById('cards').innerHTML =
    `<div class="card"><b>${{fmt(nDict)}}</b><span class="sub">dictionaries</span></div>` +
    `<div class="card"><b>${{fmt(nTag)}}</b><span class="sub">distinct tags</span></div>` +
    `<div class="card"><b>${{fmt(nRows)}}</b><span class="sub">TSV rows</span></div>` +
    `<div class="card"><b>${{fmt(totalHits)}}</b><span class="sub">tag hits (all)</span></div>`;
}}

function renderHeat() {{
  const metric = document.getElementById('metric').value;
  const topn = Math.max(5, Math.min(96, +document.getElementById('topn').value || 20));
  const hideStruct = document.getElementById('struct').checked;
  const log = document.getElementById('log').checked;
  const tags = topTags(topn, hideStruct);
  let maxV = 0;
  const vals = tags.map(tag => IX.dicts.map(d => {{
    const r = IX.by[d + '\\0' + tag];
    const v = r ? (metric === 'count' ? r.count : r.per_1000) : 0;
    if (v > maxV) maxV = v;
    return v;
  }}));
  // vals is tag-major; transpose for rendering
  let html = '<table class="heat"><thead><tr><th class="corner">dict</th>';
  for (const t of tags) html += `<th class="colh" title="${{esc(t)}}">${{esc(t)}}</th>`;
  html += '</tr></thead><tbody>';
  for (let di = 0; di < IX.dicts.length; di++) {{
    const d = IX.dicts[di];
    html += `<tr><th class="rowh">${{esc(d)}}</th>`;
    for (let ti = 0; ti < tags.length; ti++) {{
      const v = vals[ti][di];
      const t = maxV ? v / maxV : 0;
      const title = `${{d}} · ${{tags[ti]}} = ${{metric === 'count' ? fmt(v) : fmtN(v, 2)}}`;
      const lab = v === 0 ? '' : (metric === 'count'
        ? (v >= 1000 ? (v/1000).toFixed(v >= 10000 ? 0 : 1) + 'k' : String(v))
        : (v >= 100 ? String(Math.round(v)) : fmtN(v, 1)));
      html += `<td class="cell" style="background:${{cellBg(t, log)}}" title="${{esc(title)}}">${{lab}}</td>`;
    }}
    html += '</tr>';
  }}
  html += '</tbody></table>';
  document.getElementById('heat').innerHTML = html;
}}

function renderUnder() {{
  const dens = IX.dicts.map(d => [d, density(d, true), IX.entries[d]])
    .sort((a, b) => a[1] - b[1]);
  const maxD = dens[dens.length - 1][1] || 1;
  const el = document.getElementById('under');
  el.innerHTML = dens.slice(0, 12).map(([d, den, ent]) => {{
    const pct = Math.max(1.5, den / maxD * 100);
    return `<div class="bar-row">
      <div class="lbl">${{esc(d)}} <small>${{fmt(ent)}} ent</small></div>
      <div class="track"><div class="fill" style="width:${{pct.toFixed(1)}}%"></div></div>
      <div class="val">${{fmtN(den, 2)}} /ent</div>
    </div>`;
  }}).join('');
}}

function renderSummary() {{
  const rows = IX.dicts.map(d => {{
    const tags = DATA.rows.filter(r => r.dict === d);
    const hits = tags.reduce((a, r) => a + r.count, 0);
    return {{
      d, e: IX.entries[d], n: tags.length, hits, den: density(d, true)
    }};
  }}).sort((a, b) => a.den - b.den);
  document.querySelector('#summary tbody').innerHTML = rows.map(r =>
    `<tr><td>${{esc(r.d)}}</td><td class="num">${{fmt(r.e)}}</td>
     <td class="num">${{fmt(r.n)}}</td><td class="num">${{fmt(r.hits)}}</td>
     <td class="num">${{fmtN(r.den, 2)}}</td></tr>`).join('');
}}

document.getElementById('stamp').textContent = DATA.generated_at;
document.getElementById('trust').innerHTML =
  `<b>Trust block.</b> Feed: <b>${{esc(DATA.source)}}</b> (embedded ${{esc(DATA.generated_at)}}). ` +
  `Census: E39 / H683 · methodology ` +
  `<a href="https://github.com/gasyoun/SanskritLexicography/blob/master/data/MARKUP_TAG_CENSUS_CSLORIG_2026.md">MARKUP_TAG_CENSUS_CSLORIG_2026.md</a>. ` +
  `FAIR package: <a href="https://github.com/gasyoun/SanskritLexicography/blob/master/data/FAIR_RELEASE_1.md">FAIR_RELEASE_1.md</a> (CC-BY-4.0). ` +
  `Generator: <code>data/markup_tag_census.py</code> over csl-orig v02 — this page only charts the committed TSV. ` +
  `Download: <a href="https://raw.githubusercontent.com/gasyoun/SanskritLexicography/master/data/markup_tag_census.tsv">raw TSV</a>.`;

['metric','topn','struct','log'].forEach(id =>
  document.getElementById(id).addEventListener('change', renderHeat));
document.getElementById('topn').addEventListener('input', renderHeat);

renderCards();
renderHeat();
renderUnder();
renderSummary();
</script>
</body>
</html>
"""
    out = HERE / "markup_tag_heatmap.html"
    out.write_text(html, encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size} bytes)")


def write_ru_gloss(stats: dict) -> None:
    payload = {"generated_at": GENERATED, "source": "RussianTranslation/glossary/ru_gloss_gap_stats.json", **stats}
    data_js = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RU-gloss coverage &amp; gap head — SanskritLexicography</title>
<style>{CSS}</style>
</head>
<body>
<p class="nav">
  <a href="markup_tag_heatmap.html">← Markup-tag heatmap</a>
  <a href="https://github.com/gasyoun/SanskritLexicography/blob/master/progress_dashboard/">progress dashboard</a>
  <a href="https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/glossary/ru_gloss_gap_stats.json">raw JSON</a>
</p>
<h1>RU-gloss coverage &amp; gap ranking</h1>
<p class="mut">Committed H685 gap stats over the Russian gloss layers vs dictionary headwords.
  Charts the JSON only — the full gap-list TSV is gitignored (~5.3&nbsp;MB) and is not loaded here.
  Generated <span id="stamp"></span>.</p>

<div class="cards" id="cards"></div>

<h2>Per-dictionary any-layer coverage</h2>
<p class="mut"><code>any_pct</code> = share of headwords with at least one RU layer
  (surface / lemma / root). GRA high · SKD low is the standing pattern.</p>
<div class="bar-wrap" id="cov"></div>

<h2>Token-coverage ladder</h2>
<p class="mut">How much of the DCS-frequency token mass is covered as layers stack.</p>
<div class="bar-wrap" id="ladder"></div>

<h2>Gap head — top 20 DCS-frequent keys still missing RU</h2>
<p class="mut">From <code>gap_head_top20</code>: highest DCS token counts among keys that lack a RU gloss.
  Useful triage for the next translation batch, not a complete gap census.</p>
<table id="gaps">
  <thead><tr>
    <th class="num">#</th><th>key (SLP1)</th><th class="num">DCS count</th><th>dicts</th>
  </tr></thead>
  <tbody></tbody>
</table>

<div class="trust" id="trust"></div>
<footer>
  Offline single-file page; data embedded from
  <a href="https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/glossary/ru_gloss_gap_stats.json">ru_gloss_gap_stats.json</a>.
  Full gap list stays local/gitignored (<code>glossary/ru_gloss_gaps.tsv</code>).
  Rebuild: <code>python data/viz/build_viz_pages.py</code>.
  Translation velocity context:
  <a href="https://github.com/gasyoun/SanskritLexicography/tree/master/progress_dashboard">progress_dashboard/</a>.
</footer>
<script>
'use strict';
const DATA = {data_js};
const esc = s => String(s).replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
const fmt = n => (n == null ? '—' : Number(n).toLocaleString('en-US'));
const fmtN = (n, d) => (n == null ? '—' : Number(n).toLocaleString('en-US', {{maximumFractionDigits: d}}));

function barRow(label, sub, value, total, valText) {{
  const pct = total ? Math.max(1.5, value / total * 100) : 0;
  return `<div class="bar-row">
    <div class="lbl" style="flex-basis:6.5rem">${{esc(label)}}${{sub ? ` <small>${{esc(sub)}}</small>` : ''}}</div>
    <div class="track"><div class="fill" style="width:${{pct.toFixed(1)}}%"></div></div>
    <div class="val">${{valText != null ? valText : fmt(value)}}</div>
  </div>`;
}}

document.getElementById('stamp').textContent = DATA.generated_at;

document.getElementById('cards').innerHTML = [
  ['corpus_rows', 'corpus rows', DATA.corpus_rows],
  ['hapax_rate_pct', 'hapax rate %', DATA.hapax_rate_pct],
  ['gap_keys_total', 'gap keys total', DATA.gap_keys_total],
  ['gap_keys_in_dcs', 'gap keys in DCS', DATA.gap_keys_in_dcs],
  ['corpus_distinct_keys', 'distinct keys', DATA.corpus_distinct_keys],
  ['lemma_layer_keys', 'lemma-layer keys', DATA.lemma_layer_keys],
].map(([_, sub, v]) =>
  `<div class="card"><b>${{typeof v === 'number' && v % 1 ? fmtN(v, 2) : fmt(v)}}</b><span class="sub">${{esc(sub)}}</span></div>`
).join('');

const cov = Object.entries(DATA.per_dict_coverage || {{}})
  .map(([d, x]) => ({{ d, ...x }}))
  .sort((a, b) => b.any_pct - a.any_pct);
const maxPct = 100;
document.getElementById('cov').innerHTML = cov.map(r =>
  barRow(r.d, `${{fmt(r.any)}}/${{fmt(r.headwords)}}`, r.any_pct, maxPct,
         `${{fmtN(r.any_pct, 2)}}%`)
).join('');

const ladder = DATA.token_coverage_pct || {{}};
const order = [
  ['dcs_only', 'DCS lemma only'],
  ['plus_vidyut', '+ Vidyut'],
  ['plus_marker', '+ marker layer'],
];
document.getElementById('ladder').innerHTML = order.map(([k, lab]) =>
  barRow(lab, k, ladder[k] || 0, 100, `${{fmtN(ladder[k], 2)}}%`)
).join('');

const gaps = DATA.gap_head_top20 || [];
document.querySelector('#gaps tbody').innerHTML = gaps.length
  ? gaps.map((g, i) =>
      `<tr><td class="num">${{i + 1}}</td><td><code>${{esc(g.key)}}</code></td>
       <td class="num">${{fmt(g.dcs_count)}}</td>
       <td class="mut">${{esc((g.dicts || []).join(', '))}}</td></tr>`).join('')
  : '<tr><td colspan="4" class="mut">no gap_head_top20 in feed</td></tr>';

document.getElementById('trust').innerHTML =
  `<b>Trust block.</b> Feed: <b>${{esc(DATA.source)}}</b> (embedded ${{esc(DATA.generated_at)}}). ` +
  `H685 RU-gloss gap stats — corpus rows ${{fmt(DATA.corpus_rows)}}, gap keys ${{fmt(DATA.gap_keys_total)}} ` +
  `(${{fmt(DATA.gap_keys_in_dcs)}} attested in DCS). ` +
  `DCS frequency meta: ${{esc((DATA.dcs_freq_meta && DATA.dcs_freq_meta.source) || 'n/a')}}. ` +
  `The full gap list (<code>${{esc(DATA.gap_list_file || 'glossary/ru_gloss_gaps.tsv')}}</code>) is gitignored and is ` +
  `<b>not</b> committed or loaded by this page — chart the JSON only. ` +
  `Download: <a href="https://raw.githubusercontent.com/gasyoun/SanskritLexicography/master/RussianTranslation/glossary/ru_gloss_gap_stats.json">raw JSON</a>. ` +
  `No rights-gated raw corpus is embedded.`;
</script>
</body>
</html>
"""
    out = HERE / "ru_gloss_gaps.html"
    out.write_text(html, encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size} bytes)")


def write_readme() -> None:
    text = f"""# data/viz — static charts over committed census feeds

_Created: 23-07-2026 · Last updated: 23-07-2026_

Offline single-file HTML pages that **chart already-committed derived stats** —
they do not re-crawl csl-orig or corpus_lexicon.

| Page | Feed | Handoff |
|---|---|---|
| [markup_tag_heatmap.html](https://github.com/gasyoun/SanskritLexicography/blob/master/data/viz/markup_tag_heatmap.html) | [`../markup_tag_census.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/markup_tag_census.tsv) | H683 / E39 / FAIR #1 |
| [ru_gloss_gaps.html](https://github.com/gasyoun/SanskritLexicography/blob/master/data/viz/ru_gloss_gaps.html) | [`../../RussianTranslation/glossary/ru_gloss_gap_stats.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/glossary/ru_gloss_gap_stats.json) | H685 |

## Rebuild

```bash
python data/viz/build_viz_pages.py
```

Stops with a clear error if either feed is missing. Does **not** regenerate the
TSV/JSON — only re-embeds them into the HTML.

## Explicit non-goals

- Headword Jaccard heatmap — already on
  [csl-atlas dictionary-overlap](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/dictionary-overlap.md).
- Committing `ru_gloss_gaps.tsv` (gitignored full gap list).

Generated snapshot date baked into the HTML: **{GENERATED}** (H1527).

_Dr. Mārcis Gasūns_
"""
    out = HERE / "README.md"
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(ROOT)}")


def main() -> None:
    rows = load_tsv()
    stats = load_json()
    write_markup(rows)
    write_ru_gloss(stats)
    write_readme()


if __name__ == "__main__":
    main()
