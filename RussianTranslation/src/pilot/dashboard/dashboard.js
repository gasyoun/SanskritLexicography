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

// ---------------- Evolution timelapse ----------------
let evoData = null;
let evoCursor = 0;
let evoInit = false;
let evoPlaying = false;
let evoPlayTimer = null;
let evoFullHistory = true;

function fmtNum(v, pct) {
  if (!Number.isFinite(v)) return '--';
  if (pct) return (Math.round(v * 100) / 100) + '%';
  if (v >= 1000) return (v / 1000).toFixed(v >= 10000 ? 0 : 1) + 'k';
  return String(Math.round(v * 100) / 100);
}

function svgLine(values, opts) {
  opts = opts || {};
  const W = 320, H = 110, padL = 30, padR = 6, padT = 10, padB = 14;
  const n = values.length;
  const cursor = Number.isInteger(opts.cursor) ? opts.cursor : n - 1;
  const upTo = opts.grow ? cursor : n - 1;
  const nums = values.filter(v => Number.isFinite(v));
  const maxV = nums.length ? Math.max(...nums) : 1;
  const span = maxV || 1;
  const x = (i) => padL + (n <= 1 ? 0 : (W - padL - padR) * i / (n - 1));
  const y = (v) => padT + (H - padT - padB) * (1 - v / span);
  const pts = [];
  for (let i = 0; i <= upTo; i++) {
    const v = values[i];
    if (!Number.isFinite(v)) continue;
    pts.push(`${x(i).toFixed(1)},${y(v).toFixed(1)}`);
  }
  const color = opts.color || '#4da3ff';
  let area = '';
  if (opts.area && pts.length) {
    area = `<polygon points="${padL.toFixed(1)},${y(0).toFixed(1)} ${pts.join(' ')} ${x(upTo).toFixed(1)},${y(0).toFixed(1)}" fill="${color}" opacity="0.13"/>`;
  }
  const line = pts.length ? `<polyline points="${pts.join(' ')}" fill="none" stroke="${color}" stroke-width="2" vector-effect="non-scaling-stroke"/>` : '';
  const cx = x(cursor);
  const cursorLine = `<line x1="${cx.toFixed(1)}" y1="${padT}" x2="${cx.toFixed(1)}" y2="${H - padB}" stroke="var(--evo-cursor,#9aa)" stroke-dasharray="3 3" stroke-width="1" vector-effect="non-scaling-stroke"/>`;
  const cv = values[cursor];
  const dot = Number.isFinite(cv) ? `<circle cx="${cx.toFixed(1)}" cy="${y(cv).toFixed(1)}" r="3" fill="${color}"/>` : '';
  const yMax = `<text x="1" y="${(y(maxV) + 3).toFixed(1)}" class="evo-axis">${esc(fmtNum(maxV, opts.pct))}</text>`;
  const yMin = `<text x="1" y="${y(0).toFixed(1)}" class="evo-axis">0</text>`;
  return `<svg viewBox="0 0 ${W} ${H}" class="evo-svg" preserveAspectRatio="none">${area}${line}${cursorLine}${dot}${yMax}${yMin}</svg>`;
}

function evoCard(title, values, opts) {
  opts = opts || {};
  const cur = (values || [])[evoCursor];
  const val = Number.isFinite(cur) ? fmtNum(cur, opts.pct) : '--';
  return `<div class="evo-card"><div class="evo-card-head"><span>${esc(title)}</span><b>${esc(val)}</b></div>${
    svgLine(values || [], { ...opts, cursor: evoCursor, grow: !evoFullHistory })
  }</div>`;
}

