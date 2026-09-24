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

# --- H5468 precision filters (H5262 spot-check, 6 of 30 flags were measurement artifacts)
# 1. Ellipsis fragments. PWG prints a prefix series elliptically and the RU gloss keeps the
#    shape: "срезающий, разрезающий, -ламывающий, -рывающий". The token after the hyphen is
#    half a word ("-ламывающий" = раз-/об-ламывающий), so pymorphy invents a lemma
#    ("ламывать") that NKRYa can only answer 0 to. The hyphen is NOT part of the token —
#    CYR_WORD starts matching after it — so the fragment is invisible unless the character
#    in front of the match is inspected. An internal hyphen ("столько-то") is consumed by
#    CYR_WORD itself, so this test never fires on a real compound.
# 2. Sentence-internal capitals are proper names. pymorphy's Name/Surn/Geox grammemes miss
#    Indic onomastics: "Сарасвати" parses as a verb ("сарасватить"). A token capitalised in
#    every one of its sentence-internal occurrences is a name, whatever pymorphy says.
# 3. An explicit term list for what neither test catches: Indological terms in the Russian
#    scholarly register that pymorphy mis-lemmatises ("бодхисаттв" -> "бодхисаттво").
#    Every entry needs a spot-check witness — see data/h5262_term_skiplist.txt.
SENTENCE_BREAK = set(".!?;|\n\r")
TERM_SKIPLIST_FILE = "h5262_term_skiplist.txt"


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


def load_term_skiplist(path=None):
    """Lowercased surface/lemma entries of data/h5262_term_skiplist.txt (may be absent)."""
    path = path or os.path.join(REPO, "data", TERM_SKIPLIST_FILE)
    out = set()
    if not os.path.exists(path):
        return out
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.split("#", 1)[0].strip().lower()
            if line:
                out.add(line)
    return out


def is_ellipsis_fragment(text, start):
    """True when the token at `start` is the tail of an ellipted prefix series.

    "срезающий, разрезающий, -ламывающий" — the hyphen stands for the prefixes printed on
    the earlier members, so "-ламывающий" is not a word and its lemma is an invention.
    """
    return start > 0 and text[start - 1] == "-"


def _sentence_internal(text, start):
    """True when the token at `start` is NOT the first token of its sentence or segment."""
    i = start - 1
    while i >= 0 and text[i].isspace():
        i -= 1
    if i < 0:
        return False
    return text[i] not in SENTENCE_BREAK


def iter_store(path, limit=None):
    with io.open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            if limit is not None and i >= limit:
                return
            yield json.loads(line)


def extract(store, out_path, limit=None, skiplist=None):
    lem = Lemmatizer()
    skip_terms = load_term_skiplist() if skiplist is None else skiplist
    per_lemma = {}
    cards = 0
    tokens_seen = 0
    tokens_kept = 0
    skipped_pos = Counter()
    # Capitalisation evidence per surface token. `cap_internal` counts capitals that are
    # NOT sentence/segment-initial — those alone prove a name. `cap_any`/`low_any` count
    # every occurrence, for the weaker second test below.
    cap_internal = Counter()
    cap_any = Counter()
    low_any = Counter()
    started = time.time()

    for rec in iter_store(store, limit):
        cards += 1
        text = gloss_text(rec.get("ru"))
        if not text.strip():
            continue
        card_id = rec.get("subcard") or rec.get("key1") or str(cards)
        for match in CYR_WORD.finditer(text):
            token = match.group(0)
            tokens_seen += 1
            if len(token) < MIN_LEN:
                continue
            if is_ellipsis_fragment(text, match.start()):
                skipped_pos["ellipsis-fragment"] += 1
                continue
            if token.lower() in skip_terms:
                skipped_pos["term-skiplist"] += 1
                continue
            hit = lem(token)
            if hit is None:
                skipped_pos["non-content-or-name"] += 1
                continue
            lemma, pos = hit
            if lemma in skip_terms:
                skipped_pos["term-skiplist"] += 1
                continue
            if token[0].isupper():
                cap_any[token.lower()] += 1
                if _sentence_internal(text, match.start()):
                    cap_internal[token.lower()] += 1
            else:
                low_any[token.lower()] += 1
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

    # A surface token capitalised in every one of its sentence-internal occurrences is a
    # proper name pymorphy failed to tag. Drop a lemma only when ALL of its surface forms
    # are such tokens — a lemma with any lowercase witness is an ordinary word that merely
    # happens to also start a name.
    # Two tests, both requiring no lowercase witness anywhere:
    #  (a) one sentence-internal capital is already decisive — no ordinary word takes one;
    #  (b) a token that is ALWAYS capitalised and occurs at least twice is a name even when
    #      every occurrence opens its gloss segment (PWG-RU glosses open lowercase, so a
    #      repeated segment-initial capital is onomastics: «Сарасвати», live 24-09-2026).
    name_tokens = {t for t, n in cap_any.items()
                   if not low_any.get(t) and (cap_internal.get(t) or n >= 2)}
    dropped_names = 0
    rows = []
    for slot in per_lemma.values():
        if name_tokens.issuperset(slot["forms"]):
            dropped_names += 1
            skipped_pos["proper-name-capitalised"] += slot["occurrences"]
            continue
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
        "precision_filters": {
            "handoff": "H5468",
            "ellipsis_fragments_skipped": skipped_pos.get("ellipsis-fragment", 0),
            "term_skiplist_skipped": skipped_pos.get("term-skiplist", 0),
            "term_skiplist_entries": len(skip_terms),
            "proper_name_lemmas_dropped": dropped_names,
        },
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


