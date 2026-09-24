#!/usr/bin/env python3
"""H5262 — NKRYa ipm batch audit of every PWG-RU store content word.

Ruling (MG, grill 22-09-2026, docs/GRILL_NKRYA_SKILL_DECISIONS_22-09-2026.md row 6):
the audit unit is EVERY CONTENT WORD's ipm, not only collocation pairs. The goal is
to flag rare, archaic or non-existent Russian words (the «союзить» class, H5069 C02).

Four stages, each resumable and each writing one durable artifact:

  extract   store -> reports/H5262_lemma_census.json      (no network, deterministic)
  query     census -> reports/H5262_ipm_ledger.jsonl      (NKRYa, cache-first, throttled)
  flag      census+ledger -> reports/H5262_flags.json     (no network)
  report    all of the above -> a dated markdown census

The store is read-only here: this tool never writes a card back.

Gloss scope. Only the `{%...%}` spans of a card's `ru` field are audited — that is the
translated gloss proper. Everything outside them ({#SLP1#} Sanskrit, <ab> abbreviations,
<ls> source references, <lex> grammar) is apparatus the pipeline deliberately leaves
untouched (CLAUDE.md, "Key format invariant"), so it is skipped, as the mission asks.

Lemmatizer: pymorphy3 (pinned in requirements.txt), already an estate dependency — the
mission's "check RussianTranslation and RuWritingStyles before adding one" resolved to
pymorphy3, which both already carry. Its version is recorded in every artifact.

CLI:
  python src/h5262_ipm_audit.py extract
  python src/h5262_ipm_audit.py query --limit 60
  python src/h5262_ipm_audit.py query --limit 60 --offline     # cache only, 0 API calls
  python src/h5262_ipm_audit.py flag
  python src/h5262_ipm_audit.py report
  python src/h5262_ipm_audit.py --selftest                     # offline, synthetic
"""

import argparse
import io
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)                       # RussianTranslation/
REPORTS = os.path.join(REPO, "reports")

CENSUS = os.path.join(REPORTS, "H5262_lemma_census.json")
LEDGER = os.path.join(REPORTS, "H5262_ipm_ledger.jsonl")
FLAGS = os.path.join(REPORTS, "H5262_flags.json")

# ---------------------------------------------------------------- extraction

GLOSS_SPAN = re.compile(r"\{%(.*?)%\}", re.S)
BRACED_SLP1 = re.compile(r"\{#.*?#\}", re.S)
TAG = re.compile(r"<[^>]*>")
CYR_WORD = re.compile(r"[А-Яа-яЁё]+(?:-[А-Яа-яЁё]+)*")

# pymorphy POS tags that carry lexical content. PRED/NPRO/PREP/CONJ/PRCL/INTJ/NUMR are
# function words or numerals — an ipm verdict on "и" or "два" says nothing about a gloss.
CONTENT_POS = {"NOUN", "ADJF", "ADJS", "VERB", "INFN", "PRTF", "PRTS", "GRND",
               "ADVB", "COMP"}
# A proper name is out of scope by the mission ("skip ... and names").
NAME_GRAMMEMES = {"Name", "Surn", "Patr", "Geox", "Orgn", "Trad"}

# Single-letter and two-letter Cyrillic run-ins are apparatus debris, not glosses.
MIN_LEN = 3
# Lexicographic shorthand, not Russian vocabulary: "кого-л.", "что-л.", "кому-л." —
# pymorphy happily lemmatizes them ("кого-л" -> "кома-л"), and an ipm verdict on such a
# form would be meaningless. They are abbreviations, which the mission excludes.
ABBREV_DASH_L = re.compile(r"^[а-яё]+-л$")


def gloss_text(ru):
    """Concatenated {%...%} gloss spans of a card, apparatus stripped."""
    out = []
    for span in GLOSS_SPAN.findall(ru or ""):
        span = BRACED_SLP1.sub(" ", span)
        span = TAG.sub(" ", span)
        out.append(span)
    return "\n".join(out)


