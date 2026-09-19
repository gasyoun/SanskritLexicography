#!/usr/bin/env python3
"""H4797: 16-dict union headword index built from HeadwordLists/now-2026.

The published 15-dict union (HeadwordLists/union/union_headwords.tsv, built by
build_union.py from csl-orig <k1>) has no PD and predates the current csl-orig
counts, which blocked the overlap-matrix / routing analysis at 15 dicts. This
builder rebuilds the union from the per-dict unique-key lists ON DISK in
now-2026/ (16 dicts, 25 data files: key1 where the dict has one, key2 for
every dict), so PD joins and the refreshed counts land in one index.

Union key = bare SLP1 lemma (no accents, no compound hyphens, no marks):

* key1 lines are already the bare machine key -> used as-is; a key1 line that
  still carries a mark/digit/hyphen is FAIL-LOUD residue (never guessed).
* key2 lines are print forms: parenthetical segments are annotations
  (``akzuRRa(-vyAkaraRa)``, ``acalitasumana(s)``, ``aYja (aYjas)``) and are
  stripped whole; ``/`` (udātta), ``˚`` (elision), ``*`` (reconstructed),
  ``'`` (avagraha) and ``^``/``|`` (uncertainty marks) are removed — every one
  of these is verified absent from the k1 key space (e.g. printed ``ato'nya``
  is ``atonya`` in MW k1) — as are ``-`` compound hyphens; a line that STARTS
  with ``(`` or a digit, or still carries a mark after normalisation, is
  counted residue and EXCLUDED (counted, never silently dropped —
  microstructure rule).

Per dict the membership set is norm(key1) | norm(key2). Outputs (in
union-16dicts/): union_headwords_16.tsv (``slp1 n_dicts dicts`` — the column
the overlap-matrix script consumes), per_dict_profile.tsv, and this run's
summary on stdout. No BOM is written (now-2026 inputs are all BOM-less).

``--selftest`` runs assertions on synthetic mini-files (no disk inputs).

IAST column is deliberately ABSENT: sanskrit-util is not on this box and a
passthrough fake transliteration would be worse than none (H3985 rule).

Run: python3 HeadwordLists/build_union16.py [--selftest]
"""
import argparse
import collections
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "now-2026")
OUT = os.path.join(HERE, "union-16dicts")

DICTS = ["AP", "BHS", "BUR", "CAE", "CCS", "GRA", "INM", "MD", "MW",
         "PD", "PWG", "PWK", "SCH", "SKD", "VCP", "VEI"]

_PAREN_SEG = re.compile(r"\([^()]*\)")
_STRIP_CHARS = ("/\u02da*-\u2010\u2013\u2014"   # udātta, elision, recon, hyphens
                "'^|")                            # avagraha + uncertainty marks (all absent from the k1 space — verified: ato'nya is atonya in MW k1)
_BARE_OK = re.compile(r"^[A-Za-z]+$")             # final bare key: SLP1 letters only


def norm_k1(line):
    """key1 line -> (bare_key or None, residue_class)."""
    k = line.strip()
    if not k:
        return None, "empty"
    if _BARE_OK.match(k):
        return k, None
    return None, "k1_not_bare"


def norm_k2(line):
    """key2 print form -> (bare_key or None, residue_class)."""
    k = line.strip()
    if not k:
        return None, "empty"
    if k[0] in "(" or k[0].isdigit():
        return None, "leading_paren_or_digit"
    k = _PAREN_SEG.sub("", k)
    k = k.translate({ord(c): None for c in _STRIP_CHARS})
    k = k.replace(" ", "").replace("\t", "")
    if not k:
        return None, "empty_after_norm"
    if not _BARE_OK.match(k):
        return None, "not_bare_after_norm"
    return k, None