def risk_order(rows, known=None):
    """Census rows, most-likely-flagged first — the order a rate-limited pass spends calls.

    The NKRYa key sustains about 60 calls/hour per ACCOUNT (shared by every session), so
    the full census is days of wall-clock. Spending the first calls where flags live makes
    a partial pass useful: (1) lemmas pymorphy3's dictionary does not know — the
    «союзить» class sits here by construction; (2) hapax lemmas, longest first (rare
    derivations are long); (3) everything else, rarest in the store first.
    """
    if known is None:
        import pymorphy3
        known = pymorphy3.MorphAnalyzer().word_is_known

    def key(r):
        tier = 0 if not known(r["lemma"]) else (1 if r["occurrences"] == 1 else 2)
        return (tier, r["occurrences"], -len(r["lemma"]), r["lemma"])
    return sorted(rows, key=key)


# Below this MAIN ipm a lemma also gets its hit counts (MAIN + 19c slice) — the archaism
# test and the portrait-less fallback need them. Above it a word is common enough that a
# 19c over-concentration would be a curiosity, not a gloss defect, and the two extra
# calls per lemma would triple the pass (budget: ~60 calls/hour per account).
HITS_BELOW_IPM = 10.0


def _conc(client, lexgramm, subcorpus=None):
    """(hits, corpus_words) for one concordance query; an empty queryStats is 0 hits.

    Goes through the shared client's cached, throttled `_call` because the public
    `concordance()` drops corpusStats/subcorpStats, and the corpus size is what turns a
    hit count into an ipm for a lemma the word-portrait index does not carry.
    """
    payload = {"corpus": {"type": "MAIN"}, "lexGramm": lexgramm,
               "params": {"pageParams": {"page": 0, "docsPerPage": 1,
                                         "snippetsPerDoc": 1}, "seed": 5261}}
    if subcorpus:
        payload["subcorpus"] = {"sectionValues": [{"conditionValues": list(subcorpus)}]}
    raw = client._call("/lex-gramm/concordance", payload, "POST")
    hits = (raw.get("queryStats") or {}).get("wordUsageCount") or 0
    stats = (raw.get("subcorpStats") if subcorpus else raw.get("corpusStats")) or {}
    return hits, stats.get("wordUsageCount")


