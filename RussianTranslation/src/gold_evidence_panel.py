#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gold_evidence_panel.py — the evidence a G6 gold card must carry BEFORE the vote (H1801).

MG's ruling of 28-07-2026, after the first real G6 vote (H1796): a card that shows
only the Sanskrit form, the Russian rendering and the LLM's label asks the reviewer
to rule on evidence the pipeline already owns but withheld. «Это все надо давать
ДО, а не ПОСЛЕ.»  Measured on those 20 cards: one label reversed at adjudication
once the withheld evidence surfaced (id **122**, ``na`` -> «словно», ``08_rigveda``
— Grassmann s.v. ``na`` records the Rigvedic comparison sense in the very first
line of the entry), and four further cards carried the same complaint unprompted.

This module builds the four panels and hands them to a sheet generator:

  1. **dictionary** — period-routed. Vedic ⇒ GRA (Grassmann, Rigveda) first, then
     MW/PWG; Classical / Epic / Medieval ⇒ MW + PWG.  The sense LIST for the
     headword, never a single gloss, and always stamped with which dictionary it
     came from.  This is the panel that fixes id 122.
  2. **root** — headword -> root -> the root's own meaning, routed through Whitney
     (MG named Whitney explicitly): DCS ``lemma2root`` for the root, the MW↔Whitney
     ``root_crosswalk`` for the Whitney id, ``Whitney-numbered-2026.md`` for
     Whitney's own gloss, ``mw_roots.tsv`` for the class/verb-type.
  3. **contexts** — attested occurrences of the form in the card's OWN ``work``,
     with locus, from the SamudraManthanam verse corpus, each paired with the
     published Russian translation of that passage.
  4. **glossary** — the A2/A4 ranked Saṃskṛta→Russian figures for the form
     (``SanskritRussian/surface_glossary.tsv``): how this form is actually rendered
     across the aligned corpus, ranked by frequency.  For id 122 this alone would
     have shown «как» (213×, of which ``08_rigveda`` 25×) standing beside «не».

**Never fake completeness** (MG rule 4).  Every panel returns ``searched`` — the
concrete list of what was looked in — and a panel that found nothing renders an
explicit ``evidence not found: <what was searched>`` line.  A blank panel and an
unsearched panel must not look alike; that indistinguishability is what produced
the low-information votes in the first place.

Contexts are graded and the grade is shown, because a silent "no contexts" on a
form that IS attested would be its own quiet lie:

  ``token``      the form stands as a whole word in the passage's SLP1 — best;
  ``substring``  it is inside a sandhi/compound blob (only for forms ≥4 chars,
                 or ``na`` would match every second word);
  ``glossary``   the raw text search did not localize it, but the aligned corpus
                 lexicon does attest it in that work, with a count.

