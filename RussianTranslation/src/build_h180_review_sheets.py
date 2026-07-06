#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_h180_review_sheets.py — the four (three buildable) H180 human HTML voting
sheets, following the org /review-sheet convention (interactive HTML, never
markdown checkboxes — [[feedback_interactive_review_not_checkboxes]]).

Reuses the self-contained-HTML pattern of build_renou_pilot_sheet.py: one card
per item, approve/reject/defer + free-text note, running tally, localStorage
persistence, keyboard shortcuts, and a "Download decisions.json" export matching
the {sheet_id, generated, decided, items:[{id, decision, note}]} contract that
/decisions-apply consumes.

Three sheets are built (the fourth — Arm-A-vs-B coherence — needs the deferred
Arm-B model run, so it is intentionally skipped until synth output exists):

  1. typology  — κ-label sample: the 7 five-layer roots' non-pwg sub-card senses
                 + a deterministic 30-item random tail; confirm/correct the
                 LLM-proposed relationship subtype (reject → write the right
                 subtype in the note, for κ vs the LLM proposal).
  2. learner   — threshold calibration: a stratified sample across the retention
                 bands; is this headword learner-core (does a Russian student
                 need it)?
  3. reglue    — 15-card spot-check: is each rendered re-glue well-formed
                 (supplements at sensible senses, cancellations visible)?

PUBLISH SAFETY: the typology + reglue sheets embed translated `ru` bodies from
the gitignored/unpublished store, and this repo is PUBLIC — so the generated
HTML + the samples that carry translations are gitignored (see .gitignore). Only
this generator is committed; sheets are opened locally from file:// and voted in
the browser, then decisions.json feeds /decisions-apply.

