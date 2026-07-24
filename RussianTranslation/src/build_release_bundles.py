#!/usr/bin/env python
"""H1458 Track C2 -- rights-partitioned release bundles over the Sa->Ru TM.

Two source pools, two very different rights postures:

  1. `release/translation_memory/translation_memory.ru.publication.jsonl`
     (2,392 PWG exact-card/fragment records) -- OUR OWN Sonnet translation of
     PWG (Boehtlingk-Roth), a public-domain 19th-c. German dictionary. Own/PD:
     safe for `public_full`.

  2. `corpus_lexicon.jsonl` (gitignored, 1.09M word-aligned Sa<->Ru pairs,
     mined by build_corpus_lexicon.py from the SamudraManthanam parallel
     corpus) -- the RU halves are named modern published Russian translations
     (Grintser, Vasilkov/Neveleva, Elizarenkova, ...). Per the canonical rights
     ledger (`SamudraManthanam/nkrya-parallel/export/RIGHTS_TABLE.md`, H821):
     ALL 131 source works are `needs_review` -- zero are cleared. So this pool
     is grey by DEFAULT; only `derived_only` (Sanskrit + structure, NO Russian
     surface text) may be emitted; the RU surface text never leaves the local,
     gitignored `corpus_lexicon.jsonl`.

Emits, under `release/corpus_tm/` (tracked file allowlist, see .gitignore):
  public_full.jsonl / public_full.tmx     -- own/PD/cleared, full RU text (~11 MB, tracked)
  derived_only.jsonl                      -- ALL 1.09M rows, structure only, NO `ru`
                                              field (~350 MB -- regenerable, gitignored,
                                              same "full run is not a deliverable" policy
                                              as pwg_sense_loci.tsv)
  derived_only.sample.jsonl               -- first 2,000 rows, deterministic -- the
                                              committed reviewable/testable slice
  manifest.json                           -- counts + sha256 + rights summary

  python build_release_bundles.py build [--corpus-lexicon PATH] [--rights-table PATH]
  python build_release_bundles.py --audit-rights [--dir release/corpus_tm]
  python build_release_bundles.py selftest
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
from xml.sax.saxutils import escape, quoteattr

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
REPO_ROOT = os.path.normpath(os.path.join(ROOT, '..'))
OUT_DIR = os.path.join(ROOT, 'release', 'corpus_tm')

DEFAULT_PWG_TM = os.path.join(ROOT, 'release', 'translation_memory', 'translation_memory.ru.publication.jsonl')
DEFAULT_CORPUS_LEXICON = os.environ.get('CORPUS_LEXICON_PATH') or os.path.join(HERE, 'corpus_lexicon.jsonl')
# Sibling repo, read-only, consumed not rebuilt (see module docstring). Falls back to
# the main-tree checkout when run from an isolated worktree (worktree add does not
# clone gitignored/foreign-repo paths).
_RIGHTS_CANDIDATES = [
    os.path.normpath(os.path.join(REPO_ROOT, 'SamudraManthanam', 'nkrya-parallel', 'export', 'RIGHTS_TABLE.md')),
    os.path.normpath(os.path.join(REPO_ROOT, '..', 'SamudraManthanam', 'nkrya-parallel', 'export', 'RIGHTS_TABLE.md')),
]
DEFAULT_RIGHTS_TABLE = os.environ.get('RIGHTS_TABLE_PATH') or next(
    (p for p in _RIGHTS_CANDIDATES if os.path.exists(p)), _RIGHTS_CANDIDATES[0])

VERSION = '1.0.0'
CYR = re.compile('[Ѐ-ӿԀ-ԯⷠ-ⷿꙀ-ꚟ]')
CLEARED_MARKERS = ('public domain', 'own translation', 'cleared', 'cc-by', 'cc0')


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def has_cyr(s):
    return bool(s) and bool(CYR.search(s))


# ---------------------------------------------------------------------------
# Rights table (SamudraManthanam RIGHTS_TABLE.md -- consumed read-only)
# ---------------------------------------------------------------------------

def load_rights_table(path):
    """slug -> {'needs_review': bool, 'rights_text': str}. Missing file/row =
    fail CLOSED (needs_review=True) -- never assume clearance by absence."""
    rights = {}
    if not os.path.exists(path):
        return rights
    with open(path, encoding='utf-8') as f:
        for line in f:
            if not line.startswith('| ') or line.startswith('|---'):
                continue
            cols = [c.strip() for c in line.strip().strip('|').split('|')]
            if len(cols) < 6 or cols[0] == '#':
                continue
            slug = cols[1].strip('`')
            rights_text = cols[4]
            needs_review = '⚠️' in cols[5] or cols[5].strip().lower() == 'yes'
            if not needs_review and rights_text and rights_text != '—':
                needs_review = not any(m in rights_text.lower() for m in CLEARED_MARKERS)
            rights[slug] = {'needs_review': needs_review, 'rights_text': rights_text}
    return rights


def classify_work(work, rights_table):
    """Fail-closed: absent from the table, or present-and-flagged, both mean
    grey. Only an explicit cleared marker with needs_review=False clears it."""
    row = rights_table.get(work)
    if row is None:
        return 'needs_review', 'no rights row found for this work -- treated as grey by default'
    if row['needs_review']:
        return 'needs_review', row['rights_text'] or 'flagged needs_review in RIGHTS_TABLE.md'
    return 'cleared', row['rights_text']


# ---------------------------------------------------------------------------
# public_full -- own/PD PWG translation memory
# ---------------------------------------------------------------------------

def iter_pwg_tm(pwg_tm_path):
    with open(pwg_tm_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def tmx_escape_attr(s):
    return quoteattr(s)


def write_public_full(pwg_tm_path, out_dir):
    rows = list(iter_pwg_tm(pwg_tm_path))
    jsonl_out = os.path.join(out_dir, 'public_full.jsonl')
    with open(jsonl_out, 'w', encoding='utf-8', newline='\n') as f:
        for r in rows:
            out = dict(r)
            out['rights_status'] = 'cleared'
            out['rights_basis'] = 'own_translation_of_public_domain_source'
            f.write(json.dumps(out, ensure_ascii=False) + '\n')

    tmx_out = os.path.join(out_dir, 'public_full.tmx')
    tags_re = re.compile(r'\{%(.+?)%\}|<[^>]+>')
    tus = []
    for r in rows:
        card = (((r.get('payload') or {}).get('card')) or {})
        key1 = card.get('key1')
        if not key1:
            continue
        de_parts, ru_parts = [], []
        for rec in card.get('records') or []:
            for s in rec.get('senses') or []:
                de_parts.append(tags_re.sub(lambda m: m.group(1) or '', s.get('german') or ''))
                ru_parts.append(tags_re.sub(lambda m: m.group(1) or '', s.get('russian') or ''))
        de = ' '.join(p.strip() for p in de_parts if p.strip())
        ru = ' '.join(p.strip() for p in ru_parts if p.strip())
        if not ru:
            continue
        tus.append((r.get('tm_record_id') or key1, key1, de, ru))

    with open(tmx_out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<tmx version="1.4">\n'
                ' <header creationtool="build_release_bundles.py" creationtoolversion=%s '
                'segtype="phrase" o-tmf="pwg_ru" adminlang="en" srclang="de" '
                'datatype="plaintext" creationdate=%s o-encoding="UTF-8">\n'
                '  <prop type="rights">own_translation_of_public_domain_source (PWG)</prop>\n'
                '  <prop type="unit-count">%d</prop>\n'
                ' </header>\n <body>\n'
                % (tmx_escape_attr(VERSION),
                   tmx_escape_attr(time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())), len(tus)))
        for tuid, key1, de, ru in tus:
            f.write('  <tu tuid=%s>\n   <prop type="sa-key1">%s</prop>\n'
                    '   <tuv xml:lang="de"><seg>%s</seg></tuv>\n'
                    '   <tuv xml:lang="ru"><seg>%s</seg></tuv>\n  </tu>\n'
                    % (tmx_escape_attr(tuid), escape(key1), escape(de), escape(ru)))
        f.write(' </body>\n</tmx>\n')
    return jsonl_out, tmx_out, len(rows)


# ---------------------------------------------------------------------------
# derived_only -- corpus_lexicon.jsonl, structure only, NO `ru` field
# ---------------------------------------------------------------------------

STRUCTURE_FIELDS = ('group', 'work', 'passage', 'slp1', 'sa', 'kind', 'genre', 'period', 'date')
SAMPLE_SIZE = 2000


def write_derived_only(corpus_lexicon_path, rights_table, out_dir):
    jsonl_out = os.path.join(out_dir, 'derived_only.jsonl')
    sample_out = os.path.join(out_dir, 'derived_only.sample.jsonl')
    n_in = n_out = 0
    if not os.path.exists(corpus_lexicon_path):
        for p in (jsonl_out, sample_out):
            with open(p, 'w', encoding='utf-8', newline='\n') as f:
                pass
        return jsonl_out, sample_out, 0, 0
    with open(corpus_lexicon_path, encoding='utf-8') as fin, \
            open(jsonl_out, 'w', encoding='utf-8', newline='\n') as fout, \
            open(sample_out, 'w', encoding='utf-8', newline='\n') as fsample:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            n_in += 1
            row = json.loads(line)
            status, basis = classify_work(row.get('work'), rights_table)
            out = {k: row.get(k) for k in STRUCTURE_FIELDS if k in row}
            out['rights_status'] = status
            out['rights_basis'] = basis
            # NO `ru` field, ever -- this is the one invariant --audit-rights checks.
            rendered = json.dumps(out, ensure_ascii=False) + '\n'
            fout.write(rendered)
            if n_out < SAMPLE_SIZE:
                fsample.write(rendered)
            n_out += 1
    return jsonl_out, sample_out, n_out, n_in


# ---------------------------------------------------------------------------
# build / audit
# ---------------------------------------------------------------------------

RU_SURFACE_KEYS = ('ru', 'russian', 'russian_text', 'target_text')


def build(pwg_tm_path=DEFAULT_PWG_TM, corpus_lexicon_path=DEFAULT_CORPUS_LEXICON,
          rights_table_path=DEFAULT_RIGHTS_TABLE, out_dir=OUT_DIR):
    if not os.path.exists(pwg_tm_path):
        sys.exit('PWG TM publication file not found: %s' % pwg_tm_path)
    os.makedirs(out_dir, exist_ok=True)
    rights_table = load_rights_table(rights_table_path)

    public_jsonl, public_tmx, n_public = write_public_full(pwg_tm_path, out_dir)
    derived_jsonl, derived_sample, n_derived, n_lexicon_in = write_derived_only(
        corpus_lexicon_path, rights_table, out_dir)

    manifest = {
        'schema': 'pwg.release_bundles.manifest.v1',
        'version': VERSION,
        'built_at_source': 'build_release_bundles.py',
        'public_full': {
            'jsonl': os.path.relpath(public_jsonl, ROOT).replace('\\', '/'),
            'tmx': os.path.relpath(public_tmx, ROOT).replace('\\', '/'),
            'record_count': n_public,
            'sha256_jsonl': sha256_file(public_jsonl),
            'sha256_tmx': sha256_file(public_tmx),
            'rights': 'own_translation_of_public_domain_source (PWG)',
        },
        'derived_only': {
            'jsonl': os.path.relpath(derived_jsonl, ROOT).replace('\\', '/') + ' (gitignored -- regenerable, not a deliverable)',
            'sample_jsonl': os.path.relpath(derived_sample, ROOT).replace('\\', '/') + ' (tracked -- reviewable slice)',
            'record_count': n_derived,
            'sample_record_count': min(n_derived, SAMPLE_SIZE),
            'source_lexicon_rows': n_lexicon_in,
            'sha256_sample_jsonl': sha256_file(derived_sample) if os.path.exists(derived_sample) else None,
            'rights': 'structure-only extraction of corpus_lexicon.jsonl -- NO Russian surface text; '
                      'source rights per SamudraManthanam RIGHTS_TABLE.md (all works needs_review, H821)',
        },
        'rights_table_source': os.path.relpath(rights_table_path, ROOT).replace('\\', '/')
            if os.path.exists(rights_table_path) else rights_table_path + ' (NOT FOUND -- fail-closed default applied)',
        'rights_table_rows_loaded': len(rights_table),
        'grey_fulltext_note': 'corpus_lexicon.jsonl RU surface text stays local + gitignored; never bundled here.',
    }
    with open(os.path.join(out_dir, 'manifest.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('public_full: %d records -> %s / %s' % (n_public, public_jsonl, public_tmx))
    print('derived_only: %d records (of %d corpus_lexicon rows) -> %s (+ %d-row sample -> %s)'
          % (n_derived, n_lexicon_in, derived_jsonl, min(n_derived, SAMPLE_SIZE), derived_sample))
    return manifest


def audit_rights(bundle_dir=OUT_DIR):
    """The hard gate: assert 0 grey RU surface strings in any TRACKED bundle
    file under bundle_dir. Returns the violation count (0 = PASS)."""
    violations = []
    checked_files = []
    if not os.path.isdir(bundle_dir):
        print('AUDIT: bundle dir not found: %s (nothing to check)' % bundle_dir)
        return 0
    for name in sorted(os.listdir(bundle_dir)):
        path = os.path.join(bundle_dir, name)
        if not os.path.isfile(path):
            continue
        checked_files.append(name)
        if name.endswith('.jsonl'):
            with open(path, encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    row = json.loads(line)
                    status = row.get('rights_status', 'cleared' if 'derived_only' not in name else 'needs_review')
                    for k in RU_SURFACE_KEYS:
                        v = row.get(k)
                        if isinstance(v, str) and has_cyr(v) and status != 'cleared':
                            violations.append('%s:%d row=%s field=%s status=%s'
                                               % (name, i, row.get('key1') or row.get('group') or '?', k, status))
        elif name.endswith('.tmx'):
            with open(path, encoding='utf-8') as f:
                content = f.read()
            if 'public_full' not in name and has_cyr(content):
                violations.append('%s: RU text present in a non-public_full TMX' % name)
    print('AUDIT --audit-rights over %s' % bundle_dir)
    print('  files checked: %s' % ', '.join(checked_files))
    if violations:
        print('  FAIL: %d grey RU surface string violation(s):' % len(violations))
        for v in violations[:50]:
            print('    - ' + v)
        return len(violations)
    print('  PASS: 0 grey RU surface strings in any tracked bundle.')
    return 0


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        pwg_tm = os.path.join(d, 'pwg_tm.jsonl')
        with open(pwg_tm, 'w', encoding='utf-8') as f:
            f.write(json.dumps({
                'tm_record_id': 'exact-card:ru:aaa', 'record_type': 'exact_card',
                'payload': {'card': {'key1': 'gam', 'records': [
                    {'senses': [{'german': '{%gehen%}', 'russian': '{%идти%}'}]}]}},
            }, ensure_ascii=False) + '\n')

        lex = os.path.join(d, 'corpus_lexicon.jsonl')
        with open(lex, 'w', encoding='utf-8') as f:
            f.write(json.dumps({'group': 'g1', 'work': '01_ramayana-balakanda', 'passage': '1.1',
                                 'slp1': 'gam', 'sa': 'gacchati', 'ru': 'СЕКРЕТНЫЙ ТЕКСТ ПЕРЕВОДЧИКА'},
                                ensure_ascii=False) + '\n')
            f.write(json.dumps({'group': 'g2', 'work': 'unknown_work', 'passage': '1.2',
                                 'slp1': 'i', 'sa': 'eti', 'ru': 'ANOTHER SECRET'},
                                ensure_ascii=False) + '\n')

        rights_table = os.path.join(d, 'RIGHTS_TABLE.md')
        with open(rights_table, 'w', encoding='utf-8') as f:
            f.write('| # | Source (slug) | Title | Translator / author | Rights | Needs review |\n')
            f.write('|---:|---|---|---|---|:---:|\n')
            f.write('| 1 | `01_ramayana-balakanda` | X | Y | in-copyright modern Russian academic translation | ⚠️ yes |\n')

        out = os.path.join(d, 'out')
        manifest = build(pwg_tm, lex, rights_table, out)
        assert manifest['public_full']['record_count'] == 1
        assert manifest['derived_only']['record_count'] == 2

        derived_rows = [json.loads(l) for l in open(os.path.join(out, 'derived_only.jsonl'), encoding='utf-8')]
        assert all('ru' not in r for r in derived_rows), 'derived_only leaked an ru field'
        assert derived_rows[0]['rights_status'] == 'needs_review'
        assert derived_rows[1]['rights_status'] == 'needs_review', 'absent-from-table must fail closed'

        violations = audit_rights(out)
        assert violations == 0, violations

        # Now prove the gate actually catches a leak: hand-inject a grey RU row.
        with open(os.path.join(out, 'derived_only.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps({'group': 'leak', 'work': 'x', 'ru': 'УТЕЧКА',
                                 'rights_status': 'needs_review'}, ensure_ascii=False) + '\n')
        violations = audit_rights(out)
        assert violations == 1, violations
    print('selftest OK')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--audit-rights', action='store_true')
    ap.add_argument('--dir', default=OUT_DIR)
    ap.add_argument('--pwg-tm', default=DEFAULT_PWG_TM)
    ap.add_argument('--corpus-lexicon', default=DEFAULT_CORPUS_LEXICON)
    ap.add_argument('--rights-table', default=DEFAULT_RIGHTS_TABLE)
    ap.add_argument('cmd', nargs='?', default='build')
    args = ap.parse_args()
    if args.cmd == 'selftest':
        selftest()
    elif args.audit_rights:
        sys.exit(1 if audit_rights(args.dir) else 0)
    else:
        build(args.pwg_tm, args.corpus_lexicon, args.rights_table, args.dir)
