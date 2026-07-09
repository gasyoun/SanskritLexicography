import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
import gzip, json, html, re, os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(HERE, 'crosswalk_candidates.jsonl.gz')
OUT_HTML = os.path.join(REPO_ROOT, 'review', 'sanskritlexicography-acc_ncc_p2_c_d_review.html')
SHEET_ID = 'sanskritlexicography-acc_ncc_p2_c_d_review'

def trim_html(body, maxlen=280):
    if not body:
        return ''
    text = re.sub(r'<[^>]+>', ' ', body)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > maxlen:
        text = text[:maxlen].rsplit(' ', 1)[0] + '…'
    return text

rows = []
with gzip.open(SRC, 'rt', encoding='utf-8') as f:
    for line in f:
        r = json.loads(line)
        if r['tier'] not in ('C', 'D'):
            continue
        rid = f"{r['acc_L']}__{r['ncc_id']}"
        rows.append({
            'id': rid,
            'tier': r['tier'],
            'score': round(r['score'], 3),
            'acc_L': r['acc_L'],
            'ncc_id': r['ncc_id'],
            'acc_key': r['acc_match_key'],
            'ncc_key': r['ncc_match_key'],
            'acc_slp1': r['acc_k1_slp1'],
            'acc_body': r['acc_body'],
            'ncc_iast': r['ncc_iast'],
            'ncc_deva': r['ncc_deva'],
            'ncc_snip': trim_html(r.get('ncc_body_html', '')),
        })

# Deterministic order: Tier C first (smaller, higher precision), then Tier D by score desc
rows.sort(key=lambda r: (0 if r['tier'] == 'C' else 1, -r['score']))

print(f"Total C+D rows: {len(rows)}", file=sys.stderr)

data_json = json.dumps(rows, ensure_ascii=False, separators=(',', ':'))
print(f"Embedded data size: {len(data_json)/1e6:.1f} MB", file=sys.stderr)

TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ACC×NCC P2 — Tier C/D adjudication</title>
<style>
  :root { color-scheme: light dark; }
  * { box-sizing: border-box; }
  body { font-family: system-ui, sans-serif; margin: 0; padding: 0; background: #f4f4f6; color: #1a1a1a; }
  @media (prefers-color-scheme: dark) { body { background: #17181c; color: #e8e8ea; } }
  header { position: sticky; top: 0; z-index: 10; background: #20242c; color: #fff; padding: 10px 16px; display: flex; gap: 16px; align-items: center; flex-wrap: wrap; font-size: 14px; }
  header h1 { font-size: 15px; margin: 0; font-weight: 600; }
  #tally { display: flex; gap: 10px; margin-left: auto; font-variant-numeric: tabular-nums; }
  #tally span { padding: 2px 8px; border-radius: 10px; background: #2e333d; }
  #tally .acc { background: #1f5c34; } #tally .rej { background: #6b1f1f; } #tally .def { background: #5c4a1f; } #tally .unv { background: #333; }
  #controls { display: flex; gap: 8px; align-items: center; }
  #controls input[type=text] { padding: 4px 8px; border-radius: 4px; border: 1px solid #444; width: 160px; }
  #controls select { padding: 4px 6px; border-radius: 4px; }
  #downloadBtn { background: #3a7; color: #fff; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: 600; }
  #downloadBtn:hover { background: #2c6; }
  #scrollHost { height: calc(100vh - 52px); overflow-y: auto; position: relative; }
  #spacer { position: relative; width: 100%; }
  .row { position: absolute; left: 0; right: 0; display: grid; grid-template-columns: 70px 1fr 1fr 210px; gap: 10px; padding: 8px 16px; border-bottom: 1px solid #ddd; align-items: start; }
  @media (prefers-color-scheme: dark) { .row { border-bottom-color: #333; } }
  .row.voted-approve { background: rgba(46,160,67,0.12); }
  .row.voted-reject { background: rgba(200,40,40,0.12); }
  .row.voted-defer { background: rgba(200,160,40,0.12); }
  .row .meta { font-size: 12px; opacity: 0.75; line-height: 1.5; }
  .row .acc-col b, .row .ncc-col b { font-size: 14px; }
  .row .acc-col, .row .ncc-col { font-size: 12.5px; line-height: 1.4; overflow-wrap: break-word; }
  .row .snip { opacity: 0.85; }
  .row .actions { display: flex; flex-direction: column; gap: 4px; }
  .row .actions .btns { display: flex; gap: 4px; }
  .row button { cursor: pointer; border: 1px solid #999; background: #fff; border-radius: 4px; padding: 3px 8px; font-size: 12px; }
  @media (prefers-color-scheme: dark) { .row button { background: #24262b; color: #eee; border-color: #555; } }
  .row button.active-approve { background: #2ea043; color: #fff; border-color: #2ea043; }
  .row button.active-reject { background: #c82828; color: #fff; border-color: #c82828; }
  .row button.active-defer { background: #c8a028; color: #fff; border-color: #c8a028; }
  .row .note { width: 100%; font-size: 11px; padding: 2px 4px; }
  #jump { display: flex; gap: 4px; align-items: center; }
  #hint { font-size: 11px; opacity: 0.7; }
</style>
</head>
<body>
<header>
  <h1>ACC×NCC P2 — Tier C/D adjudication (__ROWCOUNT__ rows)</h1>
  <div id="controls">
    <select id="filterTier"><option value="">all tiers</option><option value="C">Tier C</option><option value="D">Tier D</option></select>
    <select id="filterVote"><option value="">all votes</option><option value="unvoted">unvoted</option><option value="approve">approved</option><option value="reject">rejected</option><option value="defer">deferred</option></select>
    <input type="text" id="searchBox" placeholder="filter acc/ncc key…">
    <div id="jump"><span id="hint">a/r/d = vote focused row</span></div>
  </div>
  <div id="tally">
    <span class="acc">✅ <span id="cApprove">0</span></span>
    <span class="rej">❌ <span id="cReject">0</span></span>
    <span class="def">⏸ <span id="cDefer">0</span></span>
    <span class="unv">— <span id="cUnvoted">__ROWCOUNT__</span></span>
  </div>
  <button id="downloadBtn">Download decisions.json</button>
</header>
<div id="scrollHost">
  <div id="spacer"></div>
</div>
<script>
const SHEET_ID = "__SHEET_ID__";
const DATA = __DATA_JSON__;
const ROW_HEIGHT = 92;
const STORE_KEY = "reviewsheet_" + SHEET_ID;

let decisions = {};
try {
  const saved = JSON.parse(localStorage.getItem(STORE_KEY) || "{}");
  decisions = saved;
} catch (e) { decisions = {}; }

let filtered = DATA;
let focusedIdx = -1;

const scrollHost = document.getElementById('scrollHost');
const spacer = document.getElementById('spacer');
const filterTier = document.getElementById('filterTier');
const filterVote = document.getElementById('filterVote');
const searchBox = document.getElementById('searchBox');

function escapeHtml(s) {
  return (s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function applyFilters() {
  const t = filterTier.value;
  const v = filterVote.value;
  const q = searchBox.value.trim().toLowerCase();
  filtered = DATA.filter(r => {
    if (t && r.tier !== t) return false;
    const dec = decisions[r.id] && decisions[r.id].decision;
    if (v === 'unvoted' && dec) return false;
    if (v && v !== 'unvoted' && dec !== v) return false;
    if (q && !(r.acc_key.toLowerCase().includes(q) || r.ncc_key.toLowerCase().includes(q))) return false;
    return true;
  });
  spacer.style.height = (filtered.length * ROW_HEIGHT) + 'px';
  renderVisible();
}

function rowHtml(r, idx) {
  const dec = decisions[r.id] || {};
  const cls = dec.decision ? ('voted-' + dec.decision) : '';
  const note = dec.note || '';
  return `<div class="row ${cls}" data-idx="${idx}" data-id="${r.id}" style="top:${idx * ROW_HEIGHT}px; height:${ROW_HEIGHT}px;">
    <div class="meta">tier ${r.tier}<br>score ${r.score}<br><span style="opacity:.6">${escapeHtml(r.acc_L)}</span></div>
    <div class="acc-col"><b>${escapeHtml(r.acc_slp1)}</b><br>${escapeHtml((r.acc_body||'').slice(0,220))}</div>
    <div class="ncc-col"><b>${escapeHtml(r.ncc_iast)}</b> <span style="opacity:.7">${escapeHtml(r.ncc_deva)}</span><br><span class="snip">${escapeHtml(r.ncc_snip)}</span></div>
    <div class="actions">
      <div class="btns">
        <button data-act="approve" class="${dec.decision==='approve'?'active-approve':''}">✅</button>
        <button data-act="reject" class="${dec.decision==='reject'?'active-reject':''}">❌</button>
        <button data-act="defer" class="${dec.decision==='defer'?'active-defer':''}">⏸</button>
      </div>
      <input class="note" type="text" placeholder="note" value="${escapeHtml(note)}">
    </div>
  </div>`;
}

function renderVisible() {
  const scrollTop = scrollHost.scrollTop;
  const viewH = scrollHost.clientHeight;
  const startIdx = Math.max(0, Math.floor(scrollTop / ROW_HEIGHT) - 5);
  const endIdx = Math.min(filtered.length, Math.ceil((scrollTop + viewH) / ROW_HEIGHT) + 5);
  let buf = '';
  for (let i = startIdx; i < endIdx; i++) {
    buf += rowHtml(filtered[i], i);
  }
  spacer.innerHTML = buf;
}

function vote(id, act) {
  const existing = decisions[id] || {};
  if (existing.decision === act) {
    delete decisions[id];
  } else {
    decisions[id] = { decision: act, note: existing.note || '' };
  }
  persist();
  updateTally();
  renderVisible();
}

function setNote(id, note) {
  if (!decisions[id]) decisions[id] = { decision: null, note: '' };
  decisions[id].note = note;
  persist();
}

function persist() {
  localStorage.setItem(STORE_KEY, JSON.stringify(decisions));
}

function updateTally() {
  let a=0,r=0,d=0;
  for (const k in decisions) {
    const dec = decisions[k].decision;
    if (dec === 'approve') a++;
    else if (dec === 'reject') r++;
    else if (dec === 'defer') d++;
  }
  document.getElementById('cApprove').textContent = a;
  document.getElementById('cReject').textContent = r;
  document.getElementById('cDefer').textContent = d;
  document.getElementById('cUnvoted').textContent = DATA.length - a - r - d;
}

scrollHost.addEventListener('scroll', () => window.requestAnimationFrame(renderVisible));
window.addEventListener('resize', renderVisible);

spacer.addEventListener('click', (e) => {
  const btn = e.target.closest('button');
  if (btn) {
    const rowEl = e.target.closest('.row');
    vote(rowEl.dataset.id, btn.dataset.act);
    focusedIdx = parseInt(rowEl.dataset.idx, 10);
    return;
  }
  const rowEl = e.target.closest('.row');
  if (rowEl) focusedIdx = parseInt(rowEl.dataset.idx, 10);
});
spacer.addEventListener('change', (e) => {
  if (e.target.classList.contains('note')) {
    const rowEl = e.target.closest('.row');
    setNote(rowEl.dataset.id, e.target.value);
  }
});

document.addEventListener('keydown', (e) => {
  if (document.activeElement && document.activeElement.tagName === 'INPUT') return;
  if (focusedIdx < 0) return;
  const row = filtered[focusedIdx];
  if (!row) return;
  if (e.key === 'a') vote(row.id, 'approve');
  else if (e.key === 'r') vote(row.id, 'reject');
  else if (e.key === 'd') vote(row.id, 'defer');
  else if (e.key === 'ArrowDown') { focusedIdx = Math.min(filtered.length - 1, focusedIdx + 1); scrollHost.scrollTop = focusedIdx * ROW_HEIGHT - 100; }
  else if (e.key === 'ArrowUp') { focusedIdx = Math.max(0, focusedIdx - 1); scrollHost.scrollTop = focusedIdx * ROW_HEIGHT - 100; }
});

filterTier.addEventListener('change', applyFilters);
filterVote.addEventListener('change', applyFilters);
searchBox.addEventListener('input', applyFilters);

document.getElementById('downloadBtn').addEventListener('click', () => {
  const items = DATA.map(r => ({
    id: r.id,
    decision: (decisions[r.id] && decisions[r.id].decision) || null,
    note: (decisions[r.id] && decisions[r.id].note) || ''
  }));
  const payload = { sheet_id: SHEET_ID, generated: new Date().toISOString(), decided: Object.keys(decisions).length, items };
  const blob = new Blob([JSON.stringify(payload, null, 1)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = SHEET_ID + '_decisions.json';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
});

applyFilters();
updateTally();
</script>
</body>
</html>
'''

out = (TEMPLATE
       .replace('__ROWCOUNT__', str(len(rows)))
       .replace('__SHEET_ID__', SHEET_ID)
       .replace('__DATA_JSON__', data_json))

os.makedirs(os.path.dirname(OUT_HTML), exist_ok=True)
with open(OUT_HTML, 'w', encoding='utf-8') as f:
    f.write(out)

print(f"Wrote {OUT_HTML} ({len(out)/1e6:.1f} MB)", file=sys.stderr)
