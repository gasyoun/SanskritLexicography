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
_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
from proc_tree import run_tree_kill, terminate_tree, windows_hidden_flags  # noqa: E402  (shared D-J tree-kill runner)
import card_fields  # noqa: E402  (C-01: the one restore/promote field set, shared with the JS lane)
from execution_contract import ActiveCallClaim, SCHEMA_V1, SCHEMA_V2, validate_manifest, validate_profile  # noqa: E402

AUTH_RE = re.compile(r'401|authentication|not logged in|invalid.*credential', re.I)
RATE_RE = re.compile(r'429|rate.?limit|usage limit|too many requests', re.I)
CONN_RE = re.compile(r'connection closed|econnreset|socket hang up|network error', re.I)
EXIT_AUTH = 20
EXIT_RATE_LIMIT = 21
EXIT_TIMEOUT = 22
EXIT_MALFORMED = 23
EXIT_CONTENT = 24

# R4 (C-15): the hard per-call subprocess ceiling. "NOTHING runs past 3 min (MG)". The bare
# operator default was 7200 s -- 40x this -- because `budgets.timeout_ceil_ms` was never read.
HARD_TIMEOUT_MS = 180000


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
    resolved = claude_bin
    if not os.path.dirname(claude_bin):
        resolved = shutil.which(claude_bin)
        if not resolved:
            raise FileNotFoundError('Claude CLI %r is not resolvable on PATH' % claude_bin)
    if os.name != 'nt':
        return [resolved]
    if os.path.splitext(resolved)[1].lower() in ('.exe', '.com'):
        return [resolved]
    node = shutil.which('node')
    shim_dir = os.path.dirname(os.path.abspath(resolved)) or '.'
    base = os.path.join(shim_dir, 'node_modules', '@anthropic-ai', 'claude-code')
    entries = sorted(glob.glob(os.path.join(base, 'cli*.cjs')) +
                     glob.glob(os.path.join(base, 'cli*.js')))
    if node and entries:
        return [node, entries[0]]
    raise FileNotFoundError('refusing unresolved Windows Claude shim %r; Node CLI entry missing'
                            % resolved)


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


def restore_text(text, placeholders, unmapped=None):
    """Unmask `{Tn}` against `placeholders`.

    C-42: an index outside the map still returns the token verbatim (changing that is a
    behaviour change this correction does not make), but it is now COUNTED into `unmapped`
    when a caller supplies a sink. The silent pass-through is how a raw `{T196}` reached the
    canonical store on a card that reported success: the article is masked WHOLE (235+
    placeholders) but restored per-subcard against a subcard-local map, so a high global
    index maps nothing. Counting is what lets `normalize_batch` gate on zero.
    """
    def repl(match):
        idx = int(match.group(1)) - 1
        if 0 <= idx < len(placeholders):
            return placeholders[idx]
        if unmapped is not None:
            unmapped.append(match.group(0))
        return match.group(0)
    return re.sub(r'\{T(\d+)\}', repl, text or '')


def restore_card(card, field, placeholders, unmapped=None):
    """Unmask every field the promote path reads -- the set is `card_fields`, not a local list.

    C-01: this used to restore three things (record.grammar, sense.german, sense.<field>)
    while `promote_final_cards.rows_for` read six, so card.iast / record.h / sense.tag /
    sense.differentia were promoted with their `{Tn}` intact -- 670 store rows, 223 of them
    a raw `{Tn}` in the HEADWORD. The lists are now one constant, pinned by
    `test_restore_covers_every_promoted_field`.

    Deliberate delta from the old loop: a field is restored only when it is a `str`. The old
    code tested key-presence and passed `text or ''`, silently rewriting a `None` grammar to
    `''`. Extending that to `h` would have laundered the 468 known `h is None` rows into
    empty strings -- destroying the very signal C-02 is diagnosed by. A non-str field is now
    left exactly as found.
    """
    return card_fields.restore_card_fields(
        card, field, lambda text: restore_text(text, placeholders, unmapped))


def stitch_records(senses, owners):
    """Rebuild `records[]` from healed senses, preserving each sense's `(h, grammar)` owner.

    C-02: the stitch used to emit a single `{'senses': senses}` record -- no `h`, no
    `grammar` -- which violates `schemas/pwg_ru_final_card.schema.json` (`record.required =
    {h, grammar, senses}`) and made the promote path write `h: null`. It also collapsed real
    homonyms: 79 sub-cards legitimately carry more than one distinct `h`, so one flat record
    cannot represent them.

    Consecutive senses sharing an owner stay in one record; a change of owner opens the next.
    Order is preserved exactly, so the whole-card `<ls>`/`{#` fidelity counts are unchanged.
    """
    records = []
    for sense, owner in zip(senses, owners):
        if not records or records[-1]['_owner'] != owner:
            rec_h, rec_grammar = owner
            records.append({'_owner': owner, 'h': rec_h, 'grammar': rec_grammar, 'senses': []})
        records[-1]['senses'].append(sense)
    for record in records:
        record.pop('_owner', None)
    return records


