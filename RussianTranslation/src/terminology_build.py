#!/usr/bin/env python
"""H1458 Track C1 -- curate the Sa->Ru terminology dataset (D13) from the
publication-grade PWG translation memory (release/translation_memory/).

Every source row is our own Sonnet translation of PWG (Boehtlingk-Roth), a
public-domain 19th-century German dictionary -- own/PD, no third-party rights
question. This sidesteps the D9 "MW-English must only reach RU via a curated
step" concern entirely by not touching MW English at all: the term gloss is
extracted directly from the already-published RU translation's {%...%} core
gloss span(s) (PWG's own semantic-gloss delimiter -- see ABBREVIATIONS_RU.md /
mw_ru markup conventions), one term per headword (its first/primary sense
only, to keep the curated layer concise rather than reproducing full entries).

  python terminology_build.py build   [--tm PATH] [--out-dir DIR]
  python terminology_build.py selftest

Term-level oral/corpus feeds (Track B units) are NOT included yet -- Track B
(H290) has not landed any graded oral units this pass (SamudraManthanam sample
still pending); rerun this build once B4 lands to fold those in (see the
DATASHEET's Known Limitations section, which this script keeps in sync).
"""
import hashlib
import json
import os
import re
import sys
import argparse

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
DEFAULT_TM = os.path.join(ROOT, 'release', 'translation_memory', 'translation_memory.ru.publication.jsonl')
OUT_DIR = os.path.join(ROOT, 'release', 'sa_ru_terminology')
JSONL_OUT = os.path.join(OUT_DIR, 'sa_ru_terminology.ru.jsonl')
MANIFEST_OUT = os.path.join(OUT_DIR, 'manifest.ru.json')
DATASHEET_OUT = os.path.join(OUT_DIR, 'DATASHEET.ru.md')

VERSION = '1.0.0'
GLOSS_RE = re.compile(r'\{%(.+?)%\}')
TAG_RE = re.compile(r'<[^>]+>')


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def clean_gloss(russian_html):
    """Extract the PWG core-gloss span(s) {%...%} from one sense's `russian`
    field; strip any residual markup. Falls back to a markup-stripped snippet
    if a sense carries no {%...%} span (citation-only senses)."""
    spans = GLOSS_RE.findall(russian_html or '')
    if spans:
        return '; '.join(s.strip() for s in spans if s.strip())
    stripped = TAG_RE.sub(' ', russian_html or '')
    stripped = re.sub(r'\s+', ' ', stripped).strip()
    return stripped[:120]


def primary_sense(senses):
    """The first sense (PWG's own printed order -- 'tag' is a string like
    "1"/"cau. 1", not an int, so list order is citation order, not a sort)
    that carries a real {%...%} gloss span. Citation-only senses (pure <ls>
    references, no gloss) are skipped rather than accepted via the
    markup-stripped fallback, which only fires if NO sense has a span."""
    for s in senses:
        spans = GLOSS_RE.findall(s.get('russian') or '')
        if spans:
            return '; '.join(x.strip() for x in spans if x.strip())
    for s in senses:
        fallback = clean_gloss(s.get('russian'))
        if fallback:
            return fallback
    return ''