Data sources are all pre-existing, canonical assets — nothing here derives a new
one (``/prior-art``, SHARED_CODE §11/§13/§17):

  ``csl-orig/v02/{gra,mw,pwg}/*.txt``       the three dictionaries
  ``csl-orig/v02/mw/mw_roots.tsv``          MW root inventory (SHARED_CODE §11)
  ``MWS/root_crosswalk/root_crosswalk.csv`` MW↔Whitney↔DCS join (SHARED_CODE §17)
  ``WhitneyRoots/Whitney-numbered-2026.md`` the 935-root hub, Whitney's glosses
  ``SanskritRussian/dcs_form2lemma.tsv``    form -> lemma (DCS)
  ``SanskritRussian/dcs_lemma2root.tsv``    lemma -> root (DCS)
  ``SanskritRussian/surface_glossary.tsv``  ranked Sa→Ru renderings (A2/A4)
  ``SamudraManthanam/web/corpus_builder/jsonl/<work>.jsonl``  the verse corpus

All of them are big and none is in CI, so every loader is BATCH: one streaming
pass per file for the whole card set, collecting only the wanted keys.  The
selftest runs entirely on tiny fixtures written to a temp dir, so it is green in
CI where none of the eight assets exists.

  python src/gold_evidence_panel.py --selftest
  python src/gold_evidence_panel.py --form na --work 08_rigveda --period Vedic
"""
import argparse
import collections
import html
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
GH = os.path.normpath(os.path.join(RT, "..", ".."))

#: SHARED_CODE §13 — the canonical CDSL-markup -> readable IAST display layer.
#: Absent in CI (sibling repo not checked out); the fallback only strips markup,
#: never transcodes, and every panel it touches is stamped ``iast_layer:
#: "fallback"`` so a degraded rendering can never pass for the canonical one.
sys.path.insert(0, os.path.join(GH, "sanskrit-util", "py"))
try:
    from sanskrit_util import source_line_to_iast as _source_line_to_iast
    IAST_LAYER = "sanskrit_util"
except ImportError:                                          # pragma: no cover
    _source_line_to_iast = None
    IAST_LAYER = "fallback"

DEFAULT_PATHS = {
    "gra": os.path.join(GH, "csl-orig", "v02", "gra", "gra.txt"),
    "mw": os.path.join(GH, "csl-orig", "v02", "mw", "mw.txt"),
    "pwg": os.path.join(GH, "csl-orig", "v02", "pwg", "pwg.txt"),
    "mw_roots": os.path.join(GH, "csl-orig", "v02", "mw", "mw_roots.tsv"),
    "mw_etymology": os.path.join(GH, "csl-orig", "v02", "mw", "mw_etymology.tsv"),
    "pwg_etymology": os.path.join(GH, "csl-orig", "v02", "pwg", "pwg_etymology.tsv"),
    "form2lemma": os.path.join(GH, "SanskritRussian", "dcs_form2lemma.tsv"),
    "lemma2root": os.path.join(GH, "SanskritRussian", "dcs_lemma2root.tsv"),
    "surface_glossary": os.path.join(GH, "SanskritRussian", "surface_glossary.tsv"),
    "root_crosswalk": os.path.join(GH, "MWS", "root_crosswalk", "root_crosswalk.csv"),
    "whitney": os.path.join(GH, "WhitneyRoots", "Whitney-numbered-2026.md"),
    "corpus": os.path.join(GH, "SamudraManthanam", "web", "corpus_builder", "jsonl"),
}

DICT_NAME = {
    "GRA": "Grassmann, Wörterbuch zum Rig-Veda",
    "MW": "Monier-Williams Sanskrit-English",
    "PWG": "Petersburger Wörterbuch (Böhtlingk-Roth)",
}

#: Works whose language is Vedic even when the stratum label is coarser — the
#: Saṃhitās and the early Upaniṣads/Brāhmaṇas.  Routing reads BOTH the card's
#: ``period`` and its ``work``: id 122 is labelled Vedic AND sits in 08_rigveda,
#: and it was the dictionary-vs-work mismatch that produced the wrong ruling.
VEDIC_WORK = re.compile(
    r"^(\d+_(rigveda|atharvaveda|samaveda|yajurveda)"
    r"|.*-up|.*brahmana.*|.*aranyaka.*|.*samhita.*)$", re.I)
#: GRA covers the Rigveda only — an Upaniṣad headword legitimately misses there,
#: so Vedic routing keeps MW/PWG behind GRA rather than stopping at a GRA miss.
RIGVEDIC_WORK = re.compile(r"^\d+_rigveda$", re.I)

MAX_ENTRIES_PER_DICT = 3
#: Total entries a dictionary panel shows. A compound card tries many keys, and
#: without a ceiling the weaker keys bury the strong one.
MAX_DICT_ENTRIES_SHOWN = 4
MAX_LEMMAS = 3
#: A homograph guard. ``na`` resolves in DCS to six lemmas, among them the
#: pronoun stem ``mad`` (the enclitic ``nas`` "us", 836×) beside the particle
#: ``na`` (63 304×).  Left unfiltered the panel served Grassmann's √mad
#: "hilarate" as a sense of ``na`` — a fabricated chain of exactly the kind rule
#: 4 forbids.  A candidate must carry at least this share of the top candidate's
#: corpus count to be shown; the rejects are still named in ``searched``.
MIN_LEMMA_SHARE = 0.1
#: Whitney's roots are VERBAL roots.  A particle or a pronoun has no dhātu, so
#: chaining one to a root is always a homograph accident, never a derivation.
ROOTABLE_UPOS = ("VERB", "NOUN", "ADJ", "")
MAX_CONTEXTS = 3
MAX_GLOSSES = 8
ENTRY_CHARS = 700
CONTEXT_CHARS = 260
#: Below this length a substring hit is noise, not evidence (``na`` is inside
#: every second Sanskrit word).
MIN_SUBSTRING_FORM = 4

_HDR = re.compile(r"^<L>(?P<L>[^<]*)<pc>(?P<pc>[^<]*)<k1>(?P<k1>[^<]*)"
                  r"<k2>(?P<k2>[^<]*)(?:<h>(?P<h>[^<]*))?(?:<e>(?P<e>[^<]*))?")
_TOKEN_SPLIT = re.compile(r"[^A-Za-z']+")
_TAGS = re.compile(r"<[^>]+>")
_BRACES = re.compile(r"\{[@#%](.*?)[@#%]\}")


# --------------------------------------------------------------------- routing
def route_dictionaries(period, work):
    """Which dictionaries this card's sense list must come from, in order.

    Returns ``(codes, reason)``.  MG's rule: Vedic ⇒ GRA first (Grassmann is the
    Rigveda dictionary), Classical / Epic / Medieval ⇒ MW + PWG.
    """
    period = (period or "").strip()
    work = (work or "").strip()
    vedic_period = period.lower().startswith("vedic")
    vedic_work = bool(VEDIC_WORK.match(work))
    if vedic_period or vedic_work:
        why = []
        if vedic_period:
            why.append("period=%s" % period)
        if vedic_work:
            why.append("work=%s" % work)
        if RIGVEDIC_WORK.match(work):
            return ["GRA", "MW", "PWG"], "ведийская маршрутизация (%s) → GRA первым" % ", ".join(why)
        return ["GRA", "MW", "PWG"], (
            "ведийская маршрутизация (%s) → GRA первым; GRA покрывает только РВ, "
            "поэтому MW/PWG остаются в цепочке" % ", ".join(why))
    return ["MW", "PWG"], "непедийская маршрутизация (period=%s, work=%s) → MW + PWG" % (
        period or "?", work or "?")


# --------------------------------------------------------------------- loaders
def load_form2lemma(path, forms):
    """form_slp1 -> [(lemma, upos, count)] sorted by descending corpus count."""
    want, out = set(forms), {}
    if not os.path.exists(path):
        return out
    with io.open(path, encoding="utf-8") as fh:
        fh.readline()
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 3 and p[0] in want:
                try:
                    n = int(p[3]) if len(p) > 3 else 0
                except ValueError:
                    n = 0
                out.setdefault(p[0], []).append((p[1], p[2], n))
    for k in out:
        out[k].sort(key=lambda t: -t[2])
    return out


def split_lemmas(lemmas):
    """(kept, dropped) — the homograph guard, by corpus-count share.

    Returns the rejects too, so the panel can NAME what it declined to use
    instead of silently narrowing the evidence.
    """
    if not lemmas:
        return [], []
    top = max(n for _lm, _u, n in lemmas) or 0
    if top <= 0:
        return lemmas[:MAX_LEMMAS], lemmas[MAX_LEMMAS:]
    kept = [t for t in lemmas if t[2] >= top * MIN_LEMMA_SHARE]
    dropped = [t for t in lemmas if t[2] < top * MIN_LEMMA_SHARE]
    return kept[:MAX_LEMMAS], dropped + kept[MAX_LEMMAS:]


def load_lemma2root(path):
    """lemma_slp1 -> [(root_slp1, how)].  Small file (12.5k rows), loaded whole."""
    out = {}
    if not os.path.exists(path):
        return out
    with io.open(path, encoding="utf-8") as fh:
        fh.readline()
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 2:
                out.setdefault(p[0], []).append((p[1], p[2] if len(p) > 2 else ""))
    return out


def load_surface_glossary(path, forms):
    """form_slp1 -> [{ru, n, n_form_total, works}] ranked by descending n."""
    want, out = set(forms), {}
    if not os.path.exists(path):
        return out
    with io.open(path, encoding="utf-8") as fh:
        fh.readline()
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 5 and p[0] in want:
                try:
                    n, tot = int(p[3]), int(p[4])
                except ValueError:
                    n, tot = 0, 0
                works = {}
                for chunk in (p[5] if len(p) > 5 else "").split("|"):
                    if ":" in chunk:
                        w, _, c = chunk.rpartition(":")
                        try:
                            works[w] = int(c)
                        except ValueError:
                            pass
                out.setdefault(p[0], []).append(
                    {"sa": p[1], "ru": p[2], "n": n, "n_form_total": tot, "works": works})
    for k in out:
        out[k].sort(key=lambda d: -d["n"])
    return out


def clean_entry_text(raw, code):
    """One csl-orig entry body -> readable text (SHARED_CODE §13)."""
    if _source_line_to_iast is not None:
        try:
            return _source_line_to_iast(raw, code.lower()).strip()
        except Exception:                                    # pragma: no cover
            pass
    return _TAGS.sub("", _BRACES.sub(r"\1", raw)).replace("¦", "").strip()


def load_dict_entries(path, code, keys, max_per_key=MAX_ENTRIES_PER_DICT):
    """k1 -> [{L, pc, hom, text}] for the wanted headwords. One streaming pass.

    Body lines that are pure citation blocks (GRA's ``<div n="TS">`` attestation
    lists) are dropped from the displayed sense text and counted instead — they
    are references, and the panel's job is the SENSE list.
    """
    want, out = set(keys), {}
    if not want or not os.path.exists(path):
        return out
    k1 = meta = None
    body, cites = [], 0
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("<L>"):
                m = _HDR.match(line)
                k1 = m.group("k1") if m else None
                meta = ((m.group("L"), m.group("pc"), m.group("h")) if m
                        else (None, None, None))
                body, cites = [], 0
                continue
            if line.startswith("<LEND>"):
                if k1 in want and len(out.get(k1, [])) < max_per_key:
                    text = clean_entry_text(" ".join(body), code)
                    if len(text) > ENTRY_CHARS:
                        text = text[:ENTRY_CHARS].rsplit(" ", 1)[0] + " …"
                    out.setdefault(k1, []).append(
                        {"L": meta[0], "pc": meta[1], "hom": meta[2],
                         "text": text, "citation_lines": cites})
                k1 = None
                continue
            if k1 in want:
                if line.startswith("<div"):
                    cites += 1
                else:
                    body.append(line)
    return out


def load_mw_roots(path):
    """root_slp1 -> {root_iast, verb_type, classes, whitney_anchor}."""
    out = {}
    if not os.path.exists(path):
        return out
    with io.open(path, encoding="utf-8") as fh:
        head = fh.readline().rstrip("\n").split("\t")
        idx = {c: i for i, c in enumerate(head)}
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) <= idx.get("k1_slp1", 2):
                continue

            def get(col):
                i = idx.get(col)
                return p[i] if i is not None and i < len(p) else ""
            out.setdefault(get("k1_slp1"), {
                "root_iast": get("root_iast"), "verb_type": get("verb_type"),
                "classes": get("classes"), "whitney_anchor": get("whitney_anchor"),
                "mw_L": get("mw_L")})
    return out


def _load_tsv_map(path, key_col, val_cols, keep=None):
    """key -> [tuple(val_cols)] over a headered TSV, with an optional row filter."""
    out = {}
    if not os.path.exists(path):
        return out
    with io.open(path, encoding="utf-8") as fh:
        head = fh.readline().rstrip("\n").split("\t")
        idx = {c: i for i, c in enumerate(head)}
        if key_col not in idx:
            return out
        for line in fh:
            p = line.rstrip("\n").split("\t")

            def get(col):
                i = idx.get(col)
                return p[i] if i is not None and i < len(p) else ""
            if keep and not keep(get):
                continue
            k = get(key_col)
            if k:
                out.setdefault(k, []).append(tuple(get(c) for c in val_cols))
    return out


def load_mw_etymology(path):
    """MW headword_slp1 -> [(root_slp1, root_via, deriv_type)] (SHARED_CODE §11:
    the DERIVATION table, distinct from the root INVENTORY ``mw_roots.tsv``)."""
    return _load_tsv_map(path, "headword_slp1",
                         ("root_slp1", "root_via", "deriv_type"),
                         keep=lambda get: bool(get("root_slp1")))


def load_pwg_etymology(path):
    """PWG headword_slp1 -> [(source_slp1, deriv_marker, source_gloss_de)],
    restricted to the rows PWG itself marks as deriving from a ROOT."""
    return _load_tsv_map(path, "headword_slp1",
                         ("source_slp1", "deriv_marker", "source_gloss_de"),
                         keep=lambda get: (get("is_root") or "").strip().lower()
                         == "true" and bool(get("source_slp1")))


def _split_csv_line(line):
    """Minimal RFC4180 field split — root_crosswalk quotes its class lists."""
    out, cur, q = [], [], False
    for ch in line:
        if ch == '"':
            q = not q
        elif ch == "," and not q:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out


def _norm_root_iast(s):
    """``2 akṣ`` / ``√gam`` / ``gam`` all fold to ``akṣ`` / ``gam``."""
    s = (s or "").strip().lstrip("√").strip()
    s = re.sub(r"^\d+\s+", "", s)
    return s.strip()


def load_root_crosswalk(path):
    """normalized Whitney root (IAST) -> [{whitney_id, root, in_MW, mw_classes, dcs_freq}]."""
    out = {}
    if not os.path.exists(path):
        return out
    with io.open(path, encoding="utf-8") as fh:
        head = _split_csv_line(fh.readline().rstrip("\n"))
        idx = {c: i for i, c in enumerate(head)}
        for line in fh:
            p = _split_csv_line(line.rstrip("\n"))
            if len(p) < 2:
                continue

            def get(col):
                i = idx.get(col)
                return p[i] if i is not None and i < len(p) else ""
            out.setdefault(_norm_root_iast(get("root")), []).append({
                "whitney_id": get("whitney_id"), "root": get("root"),
                "in_MW": get("in_MW"), "mw_classes": get("mw_classes"),
                "dcs_freq": get("dcs_freq")})
    return out


_WHITNEY_LINE = re.compile(r"^(\d+)\.\s*(.*)$")


def load_whitney(path):
    """whitney_id -> Whitney's own numbered line (root + his English gloss)."""
    out = {}
    if not os.path.exists(path):
        return out
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            m = _WHITNEY_LINE.match(line.strip())
            if m:
                out[m.group(1)] = m.group(2).strip()
    return out


# --------------------------------------------------------------------- corpus
def _windows(text, needle, width=CONTEXT_CHARS):
    """A readable window around the first hit in a multi-verse blob."""
    i = text.find(needle)
    if i < 0:
        if len(text) <= width:
            return text
        return text[:width].rsplit(" ", 1)[0] + " …"
    lo = max(0, i - width // 2)
    hi = min(len(text), i + len(needle) + width // 2)
    return ("… " if lo else "") + text[lo:hi].strip() + (" …" if hi < len(text) else "")


def corpus_contexts(corpus_dir, work, form_slp1, limit=MAX_CONTEXTS):
    """Attested occurrences of ``form_slp1`` in ``work``, with locus + the
    published Russian of that passage.  Returns ``(hits, tier, searched)``."""
    path = os.path.join(corpus_dir, (work or "") + ".jsonl")
    searched = ["корпус %s.jsonl (токен, затем подстрока)" % (work or "?")]
    if not work or not os.path.exists(path):
        return [], "missing", ["корпус %s.jsonl — файла нет" % (work or "?")]
    sa, ru = [], {}
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("deleted"):
                continue
            if r.get("seg") == "sa":
                sa.append(r)
            elif r.get("seg") == "ru":
                ru[r.get("group")] = r
    exact, sub = [], []
    for r in sa:
        slp1 = r.get("slp1") or ""
        if not slp1:
            continue
        if form_slp1 in set(t for t in _TOKEN_SPLIT.split(slp1) if t):
            exact.append(r)
        elif len(form_slp1) >= MIN_SUBSTRING_FORM and form_slp1 in slp1:
            sub.append(r)
        if len(exact) >= limit:
            break
    chosen, tier = (exact, "token") if exact else (sub, "substring")
    hits = []
    for r in chosen[:limit]:
        counterpart = ru.get(r.get("group")) or {}
        hits.append({
            "passage": r.get("passage"), "work": work,
            "sa": _windows(r.get("text") or "", ""),
            "sa_slp1_window": _windows(r.get("slp1") or "", form_slp1),
            "ru": _windows(counterpart.get("text") or "", ""),
            "has_ru": bool(counterpart.get("text")),
        })
    return hits, (tier if hits else "none"), searched


# ---------------------------------------------------------------------- panels
def dictionary_panel(row, dict_entries, lemmas):
    """Period-routed sense list. ``dict_entries`` is {code: {k1: [entry]}}."""
    codes, reason = route_dictionaries(row.get("period"), row.get("work"))
    keys = dictionary_keys(row, lemmas)
    found, searched = [], []
    for code in codes:
        per_dict = dict_entries.get(code) or {}
        for key, why in keys:
            searched.append("%s k1=%s (%s)" % (code, key, why))
            for entry in per_dict.get(key, []):
                if len(found) >= MAX_DICT_ENTRIES_SHOWN:
                    break
                found.append({"dict": code, "dict_name": DICT_NAME.get(code, code),
                              "key": key, "via": why, **entry})
        if found:
            break
    return {"panel": "dictionary", "found": bool(found), "routing": reason,
            "routed_to": codes, "keys": [k for k, _w in keys], "entries": found,
            "searched": searched, "iast_layer": IAST_LAYER}


def headword_variants(form):
    """[(key, why)] — bounded, LABELLED normalizations of a card's form.

    The gold scaffold's ``slp1`` field is the corpus aligner's token, and it is
    not always true SLP1: ``advaita`` stands for ``advEta`` (the ``ai``/``au``
    digraphs were never folded) and ``avAk-SAKaH`` keeps a compound hyphen and a
    case ending.  Both miss every dictionary on the raw key, and both are one
    mechanical step from a real headword — ``advEta`` and ``avAkSAKa`` are
    entries in MW *and* PWG.  So the lookup tries a small closed set of
    transcoding/segmentation variants and REPORTS which one hit; it never
    guesses at meaning, and a variant hit is visibly a variant hit.
    """
    out, seen = [], set()

    def add(key, why):
        if key and key not in seen:
            seen.add(key)
            out.append((key, why))

    def expand(base, why):
        """All spellings of ONE base, before moving to a weaker base.

        Order matters: a whole-word key must be exhausted before a compound
        PART is tried, or ``avAk`` ("downwards") outranks ``avAkSAKa``
        ("having shoots turned downwards") — the part wins over the word the
        card is actually about.
        """
        for key, tag in ((base, why),
                         (base.replace("ai", "E").replace("au", "O"),
                          "%s + ai/au → E/O" % why)):
            add(key, tag)
            if key.endswith("H") and len(key) > 2:
                add(key[:-1], "%s без конечной висарги" % tag)

    form = form or ""
    expand(form, "как в карточке")
    if "-" in form:
        expand(form.replace("-", ""), "композит без дефиса")
        for part in form.split("-"):
            expand(part, "часть композита")
    return out


def dictionary_keys(row, lemmas):
    """[(key, why)] — the card's own form (and its variants) first, then its DCS
    lemmas (homograph-filtered — see ``MIN_LEMMA_SHARE``)."""
    kept, _dropped = split_lemmas(lemmas)
    keys, seen = [], set()
    for key, why in headword_variants(row.get("slp1")):
        seen.add(key)
        keys.append((key, why))
    for lemma, _u, _n in kept:
        if lemma and lemma not in seen:
            seen.add(lemma)
            keys.append((lemma, "лемма DCS"))
    return keys


def root_panel(row, lemmas, l2r, mw_roots, xwalk, whitney,
               mw_etym=None, pwg_etym=None):
    """Headword -> root -> the root's own meaning, routed through Whitney.

    Three derivation sources, each stamped on the line it produced, because they
    disagree and a reviewer must see WHICH one is talking: DCS ``lemma2root``
    (corpus-derived), MW's own ``mw_etymology`` root attribution, and PWG's
    ``von X`` derivation.  ``dcs_lemma2root`` alone covers only the verbal side —
    it left 18 of the 20 starter cards rootless, which for a sheet MG asked to
    carry a root line is a miss, not a fact about the words.
    """
    mw_etym, pwg_etym = mw_etym or {}, pwg_etym or {}
    kept, dropped = split_lemmas(lemmas)
    searched, roots, seen = [], [], set()
    for lemma, upos, _n in dropped:
        searched.append("омограф отклонён по частотности: %s (%s)" % (lemma, upos))

    def add(root_slp1, lemma, how, src):
        if not root_slp1 or (root_slp1, src) in seen:
            return
        seen.add((root_slp1, src))
        mw = mw_roots.get(root_slp1) or {}
        iast = _norm_root_iast(mw.get("root_iast") or "")
        wid, wline = None, None
        if iast:
            searched.append("root_crosswalk[%s]" % iast)
            for cand in xwalk.get(iast, []):
                wid = cand.get("whitney_id")
                wline = whitney.get(wid)
                break
        roots.append({
            "root_slp1": root_slp1, "root_iast": iast or None, "how": how,
            "lemma": lemma, "source": src, "mw_classes": mw.get("classes") or None,
            "verb_type": mw.get("verb_type") or None,
            "whitney_id": wid, "whitney_line": wline})

    # The card's own surface form is a legitimate etymology key too — the MW/PWG
    # tables are headword-keyed, and an uninflected headword card (``advaita``,
    # ``saMsAra``) never needs the lemma detour.  Candidates are collected as
    # lemma -> {upos}: when the form IS its own lemma (``na``), merging the two
    # keeps the part-of-speech verdict attached instead of letting the bare
    # surface key silently outrank it.
    order, by_upos = [], {}
    for lemma, upos, _n in kept:
        if lemma not in by_upos:
            order.append(lemma)
            by_upos[lemma] = set()
        by_upos[lemma].add(upos)
    form = row.get("slp1")
    if form and form not in by_upos:
        order.insert(0, form)
        by_upos[form] = set()
    for lemma in order:
        tags = set(u for u in by_upos[lemma] if u)
        if tags and not (tags & set(ROOTABLE_UPOS)):
            searched.append("%s (%s) — не глагольная часть речи, корень не выводится"
                            % (lemma, "/".join(sorted(tags))))
            continue
        searched.append("dcs_lemma2root[%s]" % lemma)
        for root_slp1, how in l2r.get(lemma, []):
            add(root_slp1, lemma, how, "DCS")
        searched.append("mw_etymology[%s]" % lemma)
        for root_slp1, via, deriv in mw_etym.get(lemma, []):
            add(root_slp1, lemma, via or deriv or "fr-root", "MW")
        searched.append("pwg_etymology[%s]" % lemma)
        for src_slp1, marker, _gloss in pwg_etym.get(lemma, []):
            add(src_slp1, lemma, marker or "von", "PWG")
    if not lemmas:
        searched.append("dcs_form2lemma[%s] — лемма не найдена" % row.get("slp1"))
    return {"panel": "root", "found": bool(roots), "roots": roots,
            "lemmas": [{"lemma": lm, "upos": u, "n": n} for lm, u, n in kept],
            "dropped_lemmas": [{"lemma": lm, "upos": u, "n": n} for lm, u, n in dropped],
            "searched": searched}


def context_panel(row, corpus_dir, surface):
    """≥1 attested occurrence in the card's own work — or why there is none."""
    form = row.get("slp1") or ""
    work = row.get("work") or ""
    hits, tier, searched = corpus_contexts(corpus_dir, work, form)
    attested = None
    if not hits:
        for g in surface.get(form, []):
            if work in g.get("works", {}):
                attested = (attested or 0) + g["works"][work]
        searched.append("surface_glossary[%s].works[%s]" % (form, work))
        if attested:
            tier = "glossary"
    return {"panel": "contexts", "found": bool(hits), "tier": tier,
            "hits": hits, "glossary_attested_n": attested, "searched": searched}


def glossary_panel(row, surface):
    """A2/A4: how this form is actually rendered into Russian, ranked."""
    form = row.get("slp1") or ""
    rows = surface.get(form, [])
    work = row.get("work") or ""
    out = []
    for g in rows[:MAX_GLOSSES]:
        out.append({"ru": g["ru"], "n": g["n"], "n_form_total": g["n_form_total"],
                    "in_this_work": g.get("works", {}).get(work, 0),
                    "top_works": sorted(g.get("works", {}).items(),
                                        key=lambda kv: -kv[1])[:5]})
    return {"panel": "glossary", "found": bool(out), "glosses": out,
            "n_variants": len(rows),
            "searched": ["surface_glossary[%s]" % form]}


# ------------------------------------------------------------------- batch API
def build_panels(rows, paths=None):
    """All four panels for every row. One streaming pass per big asset."""
    paths = dict(DEFAULT_PATHS, **(paths or {}))
    forms = [r.get("slp1") for r in rows if r.get("slp1")]
    lemmas_by_form = load_form2lemma(paths["form2lemma"], forms)
    surface = load_surface_glossary(paths["surface_glossary"], forms)
    l2r = load_lemma2root(paths["lemma2root"])
    mw_roots = load_mw_roots(paths["mw_roots"])
    mw_etym = load_mw_etymology(paths["mw_etymology"])
    pwg_etym = load_pwg_etymology(paths["pwg_etymology"])
    xwalk = load_root_crosswalk(paths["root_crosswalk"])
    whitney = load_whitney(paths["whitney"])

    wanted = collections.defaultdict(set)
    for r in rows:
        codes, _ = route_dictionaries(r.get("period"), r.get("work"))
        for key, _why in dictionary_keys(r, lemmas_by_form.get(r.get("slp1"), [])):
            for code in codes:
                wanted[code].add(key)
    dict_entries = {code: load_dict_entries(paths[code.lower()], code, keys)
                    for code, keys in wanted.items()}

    out = {}
    for r in rows:
        lemmas = lemmas_by_form.get(r.get("slp1"), [])
        out[str(r["id"])] = {
            "dictionary": dictionary_panel(r, dict_entries, lemmas),
            "root": root_panel(r, lemmas, l2r, mw_roots, xwalk, whitney,
                               mw_etym, pwg_etym),
            "contexts": context_panel(r, paths["corpus"], surface),
            "glossary": glossary_panel(r, surface),
        }
    return out


# --------------------------------------------------------------------- render
def _esc(s):
    return html.escape("" if s is None else str(s))


def _not_found(panel):
    return ('<div class="muted"><b>evidence not found</b>: искали — %s</div>'
            % _esc(" · ".join(panel.get("searched") or ["(ничего)"])))


def render_dictionary(panel):
    head = '<div class="muted">%s</div>' % _esc(panel["routing"])
    if not panel["found"]:
        return head + _not_found(panel)
    parts = [head]
    for e in panel["entries"]:
        hom = (" <sup>%s</sup>" % _esc(e["hom"])) if e.get("hom") else ""
        cites = ("" if not e.get("citation_lines") else
                 ' <span class="muted">(+%d строк цитат)</span>' % e["citation_lines"])
        parts.append('<div><b>%s</b>%s · <i>%s</i> · заголовок <b>%s</b> '
                     '<span class="muted">(%s)</span> · L%s pc%s%s<pre>%s</pre></div>'
                     % (_esc(e["dict"]), hom, _esc(e["dict_name"]), _esc(e["key"]),
                        _esc(e.get("via") or ""), _esc(e["L"]), _esc(e["pc"]),
                        cites, _esc(e["text"])))
    if panel.get("iast_layer") == "fallback":
        parts.append('<div class="muted">рендер IAST: fallback '
                     '(sanskrit-util недоступен) — разметка снята, транслитерация не выполнена</div>')
    return "".join(parts)


def render_root(panel):
    if not panel["found"]:
        return _not_found(panel)
    parts = []
    if panel.get("lemmas"):
        parts.append('<div class="muted">лемма: %s</div>' % _esc(", ".join(
            "%s (%s, %d×)" % (d["lemma"], d["upos"], d["n"]) for d in panel["lemmas"])))
    for r in panel["roots"]:
        w = ("Whitney %s — %s" % (r["whitney_id"], r["whitney_line"])
             if r.get("whitney_line") else
             "Whitney: соответствие не найдено (root_crosswalk)")
        cls = (" · класс %s" % r["mw_classes"]) if r.get("mw_classes") else ""
        parts.append('<div>√<b>%s</b>%s <span class="muted">(%s: %s ← %s)</span><br>%s</div>'
                     % (_esc(r["root_iast"] or r["root_slp1"]), _esc(cls),
                        _esc(r.get("source") or "?"), _esc(r["how"]),
                        _esc(r["lemma"]), _esc(w)))
    return "".join(parts)


def render_contexts(panel):
    if not panel["found"]:
        if panel.get("tier") == "glossary" and panel.get("glossary_attested_n"):
            return ('<div class="muted">Точное вхождение в тексте не локализовано, но '
                    'выровненный корпусный лексикон фиксирует форму в этой работе '
                    '%d×.</div>' % panel["glossary_attested_n"]) + _not_found(panel)
        return _not_found(panel)
    tier = {"token": "точное словоформенное совпадение",
            "substring": "форма внутри сандхи/композита"}.get(panel["tier"], panel["tier"])
    parts = ['<div class="muted">%s · %d контекст(ов)</div>' % (_esc(tier), len(panel["hits"]))]
    for h in panel["hits"]:
        ru = (_esc(h["ru"]) if h.get("has_ru")
              else '<span class="muted">русского сегмента для этого пассажа нет</span>')
        parts.append('<div><b>%s %s</b><pre>%s</pre><pre>%s</pre></div>'
                     % (_esc(h["work"]), _esc(h["passage"]), _esc(h["sa"]), ru))
    return "".join(parts)


def render_glossary(panel):
    if not panel["found"]:
        return _not_found(panel)
    rows = []
    for g in panel["glosses"]:
        here = (" <b>(в этой работе %d×)</b>" % g["in_this_work"]) if g["in_this_work"] else ""
        works = ", ".join("%s:%d" % (w, n) for w, n in g["top_works"])
        rows.append("<tr><td>%s</td><td>%d</td><td>%s%s</td></tr>"
                    % (_esc(g["ru"]), g["n"], _esc(works), here))
    return ('<div class="muted">%d вариантов перевода этой формы в выровненном корпусе</div>'
            "<table><tr><th>русский</th><th>n</th><th>работы</th></tr>%s</table>"
            % (panel["n_variants"], "".join(rows)))


def render_panels(panels):
    """[(title, html)] in the order a reviewer should read them."""
    return [
        ("Словарь (по периоду)", render_dictionary(panels["dictionary"])),
        ("Корень (Whitney)", render_root(panels["root"])),
        ("Контексты из этой же работы", render_contexts(panels["contexts"])),
        ("Как эта форма переводится в корпусе (A2/A4)", render_glossary(panels["glossary"])),
    ]


def coverage(panels_by_id):
    """Per-panel found-counts — the number the diff report is built on."""
    c = collections.Counter()
    for p in panels_by_id.values():
        for name in ("dictionary", "root", "contexts", "glossary"):
            if p[name]["found"]:
                c[name] += 1
        c["cards"] += 1
        if any(p[n]["found"] for n in ("dictionary", "root", "contexts", "glossary")):
            c["any"] += 1
    return c


# -------------------------------------------------------------------- selftest
FIXTURE_GRA = """<L>4792<pc>0700<k1>na<k2>na
{@ná@}¦ Verneinungswort, theils verneinend {%nicht%}, theils {%wie, gleichwie%}.
<div n="TS">-a 1〉 {5,4}; {7,7}.
<LEND>
<L>6533<pc>0977<k1>mad<k2>mad
{@√mad@}¦ {%wallen, sprudeln%}, sich berauschen.
<LEND>
"""
FIXTURE_MW = """<L>1<pc>1,1<k1>rAjan<k2>rAjan<h>1<e>1
<s>rAjan</s> ¦ <lex>m.</lex> a king, sovereign, prince
<LEND>
<L>2<pc>1,2<k1>advEta<k2>advEta<e>1
<s>advEta</s> ¦ <lex>n.</lex> non-duality, identity of Brahman and the Self
<LEND>
<L>3<pc>1,3<k1>avAkSAKa<k2>avAkSAKa<e>1
<s>avAkSAKa</s> ¦ <lex>mfn.</lex> having the branches downwards
<LEND>
"""
FIXTURE_PWG = """<L>2<pc>1-0002<k1>rAjan<k2>rAjan
{#rAjan#}¦ <ab>m.</ab> {%König, Fürst%}
<LEND>
"""
#: ``na``'s real DCS lemma set, abridged: the particle that carries the form,
#: plus the pronoun stem ``mad`` that is the homograph trap (the enclitic
#: ``nas`` "us") and a rare NOUN reading.
FIXTURE_F2L = ("form_slp1\tlemma_slp1\tupos\tcount\n"
               "na\tna\tPART\t63304\n"
               "na\tmad\tPRON\t836\n"
               "na\tna\tNOUN\t15\n"
               "rAjAnam\trAjan\tNOUN\t120\n"
               "gacCati\tgam\tVERB\t99\n")
FIXTURE_L2R = ("lemma_slp1\troot_slp1\thow\n"
               "gam\tgam\tself\n"
               "mad\tmad\tself\n")
FIXTURE_MWROOTS = ("mw_L\te\tk1_slp1\troot_iast\tverb_type\tclasses\t"
                   "whitney_anchor\twestergaard\n"
                   "500\t1\tgam\tgam\tgenuineroot\t1P\t\t\n"
                   "600\t1\tmad\tmad\tgenuineroot\t4P\t\t\n"
                   "700\t1\trAj\trāj\tgenuineroot\t1P\t\t\n")
FIXTURE_MW_ETYM = (
    "L_id\theadword\theadword_slp1\troot\troot_slp1\troot_via\troot_class\t"
    "root_canonical\tderiv_type\n"
    "10\trājan\trAjan\trāj\trAj\tfr-root\t1P\tY\troot-attribution\n")
FIXTURE_PWG_ETYM = (
    "L_id\theadword\theadword_slp1\tsource\tsource_slp1\tsource_class\tis_root\t"
    "source_gloss_de\tderiv_marker\tcontext\n"
    "9\trājan\trAjan\trāj\trAj\troot\tTrue\therrschen\tvon\t\n"
    "11\tkhinna\tKinna\tkhid\tKid\troot\tFalse\t\tvon\t\n")
FIXTURE_XWALK = ('whitney_id,root,in_MW,mw_L,mw_classes,dcs_status,dcs_freq\n'
                 '361,gam,yes,500,"1",matched,10000\n'
                 '545,mad,yes,600,"4",matched,300\n'
                 '700,rāj,yes,700,"1",matched,900\n')
FIXTURE_WHITNEY = ('361. √gam "go"\n362. √gar "swallow"\n545. √mad "hilarate"\n'
                   '700. √rāj "rule"\n')
FIXTURE_SURFACE = ("form_slp1\tsa\tru\tn\tn_form_total\tworks\n"
                   "na\tna\tне\t3543\t4843\t08_rigveda:25|raghuvamsha:50\n"
                   "na\tna\tкак\t213\t4843\t08_rigveda:25|01_rigveda:69\n"
                   "gacCati\tgacchati\tидет\t7\t7\tsome-unindexed-work:7\n")
FIXTURE_CORPUS = {
    "08_rigveda": [
        {"group": "g1", "seg": "sa", "passage": "1.2", "deleted": False,
         "text": "gāṃ na carṣaṇīsaham", "slp1": "gAM na carzaRIsaham"},
        {"group": "g1", "seg": "ru", "passage": "1.2", "deleted": False,
         "text": "словно бык, побеждающий народы"},
    ],
    "raghuvamsha": [
        {"group": "r1", "seg": "sa", "passage": "5.66", "deleted": False,
         "text": "aruṇāṃśubhir", "slp1": "aruRAMSuBir udayati"},
        {"group": "r1", "seg": "ru", "passage": "5.66", "deleted": False,
         "text": "лучами Аруны"},
    ],
    "nyaya-bhashya": [
        {"group": "n1", "seg": "sa", "passage": "3.2.11", "deleted": False,
         "text": "niyamahetv", "slp1": "niyamahetvaBAvAt"},
    ],
}


def _write_fixtures(tmp):
    os.makedirs(tmp, exist_ok=True)
    corpus = os.path.join(tmp, "corpus")
    os.makedirs(corpus, exist_ok=True)
    files = {"gra.txt": FIXTURE_GRA, "mw.txt": FIXTURE_MW, "pwg.txt": FIXTURE_PWG,
             "f2l.tsv": FIXTURE_F2L, "l2r.tsv": FIXTURE_L2R,
             "mw_roots.tsv": FIXTURE_MWROOTS, "xwalk.csv": FIXTURE_XWALK,
             "whitney.md": FIXTURE_WHITNEY, "surface.tsv": FIXTURE_SURFACE,
             "mw_etym.tsv": FIXTURE_MW_ETYM, "pwg_etym.tsv": FIXTURE_PWG_ETYM}
    for name, text in files.items():
        with io.open(os.path.join(tmp, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    for work, recs in FIXTURE_CORPUS.items():
        with io.open(os.path.join(corpus, work + ".jsonl"), "w",
                     encoding="utf-8", newline="\n") as fh:
            for r in recs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    return {"gra": os.path.join(tmp, "gra.txt"), "mw": os.path.join(tmp, "mw.txt"),
            "pwg": os.path.join(tmp, "pwg.txt"),
            "form2lemma": os.path.join(tmp, "f2l.tsv"),
            "lemma2root": os.path.join(tmp, "l2r.tsv"),
            "mw_roots": os.path.join(tmp, "mw_roots.tsv"),
            "mw_etymology": os.path.join(tmp, "mw_etym.tsv"),
            "pwg_etymology": os.path.join(tmp, "pwg_etym.tsv"),
            "root_crosswalk": os.path.join(tmp, "xwalk.csv"),
            "whitney": os.path.join(tmp, "whitney.md"),
            "surface_glossary": os.path.join(tmp, "surface.tsv"),
            "corpus": corpus}


def selftest():
    """The four cases H1801 names, plus the routing table and the honesty rule."""
    import tempfile
    tmp = os.path.join(tempfile.gettempdir(), "h1801_evidence_fixture")
    paths = _write_fixtures(tmp)
    fails = []

    def check(cond, msg):
        if not cond:
            fails.append(msg)

    # --- routing table -----------------------------------------------------
    check(route_dictionaries("Vedic", "08_rigveda")[0][0] == "GRA",
          "Vedic/rigveda must route to GRA first")
    check(route_dictionaries("Vedic", "br-up")[0][0] == "GRA",
          "Vedic upanisad must route to GRA first (with MW/PWG behind it)")
    check(route_dictionaries("Classical", "raghuvamsha")[0] == ["MW", "PWG"],
          "Classical must route to MW+PWG, never GRA")
    check(route_dictionaries("Medieval", "hatha-yoga-pradipika")[0] == ["MW", "PWG"],
          "Medieval must route to MW+PWG")
    check(route_dictionaries("Epic / early-Classical", "01_mahabharata-adiparva")[0]
          == ["MW", "PWG"], "Epic must route to MW+PWG")
    # a Vedic-language work under a coarser period label still routes Vedic
    check(route_dictionaries("Classical", "03_atharvaveda")[0][0] == "GRA",
          "a Vedic WORK must route to GRA even under a non-Vedic period label")

    rows = [
        # 1. Vedic routing -> GRA, the id-122 case
        {"id": 122, "slp1": "na", "sa": "na", "ru": "словно", "kind": "translation",
         "period": "Vedic", "work": "08_rigveda", "label": "correct"},
        # 2. Classical routing -> MW/PWG, root present via lemma
        {"id": 900, "slp1": "rAjAnam", "sa": "rājānam", "ru": "царя",
         "kind": "translation", "period": "Classical", "work": "raghuvamsha",
         "label": "correct"},
        # 3. headword with no root hit (and no dictionary hit)
        {"id": 901, "slp1": "aruRAmSub", "sa": "aruṇāmśub", "ru": "Аруна",
         "kind": "commentary", "period": "Classical", "work": "raghuvamsha",
         "label": "partial"},
        # 4. a form with zero corpus contexts in its own work
        {"id": 902, "slp1": "gacCati", "sa": "gacchati", "ru": "идет",
         "kind": "translation", "period": "Classical", "work": "nyaya-bhashya",
         "label": "correct"},
    ]
    P = build_panels(rows, paths)

    # --- case 1: Vedic -> GRA, and the comparison sense is actually shown ---
    d = P["122"]["dictionary"]
    check(d["found"], "122: GRA entry for na must be found")
    check(d["entries"][0]["dict"] == "GRA", "122: must be served by GRA, not MW/PWG")
    check("gleichwie" in d["entries"][0]["text"],
          "122: the comparison sense must be IN the shown text (this is the whole point)")
    check(P["122"]["glossary"]["found"], "122: ranked glossary must populate")
    check(any(g["ru"] == "как" and g["in_this_work"] for g in P["122"]["glossary"]["glosses"]),
          "122: «как» must be shown as attested in 08_rigveda")
    c = P["122"]["contexts"]
    check(c["found"] and c["tier"] == "token", "122: exact-token context expected")
    check(c["hits"][0]["has_ru"], "122: the paired Russian of record must come with it")

    # --- the homograph guard, on the card that motivated it ----------------
    check(all(e["key"] != "mad" for e in d["entries"]),
          "122: the pronoun-stem homograph mad must not supply a sense of na")
    check("mad" not in [k for k, _w in dictionary_keys(
        rows[0], [("na", "PART", 63304), ("mad", "PRON", 836)])],
          "122: mad must not even become a dictionary key")
    r122 = P["122"]["root"]
    check(not any(rt["root_slp1"] == "mad" for rt in r122["roots"]),
          "122: √mad «hilarate» must NOT be offered as the root of the particle na")
    check(any("mad" in s for s in r122["searched"]),
          "122: the rejected homograph must still be NAMED, not silently dropped")
    check(any("не глагольная часть речи" in s for s in r122["searched"]),
          "122: a PART lemma must be reported as having no dhatu, not left blank")

    # --- case 2: Classical -> MW/PWG + Whitney root ------------------------
    d = P["900"]["dictionary"]
    check(d["found"] and d["entries"][0]["dict"] == "MW",
          "900: Classical card must be served by MW")
    check("king" in d["entries"][0]["text"], "900: MW sense text must survive the IAST layer")
    r = P["902"]["root"]
    check(r["found"] and r["roots"][0]["whitney_line"] and "go" in r["roots"][0]["whitney_line"],
          "902: Whitney's own gloss for the root must be shown")
    check(r["roots"][0]["mw_classes"] == "1P", "902: MW class must come from mw_roots.tsv")
    check(r["roots"][0]["source"] == "DCS", "902: a verbal form must resolve via DCS")

    # --- the nominal side: DCS has no root for rAjan, MW/PWG etymology does --
    r900 = P["900"]["root"]
    check(r900["found"], "900: a NOMINAL headword must still get a root line")
    srcs = set(rt["source"] for rt in r900["roots"])
    check("MW" in srcs and "PWG" in srcs,
          "900: both etymology tables must contribute, each stamped with its source")
    check(all("√" not in (rt["root_slp1"] or "") for rt in r900["roots"]),
          "900: root keys stay bare SLP1")
    check(any(rt["whitney_line"] and "rāj" in rt["whitney_line"] for rt in r900["roots"]),
          "900: the MW/PWG root must still reach Whitney's own line")
    check("mw_etymology" in " ".join(r900["searched"])
          and "pwg_etymology" in " ".join(r900["searched"]),
          "900: both etymology lookups must be named in searched")
    # PWG rows NOT marked is_root must never be read as a root derivation
    check(all(rt["root_slp1"] != "Kid" for rt in r900["roots"]),
          "900: an is_root=False PWG row must not produce a root line")

    # --- case 3: no root hit, no dictionary hit -> explicit, not blank ------
    r = P["901"]["root"]
    check(not r["found"], "901: must report no root")
    check(r["searched"], "901: must say what was searched for the root")
    check("dcs_form2lemma" in " ".join(r["searched"]),
          "901: the unresolved lemma lookup must be named")
    check(not P["901"]["dictionary"]["found"], "901: must report no dictionary entry")
    check(P["901"]["dictionary"]["searched"], "901: must say which dict keys were tried")
    check("evidence not found" in render_root(r),
          "901: a blank panel and an unsearched panel must not look alike")

    # --- case 4: zero corpus contexts in its own work -----------------------
    c = P["902"]["contexts"]
    check(not c["found"], "902: gacCati does not occur in nyaya-bhashya")
    check(c["tier"] == "none", "902: tier must be none, not a silent empty")
    check("evidence not found" in render_contexts(c),
          "902: the empty context panel must say what was searched")
    # ... and the glossary layer must NOT be allowed to fake a context hit
    check(P["902"]["glossary"]["found"], "902: the form IS in the glossary")
    check(c["glossary_attested_n"] is None,
          "902: the glossary attests it elsewhere, never in THIS work — must not be claimed")

    # --- the key-variant layer: a mis-transcoded scaffold key still resolves,
    #     and the card SAYS it resolved through a variant -----------------------
    vrows = [
        {"id": 80, "slp1": "advaita", "sa": "advaita", "ru": "недвойственный",
         "kind": "commentary", "period": "Classical", "work": "nyaya-bhashya",
         "label": "correct"},
        {"id": 92, "slp1": "avAk-SAKaH", "sa": "avāk-śākhaḥ", "ru": "с ветвями вниз",
         "kind": "commentary", "period": "Classical", "work": "nyaya-bhashya",
         "label": "correct"},
    ]
    V = build_panels(vrows, paths)
    d80 = V["80"]["dictionary"]
    check(d80["found"] and d80["entries"][0]["key"] == "advEta",
          "80: ai→E must recover the real MW headword advEta")
    check("ai/au" in d80["entries"][0]["via"],
          "80: the card must SAY the hit came through a variant, not pass it off as exact")
    d92 = V["92"]["dictionary"]
    check(d92["found"] and d92["entries"][0]["key"] == "avAkSAKa",
          "92: de-hyphenation must recover the compound headword")
    check([k for k, _w in dictionary_keys(vrows[1], [])].index("avAkSAKa")
          < [k for k, _w in dictionary_keys(vrows[1], [])].index("avAk"),
          "92: the whole compound must be tried BEFORE its parts")
    check(any("часть композита" in w for _k, w in
              dictionary_keys(vrows[1], [])), "92: compound parts must also be tried")
    check([k for k, _w in dictionary_keys(vrows[1], [])][0] == "avAk-SAKaH",
          "92: the card's own form is always tried FIRST, before any variant")
    check("SAKa" in [k for k, _w in dictionary_keys(vrows[1], [])],
          "92: the visarga-stripped part must be among the keys")

    # --- the substring tier -------------------------------------------------
    hits, tier, _ = corpus_contexts(paths["corpus"], "raghuvamsha", "aruRAMSuBir")
    check(tier == "token", "whole-token match must be graded token")
    hits, tier, _ = corpus_contexts(paths["corpus"], "raghuvamsha", "aruRAMSu")
    check(tier == "substring" and hits, "in-compound match must be graded substring")
    hits, tier, _ = corpus_contexts(paths["corpus"], "raghuvamsha", "na")
    check(tier == "none",
          "a <4-char form must NOT substring-match (na is inside every second word)")
    _, tier, searched = corpus_contexts(paths["corpus"], "no-such-work", "na")
    check(tier == "missing" and "файла нет" in " ".join(searched),
          "a missing corpus file must be reported, not silently empty")

    # --- render layer never crashes on any panel ---------------------------
    for cid, panels in P.items():
        for title, body in render_panels(panels):
            check(isinstance(body, str) and body, "render %s/%s empty" % (cid, title))

    cov = coverage(P)
    print("selftest: %d cards · dictionary %d · root %d · contexts %d · glossary %d"
          % (cov["cards"], cov["dictionary"], cov["root"], cov["contexts"], cov["glossary"]))
    if fails:
        for f in fails:
            print("FAIL:", f)
        print("selftest: %d/%d checks FAILED" % (len(fails), len(fails)))
        return 1
    print("selftest: OK (iast layer: %s)" % IAST_LAYER)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--form", help="ad-hoc probe: SLP1 form")
    ap.add_argument("--work", default="", help="ad-hoc probe: corpus work")
    ap.add_argument("--period", default="Classical", help="ad-hoc probe: period")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.form:
        ap.error("give --form (with --work/--period) or --selftest")
    row = {"id": "probe", "slp1": args.form, "sa": args.form, "ru": "",
           "kind": "translation", "period": args.period, "work": args.work,
           "label": "correct"}
    P = build_panels([row])["probe"]
    print(json.dumps(P, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