def count_card(card, needle):
    """Count `needle` across the card's `german` senses.

    DELIBERATELY still `german`-only. The C-02 boundary asks to "make count_card/countOf see
    record-level fields", but that is wrong AT THIS SITE and its own fixture proves it: this
    count is compared against `inp['ls']`/`inp['sk']`, which are SOURCE-occurrence counts
    (`raw.count('<ls')`). One source token echoed into both `grammar` and `german` -- exactly
    what `headless_worker_selftest.success_runner` builds, `{T1}` in both -- then counts 2
    against a denominator of 1 and the card is rejected as a fidelity failure.

    Adding record-level text belongs with the token-MULTISET guards (C-17, Step 6), whose
    denominator really is the whole skeleton. Restoring `grammar` on the stitch lane (C-02)
    leaves this count unchanged, because stitched cards previously carried no `grammar` term
    at all -- so historical comparisons stay valid.
    """
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
            unmapped = []
            card = restore_card(card, manifest['field'],
                                manifest['placeholder_maps'].get(key, []), unmapped)
            inp = manifest['inputs'][key]
            if count_card(card, '<ls') != inp['ls'] or count_card(card, '{#') != inp['sk']:
                error = 'fidelity-reject'
                card = None
            elif unmapped:
                # C-42: an out-of-range {Tn} maps nothing and cannot be recovered downstream.
                error = 'unmapped-token-reject'
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
    # C-17: collect {Tn} from EVERY source-mirror field (record.grammar + sense.german), driven
    # by the one `card_fields.TOKEN_FIDELITY_FIELDS` tuple the JS `cardTokens` also uses. The old
    # body read `sense.german` only, so a grammar-{Tn} card counted fewer tokens than its skeleton
    # and was falsely `fragment-fidelity-reject`ed on this lane while JS accepted it.
    record_fields = [n for lvl, n in card_fields.TOKEN_FIDELITY_FIELDS if lvl == 'record']
    sense_fields = [n for lvl, n in card_fields.TOKEN_FIDELITY_FIELDS if lvl == 'sense']
    tokens = []
    for record in card.get('records') or []:
        for name in record_fields:
            tokens.extend(re.findall(r'\{T\d+\}', record.get(name) or ''))
        for sense in record.get('senses') or []:
            for name in sense_fields:
                tokens.extend(re.findall(r'\{T\d+\}', sense.get(name) or ''))
    return collections.Counter(tokens)


# run_tree_kill / terminate_tree moved to proc_tree (shared D-J runner); imported above.