class Lemmatizer(object):
    def __init__(self):
        import pymorphy3
        self.version = getattr(pymorphy3, "__version__", "?")
        self.morph = pymorphy3.MorphAnalyzer()
        self._cache = {}

    def __call__(self, token):
        """(lemma, pos) for a content word, or None to skip it."""
        key = token.lower()
        if key in self._cache:
            return self._cache[key]
        result = None
        if ABBREV_DASH_L.match(key):
            self._cache[key] = None
            return None
        parses = self.morph.parse(key)
        if parses:
            p = parses[0]
            tag = p.tag
            pos = str(tag.POS or "")
            grammemes = set(str(tag).replace(" ", ",").split(","))
            if pos in CONTENT_POS and not (grammemes & NAME_GRAMMEMES):
                result = (p.normal_form.replace("ё", "е"), pos)
        self._cache[key] = result
        return result


def iter_store(path, limit=None):
    with io.open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            if limit is not None and i >= limit:
                return
            yield json.loads(line)


def extract(store, out_path, limit=None):
    lem = Lemmatizer()
    per_lemma = {}
    cards = 0
    tokens_seen = 0
    tokens_kept = 0
    skipped_pos = Counter()
    started = time.time()

    for rec in iter_store(store, limit):
        cards += 1
        text = gloss_text(rec.get("ru"))
        if not text.strip():
            continue
        card_id = rec.get("subcard") or rec.get("key1") or str(cards)
        for token in CYR_WORD.findall(text):
            tokens_seen += 1
            if len(token) < MIN_LEN:
                continue
            hit = lem(token)
            if hit is None:
                skipped_pos["non-content-or-name"] += 1
                continue
            lemma, pos = hit
            tokens_kept += 1
            slot = per_lemma.get(lemma)
            if slot is None:
                slot = per_lemma[lemma] = {
                    "lemma": lemma, "pos": Counter(), "occurrences": 0,
                    "cards": set(), "forms": Counter()}
            slot["pos"][pos] += 1
            slot["occurrences"] += 1
            slot["forms"][token.lower()] += 1
            if len(slot["cards"]) < 40:
                slot["cards"].add(card_id)

    rows = []
    for slot in per_lemma.values():
        rows.append({
            "lemma": slot["lemma"],
            "pos": slot["pos"].most_common(1)[0][0],
            "pos_all": dict(slot["pos"]),
            "occurrences": slot["occurrences"],
            "cards": sorted(slot["cards"]),
            "forms": [f for f, _ in slot["forms"].most_common(5)],
        })
    rows.sort(key=lambda r: (-r["occurrences"], r["lemma"]))

    doc = {
        "handoff": "H5262",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "store": store,
        "store_cards": cards,
        "lemmatizer": "pymorphy3 " + lem.version,
        "gloss_scope": "{%...%} spans of the `ru` field only",
        "tokens_seen": tokens_seen,
        "tokens_content": tokens_kept,
        "skipped": dict(skipped_pos),
        "distinct_lemmas": len(rows),
        "elapsed_s": round(time.time() - started, 1),
        "lemmas": rows,
    }
    _write_json(out_path, doc)
    print("extract: %d cards -> %d distinct content lemmas (%d content tokens) in %.1fs"
          % (cards, len(rows), tokens_kept, doc["elapsed_s"]))
    print("  -> " + out_path)
    return doc


# -------------------------------------------------------------------- query

def _load_ledger(path):
    done = {}
    if os.path.exists(path):
        with io.open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                done[rec["lemma"]] = rec
    return done


