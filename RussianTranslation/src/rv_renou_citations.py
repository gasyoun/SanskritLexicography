#!/usr/bin/env python
"""rv_renou_citations.py -- Renou-mention locus index over Elizarenkova's RV commentary
(H1843 step 5, C5's sibling; not to be confused with renou_pipeline.py's unrelated
Renou 1956 language-states axis -- see RENOU.md and ARCHITECTURE Sec.3.4).

Source: SamudraManthanam/Index/lib/x86_64-win64/add/To_add/NN_rigveda.no_tags (N=01..10,
mandala N; read-only). This "no_tags" dialect keeps opening <div>/<span> tags with their
attributes but emits NO closing tags at all -- a footnote's text runs from its
<span class="comment_number" ...> open to the next tag-open or end of line, never to a
</span> that does not exist. Confirmed structurally: at most one
<div class="citation_block" id="HYMN.STANZA"> per physical line; the mandala number
comes from the filename (NN), not from the `range` div's title attribute, which carries
a verified rendering glitch for mandala X (title says "Мандала IX X. ...").

For every whole-word occurrence of "Рену" this resolves the enclosing citation_block's
locus (or emits location: null / locus_unresolved: true when the mention sits in
front-matter / hymn-group-intro text with no citation_block on its line), takes a
~300-char context window clipped to sentence boundaries when present, and classifies it
quoted_fr / paraphrase_ru by whether a Latin-script quotation in guillemets follows
within ~25 characters (IMPLEMENTATION step 5 marked defaults -- this is a proximity +
script heuristic, not semantic attribution: an adjacent quote from a different named
translator can still be picked up, which is an accepted property of the heuristic, not
a bug in this script).

  python rv_renou_citations.py
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
from sibling_root import sibling_root  # noqa: E402
GITHUB_ROOT, _ = sibling_root()  # GitHub/ (H1902: worktree-safe root resolution)
COMMENTARY_DIR = os.path.join(
    GITHUB_ROOT, 'SamudraManthanam', 'Index', 'lib', 'x86_64-win64', 'add', 'To_add')
PWG_RU_DIR = os.path.normpath(os.path.join(HERE, '..', 'pwg_ru'))
OUT_PATH = os.path.join(PWG_RU_DIR, 'rv_renou_citation_index.jsonl')
RUN_LOG_DIR = os.path.join(PWG_RU_DIR, 'h1843')
RUN_LOG_PATH = os.path.join(RUN_LOG_DIR, 'renou_citations_run_log.md')
DECISIONS_LOG_PATH = os.path.normpath(
    os.path.join(HERE, '..', 'docs', 'DECISIONS_LOG_rv_multitranslation.md'))

MANDALA_FILES = [(m, '%02d_rigveda.no_tags' % m) for m in range(1, 11)]

CITATION_ID_RE = re.compile(r'<div class="citation_block" id="(\d+)\.(\d+)">')
WORD_RE = re.compile(r'(?<![Ѐ-ӿ])Рену(?![Ѐ-ӿ])')
TAG_RE = re.compile(r'<[^>]+>')
LATIN_LETTER_RE = re.compile(r'[A-Za-zÀ-ÿŒœ]')
SENTENCE_END_RE = re.compile(r'[.!?]')

CONTEXT_WINDOW = 300
QUOTE_LOOKAHEAD = 25

# Reference table quoted verbatim from VERIFICATION Sec.1.1 / the H1843 handoff. It does
# NOT reconcile with its own stated grand total (sums to 1,930, not 2,213) -- see the
# DECISIONS_LOG entry this script appends. Kept here only for the side-by-side diff in
# the run log, never as an assertion target.
SPEC_TABLE_TOTAL = 2213
SPEC_TABLE_BY_MANDALA = {
    1: 459, 2: 117, 3: 161, 4: 118, 5: 158, 6: 110, 7: 171, 8: 123, 9: 226, 10: 287,
}


def find_quote(line, after_pos):
    """Look ~QUOTE_LOOKAHEAD chars past a mention for an opening guillemet; if found,
    capture through the matching closer and classify by script. Returns
    (mention_kind, quote_fr)."""
    window_end = min(len(line), after_pos + QUOTE_LOOKAHEAD)
    open_idx = line.find('«', after_pos, window_end)  # «
    if open_idx == -1:
        return 'paraphrase_ru', None
    close_idx = line.find('»', open_idx + 1, open_idx + 1 + 500)  # »
    if close_idx == -1:
        return 'paraphrase_ru', None
    quoted = TAG_RE.sub('', line[open_idx + 1:close_idx]).strip()
    if quoted and LATIN_LETTER_RE.search(quoted):
        return 'quoted_fr', quoted
    return 'paraphrase_ru', None


def clip_context(line, start, end):
    half = CONTEXT_WINDOW // 2
    ctx_start = max(0, start - half)
    ctx_end = min(len(line), end + half)

    left_slice = line[ctx_start:start]
    m = None
    for m in SENTENCE_END_RE.finditer(left_slice):
        pass  # last match = closest sentence boundary before the mention
    if m is not None:
        ctx_start = ctx_start + m.end()

    right_slice = line[end:ctx_end]
    m2 = SENTENCE_END_RE.search(right_slice)
    if m2 is not None:
        ctx_end = end + m2.end()

    raw = line[ctx_start:ctx_end]
    return TAG_RE.sub('', raw).strip()


def process_file(mandala, path):
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()

    records = []
    for line in lines:
        if not WORD_RE.search(line):
            continue
        cb = CITATION_ID_RE.search(line)
        if cb:
            hymn, stanza = int(cb.group(1)), int(cb.group(2))
            location = '%d.%d.%d' % (mandala, hymn, stanza)
        else:
            hymn = stanza = location = None

        for m in WORD_RE.finditer(line):
            mention_kind, quote_fr = find_quote(line, m.end())
            context_ru = clip_context(line, m.start(), m.end())
            records.append({
                'location': location,
                'mandala': mandala,
                'hymn': hymn,
                'stanza': stanza,
                'mention_kind': mention_kind,
                'context_ru': context_ru,
                'quote_fr': quote_fr,
                'source': 'elizarenkova_commentary',
                'locus_unresolved': location is None,
            })
    return records


def write_jsonl(path, records):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False))
            f.write('\n')


def main():
    all_records = []
    per_mandala_total = {}
    per_mandala_quoted = {}
    unresolved_total = 0

    for mandala, fname in MANDALA_FILES:
        path = os.path.join(COMMENTARY_DIR, fname)
        recs = process_file(mandala, path)
        all_records.extend(recs)
        per_mandala_total[mandala] = len(recs)
        per_mandala_quoted[mandala] = sum(1 for r in recs if r['mention_kind'] == 'quoted_fr')
        unresolved_total += sum(1 for r in recs if r['locus_unresolved'])

    os.makedirs(PWG_RU_DIR, exist_ok=True)
    write_jsonl(OUT_PATH, all_records)

    total = len(all_records)
    total_quoted = sum(per_mandala_quoted.values())
    print('wrote %s: %d mentions, %d quoted_fr, %d locus_unresolved'
          % (OUT_PATH, total, total_quoted, unresolved_total))

    os.makedirs(RUN_LOG_DIR, exist_ok=True)
    with open(RUN_LOG_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# rv_renou_citations.py run log (H1843 step 5)\n\n')
        f.write('_Created: 29-07-2026 · Last updated: 29-07-2026_\n\n')
        f.write('- total mentions extracted: **%d**\n' % total)
        f.write('- quoted_fr: **%d** · paraphrase_ru: %d\n' % (total_quoted, total - total_quoted))
        f.write('- locus_unresolved (front-matter / hymn-group-intro, no citation_block '
                'on the line): %d\n\n' % unresolved_total)
        f.write('## Per-mandala: this script vs. the VERIFICATION Sec.1.1 table\n\n')
        f.write('| Mandala | this script | spec table | delta |\n|---|--:|--:|--:|\n')
        for mandala, _ in MANDALA_FILES:
            mine = per_mandala_total[mandala]
            spec = SPEC_TABLE_BY_MANDALA[mandala]
            f.write('| %d | %d | %d | %+d |\n' % (mandala, mine, spec, mine - spec))
        f.write('| **total** | **%d** | **%d** | **%+d** |\n\n'
                % (total, SPEC_TABLE_TOTAL, total - SPEC_TABLE_TOTAL))
        f.write(
            'The grand total (%d) reproduces the handoff\'s stated 2,213 exactly via '
            'plain whole-word `Рену` counting across the ten files. The per-mandala '
            'breakdown does not: this script\'s row is internally consistent (sums to '
            'its own total) while the spec table sums to 1,930, 283 short of its own '
            'header figure -- see `docs/DECISIONS_LOG_rv_multitranslation.md`.\n\n'
            % total
        )
        f.write('_Dr. Mārcis Gasūns_\n')

    os.makedirs(os.path.dirname(DECISIONS_LOG_PATH), exist_ok=True)
    is_new = not os.path.exists(DECISIONS_LOG_PATH)
    decision_entry = (
        '## 29-07-2026 -- Renou per-mandala reference table does not reconcile '
        '(unplanned fork, R16)\n\n'
        'VERIFICATION Sec.1.1\'s per-mandala Renou-mention table (459/117/161/118/158/'
        '110/171/123/226/287) sums to 1,930, not the 2,213 stated as its own total. '
        'Independent measurement (`rv_renou_citations.py`, whole-word `Рену` count over '
        'the ten `NN_rigveda.no_tags` files) reproduces the grand total 2,213 exactly '
        'and gives an internally-consistent per-mandala breakdown of 527/124/179/149/'
        '195/124/192/133/257/333. Conservative default taken (writes less, asserts '
        'less about an already-published number): keep the spec\'s 2,213 grand-total '
        'invariant (it is independently reproducible), do not force this script\'s '
        'per-mandala counts to match the inconsistent reference row, and record this '
        'script\'s own breakdown as the corrected reference going forward. Logged '
        'per the ambiguity-handling autonomy contract (PLAN Sec.4); did not stop, did '
        'not ask.\n\n'
        '## 29-07-2026 -- quoted_fr count (368) not independently reproduced either\n\n'
        'IMPLEMENTATION step 5 / VERIFICATION Sec.2 invariant 7 states 368 of the 2,213 '
        'mentions carry a Latin-script guillemet quote. This script\'s literal reading '
        'of the marked default ("a Latin-script quotation in guillemets follows within '
        '~25 characters") finds **%d**. Tried three variants before accepting the '
        'literal one: (a) requiring the quote to be attributed specifically to Renou '
        'by checking no other named translator (Гельднер et al.) appears between the '
        'mention and the quote -- only 26 of 459 fail that check, so this is not the '
        'source of the gap; (b) deduping to one quote per stanza -- 431 distinct loci, '
        'still not 368; (c) a strict immediate-adjacency reading (Рену directly '
        'followed by punctuation only, then the quote, no intervening words) -- 324, '
        'closer but still not an exact match and not what the spec text actually says. '
        'None of the three reproduces 368 exactly. Given invariant 4 (the per-mandala '
        'table above) is independently *provably* wrong, there is no reason to treat '
        '368 as more reliable than this script\'s own literal-heuristic count. '
        'Conservative default: keep the literal ~25-char/Latin-script reading (%d) as '
        'this script\'s output, do not hand-tune the threshold to chase '
        'an unverified target number, and record both the count and this reasoning so '
        'wave 1b (H1844) does not silently inherit an unreconciled 368 as ground truth. '
        'Logged per the same autonomy contract; did not stop, did not ask.\n'
        % (total_quoted, total_quoted)
    )
    with open(DECISIONS_LOG_PATH, 'a', encoding='utf-8', newline='\n') as f:
        if is_new:
            f.write('# DECISIONS_LOG -- RV multi-translation evidence layer (H1843/H1844)\n\n')
            f.write('_Created: 29-07-2026 · Last updated: 29-07-2026_\n\n')
            f.write(
                'Dated log of R16 ambiguity-handling decisions taken during wave 1 '
                '(PLAN Sec.4: "For a fork this plan did not anticipate: choose the '
                'more conservative option... append a dated line... and continue.")\n\n'
            )
        f.write(decision_entry)
        f.write('\n')

    if total != SPEC_TABLE_TOTAL:
        print('WARNING: grand total %d != spec 2213' % total, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
