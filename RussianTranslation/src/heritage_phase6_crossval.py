#!/usr/bin/env python3
"""H3171 — Heritage phase 6: segmenter-as-service cross-validation vs DharmaMitra.

Witness A  Sanskrit Heritage segmenter/lemmatizer, UoHyd mirror v3.77
           (https://sanskrit.uohyd.ac.in/SKT, /cgi-bin/SKT/sktreader), Word
           mode, SLP1 input, Monier-Williams lexicon. Live service: every
           response disk-cached, 2 s inter-request throttle, identifying
           User-Agent (HERITAGE_INRIA_ROADMAP fence: live-service etiquette).
Witness B  DharmaMitra ByT5 multi-task analyzer, local pinned revision
           chronbmm/sanskrit5-multitask@c0d2ada (csl-atlas scripts/lib/
           dharmamitra_infer.py contract, SLM = unsandhied-lemma-
           morphosyntax). The live dharmamitra.org/api/tagging/ was probed
           same-day and returned identity echoes even for sandhi-bearing
           sentences (FINDINGS §95 failure class, now chronic) -> documented
           reproducible local path used instead.

Evaluation set  RussianTranslation/gold/saru_gloss_gold_set.jsonl — the
110-row H1349 wave-2 adjudicated glossary sample (3-judge panel on the
automatic lemma per surface form). Agreement vs the ADJUDICATION is computed
on the panel-'correct' rows (the only ones carrying a trusted reference
lemma); engine-vs-engine agreement is computed on all 110 rows separately.

Outputs (RussianTranslation/gold/):
  h3171_results.jsonl      per-row witness outputs + verdicts
  h3171_stats.json         machine-readable summary (agreements, classes)
  h3171_disagreements.tsv  disagreement rows for classification
  _cache_h3171/            every live response + request ledger

Run: python RussianTranslation/src/heritage_phase6_crossval.py
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent          # RussianTranslation/src
RT = HERE.parent                                # RussianTranslation/
GOLD_DIR = RT / "gold"
GOLD_PATH = GOLD_DIR / "saru_gloss_gold_set.jsonl"
CACHE_DIR = GOLD_DIR / "_cache_h3171"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
LEDGER = CACHE_DIR / "requests_ledger.jsonl"

UA = ("Mozilla/5.0 (compatible; SanskritLexicography-H3171 heritage-phase6 "
      "cross-validation client; +https://github.com/gasyoun/SanskritLexicography)")
THROTTLE_S = 2.0
READER_URL = "https://sanskrit.uohyd.ac.in/cgi-bin/SKT/sktreader"

HF_MODEL_ID = "chronbmm/sanskrit5-multitask"
PINNED_REVISION = "c0d2ada54f3d19903149425aa888a203601423f8"
SLM_PREFIX = "SLM "
DM_BATCH = 16

# ---------------------------------------------------------------- translit
# Reverse of the vendored csl-atlas SLP1_TO_IAST table (scripts/lib/
# dharmamitra_infer.py) — longest-match first so kh/K etc. resolve.
_SLP1_TO_IAST = {
    "A": "ā", "I": "ī", "U": "ū", "F": "ṝ", "X": "ḹ", "E": "ai", "O": "au",
    "f": "ṛ", "x": "ḷ", "M": "ṃ", "H": "ḥ", "~": "m̐", "z": "ṣ",
    "K": "kh", "G": "gh", "C": "ch", "J": "jh", "W": "ṭh", "Q": "ḍh",
    "P": "ph", "B": "bh", "N": "ṅ", "Y": "ñ", "w": "ṭ", "q": "ḍ",
    "R": "ṇ", "S": "ś", "L": "ḷ",
}
for _ch in "aeioukgcjt d p b m y r l v sh":
    pass
_IAST_TO_SLP1: dict[str, str] = {}
for slp, ias in _SLP1_TO_IAST.items():
    _IAST_TO_SLP1[ias] = slp
for lo, up in [("a", "A"), ("i", "I"), ("u", "U"), ("f", "F"), ("x", "X"),
               ("e", "E"), ("o", "O")]:
    _IAST_TO_SLP1.setdefault(lo, lo)
    _IAST_TO_SLP1.setdefault(up, up)
for ch in "kgcjtdnpbmyrlvsh":
    _IAST_TO_SLP1.setdefault(ch, ch)


def iast_to_slp1(text: str) -> str:
    out, i = [], 0
    while i < len(text):
        two = text[i:i + 2]
        if two in _IAST_TO_SLP1:  # ṭh, ḍh, m̐ ...
            out.append(_IAST_TO_SLP1[two])
            i += 2
            continue
        out.append(_IAST_TO_SLP1.get(text[i], text[i]))
        i += 1
    return "".join(out)


# ------------------------------------------------------------- normalization
_VOWELS = set("aeAiIuUfFxXeEoO")


def nasal_norm(slp1: str) -> str:
    """Fold anusvara/homorganic-nasal spellings (phase-4 nasal-norm).

    M, N, Y, R before a non-vowel (or word-final) collapse to M; a word-final
    plain m after a vowel folds to M too (Heritage AvAsam vs DCS AvAsaM)."""
    out = []
    for i, ch in enumerate(slp1):
        nxt = slp1[i + 1] if i + 1 < len(slp1) else ""
        precons = ch in "MNYR" and (nxt == "" or nxt not in _VOWELS)
        if precons:
            out.append("M")
        elif ch == "m" and nxt == "":
            out.append("M")
        else:
            out.append(ch)
    return "".join(out)


def norm_lemma(lem: str) -> str:
    lem = lem.strip()
    lem = re.sub(r"_?\d+$", "", lem)          # Heritage homonym index vṛ_1
    lem = lem.replace("'", "").replace("’", "")  # avagraha artifacts
    return nasal_norm(lem)


# ------------------------------------------------------------ gold sample
def load_gold():
    rows = []
    for line in GOLD_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def surface_slp1(row) -> str:
    """Compound-seam hyphen dropped; the reader re-discovers seams itself."""
    return row["slp1"].replace("-", "")


# ---------------------------------------------------------- witness: Heritage
def heritage_fetch(sl: str) -> str:
    params = {
        "lex": "MW", "cache": "t", "st": "f", "us": "f", "font": "roma",
        "t": "SL", "text": sl, "topic": "",
        "corpmode": "", "corpdir": "", "sentno": "",
    }
    url = READER_URL + "?" + urllib.parse.urlencode(params)
    key = hashlib.sha256(url.encode()).hexdigest()[:24]
    path = CACHE_DIR / f"her_{key}.txt"
    if path.exists():
        body = path.read_text(encoding="utf-8", errors="replace")
        LEDGER.open("a", encoding="utf-8").write(json.dumps(
            {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "service": "heritage", "cached": True, "text": sl}) + "\n")
        return body
    wait = THROTTLE_S - (time.time() - _LAST_HIT[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            body = r.read().decode("utf-8", "replace")
            status, final = r.status, r.geturl()
    except Exception as e:  # noqa: BLE001
        body = f"__ERROR__ {e.__class__.__name__}: {e}"
        status, final = -1, url
    _LAST_HIT[0] = time.time()
    path.write_text(f"[{status}] [{final}]\n{body}", encoding="utf-8")
    LEDGER.open("a", encoding="utf-8").write(json.dumps(
        {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "service": "heritage", "cached": False, "http": status,
         "throttle_s": THROTTLE_S, "text": sl}) + "\n")
    return body


_LAST_HIT = [0.0]

_SOL_RE = re.compile(r"Solution \d+")
_NAVY_RE = re.compile(r'<a class="navy"[^>]*>\s*<i>(.*?)</i></a>', re.S)
_FATAL_RE = re.compile(r"Fatal error\s*</span><span class=\"blue\">([^<]+)")
_NOSOL_RE = re.compile(r"0</span><span class=\"blue\"> solution|kept among\s*<span class=\"magenta\">0", re.S)


def heritage_parse(page: str):
    """-> {ok: bool, reason: str, solutions: [ [ {seg, stems_slp1} ] ]}."""
    m = _FATAL_RE.search(page)
    if m:
        return {"ok": False, "reason": "fatal:" + m.group(1).strip(), "solutions": []}
    chunks = _SOL_RE.split(page)[1:]
    if not chunks:
        return {"ok": False, "reason": "no-solutions-block", "solutions": []}
    sols = []
    for chunk in chunks:
        segs = []
        # each segment: bold surface followed by analysis table of navy stems
        for blk in re.split(r"<b>", chunk)[1:]:
            surf_m = re.match(r"([^<]+)</b>", blk)
            stems = [iast_to_slp1(html.unescape(re.sub(r"<[^>]+>", "", s))).strip()
                     for s in _NAVY_RE.findall(blk)]
            segs.append({"seg": (surf_m.group(1).strip() if surf_m else ""),
                         "stems_slp1": [re.sub(r"_\d+$", "", s) for s in stems]})
        if segs:
            sols.append(segs)
    if not sols:
        return {"ok": False, "reason": "zero-analyses", "solutions": []}
    return {"ok": True, "reason": "", "solutions": sols}


def heritage_lemmas(parsed) -> set[str]:
    out = set()
    for sol in parsed["solutions"]:
        for seg in sol:
            for st in seg["stems_slp1"]:
                if st:
                    out.add(norm_lemma(st))
    return out


# ------------------------------------------------------- witness: DharmaMitra
_DM_CACHE = CACHE_DIR / "dm_local_slm.json"

def dm_local(rows_by_key: dict[str, str]) -> dict[str, list[dict]]:
    cache = json.loads(_DM_CACHE.read_text(encoding="utf-8")) if _DM_CACHE.exists() else {}
    todo_keys = [k for k in rows_by_key if k not in cache]
    if todo_keys:
        import torch
        from transformers import AutoTokenizer, T5ForConditionalGeneration
        print(f"[dm] loading {HF_MODEL_ID}@{PINNED_REVISION[:12]} (cpu)...")
        tok = AutoTokenizer.from_pretrained(HF_MODEL_ID, revision=PINNED_REVISION)
        model = T5ForConditionalGeneration.from_pretrained(HF_MODEL_ID, revision=PINNED_REVISION)
        model.eval()
        keys = list(todo_keys)
        for i in range(0, len(keys), DM_BATCH):
            chunk = keys[i:i + DM_BATCH]
            enc = tok([SLM_PREFIX + rows_by_key[k] for k in chunk],
                      return_tensors="pt", padding=True, truncation=True,
                      max_length=512)
            with torch.no_grad():
                gen = model.generate(**enc, max_length=512, num_beams=1)
            dec = tok.batch_decode(gen, skip_special_tokens=True)
            for k, raw in zip(chunk, dec):
                cache[k] = raw
            _DM_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1),
                                 encoding="utf-8")
            print(f"[dm] inferred {min(i+DM_BATCH, len(keys))}/{len(keys)}")
    parsed = {}
    for k, raw in cache.items():
        toks = []
        for t in raw.split():
            parts = t.split("_")
            # DM output is IAST; gold comparisons run in SLP1 space
            conv = lambda s: iast_to_slp1(s) if s else s
            surf = conv(parts[0]) if parts else ""
            lem = conv(parts[1]) if len(parts) > 1 and parts[1] else ""
            tags = parts[2] if len(parts) > 2 else ""
            toks.append({"surf": html.unescape(surf), "lemma": lem, "tags": tags})
        parsed[k] = toks
    return parsed


def dm_lemmas(toks) -> set[str]:
    return {norm_lemma(t["lemma"]) for t in toks if t["lemma"]}


# ------------------------------------------------------------------ scoring
def wilson(p: float, n: int, z: float = 1.96):
    if n == 0:
        return None, None
    den = 1 + z * z / n
    centre = p + z * z / (2 * n)
    spread = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return max(0.0, (centre - spread) / den), min(1.0, (centre + spread) / den)


SUPPLETIVE = [  # seed table from HeadwordLists/heritage_forms_oracle.md
    ("vah", "UQa"), ("aYj", "akta"), ("kf", "kAray"), ("sic", "secay"),
    ("tyaj", "tyakta"), ("Df", "Dfta"), ("kf", "kfRvat"), ("pF", "pAray"),
    ("pf", "pAray"), ("gam", "gata"), ("jan", "janita"), ("BU", "BUta"),
]


def related(a: str, b: str) -> bool:
    """Mechanical policy-relation hints (root<->derived stem family)."""
    if not a or not b:
        return False
    if a.startswith(b) or b.startswith(a):
        return min(len(a), len(b)) >= 3
    for x, y in SUPPLETIVE:
        if {a, b} == {norm_lemma(x), norm_lemma(y)}:
            return True
    return False


def main():
    gold = load_gold()
    print(f"gold rows: {len(gold)}")

    # ---- witness A: Heritage (live, throttled, cached)
    her_parsed = {}
    for row in gold:
        key = str(row["id"])
        sl = surface_slp1(row)
        page = heritage_fetch(sl)
        pr = heritage_parse(page)
        her_parsed[key] = pr
        flag = "" if pr["ok"] else f"  [{pr['reason']}]"
        print(f"[her] {key:>4} {sl:<28} solutions={len(pr['solutions'])}{flag}")

    # ---- witness B: DharmaMitra (local pinned model)
    dm_inputs = {str(row["id"]): surface_slp1(row) for row in gold}
    dm_iast = {k: "".join(_SLP1_TO_IAST.get(c, c) for c in s)
               for k, s in dm_inputs.items()}
    dm_toks = dm_local(dm_iast)

    # ---- scoring
    results, stats = [], {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_rows": len(gold),
        "heritage": {}, "dharmamitra": {}, "engine_vs_engine": {},
    }
    n_gold = her_ok = dm_ok = 0
    her_hit = dm_hit = both_hit = eng_hit = 0
    for row in gold:
        key = str(row["id"])
        gl_raw = row.get("lemma", "")
        gl = norm_lemma(gl_raw)
        groot = norm_lemma(row.get("root", "") or "")
        hp = her_parsed[key]
        hl = heritage_lemmas(hp)
        dtoks = dm_toks[key]
        dl = dm_lemmas(dtoks)

        rec = {
            "id": row["id"], "slp1": row["slp1"], "panel_lemma": row["panel_lemma"],
            "gold_lemma": gl_raw, "gold_norm": gl, "root": row.get("root", ""),
            "heritage_ok": hp["ok"], "heritage_stems": sorted(hl),
            "heritage_solutions": [[[s["seg"], s["stems_slp1"]] for s in sol]
                                   for sol in hp["solutions"]],
            "dm_tokens": dtoks, "dm_lemmas": sorted(dl),
        }
        if row["panel_lemma"] == "correct":
            n_gold += 1
            h_hit = gl in hl if gl else False
            d_hit = gl in dl if gl else False
            her_hit += h_hit
            dm_hit += d_hit
            both_hit += (h_hit and d_hit)
            her_ok += hp["ok"]
            dm_ok += bool(dl)
            rec.update({"vs_gold_heritage": h_hit, "vs_gold_dm": d_hit})
        e_hit = bool(hl & dl)
        eng_hit += e_hit
        rec["engine_vs_engine"] = e_hit
        results.append(rec)

    n_all = len(gold)
    for name, hit, denom in [
        ("heritage_vs_adjudication", her_hit, n_gold),
        ("dharmamitra_vs_adjudication", dm_hit, n_gold),
        ("both_witnesses_vs_adjudication", both_hit, n_gold),
        ("engine_vs_engine_all_rows", eng_hit, n_all),
    ]:
        lo, hi = wilson(hit / denom if denom else 0, denom)
        stats_key = name.split("_vs_")[0] if "_vs_" in name else name
        stats[name if name != "engine_vs_engine_all_rows" else "engine_vs_engine"] = {
            "agree": hit, "n": denom,
            "pct": round(100 * hit / denom, 1) if denom else None,
            "wilson95": [round(lo, 3) if lo is not None else None,
                         round(hi, 3) if hi is not None else None],
        }
    stats["coverage"] = {
        "heritage_analyzed_of_gold": her_ok, "dm_nonempty_of_gold": dm_ok,
        "n_adjudicated_correct": n_gold,
    }

    (GOLD_DIR / "h3171_results.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in results) + "\n",
        encoding="utf-8")
    (GOLD_DIR / "h3171_stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # ---- disagreement TSV for classification
    lines = ["id\tsurface_slp1\tgold\troot\tpanel\theritage_stems\tdm_lemmas\tverdict_hint"]
    for rec in results:
        if rec["panel_lemma"] != "correct":
            continue
        h_hit, d_hit = rec.get("vs_gold_heritage"), rec.get("vs_gold_dm")
        if h_hit and d_hit:
            continue
        gl = rec["gold_norm"]
        hints = []
        for side, lems in (("her", rec["heritage_stems"]), ("dm", rec["dm_lemmas"])):
            if any(norm_eq(x, gl) for x in lems):
                hints.append(f"{side}:convention")
            elif any(related(x, gl) for x in lems):
                hints.append(f"{side}:policy?")
        lines.append("\t".join([
            str(rec["id"]), rec["slp1"], rec["gold_lemma"], rec["root"],
            rec["panel_lemma"],
            ";".join(rec["heritage_stems"]) or "-",
            ";".join(rec["dm_lemmas"]) or "-",
            ",".join(hints) or "-",
        ]))
    (GOLD_DIR / "h3171_disagreements.tsv").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(stats, ensure_ascii=False, indent=1))


def norm_eq(a: str, b: str) -> bool:
    return a != b and nasal_norm(re.sub(r"[^A-Za-z']", "", a)) == \
        nasal_norm(re.sub(r"[^A-Za-z']", "", b))


if __name__ == "__main__":
    main()