def query(census_path, ledger_path, limit=None, offline=False, with_19c=False,
          client=None):
    """Resumable, cache-first, throttled ipm lookups. Appends one ledger row per lemma."""
    census = _read_json(census_path)
    done = _load_ledger(ledger_path)
    todo = [r for r in census["lemmas"] if r["lemma"] not in done]
    if limit is not None:
        todo = todo[:limit]

    if client is None:
        sys.path.insert(0, HERE)
        import nkrya_client
        client = nkrya_client.NkryaClient(offline=offline)

    started = time.time()
    calls_before = client.http_calls
    written = 0
    errors = 0
    uncached = 0
    last_error = None
    fh = io.open(ledger_path, "a", encoding="utf-8")
    try:
        for row in todo:
            lemma, pos = row["lemma"], row["pos"]
            rec = {"lemma": lemma, "pos": pos,
                   "queried_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            try:
                main = client.freq(lemma, pos=_nkrya_pos(pos))
                rec["ipm"] = main.get("ipm")
                rec["category"] = main.get("category")
                if with_19c:
                    rec["hits_main"] = client.concordance(
                        _lemma_query(lemma), n=0)["hits"]
                    rec["hits_19c"] = client.concordance(
                        _lemma_query(lemma), n=0,
                        subcorpus_conditions=[_slice_19c()])["hits"]
            except Exception as exc:                 # noqa: BLE001 — logged, not fatal
                # A failure is NEVER persisted: the ledger is the resume key, so a row
                # written for an uncached-offline miss or a transient API error would
                # retire a lemma that was never actually answered.
                name = type(exc).__name__
                last_error = "%s: %s" % (name, str(exc)[:200])
                if "Offline" in name:
                    uncached += 1
                    continue
                errors += 1
                if errors >= 3 and not offline:
                    print("query: stopping after 3 live errors — last: %s" % last_error)
                    break
                continue
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh.flush()
            written += 1
    finally:
        fh.close()

    elapsed = time.time() - started
    calls = client.http_calls - calls_before
    print("query: %d verdicts written (%d census lemmas still unanswered), "
          "%d API calls, %d cache hits, %d uncached-offline, %d errors, %.1fs"
          % (written, len(census["lemmas"]) - len(done) - written, calls,
             max(written - calls, 0), uncached, errors, elapsed))
    print("  -> " + ledger_path)
    return {"written": written, "api_calls": calls, "uncached": uncached,
            "errors": errors, "last_error": last_error,
            "elapsed_s": round(elapsed, 1)}


def _nkrya_pos(pos):
    """pymorphy POS -> NKRYa word-portrait pos, or None when there is no clean map."""
    return {"NOUN": "S", "ADJF": "A", "ADJS": "A", "VERB": "V", "INFN": "V",
            "PRTF": "V", "PRTS": "V", "GRND": "V", "ADVB": "ADV"}.get(pos)


def _lemma_query(lemma):
    return [{"words": [{"reqs": [[{"type": "lex", "vals": [lemma]}]]}]}]


def _slice_19c():
    sys.path.insert(0, HERE)
    import nkrya_client
    return nkrya_client.SLICE_19C


# --------------------------------------------------------------------- flag

# Class boundaries. NKRYa's own frequency category 1 is "ipm < 1" — the mission names
# it directly; ABSENT is a null ipm (the portrait has no frequency record at all).
RARE_IPM = 1.0
# "19c share far exceeds the modern share": the 1800-1899 slice holds at least this
# share of ALL the lemma's usages, on enough 19c hits for the share to mean anything.
# The MAIN corpus is overwhelmingly post-1900, so a lemma living half in the 19c slice
# is by construction one the modern language has left behind.
ARCHAIC_SHARE = 0.5
ARCHAIC_MIN_HITS = 10


def flag(census_path, ledger_path, out_path):
    census = _read_json(census_path)
    ledger = _load_ledger(ledger_path)
    by_lemma = {r["lemma"]: r for r in census["lemmas"]}

    flagged = []
    counts = Counter()
    for lemma, rec in ledger.items():
        row = by_lemma.get(lemma)
        if row is None or rec.get("error"):
            counts["no-verdict"] += 1
            continue
        classes = []
        ipm, cat = rec.get("ipm"), rec.get("category")
        if ipm is None and cat is None:
            classes.append("ABSENT")
        elif cat == 1 or (ipm is not None and ipm < RARE_IPM):
            classes.append("RARE")
        hm, h19 = rec.get("hits_main"), rec.get("hits_19c")
        if hm and h19 and h19 >= ARCHAIC_MIN_HITS:
            rec["share_19c"] = round(float(h19) / float(hm), 4)
            if rec["share_19c"] >= ARCHAIC_SHARE:
                classes.append("ARCHAIC")
        if not classes:
            counts["clean"] += 1
            continue
        for c in classes:
            counts[c] += 1
        flagged.append({
            "lemma": lemma, "pos": row["pos"], "classes": classes,
            "ipm": ipm, "category": cat,
            "occurrences": row["occurrences"], "cards": row["cards"][:10],
            "forms": row["forms"],
            "severity": _severity(classes, ipm, row["occurrences"]),
        })

    flagged.sort(key=lambda r: (-r["severity"], r["lemma"]))
    doc = {
        "handoff": "H5262",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "thresholds": {"rare_ipm": RARE_IPM, "archaic_share": ARCHAIC_SHARE,
                       "archaic_min_hits": ARCHAIC_MIN_HITS},
        "lemmas_with_verdict": sum(1 for r in ledger.values() if not r.get("error")),
        "counts": dict(counts),
        "flagged": flagged,
    }
    _write_json(out_path, doc)
    print("flag: %d flagged of %d lemmas with a verdict (%s)"
          % (len(flagged), doc["lemmas_with_verdict"],
             ", ".join("%s=%d" % kv for kv in sorted(counts.items()))))
    print("  -> " + out_path)
    return doc


def _severity(classes, ipm, occurrences):
    """A card is worse the rarer the word AND the more cards carry it."""
    base = {"ABSENT": 100.0, "RARE": 50.0, "ARCHAIC": 30.0}
    score = sum(base.get(c, 0.0) for c in classes)
    if ipm is not None and ipm > 0:
        score += max(0.0, 10.0 - ipm)
    return round(score + min(float(occurrences), 20.0), 2)


# ------------------------------------------------------------------- report

def report(census_path, ledger_path, flags_path, out_path):
    census = _read_json(census_path)
    ledger = _load_ledger(ledger_path)
    flags = _read_json(flags_path) if os.path.exists(flags_path) else {
        "counts": {}, "flagged": []}

    pos_hist = Counter(r["pos"] for r in census["lemmas"])
    occ = [r["occurrences"] for r in census["lemmas"]]
    hapax = sum(1 for n in occ if n == 1)
    today = time.strftime("%d-%m-%Y")

    lines = []
    w = lines.append
    w("_Created: %s · Last updated: %s_" % (today, today))
    w("")
    w("# H5262 — NKRYa ipm census of the PWG-RU store's content words")
    w("")
    w("Batch audit of every Russian content word in the PWG-RU store's glosses against "
      "NKRYa word frequency (MG's ruling, grill 22-09-2026, row 6: *every content word's "
      "ipm*, not only collocation pairs). Generated by "
      "[src/h5262_ipm_audit.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h5262_ipm_audit.py) — "
      "the store is read-only throughout and no paid generation call is made.")
    w("")
    w("## 1. Extraction census (offline, deterministic)")
    w("")
    w("| Measure | Value |")
    w("|---|---|")
    w("| Store cards read | %d |" % census["store_cards"])
    w("| Gloss scope | %s |" % census["gloss_scope"])
    w("| Cyrillic tokens seen | %d |" % census["tokens_seen"])
    w("| Content tokens kept | %d |" % census["tokens_content"])
    w("| Tokens skipped (function word, name, <3 chars) | %d |"
      % census["skipped"].get("non-content-or-name", 0))
    w("| **Distinct content lemmas** | **%d** |" % census["distinct_lemmas"])
    w("| Hapax lemmas (1 occurrence) | %d |" % hapax)
    w("| Lemmatizer | %s |" % census["lemmatizer"])
    w("| Extraction wall-clock | %.1f s |" % census["elapsed_s"])
    w("")
    w("Distinct lemmas by part of speech: "
      + ", ".join("%s %d" % kv for kv in pos_hist.most_common()) + ".")
    w("")
    w("Most frequent gloss lemmas (sanity check — these should be ordinary Russian):")
    w("")
    w("| Lemma | POS | Occurrences | Cards |")
    w("|---|---|---|---|")
    for r in census["lemmas"][:15]:
        w("| %s | %s | %d | %d+ |" % (r["lemma"], r["pos"], r["occurrences"],
                                      len(r["cards"])))
    w("")
    w("## 2. NKRYa ipm lookups")
    w("")
    verdicts = sum(1 for r in ledger.values() if not r.get("error"))
    errs = Counter()
    for r in ledger.values():
        if r.get("error"):
            errs[r["error"].split(":")[0]] += 1
    w("| Measure | Value |")
    w("|---|---|")
    w("| Ledger rows | %d |" % len(ledger))
    w("| Rows with an ipm verdict | %d |" % verdicts)
    w("| Rows with an error | %d |" % (len(ledger) - verdicts))
    w("| Census lemmas still unqueried | %d |"
      % (census["distinct_lemmas"] - len(ledger)))
    w("")
    if errs:
        w("Error classes: " + ", ".join("`%s` ×%d" % kv for kv in errs.most_common())
          + ".")
        w("")
    w("## 3. Flags")
    w("")
    if flags["flagged"]:
        w("| Class | Count |")
        w("|---|---|")
        for k, v in sorted(flags["counts"].items()):
            w("| %s | %d |" % (k, v))
        w("")
        w("Top flagged lemmas by severity:")
        w("")
        w("| Lemma | POS | Classes | ipm | cat | Occurrences |")
        w("|---|---|---|---|---|---|")
        for r in flags["flagged"][:30]:
            w("| %s | %s | %s | %s | %s | %d |"
              % (r["lemma"], r["pos"], "+".join(r["classes"]),
                 r["ipm"], r["category"], r["occurrences"]))
    else:
        w("No flags yet — the ipm ledger carries no verdicts (see §2 and the blocker "
          "in the handoff close-out).")
    w("")
    unanswered = census["distinct_lemmas"] - verdicts
    if unanswered > 0:
        w("## 4. What is blocked, and by what")
        w("")
        w("%d of the %d distinct lemmas have no ipm verdict, because **no NKRYa API "
          "token exists on either box**: `python src/nkrya_client.py probe` reports "
          "no token in the Windows credential store, and the Mac keychain has no "
          "`ruscorpora-api` item either (both probed 24-09-2026). The %d verdicts "
          "above come from the H5261 C07 pilot's disk cache."
          % (unanswered, census["distinct_lemmas"], verdicts))
        w("")
        w("The human step was named when the handoffs were minted and is still open "
          "(GRILL_NKRYA_SKILL_DECISIONS_22-09-2026.md, «Human step»): MG generates a "
          "non-expiring key at https://ruscorpora.ru/accounts/profile/for-devs and "
          "stores it with")
        w("")
        w("```bash")
        w("python -c \"import keyring,getpass; "
          "keyring.set_password('ruscorpora-api','token',getpass.getpass())\"")
        w("```")
        w("")
        w("Once the key is stored, `query` resumes where it stopped — it re-asks every "
          "lemma that has no verdict row, because a failed lookup is never written to "
          "the ledger. At the client's 6 requests/minute throttle the full census is "
          "about %d hours of wall-clock for the MAIN pass alone, so the intended "
          "shape is a long unattended drain (or several), not one sitting."
          % max(1, int(round(unanswered / 6.0 / 60.0))))
        w("")
    w("## %d. Reproduce" % (5 if unanswered > 0 else 4))
    w("")
    w("```bash")
    w("python src/h5262_ipm_audit.py extract")
    w("python src/h5262_ipm_audit.py query --limit 60")
    w("python src/h5262_ipm_audit.py flag")
    w("python src/h5262_ipm_audit.py report")
    w("```")
    w("")
    w("_Гасунс_")

    _write_text(out_path, "\n".join(lines) + "\n")
    print("report -> " + out_path)
    return out_path


# ------------------------------------------------------------------ helpers

def _write_json(path, doc):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


def _read_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def default_store():
    sys.path.insert(0, HERE)
    import store_path
    return store_path.canonical_store(os.path.join(HERE, "pwg_ru_translated.jsonl"))


# ----------------------------------------------------------------- selftest

class _FakeClient(object):
    """Deterministic stand-in for NkryaClient — proves flag/severity without network."""

    TABLE = {"близкий": (120.0, 6), "союзить": (None, None), "друг": (300.0, 6),
             "доверенный": (0.4, 1)}

    def __init__(self):
        self.http_calls = 0

    def freq(self, lemma, pos=None, corpus="MAIN"):
        self.http_calls += 1
        ipm, cat = self.TABLE.get(lemma, (5.0, 4))
        return {"ipm": ipm, "category": cat}

    def concordance(self, *a, **kw):
        return {"hits": 0, "docs": 0, "lines": []}


def selftest():
    import tempfile
    checks = 0

    def ok(cond, label):
        nonlocal checks
        if not cond:
            raise SystemExit("SELFTEST FAIL: " + label)
        checks += 1

    ru = ('6) {%близкий, родственный%}; <lex>m.</lex> {%друг, союзить%} '
          '({#Api#})\n<ls>M. 2,109.</ls> {#mAturAptAM#}')
    text = gloss_text(ru)
    ok("близкий" in text and "друг" in text, "gloss spans extracted")
    ok("Api" not in text and "mAturAptAM" not in text, "{#...#} Sanskrit skipped")
    ok("lex" not in text, "tags stripped")
    ok("M. 2,109" not in text, "<ls> references outside a span are skipped")

    tmp = tempfile.mkdtemp(prefix="h5262_")
    store = os.path.join(tmp, "store.jsonl")
    with io.open(store, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"subcard": "c1", "ru": ru}, ensure_ascii=False) + "\n")
        fh.write(json.dumps({"subcard": "c2",
                             "ru": "{%доверенный и союзить%}"},
                            ensure_ascii=False) + "\n")

    census_p = os.path.join(tmp, "census.json")
    doc = extract(store, census_p)
    lemmas = {r["lemma"] for r in doc["lemmas"]}
    ok("близкий" in lemmas, "adjective lemmatized")
    ok("друг" in lemmas, "noun lemmatized")
    ok("и" not in lemmas, "conjunction dropped as a function word")
    ok(doc["store_cards"] == 2, "both cards read")

    ledger_p = os.path.join(tmp, "ledger.jsonl")
    fake = _FakeClient()
    stats = query(census_p, ledger_p, client=fake)
    ok(stats["written"] == doc["distinct_lemmas"], "one ledger row per lemma")
    again = query(census_p, ledger_p, client=fake)
    ok(again["written"] == 0, "resumable: a second pass re-queries nothing")

    miss_ledger = os.path.join(tmp, "miss.jsonl")

    class NkryaOffline(Exception):
        """Same class name the shared client raises on a cache miss in offline mode."""

    class _AllOffline(object):
        http_calls = 0

        def freq(self, lemma, pos=None, corpus="MAIN"):
            raise NkryaOffline("not cached")

    miss = query(census_p, miss_ledger, client=_AllOffline())
    ok(miss["written"] == 0 and miss["uncached"] == doc["distinct_lemmas"],
       "an uncached-offline miss is counted, never written")
    ok(not os.path.exists(miss_ledger) or os.path.getsize(miss_ledger) == 0,
       "a miss leaves the ledger empty so the lemma is retried, not retired")

    flags_p = os.path.join(tmp, "flags.json")
    fdoc = flag(census_p, ledger_p, flags_p)
    flagged = {r["lemma"]: r for r in fdoc["flagged"]}
    ok("союзить" in flagged and "ABSENT" in flagged["союзить"]["classes"],
       "a corpus-absent verb is flagged ABSENT")
    ok("доверенный" in flagged and "RARE" in flagged["доверенный"]["classes"],
       "category-1 ipm is flagged RARE")
    ok("близкий" not in flagged, "an ordinary word stays clean")
    ok(flagged["союзить"]["severity"] > flagged["доверенный"]["severity"],
       "ABSENT outranks RARE in severity")

    rep = os.path.join(tmp, "report.md")
    report(census_p, ledger_p, flags_p, rep)
    with io.open(rep, encoding="utf-8") as fh:
        body = fh.read()
    ok("союзить" in body, "report names the flagged lemma")

    print("h5262_ipm_audit selftest OK (%d checks, offline)" % checks)
    return 0


