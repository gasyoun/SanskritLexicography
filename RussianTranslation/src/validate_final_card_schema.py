#!/usr/bin/env python
"""Validate canonical pwg_ru final translated cards.

This is a lightweight standard-library gate for the v1 final-card contract in
schemas/pwg_ru_final_card.schema.json. It validates workflow results shaped as
{key, card, judge}, including Apresjan near-synonym discrimination evidence.

  python validate_final_card_schema.py [workflow-output.json ...]
  python validate_final_card_schema.py --selftest
"""
import copy, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from safe_filename import safe_name

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
SCHEMA = os.path.join(ROOT, 'schemas', 'pwg_ru_final_card.schema.json')
DEFAULT_FIXTURE = os.path.join(HERE, 'fixtures', 'final_card_workflow.json')
PORTRAIT_DIR = os.path.join(HERE, 'pilot', 'input')

SCHEMA_ID = 'pwg_ru.final_card.schema.v1'
RESULT_REQUIRED = {'card', 'judge'}
CARD_REQUIRED = {'key1', 'iast', 'records', 'notes'}
RECORD_REQUIRED = {'h', 'grammar', 'senses'}
SENSE_REQUIRED = {
    'tag', 'german', 'russian', 'equivalence_type', 'source_type',
    'stratum', 'differentia',
}
JUDGE_REQUIRED = {
    'key1', 'ok', 'severity', 'register_ok', 'sigla_kept', 'coverage_ok',
    'corpus_used', 'discrimination_quality', 'issues', 'note',
}
ISSUE_REQUIRED = {'severity', 'detail'}
EQ_TYPES = {'equivalent', 'explanatory'}
SOURCE_TYPES = {'attested', 'lexicographic', 'mixed'}
DISCRIMINATION_QUALITY = {'strong', 'adequate', 'weak', 'missing'}
HIGH_DISCRIMINATION = {'strong', 'adequate'}


def fail(msg):
    raise ValueError(msg)


def need_obj(obj, where):
    if not isinstance(obj, dict):
        fail('%s must be an object' % where)


def need_keys(obj, keys, where):
    miss = sorted(k for k in keys if k not in obj)
    if miss:
        fail('%s missing keys: %s' % (where, ', '.join(miss)))


def need_str(obj, key, where, nonempty=False):
    if not isinstance(obj.get(key), str):
        fail('%s.%s must be a string' % (where, key))
    if nonempty and not obj[key]:
        fail('%s.%s must be non-empty' % (where, key))


def need_bool(obj, key, where):
    if not isinstance(obj.get(key), bool):
        fail('%s.%s must be a boolean' % (where, key))


def need_list(obj, key, where):
    if not isinstance(obj.get(key), list):
        fail('%s.%s must be a list' % (where, key))


def result_items(raw):
    """Return workflow result objects from common harness wrapper shapes."""
    if isinstance(raw, dict):
        if isinstance(raw.get('results'), list):
            return raw['results']
        if isinstance(raw.get('result'), dict):
            return result_items(raw['result'])
        if RESULT_REQUIRED <= set(raw):
            return [raw]
        for v in raw.values():
            try:
                items = result_items(v)
            except ValueError:
                continue
            if items:
                return items
    if isinstance(raw, list):
        if all(isinstance(v, dict) and RESULT_REQUIRED <= set(v) for v in raw):
            return raw
        for v in raw:
            try:
                items = result_items(v)
            except ValueError:
                continue
            if items:
                return items
    fail('no final-card results found')


def _portrait_paths(key1):
    stem = safe_name(key1)
    return [
        os.path.join(PORTRAIT_DIR, stem + '.portrait.json'),
        os.path.join(PORTRAIT_DIR, key1 + '.portrait.json'),
    ]


def has_corpus_candidates(key1):
    """Return True when a pilot portrait for key1 has non-empty corpus candidates."""
    for path in _portrait_paths(key1):
        if not os.path.exists(path):
            continue
        portraits = json.load(open(path, encoding='utf-8'))
        if isinstance(portraits, dict):
            portraits = [portraits]
        for p in portraits:
            cs = p.get('corpus_synonyms') or {}
            if cs.get('candidates'):
                return True
    return False


def iter_senses(card):
    for rec in card.get('records', []):
        for sense in rec.get('senses', []):
            yield sense


def validate_issue(issue, where):
    need_obj(issue, where)
    need_keys(issue, ISSUE_REQUIRED, where)
    if not isinstance(issue.get('severity'), int) or not 1 <= issue['severity'] <= 5:
        fail('%s.severity must be an integer 1..5' % where)
    need_str(issue, 'detail', where)


def validate_judge(judge, key1):
    need_obj(judge, 'judge')
    need_keys(judge, JUDGE_REQUIRED, 'judge')
    need_str(judge, 'key1', 'judge', nonempty=True)
    if judge['key1'] != key1:
        fail('judge.key1 %r does not match card.key1 %r' % (judge['key1'], key1))
    for key in ('ok', 'register_ok', 'sigla_kept', 'coverage_ok', 'corpus_used'):
        need_bool(judge, key, 'judge')
    if not isinstance(judge.get('severity'), int) or not 1 <= judge['severity'] <= 5:
        fail('judge.severity must be an integer 1..5')
    if judge.get('discrimination_quality') not in DISCRIMINATION_QUALITY:
        fail('judge bad discrimination_quality: %r' % judge.get('discrimination_quality'))
    need_list(judge, 'issues', 'judge')
    for i, issue in enumerate(judge['issues']):
        validate_issue(issue, 'judge.issues[%d]' % i)
    need_str(judge, 'note', 'judge')


