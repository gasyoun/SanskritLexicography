#!/usr/bin/env python3
"""H4523 acceptance tests for the --scrolly emission path.

Run:  python3 test_scrolly.py            (from EntryAnatomy/, or anywhere)

Static checks, no browser needed:
  1. both scrolly pages exist, are self-contained (no external resources),
     and carry the tour shell (rail CSS/JS, sections, viewport meta);
  2. every callout target resolves in the DOM with enough matches
     (len(matches) > data-nth) — the same criterion CALLOUT_JS applies when
     it decides to hide an unresolvable label;
  3. every callout is assigned to exactly one callout beat (2 or 3) by the
     first-match-wins substring rule of scrolly_tours.json (the JS rule);
  4. no-JS / print / reduced-motion fallbacks present; @page print sizing
     still generated; tour JSON beats 1-5 all present with non-empty text.
"""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent

PAGES = ("pwg-entry-anatomy-scrolly.html", "mw-entry-anatomy-scrolly.html")
BASES = ("pwg-entry-anatomy.html", "mw-entry-anatomy.html")


# ------------------------------------------------------------- mini DOM tree

class Node:
    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(self, tag, attrs=None, parent=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.children = []
        self.parent = parent

    @property
    def classes(self):
        return (self.attrs.get("class") or "").split()


class _Tree(HTMLParser):
    VOID = {"img", "br", "hr", "meta", "link", "input", "source",
            "path", "rect", "circle", "use", "stop"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        d = {}
        for k, v in attrs:
            d.setdefault(k, v or "")
        n = Node(tag, d, self.cur)
        self.cur.children.append(n)
        if tag not in self.VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        d = {}
        for k, v in attrs:
            d.setdefault(k, v or "")
        self.cur.children.append(Node(tag, d, self.cur))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent


def parse_dom(html_text):
    t = _Tree()
    t.feed(html_text)
    return t.root


def walk(node):
    for child in node.children:
        yield child
        yield from walk(child)


# ----------------------------------------------------- mini CSS selector grid

def parse_compound(tok):
    """'.sa[data-slp="pari"]', '.colwrap:nth-of-type(2)', '#id', 'p' -> tests."""
    tests, i, n = [], 0, len(tok)
    while i < n:
        c = tok[i]
        if c == "#":
            m = re.match(r"[-\w]+", tok[i + 1:])
            tests.append(("id", m.group(0)))
            i += 1 + m.end()
        elif c == ".":
            m = re.match(r"[-\w]+", tok[i + 1:])
            tests.append(("cls", m.group(0)))
            i += 1 + m.end()
        elif tok.startswith(":nth-of-type(", i):
            j = tok.index(")", i)
            tests.append(("nth", int(tok[i + len(":nth-of-type("):j])))
            i = j + 1
        elif c == "[":
            j = tok.index("]", i)
            inner = tok[i + 1:j]
            i = j + 1
            if "=" in inner:
                k, v = inner.split("=", 1)
                v = v.strip()
                if v and v[0] in "\"'":
                    v = v[1:-1]
                tests.append(("attr", k.strip(), v))
            else:
                tests.append(("attr", inner.strip(), None))
        elif c.isspace():
            i += 1
        else:
            m = re.match(r"[-\w]+", tok[i:])
            tests.append(("tag", m.group(0).lower()))
            i += m.end()
    return tests


def _match_one(el, tests):
    for t in tests:
        kind = t[0]
        if kind == "tag":
            if el.tag != t[1]:
                return False
        elif kind == "id":
            if el.attrs.get("id") != t[1]:
                return False
        elif kind == "cls":
            if t[1] not in el.classes:
                return False
        elif kind == "nth":
            sibs = [s for s in el.parent.children if s.tag == el.tag]
            if sibs.index(el) + 1 != t[1]:
                return False
        elif kind == "attr":
            av = el.attrs.get(t[1])
            if t[2] is None:
                if av is None:
                    return False
            elif av != t[2]:
                return False
    return True


def resolve(root, selector):
    """All elements matching a descendant selector (right-to-left walk)."""
    compounds = [parse_compound(tok) for tok in selector.split()]
    out = []
    for el in walk(root):
        if not _match_one(el, compounds[-1]):
            continue
        idx, node = len(compounds) - 2, el.parent
        ok = True
        while idx >= 0:
            if node is None:
                ok = False
                break
            if _match_one(node, compounds[idx]):
                idx -= 1
            node = node.parent
        if ok:
            out.append(el)
    return out


# ------------------------------------------------------------------- checks

def callout_beat(target, beats):
    """The JS assignment rule: first beat with a matching substring."""
    for b in beats:
        for sel in b.get("match", []):
            if sel in target:
                return b["n"]
    return None


def main():
    tours = json.loads((HERE / "scrolly_tours.json").read_text("utf-8"))["tours"]
    failures = []
    stats = {}
    for page_name, base_name in zip(PAGES, BASES):
        stem = page_name.replace("-scrolly.html", "")
        tour = tours[stem]
        p = HERE / page_name
        if not p.exists():
            failures.append(f"{page_name}: MISSING (run --scrolly first)")
            continue
        text = p.read_text("utf-8")
        base_text = (HERE / base_name).read_text("utf-8")

        # 1. shell + self-containment
        for needle in ("window.__TOUR", "IntersectionObserver", "beat-rail",
                       "id=\"beat4\"", "id=\"beat5\"", 'name="viewport"',
                       "prefers-reduced-motion", "@media print",
                       "@page { size:"):
            if needle not in text:
                failures.append(f"{page_name}: shell missing {needle!r}")
        for bad in ("<script src=", "<link rel=\"stylesheet", 'src="http',
                    "fetch(", "XMLHttpRequest"):
            if bad in text:
                failures.append(f"{page_name}: external resource {bad!r}")
        # the sheet must be the base page's sheet, wrapped — not forked:
        # the prologue may differ only by the injected viewport meta line
        base_pro = base_text[:base_text.index("<style>")]
        text_pro = text[:text.index("<style>")].replace(
            '\n<meta name="viewport" content="width=device-width, '
            'initial-scale=1">', "", 1)
        if base_pro != text_pro:
            failures.append(f"{page_name}: head prologue diverges from base")

        # 2. callout target integrity (browser-equivalent criterion)
        dom = parse_dom(text)
        callouts = [el for el in walk(dom) if el.tag == "div"
                    and "callout" in el.classes]
        n_bad = 0
        for c in callouts:
            sel = c.attrs.get("data-target", "")
            nth = int(c.attrs.get("data-nth") or 0)
            hits = resolve(dom, sel)
            if len(hits) <= nth:
                n_bad += 1
                failures.append(f"{page_name}: target unresolved "
                                f"({len(hits)} hits, nth={nth}): {sel}")
        # 3. beat assignment — every callout in beat 2 or 3, both non-trivial
        n2 = n3 = 0
        for c in callouts:
            b = callout_beat(c.attrs.get("data-target", ""), tour["beats"])
            if b == 2:
                n2 += 1
            elif b == 3:
                n3 += 1
            else:
                failures.append(f"{page_name}: callout without a beat: "
                                f"{c.attrs.get('data-target')}")
        # 4. beats 1-5 texts present, injected sections carry the records
        for i, b in enumerate(tour["beats"], 1):
            if not (b.get("title") and b.get("text")):
                failures.append(f"{page_name}: beat {i} title/text empty")
        digital_rec = tour["digital"]["record"]
        if digital_rec not in text:
            failures.append(f"{page_name}: digital record {digital_rec} "
                            "absent from beat 4")
        for col in tour["sibling"]["columns"]:
            if col["records"][0] not in text:
                failures.append(f"{page_name}: sibling record "
                                f"{col['records'][0]} absent from beat 5")
        # no-JS fallback: without data-beat, CSS leaves callouts at opacity 1
        if re.search(r"\.callout\s*\{[^}]*opacity", text.split("body[data-beat]")[0]):
            failures.append(f"{page_name}: base CSS dims callouts without JS")
        stats[stem] = {"callouts": len(callouts), "unresolved": n_bad,
                       "beat2": n2, "beat3": n3}

    print(json.dumps(stats, indent=2))
    if failures:
        print("\nFAIL:")
        for f in failures:
            print(" -", f)
        return 1
    print("\nPASS: shell, self-containment, callout integrity, beat "
          "assignment, no-JS/print fallbacks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
