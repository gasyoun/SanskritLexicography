#-*- coding:utf-8 -*-
"""build_affix_teaching.py — derive a printable poster, an interactive quiz, and an
Anki-importable flashcard deck from affix_pedagogy.json (one source → three teaching artifacts).

  python build_affix_teaching.py
    -> affix_poster.html      print-optimized one-page wall chart (light theme, @page)
    -> affix_quiz.html        self-contained MCQ drill (generates questions from the data)
    -> affix_flashcards.tsv   front<TAB>back, ready to import into Anki / Quizlet
"""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'affix_pedagogy.json'), encoding='utf-8'))
AFX = D['affixes']

# stable group order by total productivity
groups = {}
for a in AFX:
    groups.setdefault(a['group'], []).append(a)
order = sorted(groups, key=lambda g: -sum(x['apte_roots'] for x in groups[g]))

# ---------------------------------------------------------------- poster
rows = []
for g in order:
    items = sorted(groups[g], key=lambda x: -x['apte_roots'])
    cells = []
    for a in items:
        ex = a['examples'][0]['word_iast'] if a['examples'] else ''
        cells.append(
            '<div class="row"><span class="sfx">-%s</span>'
            '<span class="pr">%s %s</span>'
            '<span class="fn">%s</span>'
            '<span class="rc">%d</span>'
            '<span class="ex">%s</span></div>'
            % (a['surface'], a['pratyaya_deva'], a['pratyaya'], a['function'], a['apte_roots'], ex))
    rows.append('<section class="grp"><h2>%s</h2>%s</section>' % (g, ''.join(cells)))

POSTER = '''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
<title>Sanskrit affixes — wall chart</title>
<style>
@page { size: A4 landscape; margin: 10mm; }
body { font-family: "Segoe UI", system-ui, sans-serif; color: #1a1a18; background: #fff; margin: 14px; }
h1 { font-size: 20px; margin: 0 0 2px; }
.sub { color: #5f5e5a; font-size: 11px; margin: 0 0 10px; }
.cols { column-count: 3; column-gap: 14px; }
.grp { break-inside: avoid; border: 0.5px solid #d3d1c7; border-radius: 6px; padding: 6px 8px; margin: 0 0 10px; }
.grp h2 { font-size: 12px; color: #534ab7; margin: 0 0 4px; border-bottom: 0.5px solid #eee; padding-bottom: 2px; }
.row { display: grid; grid-template-columns: 38px 64px 1fr 22px; gap: 4px; align-items: baseline; font-size: 10px; padding: 1px 0; }
.sfx { font-weight: 600; font-size: 12px; }
.pr { color: #3c3489; }
.fn { color: #444; }
.rc { color: #888; text-align: right; }
.ex { grid-column: 1 / -1; color: #777; font-style: italic; font-size: 9.5px; margin: 0 0 1px 38px; }
@media print { .grp { border-color: #bbb; } }
</style></head><body>
<h1>Sanskrit affixes — what forms what</h1>
<p class="sub">Grouped by function · the number = Apte productivity (distinct roots taking the affix) · surface suffix ← Pāṇinian pratyaya · one example each. Built from affix_map.tsv.</p>
<div class="cols">%s</div>
</body></html>''' % ''.join(rows)

