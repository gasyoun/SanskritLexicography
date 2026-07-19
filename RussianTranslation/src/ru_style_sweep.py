#!/usr/bin/env python
r"""Mechanical Russian style rules and the H1305 store-repair utility.

The hard rules are:

* R1: replace ё/Ё with е/Е, except standalone всё/Всё.
* R2: use вм. for high-confidence editorial uses of вместо.
* R3: use в знач. for high-confidence lexical uses of в значении.
* R4: translate ``ed. Bomb.`` only outside ``<ls>...</ls>``.

R2/R3 deliberately fail open for ambiguous prose.  The workflow gate inspects only
structured ``sense.russian`` values; rendered notes and other Markdown are out of scope.

Usage::

    python src/ru_style_sweep.py                         # store dry-run
    python src/ru_style_sweep.py --apply                 # safe store apply
    python src/ru_style_sweep.py --wf wf_output.json     # workflow audit
    python src/ru_style_sweep.py --repair-from OLD.jsonl # H1305 repair dry-run
    python src/ru_style_sweep.py --repair-from OLD.jsonl --apply
    python src/ru_style_sweep.py --selftest
"""
import argparse
import collections
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from store_path import canonical_store  # noqa: E402

RT = os.path.dirname(HERE)
SAMPLES_PER_RULE = 6

# ---------------------------------------------------------------------------
# Shared rule definitions.
# ---------------------------------------------------------------------------
YO_CHAR = re.compile('[ёЁ]')
WHITELIST_VSE = re.compile(r'(?<![а-яёА-ЯЁ\-])[Вв]сё(?![а-яёА-ЯЁ\-])')

VMESTO = re.compile(r'\bвместо\b', re.I)
VZNACH = re.compile(r'\bв\s+значении\b', re.I)
VMESTO_CAP = re.compile(r'\bВместо\b')
VMESTO_LOW = re.compile(r'\bвместо\b')
VZNACH_CAP = re.compile(r'\bВ\s+значении\b')
VZNACH_LOW = re.compile(r'\bв\s+значении\b')

# A match inside a quoted/retained gloss is prose, never editorial apparatus.
PROTECTED_PROSE = re.compile(r'\{%.*?%\}|«[^»]*»', re.S)
R2_CORRECTION_CUE = re.compile(
    r'ошибочн|опечатк|неверн|неточн|бессмысленн|непонятн|v\.\s*l\.|вариант', re.I)
R2_OBJECT = re.compile(
    r'^\s*(?:\{#|<ab\b|<lex\b|'
    r'(?:прост|втор|предикатив|обычн|употребительн|этого|котор|глагол)\w*)', re.I)
R2_FOLLOW = re.compile(
    r'следует\s+(?:читать|поставить)|читает|имеет|поставила', re.I)
R3_OBJECT = re.compile(r'^\s*(?:\{#|\{%|<ab\b|<lex\b|«)', re.I)
R3_LEXICAL_CUE = re.compile(
    r'употреб|слово|форма|термин|здесь|означа|понима|смысл|также|как', re.I)

LS_SPAN = re.compile(r'<ls\b[^>]*>.*?</ls>', re.S)
BOMB = re.compile(r'ed\.\s*Bomb\.')

RULE_ORDER = ('R4_bomb', 'R2_vmesto', 'R3_vznach', 'R1_yo')


def apply_no_yo(text):
    """Replace ё/Ё outside the standalone всё/Всё whitelist."""
    if not text or 'ё' not in text.lower():
        return text, 0
    protected = [(m.start(), m.end()) for m in WHITELIST_VSE.finditer(text)]
    out = list(text)
    n = 0
    for match in YO_CHAR.finditer(text):
        pos = match.start()
        if any(start <= pos < end for start, end in protected):
            continue
        out[pos] = 'Е' if match.group(0) == 'Ё' else 'е'
        n += 1
    return ''.join(out), n


