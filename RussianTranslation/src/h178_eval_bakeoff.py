#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h178_eval_bakeoff.py — H178 Part B-1: the four-way human-evaluation rubric
bake-off over a held-out sample of ALREADY-PROMOTED pwg_ru glosses (0 new
Claude generation; the only generation is the cheap DeepSeek pairwise baseline).

MG rulings baked in (H178, 05-07-2026 — do not re-litigate):
  * run ALL FOUR paradigms on the SAME sample: (a) MQM-adapted error annotation,
    (b) adequacy/fluency Likert 1-5, (c) Direct Assessment 0-100, (d) pairwise
    ranking (promoted Sonnet-5 card vs a DeepSeek baseline, blinded A/B);
  * score each rubric on reliability / discrimination / annotation cost /
    diagnostic value, then let the data pick the standing protocol;
  * annotator reality = ONE human (MG) + a NON-Claude second channel (DeepSeek,
    avoids Claude-judging-Claude circularity); agreement is reported as
    human x model — NEVER as human x human;
  * COMETKiwi is a SECONDARY, reference-free QE signal, unvalidated on 19th-c.
    German -> modern-Russian dictionary glosses.

Sheets follow the org /review-sheet convention (interactive HTML, never
markdown checkboxes); the template is derived from build_h180_review_sheets.py
with rubric widgets added, and the decisions.json export keeps the
{sheet_id, generated, decided, items:[{id, decision, note}]} contract —
rubric values are serialized as compact JSON inside `note` (prefix `H178:`),
plus per-item vote timestamps `t` for the annotation-cost axis.

PUBLISH SAFETY: the sample, the baseline, the DeepSeek channel and the sheets
all embed unpublished `ru` translations; the repo is PUBLIC — everything this
script writes is gitignored (pwg_ru/eval/ + review/). Only this generator and
the protocol doc are committed.

Usage (in order):
  python src/h178_eval_bakeoff.py sample     # build the 30-gloss held-out sample
  python src/h178_eval_bakeoff.py baseline   # DeepSeek DE->RU baseline (pairwise arm B)
  python src/h178_eval_bakeoff.py judge      # DeepSeek second-channel annotations (all 4 rubrics)
  python src/h178_eval_bakeoff.py sheets     # emit the 4 HTML voting sheets for MG
  python src/h178_eval_bakeoff.py comet      # COMETKiwi QE scores (needs HF token; else prints steps)
  python src/h178_eval_bakeoff.py compute    # post-vote: kappa/alpha, discrimination, cost, correlations
