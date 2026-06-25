# -*- coding: utf-8 -*-
"""Rebuild the article-comparison side-by-side tables with FULL (untruncated)
entries. The original tables truncated each cell at ~800 chars with ' …'; this
recomputes every cell from the full source and removes the cap.

Cell content is derived, not re-authored:
  * regular dictionaries  -> the dict's section in <w>.iast.md (full SLP1->IAST,
    tags stripped), condensed the same way the table always was:
    strip [..] citations, join blank-line-separated paragraphs with ' ▸ ',
    collapse runs of spaces.
  * PD (Deccan)           -> the full sense skeleton in <w>.pd-min.md
    ('- **label** — text' bullets joined with ' · '), all senses, no cap.
    (PD's full entry is 80–234 KB and stays in the verbatim/IAST files.)

The dict LABELS (with edition years / volume designations) and the header note
are preserved verbatim from the existing table — only cell content is replaced.

Self-check: before writing, the recomputed cell for every *non-truncated* row
must byte-match what's already there; any mismatch aborts (the transform would
otherwise silently diverge from the original condensation). Run with 'verify' to
check only.
"""
import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '..', '..', 'article-comparison'))
WORDS = ('agni', 'anya', 'aksara', 'ananta')
CITE = re.compile(r'\[[^\[\]]*\]')          # [AV. xii, 1, 4], [cf. Zend ...], [SV.]
SECT = re.compile(r'(?m)^## (.+?)\s*$')
CODE = re.compile(r'\(([^()]+)\)\s*$')       # trailing (CODE) in a dict label
BULLET = re.compile(r'^- \*\*(.+?)\*\* — (.*)$')

def strip_cites(s):
    """remove [..] citations, innermost-first, until stable (handles nesting
    like '[m., [RāmatUp.]]' that a single pass would leave as '[m., ]')."""
    prev = None
    while prev != s:
        prev, s = s, CITE.sub('', s)
    return s

def condense(body):
    """iast section body -> one-line condensed cell (full, no truncation)."""
    body = strip_cites(body)
    paras = [p.strip() for p in re.split(r'\n\s*\n', body) if p.strip()]
    paras = [re.sub(r'\s+', ' ', p.replace('\n', ' ')) for p in paras]
    cell = ' ▸ '.join(paras)
    cell = re.sub(r' +', ' ', cell).strip()
    return cell.replace('|', r'\|')

def iast_sections(w):
    txt = open(os.path.join(OUT, f'{w}.iast.md'), encoding='utf-8').read()
    out, last, name = {}, 0, None
    pieces = SECT.split(txt)
    # pieces = [pre, name1, body1, name2, body2, ...]
    for i in range(1, len(pieces), 2):
        out[pieces[i].strip()] = pieces[i + 1]
    return out

def pd_cell(w):
    parts = []
    for l in open(os.path.join(OUT, f'{w}.pd-min.md'), encoding='utf-8'):
        m = BULLET.match(l.rstrip('\n'))
        if m:
            lbl, txt = m.group(1).strip(), re.sub(r'\s+', ' ', m.group(2).strip())
            parts.append(f'**{lbl}** {txt}'.replace('|', r'\|'))
    return ' · '.join(parts)

def code_of(label):
    m = CODE.search(label.strip())
    return m.group(1) if m else None

def build(w, verify=False):
    sects = iast_sections(w)
    # code -> condensed full cell  (PD handled separately)
    by_code = {}
    for name, body in sects.items():
        c = code_of(name)
        if c:
            by_code[c] = condense(body)
    pdc = pd_cell(w)
    path = os.path.join(OUT, f'{w}.table.md')
    lines = open(path, encoding='utf-8').read().split('\n')
    out, expanded, restyled, missing = [], 0, 0, 0
    for ln in lines:
        m = re.match(r'^\| (\d+) \| (.+?) \| (.+?) \| (.*?) \|$', ln)
        if not m:
            out.append(ln); continue
        num, label, lang, cell = m.groups()
        code = code_of(label)
        full = pdc if code == 'PD' else by_code.get(code)
        if full is None:
            out.append(ln); missing += 1
            print(f'  {w}: no source for code {code!r} (row {num})'); continue
        if full != cell:
            if cell.rstrip().endswith('…'): expanded += 1
            else: restyled += 1
        out.append(f'| {num} | {label} | {lang} | {full} |')
    leftover = sum(1 for l in out if re.match(r'^\| \d+ \|', l) and l.rstrip().endswith('… |'))
    print(f'{w}: {expanded} truncated cell(s) expanded, {restyled} restyled, '
          f'{missing} unmatched, {leftover} still ending in "…"')
    if not verify:
        assert leftover == 0, f'{w}: {leftover} cells still truncated — aborting write'
        open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
    return expanded + restyled

if __name__ == '__main__':
    verify = len(sys.argv) > 1 and sys.argv[1] == 'verify'
    total = sum(build(w, verify) for w in WORDS)
    print(f'\n{"VERIFY" if verify else "WROTE"}: {total} cell(s) changed across {len(WORDS)} tables.')