def validate_sense(sense, where):
    need_obj(sense, where)
    need_keys(sense, SENSE_REQUIRED, where)
    for key in ('tag', 'german', 'russian', 'stratum', 'differentia'):
        need_str(sense, key, where, nonempty=(key == 'tag'))
    if sense.get('equivalence_type') not in EQ_TYPES:
        fail('%s bad equivalence_type: %r' % (where, sense.get('equivalence_type')))
    if sense.get('source_type') not in SOURCE_TYPES:
        fail('%s bad source_type: %r' % (where, sense.get('source_type')))
    # Optional apparatus fields (added 2026-06-24, apparatus study). Validated
    # only when present, so existing cards stay valid.
    if 'government' in sense:
        need_str(sense, 'government', where)
    if 'labels' in sense:
        need_list(sense, 'labels', where)
        for k, lab in enumerate(sense['labels']):
            if not isinstance(lab, str) or not lab:
                fail('%s.labels[%d] must be a non-empty string' % (where, k))


def validate_card(card):
    need_obj(card, 'card')
    need_keys(card, CARD_REQUIRED, 'card')
    need_str(card, 'key1', 'card', nonempty=True)
    need_str(card, 'iast', 'card')
    need_str(card, 'notes', 'card')
    need_list(card, 'records', 'card')
    if not card['records']:
        fail('%s has no records' % card['key1'])
    for i, rec in enumerate(card['records']):
        where = 'card.records[%d]' % i
        need_obj(rec, where)
        need_keys(rec, RECORD_REQUIRED, where)
        need_str(rec, 'h', where)
        need_str(rec, 'grammar', where)
        need_list(rec, 'senses', where)
        if not rec['senses']:
            fail('%s.senses must not be empty' % where)
        for j, sense in enumerate(rec['senses']):
            validate_sense(sense, '%s.senses[%d]' % (where, j))


def validate_result(res, force_corpus_candidates=None):
    need_obj(res, 'result')
    need_keys(res, RESULT_REQUIRED, 'result')
    card = res['card']
    validate_card(card)
    key1 = card['key1']
    if 'key' in res and res['key'] != key1:
        fail('result.key %r does not match card.key1 %r' % (res['key'], key1))
    judge = res['judge']
    validate_judge(judge, key1)

    has_diff = any((s.get('differentia') or '').strip() for s in iter_senses(card))
    corpus_candidates = (has_corpus_candidates(key1) if force_corpus_candidates is None
                         else force_corpus_candidates)
    if (corpus_candidates and judge.get('corpus_used') and
            judge.get('discrimination_quality') in HIGH_DISCRIMINATION and not has_diff):
        fail('%s has corpus candidates and %s discrimination, but no non-empty differentia'
             % (key1, judge.get('discrimination_quality')))


def load_results(path):
    raw = json.load(open(path, encoding='utf-8'))
    return result_items(raw)


def validate_file(path):
    checked = 0
    for res in load_results(path):
        validate_result(res)
        checked += 1
    return checked


def cmd_selftest():
    base = load_results(DEFAULT_FIXTURE)[0]
    cases = []

    missing_diff = copy.deepcopy(base)
    del missing_diff['card']['records'][0]['senses'][0]['differentia']
    cases.append(('missing differentia field', missing_diff))

    missing_judge = copy.deepcopy(base)
    del missing_judge['judge']['coverage_ok']
    cases.append(('missing judge field', missing_judge))

    bad_quality = copy.deepcopy(base)
    bad_quality['judge']['discrimination_quality'] = 'excellent'
    cases.append(('invalid discrimination_quality', bad_quality))

    no_nonempty_diff = copy.deepcopy(base)
    for sense in no_nonempty_diff['card']['records'][0]['senses']:
        sense['differentia'] = ''
    cases.append(('strong discrimination without differentia', no_nonempty_diff))

    bad_labels = copy.deepcopy(base)
    bad_labels['card']['records'][0]['senses'][0]['labels'] = 'астр.'
    cases.append(('labels not a list', bad_labels))

    bad_government = copy.deepcopy(base)
    bad_government['card']['records'][0]['senses'][0]['government'] = ['+ Acc.']
    cases.append(('government not a string', bad_government))

    for name, bad in cases:
        try:
            validate_result(bad, force_corpus_candidates=True)
        except ValueError:
            continue
        fail('selftest case unexpectedly passed: %s' % name)
    print('final-card schema selftest OK: %d negative case(s)' % len(cases))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--selftest':
        cmd_selftest()
        return
    schema = json.load(open(SCHEMA, encoding='utf-8'))
    if schema.get('$id') != SCHEMA_ID:
        fail('unexpected schema id')
    paths = sys.argv[1:] or [DEFAULT_FIXTURE]
    total = 0
    for path in paths:
        total += validate_file(path)
    print('final-card schema validation OK: %d result(s)' % total)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('FINAL-CARD SCHEMA CHECK FAILED: %s' % e, file=sys.stderr)
        raise SystemExit(1)
