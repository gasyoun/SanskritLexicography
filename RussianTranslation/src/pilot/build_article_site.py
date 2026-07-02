#!/usr/bin/env python
r"""Compile the PWG->RU(+EN) translations into human-readable articles.

Produces, under RussianTranslation/article_site/ :
  * md/<root>.md               -- one file per root article (DE source + RU + EN)
  * md/subcards/<subcard>.md   -- one file per sub-card (prefixed form)
  * articles.js                -- window.ARTICLES data (pre-rendered HTML), embedded
  * index.html                 -- self-contained browser (RU default, EN tab, IAST)

Data sources (both already exist; nothing regenerated):
  * src/pwg_ru_translated.jsonl -- RU spine, flat per-sense rows (de, ru, subcard,
    sense_tag, h, iast, dcs_freq, review_status, provenance). ~46 roots.
  * wf_output.en.<root>.json    -- EN per-root stores (records[].senses[] german+english).

Markup rendering (IAST, per MG 2026-07-01):
  {#SLP1#}   -> italic IAST (SLP1->IAST via corpus_gate._S2I; Vedic accents dropped)
  {%gloss%}  -> the translatable gloss, unwrapped
  <ls>..</ls>-> citation span   <ab>..</ab> -> abbreviation
  <lex>..>   -> grammar label    <is>/<hom>/<div>/[Page..] -> unwrapped / dropped

  python src/pilot/build_article_site.py            # build everything
  python src/pilot/build_article_site.py --root gam # one root (debug print)
"""
import argparse
import glob
import html
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
REPO = os.path.dirname(SRC)
sys.path.insert(0, SRC)
import corpus_gate as cg  # noqa: E402  (_S2I SLP1->IAST map)
import ls_resolver as lsr  # noqa: E402  (<ls> citation -> Cologne scan URL; PWG paths)

RU_STORE = os.path.join(SRC, 'pwg_ru_translated.jsonl')
OUT_DIR = os.path.join(REPO, 'article_site')

_ACCENT = re.compile(r'[\\/^~]')          # Vedic udatta/anudatta/svarita markers
_SK = re.compile(r'\{#(.*?)#\}', re.S)
_GL = re.compile(r'\{%(.*?)%\}', re.S)
_LS = re.compile(r'<ls\b([^>]*)>(.*?)</ls>', re.S)
_N_ATTR = re.compile(r'\bn\s*=\s*"([^"]*)"')


def _ls_href(attrs, visible):
    """Resolve one <ls> citation to a Cologne scan URL (PWG), or None.

    `attrs` is the raw attribute string of the <ls> tag; the `n=` attribute
    carries the normalized prefix (+ leading coords) that the source uses so
    bare-number continuation refs (e.g. `4,10,7.` after `AV. 11,4,26.`) resolve
    against the right work. `visible` is the inner text shown to the reader."""
    m = _N_ATTR.search(attrs or '')
    n_attr = m.group(1) if m else None
    try:
        return lsr.generate_href('pwg', n_attr, (visible or '').strip())
    except Exception:
        return None
_AB = re.compile(r'<ab\b[^>]*>(.*?)</ab>', re.S)
_LEX = re.compile(r'<lex\b[^>]*>(.*?)</lex>', re.S)
_IS = re.compile(r'<is\b[^>]*>(.*?)</is>', re.S)
_HOM = re.compile(r'<hom\b[^>]*>(.*?)</hom>', re.S)
_PAGE = re.compile(r'\[Page[^\]]*\]')
_TAG = re.compile(r'<[^>]+>')             # any leftover tag


def slp1_iast(s):
    """SLP1 running text -> IAST (drop Vedic accent marks for readability)."""
    s = _ACCENT.sub('', s or '')
    return ''.join(cg._S2I.get(c, c) for c in s)


