#!/usr/bin/env python
"""rv_spine_build.py -- the deterministic RV multi-translation evidence spine (H1843 C2).

Three parts, one script (IMPLEMENTATION steps 2-4):

  1. rv_stanza_translations.jsonl -- one record per stanza (10,552), all four
     translators' status/text, keyed by `location`.
  2. rv_lemma_occurrences.jsonl -- one record per lemma, grouping the 164,758
     RV tokens (VedaWeb lemmatization.json `transformContext`), carrying the
     union of id_gra/id_pwg/id_mw already present on the tokens.
  3. rv_translation_spine.tsv (or a 500-row sample if the full TSV exceeds
     200 MB) + schemas/rv_translation_spine.schema.json -- the flat,
     denormalised mirror of 1+2, one row per lemma x location x translator.

No fuzzy joins anywhere: the join key is `location`, exact, per ARCHITECTURE Sec.1.
Reads only the read-only VisualDCS vedaweb feed and this repo's own
pwg_ru/griffith_en_1896.json (H1843 step 1 output); writes only into pwg_ru/ and
schemas/.

  python rv_spine_build.py              build all three parts
  python rv_spine_build.py --validate   validate the two JSONL outputs against the schema
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
from sibling_root import sibling_root  # noqa: E402
GITHUB_ROOT, _ = sibling_root()  # GitHub/ (H1902: worktree-safe root resolution)
VEDAWEB_DIR = os.path.join(GITHUB_ROOT, 'VisualDCS', 'non-derived', 'vedaweb')
PWG_RU_DIR = os.path.normpath(os.path.join(HERE, '..', 'pwg_ru'))
SCHEMAS_DIR = os.path.normpath(os.path.join(HERE, '..', 'schemas'))
RUN_LOG_DIR = os.path.join(PWG_RU_DIR, 'h1843')

LEMMATIZATION_PATH = os.path.join(VEDAWEB_DIR, 'lemmatization.json')

# translator key -> path. griffith is this handoff's own step-1 output, the
# other three are the read-only VedaWeb feed (ARCHITECTURE Sec.3.1 keys).
TRANSLATOR_PATHS = {
    'grassmann_de_1876': os.path.join(VEDAWEB_DIR, 'grassmann_de_1876_1877.json'),
    'geldner_de_1951': os.path.join(VEDAWEB_DIR, 'geldner_de_1951_1957.json'),
    'elizarenkova_ru_1989': os.path.join(VEDAWEB_DIR, 'elizarenkova_ru_1989_1999.json'),
    'griffith_en_1896': os.path.join(PWG_RU_DIR, 'griffith_en_1896.json'),
}
TRANSLATOR_ORDER = [
    'grassmann_de_1876', 'geldner_de_1951', 'elizarenkova_ru_1989', 'griffith_en_1896',
]

STANZA_OUT = os.path.join(PWG_RU_DIR, 'rv_stanza_translations.jsonl')
LEMMA_OUT = os.path.join(PWG_RU_DIR, 'rv_lemma_occurrences.jsonl')
TSV_OUT = os.path.join(PWG_RU_DIR, 'rv_translation_spine.tsv')
TSV_SAMPLE_OUT = os.path.join(PWG_RU_DIR, 'rv_translation_spine.sample.tsv')
SCHEMA_OUT = os.path.join(SCHEMAS_DIR, 'rv_translation_spine.schema.json')

# IMPLEMENTATION step 4 names 200 MB as the gitignore threshold, but GitHub's
# actual hard per-file limit is 100 MB (a push of the un-gitignored 173.6 MB
# TSV was rejected, GH001). Using 90 MB as the effective threshold -- see
# docs/DECISIONS_LOG_rv_multitranslation.md.
TSV_SIZE_LIMIT_BYTES = 90 * 1024 * 1024
TSV_SAMPLE_ROWS = 500

# Hard invariants (ARCHITECTURE Sec.1 / VERIFICATION Sec.2), measured 29-07-2026.
EXPECTED_STANZA_COUNT = 10552
EXPECTED_TOKEN_COUNT = 164758
EXPECTED_ABSENT = {
    'grassmann_de_1876': 0,
    'geldner_de_1951': 4,
    'elizarenkova_ru_1989': 0,
    'griffith_en_1896': 0,
}
EXPECTED_GELDNER_ABSENT_LOCATIONS = {'10.106.5', '10.106.6', '10.106.7', '10.106.8'}


def load_lemmatization():
    with open(LEMMATIZATION_PATH, encoding='utf-8') as f:
        return json.load(f)


def load_translator_texts(path):
    """location -> text (raw, un-stripped) for one translator file."""
    with open(path, encoding='utf-8') as f:
        d = json.load(f)
    texts = {}
    for rec in d['contents']:
        texts[rec['location']] = rec.get('text')
    return texts


def classify(text):
    if text is None or not text.strip():
        return 'empty' if text is not None else 'absent_from_source'
    return 'present'


# ---------------------------------------------------------------------------
# Step 2 -- stanza table
# ---------------------------------------------------------------------------

def build_stanza_records(canonical_locations, translator_texts):
    """translator_texts: {translator_key: {location: text}}."""
    records = []
    absent_counts = {k: 0 for k in TRANSLATOR_ORDER}
    absent_locations = {k: [] for k in TRANSLATOR_ORDER}
    empty_counts = {k: 0 for k in TRANSLATOR_ORDER}

    for loc in canonical_locations:
        mandala, hymn, stanza = (int(x) for x in loc.split('.'))
        translations = {}
        for key in TRANSLATOR_ORDER:
            texts = translator_texts[key]
            if loc not in texts:
                status = 'absent_from_source'
                text = None
            else:
                raw = texts[loc]
                if raw is None or not raw.strip():
                    status = 'empty'
                    text = raw if raw is not None else ''
                else:
                    status = 'present'
                    text = raw
            translations[key] = {'status': status, 'text': text}
            if status == 'absent_from_source':
                absent_counts[key] += 1
                absent_locations[key].append(loc)
            elif status == 'empty':
                empty_counts[key] += 1
        records.append({
            'location': loc, 'mandala': mandala, 'hymn': hymn, 'stanza': stanza,
            'translations': translations, 'divergence': None,
        })

    stats = {
        'absent_counts': absent_counts,
        'absent_locations': absent_locations,
        'empty_counts': empty_counts,
    }
    return records, stats


def verify_stanza_invariants(stats):
    problems = []
    for key, expected in EXPECTED_ABSENT.items():
        actual = stats['absent_counts'][key]
        if actual != expected:
            problems.append(
                '%s: expected %d absent_from_source, got %d' % (key, expected, actual))
    geldner_locs = set(stats['absent_locations']['geldner_de_1951'])
    if geldner_locs != EXPECTED_GELDNER_ABSENT_LOCATIONS:
        problems.append('geldner absent locations mismatch: got %s, expected %s'
                         % (sorted(geldner_locs), sorted(EXPECTED_GELDNER_ABSENT_LOCATIONS)))
    for key, count in stats['empty_counts'].items():
        if count != 0:
            problems.append('%s: expected 0 empty rows, got %d' % (key, count))
    if problems:
        raise AssertionError(
            'Hard invariant violation (VERIFICATION Sec.2) -- parse bug, not a finding:\n  '
            + '\n  '.join(problems))


# ---------------------------------------------------------------------------
# Step 3 -- lemma occurrences
# ---------------------------------------------------------------------------

def _sort_ids(id_set):
    def key(x):
        try:
            return (0, float(x))
        except ValueError:
            return (1, x)
    return sorted(id_set, key=key)


def build_lemma_records(lemmatization_doc):
    groups = {}  # key -> mutable accumulator
    order = []   # preserve first-seen order for reproducibility
    total_tokens = 0

    for rec in lemmatization_doc['contents']:
        loc = rec['location']
        tokens = json.loads(rec['transformContext'])
        for idx, tok in enumerate(tokens):
            total_tokens += 1
            lemma = tok.get('lemma') or ''
            lemma_missing = not lemma
            key = tok['form'] if lemma_missing else lemma
            if key not in groups:
                groups[key] = {
                    'lemma': key,
                    'lemma_ewaia': tok.get('lemma_ewaia', '') or '',
                    'lemma_missing': lemma_missing,
                    'id_gra': set(), 'id_pwg': set(), 'id_mw': set(),
                    'occurrences': [],
                }
                order.append(key)
            group = groups[key]
            group['id_gra'].update(tok.get('id_gra') or [])
            group['id_pwg'].update(tok.get('id_pwg') or [])
            group['id_mw'].update(tok.get('id_mw') or [])
            group['occurrences'].append({
                'location': loc, 'form': tok['form'], 'token_index': idx, 'wordlevel': None,
            })

    records = []
    for key in order:
        group = groups[key]
        rec = {
            'lemma': group['lemma'],
            'lemma_ewaia': group['lemma_ewaia'],
            'id_gra': _sort_ids(group['id_gra']),
            'id_pwg': _sort_ids(group['id_pwg']),
            'id_mw': _sort_ids(group['id_mw']),
            'occurrence_count': len(group['occurrences']),
            'occurrences': group['occurrences'],
        }
        if group['lemma_missing']:
            rec['lemma_missing'] = True
        records.append(rec)
    return records, total_tokens


def verify_lemma_invariants(total_tokens):
    if total_tokens != EXPECTED_TOKEN_COUNT:
        raise AssertionError(
            'Hard invariant violation (VERIFICATION Sec.2): expected %d RV tokens, got %d'
            % (EXPECTED_TOKEN_COUNT, total_tokens))


# ---------------------------------------------------------------------------
# Step 4 -- flat mirror TSV + schema
# ---------------------------------------------------------------------------

TSV_COLUMNS = [
    'lemma', 'id_gra', 'id_pwg', 'location', 'form', 'translator', 'status',
    'text', 'divergence_class', 'wordlevel_span', 'wordlevel_confidence',
]


def _tsv_escape(value):
    if value is None:
        return ''
    return str(value).replace('\t', ' ').replace('\n', '\\n').replace('\r', '')


def iter_tsv_rows(lemma_records, stanza_by_location):
    for lrec in lemma_records:
        id_gra = ','.join(lrec['id_gra'])
        id_pwg = ','.join(lrec['id_pwg'])
        for occ in lrec['occurrences']:
            stanza = stanza_by_location[occ['location']]
            for translator in TRANSLATOR_ORDER:
                t = stanza['translations'][translator]
                yield [
                    lrec['lemma'], id_gra, id_pwg, occ['location'], occ['form'],
                    translator, t['status'], t['text'], '', '', '',
                ]


def write_tsv(lemma_records, stanza_by_location):
    """Writes the full TSV unless it would exceed TSV_SIZE_LIMIT_BYTES, in which
    case (marked default, IMPLEMENTATION step 4) it writes only a 500-row
    sample and gitignores the full generated file."""
    header = '\t'.join(TSV_COLUMNS) + '\n'
    row_count = 0
    byte_count = len(header.encode('utf-8'))
    sample_rows = []

    tmp_path = TSV_OUT + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(header)
        for row in iter_tsv_rows(lemma_records, stanza_by_location):
            line = '\t'.join(_tsv_escape(v) for v in row) + '\n'
            f.write(line)
            byte_count += len(line.encode('utf-8'))
            row_count += 1
            if len(sample_rows) < TSV_SAMPLE_ROWS:
                sample_rows.append(line)

    oversized = byte_count > TSV_SIZE_LIMIT_BYTES
    if oversized:
        os.replace(tmp_path, TSV_OUT)  # kept, but gitignored (see below)
        with open(TSV_SAMPLE_OUT, 'w', encoding='utf-8', newline='\n') as f:
            f.write(header)
            f.writelines(sample_rows)
        gitignore_path = os.path.join(PWG_RU_DIR, '.gitignore')
        entry = 'rv_translation_spine.tsv\n'
        existing = ''
        if os.path.exists(gitignore_path):
            with open(gitignore_path, encoding='utf-8') as f:
                existing = f.read()
        if entry not in existing:
            with open(gitignore_path, 'a', encoding='utf-8', newline='\n') as f:
                if existing and not existing.endswith('\n'):
                    f.write('\n')
                f.write(entry)
    else:
        os.replace(tmp_path, TSV_OUT)
        if os.path.exists(TSV_SAMPLE_OUT):
            os.remove(TSV_SAMPLE_OUT)

    return row_count, byte_count, oversized


SCHEMA_DOC = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "pwg.rv_translation_spine.v1",
    "title": "RV multi-translation evidence spine",
    "description": (
        "Schema for pwg_ru/rv_stanza_translations.jsonl and "
        "pwg_ru/rv_lemma_occurrences.jsonl (H1843 wave 1a). Each line of either "
        "file is one JSON object matching stanza_record or lemma_record below."
    ),
    "type": "object",
    "oneOf": [
        {"$ref": "#/$defs/stanza_record"},
        {"$ref": "#/$defs/lemma_record"},
    ],
    "$defs": {
        "status": {
            "enum": ["present", "absent_from_source", "empty"],
        },
        "translator": {
            "enum": [
                "grassmann_de_1876", "geldner_de_1951",
                "elizarenkova_ru_1989", "griffith_en_1896",
            ],
        },
        "divergence_class": {
            "enum": [
                "agreement", "lexical_variant", "semantic_shift",
                "omitted_by_one", "added_by_one",
            ],
        },
        "translation_status": {
            "type": "object",
            "additionalProperties": False,
            "required": ["status", "text"],
            "properties": {
                "status": {"$ref": "#/$defs/status"},
                "text": {"type": ["string", "null"]},
            },
        },
        "stanza_record": {
            "type": "object",
            "additionalProperties": False,
            "required": ["location", "mandala", "hymn", "stanza", "translations", "divergence"],
            "properties": {
                "location": {"type": "string"},
                "mandala": {"type": "integer", "minimum": 1},
                "hymn": {"type": "integer", "minimum": 1},
                "stanza": {"type": "integer", "minimum": 1},
                "translations": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "grassmann_de_1876": {"$ref": "#/$defs/translation_status"},
                        "geldner_de_1951": {"$ref": "#/$defs/translation_status"},
                        "elizarenkova_ru_1989": {"$ref": "#/$defs/translation_status"},
                        "griffith_en_1896": {"$ref": "#/$defs/translation_status"},
                    },
                },
                "divergence": {
                    "oneOf": [{"type": "null"}, {"type": "object"}],
                },
            },
        },
        "occurrence": {
            "type": "object",
            "additionalProperties": False,
            "required": ["location", "form", "token_index", "wordlevel"],
            "properties": {
                "location": {"type": "string"},
                "form": {"type": "string"},
                "token_index": {"type": "integer", "minimum": 0},
                "wordlevel": {"oneOf": [{"type": "null"}, {"type": "object"}]},
            },
        },
        "lemma_record": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "lemma", "lemma_ewaia", "id_gra", "id_pwg", "id_mw",
                "occurrence_count", "occurrences",
            ],
            "properties": {
                "lemma": {"type": "string"},
                "lemma_ewaia": {"type": "string"},
                "lemma_missing": {"type": "boolean"},
                "id_gra": {"type": "array", "items": {"type": "string"}},
                "id_pwg": {"type": "array", "items": {"type": "string"}},
                "id_mw": {"type": "array", "items": {"type": "string"}},
                "occurrence_count": {"type": "integer", "minimum": 0},
                "occurrences": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/occurrence"},
                },
            },
        },
    },
}


def write_schema():
    os.makedirs(SCHEMAS_DIR, exist_ok=True)
    with open(SCHEMA_OUT, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(SCHEMA_DOC, f, ensure_ascii=False, indent=2)
        f.write('\n')


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_jsonl(path, schema):
    import jsonschema
    validator = jsonschema.Draft202012Validator(schema)
    n = 0
    errors = []
    with open(path, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            errs = list(validator.iter_errors(rec))
            if errs:
                errors.append((i, [str(e.message) for e in errs[:3]]))
            n += 1
    return n, errors


def run_validate():
    with open(SCHEMA_OUT, encoding='utf-8') as f:
        schema = json.load(f)
    ok = True
    for path in (STANZA_OUT, LEMMA_OUT):
        n, errors = validate_jsonl(path, schema)
        print('%s: %d records, %d schema violations' % (path, n, len(errors)))
        for lineno, msgs in errors[:10]:
            print('  line %d: %s' % (lineno, '; '.join(msgs)))
            ok = False
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def write_jsonl(path, records):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False))
            f.write('\n')


def run_build():
    doc = load_lemmatization()
    canonical_locations = [rec['location'] for rec in doc['contents']]
    canonical_set = set(canonical_locations)
    assert len(canonical_locations) == EXPECTED_STANZA_COUNT, (
        'expected %d canonical stanzas, got %d'
        % (EXPECTED_STANZA_COUNT, len(canonical_locations)))

    translator_texts = {}
    extras_log = {}
    for key in TRANSLATOR_ORDER:
        texts = load_translator_texts(TRANSLATOR_PATHS[key])
        extras = sorted(set(texts) - canonical_set)
        if extras:
            extras_log[key] = extras  # marked default: log and ignore
        translator_texts[key] = texts

    stanza_records, stanza_stats = build_stanza_records(canonical_locations, translator_texts)
    verify_stanza_invariants(stanza_stats)
    write_jsonl(STANZA_OUT, stanza_records)
    print('wrote %s: %d stanza records' % (STANZA_OUT, len(stanza_records)))

    lemma_records, total_tokens = build_lemma_records(doc)
    verify_lemma_invariants(total_tokens)
    write_jsonl(LEMMA_OUT, lemma_records)
    print('wrote %s: %d lemma records, %d tokens' % (LEMMA_OUT, len(lemma_records), total_tokens))

    stanza_by_location = {r['location']: r for r in stanza_records}
    row_count, byte_count, oversized = write_tsv(lemma_records, stanza_by_location)
    print('wrote TSV: %d rows, %.1f MB, oversized=%s'
          % (row_count, byte_count / (1024.0 * 1024.0), oversized))

    write_schema()
    print('wrote %s' % SCHEMA_OUT)

    os.makedirs(RUN_LOG_DIR, exist_ok=True)
    log_path = os.path.join(RUN_LOG_DIR, 'spine_build_run_log.md')
    with open(log_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# rv_spine_build.py run log (H1843 steps 2-4)\n\n')
        f.write('_Created: 29-07-2026 · Last updated: 29-07-2026_\n\n')
        f.write('- canonical stanzas: %d\n' % len(canonical_locations))
        f.write('- total RV tokens: %d\n' % total_tokens)
        f.write('- distinct lemma/form-keyed groups: %d\n' % len(lemma_records))
        f.write('- absent_from_source counts: %s\n' % stanza_stats['absent_counts'])
        f.write('- TSV rows: %d (%.1f MB, oversized=%s)\n\n' % (
            row_count, byte_count / (1024.0 * 1024.0), oversized))
        if extras_log:
            f.write('## Translator locations outside the canonical set (logged, ignored)\n\n')
            for key, extras in extras_log.items():
                f.write('- %s: %d extra locations\n' % (key, len(extras)))
            f.write('\n')
        f.write('_Dr. Mārcis Gasūns_\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--validate', action='store_true')
    args = parser.parse_args()
    if args.validate:
        return run_validate()
    run_build()
    return 0


if __name__ == '__main__':
    sys.exit(main())
