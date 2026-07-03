"""Phase 5 of HERITAGE_INRIA_ROADMAP.md: DICO French-gloss witness layer.

For each mw_key1 in mw_heritage_crosswalk.tsv that resolved to a DICO anchor
(heritage_entry_anchor = "DICO/<file>.html#<key>"), extract the French gloss
prose that follows that entry's <a class="navy" name="KEY"> anchor in the
raw DICO HTML, up to the next GENUINE entry boundary — a navy anchor
immediately preceded by a Deva headword span or a <p></p> break (see
is_entry_boundary/true_boundary_start below). Navy anchors nested mid-prose
(a capitalized proper noun mentioned inline, a dual-form aside) are NOT
boundaries, so they don't truncate the entry they're embedded in. Reuses
heritage_mw_crosswalk.py's key-normalisation conventions rather than
re-parsing DICO's anchor scheme from scratch.

Output: heritage_dico_gloss.tsv (mw_key1, heritage_entry_anchor, gloss_fr, cross_refs)
"""
import sys, os, re, glob, csv, html
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import heritage_mw_crosswalk as hmc

MIRROR = os.path.join(HERE, "heritage_mirror")
CROSSWALK_TSV = os.path.join(HERE, "mw_heritage_crosswalk.tsv")
OUT_TSV = os.path.join(HERE, "heritage_dico_gloss.tsv")

# A genuine new-entry boundary: a navy anchor immediately preceded (modulo
# whitespace/&#160; entities) by a tag close — either a Deva headword span
# (</span>, a fresh top-level headword) or a paragraph break (<p></p>, a
# compound/sub-entry sharing the previous headword's letter group). Navy
# anchors preceded by plain running prose (e.g. a capitalized proper noun
# or a "du."-tagged dual form mentioned inline within another entry's
# gloss) are NOT boundaries — they're cross-reference targets embedded in
# the surrounding entry's own definition and must not truncate it.
STRIP_WS_RE = re.compile(r'(?:\s|&#160;|&#xA0;)+$')
NAVY_OPEN_RE = re.compile(r'<a class="navy" name="([^"]*)"')


def is_entry_boundary(text, anchor_start):
    window = text[max(0, anchor_start - 80):anchor_start]
    prefix = STRIP_WS_RE.sub('', window)
    return prefix.endswith('>')


def true_boundary_start(text, anchor_start):
    """The previous entry's gloss must end BEFORE this boundary anchor's own
    Deva headword span (or preceding <p>), not at the anchor itself — else
    the next headword's Devanagari text leaks into the previous entry's gloss."""
    win_start = max(0, anchor_start - 200)
    window = text[win_start:anchor_start]
    marker = max(window.rfind('<span class="deva"'), window.rfind('<p>'))
    return win_start + marker if marker != -1 else anchor_start
# blue = inline citation link within the gloss prose; green = trailing "see
# also" synonym/derived-form link. Both point at other DICO entry anchors.
CROSSREF_HREF_RE = re.compile(r'<a class="(?:blue|green)" href="[^#"]*#([^"]*)"')
TAG_RE = re.compile(r'<[^>]+>')


def strip_html(fragment):
    text = TAG_RE.sub(' ', fragment)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def entry_spans(text):
    """Yield (key, start_of_gloss, end_of_gloss) for every navy anchor in file text.

    end_of_gloss is the next GENUINE entry boundary (see is_entry_boundary),
    not just the next navy anchor — so a proper-noun cross-reference or
    dual-form anchor nested mid-paragraph doesn't truncate the entry it's
    nested in.
    """
    navy_opens = list(NAVY_OPEN_RE.finditer(text))
    boundary_starts = [true_boundary_start(text, m.start())
                        for m in navy_opens if is_entry_boundary(text, m.start())]
    boundary_starts.append(len(text))
    bi = 0
    for m in navy_opens:
        key = m.group(1)
        close = text.find('</a>', m.end())
        if close == -1:
            continue
        gloss_start = close + len('</a>')
        while bi + 1 < len(boundary_starts) and boundary_starts[bi] <= gloss_start:
            bi += 1
        gloss_end = boundary_starts[bi]
        yield key, gloss_start, gloss_end


def build_file_index():
    """Cache each DICO file's raw text and its parsed entry spans, keyed by filename."""
    cache = {}
    for fp in sorted(glob.glob(os.path.join(MIRROR, "DICO", "*.html"))):
        fname = os.path.basename(fp)
        text = open(fp, encoding='utf-8').read()
        cache[fname] = (text, list(entry_spans(text)))
    return cache


def main():
    if not os.path.exists(CROSSWALK_TSV):
        sys.exit(f"{CROSSWALK_TSV} not found — run heritage_mw_crosswalk.py first (Phase 2).")

    file_cache = build_file_index()

    rows = []
    n_covered_resolved = 0
    n_extracted = 0
    n_skip_no_span_match = 0

    with open(CROSSWALK_TSV, encoding='utf-8', newline='') as f:
        r = csv.DictReader(f, delimiter='\t')
        for row in r:
            anchor = row['heritage_entry_anchor']
            if not anchor:
                continue
            n_covered_resolved += 1
            fname, key = anchor.split('/')[1].split('#', 1)
            text, spans = file_cache.get(fname, ("", []))
            match = None
            for k, gs, ge in spans:
                if k == key:
                    match = (gs, ge)
                    break
            if match is None:
                n_skip_no_span_match += 1
                continue
            gs, ge = match
            fragment = text[gs:ge]
            cross_refs = sorted(set(CROSSREF_HREF_RE.findall(fragment)))
            gloss_fr = strip_html(fragment)
            if not gloss_fr:
                n_skip_no_span_match += 1
                continue
            n_extracted += 1
            rows.append((row['mw_key1'], anchor, gloss_fr, "|".join(cross_refs)))

    with open(OUT_TSV, 'w', encoding='utf-8', newline='\n') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(["mw_key1", "heritage_entry_anchor", "gloss_fr", "cross_refs"])
        for row in rows:
            w.writerow(row)

    print(f"crosswalk rows with a resolved DICO anchor: {n_covered_resolved}")
    print(f"glosses extracted: {n_extracted}")
    print(f"skipped (no matching span / empty gloss): {n_skip_no_span_match}")
    print(f"written: {OUT_TSV}")


if __name__ == "__main__":
    main()