class HeadlessEngine:
    def __init__(self, manifest, claude, timeout, runner, max_agents_override=None):
        self.m = manifest
        self.claude = claude
        budgets = manifest.get('budgets') or {}
        # R4 (C-15): clamp every subprocess to min(operator, budgets.timeout_ceil_ms, HARD).
        eff_ms = min(int(timeout) * 1000, HARD_TIMEOUT_MS)
        ceil_ms = budgets.get('timeout_ceil_ms')
        if ceil_ms:
            eff_ms = min(eff_ms, int(ceil_ms))
        self.timeout = eff_ms / 1000.0
        self.run = runner or run_tree_kill
        self.attempts = []
        self.failures = {}
        self.translate_calls = 0
        self.heal_calls = 0
        self.kill_timeouts = 0
        self.conn_errors = 0
        # R3 (C-12/C-13): the manifest agent budgets were write-only -- emitted, validated-adjacent,
        # never read by the executor. Enforce them here. None = unbounded (back-compat). The
        # `--max-agents` override caps the TOTAL across both lanes and binds even without budgets.
        self.max_translate_agents = budgets.get('max_translate_agents')
        self.max_heal_agents = budgets.get('max_heal_agents')
        self.max_total_agents = budgets.get('max_agents')
        if max_agents_override is not None:
            self.max_total_agents = (max_agents_override if self.max_total_agents is None
                                     else min(self.max_total_agents, max_agents_override))
        self.budget_stops = 0
        # R5 (C-25): the CLI wrapper's usage/cost were parsed then dropped at the call site, so
        # actual spend was unreconcilable and a priced run ended STOP_COST_UNEVALUABLE. Accumulate.
        self.usage = {'input_tokens': 0, 'output_tokens': 0, 'cache_read_tokens': 0,
                      'cache_creation_tokens': 0, 'subagent_tokens': 0,
                      'observed_cost_usd': 0.0, 'cost_evaluable': True, 'priced_calls': 0,
                      'missing_usage_calls': 0}

    def note(self, key, error):
        self.failures[key] = str(error)[:300]

    def _accumulate_usage(self, wrapper):
        """R5: fold one CLI wrapper's usage/cost into the running totals. A missing usage or cost
        field flips `cost_evaluable` False (so a real call is never priced at $0) instead of being
        silently dropped. `subagent_tokens` is the field the economy pricer reads."""
        self.usage['priced_calls'] += 1
        u = wrapper.get('usage') if isinstance(wrapper, dict) else None
        if isinstance(u, dict):
            # These are disjoint Claude usage fields; sum them, never overwrite. Prior calls'
            # totals are retained even when a later call arrives with no usage.
            self.usage['input_tokens'] += int(u.get('input_tokens') or 0)
            self.usage['output_tokens'] += int(u.get('output_tokens') or 0)
            self.usage['cache_read_tokens'] += int(u.get('cache_read_input_tokens') or 0)
            self.usage['cache_creation_tokens'] += int(u.get('cache_creation_input_tokens') or 0)
        else:
            # Retain known telemetry; mark the whole run unpriceable and count the gap.
            self.usage['cost_evaluable'] = False
            self.usage['missing_usage_calls'] += 1
        cost = wrapper.get('total_cost_usd') if isinstance(wrapper, dict) else None
        if cost is None:
            self.usage['cost_evaluable'] = False
        else:
            # observed_cost_usd stays authoritative (accumulated CLI cost), not recomputed from tokens.
            self.usage['observed_cost_usd'] += float(cost)
        self.usage['subagent_tokens'] = (
            self.usage['input_tokens'] + self.usage['output_tokens']
            + self.usage['cache_read_tokens'] + self.usage['cache_creation_tokens'])

    def _budget_ok(self, heal):
        """R3: True while another spawn on this lane stays within the manifest agent budgets.
        Checked BEFORE the counter increments and the subprocess spawns, so `translate_calls` /
        `heal_calls` can never exceed their ceilings. None = unbounded (back-compat)."""
        if (self.max_total_agents is not None and
                self.translate_calls + self.heal_calls >= self.max_total_agents):
            return False
        if heal:
            return self.max_heal_agents is None or self.heal_calls < self.max_heal_agents
        return self.max_translate_agents is None or self.translate_calls < self.max_translate_agents

    def call(self, prompt, label, keys, heal=False):
        if not self._budget_ok(heal):
            # R3: a refused call consumes NO spawn and returns a typed stop reason.
            self.budget_stops += 1
            return None, 'budget_exceeded:%s' % ('heal' if heal else 'translate')
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
            structured, wrapper = extract_structured(proc.stdout)
        except ValueError as exc:
            self.attempts.append({'label': label, 'keys': keys, 'returncode': 0,
                                  'elapsed_ms': elapsed, 'classification': 'malformed_output'})
            return None, 'malformed_output:%s' % exc
        self._accumulate_usage(wrapper)     # R5: capture spend instead of discarding it
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
                if error.startswith('budget_exceeded'):
                    break                    # R3: retrying/bisecting would only refuse again
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
                self.m.get('runtime', {}).get('binary_split', True) and
                self._budget_ok(False)):
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
                if error.startswith('budget_exceeded'):
                    break                    # R3: heal ceiling hit -- stop, do not bisect
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
        if (len(pending) > 1 and not no_bisect and budget['spent'] < budget['max']
                and self._budget_ok(True)):
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
        owners = []          # C-02: parallel to `senses` -- the (h, grammar) each came from
        unmapped = []        # C-42: {Tn} indices that map nothing, instead of a silent pass
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
                # C-02: keep each sense's OWNING record. The old comprehension here flattened
                # `records -> senses` and dropped `record` itself, so the stitch below had no
                # `h`/`grammar` left in scope to emit and every promoted row read `h: null`
                # (468 rows / 20 sub-cards). `h` is free lexicographic text ("2. bhid",
                # "PW 3 (с anu, отсылка к entry 5)"), so a dropped one cannot be reconstructed
                # later -- it has to survive the flatten.
                frag_records = []
                if index < len(cached) and cached[index]:
                    # R6: a served frag-TM slot is v2 -- it carries the PER-SENSE owner harvested at
                    # the fresh-resolve run. v1 (ownerless) rows are a serve-time cache MISS (the
                    # gview build drops them), so a served slot restores each sense's real
                    # (h, grammar) instead of the C-02 residual null owner that regenerated null-`h`
                    # rows on every warm run.
                    slot = cached[index]
                    c_senses = slot.get('senses') or []
                    c_owners = slot.get('owners') or []
                    frag_records = [((c_owners[j] or [None, None])[0] if j < len(c_owners) else None,
                                     (c_owners[j] or [None, None])[1] if j < len(c_owners) else None,
                                     [c_senses[j]])
                                    for j in range(len(c_senses))]
                elif index in resolved:
                    card = restore_card(resolved[index], self.m['field'],
                                        phs[index] if index < len(phs) else [], unmapped)
                    frag_records = [(record.get('h'), record.get('grammar'),
                                     record.get('senses') or [])
                                    for record in card.get('records') or []]
                    frag_senses = [sense for _, _, group in frag_records for sense in group]
                    # R6: carry the PER-SENSE owner into frag_prov so a later warm-cache stitch of
                    # this fragment restores each sense's (h, grammar) instead of a null owner.
                    frag_owners = [[rh, rg] for rh, rg, group in frag_records for _ in group]
                    if fragment.get('fsha') and frag_senses:
                        frag_prov.append({'fsha': fragment['fsha'], 'senses': frag_senses,
                                          'owners': frag_owners})
                for rec_h, rec_grammar, group in frag_records:
                    for sense in group:
                        source_ord = fragment.get('si')
                        if source_ord is not None:
                            if source_ord in sense_tags:
                                sense['tag'] = sense_tags[source_ord]
                            else:
                                sense_tags[source_ord] = sense.get('tag')
                        senses.append(sense)
                        owners.append((rec_h, rec_grammar))
        if not senses:
            self.note(key, 'selfheal-nothing-resolved')
            return None
        card = {'key1': key, 'records': stitch_records(senses, owners)}
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
        # C-42: a {Tn} whose index maps nothing used to be written through verbatim on a card
        # that reported success -- that is how `ban_d~~h0_11_ni` and `ban_d~~h0_21_upasam_0`
        # reached the canonical store carrying a raw {T196}/{T235}. The token is unrecoverable
        # by construction (the index addresses a whole-article map the sub-card never had), so
        # refuse the card instead of promoting a known-corrupt one.
        if unmapped:
            self.note(key, 'unmapped-token-reject: %d out-of-range placeholder(s): %s'
                      % (len(unmapped), ', '.join(sorted(set(unmapped))[:6])))
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


