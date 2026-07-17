#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a self-contained, filterable HTML view of FEATURES_INDEX.md.

The "Каталог каталогов" interactive artifact promised in FEATURES_INDEX.md's
"Interactive view" note: search + category tabs + status/tier/language filters
+ a changelog, over the same catalogue, rendered from the Markdown source so the
two never drift. Pure stdlib, no dependencies.

Usage:
    python build_features_index_html.py [--src FEATURES_INDEX.md] [--out features_index.html]

Auto-generated output; do not hand-edit features_index.html — edit the Markdown
source and re-run.
"""
import argparse
import html
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
CODE_RE = re.compile(r"`([^`]+)`")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
ITAL_RE = re.compile(r"(?<!\*)\*(?!\*)([^*]+)\*(?!\*)")


def md_inline_to_html(text):
    """Convert the small Markdown subset used in cells to safe HTML."""
    # Protect by escaping first, then re-introduce the tags we allow.
    out = html.escape(text, quote=False)
    # Links: [text](url)  -> re-run on escaped text (brackets/parens survive escape)
    def _link(m):
        label, url = m.group(1), m.group(2)
        url = url.replace('"', "%22")
        return f'<a href="{url}" target="_blank" rel="noopener">{label}</a>'
    out = LINK_RE.sub(_link, out)
    out = BOLD_RE.sub(r"<strong>\1</strong>", out)
    out = CODE_RE.sub(r"<code>\1</code>", out)
    out = ITAL_RE.sub(r"<em>\1</em>", out)
    return out


def strip_md(text):
    """Plain-text form of a cell (for search + attribute extraction)."""
    t = LINK_RE.sub(r"\1", text)
    t = t.replace("*", "").replace("`", "")
    return t.strip()


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def is_sep_row(line):
    return bool(re.match(r"^\|?[\s:|-]+\|[\s:|-]+$", line.strip())) and "-" in line


def parse(md_text):
    """Return (glance, sections) where sections is a list of dicts:
    {h2, h3, headers, rows:[[cells]]}."""
    lines = md_text.splitlines()
    glance = ""
    sections = []
    h2 = h3 = ""
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            h2 = line[3:].strip()
            h3 = ""
        elif line.startswith("### "):
            h3 = line[4:].strip()
        elif line.startswith("**At a glance:**"):
            glance = strip_md(line.replace("**At a glance:**", "")).strip()
        elif line.strip().startswith("|") and i + 1 < len(lines) and is_sep_row(lines[i + 1]):
            headers = split_row(line)
            rows = []
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                if is_sep_row(lines[i]):
                    i += 1
                    continue
                rows.append(split_row(lines[i]))
                i += 1
            sections.append({"h2": h2, "h3": h3, "headers": headers, "rows": rows})
            continue
        i += 1
    return glance, sections


# --- category routing -------------------------------------------------------
def category_of(sec):
    h2 = sec["h2"].lower()
    if h2.startswith("i.") or "data asset" in h2:
        return "data"
    if h2.startswith("ii.") or "dictionaries" in h2:
        return "dictionaries"
    if h2.startswith("iii.") or "interfaces" in h2:
        return "interfaces"
    if h2.startswith("iv.") or h2.startswith("tools") or "tools" in h2:
        return "tools"
    if h2.startswith("vi.") or "methods" in h2 or "algorithm" in h2:
        return "methods"
    if h2.startswith("v.") or "drill" in h2:
        return "drills"
    if "changelog" in h2:
        return "changelog"
    if "contributing" in h2:
        return "contributing"
    return "other"


STATUS_RE = re.compile(r"(🟢|🟡|🔴|⚪|🔵)")


def row_status(cells_plain):
    joined = " ".join(cells_plain)
    if "Live" in joined:
        return "live"
    if "Beta" in joined:
        return "beta"
    return ""


def row_tier(cells_plain):
    joined = " ".join(cells_plain)
    if "🟢" in joined:
        return "large"
    if "🟡" in joined:
        return "medium"
    if "⚪" in joined:
        return "small"
    return ""


TABS = [
    ("data", "Данные"),
    ("dictionaries", "Словари"),
    ("interfaces", "Интерфейсы"),
    ("tools", "Инструменты"),
    ("drills", "Упражнения"),
    ("methods", "Методы"),
    ("changelog", "Changelog"),
]


def build_html(glance, sections, src_name):
    cat_rows = {k: [] for k, _ in TABS}
    languages = set()
    for sec in sections:
        cat = category_of(sec)
        if cat not in cat_rows:
            continue
        headers = sec["headers"]
        try:
            lang_idx = next(n for n, h in enumerate(headers) if strip_md(h).lower() in ("language",))
        except StopIteration:
            lang_idx = None
        for cells in sec["rows"]:
            plain = [strip_md(c) for c in cells]
            html_cells = [md_inline_to_html(c) for c in cells]
            lang = plain[lang_idx] if lang_idx is not None and lang_idx < len(plain) else ""
            if lang:
                languages.add(lang)
            cat_rows[cat].append({
                "h3": sec["h3"],
                "headers": [strip_md(h) for h in headers],
                "cells": html_cells,
                "search": " ".join(plain).lower(),
                "status": row_status(plain),
                "tier": row_tier(plain),
                "lang": lang,
            })

    def render_cat(cat):
        rows = cat_rows[cat]
        if not rows:
            return f'<div class="pane" data-cat="{cat}"><p class="empty">Нет записей.</p></div>'
        # group by h3 subsection
        blocks = []
        cur_h3 = None
        buf = []

        def flush():
            if not buf:
                return
            hdrs = buf[0]["headers"]
            thead = "".join(f"<th>{html.escape(h)}</th>" for h in hdrs)
            trs = []
            for r in buf:
                tds = "".join(f"<td>{c}</td>" for c in r["cells"])
                trs.append(
                    f'<tr data-search="{html.escape(r["search"], quote=True)}" '
                    f'data-status="{r["status"]}" data-tier="{r["tier"]}" '
                    f'data-lang="{html.escape(r["lang"], quote=True)}">{tds}</tr>'
                )
            sub = f'<h3 class="sub">{html.escape(cur_h3)}</h3>' if cur_h3 else ""
            blocks.append(
                sub + f'<div class="tblwrap"><table><thead><tr>{thead}</tr></thead>'
                f'<tbody>{"".join(trs)}</tbody></table></div>'
            )

        for r in rows:
            if r["h3"] != cur_h3:
                flush()
                buf = []
                cur_h3 = r["h3"]
            buf.append(r)
        flush()
        active = " active" if cat == "data" else ""
        return f'<div class="pane{active}" data-cat="{cat}">{"".join(blocks)}</div>'

    panes = "".join(render_cat(k) for k, _ in TABS)
    tabs_html = "".join(
        f'<button class="tab{" active" if k == "data" else ""}" data-tab="{k}">'
        f'{html.escape(label)} <span class="cnt">{len(cat_rows[k])}</span></button>'
        for k, label in TABS
    )
    lang_opts = "".join(
        f'<option value="{html.escape(l, quote=True)}">{html.escape(l)}</option>'
        for l in sorted(languages)
    )
    glance_html = md_inline_to_html(glance) if glance else ""

    return TEMPLATE.format(
        glance=glance_html,
        tabs=tabs_html,
        panes=panes,
        lang_opts=lang_opts,
        src=html.escape(src_name),
    )


TEMPLATE = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Каталог каталогов — Sanskrit Lexicon</title>
<style>
  :root {{
    --bg:#fbfaf7; --fg:#1c1a17; --mut:#6b6357; --line:#e4ded2; --card:#fff;
    --acc:#8a5a2b; --acc-bg:#f3ead c; --live:#1a8a3c; --beta:#b7860b;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#17150f; --fg:#ece7dd; --mut:#9a9081; --line:#2f2a20;
      --card:#201d16; --acc:#d8a366; --acc-bg:#2a2113; --live:#4cc06a; --beta:#e0b74a; }}
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg);
    font:15px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif; }}
  header {{ padding:22px 20px 10px; max-width:1200px; margin:0 auto; }}
  h1 {{ font-size:1.5rem; margin:0 0 4px; }}
  .glance {{ color:var(--mut); font-size:.92rem; margin:0 0 4px; }}
  .note {{ color:var(--mut); font-size:.8rem; }}
  .controls {{ position:sticky; top:0; z-index:5; background:var(--bg);
    padding:10px 20px; border-bottom:1px solid var(--line); }}
  .controls .inner {{ max-width:1200px; margin:0 auto; display:flex;
    flex-wrap:wrap; gap:8px; align-items:center; }}
  input#q {{ flex:1 1 240px; min-width:180px; padding:8px 11px; font-size:.95rem;
    border:1px solid var(--line); border-radius:8px; background:var(--card); color:var(--fg); }}
  select {{ padding:7px 9px; border:1px solid var(--line); border-radius:8px;
    background:var(--card); color:var(--fg); font-size:.85rem; }}
  .tabs {{ display:flex; flex-wrap:wrap; gap:6px; }}
  .tab {{ padding:7px 13px; border:1px solid var(--line); border-radius:20px;
    background:var(--card); color:var(--fg); cursor:pointer; font-size:.85rem; }}
  .tab.active {{ background:var(--acc); color:#fff; border-color:var(--acc); }}
  .cnt {{ opacity:.65; font-size:.78em; }}
  main {{ max-width:1200px; margin:0 auto; padding:14px 20px 60px; }}
  .pane {{ display:none; }}
  .pane.active {{ display:block; }}
  h3.sub {{ font-size:.98rem; color:var(--acc); margin:20px 0 8px;
    border-bottom:1px solid var(--line); padding-bottom:4px; }}
  .tblwrap {{ overflow-x:auto; border:1px solid var(--line); border-radius:8px; margin-bottom:8px; }}
  table {{ border-collapse:collapse; width:100%; font-size:.85rem; }}
  th,td {{ text-align:left; padding:7px 9px; border-bottom:1px solid var(--line);
    vertical-align:top; }}
  th {{ background:var(--acc-bg); color:var(--fg); position:sticky; top:0;
    font-weight:600; white-space:nowrap; }}
  tr:last-child td {{ border-bottom:none; }}
  tr:hover td {{ background:var(--acc-bg); }}
  td code {{ background:var(--acc-bg); padding:1px 4px; border-radius:4px;
    font-size:.9em; word-break:break-word; }}
  a {{ color:var(--acc); }}
  .hidden {{ display:none; }}
  .empty {{ color:var(--mut); padding:20px; }}
  #nores {{ color:var(--mut); padding:24px 0; display:none; }}
  footer {{ max-width:1200px; margin:0 auto; padding:0 20px 40px; color:var(--mut);
    font-size:.8rem; }}
</style>
</head>
<body>
<header>
  <h1>Каталог каталогов</h1>
  <p class="glance">{glance}</p>
  <p class="note">Фильтруемый вид над <code>{src}</code>. Автогенерируется — правьте Markdown-источник, не этот файл.</p>
</header>
<div class="controls"><div class="inner">
  <input id="q" type="search" placeholder="Поиск по всему каталогу…" autocomplete="off">
  <select id="fstatus"><option value="">Статус: все</option><option value="live">🟢 Live</option><option value="beta">🟡 Beta</option></select>
  <select id="ftier"><option value="">Размер: все</option><option value="large">🟢 &gt;10 MB</option><option value="medium">🟡 1–10 MB</option><option value="small">⚪ &lt;1 MB</option></select>
  <select id="flang"><option value="">Язык: все</option>{lang_opts}</select>
  <div class="tabs">{tabs}</div>
</div></div>
<main>
  {panes}
  <p id="nores">Ничего не найдено под текущие фильтры.</p>
</main>
<footer>Sanskrit Lexicon project · сгенерировано из FEATURES_INDEX.md.</footer>
<script>
(function () {{
  var q = document.getElementById('q');
  var fstatus = document.getElementById('fstatus');
  var ftier = document.getElementById('ftier');
  var flang = document.getElementById('flang');
  var tabs = document.querySelectorAll('.tab');
  var panes = document.querySelectorAll('.pane');
  var nores = document.getElementById('nores');
  var cur = 'data';

  function apply() {{
    var term = q.value.trim().toLowerCase();
    var st = fstatus.value, ti = ftier.value, la = flang.value;
    var visible = 0;
    document.querySelectorAll('.pane[data-cat="' + cur + '"] tbody tr').forEach(function (tr) {{
      var ok = true;
      if (term && tr.getAttribute('data-search').indexOf(term) === -1) ok = false;
      if (ok && st && tr.getAttribute('data-status') !== st) ok = false;
      if (ok && ti && tr.getAttribute('data-tier') !== ti) ok = false;
      if (ok && la && tr.getAttribute('data-lang') !== la) ok = false;
      tr.classList.toggle('hidden', !ok);
      if (ok) visible++;
    }});
    // hide subsection blocks that ended up empty
    document.querySelectorAll('.pane[data-cat="' + cur + '"] .tblwrap').forEach(function (w) {{
      var any = w.querySelectorAll('tbody tr:not(.hidden)').length > 0;
      w.classList.toggle('hidden', !any);
      var h = w.previousElementSibling;
      if (h && h.classList.contains('sub')) h.classList.toggle('hidden', !any);
    }});
    nores.style.display = visible ? 'none' : 'block';
  }}

  tabs.forEach(function (t) {{
    t.addEventListener('click', function () {{
      cur = t.getAttribute('data-tab');
      tabs.forEach(function (x) {{ x.classList.remove('active'); }});
      t.classList.add('active');
      panes.forEach(function (p) {{
        p.classList.toggle('active', p.getAttribute('data-cat') === cur);
      }});
      // status/tier/lang only meaningful on some tabs, but harmless elsewhere
      apply();
    }});
  }});
  [q, fstatus, ftier, flang].forEach(function (el) {{
    el.addEventListener('input', apply);
    el.addEventListener('change', apply);
  }});
  apply();
}})();
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", default="FEATURES_INDEX.md")
    ap.add_argument("--out", default="features_index.html")
    args = ap.parse_args()
    with open(args.src, "r", encoding="utf-8") as fh:
        md_text = fh.read()
    glance, sections = parse(md_text)
    out_html = build_html(glance, sections, args.src)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out_html)
    total = sum(len(s["rows"]) for s in sections)
    print(f"Wrote {args.out}: {len(sections)} tables, {total} rows.")


if __name__ == "__main__":
    main()