def apply_bomb_prose_only(text):
    """Translate ``ed. Bomb.`` only outside citation spans."""
    if not text or 'Bomb' not in text:
        return text, 0
    out, count, last = [], 0, 0
    for match in LS_SPAN.finditer(text):
        segment, changed = BOMB.subn('Бомбейская ред.', text[last:match.start()])
        count += changed
        out.extend((segment, match.group(0)))
        last = match.end()
    tail, changed = BOMB.subn('Бомбейская ред.', text[last:])
    count += changed
    out.append(tail)
    return ''.join(out), count


def _protected_ranges(text):
    return [(match.start(), match.end()) for match in PROTECTED_PROSE.finditer(text or '')]


def _is_protected(ranges, position):
    return any(start <= position < end for start, end in ranges)


def _snippet(text, match, radius=80):
    start = max(0, match.start() - radius)
    end = min(len(text), match.end() + radius)
    return text[start:end].replace('\n', ' ')


def _r2_editorial(text, match):
    ranges = _protected_ranges(text)
    if _is_protected(ranges, match.start()):
        return False
    before = text[max(0, match.start() - 120):match.start()]
    after = text[match.end():match.end() + 120]
    return bool(
        R2_CORRECTION_CUE.search(before + match.group(0) + after)
        or R2_OBJECT.search(after)
        or R2_FOLLOW.search(after)
    )


def _r3_editorial(text, match):
    ranges = _protected_ranges(text)
    if _is_protected(ranges, match.start()):
        return False
    before = text[max(0, match.start() - 80):match.start()]
    after = text[match.end():match.end() + 80]
    return bool(
        R3_OBJECT.search(after)
        or R3_LEXICAL_CUE.search(before + after)
    )


def _apply_contextual(text, pattern, predicate, lower, upper, rule_id):
    """Apply a contextual substitution and retain diagnostic ambiguous matches."""
    if not text:
        return text, 0, []
    out, last, count, ambiguous = [], 0, 0, []
    for match in pattern.finditer(text):
        out.append(text[last:match.start()])
        if predicate(text, match):
            replacement = upper if match.group(0)[:1].isupper() else lower
            out.append(replacement)
            count += 1
        else:
            out.append(match.group(0))
            ambiguous.append({
                'rule': rule_id,
                'start': match.start(),
                'snippet': _snippet(text, match),
            })
        last = match.end()
    out.append(text[last:])
    return ''.join(out), count, ambiguous


def _apply_terse_vmesto_detailed(text):
    return _apply_contextual(text, VMESTO, _r2_editorial, 'вм.', 'Вм.', 'R2_vmesto')


def _apply_terse_vznach_detailed(text):
    return _apply_contextual(text, VZNACH, _r3_editorial, 'в знач.', 'В знач.', 'R3_vznach')


def apply_terse_vmesto(text):
    text, count, _ = _apply_terse_vmesto_detailed(text)
    return text, count


def apply_terse_vznach(text):
    text, count, _ = _apply_terse_vznach_detailed(text)
    return text, count


def style_diagnostics(text):
    """Return the fixed text plus hard and ambiguous rule diagnostics."""
    counts = {rule: 0 for rule in RULE_ORDER}
    ambiguous = []
    text, counts['R4_bomb'] = apply_bomb_prose_only(text)
    text, counts['R2_vmesto'], found = _apply_terse_vmesto_detailed(text)
    ambiguous.extend(found)
    text, counts['R3_vznach'], found = _apply_terse_vznach_detailed(text)
    ambiguous.extend(found)
    text, counts['R1_yo'] = apply_no_yo(text)
    return {
        'text': text,
        'counts': counts,
        'violations': [rule for rule in RULE_ORDER if counts[rule]],
        'ambiguous': ambiguous,
        'ambiguous_rules': sorted({item['rule'] for item in ambiguous}),
    }


def sweep_text(text):
    """Apply hard R1-R4 rules; ambiguous R2/R3 prose is unchanged."""
    result = style_diagnostics(text)
    return result['text'], result['counts']