Inputs (all local): src/pwg_ru_translated.jsonl, src/pwg_ru_relationships.jsonl,
pwg_ru/learner_scores.tsv, pwg_ru/reglue/*.md
Outputs (local, gitignored): review/h180_{typology,learner,reglue}_sheet.html
                              review/h180_{typology,learner,reglue}_sample.jsonl

Run: python src/build_h180_review_sheets.py
"""
import sys, os, io, json, html, re, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STORE = os.path.join(HERE, "pwg_ru_translated.jsonl")
REL = os.path.join(HERE, "pwg_ru_relationships.jsonl")
LEARNER = os.path.join(ROOT, "pwg_ru", "learner_scores.tsv")
REGLUE_DIR = os.path.join(ROOT, "pwg_ru", "reglue")
REVIEW = os.path.join(ROOT, "review")
GENERATED = "2026-07-06"

FIVE_LAYER = ["yat", "vraj", "rakz", "jIv", "gA", "Sam", "Cid"]


def esc(s):
    return html.escape("" if s is None else str(s))


# ----------------------------------------------------------------------------- template
TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>%(title)s — %(n)d items</title>
<style>
  :root { --bg:#0f1115; --panel:#171a21; --panel2:#1e222b; --text:#e6e6e6; --muted:#9aa0aa;
          --accent:#5b8cff; --ok:#3fb950; --bad:#f85149; --defer:#d29922; --border:#2a2f3a; }
  * { box-sizing: border-box; }
  body { background:var(--bg); color:var(--text); font-family:-apple-system,Segoe UI,Roboto,sans-serif;
         margin:0; padding:0 0 120px 0; }
  header.top { position:sticky; top:0; z-index:10; background:var(--panel); border-bottom:1px solid var(--border);
               padding:14px 20px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;}
  header.top h1 { font-size:16px; margin:0; }
  header.top .sub { color:var(--muted); font-size:12px; max-width:760px; }
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
  .badge { font-size:11px; background:var(--panel2); padding:2px 8px; border-radius:10px;
           margin-left:8px; color:var(--muted); }
  .question { margin:8px 0 12px; font-size:14px; }
  .panel { background:var(--panel2); border-radius:8px; padding:10px 12px; font-size:13px; margin-bottom:10px; }
  .panel h4 { margin:0 0 6px; font-size:11px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); }
  .panel pre { white-space:pre-wrap; word-break:break-word; margin:0; font-size:12px; line-height:1.45; }
  .chip { display:inline-block; background:#263042; border-radius:5px; padding:2px 7px; margin:2px 3px 2px 0; font-size:12px; }
  .muted { color:var(--muted); font-style:italic; }
  .controls { display:flex; align-items:center; gap:8px; margin-top:4px; }
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
    <h1>%(title)s — %(n)d items</h1>
    <div class="sub">Generated %(generated)s &middot; sheet_id <code>%(sheet_id)s</code> &middot; %(subtitle)s</div>
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
  <div class="filterbar" id="filterbar">%(filters)s</div>
</div>
<main id="cards">
%(cards)s
</main>
<footer class="hint">%(footer)s Keyboard: <kbd>a</kbd> %(approve_label)s &middot; <kbd>r</kbd> %(reject_label)s
  &middot; <kbd>d</kbd> defer &middot; <kbd>&darr;</kbd>/<kbd>&uarr;</kbd> next/prev. Votes autosave to
  this browser's localStorage; click "Download decisions.json" when done (unvoted items export with
  decision:null).</footer>
<script>
(function () {
  var SHEET_ID = %(sheet_id_json)s;
  var STORE_KEY = 'review-sheet:' + SHEET_ID;
  var ids = %(ids_json)s;
  var state = {};
  try { state = JSON.parse(localStorage.getItem(STORE_KEY) || '{}') || {}; } catch (e) { state = {}; }
  function tally() {
    var c = { approve:0, reject:0, defer:0 };
    ids.forEach(function (id) { var v = state[id] && state[id].decision; if (v && c.hasOwnProperty(v)) c[v]++; });
    document.getElementById('c-approve').textContent = c.approve;
    document.getElementById('c-reject').textContent = c.reject;
    document.getElementById('c-defer').textContent = c.defer;
    document.getElementById('c-unvoted').textContent = ids.length - c.approve - c.reject - c.defer;
  }
  function applyCardUI(card) {
    var id = card.getAttribute('data-id'); var rec = state[id] || {};
    card.classList.remove('voted-approve','voted-reject','voted-defer');
    card.querySelectorAll('button.vote').forEach(function (b) { b.classList.toggle('active', b.getAttribute('data-vote') === rec.decision); });
    card.querySelector('.vote-state').textContent = rec.decision ? rec.decision : 'unvoted';
    if (rec.decision) card.classList.add('voted-' + rec.decision);
    var ta = card.querySelector('textarea.note'); if (rec.note && !ta.value) ta.value = rec.note;
  }
  function save() { localStorage.setItem(STORE_KEY, JSON.stringify(state)); tally(); }
  function vote(id, d) { state[id] = state[id] || {}; state[id].decision = d; save(); }
  function noteChange(id, t) { state[id] = state[id] || {}; state[id].note = t; save(); }
  document.querySelectorAll('.card').forEach(function (card) {
    var id = card.getAttribute('data-id'); applyCardUI(card);
    card.querySelectorAll('button.vote').forEach(function (btn) {
      btn.addEventListener('click', function () { vote(id, btn.getAttribute('data-vote')); applyCardUI(card); });
    });
    var ta = card.querySelector('textarea.note'); ta.addEventListener('input', function () { noteChange(id, ta.value); });
  });
  tally();
  document.getElementById('downloadBtn').addEventListener('click', function () {
    var decided = ids.filter(function (id) { return state[id] && state[id].decision; }).length;
    var payload = { sheet_id: SHEET_ID, generated: %(generated_json)s, decided: decided,
      items: ids.map(function (id) { var rec = state[id] || {}; return { id: id, decision: rec.decision || null, note: rec.note || '' }; }) };
    var blob = new Blob([JSON.stringify(payload, null, 2)], { type:'application/json' });
    var url = URL.createObjectURL(blob); var a = document.createElement('a');
    a.href = url; a.download = 'decisions.json'; document.body.appendChild(a); a.click();
    document.body.removeChild(a); URL.revokeObjectURL(url);
  });
  var filterbar = document.getElementById('filterbar');
  filterbar.addEventListener('click', function (e) {
    var btn = e.target.closest('button[data-filter]'); if (!btn) return;
    filterbar.querySelectorAll('button').forEach(function (b) { b.classList.remove('active'); });
    btn.classList.add('active'); var f = btn.getAttribute('data-filter');
    document.querySelectorAll('.card').forEach(function (card) {
      var show = true;
      if (f === 'unvoted') { var id = card.getAttribute('data-id'); show = !(state[id] && state[id].decision); }
      else if (f !== 'all') { show = card.getAttribute('data-filt') === f; }
      card.style.display = show ? '' : 'none';
    });
  });
  var cardsEl = Array.prototype.slice.call(document.querySelectorAll('.card'));
  var activeIdx = 0;
  function visibleCards() { return cardsEl.filter(function (c) { return c.style.display !== 'none'; }); }
  document.addEventListener('keydown', function (e) {
    if (e.target.tagName === 'TEXTAREA') return;
    var vis = visibleCards(); if (!vis.length) return;
    if (activeIdx >= vis.length) activeIdx = vis.length - 1;
    var card = vis[activeIdx]; var id = card.getAttribute('data-id');
    if (e.key === 'a') { vote(id, 'approve'); applyCardUI(card); }
    else if (e.key === 'r') { vote(id, 'reject'); applyCardUI(card); }
    else if (e.key === 'd') { vote(id, 'defer'); applyCardUI(card); }
    else if (e.key === 'ArrowDown') { activeIdx = Math.min(activeIdx + 1, vis.length - 1); vis[activeIdx].scrollIntoView({behavior:'smooth',block:'center'}); }
    else if (e.key === 'ArrowUp') { activeIdx = Math.max(activeIdx - 1, 0); vis[activeIdx].scrollIntoView({behavior:'smooth',block:'center'}); }
    else return;
    e.preventDefault();
  });
})();
</script>
</body>
</html>
'''


def render_card(item, approve_label, reject_label):
    panels = "".join(
        '<div class="panel"><h4>%s</h4>%s</div>' % (esc(h4), body)
        for h4, body in item["panels"])
    badges = "".join('<span class="badge">%s</span>' % esc(b) for b in item.get("badges", []))
    return '''
  <section class="card" data-id="%s" data-filt="%s">
    <header><div class="hw">%s %s</div></header>
    <div class="question">%s</div>
    %s
    <div class="controls">
      <button class="vote approve" data-vote="approve">&#9989; %s</button>
      <button class="vote reject" data-vote="reject">&#10060; %s</button>
      <button class="vote defer" data-vote="defer">&#9208; Defer</button>
      <span class="vote-state">unvoted</span>
    </div>
    <textarea class="note" placeholder="%s"></textarea>
  </section>''' % (esc(item["id"]), esc(item["filt"]), esc(item["title"]), badges,
                   item["question"], panels, esc(approve_label), esc(reject_label),
                   esc(item.get("note_placeholder", "free-text note (optional)")))


def write_sheet(slug, cfg, items):
    os.makedirs(REVIEW, exist_ok=True)
    # sample jsonl (audit trail of exactly what was shown)
    sample_path = os.path.join(REVIEW, f"h180_{slug}_sample.jsonl")
    with io.open(sample_path, "w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps({k: it[k] for k in ("id", "filt", "title") if k in it},
                                ensure_ascii=False) + "\n")
    cards = "\n".join(render_card(it, cfg["approve_label"], cfg["reject_label"]) for it in items)
    filters = ('<button data-filter="all" class="active">all</button>'
               + "".join('<button data-filter="%s">%s</button>' % (esc(k), esc(l)) for k, l in cfg["filters"])
               + '<button data-filter="unvoted">unvoted only</button>')
    ids = [it["id"] for it in items]
    doc = TEMPLATE % {
        "title": cfg["title"], "subtitle": cfg["subtitle"], "footer": cfg["footer"],
        "approve_label": cfg["approve_label"], "reject_label": cfg["reject_label"],
        "n": len(items), "generated": GENERATED, "sheet_id": cfg["sheet_id"],
        "cards": cards, "filters": filters,
        "sheet_id_json": json.dumps(cfg["sheet_id"]), "ids_json": json.dumps(ids),
        "generated_json": json.dumps(GENERATED),
    }
    out = os.path.join(REVIEW, f"h180_{slug}_sheet.html")
    with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)
    print(f"  {slug:9s} {len(items):3d} items -> {out}")
    return out


# ----------------------------------------------------------------------------- data
def load_store():
    by_sub = {}
    for line in io.open(STORE, encoding="utf-8"):
        line = line.strip()
        if line:
            d = json.loads(line)
            by_sub[(d["subcard"], str(d.get("sense_tag")))] = d
    return by_sub


def build_typology(by_sub):
    rows = [json.loads(l) for l in io.open(REL, encoding="utf-8") if l.strip()]
    # CORE: the 7 five-layer roots yield ~640 supplements — far too many for a κ
    # pass. Stratify by (layer, subtype) and cap ~8 per stratum so every subtype is
    # represented (κ needs coverage of each class), aiming for ~a few dozen.
    core_pool = collections.defaultdict(list)
    for r in rows:
        if r["key1"] in FIVE_LAYER:
            core_pool[(r["layer"], r["relationship"]["subtype"])].append(r)
    core = []
    for key in sorted(core_pool):
        pool = sorted(core_pool[key], key=lambda r: (r["subcard"], r["sense_tag"]))
        step = max(1, len(pool) // 8)
        core.extend(pool[::step][:8])
    # TAIL: deterministic 30-item sample, evenly-strided over the sorted remainder.
    tail = sorted((r for r in rows if r["key1"] not in FIVE_LAYER),
                  key=lambda r: (r["subcard"], r["sense_tag"]))
    step = max(1, len(tail) // 30)
    tail_sample = tail[::step][:30]
    sample = core + tail_sample
    items = []
    for r in sample:
        rel = r["relationship"]; ip = rel["insertion_point"]
        rec = by_sub.get((r["subcard"], r["sense_tag"]), {})
        ru = esc(rec.get("ru", "(body not found)"))
        de = esc(rec.get("de", ""))
        proposal = (
            f'<pre>subtype   : <b>{esc(rel["subtype"])}</b>\n'
            f'op/dir    : {esc(rel["op"])} / {esc(rel["direction"])}\n'
            f'target    : {esc(ip["target_sense"])} (anchor {esc(ip["anchor"])})\n'
            f'evidence  : {esc(rel.get("evidence",""))}</pre>')
        items.append({
            "id": f'{r["subcard"]}::{r["sense_tag"]}',
            "filt": r["layer"],
            "title": f'{esc(r["key1"])} · {esc(r["layer"])} · sense {esc(r["sense_tag"])}',
            "badges": [rel["subtype"], "5-layer" if r["key1"] in FIVE_LAYER else "tail"],
            "question": (f'Is the proposed subtype <b>«{esc(rel["subtype"])}»</b> correct '
                         f'for this sub-card? <span class="muted">(reject → write the correct '
                         f'subtype in the note, for κ)</span>'),
            "note_placeholder": "if reject: correct subtype + why (e.g. 'nws_at_sense, attaches to sense 2')",
            "panels": [("LLM proposal (confidence: llm)", proposal),
                       ("Sub-card — Russian (ru)", f'<pre>{ru}</pre>'),
                       ("Sub-card — source (de)", f'<pre>{de}</pre>')],
        })
    return items


def build_learner():
    rows = []
    with io.open(LEARNER, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 6:
                rows.append({"key1": p[0], "learner": float(p[1]), "learner_norm": float(p[2]),
                             "support": float(p[3]), "scholarly": float(p[4]), "dicts": p[5]})
    RU = ("KCH", "KOW", "KNA", "SMI", "FRI")

    def n_ru(r):
        return sum(c in r["dicts"] for c in RU)

    bands = {
        "solid": [r for r in rows if n_ru(r) >= 2],
        "koch1": [r for r in rows if "KCH" in r["dicts"] and n_ru(r) == 1],
        "medonly": [r for r in rows if r["learner"] == 0 and r["support"] > 0],
        "control": [r for r in rows if r["learner"] == 0 and r["support"] == 0 and r["scholarly"] > 0],
    }
    band_label = {"solid": "≥2 Russian dicts", "koch1": "Kochergina-only",
                  "medonly": "medium-only (learner=0)", "control": "scholarly-only control"}
    items = []
    for band, pool in bands.items():
        pool.sort(key=lambda r: r["key1"])
        step = max(1, len(pool) // 15)
        for r in pool[::step][:15]:
            scores = (f'<pre>learner_score : <b>{r["learner"]:.2f}</b>  (norm {r["learner_norm"]:.2f})\n'
                      f'support_score : {r["support"]:.2f}   (CAE/CCS/MD)\n'
                      f'scholarly     : {r["scholarly"]:.2f}   (PW/MW/AP — non-gating)</pre>')
            items.append({
                "id": f'learner::{r["key1"]}',
                "filt": band,
                "title": esc(r["key1"]),
                "badges": [band_label[band]],
                "question": ('Does a Russian student need this headword? '
                             '<span class="muted">(approve = learner-core; reject = scholarly-only / skip)</span>'),
                "note_placeholder": "optional: why keep/drop for a learner edition",
                "panels": [("retention scores", scores),
                           ("dictionaries that kept it", f'<pre>{esc(r["dicts"])}</pre>')],
            })
    return items


def build_reglue():
    order = [("gA", 5), ("Cid", 5), ("Sam", 5), ("jIv", 5), ("rakz", 5), ("vraj", 5), ("yat", 5),
             ("DA", 4), ("Ap", 4), ("Bid", 4), ("Buj", 4), ("banD", 4), ("Sru", 4),
             ("viS", 3), ("siD", 3)]
    items = []
    for key1, nlayers in order:
        p = os.path.join(REGLUE_DIR, key1 + ".md")
        if not os.path.exists(p):
            continue
        body = io.open(p, encoding="utf-8").read()
        items.append({
            "id": f"reglue::{key1}",
            "filt": f"{nlayers}L",
            "title": esc(key1),
            "badges": [f"{nlayers}-layer"],
            "question": ('Is this re-glue well-formed? <span class="muted">(supplements land at '
                         'sensible senses · cancellations visible · foreign fragments shown with RU · '
                         'nothing broken)</span>'),
            "note_placeholder": "if reject: what is misplaced / broken",
            "panels": [("rendered re-glue card", f'<pre>{esc(body)}</pre>')],
        })
    return items


def main():
    by_sub = load_store()
    print("building H180 review sheets ...")

    write_sheet("typology", {
        "sheet_id": "h180-typology-kappa-2026-07-06",
        "title": "H180 · addenda-typology κ-label",
        "subtitle": "confirm/correct the LLM-proposed relationship subtype (7 five-layer roots + 30-item tail)",
        "footer": ("Approve = the LLM subtype is right · Reject = wrong (write the correct subtype "
                   "in the note — this is the second signal for κ) · Defer = can't tell."),
        "approve_label": "Correct", "reject_label": "Wrong",
        "filters": [("pw", "pw"), ("sch", "sch"), ("pwkvn", "pwkvn"), ("nws", "nws")],
    }, build_typology(by_sub))

    write_sheet("learner", {
        "sheet_id": "h180-learner-threshold-2026-07-06",
        "title": "H180 · learner-core threshold calibration",
        "subtitle": "is each PWG headword learner-core? — stratified across retention bands",
        "footer": ("Approve = a Russian student needs this headword (learner-core) · Reject = "
                   "scholarly-only / skip · Defer = unsure. Calibrates the learner_score cut."),
        "approve_label": "Learner-core", "reject_label": "Skip",
        "filters": [("solid", "≥2 RU"), ("koch1", "Koch-only"), ("medonly", "medium-only"), ("control", "control")],
    }, build_learner())

    write_sheet("reglue", {
        "sheet_id": "h180-reglue-spotcheck-2026-07-06",
        "title": "H180 · content-aware re-glue spot-check",
        "subtitle": "eyeball each of the 15 pilot re-glue cards (success criterion d)",
        "footer": ("Approve = well-formed re-glue · Reject = something misplaced/broken (say what "
                   "in the note) · Defer = unsure."),
        "approve_label": "Well-formed", "reject_label": "Broken",
        "filters": [("5L", "5-layer"), ("4L", "4-layer"), ("3L", "3-layer")],
    }, build_reglue())

    print("\nNOTE: the 4th sheet (Arm-A-vs-B coherence) is skipped — it needs the deferred "
          "Arm-B model run (synth_de_first.py generation) before there is a B output to compare.")
    print(f"open locally, e.g.:  start {os.path.join(REVIEW, 'h180_reglue_sheet.html')}")


if __name__ == "__main__":
    main()