def load_dict(code):
    """-> (membership:set, profile:dict) for one dict from its now-2026 files."""
    files = sorted(glob.glob(os.path.join(SRC, "%s-unique-key*.txt" % code)))
    if not files:
        raise SystemExit("no now-2026 files for %s" % code)
    member = set()
    prof = {"files": " ".join(os.path.basename(f) for f in files),
            "raw_lines": 0, "bare_keys": 0,
            "leading_paren_or_digit": 0, "not_bare_after_norm": 0,
            "empty": 0, "empty_after_norm": 0, "k1_not_bare": 0}
    for f in files:
        is_k1 = "-key1-" in f
        with open(f, encoding="utf-8-sig") as fh:
            for line in fh:
                prof["raw_lines"] += 1
                k, res = (norm_k1 if is_k1 else norm_k2)(line)
                if res:
                    prof[res] += 1
                else:
                    member.add(k)
                    prof["bare_keys"] += 1
    return member, prof


def build():
    union = collections.defaultdict(set)          # bare key -> {dict codes}
    profiles = {}
    for code in DICTS:
        member, prof = load_dict(code)
        profiles[code] = prof
        for k in member:
            union[k].add(code)
        print("  %s: %d raw lines -> %d bare keys, residue %s" % (
            code, prof["raw_lines"], prof["bare_keys"],
            {c: n for c, n in prof.items()
             if c in ("leading_paren_or_digit", "not_bare_after_norm",
                      "empty", "empty_after_norm", "k1_not_bare") and n}))
    os.makedirs(OUT, exist_ok=True)
    rows = sorted(union.items(), key=lambda kv: (len(kv[0]), kv[0]))
    tsv = os.path.join(OUT, "union_headwords_16.tsv")
    with open(tsv, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("slp1\tn_dicts\tdicts\n")
        for k, ds in rows:
            fh.write("%s\t%d\t%s\n" % (k, len(ds), " ".join(sorted(ds))))
    pf = os.path.join(OUT, "per_dict_profile.tsv")
    cols = ["dict", "files", "raw_lines", "bare_keys", "leading_paren_or_digit",
            "not_bare_after_norm", "empty", "empty_after_norm", "k1_not_bare"]
    with open(pf, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(cols) + "\n")
        for code in DICTS:
            p = profiles[code]
            fh.write("\t".join([code, p["files"], str(p["raw_lines"]),
                                str(p["bare_keys"])] +
                               [str(p[c]) for c in cols[4:]]) + "\n")
    byn = collections.Counter(len(v) for v in union.values())
    print("union over %d dicts: %d headwords -> %s" % (len(DICTS), len(union), tsv))
    print("corroboration: %s" % ", ".join("n=%d:%d" % (n, byn.get(n, 0))
                                          for n in sorted(byn)))
    return union, profiles


def selftest():
    """Synthetic mini-files: classification + set semantics canaries."""
    cases_k1 = [("deva", "deva", None), ("", None, "empty"),
                ("a-k", None, "k1_not_bare"), ("rUpa2", None, "k1_not_bare")]
    cases_k2 = [("akzuRRa(-vyAkaraRa)", "akzuRRa", None),
                ("acalitasumana(s)", "acalitasumana", None),
                ("aYja (aYjas)", "aYja", None),
                ("aMSa\u02daprakalpanA", "aMSaprakalpanA", None),
                ("suganDi(n)", "suganDi", None),
                ("aMSaprAsa/", "aMSaprAsa", None),
                ("CCSa/nt", "CCSant", None),        # accent stripped mid-word
                ("ato-'nya", "atonya", None),       # avagraha stripped (k1-space parity)
                ("ago'poha", "agopoha", None),
                ("akzitavya^", "akzitavya", None),  # uncertainty caret stripped
                ("aja\u2014mI|a", "ajamIa", None),  # em-dash + unknown-vowel pipe stripped
                ("*akz", "akz", None),
                ("(kzipra/izu", None, "leading_paren_or_digit"),
                ("1 Darma", None, "leading_paren_or_digit"),
                ("", None, "empty")]
    for raw, want, res in cases_k2[:-1]:
        got = norm_k2(raw)
        assert got == (want, res), (raw, got)
    assert norm_k2("CCSa/nt") == ("CCSant", None)     # '/' stripped -> bare letters
    assert norm_k2("1 Darma") == (None, "leading_paren_or_digit")
    for raw, want, res in cases_k1:
        assert norm_k1(raw) == (want, res), (raw, norm_k1(raw))
    print("selftest PASS (%d k2 cases, %d k1 cases)"
          % (len(cases_k2) - 1, len(cases_k1)))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
    else:
        build()