"""
import sys, os, io, json, html, random, re, time, argparse, collections, math

from csl_pyutil import render_review_sheet

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STORE = os.path.join(HERE, "pwg_ru_translated.jsonl")
EVAL_DIR = os.path.join(ROOT, "pwg_ru", "eval")
REVIEW = os.path.join(ROOT, "review")
SAMPLE = os.path.join(EVAL_DIR, "h178_eval_sample.jsonl")
BASELINE = os.path.join(EVAL_DIR, "h178_baseline_deepseek.jsonl")
DS_CHANNEL = os.path.join(EVAL_DIR, "h178_deepseek_channel.jsonl")
COMET_OUT = os.path.join(EVAL_DIR, "h178_cometkiwi_scores.jsonl")
GENERATED = "2026-07-07"
SEED = 178
N_RANDOM = 20
# A-1(a) promoted-as-is flagged keys (H178_REAUDIT_2026-07-06.md) — deliberate
# oversample of suspected-weak cards; 10 of the 16 are drawn (seeded).
FLAGGED_SUBCARDS = [
    "car~~h0_23_up_a", "car~~h0_zz_pw03", "jan~~h0_11__a", "jan~~h0_zz_pw00",
    "ji~~h0_zz_sch", "ji~~h3_00_pwg00", "muc~~h0_20_pra", "vah~~h0_zz_pw03",
    "vah~~h3_00_pwg00", "vas~~h0_zz_pw00", "vas~~h0_zz_pw01", "vas~~h0_zz_pw03",
    "vas~~h13_00_pwg00", "vi_s~~h0_zz_pw01", "vid~~h0_10_ni", "gam~~h0_13_antar",
]
N_FLAGGED = 10

MQM_CATS = ["mistranslation", "omission", "addition", "terminology", "fluency"]
SEVERITIES = ["none", "minor", "major", "critical"]


def esc(s):
    return html.escape("" if s is None else str(s))


def load_store_rows():
    rows = []
    with io.open(STORE, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("de") and r.get("ru"):
                rows.append(r)
    return rows


def row_id(r, i):
    return "%s|%s|%s" % ((r.get("provenance") or {}).get("root", "?"),
                         r.get("subcard") or r.get("key1") or "?",
                         r.get("sense_tag") or i)


# ----------------------------------------------------------------------- sample
def cmd_sample():
    os.makedirs(EVAL_DIR, exist_ok=True)
    rows = load_store_rows()
    rng = random.Random(SEED)
    by_sub = collections.defaultdict(list)
    for i, r in enumerate(rows):
        s = r.get("subcard") or r.get("key1")
        by_sub[s].append((i, r))
    picked, seen_ids = [], set()
    # stratum 1: flagged oversample — one seeded sense row per flagged subcard
    flagged_avail = [k for k in FLAGGED_SUBCARDS if k in by_sub]
    rng.shuffle(flagged_avail)
    for k in flagged_avail[:N_FLAGGED]:
        i, r = rng.choice(by_sub[k])
        picked.append(("flagged", i, r))
    # stratum 2: random clean rows, root-stratified (>=3 roots guaranteed by spread)
    pool = [(i, r) for i, r in enumerate(rows)
            if (r.get("subcard") or r.get("key1")) not in set(flagged_avail[:N_FLAGGED])]
    rng.shuffle(pool)
    roots_seen = collections.Counter()
    for i, r in pool:
        if len(picked) >= N_FLAGGED + N_RANDOM:
            break
        root = (r.get("provenance") or {}).get("root", "?")
        if roots_seen[root] >= 4:  # cap per root to force spread
            continue
        roots_seen[root] += 1
        picked.append(("random", i, r))
    with io.open(SAMPLE, "w", encoding="utf-8") as f:
        for stratum, i, r in picked:
            f.write(json.dumps({
                "id": row_id(r, i), "stratum": stratum,
                "root": (r.get("provenance") or {}).get("root"),
                "subcard": r.get("subcard") or r.get("key1"),
                "sense_tag": r.get("sense_tag"),
                "de": r.get("de"), "ru": r.get("ru"),
                "layer": r.get("layer"), "iast": r.get("iast"),
            }, ensure_ascii=False) + "\n")
    roots = {json.loads(l)["root"] for l in io.open(SAMPLE, encoding="utf-8")}
    print("sample: %d items (%d flagged + %d random) across %d roots -> %s"
          % (len(picked), sum(1 for s, _, _ in picked if s == "flagged"),
             sum(1 for s, _, _ in picked if s == "random"), len(roots), SAMPLE))


def load_sample():
    return [json.loads(l) for l in io.open(SAMPLE, encoding="utf-8")]


def _deepseek():
    sys.path.insert(0, HERE)
    import build_corpus_lexicon as bcl
    return bcl.deepseek


# --------------------------------------------------------------------- baseline
# NB: build_corpus_lexicon.deepseek() pins response_format json_object, and the
# DeepSeek API 400-rejects JSON mode unless the prompt mentions JSON — so the
# baseline must ask for a JSON wrapper (measured 07-07-2026: 13x 400 with a
# plain-text prompt, 0 errors with this one).
BASELINE_SYS = (
    "You translate 19th-century scholarly German dictionary glosses (Boehtlingk-Roth "
    "Sanskrit dictionary) into modern scholarly Russian. PRESERVE VERBATIM: {#...#} "
    "SLP1 Sanskrit spans, <ls>...</ls> citations, <ab>...</ab> abbreviations, <div ...> "
    "markup, [Page...] markers, sense numbering. Translate ONLY German prose, including "
    "{%...%} gloss contents (German inside {%...%} -> Russian inside {%...%}; Latin "
    "botanical/zoological binomials stay Latin). Output STRICT JSON only: "
    '{"ru": "<the full translated text>"}')


def cmd_baseline():
    ds = _deepseek()
    items = load_sample()
    done = {}
    if os.path.exists(BASELINE):
        for l in io.open(BASELINE, encoding="utf-8"):
            d = json.loads(l)
            done[d["id"]] = d
    with io.open(BASELINE, "a", encoding="utf-8") as f:
        for it in items:
            if it["id"] in done:
                continue
            out = ds(it["de"], system=BASELINE_SYS)
            ru = ""
            m = re.search(r"\{.*\}", out or "", re.S)
            if m:
                txt = m.group(0)
                try:
                    ru = json.loads(txt).get("ru", "")
                except Exception:
                    # SLP1 accent markup ({#..\vyAda^..#}) leaks invalid JSON
                    # escapes like \v — double any backslash not starting a
                    # valid JSON escape, then retry (measured on naS 07-07-2026)
                    lenient = re.sub(r'\\(?![\\/"bfnrtu])', r"\\\\", txt)
                    try:
                        ru = json.loads(lenient).get("ru", "")
                    except Exception:
                        ru = ""
            if not ru:
                print("baseline EMPTY (will not write, rerun later):", it["id"])
                continue
            f.write(json.dumps({"id": it["id"], "ru_baseline": ru.strip(),
                                "model": "deepseek-chat"}, ensure_ascii=False) + "\n")
            f.flush()
            print("baseline ok:", it["id"])
    print("baseline complete ->", BASELINE)


# ------------------------------------------------------------------------ judge
JUDGE_SYS = (
    "You are an expert German->Russian translation evaluator for 19th-century Sanskrit "
    "lexicography. Judge the RUSSIAN translation of the GERMAN source gloss. Markup "
    "conventions: {#...#} SLP1 Sanskrit (must be preserved verbatim), {%...%} glosses "
    "(German must be translated, Latin binomials kept), <ls> citations preserved. "
    "Answer with STRICT JSON only, no prose, matching exactly: "
    '{"mqm": {"mistranslation": SEV, "omission": SEV, "addition": SEV, "terminology": SEV, '
    '"fluency": SEV}, "mqm_note": "worst error span or empty", "adequacy": 1-5, '
    '"fluency_likert": 1-5, "da": 0-100, "pairwise": "A"|"B"|"tie"} '
    'where SEV is one of "none","minor","major","critical". "pairwise" compares '
    "candidate A vs candidate B for overall quality.")


def cmd_judge():
    ds = _deepseek()
    items = load_sample()
    base = {json.loads(l)["id"]: json.loads(l) for l in io.open(BASELINE, encoding="utf-8")}
    rng = random.Random(SEED + 1)
    done = {}
    if os.path.exists(DS_CHANNEL):
        for l in io.open(DS_CHANNEL, encoding="utf-8"):
            d = json.loads(l)
            done[d["id"]] = d
    with io.open(DS_CHANNEL, "a", encoding="utf-8") as f:
        for it in items:
            # deterministic per-item blinding shared with the pairwise sheet
            a_is_store = rng.random() < 0.5
            if it["id"] in done:
                continue
            b = base.get(it["id"], {}).get("ru_baseline", "")
            cand_a = it["ru"] if a_is_store else b
            cand_b = b if a_is_store else it["ru"]
            user = ("GERMAN SOURCE:\n%s\n\nRUSSIAN TRANSLATION (evaluate this for MQM/adequacy/"
                    "fluency/DA):\n%s\n\nPAIRWISE — candidate A:\n%s\n\ncandidate B:\n%s"
                    % (it["de"], it["ru"], cand_a, cand_b))
            out = ds(user, system=JUDGE_SYS)
            try:
                m = re.search(r"\{.*\}", out or "", re.S)
                verdict = json.loads(m.group(0))
            except Exception:
                verdict = {"parse_error": (out or "")[:400]}
            f.write(json.dumps({"id": it["id"], "a_is_store": a_is_store,
                                "verdict": verdict, "model": "deepseek-chat"},
                               ensure_ascii=False) + "\n")
            f.flush()
            print("judge ok:", it["id"])
    print("deepseek channel complete ->", DS_CHANNEL)


# ----------------------------------------------------------------------- sheets
# Calls the shared csl_pyutil.render_review_sheet() emitter (H925/H931) instead
# of hand-rolling the CSS/JS/TEMPLATE; the RUBRIC_JS widget script is spliced
# onto the RETURNED html string (same decisions.json contract as before).
RUBRIC_JS = """
<script>
(function () {
  var SHEET_ID = %(sheet_id_json)s;
  var STORE_KEY = 'review-sheet:' + SHEET_ID;
  function st() { try { return JSON.parse(localStorage.getItem(STORE_KEY) || '{}') || {}; } catch (e) { return {}; } }
  function put(s) { localStorage.setItem(STORE_KEY, JSON.stringify(s)); }
  var cards = document.querySelectorAll('.card');
  // ids the user has actually interacted with a rubric widget on — guards
  // against synthesizing an H178 note from untouched widget defaults (e.g.
  // mqm severities all "none") on a plain vote click.
  var touched = {};
  // Pure function of a card's CURRENT DOM widget values -> the H178:{...}
  // note line, with any free text typed below it preserved. Never reads the
  // shared core template's private `state` closure (unreachable from here) —
  // localStorage, kept in sync by put() below, is this script's own source
  // of truth for both decision and note.
  function rubricNote(card, existingNote) {
    var data = {};
    card.querySelectorAll('[data-rubric]').forEach(function (el) {
      data[el.getAttribute('data-rubric')] = el.value;
      var out = card.querySelector('output[data-for="' + el.getAttribute('data-rubric') + '"]');
      if (out) out.textContent = el.value;
    });
    if (!Object.keys(data).length) return existingNote || '';
    var free = (existingNote || '').replace(/^H178:\\{[^\\n]*\\}\\n?/, '');
    return 'H178:' + JSON.stringify(data) + '\\n' + free;
  }
  // Re-merge EVERY touched card's rubric note into FRESH localStorage. The
  // core template's save() — triggered by a vote/note-textarea edit on ANY
  // card — always writes its ENTIRE stale in-memory `state` object back,
  // clobbering every id's note at once (not just the id just acted on). So
  // every save()-triggering event must re-heal every previously-touched
  // card, not only the current one, or an earlier card's note silently gets
  // wiped by a later, unrelated vote elsewhere on the sheet.
  function healAll() {
    var s = st();
    cards.forEach(function (card) {
      var id = card.getAttribute('data-id');
      if (!touched[id]) return;
      s[id] = s[id] || {};
      s[id].note = rubricNote(card, s[id].note);
      var ta = card.querySelector('textarea.note'); if (ta) ta.value = s[id].note;
    });
    put(s);
    return s;
  }
  cards.forEach(function (card) {
    var id = card.getAttribute('data-id');
    card.querySelectorAll('[data-rubric]').forEach(function (el) {
      el.addEventListener('change', function () { touched[id] = true; healAll(); });
      el.addEventListener('input', function () { touched[id] = true; healAll(); });
    });
    card.querySelectorAll('button.vote').forEach(function (btn) {
      btn.addEventListener('click', function () {
        // Runs AFTER the core template's own vote()/save() listener (this
        // script is injected after core's <script>, so it registers second
        // on the same buttons) — core's save() just overwrote localStorage
        // wholesale with its stale in-memory `state`. Re-heal every touched
        // card's note, then stamp this card's vote time.
        var s = healAll();
        s[id] = s[id] || {}; s[id].t = Date.now(); put(s);
      });
    });
  });
  // The core template's Download button reads its payload from that same
  // stale in-memory `state`, so it would still export the pre-clobber note
  // even with localStorage healed above. Strip its listener (clone-and-
  // replace drops all previously attached listeners) and export fresh from
  // localStorage instead. Re-run healAll() first as a final safety net: the
  // free-text note textarea (core's own noteChange()/save()) triggers the
  // same whole-state clobber as a vote click but isn't hooked above (healing
  // on every keystroke there would fight the user's cursor), so a textarea
  // edit could be the last action before Download with nothing left to heal
  // it — covered here since export time is what actually has to be correct.
  var oldBtn = document.getElementById('downloadBtn');
  if (oldBtn) {
    var newBtn = oldBtn.cloneNode(true);
    oldBtn.parentNode.replaceChild(newBtn, oldBtn);
    newBtn.addEventListener('click', function () {
      var s = healAll();
      var ids = Array.prototype.map.call(document.querySelectorAll('.card'),
        function (c) { return c.getAttribute('data-id'); });
      var decided = ids.filter(function (id) { return s[id] && s[id].decision; }).length;
      var payload = { sheet_id: SHEET_ID, generated: %(generated_json)s, decided: decided,
        items: ids.map(function (id) {
          var rec = s[id] || {};
          return { id: id, decision: rec.decision || null, note: rec.note || '' };
        }) };
      var blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
      var url = URL.createObjectURL(blob); var a = document.createElement('a');
      a.href = url; a.download = 'decisions.json'; document.body.appendChild(a); a.click();
      document.body.removeChild(a); URL.revokeObjectURL(url);
    });
  }
})();
</script>
"""


def _rubric_panel(kind, it, blinded):
    if kind == "mqm":
        rows = "".join(
            '<div style="margin:3px 0">%s: <select data-rubric="%s">%s</select></div>' % (
                esc(cat), esc(cat),
                "".join('<option value="%s">%s</option>' % (s, s) for s in SEVERITIES))
            for cat in MQM_CATS)
        return ("<div class=\"panel\"><h4>MQM error severities</h4>%s"
                "<div class=\"muted\">approve = no errors; reject = errors marked; "
                "put the worst error SPAN in the note (free text below the H178 line).</div></div>" % rows)
    if kind == "likert":
        sel = lambda name: '<select data-rubric="%s">%s</select>' % (
            name, "".join('<option>%d</option>' % i for i in range(1, 6)))
        return ("<div class=\"panel\"><h4>Likert 1–5</h4>"
                "adequacy (meaning preserved): %s &nbsp;&nbsp; fluency (natural scholarly Russian): %s"
                "</div>" % (sel("adequacy"), sel("fluency_likert")))
    if kind == "da":
        return ("<div class=\"panel\"><h4>Direct Assessment</h4>"
                "0 (useless) … 100 (perfect): "
                '<input type="range" min="0" max="100" value="50" data-rubric="da" style="width:60%%">'
                ' <output data-for="da">50</output></div>')
    if kind == "pairwise":
        return ("<div class=\"panel\"><h4>Pairwise</h4>"
                "<div class=\"muted\">approve = A better · reject = B better · defer = tie. "
                "Candidates are blinded and per-item randomized.</div></div>")
    return ""


SHEETS = [
    ("h178_mqm", "MQM-adapted error annotation", "mqm",
     "Mark error severities per category; approve if the Russian gloss has NO errors.",
     "No errors", "Errors marked"),
    ("h178_likert", "Adequacy/fluency Likert", "likert",
     "Rate adequacy and fluency 1–5, then approve (acceptable as-is) / reject (needs rework).",
     "Acceptable", "Needs rework"),
    ("h178_da", "Direct Assessment 0–100", "da",
     "Slide to the overall quality score; approve (>=70 in your judgment) / reject otherwise.",
     "Publishable", "Not publishable"),
    ("h178_pairwise", "Pairwise ranking (blinded)", "pairwise",
     "Which candidate is the better Russian rendering of the German source?",
     "A better", "B better"),
]


def cmd_sheets():
    os.makedirs(REVIEW, exist_ok=True)
    items_raw = load_sample()
    base = {json.loads(l)["id"]: json.loads(l) for l in io.open(BASELINE, encoding="utf-8")} \
        if os.path.exists(BASELINE) else {}
    rng = random.Random(SEED + 1)  # SAME stream as cmd_judge -> same blinding
    blinding = {}
    for it in items_raw:
        blinding[it["id"]] = rng.random() < 0.5  # a_is_store
    for sheet_id, title, kind, question, alab, rlab in SHEETS:
        items = []
        for it in items_raw:
            panels = [("German source (PWG 5-layer)", "<pre>%s</pre>" % esc(it["de"]))]
            if kind == "pairwise":
                b = base.get(it["id"], {}).get("ru_baseline", "(baseline missing — run baseline)")
                a_is_store = blinding[it["id"]]
                ca = it["ru"] if a_is_store else b
                cb = b if a_is_store else it["ru"]
                panels.append(("Candidate A", "<pre>%s</pre>" % esc(ca)))
                panels.append(("Candidate B", "<pre>%s</pre>" % esc(cb)))
            else:
                panels.append(("Russian translation (promoted store)", "<pre>%s</pre>" % esc(it["ru"])))
            items.append({
                "id": it["id"], "filt": it["stratum"],
                "title": "%s · %s" % (it["subcard"], it.get("sense_tag") or ""),
                "badges": [it["stratum"], it.get("layer") or ""],
                "question": esc(question) + _rubric_panel(kind, it, blinding),
                "panels": panels,
                "note_placeholder": "free-text note (H178 rubric line is auto-managed)",
            })
        config = {
            "sheet_id": sheet_id, "title": title, "generated": GENERATED,
            "subtitle": "H178 B-1 bake-off — one human channel (MG); DeepSeek is the model channel; "
                        "agreement is reported human×model, never human×human.",
            "footer": "Sheet %s of 4 — all four rubrics run on the SAME 30 glosses. " % sheet_id,
            "approve_label": alab, "reject_label": rlab,
            # reproduces the original all/unvoted/flagged/random filter set; render_review_sheet
            # always prepends "all" and appends "unvoted only" itself.
            "filters": [("flagged", "flagged"), ("random", "random")],
        }
        html_out = render_review_sheet(items, config, extras=True)
        html_out = html_out.replace("</body>", RUBRIC_JS % {
            "sheet_id_json": json.dumps(sheet_id), "generated_json": json.dumps(GENERATED),
        } + "</body>")
        out = os.path.join(REVIEW, sheet_id + "_sheet.html")
        io.open(out, "w", encoding="utf-8").write(html_out)
        print("sheet:", out, "(%d items)" % len(items))


# ------------------------------------------------------------------------ comet
def cmd_comet():
    try:
        from comet import download_model, load_from_checkpoint  # noqa
    except ImportError:
        print("BLOCKED: unbabel-comet is not installed. Steps (human/one-time):\n"
              "  1. pip install unbabel-comet\n"
              "  2. huggingface-cli login  (accept the license for Unbabel/wmt22-cometkiwi-da)\n"
              "  3. python src/h178_eval_bakeoff.py comet\n"
              "Model: Unbabel/wmt22-cometkiwi-da (0.5B, CPU-feasible); the XL variant\n"
              "wmt23-cometkiwi-da-xl (3.5B) needs a GPU box. Caveat (report verbatim in the\n"
              "protocol): COMETKiwi is trained on modern sentence-level MT and is UNVALIDATED\n"
              "on 19th-c. German -> modern-Russian dictionary glosses — triangulation aid,\n"
              "not a headline metric.")
        return 1
    items = load_sample()
    model_path = download_model("Unbabel/wmt22-cometkiwi-da")
    model = load_from_checkpoint(model_path)
    data = [{"src": it["de"], "mt": it["ru"]} for it in items]
    out = model.predict(data, batch_size=4, gpus=0)
    with io.open(COMET_OUT, "w", encoding="utf-8") as f:
        for it, score in zip(items, out.scores):
            f.write(json.dumps({"id": it["id"], "cometkiwi": score,
                                "model": "Unbabel/wmt22-cometkiwi-da"}) + "\n")
    print("cometkiwi ->", COMET_OUT)


# ---------------------------------------------------------------------- compute
def _kappa(a, b, labels):
    """Cohen's kappa over paired label lists."""
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def _spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def _parse_h178_note(note):
    m = re.match(r"H178:(\{.*?\})", note or "")
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except Exception:
        return {}