def lookup(client, lemma, pos, forms=(), hits_below=HITS_BELOW_IPM):
    """One lemma's NKRYa verdict: portrait ipm/category, then hits where they matter."""
    rec = {}
    main = client.freq(lemma, pos=_nkrya_pos(pos))
    rec["ipm"], rec["category"] = main.get("ipm"), main.get("category")
    if rec["ipm"] is not None and rec["ipm"] >= hits_below:
        return rec
    hm, words = _conc(client, _lemma_query(lemma))
    rec["hits_main"], rec["words_main"] = hm, words
    if hm == 0 and forms:
        # Zero lemma hits can mean NKRYa's own lemmatizer does not know the lemma while
        # the surface form is attested; ABSENT needs the form checked too.
        rec["form"] = forms[0]
        rec["form_hits_main"], _ = _conc(client, _lemma_query(forms[0], "form"))
    if hm:
        h19, w19 = _conc(client, _lemma_query(lemma), [_slice_19c()])
        rec["hits_19c"], rec["words_19c"] = h19, w19
    return rec


def query(census_path, ledger_path, limit=None, offline=False, order="risk",
          hits_below=HITS_BELOW_IPM, client=None, max_errors=3):
    """Resumable, cache-first, throttled lookups. Appends one ledger row per ANSWERED lemma."""
    census = _read_json(census_path)
    done = _load_ledger(ledger_path)
    todo = [r for r in census["lemmas"] if r["lemma"] not in done]
    if order == "risk":
        todo = risk_order(todo)
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
                rec.update(lookup(client, lemma, pos, row.get("forms") or (), hits_below))
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
                if errors >= max_errors and not offline:
                    print("query: stopping after %d live errors — last: %s"
                          % (errors, last_error))
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
          "%d API calls, %d uncached-offline, %d errors, %.1fs"
          % (written, len(census["lemmas"]) - len(done) - written, calls,
             uncached, errors, elapsed))
    print("  -> " + ledger_path)
    return {"written": written, "api_calls": calls, "uncached": uncached,
            "errors": errors, "last_error": last_error,
            "elapsed_s": round(elapsed, 1)}


def _nkrya_pos(pos):
    """pymorphy POS -> NKRYa word-portrait pos, or None when there is no clean map."""
    return {"NOUN": "S", "ADJF": "A", "ADJS": "A", "VERB": "V", "INFN": "V",
            "PRTF": "V", "PRTS": "V", "GRND": "V", "ADVB": "ADV"}.get(pos)


def _lemma_query(value, field="lex"):
    # Same sectionValues shape as csl_pyutil.nkrya.pair_query, one subsection. The first
    # version ({"words": [{"reqs": ...}]}) was never run live and the API answers it with
    # HTTP 422 «Задан некорректный запрос» (probed 24-09-2026). field="form" searches the
    # surface form instead of the lemma.
    return {"sectionValues": [{
        "conditionValues": [{"fieldName": "disambmod", "text": {"v": "main"}}],
        "subsectionValues": [
            {"conditionValues": [{"fieldName": field, "text": {"v": value}}]}]}]}


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
        basis = "portrait"
        if ipm is None:
            # No word-portrait record. The portrait index skips low-frequency lemmas, so
            # "no portrait" is not "absent": fall back to the lemma's concordance hits,
            # then to its surface form's, and call it ABSENT only when both are zero.
            ipm, basis = _hits_ipm(rec)
        if "-" in lemma:
            # NKRYa tokenizes a hyphenated compound («один-единственный», «столько-то»)
            # into separate words, so a single-token lex/form query can never match it:
            # zero hits here is a query-shape verdict, not a corpus one (live 24-09-2026).
            # H5468: a NON-zero count is no better. The spot-check caught «столько-то»
            # flagged RARE on a 5-hit portrait — a frequent pronoun undercounted by the
            # same tokenization. Any single-token verdict on a hyphenated lemma is
            # unverifiable, whatever number comes back.
            counts["unverifiable-compound"] += 1
            continue
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
            "ipm": ipm, "category": cat, "ipm_basis": basis,
            "hits_main": rec.get("hits_main"), "hits_19c": rec.get("hits_19c"),
            "share_19c": rec.get("share_19c"),
            "form": rec.get("form"), "form_hits_main": rec.get("form_hits_main"),
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


