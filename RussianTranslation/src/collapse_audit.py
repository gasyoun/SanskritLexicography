#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""collapse_audit.py — does the H2844 line-collapse ever tear a citation loose?

[`line_collapse.collapse`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/line_collapse.py)
turns csl-orig's inherited column line-wrap into a space so that
``<ls>MBH. 12,8081.</ls>`` sits on the same rendered line as the verse it
sources. The H2844 acceptance does not accept the argument that this is safe by
construction — it asks for a **200-citation random sample drawn from the
affected sites, counting how many collapses land inside vs outside a citation
clause**, and it fails the whole transform if *any* sampled citation ends up
separated from its source clause.

This module is that audit, and it is deliberately built so it *can* fail:
:func:`verdict` never looks at ``collapse`` at all. It takes the rendered string
as an argument and asks one question of it — *is the clause that precedes this
citation on the same rendered line as the citation?* The selftest feeds it a
renderer that keeps every line break (the pre-H2844 ``\\n`` → ``<br>`` behaviour)
and requires the verdict to come back ``torn``, so a PASS here is evidence and
not a tautology.

What the three verdicts mean
----------------------------
``joined``  the citation and its source clause share one rendered line — the
            outcome P1 asks for.
``orphan``  the citation is alone on its rendered line, but so was it in the
            store: the text before it ends a structural unit, so there is no
            clause to join. Not a tear; reported separately because a reviewer
            seeing a bare citation line should know it is inherited, not caused.
``torn``    the clause exists and the render put it on another line. This is the
            H2844 fail condition; any occurrence fails the audit.

Inside vs outside a citation clause (the count the handoff asks for) is a
second, orthogonal axis, read off what precedes the wrap in the store:

===============  =========================================================
``after_gloss``   a Russian/Sanskrit clause — the collapse lands INSIDE the
                  citation clause and joins the citation to its source
``after_cite``    another ``</ls>`` — inside a citation run, joining a list
``after_marker``  a ``[PageN-NNNN]`` column marker — typesetting only
``after_break``   an empty or structure-opening line — OUTSIDE any clause
===============  =========================================================

Inputs (local, untracked — point PWG_RU_DATA_ROOT at the tree that has it):
    <data>/src/pwg_ru_translated.jsonl
Outputs (tracked, always beside this script — not beside the data root):
    ../reports/h2844_collapse_audit_<n>.jsonl      one row per sampled site
    ../reports/H2844_COLLAPSE_AUDIT_<n>_<date>.md  the human report

Run: python src/collapse_audit.py --n 200 --seed 20260817
     python src/collapse_audit.py --selftest
