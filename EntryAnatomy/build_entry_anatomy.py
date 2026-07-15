#!/usr/bin/env python3
"""Build the Duden-style annotated "how to read an entry" pages for PWG, MW,
and the generic CDSL digital record.

Model: the Duden Deutsches Universalwoerterbuch specimen spread
(SanskritLexicography/papers/duden_deutsches_universalworterbuch-page.pdf):
a re-typeset dictionary column with callout labels wired by leader lines to
highlighted spans of the entry text.

Inputs : csl-orig/v02/pwg/pwg.txt and csl-orig/v02/mw/mw.txt (sibling repo),
         EntryAnatomy/assets/*_crop.jpg facsimile crops (Cologne scan server,
         PWGScan pwg7-1655.pdf / MWScan mw1304-hetumAtratA.pdf).
Outputs: pwg-entry-anatomy.html, mw-entry-anatomy.html,
         cdsl-record-anatomy.html (self-contained, scans embedded as data
         URIs; print CSS sizes one sheet to the content, so headless
         Chrome/Edge --print-to-pdf yields a single-page spread like Duden's).

Usage  : python build_entry_anatomy.py                       # the three H780 pages
         python build_entry_anatomy.py --markup mw kAla      # any-headword specimen
         python build_entry_anatomy.py --image page.pdf --callouts spec.json
         (H870 modes; see --help. One HTML source serves a print-faithful
         single-sheet PDF and a theme-aware interactive web page.)
"""

import argparse
import base64
import datetime
import html
import io
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from indic_transliteration import sanscript

HERE = Path(__file__).resolve().parent
CSL = HERE.parent.parent / "csl-orig" / "v02"
PWG_TXT = CSL / "pwg" / "pwg.txt"
MW_TXT = CSL / "mw" / "mw.txt"

UDATTA = "॑"    # vertical stroke above (padapatha udatta / samhita svarita)
ANUDATTA = "॒"  # horizontal bar below
ACUTE = "́"

# ---------------------------------------------------------------- extraction

def load_records(path):
    """Return {L-number-string: (headerline, body)} for the whole file."""
    recs = {}
    txt = path.read_text(encoding="utf-8")
    for m in re.finditer(r"<L>(\S+?)<pc>(\S+?)\n(.*?)\n?<LEND>", txt, re.S):
        recs[m.group(1)] = (m.group(2), m.group(3))
    return recs


def parse_header(hdr):
    """'358,3<k1>gup<k2>gup<h>1<e>1' -> dict."""
    d = {"pc": hdr.split("<", 1)[0]}
    for tag in ("k1", "k2", "h", "e"):
        m = re.search(rf"<{tag}>([^<]*)", hdr)
        if m:
            d[tag] = m.group(1)
    return d

# ---------------------------------------------------------- transliteration

def slp_dev(slp):
    """SLP1 (with /, \\, ^ accent marks) -> Devanagari with Vedic signs."""
    out = []
    for chunk in re.split(r"([/\\^])", slp):
        if chunk == "/":
            out.append(UDATTA)
        elif chunk == "\\":
            out.append(ANUDATTA)
        elif chunk == "^":
            out.append(UDATTA)
        elif chunk:
            out.append(sanscript.transliterate(chunk, sanscript.SLP1,
                                               sanscript.DEVANAGARI))
    return "".join(out)


def slp_iast(slp):
    """SLP1 -> IAST; '/' becomes a combining acute on the preceding vowel."""
    out = []
    for chunk in re.split(r"([/\\^])", slp):
        if chunk == "/":
            out.append(ACUTE)
        elif chunk in ("\\", "^"):
            pass  # samhita marks are rendered in Devanagari only
        elif chunk:
            out.append(sanscript.transliterate(chunk, sanscript.SLP1,
                                               sanscript.IAST))
    return "".join(out)

# ------------------------------------------------------------- tag renderer

def esc(s):
    return html.escape(s, quote=False)


def render_sa(m):
    slp = m.group(1)
    dev = slp_dev(slp)
    return (f'<span class="sa" data-slp="{html.escape(slp)}" '
            f'title="{html.escape(slp_iast(slp))}">{dev}</span>')