def scan_violations(text):
    """Compatibility API: return only hard rule IDs that would change ``text``."""
    return style_diagnostics(text)['violations']


def legacy_sweep_text(text):
    """Reproduce H1305's original global R2/R3 sweep for safe reconciliation."""
    counts = {rule: 0 for rule in RULE_ORDER}
    text, counts['R4_bomb'] = apply_bomb_prose_only(text)
    text, cap = VMESTO_CAP.subn('Вм.', text)
    text, low = VMESTO_LOW.subn('вм.', text)
    counts['R2_vmesto'] = cap + low
    text, cap = VZNACH_CAP.subn('В знач.', text)
    text, low = VZNACH_LOW.subn('в знач.', text)
    counts['R3_vznach'] = cap + low
    text, counts['R1_yo'] = apply_no_yo(text)
    return text, counts


# ---------------------------------------------------------------------------
# Workflow gate: structured Russian senses only.
# ---------------------------------------------------------------------------
def audit_workflow_results(results):
    rows, flagged, warned = [], [], []
    for result in results or []:
        key = result.get('key')
        if not key:
            continue
        card = result.get('card')
        if not card:
            rows.append((key, 'skip', ['NO-CARD']))
            continue
        hard, soft = set(), set()
        for record in card.get('records') or []:
            for sense in record.get('senses') or []:
                diagnostic = style_diagnostics(sense.get('russian') or '')
                hard.update(diagnostic['violations'])
                soft.update(diagnostic['ambiguous_rules'])
        if hard:
            flagged.append(key)
            rows.append((key, 'FAIL', sorted(hard)))
        elif soft:
            warned.append(key)
            rows.append((key, 'warn', sorted(soft)))
        else:
            rows.append((key, 'ok', []))
    return rows, sorted(set(flagged)), sorted(set(warned))


def cmd_wf(wf_path):
    import audit_translation as at  # noqa: E402

    with open(wf_path, encoding='utf-8') as stream:
        results = at.find_results(json.load(stream)) or []
    rows, flagged, warned = audit_workflow_results(results)
    print('=== ru_style mechanical gate (%d units) ===' % len(rows))
    print('%-28s %-5s %s' % ('unit', 'st', 'flags'))
    for key, status, marks in rows:
        if status != 'ok':
            print('%-28s %-5s %s' % (key[:28], status, ' '.join(marks)))
    print('\n%s: %d/%d clean, %d warned, %d hard-flagged' % (
        'PASS' if not flagged else 'FAIL',
        len(rows) - len(flagged) - len(warned), len(rows), len(warned), len(flagged)))
    print('WARNED_JSON: %s' % json.dumps(warned))
    print('FLAGGED_JSON: %s' % json.dumps(flagged))
    return 0 if not flagged else 1


# ---------------------------------------------------------------------------
# Store IO, backups, and repair reconciliation.
# ---------------------------------------------------------------------------
MUTABLE_ID_FIELDS = {'ru'}


def _is_mutable_identity_field(key):
    normalized = str(key).lower()
    return (
        normalized in MUTABLE_ID_FIELDS
        or 'review' in normalized
        or 'evidence' in normalized
        or 'provenance' in normalized
    )