def _render(text, mode):
    """Render one stored field (de/ru/en) to `html` or `md`.

    Sanskrit spans -> italic IAST; glosses unwrapped; citations/abbrevs kept in a
    light wrapper; structural tags dropped. The two modes differ only in the
    emphasis/needed-escaping syntax."""
    if not text:
        return ''
    t = _PAGE.sub('', text)
    if mode == 'html':
        # Convert the tags we KEEP into sentinel-wrapped tags first (LT/GT are
        # placeholder chars, unquoted class= so html.escape won't mangle them),
        # then strip leftover SOURCE structural tags (<div>, <sic/>, ...), then
        # html-escape the plain text, then restore our sentinels to real tags.
        # (The old generic <[^>]+> strip removed our own generated spans too.)
        LT, GT = '\x01', '\x02'
        t = _SK.sub(lambda m: '%si class=sa%s%s%s/i%s' % (LT, GT, slp1_iast(m.group(1)), LT, GT), t)

        def _ls_html(m):
            # Resolved citation -> clickable <a class=ls href=..> (scan page);
            # unresolved -> plain <span class=ls> (kept dim so gaps stay visible).
            # Attribute values are left unquoted so the later html.escape (which
            # escapes " ' & < >) cannot mangle them; scan URLs contain none of the
            # quote/space chars that would require quoting.
            vis = m.group(2).strip()
            url = _ls_href(m.group(1), vis)
            if url:
                # <a class=ls href=URL target=_blank rel=noopener>VIS</a>
                return '%sa class=ls href=%s target=_blank rel=noopener%s%s%s/a%s' % (
                    LT, url, GT, vis, LT, GT)
            return '%sspan class=ls%s%s%s/span%s' % (LT, GT, vis, LT, GT)
        t = _LS.sub(_ls_html, t)
        t = _AB.sub(lambda m: '%sspan class=ab%s%s%s/span%s' % (LT, GT, m.group(1).strip(), LT, GT), t)
        t = _LEX.sub(lambda m: '%sspan class=lex%s%s%s/span%s' % (LT, GT, m.group(1).strip(), LT, GT), t)
        t = _IS.sub(lambda m: '%si%s%s%s/i%s' % (LT, GT, m.group(1), LT, GT), t)
        t = _HOM.sub(lambda m: '%sb%s%s%s/b%s' % (LT, GT, m.group(1), LT, GT), t)
        t = _GL.sub(lambda m: m.group(1), t)
        t = _TAG.sub('', t)               # drop leftover source structural tags
        t = html.escape(t)                # escape &,<,> in the remaining plain text
        t = t.replace('\n', '<br>')       # real <br> (added after escape)
        t = t.replace(LT, '<').replace(GT, '>')   # restore our kept tags
    else:  # md
        t = _SK.sub(lambda m: '*%s*' % slp1_iast(m.group(1)), t)
        t = _GL.sub(lambda m: m.group(1), t)

        def _ls_md(m):
            vis = m.group(2).strip()
            url = _ls_href(m.group(1), vis)
            return '[%s](%s)' % (vis, url) if url else '[%s]' % vis
        t = _LS.sub(_ls_md, t)
        t = _AB.sub(lambda m: m.group(1).strip(), t)
        t = _LEX.sub(lambda m: '_%s_' % m.group(1).strip(), t)
        t = _IS.sub(lambda m: m.group(1), t)
        t = _HOM.sub(lambda m: '**%s**' % m.group(1), t)
        t = _TAG.sub('', t)
    t = re.sub(r'[ \t]{2,}', ' ', t)
    return t.strip()


def _root_of(key1):
    return (key1 or '').split('~~')[0]