def render_body(body, dic):
    """CDSL markup -> HTML for the typeset column. dic = 'pwg' | 'mw'."""
    s = body

    # digitization artefacts that have no print counterpart
    s = re.sub(r"\[Page[^\]]*\]\s*", "", s)
    s = re.sub(r"<info[^>]*/>", "", s)
    s = s.replace("<srs/>", "")

    # protect < > of real tags while escaping nothing else (input is ASCII-ish)
    s = re.sub(r"\{#(.*?)#\}", render_sa, s)
    s = re.sub(r"\{%(.*?)%\}", r'<span class="gloss">\1</span>', s)

    s = re.sub(r'<ls n="([^"]*)">(.*?)</ls>',
               lambda m: (f'<span class="ls lscont" '
                          f'title="{html.escape(m.group(1) + m.group(2))}">'
                          f"{esc(m.group(2))}</span>"),
               s)
    s = re.sub(r"<ls>(.*?)</ls>", r'<span class="ls">\1</span>', s)
    s = re.sub(r'<ab n="([^"]*)">(.*?)</ab>',
               r'<span class="ab" title="\1">\2</span>', s)
    s = re.sub(r"<ab>(.*?)</ab>", r'<span class="ab">\1</span>', s)
    s = re.sub(r"<lex[^>]*>(.*?)</lex>", r'<span class="lex">\1</span>', s)
    s = re.sub(r"<lang>(.*?)</lang>", r'<span class="lang">\1</span>', s)
    s = re.sub(r"<gk>(.*?)</gk>", r'<span class="gk">\1</span>', s)
    s = re.sub(r'<is n="([^"]*)">(.*?)</is>',
               r'<span class="is" title="\1">\2</span>', s)
    s = re.sub(r"<is>(.*?)</is>", r'<span class="is">\1</span>', s)
    s = re.sub(r"<i>(.*?)</i>", r'<span class="gloss">\1</span>', s)
    s = re.sub(r"<bot>(.*?)</bot>", r'<span class="bot">\1</span>', s)
    s = re.sub(r"<bio>(.*?)</bio>", r'<span class="bot">\1</span>', s)
    s = re.sub(r"<etym>(.*?)</etym>", r'<span class="gloss">\1</span>', s)
    s = re.sub(r"<hom>(.*?)</hom>", r'<span class="hom">\1</span>', s)

    if dic == "mw":
        s = re.sub(r"<s>(.*?)</s>",
                   lambda m: (f'<span class="siast" '
                              f'data-slp="{html.escape(m.group(1))}">'
                              f"{slp_iast(m.group(1))}</span>"),
                   s)
        s = re.sub(r"<s1>(.*?)</s1>",
                   lambda m: f'<span class="s1">{esc(m.group(1))}</span>', s)
        s = re.sub(r"<ns>(.*?)</ns>",
                   lambda m: f'<span class="s1">{esc(m.group(1))}</span>', s)
        s = re.sub(r'<div n="to"/>\s*', "", s)      # verb senses run on inline
        s = re.sub(r'<div n="vp"/>\s*', "", s)
        s = re.sub(r"<cf>(.*?)</cf>", r"\1", s)

    if dic == "pwg":
        # sense subdivisions run on inline in the print; keep their markers
        s = re.sub(r'<div n="[12v]">\s*', "", s)
        s = re.sub(r'<div n="p">\s*', '<span class="pfxmark"></span>', s)
        s = s.replace("〉", ")")  # 1〉 a〉 -> 1) a)
        # sense markers: "1)" "a)" following a dash or start
        s = re.sub(r"(?<![\w])([0-9a-c])\)",
                   r'<span class="sense">\1)</span>', s)
        for con in ("im", "zu", "bei"):
            s = s.replace(f"_{con}_", f' <span class="gloss">{con}</span> ')

    s = s.replace("\n", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def render_headword(hdrd, body, dic):
    """Split '<hom>?{headword}¦ rest' and typeset the headword like print.

    Returns (headword_html, rest_html_source).  The rest is raw markup still
    to be run through render_body.
    """
    hom = ""
    m = re.match(r"\s*<hom>(.*?)</hom>\s*", body)
    if m:
        hom = f'<span class="hom">{m.group(1)}</span> '
        body = body[m.end():]

    if "¦" in body:
        hw_src, rest = body.split("¦", 1)
    else:
        hw_src, rest = "", body

    hw = render_body(hw_src, dic).strip()
    if dic == "mw":
        # main entries (e=1, or hom present) carry Devanagari first, as print
        e = hdrd.get("e", "")
        if e.startswith("1"):
            k2 = hdrd.get("k2", hdrd.get("k1", ""))
            hw = (f'<span class="sa hw-dev">{slp_dev(k2)}</span> {hom}'
                  f'<span class="hw">{hw}</span>')
            hom = ""
        else:
            # roman-only subordinate headwords are capitalized in the print,
            # but run-on compounds (e=3) stay lowercase
            if not e.startswith("3"):
                hw = cap_first_iast(hw)
            hw = f'{hom}<span class="hw">{hw}</span>'
            hom = ""
    else:
        hw = f"{hom}<span " f'class="hw">{hw}</span>'
        hom = ""
    return hw, rest


def cap_first_iast(html_frag):
    """Capitalize the first letter inside the first siast span (MW print)."""
    return re.sub(r'(<span class="siast"[^>]*>)([a-zĀ-ſ])',
                  lambda m: m.group(1) + m.group(2).upper(), html_frag, count=1)

# ------------------------------------------------------------ MW paragraphs

def mw_paragraph(recs, lnums, drop_stem=None):
    """Join MW records into one print paragraph.

    Continuation records (body starting with ¦, or repeating the same <s>)
    join with '; ' exactly as the 1899 print runs them on; e3 compound
    records join with an em-dash and elide the repeated first member.
    """
    parts = []
    prev_k1 = None
    for L in lnums:
        hdr, body = recs[L]
        d = parse_header(hdr)
        e = d.get("e", "")
        starts_bare = body.lstrip().startswith("¦")
        same_stem = d.get("k1") == prev_k1
        if starts_bare or (same_stem and parts):
            rest = body.split("¦", 1)[1] if "¦" in body else body
            parts.append("; " + render_body(rest, "mw"))
        else:
            hw, rest = render_headword(d, body, "mw")
            if e.startswith("3") and drop_stem:
                hw = re.sub(
                    r'(<span class="siast"[^>]*>)' + re.escape(drop_stem) + "—",
                    r"\1—", hw)
                parts.append(' <span class="cpd">' + hw.replace(
                    '<span class="hw">', '<span class="hw cpdhw">') + "</span> "
                    + render_body(rest, "mw"))
            else:
                sep = " " if parts else ""
                parts.append(sep + hw + " " + render_body(rest, "mw"))
        prev_k1 = d.get("k1")
    return '<p class="entry">' + "".join(parts) + "</p>"


def pwg_paragraph(recs, L):
    hdr, body = recs[L]
    d = parse_header(hdr)
    hw, rest = render_headword(d, body, "pwg")
    return f'<p class="entry" data-l="{L}">{hw} {render_body(rest, "pwg")}</p>'

# ----------------------------------------------------------- callout engine

PAGE_CSS = """
:root { --hl:#cdeaf6; --line:#333; --lab:#005a87; }
* { box-sizing: border-box; }
body { margin:0; background:#f4f1ea; font-family: Georgia, 'Times New Roman', serif;
       color:#1a1a1a; }
.sheet { position:relative; width:1720px; margin:0 auto; background:#fbf9f4;
         padding:34px 30px 30px; }
header { border-bottom:2.5px solid #005a87; padding-bottom:10px; margin-bottom:6px; }
header h1 { font:700 25px/1.2 'Segoe UI', Arial, sans-serif; margin:0; color:#00344e; }
header p.sub { font:13px/1.45 'Segoe UI', Arial, sans-serif; color:#444; margin:6px 0 0;
               max-width:1100px; }
.board { position:relative; display:grid;
         grid-template-columns:300px 452px 452px 300px; column-gap:38px;
         padding-top:18px; }
.colwrap { position:relative; z-index:2; }
.colcap { font:600 10.5px/1.3 'Segoe UI', Arial, sans-serif; color:#666;
          letter-spacing:.06em; text-transform:uppercase; border-bottom:1px solid #bbb;
          margin-bottom:7px; padding-bottom:3px; }
.entry { font-size:13.6px; line-height:1.5; text-align:justify; margin:0 0 2px;
         padding-left:14px; text-indent:-14px; hyphens:manual; }
.sa { font-family:'Sanskrit Text','Adobe Devanagari','Nirmala UI',serif;
      font-size:1.12em; }
.hw { font-weight:bold; }
.hw .sa, .hw-dev { font-weight:bold; }
.siast { font-style:italic; }
.hw .siast, .cpdhw .siast { font-weight:bold; font-style:normal; }
.gloss { font-style:italic; }
.bot { font-style:italic; }
.hom { font-weight:bold; }
.sense { font-weight:bold; }
.lex, .ab { }
.ls, .lscont { font-variant:small-caps; letter-spacing:.02em; }
.is { letter-spacing:.13em; }
.s1 { }
.lang { font-style:italic; }
.gk { font-family:'Palatino Linotype', Georgia, serif; }
.more { color:#777; font-style:italic; font-size:12.5px; margin:6px 0 0; }
.callout { position:absolute; width:288px; font:11.5px/1.38 'Segoe UI', Arial, sans-serif;
           color:var(--lab); z-index:3; }
.callout b { color:#00344e; }
.callout.right { text-align:left; }
.callout.left { text-align:right; }
.hl { background:var(--hl); box-decoration-break:clone; -webkit-box-decoration-break:clone; }
svg.leaders { position:absolute; inset:0; width:100%; height:100%; z-index:1;
              pointer-events:none; }
svg.leaders path { stroke:var(--line); stroke-width:.8; fill:none; }
.bottomrow { display:flex; gap:36px; margin-top:26px; align-items:flex-start; }
.facsimile { width:520px; flex:none; }
.facsimile img { width:100%; border:1px solid #b9b2a4; box-shadow:2px 3px 8px rgba(0,0,0,.18); }
.facsimile .cap, .aboutbox { font:11.5px/1.5 'Segoe UI', Arial, sans-serif; color:#333; }
.facsimile .cap { margin-top:6px; }
.aboutbox { background:#e9f4fa; border-left:3px solid #005a87; padding:12px 16px;
            max-width:640px; }
.aboutbox h2 { font:700 13px/1.2 'Segoe UI', Arial, sans-serif; margin:0 0 6px;
               color:#00344e; }
footer { margin-top:22px; border-top:1px solid #bbb; padding-top:7px;
         font:10.5px/1.5 'Segoe UI', Arial, sans-serif; color:#666; }
a { color:#005a87; }
@media print { body { background:#fbf9f4; } .sheet { margin:0; } }
"""

CALLOUT_JS = """
function layout() {
  const board = document.querySelector('.board');
  const svg = document.querySelector('svg.leaders');
  svg.innerHTML = '';
  const brect = board.getBoundingClientRect();
  const sides = {left: [], right: []};
  document.querySelectorAll('.callout').forEach(c => {
    const sel = c.dataset.target, nth = +(c.dataset.nth || 0);
    const els = document.querySelectorAll(sel);
    const el = els[Math.min(nth, els.length - 1)];
    if (!el) { c.style.display = 'none'; return; }
    el.classList.add('hl');
    const r = el.getBoundingClientRect();
    c.tY = r.top - brect.top + r.height / 2;
    c.tXl = r.left - brect.left; c.tXr = r.right - brect.left;
    sides[c.classList.contains('left') ? 'left' : 'right'].push(c);
  });
  const bw = board.clientWidth;
  for (const side of ['left', 'right']) {
    const list = sides[side].sort((a, b) => a.tY - b.tY);
    let cursor = 0;
    for (const c of list) {
      c.style.top = '0px'; c.style[side] = '0px';
      let y = Math.max(c.tY - c.offsetHeight / 2, cursor);
      c.style.top = y + 'px';
      cursor = y + c.offsetHeight + 10;
      const cy = y + c.offsetHeight / 2;
      const gut = c.offsetWidth + 4;
      const x0 = side === 'left' ? gut : bw - gut;
      const stub = side === 'left' ? x0 + 14 : x0 - 14;
      const x1 = side === 'left' ? c.tXl - 3 : c.tXr + 3;
      const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      p.setAttribute('d', `M ${x0} ${cy} L ${stub} ${cy} L ${x1} ${c.tY}`);
      c._p = p;
      svg.appendChild(p);
    }
  }
  const sheet = document.querySelector('.sheet');
  const need = Math.max(...[...document.querySelectorAll('.callout')]
      .map(c => c.offsetTop + c.offsetHeight + 40), board.offsetHeight + 30);
  board.style.minHeight = need + 'px';
  const h = Math.max(sheet.offsetHeight,
                     document.documentElement.scrollHeight) + 10;
  const st = document.getElementById('pagesize') ||
      Object.assign(document.createElement('style'), {id: 'pagesize'});
  st.textContent = `@page { size: ${sheet.offsetWidth}px ${h}px; margin: 0; }`;
  document.head.appendChild(st);
}
function run() {
  document.querySelectorAll('.hl').forEach(e => e.classList.remove('hl'));
  layout();
  setTimeout(layout, 350);  // second pass once metrics are stable
}
if (document.fonts && document.fonts.ready)
  document.fonts.ready.then(() => setTimeout(run, 60));
else window.addEventListener('load', () => setTimeout(run, 120));
"""


def data_uri(png_path, quality=82, max_w=1200):
    from PIL import Image
    src = (io.BytesIO(png_path) if isinstance(png_path, (bytes, bytearray))
           else png_path)
    img = Image.open(src).convert("RGB")
    if img.width > max_w:
        img = img.resize((max_w, int(img.height * max_w / img.width)),
                         Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=quality)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def callout_html(side, target, nth, text):
    return (f'<div class="callout {side}" data-target="{html.escape(target)}" '
            f'data-nth="{nth}">{text}</div>')


def wrap_once(hay, needle, cls, ident=None):
    """Wrap the first literal occurrence of plain text `needle` in a span."""
    i = hay.find(needle)
    if i < 0:
        print(f"  !! anchor not found: {needle[:50]!r}")
        return hay
    idattr = f' id="{ident}"' if ident else ""
    return (hay[:i] + f'<span class="mark {cls}"{idattr}>' + needle +
            "</span>" + hay[i + len(needle):])


def page(title, subtitle, columns, callouts, facs_uri, facs_cap, about, foot):
    cols = "".join(
        f'<div class="colwrap"><div class="colcap">{cap}</div>{body}</div>'
        for cap, body in columns)
    cos = "".join(callout_html(*c) for c in callouts)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>{PAGE_CSS}</style></head>
<body><div class="sheet">
<header><h1>{html.escape(title)}</h1><p class="sub">{subtitle}</p></header>
<div class="board">
<svg class="leaders"></svg>
<div></div>{cols}<div></div>
{cos}
</div>
<div class="bottomrow">
<div class="facsimile"><img src="{facs_uri}" alt="facsimile"><div class="cap">{facs_cap}</div></div>
<div class="aboutbox">{about}</div>
</div>
<footer>{foot}</footer>
</div>
<script>{CALLOUT_JS}</script>
</body></html>"""


FOOT = ("Typeset from the Cologne Digital Sanskrit Dictionaries source "
        "(csl-orig v02) &middot; facsimiles: Cologne scan server &middot; "
        "built by build_entry_anatomy.py &middot; "
        "Fable 5 (claude-fable-5), 12-07-2026 &middot; "
        "Cologne Sanskrit-Lexicon: "
        '<a href="https://www.sanskrit-lexicon.uni-koeln.de/">'
        "sanskrit-lexicon.uni-koeln.de</a>")


# ================================================================= PWG page

def build_pwg(pwg):
    col_a = "".join(pwg_paragraph(pwg, L) for L in
                    ["117557", "117558", "117559", "117560",
                     "117561", "117562", "117563"])
    col_b = pwg_paragraph(pwg, "25758")

    # plain-text anchors wrapped after rendering (unique substrings)
    col_a = wrap_once(col_a, "(von <span class=\"hom\">1.</span>", "etym")
    col_a = wrap_once(col_a, "nach <span class=\"ls\">SĀY.</span>", "dissent")
    col_a = wrap_once(col_a, "ed. Calc.", "varlect")
    col_a = wrap_once(col_a, "nur <span class=\"ab\">loc.</span>", "restrict")
    col_b = wrap_once(col_b, "so <span class=\"ab\">v. a.</span>", "sova")
    col_b = wrap_once(col_b, "<span class=\"ab\">v. l.</span>", "varlectb")
    col_b = wrap_once(col_b, "<span class=\"ab\">med.</span>", "medlbl")

    L = "left"
    R = "right"
    callouts = [
        (L, ".colwrap:nth-of-type(2) .hom", 0,
         "<b>Homograph numbers</b> distinguish identically spelt but "
         "etymologically distinct words — four different <i>heman</i> "
         "follow one another"),
        (L, ".colwrap:nth-of-type(2) .hw .sa", 0,
         "<b>Headword in Devanāgarī</b>, exactly as printed — no "
         "transliteration is given in PWG (here <i>hemán</i> ‘impulse’)"),
        (L, ".mark.etym", 0,
         "<b>Etymology in parentheses</b>: derived from homograph 1 of the "
         "root <i>hi</i> ‘to impel’"),
        (L, ".colwrap:nth-of-type(2) .lex", 0,
         "<b>Grammatical gender</b> (m. = masculine; the following homographs "
         "show n. and adj.)"),
        (L, ".colwrap:nth-of-type(2) .gloss", 0,
         "<b>German gloss in italics</b> — PWG defines in German "
         "(<i>Antrieb</i> ‘impulse’)"),
        (L, ".colwrap:nth-of-type(2) .entry:nth-of-type(1) .sa", 1,
         "<b>Vedic saṃhitā quotation with tonal accents</b>: anudātta bar "
         "below, svarita stroke above the syllable — reproduced from the "
         "accented Ṛgveda text"),
        (L, ".colwrap:nth-of-type(2) .entry:nth-of-type(1) .ls", 1,
         "<b>Citation with exact locus</b>: ṚV. 9,97,1 = Ṛgveda, maṇḍala 9, "
         "hymn 97, verse 1 — every sense is documented from the literature"),
        (L, ".mark.dissent", 0,
         "<b>Commentators’ dissent recorded</b>: Sāyaṇa glosses the word as "
         "‘gold’ in this passage"),
        (L, ".colwrap:nth-of-type(2) .entry:nth-of-type(2) .sense", 0,
         "<b>Sense numbering</b> 1) 2) 3) 4) inside one homograph"),
        (L, ".mark.varlect", 0,
         "<b>Variant reading</b> from a specific edition (the Calcutta "
         "edition of the Mahābhārata)"),
        (L, ".colwrap:nth-of-type(2) .entry:nth-of-type(2) .lscont", 0,
         "<b>Run-on citations</b>: the repeated source is abbreviated away — "
         "‘1,81’ silently continues HALĀY."),
        (L, ".colwrap:nth-of-type(2) .entry:nth-of-type(3) .hw .sa", 0,
         "<b>Accent distinguishes homographs</b>: <i>hé-man</i> ‘winter’ "
         "(udātta on the first syllable) vs. <i>hemán</i> above — the stroke "
         "position is lexically significant"),
        (L, ".mark.restrict", 0,
         "<b>Usage restriction</b>: attested only in the locative case "
         "(‘in winter’)"),
        (L, ".colwrap:nth-of-type(2) .entry:nth-of-type(5) .is", 0,
         "<b>Indian grammatical apparatus</b>: membership in a gaṇa "
         "(Pāṇini’s word-lists) is part of the lexical record"),
        (L, ".colwrap:nth-of-type(2) .entry:nth-of-type(6) .hw", 0,
         "<b>Compounds follow as separate entries</b>: "
         "<i>hema-nābhi</i> ‘gold-nave’, with a full quotation showing the "
         "word in context"),
        (L, ".colwrap:nth-of-type(2) .entry:nth-of-type(7) .ab", 0,
         "<b>N. pr.</b> = nomen proprium; a Yakṣa named ‘Gold-Eye’ — proper "
         "names are glossed etymologically in parentheses"),
    ]
    callouts += [
        (R, ".colwrap:nth-of-type(3) .entry .hw", 0,
         "<b>√ marks a verbal root</b> — the root article is the anchor of "
         "the verbal system (√<i>cumb</i> ‘to kiss’)"),
        (R, ".colwrap:nth-of-type(3) .sa", 1,
         "<b>Present stem with accent</b> (<i>cúmbati</i>) given right after "
         "the root — the udātta stroke marks the tone"),
        (R, ".colwrap:nth-of-type(3) .ls", 0,
         "<b>Dhātupāṭha reference</b> (11,39): the Indian root-list defines "
         "class and meaning; Western and Indian lexicography meet here"),
        (R, ".colwrap:nth-of-type(3) .sa", 2,
         "<b>Poetic examples quoted in full</b>: ‘(he) kissed her softly on "
         "the cheek’ (Harivaṃśa 8745)"),
        (R, ".mark.medlbl", 0,
         "<b>Voice and derived-stem labels</b>: med. = middle voice, caus. = "
         "causative (‘to let kiss’), each with its own attestations"),
        (R, ".mark.sova", 0,
         "<b>so v. a.</b> (‘so viel als’) introduces an extended meaning: "
         "‘to touch with the mouth’ — of two conches blown like a kiss"),
        (R, ".mark.varlectb", 0,
         "<b>v. l.</b> = varia lectio, a variant reading in the Dhātupāṭha "
         "tradition itself"),
        (R, '.colwrap:nth-of-type(3) .sa[data-slp="pari"]', 0,
         "<b>Prefixed verbs nest inside the root article</b>: — <i>pari</i> "
         "‘to kiss all over’ (a bee kissing the mango blossom), then — "
         "<i>vi</i>; the dash repeats the root"),
    ]

    facs_cap = ("<b>The same entries in the 1875 print</b>: Böhtlingk &amp; "
                "Roth, <i>Sanskrit-Wörterbuch</i>, vol. 7, col. 1655 "
                "(St. Petersburg Academy edition) — the four <i>heman</i> "
                "homographs with accented Devanāgarī headwords. Scan: Cologne "
                "Sanskrit-Lexicon.")
    about = ("<h2>How to use this page</h2>"
             "The column re-typesets entries from the digital PWG text "
             "(Cologne, csl-orig v02) in the layout of the printed original; "
             "each label explains one element of the entry architecture. "
             "PWG (the ‘large Petersburg dictionary’, 1855–1875, 7 vols.) is "
             "the foundational dictionary of Western Sanskrit philology: "
             "German definitions, Devanāgarī lemmata, exhaustive citations "
             "with exact loci, and the Indian grammatical tradition "
             "(Dhātupāṭha, gaṇas, commentators) built into every article. "
             "Column captions give the print locus (volume–column) encoded "
             "as <code>&lt;pc&gt;</code> in the digital record.")
    sub = ("A specimen page after the model of Duden’s "
           "<i>Deutsches Universalwörterbuch</i> entry-anatomy spread: real "
           "entries, re-typeset from the Cologne digital text, with every "
           "microstructural element labelled. Entries: the four homographs "
           "of <i>heman</i> (with derivatives) and the root √<i>cumb</i>.")
    return page(
        "How to read an entry — Böhtlingk & Roth, Sanskrit-Wörterbuch "
        "(PWG, 1855–1875)",
        sub,
        [("PWG · Vol. 7, col. 1655", col_a),
         ("PWG · Vol. 2, col. 1044", col_b)],
        callouts,
        data_uri(HERE / "assets" / "pwg_heman_crop.jpg"),
        facs_cap, about, FOOT)


# ================================================================== MW page

def build_mw(mw):
    col_a = (
        mw_paragraph(mw, ["264069", "264070"])
        + mw_paragraph(mw, ["264077"])
        + mw_paragraph(mw, ["264121", "264122", "264123", "264124", "264125"])
        + mw_paragraph(mw, ["264126", "264127", "264128", "264129", "264130",
                            "264131", "264132", "264133", "264134", "264135",
                            "264136", "264137", "264138", "264139"],
                       drop_stem="hema")
        + '<p class="more">⋯ the compound run continues for another four '
          "columns of the print (<i>hema-kalaśa</i> … <i>hema-hasti-ratha</i>)"
          "</p>")
    col_b = (mw_paragraph(mw, ["65898"])
             + mw_paragraph(mw, ["65899"])
             + mw_paragraph(mw, ["65900", "65901"])
             + mw_paragraph(mw, ["65902"])
             + mw_paragraph(mw, ["65903"])
             + mw_paragraph(mw, ["65904", "65905", "65906"]))

    col_a = wrap_once(col_a, "(of doubtful derivation)", "doubt")
    col_a = wrap_once(col_a, "in <span class=\"ab\">comp.</span> for", "compstub")
    col_a = wrap_once(col_a, "&amp;c.", "etc") if "&amp;c." in col_a else \
        wrap_once(col_a, "&c.", "etc")
    col_b = wrap_once(col_b, "<span class=\"ab\">cl.</span>", "cl")
    col_b = wrap_once(col_b, "<span class=\"ab\">Desid.</span>", "desid")
    col_b = wrap_once(col_b, "‘defending, protecting’", "litquote")

    L, R = "left", "right"
    callouts = [
        (L, ".colwrap:nth-of-type(2) .entry:nth-of-type(1) .hw", 0,
         "<b>Subordinate headword in roman only</b> — rarer words get no "
         "Devanāgarī in the 1899 print; the acute accent marks the Vedic "
         "udātta (<i>hemán</i>)"),
        (L, ".colwrap:nth-of-type(2) .entry:nth-of-type(1) .ls", 0,
         "<b>Citation by work + locus</b>, more compressed than PWG: "
         "RV. ix, 97, 1 — roman numerals for the book"),
        (L, ".colwrap:nth-of-type(2) .entry:nth-of-type(1) .ls", 1,
         "<b>Commentator in parentheses</b>: Sāyaṇa’s divergent gloss "
         "‘gold’ noted inline"),
        (L, ".colwrap:nth-of-type(2) .entry:nth-of-type(2) .hw-dev", 0,
         "<b>Main headword: Devanāgarī + bold transliteration</b> — the "
         "print’s two-script convention; homograph number between them"),
        (L, ".colwrap:nth-of-type(2) .entry:nth-of-type(2) .hw .siast", 0,
         "<b>Accent position differs</b>: <i>héman</i> ‘winter’ vs. "
         "<i>hemán</i> ‘impulse’ — as in PWG, tone tells homographs apart"),
        (L, ".mark.doubt", 0,
         "<b>Etymological judgment stated openly</b> — ‘of doubtful "
         "derivation’; MW flags what it cannot derive"),
        (L, ".mark.etc", 0,
         "<b>&amp;c. after citations</b> = attested widely from that point "
         "on; MW compresses where PWG enumerates"),
        (L, ".colwrap:nth-of-type(2) .bot", 0,
         "<b>Botanical identification in Linnaean binomials</b> — plant "
         "names are identified, not just translated (Mesua Roxburghii)"),
        (L, ".mark.compstub", 0,
         "<b>Compound stub</b>: <i>hema</i> ‘in comp. for 3. heman’ opens "
         "the compound run — homograph number carried along"),
        (L, ".colwrap:nth-of-type(2) .cpd .cpdhw", 0,
         "<b>Compounds run on inside one paragraph</b>: the dash replaces "
         "the first member (— <i>kakṣa</i> = <i>hema-kakṣa</i>) — hundreds "
         "of compounds per column this way"),
        (L, ".colwrap:nth-of-type(2) .ab[title='golden']", 0,
         "<b>g˚ = ‘golden’</b>: even the recurring gloss word is abbreviated "
         "to its initial inside the compound run"),
        (L, ".colwrap:nth-of-type(2) .lex", 4,
         "<b>mf(ā)n.</b> = adjective of three genders, feminine stem in -ā "
         "— the parenthesis gives the feminine formation"),
    ]
    callouts += [
        (R, ".colwrap:nth-of-type(3) .entry:nth-of-type(1) .hw-dev", 0,
         "<b>Roots as headwords</b>: three homograph roots <i>gup</i> — "
         "same lemma family as PWG’s treatment, one column to compare"),
        (R, ".mark.cl", 0,
         "<b>cl. 4. P.</b> = present class 4, parasmaipada — Whitney-style "
         "verb classification up front"),
        (R, '.colwrap:nth-of-type(3) .siast[data-slp="˚pyati"]', 0,
         "<b>˚ elides the repeated stem</b>: ˚<i>pyati</i> = <i>gupyati</i>"),
        (R, ".colwrap:nth-of-type(3) .lang", 0,
         "<b>Prākṛt evidence cited</b> inside a Sanskrit entry — "
         "Middle-Indic forms in italics with their source"),
        (R, ".colwrap:nth-of-type(3) .entry:nth-of-type(2) .ab", 1,
         "<b>Principal parts listed with grammarians’ references</b>: perf. "
         "<i>jugopa</i>, fut. <i>gopsyati</i>, aor. <i>agaupsīt</i> — each "
         "form documented from Pāṇini or the literature"),
        (R, ".mark.desid", 0,
         "<b>Derived stems get their own sense blocks</b>: the desiderative "
         "<i>jugupsate</i> ‘to shun, detest’ — semantically emancipated "
         "from ‘guard’"),
        (R, ".mark.litquote", 0,
         "<b>Literal meaning in quotation marks</b> before the "
         "lexicalised use — ifc. (‘at the end of a compound’)"),
        (R, ".colwrap:nth-of-type(3) .entry:nth-of-type(4) .hw .siast", 0,
         "<b>Accented participle</b> <i>gupitá</i> — Vedic forms keep their "
         "udātta even as subordinate headwords"),
        (R, ".colwrap:nth-of-type(3) .entry:nth-of-type(6) .hw .siast", 0,
         "<b>One entry, several senses joined by semicolons</b> — in the "
         "digital text these are separate records; the print runs them on "
         "(<i>guptá</i> ‘protected; hidden; kept secret’)"),
    ]

    facs_cap = ("<b>The same entries in the 1899 print</b>: Monier-Williams, "
                "<i>A Sanskrit-English Dictionary</i>, new ed., p. 1304, "
                "col. 2 — ‘3. heman’ with Devanāgarī headword and the "
                "beginning of the compound run. Scan: Cologne "
                "Sanskrit-Lexicon.")
    about = ("<h2>How to use this page</h2>"
             "The column re-typesets entries from the digital MW text "
             "(Cologne, csl-orig v02) following the 1899 print conventions; "
             "each label explains one element. Monier-Williams (1899) is the "
             "standard English-language Sanskrit dictionary: two-script "
             "headwords, etymological grouping, compressed citations, and "
             "very long compound runs. The lemma family (<i>heman</i>, "
             "<i>gup</i>) is the same as on the PWG specimen page — compare "
             "how the two traditions treat identical material. MW’s own "
             "transliteration (kaksha, ṛi) is modernised to IAST here; the "
             "facsimile shows the original.")
    sub = ("A specimen page after the model of Duden’s "
           "<i>Deutsches Universalwörterbuch</i> entry-anatomy spread: real "
           "entries re-typeset from the Cologne digital text, every "
           "microstructural element labelled. Entries: the three homographs "
           "of <i>heman</i> with the <i>hema-</i> compound run, and the "
           "three homograph roots <i>gup</i> with participles.")
    return page(
        "How to read an entry — Monier-Williams, A Sanskrit-English "
        "Dictionary (MW, 1899)",
        sub,
        [("MW · p. 1304, col. 1–2", col_a),
         ("MW · p. 358, col. 3 – p. 359, col. 1", col_b)],
        callouts,
        data_uri(HERE / "assets" / "mw_heman_crop.jpg"),
        facs_cap, about, FOOT)


# ============================================================= generic page

GENERIC_EXTRA_CSS = """
.board.generic { grid-template-columns:330px 960px 330px; }
pre.raw { background:#20242a; color:#d8dce2; border-radius:6px; padding:14px 16px;
          font:12.5px/1.75 Consolas, 'Cascadia Mono', monospace; white-space:pre-wrap;
          word-break:break-all; margin:0 0 10px; }
pre.raw .tag { color:#6fb3e0; }
pre.raw .rawsa { color:#e6c07b; }
pre.raw .rawgl { color:#98c379; font-style:italic; }
pre.raw .pipe { color:#e06c75; font-weight:bold; }
pre.raw .acc { color:#e06c75; font-weight:bold; }
.rendered { border:1px solid #c9c2b4; background:#fff; border-radius:6px;
            padding:10px 14px 8px; margin:0 0 26px; }
.rendered .rlabel { font:600 10px/1 'Segoe UI', Arial, sans-serif; color:#888;
                    text-transform:uppercase; letter-spacing:.08em; margin-bottom:6px; }
.exh2 { font:700 15px/1.3 'Segoe UI', Arial, sans-serif; color:#00344e;
        margin:0 0 8px; }
table.slp { border-collapse:collapse; font:12px/1.5 'Segoe UI', Arial, sans-serif;
            margin-top:4px; }
table.slp td, table.slp th { border:1px solid #ccc; padding:2px 9px; text-align:center; }
table.slp th { background:#e9f4fa; }
"""


def raw_highlight(rec_text):
    s = html.escape(rec_text, quote=False)
    s = re.sub(r"&lt;(/?)([A-Za-z0-9]+)((?:(?!&gt;).)*)&gt;",
               lambda m: (f'<span class="tag tag-{m.group(2)}">&lt;'
                          f"{m.group(1)}{m.group(2)}{m.group(3)}&gt;</span>"),
               s)
    s = re.sub(r"\{#(.*?)#\}",
               lambda m: ('<span class="rawsa">{#' +
                          re.sub(r"([/\\\\^])", r'<span class="acc">\1</span>',
                                 m.group(1)) + "#}</span>"), s)
    s = re.sub(r"\{%(.*?)%\}", r'<span class="rawgl">{%\1%}</span>', s)
    s = s.replace("¦", '<span class="pipe">¦</span>')
    return s


def build_generic(pwg, mw):
    def raw_of(recs, L):
        hdr, body = recs[L]
        return f"<L>{L}<pc>{hdr}\n{body}\n<LEND>"

    ex1_raw = raw_highlight(raw_of(pwg, "117557"))
    ex2_raw = raw_highlight(raw_of(mw, "65898"))
    ex3_raw = raw_highlight(raw_of(mw, "264121") + "\n" +
                            raw_of(mw, "264122"))

    ex1_rend = pwg_paragraph(pwg, "117557")
    ex2_rend = mw_paragraph(mw, ["65898"])
    ex3_rend = mw_paragraph(mw, ["264121", "264122"])

    slp_table = ("<table class='slp'><tr><th>SLP1</th>"
                 "<td>A</td><td>I</td><td>U</td><td>f</td><td>F</td>"
                 "<td>x</td><td>E</td><td>O</td><td>M</td><td>H</td>"
                 "<td>N</td><td>Y</td><td>w</td><td>q</td><td>R</td>"
                 "<td>T</td><td>D</td><td>S</td><td>z</td><td>G</td></tr>"
                 "<tr><th>IAST</th>"
                 "<td>ā</td><td>ī</td><td>ū</td><td>ṛ</td><td>ṝ</td>"
                 "<td>ḷ</td><td>ai</td><td>au</td><td>ṃ</td><td>ḥ</td>"
                 "<td>ṅ</td><td>ñ</td><td>ṭ</td><td>ḍ</td><td>ṇ</td>"
                 "<td>th</td><td>dh</td><td>ś</td><td>ṣ</td><td>gh</td></tr>"
                 "</table>")

    centre = (
        '<div class="exh ex1"><div class="exh2">Exhibit 1 — a PWG record '
        "(hemán ‘impulse’)</div>"
        f'<pre class="raw">{ex1_raw}</pre>'
        '<div class="rendered"><div class="rlabel">renders as</div>'
        f"{ex1_rend}</div></div>"
        '<div class="exh ex2"><div class="exh2">Exhibit 2 — an MW record '
        "(root 1. gup) with its machine layer</div>"
        f'<pre class="raw">{ex2_raw}</pre>'
        '<div class="rendered"><div class="rlabel">renders as</div>'
        f"{ex2_rend}</div></div>"
        '<div class="exh ex3"><div class="exh2">Exhibit 3 — one printed '
        "entry, several records (MW 3. heman)</div>"
        f'<pre class="raw">{ex3_raw}</pre>'
        '<div class="rendered"><div class="rlabel">renders as</div>'
        f"{ex3_rend}</div>"
        "<div class='exh2' style='margin-top:18px'>The SLP1 ASCII "
        "transliteration (non-trivial mappings)</div>" + slp_table + "</div>")

    L, R = "left", "right"
    callouts = [
        (L, ".ex1 .tag-L", 0,
         "<b>&lt;L&gt; record number</b> — the stable unique id of the "
         "record in the Cologne digitization (not in the print)"),
        (L, ".ex1 .tag-pc", 0,
         "<b>&lt;pc&gt; print locus</b>: volume–column for PWG (7-1655), "
         "page,column for MW — the bridge back to the scan"),
        (L, ".ex1 .tag-k1", 0,
         "<b>&lt;k1&gt; = key1</b>, the normalized lookup key in SLP1: no "
         "accents, no compound marks — use it for matching, dedup, joins"),
        (L, ".ex1 .tag-k2", 0,
         "<b>&lt;k2&gt; = key2</b>, closer to the printed form: keeps the "
         "udātta accent (hema/n) and, in MW, compound dashes "
         "(hema—kakza) — use it for citation and editorial review"),
        (L, ".ex1 .tag-h", 0,
         "<b>&lt;h&gt; homograph number</b> in the key line; "
         "&lt;hom&gt; in the body is its printed counterpart"),
        (L, ".ex1 .rawsa", 0,
         "<b>{#…#} Sanskrit text in SLP1</b> — a strict one-character-"
         "per-phoneme ASCII encoding; rendered to Devanāgarī or IAST "
         "(table below)"),
        (L, ".ex1 .acc", 0,
         "<b>Accent characters</b>: / = udātta; in saṃhitā quotations "
         "\\ and ^ mark the anudātta bar and svarita stroke of the print"),
        (L, ".ex1 .rawgl", 0,
         "<b>{%…%} italics of the print</b> — in PWG that is the German "
         "definition text"),
        (L, ".ex1 .pipe", 0,
         "<b>¦ headword/body divider</b> — everything before it is the "
         "lemma as printed, everything after is the article"),
        (L, ".ex1 .tag-ls", 0,
         "<b>&lt;ls&gt; literature source</b>; when the source repeats, "
         "&lt;ls n=\"…\"&gt; carries the silently-omitted part, so "
         "‘9,97,1’ expands back to the full reference"),
    ]
    callouts += [
        (R, ".ex2 .tag-e", 0,
         "<b>&lt;e&gt; typographic level</b> of the headword in the 1899 "
         "MW print: 1 = main entry with Devanāgarī, 2 = subordinate "
         "roman-only entry, 3 = run-on compound; a letter suffix (1A, 2B) "
         "= continuation segment of the same entry"),
        (R, ".ex2 .tag-ab", 0,
         "<b>&lt;ab&gt; abbreviation</b> (cl., P., Ā., mfn., ifc. …); "
         "&lt;lex&gt; carries the gender/part-of-speech label"),
        (R, ".ex2 .tag-lang", 0,
         "<b>&lt;lang&gt; language label</b> — here flagging a Prākṛt "
         "form inside the Sanskrit entry"),
        (R, ".ex2 .tag-info", 0,
         "<b>&lt;info&gt; machine layer</b> — modern enrichment absent "
         "from the print: parsed gender sets, Whitney-roots and "
         "Westergaard cross-links, verb class/pada codes. Consume these "
         "before re-deriving anything"),
        (R, ".ex2 .tag-LEND", 0,
         "<b>&lt;LEND&gt; record terminator</b> — records are a flat "
         "streamable sequence, one headword segment each"),
        (R, ".ex3 .tag-L", 1,
         "<b>One printed entry ≠ one record</b>: each sense block of MW’s "
         "‘3. heman’ is its own record; the ¦-initial body and the "
         "&lt;e&gt; letter suffix (1A) mark the continuation — join on "
         "k1 + adjacency to rebuild the printed paragraph"),
        (R, ".ex3 .rendered .entry", 0,
         "<b>Round-trip check</b>: the two records above reassemble into "
         "the single print paragraph, senses joined by semicolons"),
    ]

    facs_cap = ("<b>Where the records come from</b>: Monier-Williams 1899, "
                "p. 1304 — the ‘3. heman’ entry of Exhibit 3 as printed. "
                "Scan: Cologne Sanskrit-Lexicon.")
    about = ("<h2>The Cologne record model</h2>"
             "All ~40 dictionaries of the Cologne Digital Sanskrit "
             "Dictionaries (CDSL) share this markup: a flat sequence of "
             "&lt;L&gt;…&lt;LEND&gt; records, headword keys in SLP1, "
             "print-faithful body markup, and a growing machine layer. "
             "The same tag inventory you see here reads PWG (German, "
             "1855–75) and MW (English, 1899) alike — which is what makes "
             "cross-dictionary tooling possible. Canonical sources: "
             '<a href="https://github.com/sanskrit-lexicon/csl-orig">'
             "sanskrit-lexicon/csl-orig</a> (this text), "
             '<a href="https://www.sanskrit-lexicon.uni-koeln.de/">'
             "the Cologne portal</a> (lookup + scans).")
    sub = ("The companion page to the PWG and MW specimen pages: what the "
           "<i>digital</i> record looks like underneath. Three real records "
           "shown raw and rendered, every markup element labelled.")

    body_page = page(
        "Anatomy of a CDSL record — the Cologne digital markup",
        sub,
        [("csl-orig · v02 · pwg.txt + mw.txt", centre)],
        callouts,
        data_uri(HERE / "assets" / "mw_heman_crop.jpg", max_w=900),
        facs_cap, about, FOOT)
    body_page = body_page.replace('<div class="board">',
                                  '<div class="board generic">')
    return body_page.replace("</style>", GENERIC_EXTRA_CSS + "</style>")


# ═══════════════════════════════════════════ H870 /entry-specimen engine ═══
# Two modes on top of the H780 engine above: --markup <dict> <headword>
# re-typesets any k1 headword from csl-orig; --image <path> annotates a
# supplied picture/PDF page with region-anchored callouts. One HTML source
# serves both the print-faithful single-sheet PDF (@media print) and a
# theme-aware interactive web page (hover/click sync, resize reflow,
# light/dark via prefers-color-scheme + toggle).

LIGHT_VARS = """
  --bg:#f4f1ea; --sheet:#fbf9f4; --ink:#1a1a1a; --accent:#005a87;
  --accent2:#00344e; --hlv:#cdeaf6; --linev:#333; --labv:#005a87;
  --muted:#555; --rule:#bbb; --box:#e9f4fa; --shadow:rgba(0,0,0,.18);
"""

DARK_VARS = """
  --bg:#14171c; --sheet:#1d222a; --ink:#e4e0d6; --accent:#71b8dc;
  --accent2:#a8d4ec; --hlv:#29506a; --linev:#9aa4ae; --labv:#8ec7e4;
  --muted:#98a0a8; --rule:#4a5058; --box:#232e38; --shadow:rgba(0,0,0,.5);
"""

SPECIMEN_CSS = f"""
:root {{ {LIGHT_VARS} }}
:root[data-theme="dark"] {{ {DARK_VARS} }}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{ {DARK_VARS} }}
}}
body {{ background:var(--bg); color:var(--ink); }}
.sheet {{ background:var(--sheet); }}
header {{ border-bottom-color:var(--accent); }}
header h1 {{ color:var(--accent2); }}
header p.sub {{ color:var(--muted); }}
.colcap {{ color:var(--muted); border-bottom-color:var(--rule); }}
.callout {{ color:var(--labv); cursor:pointer; }}
.callout b {{ color:var(--accent2); }}
.callout .prop {{ color:var(--muted); }}
.hl {{ background:var(--hlv); }}
svg.leaders path {{ stroke:var(--linev); }}
svg.leaders path.on {{ stroke:var(--accent); stroke-width:1.9; }}
.hl.hl-active {{ outline:2px solid var(--accent); outline-offset:1px; }}
.facsimile img {{ border-color:var(--rule); box-shadow:2px 3px 8px var(--shadow); }}
.facsimile .cap, .aboutbox {{ color:var(--ink); }}
.aboutbox {{ background:var(--box); border-left-color:var(--accent); }}
.aboutbox h2 {{ color:var(--accent2); }}
footer {{ color:var(--muted); border-top-color:var(--rule); }}
a {{ color:var(--accent); }}
.board.spec-text {{ grid-template-columns:420px 720px 420px; column-gap:40px; }}
.spec-text .callout {{ width:400px; }}
.board.spec-image {{ grid-template-columns:280px 1020px 280px; column-gap:35px; }}
.spec-image .callout {{ width:268px; }}
.imgwrap {{ position:relative; }}
.imgwrap img {{ width:100%; display:block; border:1px solid var(--rule); }}
.region {{ position:absolute; }}
.region.hl {{ background:rgba(109,186,228,.26); outline:1.6px solid var(--labv);
              outline-offset:1px; border-radius:2px; }}
.region.hl.hl-active {{ background:rgba(109,186,228,.45); }}
.themetoggle {{ position:fixed; top:14px; right:14px; z-index:9; width:38px;
   height:38px; border-radius:50%; border:1px solid var(--rule);
   background:var(--sheet); color:var(--ink); font-size:17px; cursor:pointer; }}
@media print {{
  :root, :root[data-theme="dark"], :root:not([data-theme="light"]) {{ {LIGHT_VARS} }}
  .themetoggle {{ display:none; }}
}}
"""

SPEC_JS = """
function targetEl(c) {
  const els = document.querySelectorAll(c.dataset.target);
  return els[Math.min(+(c.dataset.nth || 0), els.length - 1)];
}
function wire() {
  document.querySelectorAll('.callout').forEach(c => {
    if (c._wired) return;
    const el = targetEl(c);
    if (!el) return;
    c._wired = true;
    const on = () => { c.classList.add('active'); el.classList.add('hl-active');
                       if (c._p) c._p.classList.add('on'); };
    const off = () => { if (c._pin) return;
                        c.classList.remove('active');
                        el.classList.remove('hl-active');
                        if (c._p) c._p.classList.remove('on'); };
    for (const n of [c, el]) {
      n.addEventListener('mouseenter', on);
      n.addEventListener('mouseleave', off);
      n.addEventListener('click', ev => {
        c._pin = !c._pin; c._pin ? on() : off(); ev.stopPropagation(); });
    }
  });
}
window.addEventListener('load', () => setTimeout(wire, 700));
let _rsz = null;
window.addEventListener('resize', () => {
  clearTimeout(_rsz); _rsz = setTimeout(run, 180); });
const _btn = document.getElementById('themebtn');
if (_btn) _btn.addEventListener('click', () => {
  const r = document.documentElement;
  const cur = r.dataset.theme || 'auto';
  const next = cur === 'auto' ? 'dark' : cur === 'dark' ? 'light' : 'auto';
  if (next === 'auto') delete r.dataset.theme; else r.dataset.theme = next;
  _btn.textContent = {auto: '\\u25d0', dark: '\\u25cf', light: '\\u25cb'}[next];
});
"""


def specimen_page(title, subtitle, center_cap, center_html, callouts, foot,
                  mode, facs_uri=None, facs_cap="", about=""):
    """One self-contained specimen page: interactive on screen, single sheet
    in print. mode = 'text' | 'image'."""
    cos = "".join(callout_html(*c) for c in callouts)
    boardcls = "spec-image" if mode == "image" else "spec-text"
    bottom = ""
    if facs_uri or about:
        f = (f'<div class="facsimile"><img src="{facs_uri}" alt="facsimile">'
             f'<div class="cap">{facs_cap}</div></div>') if facs_uri else ""
        a = f'<div class="aboutbox">{about}</div>' if about else ""
        bottom = f'<div class="bottomrow">{f}{a}</div>'
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{PAGE_CSS}{SPECIMEN_CSS}</style></head>
<body>
<button class="themetoggle" id="themebtn" title="light / dark / auto">◐</button>
<div class="sheet">
<header><h1>{html.escape(title)}</h1><p class="sub">{subtitle}</p></header>
<div class="board {boardcls}">
<svg class="leaders"></svg>
<div></div>
<div class="colwrap"><div class="colcap">{center_cap}</div>{center_html}</div>
<div></div>
{cos}
</div>
{bottom}
<footer>{foot}</footer>
</div>
<script>{CALLOUT_JS}{SPEC_JS}</script>
</body></html>"""


# ------------------------------------------------------- markup mode (text)

DICT_LABEL = {
    "mw": "Monier-Williams, A Sanskrit-English Dictionary (1899)",
    "pwg": "Böhtlingk & Roth, Sanskrit-Wörterbuch (PWG, 1855–1875)",
    "pw": "Böhtlingk, Sanskrit-Wörterbuch in kürzerer Fassung (pw, 1879–1889)",
}


def dialect(dic):
    """Which render_body dialect a dictionary uses."""
    return "pwg" if dic in ("pwg", "pw") else "mw"


def load_dict_records(dic):
    path = CSL / dic / f"{dic}.txt"
    if not path.exists():
        sys.exit(f"source not found: {path}")
    return load_records(path)


def select_groups(recs, hw, dic):
    """All records with <k1> == hw, in L order, grouped into print
    paragraphs (MW: a new <e>1 record opens a paragraph, continuations
    join it; PWG and e-less dictionaries: one paragraph per record)."""
    picks = []
    for L, (hdr, _body) in recs.items():
        d = parse_header(hdr)
        if d.get("k1") == hw:
            key = int(re.sub(r"\D", "", L) or 0)
            picks.append((key, L, d))
    picks.sort()
    if not picks:
        sys.exit(f"headword {hw!r} not found in {dic}")
    groups = []
    for _, L, d in picks:
        e = d.get("e")
        if e is None or e == "1" or not groups:
            groups.append([])
        groups[-1].append(L)
    return groups


def group_paragraph(recs, group, dic):
    if dialect(dic) == "pwg":
        return pwg_paragraph(recs, group[0])
    return mw_paragraph(recs, group)


# First-pass callout proposals: (css selector, class regex, label html).
# Emitted only for classes present in the rendered column, marked
# "proposed — verify" — never presented as authoritative anatomy.
PROPOSED_CALLOUTS = [
    (".colwrap .hom", r'class="hom"',
     "<b>Homograph number</b> — identically spelt but etymologically "
     "distinct words are numbered in sequence"),
    (".colwrap .hw-dev", r"hw-dev",
     "<b>Main headword in Devanāgarī</b> — the main-entry script of the "
     "print (typographic level 1 in the digital record)"),
    (".colwrap .hw .siast", r'class="hw"',
     "<b>Transliterated headword in bold</b> — an acute accent marks the "
     "Vedic udātta where the print carries one"),
    (".colwrap .lex", r'class="lex"',
     "<b>Grammatical label</b> — gender / part of speech as printed"),
    (".colwrap .ls", r'class="ls',
     "<b>Citation</b> — literature source with locus; run-on citations "
     "abbreviate the repeated source (hover shows the expansion)"),
    (".colwrap .ab", r'class="ab',
     "<b>Abbreviation of the print</b> (cl., N., comp., ifc. …) — hover "
     "shows the expansion where the digital record encodes one"),
    (".colwrap .entry .sa", r'class="sa"',
     "<b>Sanskrit in Devanāgarī</b> — rendered from the SLP1 of the "
     "digital record; hover shows IAST"),
    (".colwrap .gloss", r'class="gloss"',
     "<b>Italics of the print</b> — definition / gloss text"),
    (".colwrap .sense", r'class="sense"',
     "<b>Sense numbering</b> — subdivisions inside one entry"),
    (".colwrap .bot", r'class="bot"',
     "<b>Botanical / zoological identification</b> — natural-history "
     "names resolved to Linnaean binomials"),
    (".colwrap .lang", r'class="lang"',
     "<b>Language label</b> — non-Sanskrit forms flagged by language"),
    (".colwrap .gk", r'class="gk"',
     "<b>Greek cognate</b> — comparative material in the etymological "
     "bracket"),
    (".colwrap .is", r'class="is"',
     "<b>Indian grammatical apparatus</b> — gaṇa membership and other "
     "references to the native tradition"),
]


def propose_callouts(center_html):
    out, side = [], "left"
    for sel, pat, note in PROPOSED_CALLOUTS:
        if re.search(pat, center_html):
            out.append((side, sel, 0,
                        note + ' <i class="prop">(proposed — verify)</i>'))
            side = "right" if side == "left" else "left"
    return out


def load_callout_spec(path):
    """--callouts spec: JSON list of {side, target, note[, nth]} or TSV
    side<TAB>target<TAB>note. Targets: a CSS selector ('.hw', '#r3'),
    literal anchor text to highlight (markup mode), or an x,y,w,h region
    in fractions of the image (image mode)."""
    p = Path(path)
    if p.suffix.lower() == ".json":
        return json.loads(p.read_text(encoding="utf-8"))
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        side, target, note = (line.split("\t") + ["", ""])[:3]
        rows.append({"side": side.strip(), "target": target.strip(),
                     "note": note.strip()})
    return rows


# dict= is carried explicitly (the endpoint's own nav links do the same).
# MW re-enabled 15-07-2026 after an api=1 probe DISPROVED the earlier
# "serves the 1872 edition" diagnosis: page=277 resolves to
# MWScanpdf/mw0277-kArSNi.pdf, the correct 1899 page, with or without
# dict=. The portal ALSO hosts the 1872 first-edition scan with colliding
# printed page numbers under a different browser (pg_NNNN.pdf files) — a
# hazard for manually-fetched pages, not for this endpoint. FINDINGS §80.
SCAN_URL = {
    "mw": ("https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2020/"
           "web/webtc/servepdf.php?dict=mw&page={page}"),
    "pwg": ("https://www.sanskrit-lexicon.uni-koeln.de/scans/PWGScan/2020/"
            "web/webtc/servepdf.php?dict=pwg&page={page}"),
}


def fetch_facsimile(dic, pc):
    """Auto-pull the print page from the Cologne scan server (H780 pattern);
    returns PNG bytes or None. Failures (offline, 429 throttle) are soft —
    the specimen just builds without the inset."""
    tmpl = SCAN_URL.get(dic)
    if not tmpl:
        return None
    page = pc.split(",")[0] if dic == "mw" else pc
    url = tmpl.format(page=page)
    import time
    import urllib.request
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (EntryAnatomy specimen build)",
        "Referer": "https://www.sanskrit-lexicon.uni-koeln.de/"})
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            if data[:4] == b"%PDF":
                return rasterize_pdf_bytes(data)
            return None
        except Exception as exc:
            if attempt == 1:
                time.sleep(8)
            else:
                print(f"  facsimile fetch failed ({exc}); "
                      "building without the print inset")
    return None


def rasterize_pdf_bytes(data, page_no=1, dpi=170):
    import fitz
    with fitz.open(stream=data, filetype="pdf") as doc:
        return doc[page_no - 1].get_pixmap(dpi=dpi).tobytes("png")


def rasterize(path, page_no=1, dpi=170):
    """A picture file -> bytes as-is; a PDF -> PNG of the given page."""
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        return rasterize_pdf_bytes(path.read_bytes(), page_no, dpi)
    return path.read_bytes()


def today():
    return datetime.date.today().strftime("%d-%m-%Y")


def spec_foot(source_line, proposed):
    prop = (" &middot; callout set proposed by the build — verify before "
            "publishing" if proposed else "")
    return (f"{source_line} &middot; built by build_entry_anatomy.py "
            f"(/entry-specimen, H870) &middot; Fable 5 (claude-fable-5), "
            f"{today()}{prop} &middot; Cologne Sanskrit-Lexicon: "
            '<a href="https://www.sanskrit-lexicon.uni-koeln.de/">'
            "sanskrit-lexicon.uni-koeln.de</a>")


def build_markup_specimen(dic, hw, callout_rows=None, facs_img=None,
                          title=None, out_dir=None, stem=None):
    recs = load_dict_records(dic)
    groups = select_groups(recs, hw, dic)
    center = "".join(group_paragraph(recs, g, dic) for g in groups)
    first = parse_header(recs[groups[0][0]][0])
    pc = first.get("pc", "?")
    label = DICT_LABEL.get(dic, dic.upper())

    proposed = not callout_rows
    if callout_rows:
        callouts = []
        for d in callout_rows:
            t = d["target"]
            if not re.match(r"^[.#\[]", t):      # literal text -> wrap + id
                ident = f"anchor{len(callouts)}"
                center = wrap_once(center, t, "anchor", ident)
                t = f"#{ident}"
            callouts.append((d.get("side", "left"), t,
                             int(d.get("nth", 0)), d["note"]))
    else:
        callouts = propose_callouts(center)

    facs_uri = facs_cap = None
    png = data_uri(facs_img, max_w=900) if facs_img else None
    if png is None:
        fetched = fetch_facsimile(dic, pc)
        if fetched:
            png = data_uri(fetched, max_w=900)
            facs_cap = (f"<b>The page in the print</b>: {label}, "
                        f"{pc} — from the Cologne scan server.")
    else:
        facs_cap = (f"<b>The entry in the print</b>: {label}, {pc} — "
                    "supplied scan (Cologne Sanskrit-Lexicon scan archive).")
    facs_uri = png

    hw_disp = slp_iast(hw)
    title = title or f"How to read an entry — {label}: {hw_disp}"
    n_recs = sum(len(g) for g in groups)
    sub = (f"Entry specimen after the model of Duden’s <i>Deutsches "
           f"Universalwörterbuch</i> spread: <i>{hw_disp}</i> re-typeset "
           f"from the Cologne digital text ({n_recs} records, "
           f"{len(groups)} print paragraph{'s' if len(groups) > 1 else ''}), "
           f"microstructural elements labelled. Interactive on screen "
           f"(hover/click a label or a highlight; light/dark toggle); one "
           f"single sheet in print.")
    about = ("<h2>How to use this page</h2>"
             "The column re-typesets every record whose key1 equals the "
             f"requested headword from csl-orig v02/{dic}; callout labels "
             "are wired by leader lines to highlighted elements. "
             + ("This callout set is a <b>first pass proposed by the build "
                "tool — verify against the print before treating it as "
                "authoritative anatomy</b>. " if proposed else "")
             + "Sigla and citations are reproduced verbatim from the "
               "digital record.")
    foot = spec_foot(
        f"Typeset from csl-orig v02/{dic} (k1 = {html.escape(hw)}, "
        f"{n_recs} records, print locus {pc})", proposed)
    page_html = specimen_page(title, sub, f"{dic.upper()} · {pc}", center,
                              callouts, foot, "text", facs_uri,
                              facs_cap or "", about)
    stem = stem or f"{dic}-{hw}-specimen"
    return write_specimen(page_html, stem, out_dir)


# ------------------------------------------------------------- image mode

def build_image_specimen(image_path, callout_rows, title=None, page_no=1,
                         dpi=170, out_dir=None, stem=None, caption=None):
    img_bytes = rasterize(image_path, page_no, dpi)
    uri = data_uri(img_bytes, quality=88, max_w=2000)

    regions, callouts = [], []
    proposed = not callout_rows
    if not callout_rows:
        callout_rows = [{"side": "left", "target": "0.05,0.05,0.9,0.9",
                         "note": "<b>Whole page</b> — supply --callouts "
                                 "with x,y,w,h regions to annotate "
                                 '<i class="prop">(proposed — verify)</i>'}]
    for d in callout_rows:
        t = d["target"]
        if isinstance(t, str) and re.match(r"^[\d.]+\s*,", t):
            t = [float(v) for v in t.split(",")]
        if isinstance(t, dict):
            t = [t["x"], t["y"], t["w"], t["h"]]
        if isinstance(t, (list, tuple)):
            rid = f"r{len(regions) + 1}"
            regions.append(
                f'<div class="region" id="{rid}" style="'
                f"left:{t[0] * 100:.2f}%;top:{t[1] * 100:.2f}%;"
                f"width:{t[2] * 100:.2f}%;height:{t[3] * 100:.2f}%" '"></div>')
            t = f"#{rid}"
        callouts.append((d.get("side", "right"), t,
                         int(d.get("nth", 0)), d["note"]))

    name = Path(image_path).name
    center = f'<div class="imgwrap"><img src="{uri}" alt="{html.escape(name)}">' \
             + "".join(regions) + "</div>"
    title = title or f"Annotated specimen — {name}"
    sub = ("Image-annotation specimen: callout labels wired by leader lines "
           "to regions of the supplied page. Interactive on screen "
           "(hover/click a label or a region; light/dark toggle); one "
           "single sheet in print.")
    foot = spec_foot(f"Annotation surface: {html.escape(name)}"
                     + (f", page {page_no}" if
                        str(image_path).lower().endswith(".pdf") else ""),
                     proposed)
    page_html = specimen_page(title, sub, caption or html.escape(name),
                              center, callouts, foot, "image")
    stem = stem or re.sub(r"[^A-Za-z0-9_-]+", "-", Path(image_path).stem) \
        + "-specimen"
    return write_specimen(page_html, stem, out_dir)


# ------------------------------------------------------------ output layer

def write_specimen(page_html, stem, out_dir=None):
    out_dir = Path(out_dir) if out_dir else HERE
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{stem}.html"
    path.write_text(page_html, encoding="utf-8")
    print(f"wrote {path.name} ({len(page_html) // 1024} KB)")
    return path


def find_browser():
    for cand in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                 r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                 r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                 "chrome", "msedge", "chromium", "google-chrome"):
        exe = cand if Path(cand).exists() else shutil.which(cand)
        if exe:
            return exe
    return None


def export_pdf(html_path):
    exe = find_browser()
    if not exe:
        print("  no Chrome/Edge found — skipped PDF export")
        return None
    pdf_path = html_path.with_suffix(".pdf")
    subprocess.run(
        [exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         "--virtual-time-budget=8000", f"--print-to-pdf={pdf_path}",
         str(html_path)],
        check=True, capture_output=True)
    print(f"wrote {pdf_path.name} ({pdf_path.stat().st_size // 1024} KB)")
    return pdf_path


# ==================================================================== main

def build_legacy():
    pwg = load_records(PWG_TXT)
    mw = load_records(MW_TXT)
    out = {
        "pwg-entry-anatomy.html": build_pwg(pwg),
        "mw-entry-anatomy.html": build_mw(mw),
        "cdsl-record-anatomy.html": build_generic(pwg, mw),
    }
    for name, htm in out.items():
        (HERE / name).write_text(htm, encoding="utf-8")
        print(f"wrote {name} ({len(htm)//1024} KB)")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Duden-style entry-anatomy specimen builder "
                    "(H780 pages + H870 /entry-specimen modes)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--markup", nargs=2, metavar=("DICT", "HEADWORD"),
                      help="re-typeset a csl-orig headword (k1, SLP1)")
    mode.add_argument("--image", metavar="PATH",
                      help="annotate a picture or PDF page")
    ap.add_argument("--callouts", metavar="SPEC",
                    help="JSON/TSV callout spec (side, target, note)")
    ap.add_argument("--facsimile", metavar="IMG",
                    help="markup mode: print-inset image "
                         "(default: auto-pull from the Cologne scan server)")
    ap.add_argument("--page", type=int, default=1,
                    help="image mode: PDF page number (default 1)")
    ap.add_argument("--dpi", type=int, default=170,
                    help="image mode: PDF rasterization DPI (default 170)")
    ap.add_argument("--title", help="page title override")
    ap.add_argument("--caption", help="column caption override")
    ap.add_argument("--stem", help="output filename stem override")
    ap.add_argument("--out", metavar="DIR", help="output directory")
    ap.add_argument("--pdf", action="store_true",
                    help="emit the print PDF (default: both outputs)")
    ap.add_argument("--web", action="store_true",
                    help="emit the interactive HTML (default: both outputs)")
    args = ap.parse_args(argv)

    if not args.markup and not args.image:
        build_legacy()
        return

    rows = load_callout_spec(args.callouts) if args.callouts else None
    if args.markup:
        dic, hw = args.markup
        html_path = build_markup_specimen(
            dic, hw, rows, args.facsimile, args.title, args.out, args.stem)
    else:
        html_path = build_image_specimen(
            args.image, rows, args.title, args.page, args.dpi,
            args.out, args.stem, args.caption)

    want_pdf = args.pdf or not args.web       # default: both
    if want_pdf:
        export_pdf(html_path)
    if args.web and not args.pdf:
        pass  # the HTML written above IS the web artifact


if __name__ == "__main__":
    main()

