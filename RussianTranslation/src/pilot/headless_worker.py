#!/usr/bin/env python
"""Execute one PWG translation manifest through Claude Code headless mode."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

AUTH_RE = re.compile(r'401|authentication|not logged in|invalid.*credential', re.I)
RATE_RE = re.compile(r'429|rate.?limit|usage limit|too many requests', re.I)
CONN_RE = re.compile(r'connection closed|econnreset|socket hang up|network error', re.I)
EXIT_AUTH = 20
EXIT_RATE_LIMIT = 21
EXIT_TIMEOUT = 22
EXIT_MALFORMED = 23
EXIT_CONTENT = 24


def sha256_path(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def atomic_json(path, payload):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + '.tmp.%d' % os.getpid()
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write('\n')
    os.replace(tmp, path)


def suggestion_block(rows):
    if not rows:
        return ''
    lines = []
    for row in rows:
        scores = 'de=%s sa=%s tag=%s combined=%s' % (
            row.get('score_de_fragment', 'n/a'), row.get('score_sa_headword', 'n/a'),
            row.get('score_semantic_tag', 'n/a'),
            row.get('score_combined', row.get('score', 'n/a')))
        lines.append('[%s %s %s] %s' % (row.get('source_kind', 'suggestion'), scores,
                                        row.get('provenance_note', ''), row.get('text', '')))
    return ('\n--- advisory translation-memory suggestions (SUGGEST ONLY; do not copy '
            'unsupported senses) ---\n' + '\n'.join(lines))


def card_block(manifest, key):
    inp = manifest['inputs'][key]
    grammar = manifest['prompt'].get('grammars', {}).get(key, '')
    return (grammar + '\n\n=== CARD ' + key + ' ===\n'
            '--- masked German (translatable only; {Tn}=masked span) ---\n' +
            inp['skeleton'] + suggestion_block(manifest.get('suggestions', {}).get(key, [])) +
            '\n--- portrait (evidence) ---\n' + inp['portrait'])


def build_prompt(manifest, keys):
    prompt = manifest['prompt']
    nws = prompt.get('nws_rule', '') if any(manifest['inputs'][k].get('nws') for k in keys) else ''
    return (prompt['preamble'] + prompt.get('grammar', '') + prompt['translation'] +
            ('\n\n' + nws + '\n' if nws else '') +
            ''.join(card_block(manifest, key) for key in keys))


def extract_structured(stdout):
    try:
        wrapper = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ValueError('Claude output is not JSON: %s' % exc)
    value = wrapper.get('structured_output')
    if value is None:
        value = wrapper.get('result')
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError('Claude result is not structured JSON: %s' % exc)
    if not isinstance(value, dict) or not isinstance(value.get('cards'), list):
        raise ValueError('Claude result has no cards[] object')
    return value, wrapper


def restore_text(text, placeholders):
    def repl(match):
        idx = int(match.group(1)) - 1
        return placeholders[idx] if 0 <= idx < len(placeholders) else match.group(0)
    return re.sub(r'\{T(\d+)\}', repl, text or '')


def restore_card(card, field, placeholders):
    for record in card.get('records') or []:
        for sense in record.get('senses') or []:
            if 'german' in sense:
                sense['german'] = restore_text(sense['german'], placeholders)
            if field in sense:
                sense[field] = restore_text(sense[field], placeholders)
    return card


def count_card(card, needle):
    return sum((sense.get('german') or '').count(needle)
               for record in card.get('records') or []
               for sense in record.get('senses') or [])


def normalize_batch(manifest, keys, structured):
    by_key = {}
    for card in structured['cards']:
        if isinstance(card, dict) and card.get('key1') not in by_key:
            by_key[card.get('key1')] = card
    nominal_map = manifest['meta'].get('nominal_keymap') or {}
    reverse = {}
    for key in keys:
        reverse.setdefault(nominal_map.get(key), []).append(key)
    rows = []
    for key in keys:
        card = by_key.get(key)
        echoed = nominal_map.get(key)
        if card is None and echoed and len(reverse.get(echoed, [])) == 1:
            card = by_key.get(echoed)
            if card:
                card['key1'] = key
        error = None
        if card is None:
            error = 'missing-or-mismatched-key'
        else:
            card = restore_card(card, manifest['field'], manifest['placeholder_maps'].get(key, []))
            inp = manifest['inputs'][key]
            if count_card(card, '<ls') != inp['ls'] or count_card(card, '{#') != inp['sk']:
                error = 'fidelity-reject'
                card = None
        row = {'key': key, 'card': card, 'judge': None, 'judge_sonnet': None,
               'escalated': False}
        if error:
            row['error'] = error
        rows.append(row)
    return rows


def classify_process(proc):
    text = (proc.stdout or '') + '\n' + (proc.stderr or '')
    if AUTH_RE.search(text):
        return 'authentication', EXIT_AUTH
    if RATE_RE.search(text):
        return 'rate_limit', EXIT_RATE_LIMIT
    if CONN_RE.search(text):
        return 'connection', proc.returncode or 1
    return 'process', proc.returncode or 1


def execute(manifest, claude='claude', timeout=7200, runner=None):
    if manifest.get('schema') != 'pwg.headless_execution_manifest.v1':
        raise ValueError('unsupported manifest schema')
    if manifest.get('presplit_keys'):
        raise ValueError('headless v1 refuses presplit cards; prepare one-card no_pwg canaries')
    results = []
    attempts = []
    run = runner or subprocess.run
    for index, keys in enumerate(manifest.get('batches') or []):
        prompt = build_prompt(manifest, keys)
        argv = [claude, '-p', '--output-format', 'json', '--json-schema',
                json.dumps(manifest['output_schema'], ensure_ascii=False, separators=(',', ':')),
                '--model', manifest['model'], '--permission-mode', 'plan']
        started = time.monotonic()
        try:
            proc = run(argv, input=prompt, text=True, encoding='utf-8', capture_output=True,
                       timeout=timeout)
        except subprocess.TimeoutExpired:
            return None, {'classification': 'timeout', 'batch': index}, EXIT_TIMEOUT
        elapsed_ms = int((time.monotonic() - started) * 1000)
        attempts.append({'batch': index, 'keys': keys, 'returncode': proc.returncode,
                         'elapsed_ms': elapsed_ms})
        if proc.returncode:
            classification, code = classify_process(proc)
            return None, {'classification': classification, 'batch': index,
                          'stderr': (proc.stderr or '')[-2000:], 'attempts': attempts}, code
        try:
            structured, _wrapper = extract_structured(proc.stdout)
        except ValueError as exc:
            return None, {'classification': 'malformed_output', 'batch': index,
                          'error': str(exc), 'attempts': attempts}, EXIT_MALFORMED
        results.extend(normalize_batch(manifest, keys, structured))
    for key, card in manifest.get('tm_resolved', {}).items():
        results.append({'key': key, 'card': card, 'judge': None, 'judge_sonnet': None,
                        'escalated': False, 'tm': True})
    for key, card in manifest.get('degenerate_resolved', {}).items():
        results.append({'key': key, 'card': card, 'judge': None, 'judge_sonnet': None,
                        'escalated': False, 'degenerate_passthrough': True})
    seen = {row['key'] for row in results}
    for key in manifest['meta']['selected_keys']:
        if key not in seen:
            results.append({'key': key, 'card': None, 'judge': None, 'judge_sonnet': None,
                            'escalated': False, 'error': 'unaccounted-key'})
    failures = {row['key']: row.get('error', 'unknown') for row in results if not row['card']}
    summary = {'root': manifest['meta']['root'], 'lang': manifest['meta']['lang'],
               'cards': len(results), 'ok': len(results) - len(failures), 'null': len(failures),
               'healed': 0, 'presplit': 0,
               'tm': sum(bool(row.get('tm')) for row in results),
               'degenerate_passthrough': sum(bool(row.get('degenerate_passthrough')) for row in results),
               'null_keys': list(failures), 'partial_keys': [], 'failures': failures,
               'headless_attempts': attempts}
    payload = {'meta': manifest['meta'], 'summary': summary, 'results': results}
    status = {'classification': 'content_failure' if failures else 'success',
              'attempts': attempts, 'null_keys': list(failures)}
    return payload, status, EXIT_CONTENT if failures else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('manifest')
    ap.add_argument('--output', required=True)
    ap.add_argument('--status-out', required=True)
    ap.add_argument('--claude-bin', default='claude')
    ap.add_argument('--timeout', type=int, default=7200)
    args = ap.parse_args(argv)
    manifest_hash = sha256_path(args.manifest)
    with open(args.manifest, encoding='utf-8') as f:
        manifest = json.load(f)
    try:
        payload, status, code = execute(manifest, args.claude_bin, args.timeout)
    except (OSError, ValueError) as exc:
        payload, status, code = None, {'classification': 'configuration', 'error': str(exc)}, 2
    status['manifest_sha256'] = manifest_hash
    if payload is not None:
        atomic_json(args.output, payload)
        status['result_sha256'] = sha256_path(args.output)
    atomic_json(args.status_out, status)
    print(json.dumps(status, ensure_ascii=False))
    raise SystemExit(code)


if __name__ == '__main__':
    main()