# --------------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")

    e = sub.add_parser("extract")
    e.add_argument("--store")
    e.add_argument("--limit", type=int)
    e.add_argument("--out", default=CENSUS)

    q = sub.add_parser("query")
    q.add_argument("--census", default=CENSUS)
    q.add_argument("--ledger", default=LEDGER)
    q.add_argument("--limit", type=int)
    q.add_argument("--offline", action="store_true")
    q.add_argument("--with-19c", action="store_true")

    f = sub.add_parser("flag")
    f.add_argument("--census", default=CENSUS)
    f.add_argument("--ledger", default=LEDGER)
    f.add_argument("--out", default=FLAGS)

    r = sub.add_parser("report")
    r.add_argument("--census", default=CENSUS)
    r.add_argument("--ledger", default=LEDGER)
    r.add_argument("--flags", default=FLAGS)
    r.add_argument("--out", default=os.path.join(
        REPO, "docs", "H5262_NKRYA_STORE_IPM_CENSUS_24-09-2026.md"))

    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.cmd == "extract":
        extract(args.store or default_store(), args.out, args.limit)
    elif args.cmd == "query":
        query(args.census, args.ledger, args.limit, args.offline, args.with_19c)
    elif args.cmd == "flag":
        flag(args.census, args.ledger, args.out)
    elif args.cmd == "report":
        report(args.census, args.ledger, args.flags, args.out)
    else:
        ap.print_help()
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
