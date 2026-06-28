let refreshMs = 5000;
let timer = null;

const $ = (id) => document.getElementById(id);

function esc(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function chipClass(state) {
  const s = String(state || '').toLowerCase();
  if (['clean', 'ready', 'ok', 'passing', 'ready-to-cut', 'report-present'].includes(s)) return 'good';
  if (['stale_artifact', 'blocked', 'fail', 'failed', 'gate_failed', 'crashed'].includes(s)) return 'bad';
  if (['needs_requeue', 'partial', 'warn', 'warning'].includes(s)) return 'warn';
  return 'neutral';
}

function chip(label, state) {
  const text = label || state || 'not available yet';
  return `<span class="chip ${chipClass(state || label)}">${esc(text)}</span>`;
}

function formatAge(seconds) {
  if (seconds === null || seconds === undefined) return '--';
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  const hours = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  return `${hours}h ${mins}m`;
}

function metric(label, value) {
  return `<div class="metric"><div class="label">${esc(label)}</div><div class="value">${esc(value ?? '--')}</div></div>`;
}

function compact(value) {
  if (value === true) return 'yes';
  if (value === false) return 'no';
  if (value === null || value === undefined || value === '') return '--';
  return value;
}

function table(headers, rows) {
  if (!rows || rows.length === 0) return '<div class="note">not available yet</div>';
  return `<table><thead><tr>${headers.map(h => `<th>${esc(h)}</th>`).join('')}</tr></thead><tbody>${
    rows.map(row => `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`).join('')
  }</tbody></table>`;
}

function renderRun(data) {
  const s = data.run_status;
  if (!s || s._error) {
    $('runChip').outerHTML = chip('not available yet', 'neutral').replace('<span', '<span id="runChip"');
    $('runMetrics').innerHTML = metric('State', 'not available yet') + metric('Workflow keys', '--') + metric('Requeue', '--');
    $('nextAction').innerHTML = '<b>Next action:</b> not available yet';
    $('queueSummary').innerHTML = '<div class="note">not available yet</div>';
    $('productionMetrics').innerHTML = '<div class="note">not available yet</div>';
    $('gateTable').innerHTML = '<div class="note">not available yet</div>';
    $('staleErrors').textContent = s && s._error ? s._error : 'not available yet';
    return;
  }
  $('runChip').outerHTML = chip(s.state, s.state).replace('<span', '<span id="runChip"');
  $('runMetrics').innerHTML = [
    metric('Current root', s.root || '--'),
    metric('State', s.state || '--'),
    metric('Workflow keys', s.workflow_keys),
    metric('Root subcards', s.root_subcards),
    metric('Translated', s.translated),
    metric('Pending', s.pending),
    metric('Requeue', s.requeue_count),
    metric('Clean keys', s.clean_key_count),
    metric('Judge sample', s.judge_sample_count),
    metric('Recorded', s.recorded_at || '--')
  ].join('');
  $('nextAction').innerHTML = `<b>Next action:</b> ${esc(s.next_action || 'not available yet')}`;
  $('queueSummary').innerHTML = table(['Queue', 'Count', 'Source'], [
    ['mechanical requeue', esc((data.requeue_keys || []).length), '<span class="mono">requeue.keys.txt</span>'],
    ['semantic sample', esc((data.judge_sample_keys || []).length), '<span class="mono">judge_sample.keys.txt</span>']
  ]);
  const pm = s.production_metrics || {};
  const metricRows = Object.entries(pm).map(([k, v]) => [esc(k), esc(compact(v))]);
  $('productionMetrics').innerHTML = metricRows.length
    ? table(['Metric', 'Value'], metricRows)
    : '<div class="note">No Max token/time metrics recorded for this window yet.</div>';
  const gates = Object.entries(s.gates || {}).map(([name, g]) => [
    esc(name),
    chip(g.returncode === 0 ? 'pass' : `exit ${g.returncode}`, g.returncode === 0 ? 'clean' : 'needs_requeue'),
    esc(g.requeue_count ?? 0),
    esc(g.seconds ?? '--')
  ]);
  $('gateTable').innerHTML = table(['Gate', 'Status', 'Requeue', 'Seconds'], gates);
  const errors = (((s.stale_check || {}).errors) || []).slice(0, 8);
  $('staleErrors').innerHTML = errors.length
    ? `<ul>${errors.map(e => `<li>${esc(e)}</li>`).join('')}</ul>`
    : 'No stale errors recorded in the latest status.';
}

function printGateStatus(key, gate) {
  if (!gate) return ['not available yet', 'neutral'];
  if (key.startsWith('G5')) return [gate.print_ready_rows > 0 ? 'partial' : 'blocked', gate.print_ready_rows > 0 ? 'partial' : 'blocked'];
  if (key.startsWith('G6')) return [gate.rows && gate.complete >= gate.rows ? 'ready' : 'blocked', gate.rows && gate.complete >= gate.rows ? 'ready' : 'blocked'];
  if (key.startsWith('G7')) return [gate.agreement_report_exists ? 'report-present' : 'blocked', gate.agreement_report_exists ? 'report-present' : 'blocked'];
  if (key.startsWith('G10')) return [gate.ready_to_cut ? 'ready-to-cut' : 'blocked', gate.ready_to_cut ? 'ready-to-cut' : 'blocked'];
  return ['unknown', 'neutral'];
}

function renderPrint(data) {
  const pg = data.print_gates;
  if (!pg || pg._error) {
    $('printChip').outerHTML = chip('not available yet', 'neutral').replace('<span', '<span id="printChip"');
    $('printGates').innerHTML = '<div class="note">not available yet</div>';
    return;
  }
  const gates = pg.gates || {};
  const anyBlocked = Object.entries(gates).some(([k, g]) => printGateStatus(k, g)[1] === 'blocked');
  $('printChip').outerHTML = chip(anyBlocked ? 'blocked' : 'ready', anyBlocked ? 'blocked' : 'ready').replace('<span', '<span id="printChip"');
  const blocks = Object.entries(gates).map(([key, g]) => {
    const [label, state] = printGateStatus(key, g);
    let rows = [];
    if (key.startsWith('G5')) rows = [
      ['review rows', g.rows], ['decisions', g.decisions], ['print-ready rows', g.print_ready_rows]
    ];
    if (key.startsWith('G6')) rows = [
      ['gold rows', g.rows], ['complete', g.complete], ['labels jsonl', g.labels_jsonl_rows]
    ];
    if (key.startsWith('G7')) rows = [
      ['queue rows', g.queue_rows], ['complete', g.complete], ['labels jsonl', g.labels_jsonl_rows], ['agreement report', g.agreement_report_exists ? 'yes' : 'no']
    ];
    if (key.startsWith('G10')) rows = [
      ['latest edition', g.latest_edition || 'none'], ['ready to cut', g.ready_to_cut ? 'yes' : 'no'], ['blockers', (g.blocked_by || []).join(', ') || 'none']
    ];
    return `<div class="gate-block"><div class="gate-title"><h3>${esc(key.replaceAll('_', ' '))}</h3>${chip(label, state)}</div>${
      table(['Metric', 'Value'], rows.map(([a, b]) => [esc(a), esc(b)]))
    }</div>`;
  });
  $('printGates').innerHTML = blocks.join('') || '<div class="note">not available yet</div>';
}

function renderEvents(data) {
  const events = (data.events || []).slice().reverse();
  $('eventCount').textContent = `${events.length} shown`;
  $('events').innerHTML = events.length ? events.map(e => `
    <div class="event-row">
      <div class="mono">${esc(e.ts || '--')}</div>
      <div>${chip(e.level || 'info', e.level || 'info')}</div>
      <div class="mono">${esc(e.type || '--')}</div>
      <div><b>${esc(e.source || '--')}</b> ${esc(e.summary || '')}</div>
    </div>`).join('') : '<div class="note">not available yet</div>';
}

function renderLedger(data) {
  const ledger = (data.ledger || []).slice().reverse();
  $('ledgerCount').textContent = `${ledger.length} shown`;
  const rows = ledger.map(r => [
    esc(r.recorded_at || '--'),
    esc(r.root || '--'),
    chip(r.state || '--', r.state || 'neutral'),
    esc(r.workflow_keys ?? '--'),
    esc(r.translated ?? '--'),
    esc(r.pending ?? '--'),
    esc(r.requeue_count ?? '--'),
    esc(r.clean_key_count ?? '--'),
    esc(r.judge_sample_count ?? '--'),
    esc(((r.production_metrics || {}).weekly_cap_fired) ? 'yes' : 'no'),
    esc(r.next_action || '--')
  ]);
  $('ledger').innerHTML = table(['Recorded', 'Root', 'State', 'Keys', 'Translated', 'Pending', 'Requeue', 'Clean', 'Sample', 'Cap', 'Next Action'], rows);
}

function renderFreshness(data) {
  const rows = Object.entries(data.freshness || {}).map(([name, f]) => [
    esc(name),
    f.exists ? chip('present', 'clean') : chip('not available yet', 'neutral'),
    esc(f.mtime || '--'),
    esc(formatAge(f.age_seconds)),
    esc(f.size ?? '--')
  ]);
  $('freshness').innerHTML = table(['File', 'Status', 'Modified', 'Age', 'Bytes'], rows);
}

async function refresh() {
  try {
    const res = await fetch('/api/status', { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    refreshMs = data.refresh_ms || refreshMs;
    $('rootPath').textContent = data.root || '';
    $('lastRefresh').textContent = new Date().toLocaleTimeString();
    const ages = Object.values(data.freshness || {}).filter(f => f.exists && Number.isFinite(f.age_seconds)).map(f => f.age_seconds);
    $('dataAge').textContent = ages.length ? formatAge(Math.min(...ages)) : '--';
    $('healthChip').outerHTML = chip('online', 'clean').replace('<span', '<span id="healthChip"');
    renderRun(data);
    renderPrint(data);
    renderEvents(data);
    renderLedger(data);
    renderFreshness(data);
  } catch (err) {
    $('lastRefresh').textContent = new Date().toLocaleTimeString();
    $('healthChip').outerHTML = chip('offline', 'blocked').replace('<span', '<span id="healthChip"');
    $('rootPath').textContent = err.message;
  } finally {
    clearTimeout(timer);
    timer = setTimeout(refresh, refreshMs);
  }
}

refresh();