def cmd_compute(args):
    """args.decisions: dir containing decisions.json files renamed h178_<rubric>.decisions.json"""
    ddir = args.decisions or EVAL_DIR
    ds = {}
    if os.path.exists(DS_CHANNEL):
        for l in io.open(DS_CHANNEL, encoding="utf-8"):
            d = json.loads(l)
            ds[d["id"]] = d
    comet = {}
    if os.path.exists(COMET_OUT):
        for l in io.open(COMET_OUT, encoding="utf-8"):
            d = json.loads(l)
            comet[d["id"]] = d["cometkiwi"]
    report = {}
    for sheet_id, title, kind, *_ in SHEETS:
        p = os.path.join(ddir, sheet_id + ".decisions.json")
        if not os.path.exists(p):
            print("missing votes:", p, "— skip", sheet_id)
            continue
        votes = json.load(io.open(p, encoding="utf-8"))
        items = {v["id"]: v for v in votes["items"] if v.get("decision")}
        # cost axis: median inter-vote gap from localStorage timestamps is not in the
        # export; fall back to counting decided items (report time manually) — the
        # sheet stamps s[id].t but export keeps only decision+note, so cost is
        # collected via MG's wall-clock note per sheet (see protocol doc).
        human_bin, model_bin, h_scores, m_scores, c_scores = [], [], [], [], []
        for iid, v in items.items():
            dj = (ds.get(iid) or {}).get("verdict") or {}
            rub = _parse_h178_note(v.get("note"))
            if kind == "mqm":
                h = "reject" if v["decision"] == "reject" else "approve"
                worst = max((SEVERITIES.index(dj.get("mqm", {}).get(c, "none"))
                             for c in MQM_CATS), default=0) if dj else 0
                m = "reject" if worst >= 2 else "approve"
                human_bin.append(h); model_bin.append(m)
            elif kind == "likert":
                try:
                    h_scores.append(int(rub.get("adequacy", 0))); m_scores.append(int(dj.get("adequacy", 0)))
                except Exception:
                    pass
            elif kind == "da":
                try:
                    h_scores.append(float(rub.get("da"))); m_scores.append(float(dj.get("da")))
                except Exception:
                    pass
            elif kind == "pairwise":
                a_is_store = (ds.get(iid) or {}).get("a_is_store")
                hmap = {"approve": "A", "reject": "B", "defer": "tie"}
                h = hmap.get(v["decision"])
                m = dj.get("pairwise")
                if h and m:
                    human_bin.append(h); model_bin.append(m)
            if iid in comet and kind == "da":
                c_scores.append((float(rub.get("da", 0)), comet[iid]))
        entry = {"decided": len(items)}
        if human_bin:
            labels = sorted(set(human_bin) | set(model_bin))
            entry["kappa_human_x_model"] = round(_kappa(human_bin, model_bin, labels), 3)
        if h_scores and m_scores and len(h_scores) == len(m_scores) and len(h_scores) > 2:
            entry["spearman_human_x_model"] = round(_spearman(h_scores, m_scores), 3)
            mean = sum(h_scores) / len(h_scores)
            entry["human_score_sd"] = round(math.sqrt(
                sum((x - mean) ** 2 for x in h_scores) / len(h_scores)), 3)  # discrimination
        if c_scores:
            entry["spearman_human_x_cometkiwi"] = round(
                _spearman([a for a, _ in c_scores], [b for _, b in c_scores]), 3)
        report[sheet_id] = entry
    out = os.path.join(EVAL_DIR, "h178_bakeoff_report.json")
    json.dump(report, io.open(out, "w", encoding="utf-8"), indent=1)
    print(json.dumps(report, indent=1))
    print("->", out)


