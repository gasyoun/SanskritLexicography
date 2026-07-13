#!/usr/bin/env python
"""Execute one PWG translation manifest through Claude Code headless mode."""
import argparse
import collections
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from proc_tree import run_tree_kill, terminate_tree  # noqa: E402  (shared D-J tree-kill runner)

AUTH_RE = re.compile(r'401|authentication|not logged in|invalid.*credential', re.I)
RATE_RE = re.compile(r'429|rate.?limit|usage limit|too many requests', re.I)
CONN_RE = re.compile(r'connection closed|econnreset|socket hang up|network error', re.I)
EXIT_AUTH = 20
EXIT_RATE_LIMIT = 21
EXIT_TIMEOUT = 22
EXIT_MALFORMED = 23
EXIT_CONTENT = 24


def claude_argv_prefix(claude_bin):
    """Return the argv prefix that invokes the Claude CLI directly (Windows-safe).

    On Windows the npm launcher is a ``.cmd``/``.ps1`` batch shim; Python routes it
    through cmd.exe, which reinterprets the ``<``/``>`` characters in a ``--json-schema``
    argument as redirection and caps the command line near 8191 chars — so a real card
    schema is corrupted and the call dies with "cannot find the file specified" (the
    H818 Windows live-acceptance D-A defect). Resolve such a shim to
    ``[node, <cli entry>.cjs]`` and invoke that directly, bypassing cmd.exe. A native
    executable, or any POSIX launcher, is returned unchanged.
    """
    if os.name != 'nt':
        return [claude_bin]
    if os.path.splitext(claude_bin)[1].lower() in ('.exe', '.com'):
        return [claude_bin]
    node = shutil.which('node')
    shim_dir = os.path.dirname(os.path.abspath(claude_bin)) or '.'
    base = os.path.join(shim_dir, 'node_modules', '@anthropic-ai', 'claude-code')
    entries = sorted(glob.glob(os.path.join(base, 'cli*.cjs')) +
                     glob.glob(os.path.join(base, 'cli*.js')))
    if node and entries:
        return [node, entries[0]]
    return [claude_bin]


class HardFailure(Exception):
    def __init__(self, classification, code, detail=''):
        super().__init__(detail or classification)
        self.classification = classification
        self.code = code
        self.detail = detail


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


def card_by_key(cards):
    out = {}
    for card in cards or []:
        if isinstance(card, dict) and card.get('key1') not in out:
            out[card.get('key1')] = card
    return out


def token_multiset(value):
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False)
    return collections.Counter(re.findall(r'\{T\d+\}', value))


def card_token_multiset(card):
    tokens = []
    for record in card.get('records') or []:
        for sense in record.get('senses') or []:
            tokens.extend(re.findall(r'\{T\d+\}', sense.get('german') or ''))
    return collections.Counter(tokens)


# run_tree_kill / terminate_tree moved to proc_tree (shared D-J runner); imported above.


