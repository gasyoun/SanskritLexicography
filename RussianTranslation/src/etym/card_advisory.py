"""Etymology advisory block for pwg_ru review cards (KEWA modern-IE lane).

The `advises` edge registered in Uprava's ``interlinks_edges.tsv`` (audit Q3,
28-08-2026, MG ruling) is real but stayed *human* advisory: dictionary
etymology arbitrates sense-order/register decisions in review, with no
programmatic consumer.  This module is the card-surface half of that edge -
READ-ONLY display, never a gate:

* it answers, per reviewed PWG ``key1``, "does Mayrhofer's KEWA treat this
  lexeme, and where" (volume + page + the joined heading + match basis);
* it is labelled КОНСУЛЬТАТИВНО on the card and must never influence
  accept/reject mechanics - the vote digest hashes ``ru``/``de`` only, and
  this block rides the display surfaces, so votes already cast cannot be
  invalidated by adding or changing it;
* absence of the crosswalk file is a silent no-op (the SpellCheck
  ``union_attestation`` graceful-absence pattern), so sheets cut on a clone
  without ``RussianTranslation/data/etym/`` render unchanged.

Inputs (read-only): ``kewa_pwg_crosswalk.tsv`` (H3169) - one row per KEWA
heading, columns ``lane, kewa_seq, vol, page, heading_idx, kewa_slp1,
match_basis, pwg_key1, ...``.  The *traditional* lane
(``pwg_etymology.tsv``) stays a separate field by the C4 ruling and is
deliberately NOT rendered here.
"""
from __future__ import annotations

import html
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
RT_ROOT = os.path.dirname(os.path.dirname(HERE))  # .../RussianTranslation
DEFAULT_CROSSWALK = os.path.join(
    RT_ROOT, "data", "etym", "kewa_pwg_crosswalk.tsv")

#: Cards show at most this many KEWA rows; the rest collapse into "+N ещё".
MAX_ROWS_PER_KEY = 6

_HEADER = ('<div class="etymadv" style="margin-top:6px;padding:4px 8px;'
           'border:1px dashed #b8a88a;border-radius:6px;font-size:0.82em;'
           'background:rgba(216,163,102,0.06)">'
           '<div class="etymadv-h" style="font-weight:600;color:#8a6d3b;">'
           'Этимология (консультативно — не влияет на приёмку): Mayrhofer KEWA</div>')

_FOOT = ('<div class="etymadv-f" style="color:#7a7264;">Полный указатель: '
         '<a href="https://samskrtam.ru/sanskrit-lexicon/KEWA/">'
         'samskrtam.ru/sanskrit-lexicon/KEWA/</a> · lane=modern-IE, '
         'традиционная этимология PWG — отдельное поле (правило C4)</div>'
         '</div>')


def load_crosswalk(path=None):
    """key1 -> list of (vol, page, kewa_slp1, match_basis), file order.

    Returns {} when the file is absent (graceful absence = the block never
    renders, matching the union=N pattern).  Only ``lane == modern-IE`` rows
    are kept; the TSV is single-lane today, the filter is future-proofing.
    """
    path = path or DEFAULT_CROSSWALK
    if not os.path.exists(path):
        return {}
    by_key = {}
    with open(path, encoding="utf-8") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        idx = {name: i for i, name in enumerate(header)}
        need = ("lane", "vol", "page", "kewa_slp1", "match_basis", "pwg_key1")
        for name in need:
            if name not in idx:
                raise ValueError(f"{path}: crosswalk missing column {name!r}")
        for ln in fh:
            ln = ln.rstrip("\n")
            if not ln:
                continue
            c = ln.split("\t")
            if len(c) < len(header):
                continue
            if c[idx["lane"]] != "modern-IE":
                continue
            by_key.setdefault(c[idx["pwg_key1"]], []).append(
                (c[idx["vol"]], c[idx["page"]],
                 c[idx["kewa_slp1"]], c[idx["match_basis"]]))
    return by_key


def advisory_rows(key1, crosswalk):
    """Capped display tuples for one key1: [(vol, page, slp1, basis), more_n]."""
    rows = crosswalk.get(key1 or "", [])
    return rows[:MAX_ROWS_PER_KEY], max(0, len(rows) - MAX_ROWS_PER_KEY)


