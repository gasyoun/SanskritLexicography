#!/usr/bin/env python3
"""H6128: UP031 manual-rewrite assist - deterministic printf->f-string for the SAFE class only.

Converts `"..." % (a, b)` sites where:
  - the left side is a plain (possibly implicitly concatenated) string literal
    with NO backslashes, NO braces, and not both quote characters;
  - placeholders are exactly %s %r %d %i %x %o %f %F %e %E %g %G %% with NO
    mapping keys and NO width/precision specs;
  - the right side is a tuple (or single expr) of simple args: Name / Attribute /
    Subscript / Constant (no starred, no dynamic fmt).
Anything else is REFUSED and counted - the residue stays for hand work.
Deterministic: same input bytes -> same output bytes.
"""
import argparse
import ast
import json
import re
import sys
from pathlib import Path

FULL_SPEC = re.compile(r"%(?:%|[srdioxXfFeEgG])")
PLACEHOLDER = re.compile(r"%(?:%|[srdioxXfFeEgG])")
PRINTF_SPEC = re.compile(r"%(?:\([^)]*\))?[#0\-+ ]*[0-9]*(?:\.[0-9]+)?[hlL]*(?:%|[srdioxXeEfFgGcrsa])")
CONVERSION = {"s": "", "r": "!r", "d": ":d", "i": ":d", "x": ":x", "o": ":o",
              "f": ":f", "F": ":F", "e": ":e", "E": ":E", "g": ":g", "G": ":G"}
SIMPLE_ARG = (ast.Name, ast.Attribute, ast.Subscript, ast.Constant)


def specs_of(value):
    return PRINTF_SPEC.findall(value)


def convert_file(path: Path, apply: bool):
    src = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        print(f"SKIP {path}: parse error {e}", file=sys.stderr)
        return 0, 0, src
    sites = []
    refused = [0]

    class V(ast.NodeVisitor):
        def visit_BinOp(self, node):
            if isinstance(node.op, ast.Mod):
                why = try_site(node)
                if why is None:
                    sites.append(node)
                else:
                    refused[0] += 1
            self.generic_visit(node)

    def try_site(node):
        left = node.left
        if not (isinstance(left, ast.Constant) and isinstance(left.value, str)):
            return "not a plain literal"
        value = left.value
        if "{" in value or "}" in value:
            return "braces in literal"
        if "\\" in value:
            return "backslash in literal"
        if "\n" in value or "\r" in value:
            return "newline in literal"
        if '"' in value and "'" in value:
            return "both quote styles"
        specs = specs_of(value)
        # every % in the literal must be one of our SIMPLE specs (no flags/width/precision)
        pos = 0
        n_specs = 0
        while True:
            m = PLACEHOLDER.search(value, pos)
            if not m:
                break
            if "%" in value[pos:m.start()]:
                return "stray % between placeholders"
            n_specs += 1
            pos = m.end()
        if "%" in value[pos:]:
            return "non-simple spec / stray %"
        if n_specs == 0:
            return "no placeholders"
        right = node.right
        args = list(right.elts) if isinstance(right, ast.Tuple) else [right]
        if len(args) != n_specs:
            return "arity mismatch"
        for a in args:
            if isinstance(a, ast.Starred) or not isinstance(a, SIMPLE_ARG):
                return "dynamic/complex arg"
        quote = "'" if '"' not in value else '"'
        if any(quote in ast.unparse(a) for a in args):
            return "arg contains the chosen quote"
        return None

    V().visit(tree)

    # keep only OUTERMOST sites - a nested BinOp inside an accepted site's span
    # would be spliced twice with stale coordinates and corrupt the file
    sites = [n for n in sites if not any(
        o is not n and o.lineno <= n.lineno and o.col_offset <= n.col_offset
        and (o.end_lineno, o.end_col_offset) >= (n.end_lineno, n.end_col_offset)
        for o in sites)]

    lines = src.splitlines(keepends=True)
    edits = []
    for node in sorted(sites, key=lambda n: (n.lineno, n.col_offset), reverse=True):
        left = node.left
        value = left.value
        args = list(node.right.elts) if isinstance(node.right, ast.Tuple) else [node.right]
        quote = "'" if '"' not in value else '"'
        out, ph = [], 0
        pos = 0
        for m in PLACEHOLDER.finditer(value):
            out.append(value[pos:m.start()])
            spec = m.group(0)
            if spec == "%%":
                out.append("%")
            else:
                expr = ast.unparse(args[ph])
                ph += 1
                out.append("{" + expr + CONVERSION[spec[-1]] + "}")
            pos = m.end()
        out.append(value[pos:])
        new_text = "f" + quote + "".join(out).replace(quote, "\\" + quote) + quote
        edits.append((node.lineno, node.col_offset, node.end_lineno, node.end_col_offset, new_text))

    lines2 = list(lines)
    for sl, sc, el, ec, repl in sorted(edits, reverse=True):
        if sl == el:
            lines2[sl - 1] = lines2[sl - 1][:sc] + repl + lines2[sl - 1][ec:]
        else:
            lines2[sl - 1] = lines2[sl - 1][:sc] + repl + lines2[el - 1][ec:]
            del lines2[sl:el]
    new_src = "".join(lines2)
    if new_src != src:
        compile(new_src, str(path), "exec")  # syntax gate
    if apply and new_src != src:
        path.write_text(new_src, encoding="utf-8")
    return len(sites), refused[0], new_src


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("files", nargs="*")
    args = ap.parse_args()
    total, refused, touched = 0, 0, 0
    detail = []
    for f in map(Path, args.files):
        try:
            n, r, new = convert_file(f, args.apply)
        except SyntaxError as e:
            # fail-soft: the compile gate refused this file's rewrite - leave it
            # untouched and count every candidate site in it as refused
            print(f"GATE-REFUSED {f}: {e}", file=sys.stderr)
            refused += 1
            detail.append({"file": str(f), "converted": 0, "refused": "gate", "error": str(e)})
            continue
        total += n
        refused += r
        if n:
            touched += 1
            detail.append({"file": str(f), "converted": n, "refused": r})
    print(json.dumps({"mode": "apply" if args.apply else "dry-run",
                      "files": len(args.files), "files_touched": touched,
                      "sites_converted": total, "sites_refused": refused}))
    Path("/tmp/h6128_rewrite_detail.json").write_text(json.dumps(detail, indent=1))


if __name__ == "__main__":
    main()