class HeadlessEngine:
    def __init__(self, manifest, claude, timeout, runner):
        self.m = manifest
        self.claude = claude
        self.timeout = timeout
        self.run = runner or run_tree_kill
        self.attempts = []
        self.failures = {}
        self.translate_calls = 0
        self.heal_calls = 0
        self.kill_timeouts = 0
        self.conn_errors = 0

    def note(self, key, error):
        self.failures[key] = str(error)[:300]

    def call(self, prompt, label, keys, heal=False):
        argv = claude_argv_prefix(self.claude) + [
                '-p', '--output-format', 'json', '--json-schema',
                json.dumps(self.m['output_schema'], ensure_ascii=False, separators=(',', ':')),
                '--model', self.m['model'], '--permission-mode', 'plan']
        started = time.monotonic()
        if heal:
            self.heal_calls += 1
        else:
            self.translate_calls += 1
        try:
            proc = self.run(argv, input=prompt, text=True, encoding='utf-8',
                            capture_output=True, timeout=self.timeout)
        except subprocess.TimeoutExpired as exc:
            self.kill_timeouts += 1
            attempt = {'label': label, 'keys': keys, 'returncode': 124,
                       'elapsed_ms': int((time.monotonic() - started) * 1000),
                       'classification': 'timeout'}
            cleanup = getattr(exc, 'cleanup_trouble', None)
            if cleanup:                                # D-J: diagnostic only; classification stays 'timeout'
                attempt['cleanup_trouble'] = cleanup
            self.attempts.append(attempt)
            return None, 'timeout'
        elapsed = int((time.monotonic() - started) * 1000)
        if proc.returncode:
            classification, code = classify_process(proc)
            if classification == 'connection':
                self.conn_errors += 1
            self.attempts.append({'label': label, 'keys': keys, 'returncode': proc.returncode,
                                  'elapsed_ms': elapsed, 'classification': classification})
            raise HardFailure(classification, code, (proc.stderr or proc.stdout or '')[-2000:])
        try:
            structured, _wrapper = extract_structured(proc.stdout)
        except ValueError as exc:
            self.attempts.append({'label': label, 'keys': keys, 'returncode': 0,
                                  'elapsed_ms': elapsed, 'classification': 'malformed_output'})
            return None, 'malformed_output:%s' % exc
        self.attempts.append({'label': label, 'keys': keys, 'returncode': 0,
                              'elapsed_ms': elapsed, 'classification': 'success'})
        return structured, None

    def whole_prompt(self, keys):
        return build_prompt(self.m, keys)

    def resolve_group(self, keys, label):
        resolved = {}
        pending = list(keys)
        attempts = int(self.m.get('runtime', {}).get('whole_attempts', 2))
        timed_out = False
        for attempt in range(attempts):
            if not pending:
                break
            structured, error = self.call(self.whole_prompt(pending),
                                          '%s%s' % (label, '.retry%d' % attempt if attempt else ''),
                                          pending)
            if error:
                for key in pending:
                    self.note(key, error)
                timed_out = error == 'timeout'
                if timed_out:
                    break
                continue
            for row in normalize_batch(self.m, pending, structured):
                if row['card']:
                    resolved[row['key']] = row['card']
                else:
                    self.note(row['key'], row.get('error', 'unresolved'))
            pending = [key for key in pending if key not in resolved]
        if (pending and len(pending) > 1 and
                self.m.get('runtime', {}).get('binary_split', True)):
            mid = (len(pending) + 1) // 2
            for suffix, half in (('A', pending[:mid]), ('B', pending[mid:])):
                child, _child_pending = self.resolve_group(half, label + '/' + suffix)
                resolved.update(child)
            pending = [key for key in pending if key not in resolved]
        return resolved, pending

    def fragment_prompt(self, key, group, indices):
        blocks = []
        for index in indices:
            frag_key = '%s_f%d' % (key, index)
            blocks.append('\n\n=== CARD %s (fragment %d/%d) ===\n'
                          '--- masked German (translatable only; {Tn}=masked span) ---\n%s'
                          % (frag_key, index + 1, len(group), group[index]['skeleton']))
        prompt = self.m['prompt']
        return prompt['preamble'] + prompt.get('grammar', '') + prompt['translation'] + ''.join(blocks)

    def heal_group(self, key, group, indices, label, budget):
        resolved = {}
        pending = list(indices)
        attempts = int(self.m.get('runtime', {}).get('fragment_attempts', 3))
        timed_out = False
        for attempt in range(attempts):
            if not pending or budget['spent'] >= budget['max']:
                break
            budget['spent'] += 1
            structured, error = self.call(self.fragment_prompt(key, group, pending),
                                          '%s%s' % (label, '.retry%d' % attempt if attempt else ''),
                                          ['%s_f%d' % (key, i) for i in pending], heal=True)
            if error:
                for index in pending:
                    self.note('%s_f%d' % (key, index), error)
                timed_out = error == 'timeout'
                if timed_out:
                    break
                continue
            by_key = card_by_key(structured['cards'])
            for index in pending:
                frag_key = '%s_f%d' % (key, index)
                card = by_key.get(frag_key)
                if not card:
                    self.note(frag_key, 'missing-or-mismatched-fragment-key')
                    continue
                if card_token_multiset(card) != token_multiset(group[index]['skeleton']):
                    self.note(frag_key, 'fragment-fidelity-reject')
                    continue
                resolved[index] = card
            pending = [index for index in pending if index not in resolved]
        no_bisect = timed_out and self.m.get('runtime', {}).get('kill_timeout_no_bisect', True)
        if (len(pending) > 1 and not no_bisect and budget['spent'] < budget['max']):
            mid = (len(pending) + 1) // 2
            for suffix, half in (('A', pending[:mid]), ('B', pending[mid:])):
                child, _ = self.heal_group(key, group, half, label + '/' + suffix, budget)
                resolved.update(child)
            pending = [index for index in pending if index not in resolved]
        return resolved, pending

    def self_heal(self, key):
        groups = self.m.get('fragment_groups', {}).get(key) or []
        if not groups:
            self.note(key, 'no-selfheal-fallback')
            return None
        runtime = self.m.get('runtime', {})
        maximum = (int((len(groups) * float(runtime.get('per_card_heal_factor', 1.5))) + 0.9999) +
                   int(runtime.get('per_card_heal_headroom', 3)))
        if not runtime.get('per_card_heal_budget', True):
            maximum = 10 ** 9
        budget = {'spent': 0, 'max': maximum}
        cached_groups = self.m.get('fragment_tm', {}).get(key) or []
        ph_groups = self.m.get('fragment_placeholder_maps', {}).get(key) or []
        senses = []
        frag_prov = []
        missing = []
        sense_tags = {}
        for gi, group in enumerate(groups):
            cached = cached_groups[gi] if gi < len(cached_groups) else []
            phs = ph_groups[gi] if gi < len(ph_groups) else []
            uncached = [i for i in range(len(group)) if i >= len(cached) or not cached[i]]
            resolved, unresolved = self.heal_group(key, group, uncached,
                                                   'heal:%s#g%d' % (key, gi + 1), budget)
            missing.extend('g%d:f%d' % (gi + 1, i) for i in unresolved)
            for index, fragment in enumerate(group):
                frag_senses = []
                if index < len(cached) and cached[index]:
                    frag_senses = cached[index]
                elif index in resolved:
                    card = restore_card(resolved[index], self.m['field'],
                                        phs[index] if index < len(phs) else [])
                    frag_senses = [sense for record in card.get('records') or []
                                   for sense in record.get('senses') or []]
                    if fragment.get('fsha') and frag_senses:
                        frag_prov.append({'fsha': fragment['fsha'], 'senses': frag_senses})
                for sense in frag_senses:
                    source_ord = fragment.get('si')
                    if source_ord is not None:
                        if source_ord in sense_tags:
                            sense['tag'] = sense_tags[source_ord]
                        else:
                            sense_tags[source_ord] = sense.get('tag')
                    senses.append(sense)
        if not senses:
            self.note(key, 'selfheal-nothing-resolved')
            return None
        card = {'key1': key, 'records': [{'senses': senses}]}
        if frag_prov:
            card['frag_prov'] = frag_prov
        if missing:
            card.update({'partial': True, 'missing_fragments': missing,
                         'missing_groups': len({item.split(':')[0] for item in missing}),
                         'total_groups': len(groups)})
        else:
            inp = self.m['inputs'][key]
            ls_count, sk_count = count_card(card, '<ls'), count_card(card, '{#')
            if ls_count != inp['ls'] or sk_count != inp['sk']:
                self.note(key, 'stitched-fidelity-reject: <ls> %d/%d, {# %d/%d' %
                          (ls_count, inp['ls'], sk_count, inp['sk']))
                return None
        return card

    def run_all(self):
        rows = []
        healed = 0
        presplit = set(self.m.get('presplit_keys') or [])
        for index, batch in enumerate(self.m.get('batches') or []):
            resolved, pending = self.resolve_group(batch, 'b%d' % index)
            for key in pending:
                card = self.self_heal(key)
                if card:
                    resolved[key] = card
                    healed += 1
            for key in batch:
                row = {'key': key, 'card': resolved.get(key), 'judge': None,
                       'judge_sonnet': None, 'escalated': key in pending and key in resolved}
                if not row['card']:
                    row['error'] = self.failures.get(key, 'unknown')
                rows.append(row)
        for key in self.m.get('presplit_keys') or []:
            card = self.self_heal(key)
            row = {'key': key, 'card': card, 'judge': None, 'judge_sonnet': None,
                   'escalated': bool(card), 'presplit': True}
            if not card:
                row['error'] = self.failures.get(key, 'unknown')
            else:
                healed += 1
            rows.append(row)
        return rows, healed, len(presplit)


def execute(manifest, claude='claude', timeout=7200, runner=None):
    if manifest.get('schema') != 'pwg.headless_execution_manifest.v1':
        raise ValueError('unsupported manifest schema')
    engine = HeadlessEngine(manifest, claude, timeout, runner)
    try:
        results, healed, presplit = engine.run_all()
    except HardFailure as exc:
        return None, {'classification': exc.classification, 'error': exc.detail,
                      'attempts': engine.attempts}, exc.code
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
               'healed': healed, 'presplit': presplit,
               'tm': sum(bool(row.get('tm')) for row in results),
               'degenerate_passthrough': sum(bool(row.get('degenerate_passthrough')) for row in results),
               'null_keys': list(failures), 'partial_keys': [], 'failures': failures,
               'translate_agents_spent': engine.translate_calls,
               'heal_agents_spent': engine.heal_calls,
               'kill_timeouts': engine.kill_timeouts, 'conn_errors': engine.conn_errors,
               'headless_attempts': engine.attempts}
    payload = {'meta': manifest['meta'], 'summary': summary, 'results': results}
    status = {'classification': 'completed_with_residuals' if failures else 'success',
              'attempts': engine.attempts, 'null_keys': list(failures)}
    return payload, status, 0


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
