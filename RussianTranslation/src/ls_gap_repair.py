#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ls_gap_repair.py — which ⚑ citation gaps are cheap? Measure, don't guess (H2835).

The first cut of this analysis classified a gap by regex: "the source resolves
elsewhere, so this must be a format problem." That heuristic **over-counts**, and
the counter-example is instructive: `TS. PRĀT.` shares its first token with `TS.`
(Taittirīya Saṃhitā, 391 resolving citations), so it scored as a cheap format gap
— but the Taittirīya *Prātiśākhya* is a **different work** with no Cologne viewer.
No regex fixes that; only a digitisation does.

So this module does not classify. It **repairs and re-tests**: apply one small,
named, reversible normalization to the citation string and ask
[`ls_resolver`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py)
again. A gap is cheap **iff some repair makes the real resolver emit a real
href** — an experiment, not an opinion. Every repair below was derived from a
verified failing/succeeding pair in the store, and each carries that pair in its
docstring so the claim can be re-checked.

The repairs are **diagnostic only**. They say "a pattern here would pay off";
they do NOT edit the store, and nothing here should be wired into rendering
before a human rules on each rule — an over-eager repair invents a citation,
which is worse than leaving it dark.

Run: python src/ls_gap_repair.py            (set PWG_RU_DATA_ROOT)
     python src/ls_gap_repair.py --selftest
"""
import sys, os, io, re, json, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("LS_RESOLVER_QUIET", "1")

from ls_links import LsLinks, HIT, MINTABLE, LS_RE, LS_PARTS, _ws

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("PWG_RU_DATA_ROOT", os.path.dirname(HERE))
STORE = os.path.join(DATA, "src", "pwg_ru_translated.jsonl")
REPORTS = os.path.join(DATA, "reports")


# --------------------------------------------------------------------- repairs
# Each repair: (name, fn, why). fn(attrs, body) -> new body (or None to skip).
# `attrs` is the raw attribute string so a repair can see the n= continuation.

def _r_uppercase_prefix(attrs, body):
    """`MBh. 1,71,17.` fails where `MBH. 1,71,17.` resolves — the prefix map is
    case-sensitive. Uppercase only the leading alphabetic run, never the locus."""
    m = re.match(r"^([A-Za-zĀĪŪṚṜḶṆṢŚṬḌṄÑṂḤāīūṛṝḷṇṣśṭḍṅñṃḥ.]+)(.*)$", body, re.S)
    if not m:
        return None
    head = m.group(1)
    return head.upper() + m.group(2) if head != head.upper() else None


def _r_drop_alt_numbering(attrs, body):
    """`VARĀH. BṚH. S. 41 (40),5.` fails; `… 41,5.` resolves. PWG prints the other
    edition's chapter in parentheses; the parenthetical is not part of the locus."""
    out = re.sub(r"\s*\((\d+)\)", "", body)
    return out if out != body else None


def _r_expand_pratis(attrs, body):
    """`ṚV. PRĀT. 13,13.` fails; `ṚV. PRĀTIŚ. 13,13.` resolves to the rvps viewer —
    two abbreviations of one work. NB this pays off for ṚV only: TS./AV./VS.
    Prātiśākhya are distinct works with no viewer, and the retest says so."""
    out = re.sub(r"\bPRĀT\.", "PRĀTIŚ.", body)
    return out if out != body else None


def _r_drop_range_tail(attrs, body):
    """`ŚAT. BR. 12,5,2,9. fgg.` — `fgg.`/`ff.` ("and following") is a reading
    instruction, not a coordinate; the head locus is the link target."""
    out = re.sub(r"\s*\b(fgg?|ff)\.\s*$", "", body).strip()
    return out if out != body else None


def _r_drop_trailing_prose(attrs, body):
    """A citation whose numbers are followed by editorial prose
    (`… 5,28,9. Sūryas iv,26`) — keep the leading coordinate run."""
    m = re.match(r"^(.*?\d[\d,\.]*)\s+[^\d\s].{3,}$", body, re.S)
    return m.group(1).strip() if m else None


def _r_drop_edition_tail(attrs, body):
    """`R. ed. Bomb. 1,2,3` — the edition marker sits between prefix and locus and
    is not a coordinate. Only tried when an edition token is actually present."""
    out = re.sub(r"\bed\.\s*(Bomb|Calc|Ser|Schl)\w*\.?\s*", "", body)
    return out if out != body else None


REPAIRS = [
    ("uppercase_prefix", _r_uppercase_prefix),
    ("drop_alt_numbering", _r_drop_alt_numbering),
    ("expand_pratis", _r_expand_pratis),
    ("drop_range_tail", _r_drop_range_tail),
    ("drop_edition_tail", _r_drop_edition_tail),
    ("drop_trailing_prose", _r_drop_trailing_prose),
]


def try_repairs(ll, tag):
    """Return (repair_name, href) for the first repair that resolves, else None.

    Repairs compose one level: a citation can need both a dropped range tail and
    an expanded abbreviation. Order is fixed, so the answer is deterministic.
    """
    m = LS_PARTS.match(_ws(tag))
    if not m:
        return None
    attrs, body = m.group(1), m.group(2)

    def attempt(b, trail):
        cand = "<ls%s>%s</ls>" % (attrs, b)
        st, href = ll.resolve(cand)
        return (("+".join(trail), href) if st == HIT else None)

    for name, fn in REPAIRS:
        b1 = fn(attrs, body)
        if not b1 or b1 == body:
            continue
        got = attempt(b1, [name])
        if got:
            return got
        for name2, fn2 in REPAIRS:
            if name2 == name:
                continue
            b2 = fn2(attrs, b1)
            if not b2 or b2 == b1:
                continue
            got = attempt(b2, [name, name2])
            if got:
                return got
    return None