def _hits_ipm(rec):
    """(ipm, basis) from concordance hits when the portrait has none; (None, ...) if zero."""
    words = rec.get("words_main")
    for hits_key, basis in (("hits_main", "hits"), ("form_hits_main", "form")):
        hits = rec.get(hits_key)
        if hits and words:
            return round(hits * 1e6 / float(words), 5), basis
    return None, "none"


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
    basis = Counter()
    for r in flags["flagged"]:
        basis[r.get("ipm_basis") or "portrait"] += 1
    stamps = sorted(r["queried_utc"] for r in ledger.values() if r.get("queried_utc"))
    live = [r for r in ledger.values() if "hits_main" in r or r.get("queried_utc", "") > "2026-09-24T15"]
    w("Lookup order is **risk-first** (`risk_order`): lemmas pymorphy3's dictionary does not "
      "know, then hapax lemmas longest-first, then the rest — so a partial pass has already "
      "spent its calls where the flags are. A lemma below %.0f ipm (or with no NKRYa word "
      "portrait) also gets its concordance hits in MAIN and in the 1800–1899 slice; a "
      "zero-hit lemma is re-checked by its surface form before it may be called absent."
      % HITS_BELOW_IPM)
    w("")
    if stamps:
        w("First verdict %s, last %s; %d verdicts carry live hit counts."
          % (stamps[0], stamps[-1], len(live)))
        w("")
    w("## 3. Flags")
    w("")
    if flags["flagged"]:
        w("| Class | Count |")
        w("|---|---|")
        for k, v in sorted(flags["counts"].items()):
            w("| %s | %d |" % (k, v))
        w("")
        w("ipm basis of the flagged lemmas: " + ", ".join(
            "%s %d" % kv for kv in sorted(basis.items())) + " (portrait = NKRYa word "
          "portrait; hits = lemma concordance count ÷ 426.2 M words; form = surface-form "
          "count, where NKRYa's lemmatizer does not know the lemma).")
        w("")
        w("Flagged lemmas by severity:")
        w("")
        w("| Lemma | POS | Classes | ipm | Basis | Hits MAIN | Hits 1800–1899 | Store uses |")
        w("|---|---|---|---|---|---|---|---|")
        for r in flags["flagged"]:
            w("| %s | %s | %s | %s | %s | %s | %s | %d |"
              % (r["lemma"], r["pos"], "+".join(r["classes"]),
                 "—" if r["ipm"] is None else r["ipm"], r.get("ipm_basis") or "portrait",
                 _dash(r.get("hits_main")), _dash(r.get("hits_19c")), r["occurrences"]))
    else:
        w("No flags yet.")
    w("")

    spot_path = os.path.join(os.path.dirname(flags_path), "H5262_spotcheck.json")
    n = 4
    if os.path.exists(spot_path):
        spot = _read_json(spot_path)
        rows = spot["rows"]
        meas = Counter(r["measurement"] for r in rows)
        defect = Counter(r["defect"] for r in rows)
        w("## %d. Precision spot-check (%d flags, by hand)" % (n, len(rows)))
        w("")
        w(spot["method"])
        w("")
        w("| Measure | Count | Share |")
        w("|---|---|---|")
        for label, cnt in (("Measurement correct (the NKRYa verdict describes the word)",
                            meas.get("correct", 0)),
                           ("Measurement artifact (tokenizer / lemmatizer / query shape)",
                            meas.get("artifact", 0)),
                           ("Gloss defect (a reviewer should replace the word)",
                            defect.get("yes", 0)),
                           ("Legitimate word (term, deliberate archaism, fine Russian)",
                            defect.get("no", 0)),
                           ("Unclear without the scan", defect.get("unclear", 0))):
            w("| %s | %d | %.0f %% |" % (label, cnt, 100.0 * cnt / max(len(rows), 1)))
        w("")
        w("| Lemma | Classes | Measurement | Defect? | Note |")
        w("|---|---|---|---|---|")
        for r in rows:
            w("| %s | %s | %s | %s | %s |" % (r["lemma"], r["classes"], r["measurement"],
                                              r["defect"], r["note"]))
        w("")
        n += 1

    sheets_path = os.path.join(os.path.dirname(flags_path), "H5262_sheets.json")
    if os.path.exists(sheets_path):
        sheets = _read_json(sheets_path)
        w("## %d. Vote sheets (≤10 cards each)" % n)
        w("")
        for s in sheets["sheets"]:
            w("%d. Sheet %d — %d cards — %s" % (s["batch"], s["batch"], s["cards"], s["url"]))
        w("")
        w(sheets.get("note", ""))
        w("")
        n += 1

    unanswered = census["distinct_lemmas"] - verdicts
    w("## %d. Coverage and what remains" % n)
    w("")
    if unanswered > 0:
        w("%d of the %d distinct lemmas have a verdict; %d are still unqueried. The NKRYa "
          "key is rate-limited per ACCOUNT (about 60 calls/hour sustained, shared by every "
          "session using it), and a lemma costs 1–4 calls, so the remainder is a long "
          "unattended drain, not a sitting. `query` resumes exactly where it stopped: the "
          "ledger records answers only, so an interrupted or rate-limited lemma is retried, "
          "never retired (FINDINGS §646)."
          % (verdicts, census["distinct_lemmas"], unanswered))
    else:
        w("Every census lemma has a verdict.")
    w("")
    n += 1
    w("## %d. Reproduce" % n)
    w("")
    w("```bash")
    w("python src/h5262_ipm_audit.py extract          # Windows box: the store lives there")
    w("python src/h5262_ipm_audit.py query            # risk order, resumable, throttled")
    w("python src/h5262_ipm_audit.py flag")
    w("python src/h5262_card_context.py --flags reports/H5262_flags.json "
      "--out reports/H5262_flag_context.json   # Windows box")
    w("python src/build_h5262_nkrya_flag_sheet.py --batch 1")
    w("python src/h5262_ipm_audit.py report")
    w("```")
    w("")
    w("_Гасунс_")

    _write_text(out_path, "\n".join(lines) + "\n")
    print("report -> " + out_path)
    return out_path