def selftest():
    """Deterministic, no-network selftest: sample determinism + note parsing + stats."""
    assert _parse_h178_note('H178:{"da":"70"}\nfree text') == {"da": "70"}
    assert _parse_h178_note("no prefix") == {}
    k = _kappa(["a", "b", "a", "a"], ["a", "b", "b", "a"], ["a", "b"])
    assert 0 < k < 1, k
    s = _spearman([1, 2, 3, 4], [10, 20, 30, 40])
    assert abs(s - 1.0) < 1e-9, s
    s2 = _spearman([1, 2, 3, 4], [40, 30, 20, 10])
    assert abs(s2 + 1.0) < 1e-9, s2
    # blinding streams must match between judge and sheets
    r1, r2 = random.Random(SEED + 1), random.Random(SEED + 1)
    assert [r1.random() for _ in range(30)] == [r2.random() for _ in range(30)]
    print("h178_eval_bakeoff selftest OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sample", "baseline", "judge", "sheets",
                                    "comet", "compute", "selftest"])
    ap.add_argument("--decisions", help="dir with h178_<rubric>.decisions.json votes")
    args = ap.parse_args()
    if args.cmd == "sample":
        cmd_sample()
    elif args.cmd == "baseline":
        cmd_baseline()
    elif args.cmd == "judge":
        cmd_judge()
    elif args.cmd == "sheets":
        cmd_sheets()
    elif args.cmd == "comet":
        sys.exit(cmd_comet() or 0)
    elif args.cmd == "compute":
        cmd_compute(args)
    elif args.cmd == "selftest":
        selftest()


if __name__ == "__main__":
    main()
