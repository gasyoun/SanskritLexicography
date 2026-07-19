#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""review_sheet_standard — repo-side wiring for the 19-07-2026 review-sheet standard.

The standard itself (V1–V8 from the h178_da vote meta-note, see
RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md section 2)
lives in ``csl_pyutil.render_review_sheet`` v0.3.0. This module holds only what
the emitter cannot know — the REPO-side lookups every SanskritLexicography sheet
generator shares:

* ``pwg_entry_href(root_slp1)`` — V4 deep link to the full PWG entry in the kosha
  colocation viewer (root -> printed column via ``src/pwg_columns.tsv``; the same
  ``koshaHref`` scheme ``pilot/build_article_site.py`` uses on the article site).
* ``slp1_iast(s)`` — headword display form for V4 card headers; imports the
  article-site transliterator when importable, with a self-contained SLP1->IAST
  fallback table so sheet generation never depends on the site builder's deps.
* ``standard_config(save_as=...)`` — the common config fragment (V3 show_ids,
  V6 note height, V8 save-path banner) to merge into each generator's config.
* ``DA_RATING`` — the V1/V5 Direct-Assessment rating spec (1–5, threshold 3,
  approve auto-raise to 4) ruled by MG 19-07-2026.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PWG_COLUMNS_TSV = os.path.join(HERE, "pwg_columns.tsv")
KOSHA_COLOC = "https://gasyoun.github.io/kosha/colocation/"

#: V1/V5 — the DA rubric as ruled in the h178_da vote meta-note: clickable 1–5
#: (5 = good), 3 = approval threshold, voting approve auto-raises to >= 4.
DA_RATING = {"label": "Direct Assessment", "scale": 5, "threshold": 3, "approve_min": 4}

#: V6 — "comment box 2 rows taller": the emitter's donor default was 44px
#: (~2 rows); the standard doubles it.
NOTE_MIN_HEIGHT_PX = 88


def standard_config(save_as=None):
    """The config fragment shared by every sheet on the standard. Merge into
    the generator's own config dict (generator keys win on collision)."""
    cfg = {"show_ids": True, "note_min_height_px": NOTE_MIN_HEIGHT_PX}
    if save_as:
        cfg["save_as"] = save_as
    return cfg


# --------------------------------------------------------------------------- SLP1 -> IAST
# Fallback mirrors pilot/build_article_site.py slp1_iast() (its cg._S2I table);
# kept dependency-free so generators never import the whole site builder.
_S2I_FALLBACK = {
    "A": "ā", "I": "ī", "U": "ū", "f": "ṛ", "F": "ṝ", "x": "ḷ", "X": "ḹ",
    "E": "ai", "O": "au", "M": "ṃ", "H": "ḥ", "K": "kh", "G": "gh", "N": "ṅ",
    "C": "ch", "J": "jh", "Y": "ñ", "w": "ṭ", "W": "ṭh", "q": "ḍ", "Q": "ḍh",
    "R": "ṇ", "T": "th", "D": "dh", "P": "ph", "B": "bh", "S": "ś", "z": "ṣ",
}
_ACCENT = re.compile(r"[/\\^]")


def slp1_iast(s):
    """SLP1 -> IAST for card-header display (V4); accents stripped."""
    try:
        sys.path.insert(0, os.path.join(HERE, "pilot"))
        from build_article_site import slp1_iast as _site_slp1_iast  # noqa: PLC0415
        return _site_slp1_iast(s)
    except Exception:
        s = _ACCENT.sub("", s or "")
        return "".join(_S2I_FALLBACK.get(c, c) for c in s)
    finally:
        try:
            sys.path.remove(os.path.join(HERE, "pilot"))
        except ValueError:
            pass


# --------------------------------------------------------------------------- root -> PWG column
_columns_cache = None


def _load_columns():
    global _columns_cache
    if _columns_cache is not None:
        return _columns_cache
    m = {}
    if os.path.exists(PWG_COLUMNS_TSV):
        with io.open(PWG_COLUMNS_TSV, encoding="utf-8") as f:
            header = f.readline().rstrip("\n").split("\t")
            col_i = header.index("column")
            hw_i = header.index("headwords")
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if len(parts) <= hw_i:
                    continue
                col = parts[col_i]
                for hw in parts[hw_i].split(","):
                    hw = hw.strip()
                    if hw and hw not in m:
                        m[hw] = col
    _columns_cache = m
    return m


def pwg_entry_href(root_slp1):
    """V4 — deep link to the full PWG entry (kosha colocation viewer), or None
    when the root has no column row. Same URL scheme as the article site's
    koshaHref (pilot/build_article_site.py)."""
    if not root_slp1:
        return None
    col = _load_columns().get(root_slp1)
    if not col:
        return None
    try:
        from urllib.parse import quote
    except ImportError:  # pragma: no cover
        from urllib import quote
    return "%s#pwg/%s?w=%s" % (KOSHA_COLOC, quote(col, safe=""), quote(root_slp1, safe=""))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for probe in ("car", "vas", "muc", "gam", "nI", "banD"):
        print(probe, slp1_iast(probe), pwg_entry_href(probe))