def iter_terms(tm_path):
    seen = set()
    with open(tm_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get('record_type') != 'exact_card':
                continue
            card = (((row.get('payload') or {}).get('card')) or {})
            key1 = card.get('key1') or ''
            iast = card.get('iast') or ''
            if not key1 or key1 in seen:
                continue
            records = card.get('records') or []
            gloss = ''
            for rec in records:
                gloss = primary_sense(rec.get('senses') or [])
                if gloss:
                    break
            if not gloss:
                continue
            seen.add(key1)
            yield {
                'schema': 'pwg.sa_ru_terminology.term.v1',
                'term_id': 'term:ru:' + key1,
                'iast': iast,
                'key1': key1,
                'ru_gloss': gloss,
                'lang': 'ru',
                'source_tm_record_id': row.get('tm_record_id'),
                'source_kind': 'pwg_tm_primary_sense',
                'rights': 'own_translation_of_pd_source',
                'modality': 'written',
            }


def build(tm_path=DEFAULT_TM, out_dir=OUT_DIR):
    if not os.path.exists(tm_path):
        sys.exit('TM publication file not found: %s (run build_tmx.py / the pwg_ru '
                  'promotion pipeline first)' % tm_path)
    os.makedirs(out_dir, exist_ok=True)
    jsonl_out = os.path.join(out_dir, 'sa_ru_terminology.ru.jsonl')
    terms = sorted(iter_terms(tm_path), key=lambda t: t['key1'])
    with open(jsonl_out, 'w', encoding='utf-8', newline='\n') as f:
        for t in terms:
            f.write(json.dumps(t, ensure_ascii=False) + '\n')
    artifact_sha256 = sha256_file(jsonl_out)
    manifest = {
        'schema': 'pwg.sa_ru_terminology.manifest.v1',
        'lang': 'ru',
        'version': VERSION,
        'artifact': 'sa_ru_terminology.ru.jsonl',
        'artifact_sha256': artifact_sha256,
        'term_count': len(terms),
        'source_tm': os.path.relpath(tm_path, ROOT).replace('\\', '/'),
        'source_tm_sha256': sha256_file(tm_path),
        'doi_status': 'reserved',
        'rights': 'own_translation_of_public_domain_source (PWG, Boehtlingk-Roth, 19th c.)',
        'known_limitations': [
            'written/PWG-derived terms only -- Track B (oral) term feeds not yet folded in',
            'one term per headword (primary sense only) -- not exhaustive per-sense coverage',
        ],
    }
    with open(os.path.join(out_dir, 'manifest.ru.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write('\n')
    write_datasheet(os.path.join(out_dir, 'DATASHEET.ru.md'), manifest)
    print('terms: %d -> %s' % (len(terms), jsonl_out))
    return manifest


def write_datasheet(path, manifest):
    content = (
        '# Curated Sanskrit-to-Russian Terminology Datasheet (ru)\n\n'
        '_Regenerated by `terminology_build.py`; version %s._\n\n'
        'Separate DOI-bound dataset track for curated Sanskrit-to-Russian terminology, '
        'curated from the publication-grade PWG translation memory\'s own RU translations '
        '(D13 of `TRANSLATION_MEMORY_DECISIONS.md`).\n\n'
        '- Terms: %d\n'
        '- DOI status: %s\n'
        '- Rights: %s\n'
        '- Source TM: `%s` (sha256 `%s`)\n'
        '- Artifact sha256: `%s`\n\n'
        '## Known limitations\n\n%s\n'
        % (manifest['version'], manifest['term_count'], manifest['doi_status'],
           manifest['rights'], manifest['source_tm'], manifest['source_tm_sha256'],
           manifest['artifact_sha256'],
           '\n'.join('- ' + s for s in manifest['known_limitations']))
    )
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)


def selftest():
    import tempfile
    fixture_tm = [
        {
            'schema': 'pwg.translation_memory.publication.v1',
            'tm_record_id': 'exact-card:ru:deadbeef',
            'record_type': 'exact_card',
            'payload': {'card': {'key1': 'gam', 'iast': 'gam', 'records': [
                {'senses': [{'tag': '1', 'russian': '{%идти%}, {%двигаться%}'}]}]}},
        },
        {
            'schema': 'pwg.translation_memory.publication.v1',
            'tm_record_id': 'exact-card:ru:cafef00d',
            'record_type': 'exact_card',
            'payload': {'card': {'key1': 'gam', 'iast': 'gam', 'records': [
                {'senses': [{'tag': '2', 'russian': 'dup, should be skipped'}]}]}},
        },
        {
            'schema': 'pwg.translation_memory.publication.v1',
            'tm_record_id': 'exact-card:ru:00000000',
            'record_type': 'exact_card',
            'payload': {'card': {'key1': 'nivas', 'iast': 'ni-vas', 'records': [
                {'senses': [{'tag': '1', 'russian': '<ls>M. 3,102.</ls> citation only, no gloss span'},
                            {'tag': '2', 'russian': '{%жить, обитать%}'}]}]}},
        },
    ]
    with tempfile.TemporaryDirectory() as d:
        tm_path = os.path.join(d, 'tm.jsonl')
        with open(tm_path, 'w', encoding='utf-8') as f:
            for r in fixture_tm:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        manifest = build(tm_path, os.path.join(d, 'out'))
        assert manifest['term_count'] == 2, manifest['term_count']
        terms = [json.loads(l) for l in open(os.path.join(d, 'out', 'sa_ru_terminology.ru.jsonl'), encoding='utf-8')]
        by_key = {t['key1']: t for t in terms}
        assert by_key['gam']['ru_gloss'] == 'идти; двигаться', by_key['gam']['ru_gloss']
        assert by_key['nivas']['ru_gloss'] == 'жить, обитать', by_key['nivas']['ru_gloss']
        assert manifest['doi_status'] == 'reserved'
    print('selftest OK')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build')
    b.add_argument('--tm', default=DEFAULT_TM)
    b.add_argument('--out-dir', default=OUT_DIR)
    sub.add_parser('selftest')
    args = ap.parse_args()
    if args.cmd == 'selftest':
        selftest()
    else:
        build(args.tm, args.out_dir)