# ------------------------------------------------------------------ helpers

def _dash(v):
    return "—" if v is None else str(v)


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
             "доверенный": (0.4, 1), "сгинуть": (None, None),
             "лемматизированный": (None, None),
             # H5468: a hyphenated compound with a REAL portrait — NKRYa's tokenizer
             # undercounts it, so the number is unverifiable, not rare.
             "столько-то": (0.4, 1)}

    def __init__(self):
        self.http_calls = 0

    def freq(self, lemma, pos=None, corpus="MAIN"):
        self.http_calls += 1
        ipm, cat = self.TABLE.get(lemma, (5.0, 4))
        return {"ipm": ipm, "category": cat}

    # (hits MAIN, hits 19c) per lemma/form; the MAIN corpus is 1e8 words, the slice 2e7.
    HITS = {"союзить": (0, 0), "доверенный": (40, 30), "сгинуть": (60, 5),
            "лемматизированный": (0, 0), "лемматизированного": (4, 0),
            "столько-то": (0, 0)}

    def _call(self, endpoint, payload, method):
        self.http_calls += 1
        cond = payload["lexGramm"]["sectionValues"][0]["subsectionValues"][0][
            "conditionValues"][0]
        main, h19 = self.HITS.get(cond["text"]["v"], (20, 2))
        if "subcorpus" in payload:
            return {"queryStats": {"wordUsageCount": h19} if h19 else {},
                    "subcorpStats": {"wordUsageCount": 20000000}}
        return {"queryStats": {"wordUsageCount": main} if main else {},
                "corpusStats": {"wordUsageCount": 100000000}}


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
        fh.write(json.dumps({"subcard": "c3",
                             "ru": "{%сгинуть; лемматизированного; столько-то%}"},
                            ensure_ascii=False) + "\n")
        # H5468 precision fixtures, one per artifact class the H5262 spot-check found.
        fh.write(json.dumps(
            {"subcard": "c4",
             "ru": "{%срезающий, разрезающий, -ламывающий%}"
                   "{%река Сарасвати и Сарасвати снова%}"
                   "{%состояния бодхисаттв в тексте%}"},
            ensure_ascii=False) + "\n")

    census_p = os.path.join(tmp, "census.json")
    skiplist = {"бодхисаттв", "бодхисаттво"}
    doc = extract(store, census_p, skiplist=skiplist)
    lemmas = {r["lemma"] for r in doc["lemmas"]}
    ok("близкий" in lemmas, "adjective lemmatized")
    ok("друг" in lemmas, "noun lemmatized")
    ok("и" not in lemmas, "conjunction dropped as a function word")
    ok(doc["store_cards"] == 4, "all cards read")

    # H5468 filter 1 — a hyphen in front of the token means an ellipted prefix series.
    ok("разрезать" in lemmas,
       "an intact member of an ellipsis series («разрезающий») is kept")
    ok("ламывать" not in lemmas,
       "the fragment after the hyphen («-ламывающий») never reaches the census")
    ok(doc["precision_filters"]["ellipsis_fragments_skipped"] == 1,
       "the skipped ellipsis fragment is counted in the census")
    # H5468 filter 2 — capitalised in every sentence-internal occurrence = a proper name.
    ok("сарасвати" not in lemmas and "сарасватить" not in lemmas,
       "an Indic proper name pymorphy reads as a verb is dropped")
    ok(doc["precision_filters"]["proper_name_lemmas_dropped"] >= 1,
       "the dropped proper name is counted in the census")
    ok("река" in lemmas,
       "a lowercase neighbour of a proper name survives the capitalisation test")
    # H5468 filter 3 — the explicit Indological term list.
    ok(not any(l.startswith("бодхисаттв") for l in lemmas),
       "a skiplisted Indological term never reaches the census")
    ok(doc["precision_filters"]["term_skiplist_skipped"] == 1,
       "the skiplist hit is counted in the census")
    ok(load_term_skiplist() >= {"бодхисаттв"},
       "the shipped data/h5262_term_skiplist.txt parses and carries its seed entry")
    ok(not is_ellipsis_fragment("столько-то", 0),
       "an INTERNAL hyphen is not an ellipsis marker — CYR_WORD consumes the whole token")

    rows = [{"lemma": "аа", "occurrences": 5}, {"lemma": "бб", "occurrences": 1},
            {"lemma": "вввв", "occurrences": 1}, {"lemma": "гг", "occurrences": 9}]
    ordered = [r["lemma"] for r in risk_order(rows, known=lambda w: w != "гг")]
    ok(ordered == ["гг", "вввв", "бб", "аа"],
       "risk order: dictionary-unknown, then hapax longest-first, then the rest")

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
    ok("hits_main" not in _load_ledger(ledger_p)["близкий"],
       "a common word (portrait ipm >= HITS_BELOW_IPM) costs one call, no hit counts")
    ok("сгинуть" in flagged and flagged["сгинуть"]["classes"] == ["RARE"]
       and flagged["сгинуть"]["ipm_basis"] == "hits",
       "portrait-less but attested: RARE from concordance hits, never ABSENT")
    by_form = [r for r in fdoc["flagged"] if "лемматизированного" in r["forms"]]
    ok(by_form and by_form[0]["classes"] == ["RARE"]
       and by_form[0]["ipm_basis"] == "form",
       "zero lemma hits but an attested surface form: RARE via the form, not ABSENT")
    ok(fdoc["counts"].get("unverifiable-compound") == 1
       and not any("-" in r["lemma"] for r in fdoc["flagged"]),
       "a hyphenated compound is unverifiable even on a category-1 portrait (H5468)")
    ok("ARCHAIC" in flagged["доверенный"]["classes"],
       "19c slice holding >= half the usages is flagged ARCHAIC")
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
    q.add_argument("--order", choices=["risk", "census"], default="risk",
                   help="risk (default): pymorphy-unknown, then hapax, first")
    q.add_argument("--hits-below", type=float, default=HITS_BELOW_IPM,
                   help="also fetch MAIN+19c hits below this portrait ipm")
    q.add_argument("--max-errors", type=int, default=3)

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
        query(args.census, args.ledger, args.limit, args.offline, args.order,
              args.hits_below, max_errors=args.max_errors)
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