def advisory_html(key1, crosswalk, iast=None):
    """Display-only HTML block for one card; '' when nothing reaches key1.

    MUST stay out of every acceptance digest (it rides the display surfaces;
    ``card_digest`` hashes ru/de only, so appending this can never invalidate
    a cast vote).
    """
    rows, more = advisory_rows(key1, crosswalk)
    if not rows:
        return ""
    out = [_HEADER, '<table class="etymadv-t" style="border-collapse:collapse;">']
    for vol, page, slp1, basis in rows:
        shown = html.escape(iast) if iast else html.escape(slp1 or "?")
        out.append(
            "<tr><td>KEWA т.%s с.%s</td><td><i>%s</i></td>"
            "<td>%s</td></tr>"
            % (html.escape(vol or "?"), html.escape(page or "?"),
               shown, html.escape(basis or "?")))
    out.append("</table>")
    if more:
        out.append('<div class="etymadv-more">… ещё %d вхождений KEWA</div>'
                   % more)
    out.append(_FOOT)
    return "".join(out)


def _selftest():
    import tempfile

    fx = "\n".join([
        "lane\tkewa_seq\tvol\tpage\theading_idx\tkewa_slp1\tmatch_basis\t"
        "pwg_key1\twitness\tn_candidates\tlemma_route\troutes_agree\tflags",
        "modern-IE\t1\tI\t13\t0\ta\texact\ta\tPWG-key1\t1\ta\t0\t",
        "modern-IE\t2\tI\t13\t1\taj\texact\taja\tPWG-key1\t2\ta|lemma\t0\t",
        "modern-IE\t3\tII\t40\t0\tBU\tlemma\tBU\tPWG-key1\t1\tlemma\t0\t",
        "modern-IE\t4\tI\t14\t0\taT\texact\t*\twitness\t1\t?\t0\t",
        "traditional\t1\tI\t99\t0\tx\texact\ta\tPWG-key1\t1\ta\t0\t",
        "modern-IE\t5\tI\t15\t0\ta2\texact\ta\tPWG-key1\t1\ta\t0\t",
        "modern-IE\t6\tI\t16\t0\ta3\texact\ta\tPWG-key1\t1\ta\t0\t",
        "modern-IE\t7\tI\t17\t0\ta4\texact\ta\tPWG-key1\t1\ta\t0\t",
        "modern-IE\t8\tI\t18\t0\ta5\texact\ta\tPWG-key1\t1\ta\t0\t",
        "modern-IE\t9\tI\t19\t0\ta6\texact\ta\tPWG-key1\t1\ta\t0\t",
        "modern-IE\t10\tI\t20\t0\ta7\texact\ta\tPWG-key1\t1\ta\t0\t",
        "modern-IE\t11\tI\t21\t0\ta8\texact\ta\tPWG-key1\t1\ta\t0\t",
        "this row has,too,few,cols",
        "",
    ])
    checks = []
    def check(cond, label):
        checks.append((bool(cond), label))

    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "cw.tsv")
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(fx + "\n")
        cw = load_crosswalk(p)
        check(set(cw) == {"a", "aja", "BU", "*"}, "lane filter + key set")
        rows, more = advisory_rows("a", cw)
        check(len(rows) == MAX_ROWS_PER_KEY and more == 2,
              "cap 6 + more=2 (traditional row excluded)")
        h = advisory_html("a", cw, iast="a")
        check("с.13" in h and "с.21" not in h and "ещё 2" in h,
              "block shows capped rows + more-count")
        check("консультативно" in h and "KEWA" in h, "label present")
        check(advisory_html("zzz-nope", cw) == "", "miss → empty block")
    check(load_crosswalk(os.path.join("no", "such", "dir.tsv")) == {},
          "graceful absence → {}")
    check(advisory_html("a", {}) == "", "empty crosswalk → empty block")
    h2 = advisory_html("a", load_crosswalk(
        os.path.join(HERE, "..", "..", "data", "etym",
                     "kewa_pwg_crosswalk.tsv")) if os.path.exists(
        os.path.join(HERE, "..", "..", "data", "etym",
                     "kewa_pwg_crosswalk.tsv")) else _MINI_CW)
    check("</div>" in h2, "live crosswalk (when present) renders")
    bad = [l for ok, l in checks if not ok]
    for ok, label in checks:
        print(f"  {'ok ' if ok else 'FAIL'} {label}")
    print("CARD_ADVISORY SELFTEST", "OK" if not bad else "FAILED")
    return 0 if not bad else 1


_MINI_CW = {"a": [("I", "13", "a", "exact")]}


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
