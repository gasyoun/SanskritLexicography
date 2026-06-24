#-*- coding:utf-8 -*-
"""build_affix_explorer.py — emit the interactive Sanskrit-affix teaching explorer.

Reads affix_pedagogy.json and writes:
  affix_explorer.html           standalone page (self-contained; for WhitneyRoots / GH Pages)
  affix_explorer.fragment.html  body fragment (host provides CSS vars; for inline preview)

The explorer: affixes grouped by what they FORM (agent / action / abstract / feminine …),
each with surface suffix, Pāṇinian pratyaya, an Apte-productivity bar, and click-to-expand
anubandha decoding + real example derivatives. Layered — surface on top, Pāṇinian on click.
"""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, 'affix_pedagogy.json'), encoding='utf-8'))

BODY = r'''
<style>
.afx-q .c-teal{background:#E1F5EE;color:#085041;}.afx-q .c-purple{background:#EEEDFE;color:#3C3489;}.afx-q .c-pink{background:#FBEAF0;color:#72243E;}.afx-q .c-gray{background:#F1EFE8;color:#444441;}
@media(prefers-color-scheme:dark){.afx-q .c-teal{background:#085041;color:#9FE1CB;}.afx-q .c-purple{background:#3C3489;color:#CECBF6;}.afx-q .c-pink{background:#72243E;color:#F4C0D1;}.afx-q .c-gray{background:#444441;color:#D3D1C7;}}
</style>
<div class="afx-q">
<h2 class="sr-only">Sanskrit affix explorer: suffixes grouped by what they form, each with productivity, Pāṇinian anubandha decoding, and example derivatives.</h2>
<div style="padding:1rem 0;">
  <input id="afx-q" type="text" placeholder="filter by suffix, function, or pratyaya…" aria-label="filter affixes" style="width:100%; margin-bottom:1rem;"/>
  <div id="afx-root"></div>
  <p style="font-size:12px; color:var(--color-text-tertiary); margin-top:1rem; line-height:1.6;">Bar = Apte productivity (number of distinct roots taking the affix). Click an affix for its anubandha (it-marker) decoding and example derivatives. <span style="color:var(--color-text-secondary);">kṛt</span> = formed from verb roots · <span style="color:var(--color-text-secondary);">taddhita</span> = from nominal stems · <span style="color:var(--color-text-secondary);">strī</span> = feminine.</p>
</div>
<script>
const AFX = __DATA__;
const KIND = {"kṛt":"c-teal","taddhita":"c-purple","strī":"c-pink","taddhita/kṛt":"c-purple"};
const rootEl = document.getElementById('afx-root');
const maxR = Math.max.apply(null, AFX.affixes.map(a=>a.apte_roots));
const groups = {};
AFX.affixes.forEach(a=>{(groups[a.group]=groups[a.group]||[]).push(a);});
const sum = arr => arr.reduce((s,a)=>s+a.apte_roots,0);
const order = Object.keys(groups).sort((x,y)=> sum(groups[y])-sum(groups[x]));
function card(a){
  const c=document.createElement('div');
  c.style.cssText='border:0.5px solid var(--color-border-tertiary); border-radius:var(--border-radius-lg); padding:.6rem .8rem; margin-bottom:8px; cursor:pointer; background:var(--color-background-primary);';
  const pct=Math.round(100*a.apte_roots/maxR);
  c.innerHTML='<div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">'
    +'<span style="font-size:18px; font-weight:500; min-width:58px;">-'+a.surface+'</span>'
    +'<span class="'+(KIND[a.kind]||'c-gray')+'" style="font-size:12px; padding:2px 8px; border-radius:var(--border-radius-md);">'+a.pratyaya_deva+' &nbsp;'+a.pratyaya+'</span>'
    +'<span style="flex:1; min-width:140px; font-size:13px; color:var(--color-text-secondary);">'+a.function+'</span>'
    +'<span style="font-size:12px; color:var(--color-text-tertiary); min-width:60px; text-align:right;">'+a.apte_roots+' roots</span></div>'
    +'<div style="height:4px; background:var(--color-background-secondary); border-radius:2px; margin-top:6px;"><div style="height:4px; width:'+pct+'%; background:var(--color-text-tertiary); border-radius:2px;"></div></div>';
  let det=null;
  c.onclick=function(){
    if(det){det.remove();det=null;return;}
    det=document.createElement('div');
    det.style.cssText='margin-top:10px; border-top:0.5px solid var(--color-border-tertiary); padding-top:8px; font-size:13px; cursor:default;';
    det.onclick=function(e){e.stopPropagation();};
    const steps=a.anubandha.map(s=>'<span style="background:var(--color-background-secondary); padding:2px 8px; border-radius:var(--border-radius-md); margin:0 4px 4px 0; display:inline-block;">'+s+'</span>').join('');
    const ex=a.examples.map(e=>'<span style="margin:0 12px 4px 0; display:inline-block;"><span style="color:var(--color-text-tertiary);">'+e.root+'</span> → <span style="font-weight:500;">'+e.word_iast+'</span></span>').join('') || '<span style="color:var(--color-text-tertiary);">—</span>';
    const mw=a.mw_count? ' · MW surface-suffix headwords: '+a.mw_count : '';
    const dsg=a.dsg_url? ' · <a href="'+a.dsg_url+'" target="_blank" rel="noopener">📖 DSG entry</a>' : '';
    det.innerHTML='<div style="margin-bottom:8px;"><span style="color:var(--color-text-secondary);">Anubandha → surface: </span>'+steps+'</div>'
      +'<div><span style="color:var(--color-text-secondary);">Examples: </span>'+ex+'</div>'
      +'<div style="color:var(--color-text-tertiary); margin-top:8px;">'+a.kind+mw+dsg+'</div>';
    c.appendChild(det);
  };
  return c;
}
function render(filter){
  rootEl.innerHTML='';
  const f=(filter||'').toLowerCase();
  order.forEach(g=>{
    const items=groups[g].filter(a=> !f || (a.surface+a.pratyaya+a.function+a.group).toLowerCase().indexOf(f)>=0).sort((x,y)=>y.apte_roots-x.apte_roots);
    if(!items.length) return;
    const sec=document.createElement('div'); sec.style.margin='0 0 1.25rem';
    const h=document.createElement('h3'); h.textContent=g; h.style.cssText='font-size:15px; font-weight:500; margin:0 0 .5rem;'; sec.appendChild(h);
    items.forEach(a=>sec.appendChild(card(a)));
    rootEl.appendChild(sec);
  });
}
document.getElementById('afx-q').addEventListener('input', e=>render(e.target.value));
render('');
</script>
</div>
'''