# ---------------------------------------------------------------- quiz (data-driven MCQ)
QUIZ = '''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Sanskrit affix quiz</title>
<style>
:root{--bg:#fff;--fg:#1a1a18;--mut:#5f5e5a;--card:#f7f5ef;--line:rgba(0,0,0,.15);--ok:#0f6e56;--no:#a32d2d;--acc:#534ab7;}
@media(prefers-color-scheme:dark){:root{--bg:#26261f;--fg:#ece9e0;--mut:#b4b2a9;--card:#33332a;--line:rgba(255,255,255,.15);--ok:#5dcaa5;--no:#f09595;--acc:#afa9ec;}}
body{font-family:system-ui,"Segoe UI",sans-serif;max-width:620px;margin:1.5rem auto;padding:0 1rem;background:var(--bg);color:var(--fg);line-height:1.5;}
h1{font-size:20px;font-weight:600;}
#score{color:var(--mut);font-size:14px;margin-bottom:1rem;}
#q{font-size:18px;margin:1rem 0;}
.opt{display:block;width:100%;text-align:left;padding:11px 14px;margin:7px 0;border:1px solid var(--line);border-radius:9px;background:var(--card);color:var(--fg);font-size:15px;cursor:pointer;}
.opt:hover{border-color:var(--acc);}
.opt.ok{border-color:var(--ok);color:var(--ok);}
.opt.no{border-color:var(--no);color:var(--no);}
#next{margin-top:1rem;padding:9px 18px;border:1px solid var(--line);border-radius:9px;background:transparent;color:var(--fg);font-size:15px;cursor:pointer;}
#fb{min-height:22px;color:var(--mut);font-size:14px;margin-top:8px;}
.k{color:var(--acc);}
</style></head><body>
<h1>Sanskrit affix quiz</h1>
<div id="score"></div><div id="q"></div><div id="opts"></div><div id="fb"></div>
<button id="next">Next →</button>
<script>
const AFX = __DATA__.affixes;
let n=0, ok=0, answered=false;
const rnd=a=>a[Math.floor(Math.random()*a.length)];
function sample(pool,k,not){const s=new Set();while(s.size<k&&s.size<pool.length){const x=rnd(pool);if(x!==not&&!s.has(x))s.add(x);}return [...s];}
function make(){
  const a=rnd(AFX), t=Math.floor(Math.random()*3);
  if(t===0){ // function -> which surface suffix
    const opts=sample(AFX,3,a).map(x=>x.surface); opts.push(a.surface);
    return {q:'Which suffix forms: <span class="k">'+a.function+'</span>?', opts:shuf(opts), ans:a.surface, fmt:s=>'-'+s};
  } else if(t===1){ // pratyaya -> surface
    const opts=sample(AFX,3,a).map(x=>x.surface); opts.push(a.surface);
    return {q:'The pratyaya <span class="k">'+a.pratyaya_deva+' ('+a.pratyaya+')</span> becomes which surface suffix?', opts:shuf(opts), ans:a.surface, fmt:s=>'-'+s};
  } else { // surface -> function
    const fns=[...new Set(AFX.map(x=>x.function))];
    const opts=sample(fns.map(f=>({surface:f})),3,{surface:a.function}).map(x=>x.surface); opts.push(a.function);
    return {q:'What does <span class="k">-'+a.surface+'</span> ('+a.pratyaya+') form?', opts:shuf([...new Set(opts)]), ans:a.function, fmt:s=>s, ex:a};
  }
}
function shuf(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
let cur;
function render(){
  answered=false; cur=make();
  document.getElementById('score').textContent='Score: '+ok+' / '+n;
  document.getElementById('q').innerHTML=cur.q;
  document.getElementById('fb').textContent='';
  const box=document.getElementById('opts'); box.innerHTML='';
  cur.opts.forEach(o=>{const b=document.createElement('button');b.className='opt';b.innerHTML=cur.fmt(o);b.onclick=()=>pick(b,o);box.appendChild(b);});
}
function pick(btn,o){
  if(answered)return; answered=true; n++;
  const right=o===cur.ans;
  if(right){ok++;btn.classList.add('ok');}
  else{btn.classList.add('no');[...document.querySelectorAll('.opt')].forEach(b=>{if(b.innerHTML===cur.fmt(cur.ans))b.classList.add('ok');});}
  document.getElementById('score').textContent='Score: '+ok+' / '+n;
  const a=cur.ex||AFX.find(x=>x.surface===cur.ans)||{};
  const ex=(a.examples&&a.examples[0])?(' · e.g. '+a.examples[0].word_iast):'';
  document.getElementById('fb').innerHTML=(right?'✓ ':'✗ ')+(a.anubandha?a.anubandha.join(' '):'')+ex;
}
document.getElementById('next').onclick=render;
render();
</script></body></html>'''.replace('__DATA__', json.dumps({'affixes': AFX}, ensure_ascii=False))

# ---------------------------------------------------------------- flashcards (Anki TSV)
cards = []
for a in AFX:
    ex = ', '.join(e['word_iast'] for e in a['examples'][:3])
    front = '%s (%s) →' % (a['pratyaya_deva'], a['pratyaya'])
    back = '-%s · %s · %s%s%s' % (a['surface'], a['function'], ' '.join(a['anubandha']),
                                  ('  ⟨e.g. ' + ex + '⟩') if ex else '',
                                  ('  ' + a['dsg_url']) if a.get('dsg_url') else '')
    cards.append('%s\t%s' % (front, back))

open(os.path.join(HERE, 'affix_poster.html'), 'w', encoding='utf-8').write(POSTER)
open(os.path.join(HERE, 'affix_quiz.html'), 'w', encoding='utf-8').write(QUIZ)
open(os.path.join(HERE, 'affix_flashcards.tsv'), 'w', encoding='utf-8').write('\n'.join(cards) + '\n')
print('wrote affix_poster.html, affix_quiz.html, affix_flashcards.tsv (%d affixes / %d cards)'
      % (len(AFX), len(cards)))