function renderEvolution() {
  if (!evoData || evoData.empty) {
    $('evoCharts').innerHTML = '<div class="note">no timelapse data yet</div>';
    return;
  }
  const s = evoData.series, days = evoData.days, hl = evoData.headline || {};
  if ($('evoSpan')) $('evoSpan').textContent = `${evoData.span.start} → ${evoData.span.end} (${evoData.span.days}d)`;
  const scrub = $('evoScrub');
  scrub.max = String(days.length - 1);
  if (evoCursor > days.length - 1) evoCursor = days.length - 1;
  scrub.value = String(evoCursor);
  $('evoDay').textContent = days[evoCursor];
  $('evoHeadline').innerHTML = [
    metric('Cards', hl.total_cards),
    metric('Headwords', hl.total_roots),
    metric('PWG coverage', (hl.coverage_pwg_pct ?? '--') + '%'),
    metric('DCS coverage', (hl.coverage_dcs_pct ?? '--') + '%'),
    metric('Rigor index', (hl.rigor_index_pct ?? '--') + '%'),
    metric('Requeue rate', (hl.requeue_rate_pct ?? '--') + '%')
  ].join('');
  $('evoCharts').innerHTML = [
    evoCard('Throughput — cards', s.cards_cumulative, { color: '#4da3ff', area: true }),
    evoCard('Coverage — % of PWG', s.coverage_pwg_pct, { color: '#38b000', pct: true }),
    evoCard('Academic rigor — %', s.rigor_index_pct, { color: '#b06bff', pct: true }),
    evoCard('Quality — requeue rate %', s.requeue_rate_pct, { color: '#ff8c42', pct: true }),
    evoCard('Cost — tokens/window', s.tokens_per_window, { color: '#e05260' }),
    evoCard('Speed — minutes/window', s.minutes_per_window, { color: '#00b3a4' })
  ].join('');
  const ft = evoData.failure_typology || {};
  const modes = ft.modes || [];
  const modeMax = Math.max(1, ...modes.map(m => m.count));
  $('evoFailures').innerHTML = modes.length ? modes.map(m =>
    `<div class="evo-bar-row"><span class="evo-bar-label">${esc(m.mode)}</span><span class="evo-bar"><span style="width:${(100 * m.count / modeMax).toFixed(1)}%"></span></span><b>${esc(m.count)}</b></div>`
  ).join('') : '<div class="note">no failures recorded</div>';
  const trends = evoData.trends || [];
  $('evoTrends').innerHTML = trends.length
    ? `<ul>${trends.map(t => `<li>${esc(t)}</li>`).join('')}</ul>`
    : 'no trends computed yet';
}

function evoStep() {
  if (!evoData || evoData.empty) return;
  evoCursor = (evoCursor + 1) % evoData.days.length;
  renderEvolution();
}

function evoSetPlaying(on) {
  evoPlaying = on;
  $('evoPlay').innerHTML = on ? '&#9208; Pause' : '&#9654; Play';
  clearInterval(evoPlayTimer);
  if (on) {
    if (evoData && evoCursor >= evoData.days.length - 1) evoCursor = 0;
    evoPlayTimer = setInterval(evoStep, 650);
  }
}

function wireEvolutionControls() {
  $('evoPlay').addEventListener('click', () => evoSetPlaying(!evoPlaying));
  $('evoScrub').addEventListener('input', (e) => {
    evoSetPlaying(false);
    evoCursor = parseInt(e.target.value, 10) || 0;
    renderEvolution();
  });
  $('evoCursorAll').addEventListener('change', (e) => {
    evoFullHistory = e.target.checked;
    renderEvolution();
  });
}

async function refreshEvolution() {
  try {
    const res = await fetch('/api/evolution', { cache: 'no-store' });
    if (res.ok) {
      evoData = await res.json();
      if (!evoInit && evoData && evoData.days && evoData.days.length) {
        evoCursor = evoData.days.length - 1;
        evoInit = true;
      }
      renderEvolution();
    }
  } catch (err) {
    /* evolution is best-effort; the status poll reports health */
  } finally {
    setTimeout(refreshEvolution, 30000);
  }
}

wireEvolutionControls();
refresh();
refreshEvolution();