# ------------------------------------------------------------------------ scan
def scan():
    ll = LsLinks()
    total = mintable = repaired = 0
    by_repair = collections.Counter()
    by_source_repaired = collections.Counter()
    unrepaired_by_source = collections.Counter()
    examples = collections.defaultdict(list)
    seen_cache = {}

    for line in io.open(STORE, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        for tag in LS_RE.findall(json.loads(line).get("de") or ""):
            total += 1
            key = _ws(tag)
            if key in seen_cache:
                status, res = seen_cache[key]
            else:
                status, _ = ll.resolve(tag)
                res = try_repairs(ll, tag) if status == MINTABLE else None
                seen_cache[key] = (status, res)
            if status != MINTABLE:
                continue
            mintable += 1
            n_attr, visible = ll.parts(tag)
            src = (n_attr or visible or "?").split()[0].rstrip(".,") if (n_attr or visible) else "?"
            if res:
                repaired += 1
                by_repair[res[0]] += 1
                by_source_repaired[src] += 1
                if len(examples[res[0]]) < 4:
                    examples[res[0]].append((key, res[1]))
            else:
                unrepaired_by_source[src] += 1
    return dict(total=total, mintable=mintable, repaired=repaired,
                by_repair=by_repair, by_source_repaired=by_source_repaired,
                unrepaired_by_source=unrepaired_by_source, examples=examples)


def write_report(r):
    os.makedirs(REPORTS, exist_ok=True)
    p = os.path.join(REPORTS, "ls_gap_repairable.tsv")
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("repair\toccurrences\texample_citation\texample_href\n")
        for name, n in r["by_repair"].most_common():
            ex = r["examples"][name][0] if r["examples"][name] else ("", "")
            fh.write("%s\t%d\t%s\t%s\n" % (name, n, ex[0], ex[1]))
    p2 = os.path.join(REPORTS, "ls_gap_unrepairable_by_source.tsv")
    with io.open(p2, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("source\toccurrences\n")
        for s, n in r["unrepaired_by_source"].most_common():
            fh.write("%s\t%d\n" % (s, n))
    return p, p2


def main():
    if not os.path.exists(STORE):
        print("store not found: %s — set PWG_RU_DATA_ROOT" % STORE)
        return 1
    print("scanning + repairing %s ..." % STORE)
    r = scan()
    m = max(r["mintable"], 1)
    print("\n<ls> occurrences       : %d" % r["total"])
    print("⚑ mintable             : %d" % r["mintable"])
    print("  repairable by a rule : %6d  %5.1f%% of ⚑   (a pattern here WOULD pay off)"
          % (r["repaired"], 100.0*r["repaired"]/m))
    print("  not repairable       : %6d  %5.1f%% of ⚑   (no viewer exists — digitisation)"
          % (r["mintable"]-r["repaired"], 100.0*(r["mintable"]-r["repaired"])/m))
    print("\nrepairs that pay, by yield:")
    for name, n in r["by_repair"].most_common():
        ex = r["examples"][name][0] if r["examples"][name] else ("", "")
        print("  %-34s %5d   e.g. %s" % (name, n, ex[0][:44]))
    print("\nsources whose repaired citations now resolve:")
    for s, n in r["by_source_repaired"].most_common(12):
        print("  %-18s %5d" % (s, n))
    print("\ntop unrepairable sources (need a viewer, not a regex):")
    for s, n in r["unrepaired_by_source"].most_common(15):
        print("  %-18s %5d" % (s, n))
    a, b = write_report(r)
    print("\nwrote %s\n      %s" % (a, b))
    return 0


# --------------------------------------------------------------------- selftest
def selftest():
    ll = LsLinks()
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    # every repair must be grounded in a real failing->resolving pair
    cases = [
        ("<ls>MBh. 1,71,17.</ls>", "uppercase_prefix"),
        ("<ls>VARĀH. BṚH. S. 41 (40),5.</ls>", "drop_alt_numbering"),
        ("<ls>ṚV. PRĀT. 13,13.</ls>", "expand_pratis"),
    ]
    for tag, want in cases:
        got = try_repairs(ll, tag)
        check(got is not None and got[0].split("+")[0] == want,
              "%s -> %s" % (tag[:38], (got[0] + " " + got[1][:44]) if got else "NO REPAIR"))

    # a repair must never rescue a work that genuinely has no viewer
    for tag in ("<ls>TS. PRĀT. 3,10.</ls>", "<ls>AV. PRĀT. 1,1.</ls>",
                "<ls>SUŚR. 1,2,3</ls>", "<ls>DAŚAK. 19,8</ls>"):
        check(try_repairs(ll, tag) is None,
              "no false rescue for %s (distinct work, no viewer)" % tag[:32])

    # an already-resolving citation is never touched
    st, href = ll.resolve("<ls>MBH. 1,71,17.</ls>")
    check(st == HIT, "a resolving citation stays resolved, untouched by repair")

    # repairs are pure: they never fabricate digits
    body = "41 (40),5."
    check("40" not in _r_drop_alt_numbering("", body) and "41" in _r_drop_alt_numbering("", body),
          "drop_alt_numbering removes the alternate, keeps the printed coordinate")
    check(_r_uppercase_prefix("", "MBH. 1,2") is None,
          "uppercase_prefix is a no-op on an already-uppercase prefix")

    print("ls_gap_repair selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