def execute(manifest, claude='claude', timeout=7200, runner=None, max_agents_override=None):
    validate_manifest(manifest, require_v2=False)
    engine = HeadlessEngine(manifest, claude, timeout, runner, max_agents_override)
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
               'budget_stops': engine.budget_stops,
               'usage': engine.usage,
               'kill_timeouts': engine.kill_timeouts, 'conn_errors': engine.conn_errors,
               'headless_attempts': engine.attempts}
    output_meta = dict(manifest['meta'])
    output_meta['execution_manifest_schema'] = manifest.get('schema')
    output_meta['execution'] = manifest.get('execution')
    output_meta['provenance_classes'] = manifest.get('key_provenance')
    payload = {'meta': output_meta, 'summary': summary, 'results': results}
    status = {'classification': 'completed_with_residuals' if failures else 'success',
              'attempts': engine.attempts, 'null_keys': list(failures)}
    return payload, status, 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('manifest')
    ap.add_argument('--output', required=True)
    ap.add_argument('--status-out', required=True)
    ap.add_argument('--claude-bin', default='claude')
    ap.add_argument('--only-profile', help='required profile-slot assertion for live v2 execution')
    ap.add_argument('--allow-historical-v1', action='store_true',
                    help='read-only/historical replay only; v1 is not a production contract')
    ap.add_argument('--timeout', type=int, default=7200)
    ap.add_argument('--max-agents', type=int, default=None,
                    help='R3: hard cap on total model spawns (translate+heal); binds even when '
                         'the manifest omits budgets, and caps the manifest budget when both set')
    args = ap.parse_args(argv)
    manifest_hash = sha256_path(args.manifest)
    with open(args.manifest, encoding='utf-8') as f:
        manifest = json.load(f)
    try:
        if manifest.get('schema') == SCHEMA_V1:
            if not args.allow_historical_v1:
                raise ValueError('v1 manifest is historical-only; production requires %s' % SCHEMA_V2)
            payload, status, code = execute(manifest, args.claude_bin, args.timeout,
                                            max_agents_override=args.max_agents)
        else:
            config_dir = os.environ.get('CLAUDE_CONFIG_DIR')
            if not config_dir:
                raise ValueError('CLAUDE_CONFIG_DIR is required for manifest v2')
            validate_profile(manifest, config_dir, args.only_profile)
            with ActiveCallClaim(manifest['execution']['config_dir_fingerprint']):
                payload, status, code = execute(manifest, args.claude_bin, args.timeout,
                                            max_agents_override=args.max_agents)
    except (OSError, RuntimeError, ValueError) as exc:
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
