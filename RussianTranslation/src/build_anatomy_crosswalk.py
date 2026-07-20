#!/usr/bin/env python
"""W1.1 -- PWG card-anatomy crosswalk (H1350 step 1).

Reads the three existing, independently-authored anatomy descriptions of a
PWG record and emits a measured coverage matrix: for every markup tag counted
by the machine census, which of the pedagogical spread / portrait schema also
names it, and where they diverge. Does not re-parse pwg.txt -- counts are
read from the already-measured parse-rules census (prior-art reuse, per
ARCHITECTURE_SanskritLexicography_PWG_DATA_LAYERS.md).

    python build_anatomy_crosswalk.py            print the matrix (markdown)
    python build_anatomy_crosswalk.py --check     exit 0 if every pwg.json
                                                   tag appears in the matrix
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
CSL_ATLAS_PARSE_RULES = os.path.join(HERE, '..', '..', '..', 'csl-atlas', 'data', 'parse-rules', 'pwg.json')
PORTRAIT_SCHEMA = os.path.join(HERE, '..', 'schemas', 'pwg_ru_lexicographic_portrait.schema.json')

# Portrait field a machine tag surfaces as, in microstructure.py's output
# (RussianTranslation/src/microstructure.py) -- hand-mapped once from reading
# the parser, not derived, since the schema's property names don't literally
# echo the source tag names.
TAG_TO_PORTRAIT_FIELD = {
    'k1': 'key1',
    'k2': 'key2',
    'h': 'h',
    'hom': 'labels (via <ab>-style diasystem folding)',
    'lex': 'senses[].grammar / pos',
    'div': 'senses[].n / senses[].sub (sense-tree node)',
    'ls': 'senses[].citations / citations_resolved / strata',
    'ab': 'senses[].ab_labels / diasystem',
    'lang': 'senses[].diasystem (source-language label)',
    'is': 'not surfaced as a named field -- retained inline in gloss_de/examples_sa text',
    'pc': 'not surfaced -- archival locus, used only by pwg_page_index.py',
    'info': 'not surfaced -- machine/infrastructure annotation, stripped before parse',
}

# The 24 pedagogical callouts from EntryAnatomy/pwg-entry-anatomy.html, in
# on-page order, hand-transcribed from the callout <div data-target> labels
# (no machine-readable callout spec exists for this page, unlike the Duden
# image-mode exemplar which has assets/duden_faser_plate_callouts.json).
PEDAGOGICAL_ELEMENTS = [
    ('Homograph numbers', 'h'),
    ('Headword in Devanagari', 'k1'),
    ('Etymology in parentheses', None),  # prose inside gloss, no dedicated tag
    ('Grammatical gender', 'lex'),
    ('German gloss in italics', None),  # {%...%} inline marker, not a tag
    ('Vedic samhita quotation with tonal accents', None),  # {#...#} inline marker
    ('Citation with exact locus', 'ls'),
    ("Commentators' dissent recorded", None),  # prose convention, no tag
    ('Sense numbering', 'div'),
    ('Variant reading', None),  # prose convention inside gloss/citation text
    ('Run-on citations', 'ls'),
    ('Accent distinguishes homographs', 'h'),
    ('Usage restriction', 'ab'),
    ('Indian grammatical apparatus', 'is'),
    ('Compounds follow as separate entries', 'k1'),
    ('N. pr. (nomen proprium)', 'ab'),
    ('Root marker (verbal root entries)', 'k1'),
    ('Present stem with accent', None),  # {#...#} inline marker
    ('Dhatupatha reference', 'ls'),
    ('Poetic examples quoted in full', None),  # {#...#} inline marker
    ('Voice and derived-stem labels', 'ab'),
    ('so v. a. (extended-meaning marker)', 'ab'),
    ('v. l. (varia lectio)', 'ab'),
    ('Prefixed verbs nest inside the root article', 'k1'),
]

# Inline markers the tag-based census can't count as <tag> occurrences
# (they are brace-delimited, not XML elements) but that both the pedagogical
# page and the portrait parser treat as first-class anatomy.
INLINE_MARKERS = {
    '{#...#}': 'SLP1 -> IAST Sanskrit (accented forms, examples)',
    '{%...%}': 'German-vs-Latin gloss switch',
    '〉 (U+3009)': 'sense-closing glyph, folded into the div/sense-number stream (MARK regex in microstructure.py)',
}


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def build_matrix():
    census = load_json(CSL_ATLAS_PARSE_RULES)
    tags = {}
    for row in census['field_inventory']:
        tags[row['tag']] = {'count': row['count'], 'adequacy': row['adequacy'], 'role': row['role']}
    for row in census['unmapped_tags']:
        tags.setdefault(row['tag'], {'count': row['count'], 'adequacy': 'unmapped', 'role': None})

    ped_by_tag = {}
    for label, tag in PEDAGOGICAL_ELEMENTS:
        if tag:
            ped_by_tag.setdefault(tag, []).append(label)

    lines = []
    lines.append('| Tag | Count | Adequacy | Pedagogical element(s) | Portrait field | Divergence note |')
    lines.append('|---|---|---|---|---|---|')
    for tag in sorted(tags, key=lambda t: -tags[t]['count']):
        info = tags[tag]
        ped = ', '.join(ped_by_tag.get(tag, [])) or '-- (not in the 24-element spread)'
        portrait = TAG_TO_PORTRAIT_FIELD.get(tag, '-- not surfaced by microstructure.py')
        note = ''
        if info['adequacy'] == 'lossy':
            note = f"lossy parse ({info['role']}) -- see W1.6 citation-coverage extension"
        elif info['adequacy'] == 'partial':
            note = f"partial parse ({info['role']})"
        elif info['adequacy'] == 'unmapped':
            note = 'present in source, no parse-rules mapping yet'
        elif tag not in TAG_TO_PORTRAIT_FIELD:
            note = 'measured by census + shown pedagogically, but dropped before the portrait stage'
        lines.append(f"| `<{tag}>` | {info['count']:,} | {info['adequacy']} | {ped} | {portrait} | {note} |")

    lines.append('')
    lines.append('### Inline (non-tag) markers')
    lines.append('')
    lines.append('| Marker | Role | Pedagogical element(s) |')
    lines.append('|---|---|---|')
    for marker, role in INLINE_MARKERS.items():
        peds = [label for label, tag in PEDAGOGICAL_ELEMENTS if tag is None and role.split()[0].strip('{}') in label]
        lines.append(f"| `{marker}` | {role} | see prose notes below |")

    lines.append('')
    lines.append('### Pedagogical elements with no dedicated markup tag')
    lines.append('')
    lines.append('These 24 elements are how a human reader recognises PWG structure; not all of')
    lines.append('them correspond to a distinct XML tag -- several are typographic/prose')
    lines.append('conventions realised through ordinary text next to a tagged span (e.g.')
    lines.append('"variant reading" is prose inside a `<ls>` citation, not its own tag).')
    lines.append('')
    for label, tag in PEDAGOGICAL_ELEMENTS:
        if tag is None:
            lines.append(f'- **{label}** -- realised via inline `{{#...#}}`/`{{%...%}}` markers or plain prose, not a distinct tag')

    return '\n'.join(lines), tags


def check(tags):
    ped_tags = {tag for _, tag in PEDAGOGICAL_ELEMENTS if tag}
    missing_ped = ped_tags - set(tags)
    if missing_ped:
        print(f'FAIL: pedagogical tags not in census: {missing_ped}', file=sys.stderr)
        return False
    unmapped_and_unexplained = [
        t for t, info in tags.items()
        if info['adequacy'] == 'unmapped' and t not in TAG_TO_PORTRAIT_FIELD
    ]
    # unmapped tags are allowed (documented in the "unmapped" note); this is
    # just a sanity print, not a failure -- W1.1's bar is "every tag appears",
    # not "every tag is fully explained".
    print(f'OK: {len(tags)} census tags all present in the matrix ({len(unmapped_and_unexplained)} unmapped/undocumented-in-portrait).')
    return True


def main():
    matrix, tags = build_matrix()
    if '--check' in sys.argv:
        ok = check(tags)
        sys.exit(0 if ok else 1)
    print(matrix)


if __name__ == '__main__':
    main()