def _read_rows(path):
    rows = []
    with open(path, encoding='utf-8') as stream:
        for line_number, line in enumerate(stream, 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except ValueError as exc:
                    raise ValueError('%s:%d: %s' % (path, line_number, exc)) from exc
    return rows


def _file_sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _row_count(path):
    with open(path, 'rb') as stream:
        return sum(1 for line in stream if line.strip())


def _utc_stamp(now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    return now.strftime('%Y%m%dT%H%M%S%fZ')


def _create_verified_backup(store, backup_dir=None, stamp=None):
    backup_dir = os.path.abspath(backup_dir or os.path.dirname(store))
    os.makedirs(backup_dir, exist_ok=True)
    stamp = stamp or _utc_stamp()
    backup = os.path.join(backup_dir, os.path.basename(store) + '.h1305.' + stamp + '.bak')
    with open(store, 'rb') as source, open(backup, 'xb') as target:
        shutil.copyfileobj(source, target, length=1024 * 1024)
    source_hash = _file_sha256(store)
    backup_hash = _file_sha256(backup)
    source_rows = _row_count(store)
    backup_rows = _row_count(backup)
    if source_hash != backup_hash or source_rows != backup_rows:
        raise RuntimeError('backup verification failed: %s' % backup)
    return {'path': backup, 'sha256': backup_hash, 'rows': backup_rows}


def _write_rows_atomic(store, rows, initial_hash, backup_dir=None, stamp=None):
    if _file_sha256(store) != initial_hash:
        raise RuntimeError('store changed after read; refusing apply')
    backup = _create_verified_backup(store, backup_dir=backup_dir, stamp=stamp)
    tmp = '%s.tmp.%d' % (store, os.getpid())
    try:
        with open(tmp, 'x', encoding='utf-8') as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + '\n')
        if _file_sha256(store) != initial_hash:
            raise RuntimeError('store changed before replace; refusing apply')
        os.replace(tmp, store)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return backup


def _identity_base(row):
    stable = {key: value for key, value in row.items() if not _is_mutable_identity_field(key)}
    payload = json.dumps(stable, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def _index_rows(rows):
    seen = collections.Counter()
    indexed = {}
    for index, row in enumerate(rows):
        base = _identity_base(row)
        ordinal = seen[base]
        seen[base] += 1
        indexed[(base, ordinal)] = index
    return indexed


def _row_label(row):
    return '%s|%s|%s' % (row.get('key1'), row.get('subcard'), row.get('sense_tag'))


def reconcile_rows(current_rows, backup_rows):
    """Rebuild recognized H1305 rows without overwriting divergent later edits."""
    current_index = _index_rows(current_rows)
    backup_index = _index_rows(backup_rows)
    output = [dict(row) for row in current_rows]
    totals = {rule: 0 for rule in RULE_ORDER}
    ambiguous_counts = collections.Counter()
    ambiguous_examples = []
    conflicts = []
    restored = []
    restored_prose = []
    current_only = []

    for identity, current_pos in current_index.items():
        current = current_rows[current_pos]
        current_ru = current.get('ru') or ''
        if identity in backup_index:
            original = backup_rows[backup_index[identity]].get('ru') or ''
            legacy, _ = legacy_sweep_text(original)
            diagnostic = style_diagnostics(original)
            desired = diagnostic['text']
            recognized = {original, legacy, desired}
            if current_ru not in recognized:
                conflicts.append({
                    'row': _row_label(current),
                    'identity': '%s:%d' % identity,
                    'reason': 'current ru diverges from original, legacy sweep, and repaired value',
                    'backup_ru': original,
                    'legacy_ru': legacy,
                    'scoped_ru': desired,
                    'current_ru': current_ru,
                })
                continue
            if legacy != desired:
                restored_prose.append({
                    'row': _row_label(current),
                    'backup_ru': original,
                    'legacy_ru': legacy,
                    'scoped_ru': desired,
                    'current_state': (
                        'legacy' if current_ru == legacy
                        else 'scoped' if current_ru == desired
                        else 'original'),
                })
        else:
            diagnostic = style_diagnostics(current_ru)
            desired = diagnostic['text']
            current_only.append(_row_label(current))

        for rule, count in diagnostic['counts'].items():
            totals[rule] += count
        for item in diagnostic['ambiguous']:
            ambiguous_counts[item['rule']] += 1
            if len(ambiguous_examples) < 100:
                ambiguous_examples.append({
                    'row': _row_label(current),
                    'rule': item['rule'],
                    'snippet': item['snippet'],
                })
        if current_ru != desired:
            output[current_pos]['ru'] = desired
            restored.append(_row_label(current))

    backup_only = [
        _row_label(backup_rows[position])
        for identity, position in backup_index.items() if identity not in current_index
    ]
    return output, {
        'rule_counts': totals,
        'ambiguous_counts': dict(sorted(ambiguous_counts.items())),
        'ambiguous_examples': ambiguous_examples,
        'changed_rows': restored,
        'restored_prose': restored_prose,
        'current_only_rows': current_only,
        'backup_only_rows': backup_only,
        'conflicts': conflicts,
    }


def _default_report_path(store, stamp):
    output_dir = os.path.join(os.path.dirname(store), 'pilot', 'output')
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, 'ru_style_repair_%s_%d.json' % (stamp, os.getpid()))


def _write_report(path, report):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'x', encoding='utf-8') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def run_repair(backup_path, apply_=False, backup_dir=None, report_path=None):
    store = canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl'))
    store = os.path.abspath(store)
    backup_path = os.path.abspath(backup_path)
    print('resolved store  : %s' % store)
    print('repair source   : %s' % backup_path)
    if not os.path.exists(store):
        raise FileNotFoundError('STORE ABSENT: %s' % store)
    if not os.path.exists(backup_path):
        raise FileNotFoundError('REPAIR SOURCE ABSENT: %s' % backup_path)

    stamp = _utc_stamp()
    initial_hash = _file_sha256(store)
    current_rows = _read_rows(store)
    backup_rows = _read_rows(backup_path)
    repaired_rows, detail = reconcile_rows(current_rows, backup_rows)
    report = {
        'schema': 'pwg_ru.ru_style_repair.v1',
        'created_utc': stamp,
        'mode': 'apply' if apply_ else 'dry-run',
        'store': store,
        'repair_source': backup_path,
        'before_sha256': initial_hash,
        'repair_source_sha256': _file_sha256(backup_path),
        'before_rows': len(current_rows),
        'repair_source_rows': len(backup_rows),
        **detail,
    }
    print('rows            : %d current / %d repair-source' % (len(current_rows), len(backup_rows)))
    print('changed rows    : %d' % len(detail['changed_rows']))
    print('restored prose  : %d reviewed occurrences' % len(detail['restored_prose']))
    print('current-only    : %d' % len(detail['current_only_rows']))
    print('backup-only     : %d' % len(detail['backup_only_rows']))
    print('conflicts       : %d' % len(detail['conflicts']))
    print('ambiguous       : %s' % (detail['ambiguous_counts'] or '{}'))

    exit_code = 0
    if detail['conflicts']:
        exit_code = 2
        report['after_sha256'] = _file_sha256(store)
        report['after_rows'] = _row_count(store)
        print('REFUSED: divergent rows require manual reconciliation', file=sys.stderr)
    elif apply_:
        backup = _write_rows_atomic(
            store, repaired_rows, initial_hash, backup_dir=backup_dir, stamp=stamp)
        report['apply_backup'] = backup
        report['after_sha256'] = _file_sha256(store)
        report['after_rows'] = _row_count(store)
        print('backup          : %s' % backup['path'])
        print('backup sha256   : %s' % backup['sha256'])
        print('wrote           : %s' % store)
    else:
        report['after_sha256'] = initial_hash
        report['after_rows'] = len(current_rows)
        print('(dry run -- pass --apply to write)')

    report_path = os.path.abspath(report_path or _default_report_path(store, stamp))
    _write_report(report_path, report)
    print('report          : %s' % report_path)
    return exit_code