frag = BODY.replace('__DATA__', json.dumps(DATA, ensure_ascii=False))

SHELL = '''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Sanskrit affix explorer</title>
<style>
:root{--color-background-primary:#fff;--color-background-secondary:#f4f2ec;--color-text-primary:#1a1a18;--color-text-secondary:#5f5e5a;--color-text-tertiary:#888780;--color-border-tertiary:rgba(0,0,0,.15);--border-radius-md:8px;--border-radius-lg:12px;}
@media(prefers-color-scheme:dark){:root{--color-background-primary:#26261f;--color-background-secondary:#33332a;--color-text-primary:#ece9e0;--color-text-secondary:#b4b2a9;--color-text-tertiary:#888780;--color-border-tertiary:rgba(255,255,255,.15);}}
.c-teal{background:#E1F5EE;color:#085041;}.c-purple{background:#EEEDFE;color:#3C3489;}.c-pink{background:#FBEAF0;color:#72243E;}.c-gray{background:#F1EFE8;color:#444441;}
@media(prefers-color-scheme:dark){.c-teal{background:#085041;color:#9FE1CB;}.c-purple{background:#3C3489;color:#CECBF6;}.c-pink{background:#72243E;color:#F4C0D1;}.c-gray{background:#444441;color:#D3D1C7;}}
body{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;max-width:760px;margin:1.5rem auto;padding:0 1.1rem;color:var(--color-text-primary);background:var(--color-background-primary);line-height:1.6;}
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);}
input{height:36px;padding:0 12px;border:0.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-md);background:var(--color-background-primary);color:var(--color-text-primary);font-size:14px;}
h1{font-size:22px;font-weight:500;}
</style></head><body>
<h1>Sanskrit affixes — what forms what</h1>
<p style="color:var(--color-text-secondary);">An interactive map of the productive Sanskrit suffixes, grouped by what they make, sized by how many roots take them (Apte data), with Pāṇinian anubandha decoding and real examples.</p>
__FRAG__
<p style="font-size:12px;color:var(--color-text-tertiary);margin-top:2rem;">Built from <code>affix_map.tsv</code> + Apte Sanskrit–Hindi productivity. Part of the sanskrit-lexicon / SanskritLexicography project.</p>
</body></html>'''

open(os.path.join(HERE, 'affix_explorer.fragment.html'), 'w', encoding='utf-8').write(frag)
open(os.path.join(HERE, 'affix_explorer.html'), 'w', encoding='utf-8').write(SHELL.replace('__FRAG__', frag))
print('wrote affix_explorer.html (standalone) + affix_explorer.fragment.html (%d affixes)'
      % len(DATA['affixes']))