def load_ru():
    """root -> ordered list of (subcard, h, iast, tag, de, ru, dcs, extra)."""
    roots = {}
    with open(RU_STORE, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            root = _root_of(r.get('key1') or r.get('subcard'))
            roots.setdefault(root, []).append(r)
    return roots


def _norm(s):
    """Whitespace-insensitive key for joining RU `de` to EN `german` (same source text)."""
    return re.sub(r'\s+', '', s or '')


def load_en(root):
    """Return two EN indices for a root, both keyed within the sub-card:
      by_text[(subcard, norm(german))] -> english   (primary; de==german join)
      by_tag[(subcard, tag)]           -> english   (fallback)
    The German source is identical in the RU and EN stores, so the text join is
    far more reliable than the tag join (RU sense_tag != EN tag conventions)."""
    fp = os.path.join(REPO, 'wf_output.en.%s.json' % root)
    if not os.path.exists(fp):
        return {}, {}
    by_text, by_tag = {}, {}
    for e in json.load(open(fp, encoding='utf-8')).get('results') or []:
        c = e.get('card')
        if not c:
            continue
        for i, s in enumerate(rec_senses(c)):
            if not s.get('english'):
                continue
            tag = str(s.get('tag') if s.get('tag') is not None else i)
            by_tag.setdefault((e['key'], tag), s['english'])
            if s.get('german'):
                by_text.setdefault((e['key'], _norm(s['german'])), s['english'])
    return by_text, by_tag


def rec_senses(card):
    for rec in (card.get('records') or []):
        for s in (rec.get('senses') or []):
            yield s


def dcs_count(dcs):
    if isinstance(dcs, dict):
        return dcs.get('count')
    return None


def load_en_full(root):
    """EN store as ordered structure: (selected_key_order, {subcard: {iast,h,senses:[{tag,german,english}]}})."""
    fp = os.path.join(REPO, 'wf_output.en.%s.json' % root)
    if not os.path.exists(fp):
        return [], {}
    d = json.load(open(fp, encoding='utf-8'))
    by_sub = {}
    for e in d['results']:
        c = e.get('card')
        if not c:
            continue
        rec0 = (c.get('records') or [{}])[0]
        senses = []
        for i, s in enumerate(rec_senses(c)):
            senses.append({'tag': str(s.get('tag') if s.get('tag') is not None else i),
                           'german': s.get('german') or '', 'english': s.get('english') or ''})
        by_sub[e['key']] = {'iast': c.get('iast') or '', 'h': rec0.get('h') or '', 'senses': senses}
    return list(d['meta'].get('selected_keys') or []), by_sub


def make_sense(tag, de, ru, en, dcs, src):
    return {
        'tag': str(tag), 'has_ru': bool(ru), 'has_en': bool(en),
        'de_html': _render(de, 'html'), 'ru_html': _render(ru, 'html'), 'en_html': _render(en, 'html'),
        'de_md': _render(de, 'md'), 'ru_md': _render(ru, 'md'), 'en_md': _render(en, 'md'),
        'dcs': dcs_count(dcs), 'src': src or '',
    }


def build_model():
    """UNION spine: every EN sub-card/sense (the full per-root set) with RU attached
    where present, plus any RU-only sub-cards/senses appended. So EN-complete roots
    (e.g. gam, 127 sub-cards) show fully even where RU is partial, and the gap is
    visible per sense (has_ru / has_en)."""
    ru = load_ru()
    en_files = {os.path.basename(f).replace('wf_output.en.', '').replace('.json', '')
                for f in glob.glob(os.path.join(REPO, 'wf_output.en.*.json'))}
    model = []
    for root in sorted(set(ru) | en_files, key=lambda s: slp1_iast(s).lower()):
        ru_rows = ru.get(root, [])
        ru_by_sub = {}
        for r in ru_rows:
            ru_by_sub.setdefault(r.get('subcard') or r.get('key1'), []).append(r)
        ru_bytext, ru_bytag = {}, {}
        for sub, rows in ru_by_sub.items():
            for i, r in enumerate(rows):
                ru_bytext.setdefault((sub, _norm(r.get('de'))), r)
                tg = str(r.get('sense_tag') if r.get('sense_tag') is not None else i)
                ru_bytag.setdefault((sub, tg), r)
        en_order, en_by_sub = load_en_full(root)
        sub_order = list(en_order)
        seen = set(sub_order)
        for r in ru_rows:
            sub = r.get('subcard') or r.get('key1')
            if sub not in seen:
                sub_order.append(sub)
                seen.add(sub)
        subcards = []
        n_sense = n_ru = n_en = 0
        for sub in sub_order:
            en_entry = en_by_sub.get(sub)
            en_senses = en_entry['senses'] if en_entry else []
            ru_sub_rows = ru_by_sub.get(sub, [])
            used = set()
            senses = []
            for i, es in enumerate(en_senses):
                rrow = (ru_bytext.get((sub, _norm(es['german'])))
                        or ru_bytag.get((sub, es['tag'])))
                if rrow is not None:
                    used.add(id(rrow))
                senses.append(make_sense(
                    tag=es['tag'], de=(rrow.get('de') if rrow else es['german']),
                    ru=(rrow.get('ru') if rrow else None), en=es['english'],
                    dcs=(rrow.get('dcs_freq') if rrow else None),
                    src=(rrow.get('source_type') if rrow else '')))
            for i, r in enumerate(ru_sub_rows):
                if id(r) in used:
                    continue
                senses.append(make_sense(
                    tag=(r.get('sense_tag') if r.get('sense_tag') is not None else i),
                    de=r.get('de'), ru=r.get('ru'), en=None,
                    dcs=r.get('dcs_freq'), src=r.get('source_type')))
            if not senses:
                continue
            # Grammatical head block (tag 'header'/'head') is the entry preamble
            # (√root, Dhātup. reference, tense stems) and must LEAD the sub-card,
            # even when the source store lists it after sense 1 (the bug that made
            # e.g. bandh open on sense 1). Stable sort keeps all other senses in
            # their original order.
            senses.sort(key=lambda s: 0 if str(s['tag']).lower() in ('header', 'head') else 1)
            ru0 = ru_sub_rows[0] if ru_sub_rows else None
            iast = (ru0.get('iast') if ru0 else '') or (en_entry.get('iast') if en_entry else '') or ''
            h = (ru0.get('h') if ru0 else '') or (en_entry.get('h') if en_entry else '') or ''
            for s in senses:
                n_sense += 1
                n_ru += 1 if s['has_ru'] else 0
                n_en += 1 if s['has_en'] else 0
            subcards.append({'key': sub, 'h': h, 'iast': iast, 'senses': senses})
        model.append({
            'root': root, 'iast': slp1_iast(root),
            'en_available': bool(en_by_sub), 'ru_available': bool(ru_rows),
            'n_subcards': len(subcards), 'n_senses': n_sense,
            'n_ru_senses': n_ru, 'n_en_senses': n_en,
            'subcards': subcards,
        })
    return model


# ---------------- markdown emitters ----------------
def sense_md(s, with_en):
    # The grammatical head block carries no sense number, so drop the "N)" chip.
    lead = '' if str(s['tag']).lower() in ('header', 'head') else '**%s)** ' % s['tag']
    out = ['', '%s%s' % (lead, s['de_md'])]
    if s['ru_md']:
        out.append('')
        out.append('- **RU:** %s' % s['ru_md'])
    if with_en and s['en_md']:
        out.append('- **EN:** %s' % s['en_md'])
    badge = []
    if s['dcs'] is not None:
        badge.append('DCS %s' % s['dcs'])
    if s['src']:
        badge.append(s['src'])
    if badge:
        out.append('  <sub>%s</sub>' % ' · '.join(badge))
    return '\n'.join(out)


def subcard_md(sub):
    head = sub['iast'] or slp1_iast(sub['h']) or sub['key']
    lines = ['## %s' % head, '', '`%s`' % sub['key'], '']
    for s in sub['senses']:
        lines.append(sense_md(s, with_en=True))
    return '\n'.join(lines) + '\n'


def root_md(r):
    lines = ['# %s' % r['iast'], '',
             '_PWG article — %d sub-card(s), %d sense(s) · RU %d/%d · EN %d/%d_' % (
                 r['n_subcards'], r['n_senses'],
                 r['n_ru_senses'], r['n_senses'], r['n_en_senses'], r['n_senses']),
             '']
    for sub in r['subcards']:
        lines.append(subcard_md(sub))
    return '\n'.join(lines)


# ---------------- html emitter ----------------
INDEX_HTML = r"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PWG — переводы статей (RU / EN)</title>
<style>
:root{--bg:#fff;--fg:#1a1a1a;--mut:#6a6a6a;--line:#e4e4e4;--accent:#7a1f1f;--sa:#0b5;--card:#fafafa}
@media(prefers-color-scheme:dark){:root{--bg:#161616;--fg:#e8e8e8;--mut:#9a9a9a;--line:#333;--accent:#e6928a;--sa:#7ddda0;--card:#1e1e1e}}
*{box-sizing:border-box}body{margin:0;font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;color:var(--fg);background:var(--bg)}
#wrap{display:flex;min-height:100vh}
#side{width:250px;border-right:1px solid var(--line);padding:10px;overflow-y:auto;height:100vh;position:sticky;top:0}
#side h1{font-size:15px;margin:4px 6px 8px}
#q{width:100%;padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);margin-bottom:8px}
.rlink{display:flex;justify-content:space-between;gap:6px;padding:4px 8px;border-radius:6px;cursor:pointer;font-size:14px}
.rlink:hover{background:var(--card)}.rlink.active{background:var(--accent);color:#fff}
.rlink .en{font-size:11px;color:var(--mut)}.rlink.active .en{color:#fff}
.cov{font-size:10px;color:var(--mut)}.cov.low{color:#c46b00;font-weight:600}
.rlink.active .cov,.rlink.active .cov.low{color:#ffd9a8}
#main{flex:1;padding:20px 28px;max-width:900px}
.iast{font-style:italic}
h2.root{font-size:26px;margin:0 0 2px}.meta{color:var(--mut);font-size:13px;margin-bottom:14px}
.tabs{display:inline-flex;border:1px solid var(--line);border-radius:8px;overflow:hidden;margin-bottom:16px}
.tabs .tab{border:0;border-right:1px solid var(--line);background:var(--bg);color:var(--fg);padding:6px 16px;cursor:pointer;font-size:14px}
.tabs .tab:last-child{border-right:0}
.tabs .tab.on{background:var(--accent);color:#fff}
.sub{margin:18px 0;padding-bottom:6px;border-bottom:1px solid var(--line)}
.sub h3{margin:0 0 2px;font-size:19px}.sub .k{color:var(--mut);font-size:12px;font-family:ui-monospace,monospace}
.sense{margin:12px 0;padding:10px 12px;background:var(--card);border-radius:8px}
.tag{font-weight:700;color:var(--accent);margin-right:4px}
.de{margin-bottom:6px}.tr{padding-top:6px;margin-top:6px;border-top:1px dashed var(--line)}
.lbl{font-size:10px;letter-spacing:.05em;color:#fff;background:var(--mut);border-radius:3px;padding:0 5px;text-transform:uppercase;margin-right:6px;vertical-align:1px}
i.sa{font-style:italic;color:var(--sa)}
.ls{color:var(--mut);font-size:.92em}
a.ls{color:var(--accent);font-size:.92em;text-decoration:none;border-bottom:1px dotted var(--accent)}
a.ls:hover{text-decoration:underline;border-bottom-color:transparent}
.ab{font-style:italic;color:var(--mut)}.lex{font-variant:small-caps;color:var(--mut)}
.badges{margin-top:6px}.badge{display:inline-block;font-size:11px;color:var(--mut);border:1px solid var(--line);border-radius:10px;padding:0 7px;margin-right:5px}
.na{color:var(--mut);font-style:italic}
/* language switch: show German always as reference in ru/en; German-only in de mode */
#artbody.lang-ru .tr.en{display:none}
#artbody.lang-en .tr.ru{display:none}
#artbody.lang-de .tr{display:none}
#artbody.lang-de .de{font-size:16px}
#artbody:not(.lang-de) .de{color:var(--mut)}   /* dim the source when a translation is primary */
#artbody:not(.lang-de) .de i.sa{color:var(--sa)}
</style></head><body><div id="wrap">
<nav id="side"><h1>PWG статьи</h1><input id="q" placeholder="фильтр корней…"><div id="list"></div></nav>
<main id="main"><div id="arthead"></div><div id="artbody" class="lang-ru"><p class="na">Загрузка…</p></div></main></div>
<script src="articles.js"></script>
<script>
var A=window.ARTICLES||{roots:[]}, lang='ru', cur=null;
var list=document.getElementById('list'), q=document.getElementById('q');
var arthead=document.getElementById('arthead'), artbody=document.getElementById('artbody');
function esc(x){return x==null?'':(''+x);}
function renderList(f){list.innerHTML='';A.roots.filter(function(r){return !f||r.iast.toLowerCase().indexOf(f)>=0||r.root.toLowerCase().indexOf(f)>=0;}).forEach(function(r){
 var d=document.createElement('div');d.className='rlink'+(cur===r.root?' active':'');
 var ruf=r.n_senses?Math.round(100*r.n_ru_senses/r.n_senses):0;
 d.innerHTML='<span class="iast">'+r.iast+'</span><span class="en" title="senses; RU / EN coverage">'+r.n_senses+' <span class="cov'+(ruf<100?' low':'')+'">RU'+ruf+'%</span></span>';
 d.onclick=function(){cur=r.root;renderList(q.value.toLowerCase());renderRoot(r);};list.appendChild(d);});}
// Language is a CSS class on #artbody (lang-de|lang-ru|lang-en). All three blocks
// are always in the DOM; the class shows/hides them, so switching cannot silently no-op.
function applyLang(){
 artbody.className='lang-'+lang;
 var t=document.querySelectorAll('.tab');for(var i=0;i<t.length;i++){t[i].classList.toggle('on',t[i].getAttribute('data-lang')===lang);}
}
function trBlock(cls,label,txt){
 return '<div class="tr '+cls+'"><span class="lbl">'+label+'</span>'+(txt?txt:'<span class="na">— нет / n/a —</span>')+'</div>';
}
function renderBody(r){
 var subs=(window.ROOT||{})[r.root]||[]; var h='';
 subs.forEach(function(sub){
  h+='<div class="sub"><h3 class="iast">'+esc(sub.iast||sub.h||sub.key)+'</h3><div class="k">'+esc(sub.key)+'</div></div>';
  sub.senses.forEach(function(s){
   var b='';if(s.dcs!=null)b+='<span class="badge">DCS '+s.dcs+'</span>';if(s.src)b+='<span class="badge">'+s.src+'</span>';
   var tg=(s.tag==='header'||s.tag==='head')?'':'<span class="tag">'+esc(s.tag)+')</span>';
   h+='<div class="sense">'
    +'<div class="de">'+tg+'<span class="lbl">DE</span>'+esc(s.de_html)+'</div>'
    +trBlock('ru','RU',s.ru_html)+trBlock('en','EN',s.en_html)
    +(b?'<div class="badges">'+b+'</div>':'')+'</div>';
  });
 });
 artbody.innerHTML=h||'<p class="na">нет данных</p>'; applyLang();
}
function renderRoot(r){
 cur=r.root;
 arthead.innerHTML='<h2 class="root iast">'+r.iast+'</h2>'
  +'<div class="meta">PWG-статья · '+r.n_subcards+' под-карт., '+r.n_senses+' знач.'
  +' · <b>RU '+r.n_ru_senses+'/'+r.n_senses+'</b> · EN '+r.n_en_senses+'/'+r.n_senses
  +(r.n_ru_senses<r.n_senses?' <span class="cov low">RU неполный</span>':'')+'</div>'
  +'<div class="tabs">'
  +'<button class="tab" data-lang="de">Deutsch (оригинал)</button>'
  +'<button class="tab" data-lang="ru">Русский</button>'
  +'<button class="tab" data-lang="en">English</button></div>';
 // lazy-load this root's data (window.ROOT[root]) via <script src> — works from file:// too
 if((window.ROOT||{})[r.root]){renderBody(r);return;}
 artbody.innerHTML='<p class="na">Загрузка…</p>';
 var sc=document.createElement('script'); sc.src='roots/'+r.safe+'.js';
 sc.onload=function(){ if(cur===r.root) renderBody(r); };
 sc.onerror=function(){ if(cur===r.root) artbody.innerHTML='<p class="na">ошибка загрузки</p>'; };
 document.head.appendChild(sc);
}
// delegated tab handler (survives per-root re-render)
document.getElementById('main').addEventListener('click',function(e){
 var b=e.target.closest?e.target.closest('.tab'):null;if(!b)return;lang=b.getAttribute('data-lang');applyLang();
});
q.oninput=function(){renderList(q.value.toLowerCase());};
renderList('');if(A.roots.length){renderList('');renderRoot(A.roots[0]);}
</script></body></html>
"""


def emit(model):
    os.makedirs(os.path.join(OUT_DIR, 'md', 'subcards'), exist_ok=True)
    # per-root + per-subcard markdown
    for r in model:
        with open(os.path.join(OUT_DIR, 'md', '%s.md' % r['root']), 'w',
                  encoding='utf-8', newline='\n') as f:
            f.write(root_md(r))
        for sub in r['subcards']:
            safe = re.sub(r'[^A-Za-z0-9_.~-]', '_', sub['key'])
            with open(os.path.join(OUT_DIR, 'md', 'subcards', '%s.md' % safe), 'w',
                      encoding='utf-8', newline='\n') as f:
                f.write(subcard_md(sub))
    # index markdown
    with open(os.path.join(OUT_DIR, 'md', 'INDEX.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# PWG articles — RU (+EN)\n\n')
        for r in model:
            f.write('- [%s](%s.md) — %d senses%s\n' % (
                r['iast'], r['root'], r['n_senses'],
                ', EN %d' % r['n_en_senses'] if r['en_available'] else ''))
    # LAZY-LOAD: articles.js carries only a tiny per-root INDEX (no senses); each root's
    # heavy pre-rendered HTML goes to roots/<safe>.js as window.ROOT["<root>"] = [...]. The
    # page loads the index (KB) up front and injects one root file on click via <script src>
    # (works from file:// too, unlike fetch). First paint drops from ~13 MB to a few KB + 1 root.
    os.makedirs(os.path.join(OUT_DIR, 'roots'), exist_ok=True)
    index = {'roots': []}
    for r in model:
        safe = re.sub(r'[^A-Za-z0-9_.~-]', '_', r['root'])
        index['roots'].append({
            'root': r['root'], 'safe': safe, 'iast': r['iast'], 'en_available': r['en_available'],
            'n_subcards': r['n_subcards'], 'n_senses': r['n_senses'],
            'n_ru_senses': r['n_ru_senses'], 'n_en_senses': r['n_en_senses']})
        subs = [{'key': s['key'], 'h': s['h'], 'iast': s['iast'], 'senses': [
            {'tag': x['tag'], 'de_html': x['de_html'], 'ru_html': x['ru_html'],
             'en_html': x['en_html'], 'dcs': x['dcs'], 'src': x['src']}
            for x in s['senses']]} for s in r['subcards']]
        with open(os.path.join(OUT_DIR, 'roots', '%s.js' % safe), 'w', encoding='utf-8', newline='\n') as f:
            f.write('window.ROOT=window.ROOT||{};window.ROOT[%s]=' % json.dumps(r['root'], ensure_ascii=False))
            json.dump(subs, f, ensure_ascii=False)
            f.write(';\n')
    with open(os.path.join(OUT_DIR, 'articles.js'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('window.ARTICLES=')
        json.dump(index, f, ensure_ascii=False)
        f.write(';\n')
    with open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(INDEX_HTML)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', help='debug: print one root and exit')
    args = ap.parse_args()
    model = build_model()
    if args.root:
        r = next((x for x in model if x['root'] == args.root), None)
        if not r:
            sys.exit('no root %r (have %d)' % (args.root, len(model)))
        print(root_md(r))
        return
    emit(model)
    roots = len(model)
    senses = sum(r['n_senses'] for r in model)
    en_roots = sum(1 for r in model if r['en_available'])
    print('article_site/: %d roots, %d senses, %d roots with EN' % (roots, senses, en_roots))
    print('  index.html + articles.js + md/%d root files + md/subcards/' % roots)
    print('  open: %s' % os.path.join(OUT_DIR, 'index.html'))


if __name__ == '__main__':
    main()