def run_store(apply_=False, backup_dir=None):
    store = os.path.abspath(canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl')))
    print('resolved store  : %s' % store)
    if not os.path.exists(store):
        raise FileNotFoundError('STORE ABSENT: %s' % store)
    initial_hash = _file_sha256(store)
    rows = _read_rows(store)
    totals = {rule: 0 for rule in RULE_ORDER}
    ambiguous = collections.Counter()
    samples = {rule: [] for rule in RULE_ORDER}
    touched = 0
    for row in rows:
        original = row.get('ru') or ''
        diagnostic = style_diagnostics(original)
        for rule, count in diagnostic['counts'].items():
            totals[rule] += count
            if count and len(samples[rule]) < SAMPLES_PER_RULE:
                samples[rule].append((_row_label(row), original, diagnostic['text']))
        for item in diagnostic['ambiguous']:
            ambiguous[item['rule']] += 1
        if diagnostic['text'] != original:
            touched += 1
            if apply_:
                row['ru'] = diagnostic['text']

    grand_total = sum(totals.values())
    print('mode            : %s' % ('APPLY' if apply_ else 'DRY RUN'))
    print('rows            : %d' % len(rows))
    print('rows touched    : %d' % touched)
    for rule in RULE_ORDER:
        print('  %-12s %d' % (rule, totals[rule]))
    print('  %-12s %d' % ('TOTAL', grand_total))
    print('ambiguous       : %s' % (dict(ambiguous) or '{}'))
    if apply_ and grand_total:
        backup = _write_rows_atomic(store, rows, initial_hash, backup_dir=backup_dir)
        print('backup          : %s' % backup['path'])
        print('backup sha256   : %s' % backup['sha256'])
        print('wrote           : %s' % store)
    elif not apply_:
        print('(dry run -- pass --apply to write)')
    return grand_total


# ---------------------------------------------------------------------------
# Deterministic selftest.
# ---------------------------------------------------------------------------
def selftest():
    fixed, count = apply_no_yo('она всё ещё ждёт')
    assert fixed == 'она всё еще ждет' and count == 2, (fixed, count)
    fixed, count = apply_no_yo('всё-таки пришёл')
    assert fixed == 'все-таки пришел' and count == 2, (fixed, count)

    fixed, count = apply_terse_vmesto('ошибочно вместо {#X#}')
    assert fixed == 'ошибочно вм. {#X#}' and count == 1, (fixed, count)
    fixed, count = apply_terse_vmesto('Вместо {#X#} следует читать {#Y#}')
    assert fixed == 'Вм. {#X#} следует читать {#Y#}' and count == 1, (fixed, count)
    for prose in (
            'Он выступил вместо брата.',
            '«в отдельные случаи [вместо того чтобы быть непрерывным]»',
            'при māraṇa вместо abhra'):
        fixed, count = apply_terse_vmesto(prose)
        assert fixed == prose and count == 0, (fixed, count)

    fixed, count = apply_terse_vznach('форма употребляется в значении {#X#}')
    assert fixed == 'форма употребляется в знач. {#X#}' and count == 1, (fixed, count)
    prose = 'Он понял знак в значении обещания.'
    fixed, count = apply_terse_vznach(prose)
    assert fixed == prose and count == 0, (fixed, count)

    fixed, count = apply_bomb_prose_only('<ls>ed. Bomb.</ls> (ed. Bomb.)')
    assert fixed == '<ls>ed. Bomb.</ls> (Бомбейская ред.)' and count == 1, (fixed, count)

    results = [{
        'key': 'clean-notes',
        'card': {'notes': 'Переводчик пришёл.', 'records': [{
            'senses': [{'russian': 'чистый текст', 'differentia': 'пришёл'}],
        }]},
    }, {
        'key': 'multi-hard',
        'card': {'records': [{'senses': [
            {'russian': 'пришёл'}, {'russian': 'ошибочно вместо {#X#}'},
        ]}]},
    }, {
        'key': 'ambiguous',
        'card': {'records': [{'senses': [{'russian': 'Он выступил вместо брата.'}]}]},
    }]
    _, flagged, warned = audit_workflow_results(results)
    assert flagged == ['multi-hard'], flagged
    assert warned == ['ambiguous'], warned

    backup_rows = [
        {'key1': 'a', 'subcard': 'a~~1', 'sense_tag': '1', 'de': 'x',
         'ru': 'Он выступил вместо брата.'},
        {'key1': 'b', 'subcard': 'b~~1', 'sense_tag': '1', 'de': 'y',
         'ru': 'ошибочно вместо {#X#}'},
    ]
    current_rows = []
    for row in backup_rows:
        copy = dict(row)
        copy['ru'] = legacy_sweep_text(row['ru'])[0]
        current_rows.append(copy)
    current_rows.append(
        {'key1': 'c', 'subcard': 'c~~1', 'sense_tag': '1', 'de': 'z', 'ru': 'всё хорошо'})
    repaired, detail = reconcile_rows(current_rows, backup_rows)
    assert repaired[0]['ru'] == backup_rows[0]['ru'], repaired[0]
    assert repaired[1]['ru'] == 'ошибочно вм. {#X#}', repaired[1]
    assert repaired[2]['ru'] == 'всё хорошо', repaired[2]
    assert len(detail['current_only_rows']) == 1 and not detail['conflicts'], detail
    assert len(detail['restored_prose']) == 1, detail['restored_prose']
    divergent = [dict(row) for row in current_rows]
    divergent[0]['ru'] = 'поздняя ручная правка'
    _, detail = reconcile_rows(divergent, backup_rows)
    assert len(detail['conflicts']) == 1, detail

    with tempfile.TemporaryDirectory() as temp_dir:
        store = os.path.join(temp_dir, 'store.jsonl')
        with open(store, 'w', encoding='utf-8') as stream:
            stream.write(json.dumps(backup_rows[0], ensure_ascii=False) + '\n')
        first = _create_verified_backup(store, temp_dir, stamp='one')
        second = _create_verified_backup(store, temp_dir, stamp='two')
        assert first['path'] != second['path'] and first['sha256'] == second['sha256']
        try:
            _create_verified_backup(store, temp_dir, stamp='one')
        except FileExistsError:
            pass
        else:
            raise AssertionError('backup path reuse did not fail')
        try:
            _write_rows_atomic(store, backup_rows, '0' * 64, backup_dir=temp_dir)
        except RuntimeError as exc:
            assert 'changed after read' in str(exc), exc
        else:
            raise AssertionError('stale store hash did not fail')

        # Simulate a concurrent change after the verified backup but immediately before
        # replacement. The second live-store hash check must still fail closed.
        initial = _file_sha256(store)
        real_hasher = _file_sha256
        store_hash_calls = [0]

        def simulated_race(path):
            if os.path.abspath(path) == os.path.abspath(store):
                store_hash_calls[0] += 1
                if store_hash_calls[0] >= 3:
                    return 'f' * 64
            return real_hasher(path)

        globals()['_file_sha256'] = simulated_race
        try:
            try:
                _write_rows_atomic(store, backup_rows, initial, backup_dir=temp_dir)
            except RuntimeError as exc:
                assert 'changed before replace' in str(exc), exc
            else:
                raise AssertionError('mid-run store change did not fail')
        finally:
            globals()['_file_sha256'] = real_hasher

    combined, counts = sweep_text(
        'ошибочно вместо {#X#}; форма употребляется в значении {#Y#}; всё хорошо')
    twice, counts2 = sweep_text(combined)
    assert combined == 'ошибочно вм. {#X#}; форма употребляется в знач. {#Y#}; всё хорошо'
    assert sum(counts.values()) == 2 and twice == combined and not sum(counts2.values())
    print('ru_style_sweep selftest: PASS')
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selftest', action='store_true')
    parser.add_argument('--wf', metavar='WF_OUTPUT')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--repair-from', metavar='H1305_BACKUP')
    parser.add_argument('--backup-dir')
    parser.add_argument('--report')
    args = parser.parse_args()
    if args.selftest:
        selftest()
        return 0
    if args.wf:
        if args.apply or args.repair_from:
            parser.error('--wf cannot be combined with --apply/--repair-from')
        return cmd_wf(args.wf)
    if args.repair_from:
        return run_repair(
            args.repair_from, apply_=args.apply,
            backup_dir=args.backup_dir, report_path=args.report)
    if args.report:
        parser.error('--report is only valid with --repair-from')
    run_store(apply_=args.apply, backup_dir=args.backup_dir)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