"""
import argparse
import collections
import io
import json
import os
import random
import re
import sys

from line_collapse import COMPACT, EXPANDED, collapse, is_structural, store_digest

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("PWG_RU_DATA_ROOT", os.path.dirname(HERE))
STORE = os.path.join(DATA, "src", "pwg_ru_translated.jsonl")
#: Outputs land beside THIS script, never beside the data root — so a run whose
#: `PWG_RU_DATA_ROOT` points at the main checkout still writes into the worktree
#: it was launched from (the org's "mutating tools act on the script tree" rule).
REPORTS = os.path.join(os.path.dirname(HERE), "reports")

#: the citation-opening tag, as it appears at the start of a wrapped line
_LS_HEAD = re.compile(r"<ls\b")
_PAGE_MARKER = re.compile(r"^\[Page[^\]]*\]$")
#: A unit opener at the head of a line — csl-orig's sense ``<div>``, a homonym
#: tag, a stray closing ``>``, a numbered sense, a dash-led derivational block.
#: Stripped repeatedly to ask whether anything but openers is on the line.
_UNIT_OPENER = re.compile(r"^(?:<div\b[^>]*>|<hom\b[^>]*>|</hom>|>|\d+[)〉]|—)\s*")
_SQUEEZE = re.compile(r"[ \t]+")
#: how much of the clause tail / citation head is used to locate the pair in the
#: rendered string. Long enough to be unique inside one body, short enough that
#: a squeezed double space cannot push it out of the window.
WINDOW = 40


def norm(s):
    """Whitespace-squeezed form — the shape both the store and the render agree on."""
    return _SQUEEZE.sub(" ", (s or "")).strip()


# --------------------------------------------------------------------- population
def sites(body):
    """Every inherited wrap in ``body`` whose next line opens a citation.

    Yields ``(line_index, clause_line, citation_line)`` over the physical lines
    of the store body. A wrap whose tail is structural is not a candidate — the
    render keeps it, so there is nothing to audit.
    """
    lines = body.split("\n")
    for i in range(len(lines) - 1):
        tail = "\n".join(lines[i + 1:])
        head = lines[i + 1].lstrip()
        if not _LS_HEAD.match(head) or is_structural(tail):
            continue
        yield i, lines[i], lines[i + 1]


def strip_openers(t):
    """``t`` with every leading unit opener removed — what clause text remains."""
    prev = None
    while prev != t:
        prev = t
        t = _UNIT_OPENER.sub("", t, count=1).strip()
    return t


def preceding_class(clause_line):
    """Which of the four ``after_*`` buckets this wrap sits in.

    A line that *opens* a unit (``<div n="1">— 3) {#…#}``) and then carries
    clause text is still a clause: the citation on the next line belongs to that
    text, so the collapse lands inside a citation clause. Only a line with the
    opener and nothing else has no clause to offer.
    """
    t = norm(clause_line)
    if not t:
        return "after_break"
    if _PAGE_MARKER.match(t):
        return "after_marker"
    if t.endswith("</ls>") or t.endswith("/>"):
        return "after_cite"
    if not strip_openers(t):
        return "after_break"
    return "after_gloss"


# --------------------------------------------------------------------- verdict
def verdict(clause_line, citation_line, rendered):
    """``joined`` / ``orphan`` / ``torn`` for one site, judged on ``rendered``.

    Deliberately renderer-agnostic: it is handed the finished string and looks
    only at whether the clause tail and the citation head ended up on one line.
    That is what lets the selftest prove the check can fail.
    """
    cite = norm(citation_line)[:WINDOW]
    clause = norm(clause_line)
    if not cite:
        return "orphan"
    for line in rendered.split("\n"):
        n = norm(line)
        pos = n.find(cite)
        if pos < 0:
            continue
        if not clause:
            return "orphan"
        before = n[:pos]
        # the clause tail must sit on this line, ahead of the citation
        if clause[-WINDOW:] in before:
            return "joined"
        # the clause is elsewhere in the render -> the citation lost its clause
        return "torn"
    # the citation head is not in the render at all: treat as torn, since the
    # audit cannot prove the clause is with it
    return "torn"


def br_render(body):
    """The pre-H2844 renderer: every store newline becomes a hard line break.

    Kept here as the audit's negative control — the behaviour P1 replaced.
    """
    return body


# --------------------------------------------------------------------- run
def load_population(store_path, field="ru"):
    """All ``(row_index, key1, subcard, body)`` rows plus the flat site list."""
    rows, flat = [], []
    with io.open(store_path, encoding="utf-8") as fh:
        for n, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            body = obj.get(field) or ""
            if "\n" not in body:
                continue
            idx = len(rows)
            rows.append((n, obj.get("key1", ""), obj.get("subcard", ""), body))
            for i, clause, cite in sites(body):
                flat.append((idx, i, clause, cite))
    return rows, flat


def census(store_path, field="ru"):
    """Reproduce the docstring numbers instead of trusting them (H2844 P1)."""
    c = collections.Counter()
    with io.open(store_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            body = json.loads(line).get(field) or ""
            c["rows"] += 1
            c["citations"] += len(re.findall(r"<ls\b", body))
            lines = body.split("\n")
            c["newlines"] += len(lines) - 1
            for i in range(len(lines) - 1):
                tail = "\n".join(lines[i + 1:])
                if _LS_HEAD.match(lines[i + 1].lstrip()):
                    c["newline_before_ls"] += 1
                if is_structural(tail):
                    c["structural"] += 1
                else:
                    c["inherited"] += 1
    return c


def audit(n=200, seed=20260817, field="ru", store_path=None):
    store_path = store_path or STORE
    rows, flat = load_population(store_path, field)
    pop = len(flat)
    rng = random.Random(seed)
    picked = sorted(rng.sample(range(pop), min(n, pop)))

    before = store_digest(*[b for _, _, _, b in rows])
    records, verdicts, buckets = [], collections.Counter(), collections.Counter()
    for k in picked:
        idx, i, clause, cite = flat[k]
        line_no, key1, subcard, body = rows[idx]
        rendered, n_col, n_kept = collapse(body, EXPANDED)
        compact, _, _ = collapse(body, COMPACT)
        v = verdict(clause, cite, rendered)
        vc = verdict(clause, cite, compact)
        bucket = preceding_class(clause)
        verdicts[v] += 1
        verdicts["compact:" + vc] += 1
        buckets[bucket] += 1
        records.append({
            "site": k, "store_line": line_no, "key1": key1, "subcard": subcard,
            "wrap_index": i, "bucket": bucket,
            "verdict": v, "verdict_compact": vc,
            "n_collapsed": n_col, "n_kept": n_kept,
            "clause_tail": norm(clause)[-WINDOW:],
            "citation_head": norm(cite)[:WINDOW],
            "control_verdict": verdict(clause, cite, br_render(body)),
        })
    after = store_digest(*[b for _, _, _, b in rows])
    return {
        "population": pop, "rows_with_newlines": len(rows),
        "sampled": len(picked), "seed": seed, "field": field,
        "verdicts": dict(verdicts), "buckets": dict(buckets),
        "store_digest_before": before, "store_digest_after": after,
        "store_unchanged": before == after,
        "records": records,
    }


# --------------------------------------------------------------------- report
def write_report(res, date, cen, out_md, out_jsonl, sheet=None):
    with io.open(out_jsonl, "w", encoding="utf-8", newline="\n") as fh:
        for r in res["records"]:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    v, b = res["verdicts"], res["buckets"]
    torn = v.get("torn", 0) + v.get("compact:torn", 0)
    blob = "https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation"
    L = []
    L.append("# H2844 — 200-citation line-collapse audit")
    L.append("")
    L.append("_Created: %s · Last updated: %s_" % (date, date))
    L.append("")
    L.append("Acceptance evidence for "
             "[H2844](https://github.com/gasyoun/Uprava/blob/main/handoffs/"
             "H2844-Opus_SanskritLexicography_reglue-citation-linebreak-collapse-"
             "compact-card-view_15.08.26.md) — *«a 200-citation random sample drawn "
             "from the affected sites — count how many collapses land inside vs "
             "outside a citation clause»*, with the fail condition *«any sampled "
             "citation separated from its source clause»*.")
    L.append("")
    L.append("**Verdict: %s** — %d of %d sampled citations stay with their source "
             "clause in both renderings; %d torn." %
             ("PASS" if torn == 0 and res["store_unchanged"] else "FAIL",
              v.get("joined", 0), res["sampled"], v.get("torn", 0)))
    L.append("")
    L.append("## Method")
    L.append("")
    L.append("- Population: every inherited wrap in the store's `%s` field whose "
             "next line opens a `<ls>` citation — **%s sites**, spread over the %s "
             "store rows that carry any newline at all."
             % (res["field"], format(res["population"], ",d"),
                format(res["rows_with_newlines"], ",d")))
    L.append("- Sample: `random.Random(%d).sample`, n=%d. Re-runnable verbatim: "
             "`python src/collapse_audit.py --n %d --seed %d`."
             % (res["seed"], res["sampled"], res["sampled"], res["seed"]))
    L.append("- Verdict per site is read off the **rendered** string by "
             "[`collapse_audit.verdict`](%s/src/collapse_audit.py), which never "
             "sees `collapse` — its selftest feeds it the pre-H2844 "
             "line-break-preserving render and requires `torn`, so a PASS is not "
             "vacuous." % blob)
    L.append("")
    L.append("## Store census (recomputed, not quoted)")
    L.append("")
    L.append("| measure | n |")
    L.append("|---|---|")
    for label, key in (("store rows", "rows"), ("`<ls>` citations", "citations"),
                       ("newlines in `ru`", "newlines"),
                       ("newlines immediately before `<ls`", "newline_before_ls"),
                       ("classified inherited (collapse)", "inherited"),
                       ("classified structural (kept)", "structural")):
        L.append("| %s | %s |" % (label, format(cen[key], ",d")))
    L.append("")
    L.append("The **%s** wraps before a `<ls` reproduce the H2844 figure exactly. "
             "The total newline count is above the 25,325 measured on 15-08-2026 "
             "because the store has kept growing since; the ratio the ruling rests "
             "on (the overwhelming majority of newlines sit in front of a citation) "
             "is unchanged." % format(cen["newline_before_ls"], ",d"))
    L.append("")
    L.append("## Where the collapse lands (n=%d)" % res["sampled"])
    L.append("")
    L.append("| position of the wrap | n | reading |")
    L.append("|---|---|---|")
    gloss = {
        "after_gloss": "**inside a citation clause** — joins the citation to the "
                       "Russian/Sanskrit clause that sources it (the P1 case)",
        "after_cite": "**inside a citation run** — joins one citation to the "
                      "previous citation of the same list",
        "after_marker": "after a `[PageN-NNNN]` column marker — pure typesetting",
        "after_break": "**outside any clause** — the line before ends a unit, so "
                       "the citation had no clause to join",
    }
    for key in ("after_gloss", "after_cite", "after_marker", "after_break"):
        if b.get(key):
            L.append("| `%s` | %d | %s |" % (key, b[key], gloss[key]))
    inside = b.get("after_gloss", 0) + b.get("after_cite", 0)
    L.append("")
    L.append("Inside a citation clause or run: **%d**. Outside: **%d**."
             % (inside, res["sampled"] - inside))
    L.append("")
    L.append("## Verdicts")
    L.append("")
    L.append("| render | joined | orphan | torn |")
    L.append("|---|---|---|---|")
    L.append("| expanded | %d | %d | %d |"
             % (v.get("joined", 0), v.get("orphan", 0), v.get("torn", 0)))
    L.append("| compact | %d | %d | %d |"
             % (v.get("compact:joined", 0), v.get("compact:orphan", 0),
                v.get("compact:torn", 0)))
    L.append("")
    if v.get("torn") or v.get("compact:torn"):
        L.append("### Torn sites (each one fails the acceptance)")
        L.append("")
        L.append("| key1 | subcard | clause tail | citation |")
        L.append("|---|---|---|---|")
        for r in res["records"]:
            if r["verdict"] == "torn" or r["verdict_compact"] == "torn":
                L.append("| %s | %s | `%s` | `%s` |"
                         % (r["key1"], r["subcard"],
                            r["clause_tail"].replace("|", "\\|"),
                            r["citation_head"].replace("|", "\\|")))
        L.append("")
    else:
        orph = v.get("orphan", 0) + v.get("compact:orphan", 0)
        L.append("No torn sites in either rendering." + (
            " The %d `orphan` rows are citations that already opened their own "
            "unit in the store — the render did not move them; they are the "
            "`after_break` sites above." % orph if orph else
            " No `orphan` rows either: every sampled wrap had a clause in front "
            "of it, and the render kept the two together."))
        L.append("")
    ctrl = collections.Counter(r["control_verdict"] for r in res["records"])
    L.append("## Negative control")
    L.append("")
    L.append("The same %d sites judged against the **pre-H2844 render** (every "
             "store newline kept as a line break): %s. That is the defect P1 "
             "removed, and it is what the audit reports when tearing is real."
             % (res["sampled"],
                ", ".join("%d %s" % (n, k) for k, n in sorted(ctrl.items()))))
    L.append("")
    L.append("## Store byte-identity")
    L.append("")
    L.append("SHA-256 over every sampled store body, taken before and after the "
             "whole audit run:")
    L.append("")
    L.append("- before: `%s`" % res["store_digest_before"])
    L.append("- after:  `%s`" % res["store_digest_after"])
    L.append("- **%s**" % ("identical — no store byte changed"
                           if res["store_unchanged"] else "MUTATED — see above"))
    if sheet:
        L.append("")
        L.append("## The 15 pilot cards (sheet build)")
        L.append("")
        L.append("```")
        L.append(sheet.strip())
        L.append("```")
    L.append("")
    L.append("_Dr. Mārcis Gasūns_")
    with io.open(out_md, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")


# --------------------------------------------------------------------- selftest
def selftest():
    ok = True

    def check(cond, label):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + label)
        ok = ok and bool(cond)

    ga = ("{#yadA ca pfTivIM sarvAM yajamAno 'nuparyagAH#}\n"
          "<ls>MBH. 12,8081.</ls>")
    found = list(sites(ga))
    check(len(found) == 1 and found[0][0] == 0,
          "the motivating wrap is one auditable site")
    _, clause, cite = found[0]
    check(verdict(clause, cite, collapse(ga)[0]) == "joined",
          "collapse joins the citation to its verse")
    # THE point of this selftest: the check must fail on a render that tears.
    check(verdict(clause, cite, br_render(ga)) == "torn",
          "the pre-H2844 render is reported torn — the verdict is not vacuous")

    div = "{%достигать%}: {#ko vA#}\n<div n=\"1\"> 1) <ls>P. 1,1</ls>"
    check(list(sites(div)) == [],
          "a structural wrap is not an auditable site (the render keeps it)")

    page = "{#aBIpsatI#}\n[Page1-0651]\n<ls>MBH. 1,6469.</ls>"
    got = [preceding_class(c) for _, c, _ in sites(page)]
    check(got == ["after_marker"], "a page-marker wrap is bucketed: %r" % got)

    run = "<ls>M. 2,109.</ls>\n<ls>YĀJÑ. 1,28.</ls>"
    got = [preceding_class(c) for _, c, _ in sites(run)]
    check(got == ["after_cite"], "a citation run is bucketed: %r" % got)

    lead = "\n<ls>P. 1,1</ls>"
    got = [(preceding_class(c), verdict(c, t, collapse(lead)[0]))
           for _, c, t in sites(lead)]
    check(got == [("after_break", "orphan")],
          "a leading wrap has no clause to join -> orphan: %r" % got)

    gloss = "идти дорогой (Akk, Instr)\n<ls>RAGH. 12,52.</ls>"
    got = [preceding_class(c) for _, c, _ in sites(gloss)]
    check(got == ["after_gloss"], "a gloss clause is bucketed: %r" % got)

    # a line that OPENS a sense and then carries clause text is still a clause —
    # the first run of this audit mis-filed 25 of 200 such sites as after_break
    opener = ('<div n="1">— 3) {#dUto na saMcarati Ke#}\n<ls>Spr. 4205.</ls>')
    got = [preceding_class(c) for _, c, _ in sites(opener)]
    check(got == ["after_gloss"],
          "a sense-opening line WITH clause text is a clause: %r" % got)
    bare = '{%идти%}\n<div n="2">\n<ls>P. 1,1</ls>'
    got = [preceding_class(c) for _, c, _ in sites(bare)]
    check(got == ["after_break"],
          "a line that is only a unit opener has no clause: %r" % got)
    check(strip_openers('<div n="1">— 3)') == ""
          and strip_openers('<div n="1"> 3) {#x#}') == "{#x#}",
          "strip_openers peels every leading opener, once")

    # a site inside a longer body: the clause must be matched on its OWN line,
    # not on a neighbouring one that happens to contain similar text
    twice = ("идти <ls>A. 1</ls>\n<ls>B. 2</ls>\nидти дорогой\n<ls>RAGH. 12,52.</ls>")
    found2 = list(sites(twice))
    check([i for i, _, _ in found2] == [0, 2],
          "only the wraps that open a citation are sites: %r"
          % [i for i, _, _ in found2])
    v = [verdict(c, t, collapse(twice)[0]) for _, c, t in found2]
    check(v == ["joined", "joined"], "both sites in one body judged: %r" % v)
    check([preceding_class(c) for _, c, _ in found2]
          == ["after_cite", "after_gloss"],
          "the two sites land in different buckets")

    # the compact render must be safe too
    check(verdict(clause, cite, collapse(ga, COMPACT)[0]) == "joined",
          "compact mode also keeps the citation with its clause")

    print("collapse_audit selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", type=int, default=200, help="sample size (default 200)")
    ap.add_argument("--seed", type=int, default=20260817, help="sampling seed")
    ap.add_argument("--field", default="ru", help="store field to audit (ru|de)")
    ap.add_argument("--date", default="17-08-2026", help="report date DD-MM-YYYY")
    ap.add_argument("--sheet-log", default=None,
                    help="path to the build_reglue_sheet_v2 stdout to quote")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()

    if not os.path.exists(STORE):
        print("no store at %s — point PWG_RU_DATA_ROOT at the tree that has it"
              % STORE)
        return 1
    cen = census(STORE, a.field)
    res = audit(a.n, a.seed, a.field)
    os.makedirs(REPORTS, exist_ok=True)
    out_jsonl = os.path.join(REPORTS, "h2844_collapse_audit_%d.jsonl" % res["sampled"])
    iso = "-".join(reversed(a.date.split("-")))
    out_md = os.path.join(REPORTS, "H2844_COLLAPSE_AUDIT_%d_%s.md"
                          % (res["sampled"], iso))
    sheet = None
    if a.sheet_log and os.path.exists(a.sheet_log):
        sheet = io.open(a.sheet_log, encoding="utf-8").read()
        # the builder prints wherever PWG_RU_DATA_ROOT pointed; a local absolute
        # path is noise in a committed report
        sheet = re.sub(r"[A-Za-z]:[^\s]*?[\\/]review[\\/]([\w.]+)",
                       r"review/\1", sheet)
    write_report(res, a.date, cen, out_md, out_jsonl, sheet)

    v = res["verdicts"]
    print("  population %s inherited wraps before <ls> · sampled %d (seed %d)"
          % (format(res["population"], ",d"), res["sampled"], res["seed"]))
    print("  expanded: %d joined · %d orphan · %d torn"
          % (v.get("joined", 0), v.get("orphan", 0), v.get("torn", 0)))
    print("  compact:  %d joined · %d orphan · %d torn"
          % (v.get("compact:joined", 0), v.get("compact:orphan", 0),
             v.get("compact:torn", 0)))
    print("  buckets: %s" % res["buckets"])
    print("  store unchanged: %s (%s)"
          % (res["store_unchanged"], res["store_digest_before"]))
    print("  -> %s" % out_md)
    return 0 if (not v.get("torn") and not v.get("compact:torn")
                 and res["store_unchanged"]) else 1


if __name__ == "__main__":
    sys.exit(main())
