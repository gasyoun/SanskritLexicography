#!/usr/bin/env python
"""build_renou_pilot_sheet.py — render the Step-0 pilot review sheet from
renou_pilot_sample.jsonl into a single self-contained HTML file.

Follows the org /review-sheet convention (interactive HTML, never markdown
checkboxes): one card per sample item, approve/reject/defer + free-text note,
running tally, localStorage persistence, "Download decisions.json" export
matching the {sheet_id, generated, decided, items:[{id, decision, note}]}
contract. No server, no CDN — opens from file://.

  python build_renou_pilot_sheet.py [--sample renou_pilot_sample.jsonl]
                                     [--out ../review/renou_pilot_sheet.html]

Computed by Sonnet 5 (claude-sonnet-5).
"""
import html
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET_ID = 'renou-pilot-2026-07-02'

STRATUM_LABEL = {
    'A': 'A — dcs-only states',
    'B': 'B — bhs-only V',
    'C': 'C — maximal-span suspects',
    'D': 'D — single-era dcs_adds',
    'E': 'E — corroborated controls',
}
STATE_NAME = {'I': 'I Vedic', 'II': 'II Pāṇinian', 'III': 'III Epic',
              'IV': 'IV Classical', 'V': 'V Buddhist/Jaina'}


def esc(s):
    return html.escape(str(s) if s is not None else '')


def render_ls_citations(cites):
    if not cites:
        return '<div class="muted">no resolved &lt;ls&gt; citations recovered</div>'
    rows = []
    for c in cites:
        rows.append('<li><b>%s</b> — %s (state %s%s)</li>' % (
            esc(c.get('siglum')), esc(c.get('name')), esc(c.get('state')),
            ', date %s' % c['date'] if c.get('date') is not None else ''))
    return '<ul class="cites">%s</ul>' % ''.join(rows)


def render_dcs_evidence(ev):
    if not ev:
        return '<div class="muted">lemma absent from dcs_lemma_renou.json</div>'
    supp = ev.get('state_support')
    supp_line = ('no support entry for this state (below min-support / filtered)'
                 if not supp else
                 'confidence <b>%s</b>, n=<b>%s</b> texts' % (esc(supp.get('conf')), esc(supp.get('n'))))
    return ('<div>lemma total: <b>%s</b> DCS texts &middot; oldest attestation: '
            '<b>%s</b> (%s) </div><div>this state: %s</div>') % (
        esc(ev.get('n_texts_lemma_total')), esc(ev.get('oldest_text')),
        esc(ev.get('oldest_date')), supp_line)


def render_provenance(prov):
    rows = []
    for st in ('I', 'II', 'III', 'IV', 'V'):
        if st in (prov or {}):
            rows.append('<span class="chip">%s: %s</span>' % (st, '+'.join(prov[st])))
    return ' '.join(rows) or '<span class="muted">none</span>'


def render_card(item):
    iid = esc(item['item_id'])
    stratum = STRATUM_LABEL.get(item['stratum'], item['stratum'])
    hw = esc(item.get('headword_iast') or item.get('headword_key2'))
    key2 = esc(item.get('headword_key2'))
    dic = esc(item['dict'].upper())
    cstate = esc(item['contested_state'])
    cstate_name = esc(STATE_NAME.get(item['contested_state'], item['contested_state']))
    enriched = ' '.join('<span class="chip small">%s</span>' % esc(s)
                         for s in (item.get('renou_enriched') or []))
    question = ('Is state <b>%s</b> (%s) justified for <b>%s</b> — is the word genuinely '
                'attested in that Sanskrit?' % (cstate, cstate_name, hw))
    return '''
  <section class="card" data-id="%s" data-stratum="%s">
    <header>
      <div class="hw">%s <span class="dict-badge">%s</span></div>
      <div class="stratum-badge">%s</div>
    </header>
    <div class="key2">key2: %s</div>
    <div class="question">%s</div>
    <div class="grid">
      <div class="panel">
        <h4>renou_enriched (all states)</h4>
        <div>%s</div>
        <h4>renou_provenance (signal per state)</h4>
        <div>%s</div>
      </div>
      <div class="panel">
        <h4>Resolved &lt;ls&gt; citations</h4>
        %s
      </div>
      <div class="panel">
        <h4>DCS evidence for state %s</h4>
        %s
      </div>
    </div>
    <div class="controls">
      <button class="vote approve" data-vote="approve">&#9989; Approve</button>
      <button class="vote reject" data-vote="reject">&#10060; Reject</button>
      <button class="vote defer" data-vote="defer">&#9208; Defer</button>
      <span class="vote-state">unvoted</span>
    </div>
    <textarea class="note" placeholder="free-text note (optional)"></textarea>
  </section>''' % (iid, esc(item['stratum']), hw, dic, stratum, key2, question,
                    enriched, render_provenance(item.get('renou_provenance')),
                    render_ls_citations(item.get('resolved_ls_citations')), cstate,
                    render_dcs_evidence(item.get('dcs_evidence')))


TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Renou Step-0 pilot review — %(n)d items</title>
<style>
  :root { --bg:#0f1115; --panel:#171a21; --panel2:#1e222b; --text:#e6e6e6; --muted:#9aa0aa;
          --accent:#5b8cff; --ok:#3fb950; --bad:#f85149; --defer:#d29922; --border:#2a2f3a; }
  * { box-sizing: border-box; }
  body { background:var(--bg); color:var(--text); font-family: -apple-system, Segoe UI, Roboto, sans-serif;
         margin:0; padding:0 0 120px 0; }
  header.top { position:sticky; top:0; z-index:10; background:var(--panel); border-bottom:1px solid var(--border);
               padding:14px 20px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;}
  header.top h1 { font-size:16px; margin:0; }
  header.top .sub { color:var(--muted); font-size:12px; }
  .tally { display:flex; gap:14px; font-size:13px; }
  .tally span.count { font-weight:700; }
  .tally .approve { color:var(--ok); } .tally .reject { color:var(--bad); }
  .tally .defer { color:var(--defer); } .tally .unvoted { color:var(--muted); }
  .toolbar { padding:10px 20px; display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
  button.dl { background:var(--accent); color:#fff; border:none; padding:8px 14px; border-radius:6px;
              cursor:pointer; font-size:13px; }
  button.dl:hover { opacity:.9; }
  .filterbar { display:flex; gap:6px; flex-wrap:wrap; }
  .filterbar button { background:var(--panel2); border:1px solid var(--border); color:var(--text);
                       padding:6px 10px; border-radius:14px; font-size:12px; cursor:pointer; }
  .filterbar button.active { border-color:var(--accent); color:var(--accent); }
  main { max-width:980px; margin:0 auto; padding:10px 20px; }
  .card { background:var(--panel); border:1px solid var(--border); border-radius:10px; padding:16px;
          margin-bottom:16px; }
  .card.voted-approve { border-left:4px solid var(--ok); }
  .card.voted-reject { border-left:4px solid var(--bad); }
  .card.voted-defer { border-left:4px solid var(--defer); }
  .card header { display:flex; justify-content:space-between; align-items:baseline; }
  .card .hw { font-size:18px; font-weight:700; }
  .dict-badge { font-size:11px; background:var(--panel2); padding:2px 8px; border-radius:10px;
                margin-left:8px; color:var(--muted); }
  .stratum-badge { font-size:11px; color:var(--muted); }
  .key2 { color:var(--muted); font-size:12px; margin:2px 0 8px; }
  .question { margin:8px 0 12px; font-size:14px; }
  .grid { display:grid; grid-template-columns: 1fr 1fr 1fr; gap:12px; margin-bottom:12px; }
  .panel { background:var(--panel2); border-radius:8px; padding:10px 12px; font-size:13px; }
  .panel h4 { margin:0 0 6px; font-size:11px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); }
  .chip { display:inline-block; background:#263042; border-radius:5px; padding:2px 7px; margin:2px 3px 2px 0;
          font-size:12px; }
  .chip.small { font-size:11px; padding:1px 6px; }
  ul.cites { margin:0; padding-left:18px; }
  ul.cites li { margin-bottom:3px; }
  .muted { color:var(--muted); font-style:italic; }
  .controls { display:flex; align-items:center; gap:8px; }
  button.vote { border:1px solid var(--border); background:var(--panel2); color:var(--text);
                padding:7px 12px; border-radius:6px; cursor:pointer; font-size:13px; }
  button.vote.approve.active { background:var(--ok); border-color:var(--ok); color:#04240b; }
  button.vote.reject.active { background:var(--bad); border-color:var(--bad); color:#2a0a08; }
  button.vote.defer.active { background:var(--defer); border-color:var(--defer); color:#2a1d02; }
  .vote-state { margin-left:6px; font-size:12px; color:var(--muted); }
  textarea.note { width:100%%; margin-top:10px; min-height:44px; background:#11141a; color:var(--text);
                  border:1px solid var(--border); border-radius:6px; padding:8px; font-size:13px;
                  font-family:inherit; resize:vertical; }
  footer.hint { max-width:980px; margin:20px auto; padding:0 20px; color:var(--muted); font-size:12px; }
  kbd { background:#263042; border-radius:4px; padding:1px 5px; font-size:11px; }
</style>
</head>
<body>
<header class="top">
  <div>
    <h1>Renou Step-0 pilot human validation — %(n)d items</h1>
    <div class="sub">Generated %(generated)s &middot; sheet_id <code>%(sheet_id)s</code> &middot;
      strata A(dcs-only) B(bhs-only V) C(maximal-span) D(single-era dcs_adds) E(controls)</div>
  </div>
  <div class="tally" id="tally">
    <span class="approve">&#9989; <span class="count" id="c-approve">0</span></span>
    <span class="reject">&#10060; <span class="count" id="c-reject">0</span></span>
    <span class="defer">&#9208; <span class="count" id="c-defer">0</span></span>
    <span class="unvoted">&#9711; <span class="count" id="c-unvoted">%(n)d</span></span>
  </div>
</header>
<div class="toolbar">
  <button class="dl" id="downloadBtn">Download decisions.json</button>
  <div class="filterbar" id="filterbar">
    <button data-filter="all" class="active">all</button>
    <button data-filter="A">A</button>
    <button data-filter="B">B</button>
    <button data-filter="C">C</button>
    <button data-filter="D">D</button>
    <button data-filter="E">E</button>
    <button data-filter="unvoted">unvoted only</button>
  </div>
</div>
<main id="cards">
%(cards)s
</main>
<footer class="hint">
  Judgment question per item: is the contested state genuinely attested for this
  headword in that era of Sanskrit? Approve = justified &middot; Reject = over-tag
  &middot; Defer = can't tell from the evidence shown. Keyboard: <kbd>a</kbd> approve
  &middot; <kbd>r</kbd> reject &middot; <kbd>d</kbd> defer &middot; <kbd>&darr;</kbd>/<kbd>&uarr;</kbd>
  next/prev card. Votes autosave to this browser's localStorage as you click;
  click "Download decisions.json" when done (or partway — unvoted items are
  included with decision:null).
</footer>
<script>
(function () {
  var SHEET_ID = %(sheet_id_json)s;
  var STORE_KEY = 'review-sheet:' + SHEET_ID;
  var ids = %(ids_json)s;
  var state = {};
  try {
    var saved = JSON.parse(localStorage.getItem(STORE_KEY) || '{}');
    state = saved || {};
  } catch (e) { state = {}; }

  function tally() {
    var c = { approve: 0, reject: 0, defer: 0 };
    ids.forEach(function (id) {
      var v = state[id] && state[id].decision;
      if (v && c.hasOwnProperty(v)) c[v]++;
    });
    document.getElementById('c-approve').textContent = c.approve;
    document.getElementById('c-reject').textContent = c.reject;
    document.getElementById('c-defer').textContent = c.defer;
    document.getElementById('c-unvoted').textContent = ids.length - c.approve - c.reject - c.defer;
  }

  function applyCardUI(card) {
    var id = card.getAttribute('data-id');
    var rec = state[id] || {};
    card.classList.remove('voted-approve', 'voted-reject', 'voted-defer');
    var buttons = card.querySelectorAll('button.vote');
    buttons.forEach(function (b) { b.classList.toggle('active', b.getAttribute('data-vote') === rec.decision); });
    var label = card.querySelector('.vote-state');
    label.textContent = rec.decision ? rec.decision : 'unvoted';
    if (rec.decision) card.classList.add('voted-' + rec.decision);
    var ta = card.querySelector('textarea.note');
    if (rec.note && !ta.value) ta.value = rec.note;
  }

  function save() {
    localStorage.setItem(STORE_KEY, JSON.stringify(state));
    tally();
  }

  function vote(id, decision) {
    state[id] = state[id] || {};
    state[id].decision = decision;
    save();
  }

  function noteChange(id, text) {
    state[id] = state[id] || {};
    state[id].note = text;
    save();
  }

  document.querySelectorAll('.card').forEach(function (card) {
    var id = card.getAttribute('data-id');
    applyCardUI(card);
    card.querySelectorAll('button.vote').forEach(function (btn) {
      btn.addEventListener('click', function () {
        vote(id, btn.getAttribute('data-vote'));
        applyCardUI(card);
      });
    });
    var ta = card.querySelector('textarea.note');
    ta.addEventListener('input', function () { noteChange(id, ta.value); });
  });

  tally();

  document.getElementById('downloadBtn').addEventListener('click', function () {
    var decided = ids.filter(function (id) { return state[id] && state[id].decision; }).length;
    var payload = {
      sheet_id: SHEET_ID,
      generated: %(generated_json)s,
      decided: decided,
      items: ids.map(function (id) {
        var rec = state[id] || {};
        return { id: id, decision: rec.decision || null, note: rec.note || '' };
      })
    };
    var blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'decisions.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });

  // filters
  var filterbar = document.getElementById('filterbar');
  filterbar.addEventListener('click', function (e) {
    var btn = e.target.closest('button[data-filter]');
    if (!btn) return;
    filterbar.querySelectorAll('button').forEach(function (b) { b.classList.remove('active'); });
    btn.classList.add('active');
    var f = btn.getAttribute('data-filter');
    document.querySelectorAll('.card').forEach(function (card) {
      var show = true;
      if (f === 'unvoted') {
        var id = card.getAttribute('data-id');
        show = !(state[id] && state[id].decision);
      } else if (f !== 'all') {
        show = card.getAttribute('data-stratum') === f;
      }
      card.style.display = show ? '' : 'none';
    });
  });

  // keyboard shortcuts on the currently-focused / nearest-in-view card
  var cardsEl = Array.prototype.slice.call(document.querySelectorAll('.card'));
  var activeIdx = 0;
  function visibleCards() {
    return cardsEl.filter(function (c) { return c.style.display !== 'none'; });
  }
  function scrollToCard(card) {
    if (card) card.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
  document.addEventListener('keydown', function (e) {
    if (e.target.tagName === 'TEXTAREA') return;
    var vis = visibleCards();
    if (!vis.length) return;
    if (activeIdx >= vis.length) activeIdx = vis.length - 1;
    var card = vis[activeIdx];
    var id = card.getAttribute('data-id');
    if (e.key === 'a') { vote(id, 'approve'); applyCardUI(card); }
    else if (e.key === 'r') { vote(id, 'reject'); applyCardUI(card); }
    else if (e.key === 'd') { vote(id, 'defer'); applyCardUI(card); }
    else if (e.key === 'ArrowDown') { activeIdx = Math.min(activeIdx + 1, vis.length - 1); scrollToCard(vis[activeIdx]); }
    else if (e.key === 'ArrowUp') { activeIdx = Math.max(activeIdx - 1, 0); scrollToCard(vis[activeIdx]); }
    else return;
    e.preventDefault();
  });
})();
</script>
</body>
</html>
'''


def main():
    args = sys.argv[1:]
    sample_path = os.path.join(HERE, 'renou_pilot_sample.jsonl')
    out_path = os.path.normpath(os.path.join(HERE, '..', 'review', 'renou_pilot_sheet.html'))
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--sample':
            sample_path = args[i + 1]; i += 2
        elif a == '--out':
            out_path = args[i + 1]; i += 2
        else:
            raise SystemExit('unknown option: %s' % a)

    items = [json.loads(line) for line in open(sample_path, encoding='utf-8') if line.strip()]
    cards_html = '\n'.join(render_card(it) for it in items)
    ids = [it['item_id'] for it in items]
    generated = '2026-07-02'

    doc = TEMPLATE % {
        'n': len(items),
        'generated': generated,
        'sheet_id': SHEET_ID,
        'cards': cards_html,
        'sheet_id_json': json.dumps(SHEET_ID),
        'ids_json': json.dumps(ids),
        'generated_json': json.dumps(generated),
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(doc)
    print('wrote %d cards -> %s' % (len(items), out_path))


if __name__ == '__main__':
    main()
