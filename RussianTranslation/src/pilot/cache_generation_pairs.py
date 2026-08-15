#!/usr/bin/env python
"""H2703 — exact-request DeepSeek Pro generation cold/warm pairs.

Compiles one sealed v0 request per frozen H2676 Q3 card, schedules each card
twice (cold then warm, contiguous), reserves every billable attempt, and
dispatches at most 44 base calls. Controller-feedback retries are undeclared
variants and are refused. Transport retries of the sealed request are opt-in
and count against the ceiling; the sealed default is one HTTP call per slot
so 22 pairs can complete inside 44.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
H1210 = os.path.join(HERE, 'h1210')
H1209 = os.path.join(HERE, 'h1209')
for path in (HERE, H1210, H1209):
    if path not in sys.path:
        sys.path.insert(0, path)
SRC = os.path.dirname(HERE)
RT = os.path.dirname(SRC)
REPO = os.path.dirname(RT)

import cache_baseline_freeze as freeze  # noqa: E402
import cache_economy_report as report  # noqa: E402
import cache_event_ledger as ledger  # noqa: E402
import cache_identity as ident  # noqa: E402
import cache_pair_compare as pair_compare  # noqa: E402
import cache_scheduler as sched  # noqa: E402
import call_reservation as reserve  # noqa: E402
import deepseek_arm as ds_arm  # noqa: E402
import det_gate  # noqa: E402
import prompt_compiler as compiler  # noqa: E402
import build_args  # noqa: E402

H2676_DIR = os.path.join(RT, 'experiments', 'H2676_v4pro_q3_rematch')
EXP_DIR = os.path.join(RT, 'experiments', 'pwg_cache_economy', 'h2703_generation')
DEFAULT_ENV = os.path.join(os.path.dirname(REPO), 'ORS-FAQ', '.env')

N_PAIRS = 22
MAX_BASE_CALLS = 44
PARSEABLE_MIN = 42
REQUESTED_MODEL = 'deepseek-v4-pro'
PROVIDER = 'deepseek'
REASONING_EFFORT = 'high'
MAX_TOKENS = 32768
TEMPERATURE = 0.2
COST_CEILING_USD = 5.0
TIMEOUT_S = 1800
RUN_ID = 'h2703-generation-q3-pairs'


class GateStop(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def worker_schema(manifest):
    return {
        'type': 'object',
        'additionalProperties': False,
        'required': ['card', 'self_report'],
        'properties': {
            'card': {'$ref': '#/$defs/card'},
            'self_report': build_args.SELF_REPORT,
        },
        '$defs': manifest['output_schema']['$defs'],
    }


def load_cohort():
    sample = json.loads(open(
        os.path.join(H2676_DIR, 'sample_keys.json'), encoding='utf-8').read())
    keymap = json.loads(open(
        os.path.join(H2676_DIR, 'payload_key_map.json'), encoding='utf-8').read())
    payload = json.loads(open(
        os.path.join(H2676_DIR, 'slice_payload.json'), encoding='utf-8').read())
    manifest = json.loads(open(
        os.path.join(H2676_DIR, 'h2676.manifest.json'), encoding='utf-8').read())
    order = list(keymap['main_payload_keys'])
    if len(order) != N_PAIRS:
        raise GateStop('cohort key count %d != %d' % (len(order), N_PAIRS))
    slp = list(sample['main_arm']['keys'])
    if len(slp) != N_PAIRS:
        raise GateStop('sample_keys count %d != %d' % (len(slp), N_PAIRS))
    by_key = {card['key1']: card for card in payload['cards']}
    missing = [key for key in order if key not in by_key]
    if missing:
        raise GateStop('payload missing keys: %s' % missing)
    cards = [by_key[key] for key in order]
    return {
        'sample': sample,
        'keymap': keymap,
        'payload': payload,
        'manifest': manifest,
        'cards': cards,
        'order': order,
        'slp': slp,
        'common': payload['prompt_common'],
        'schema': worker_schema(manifest),
        'field': manifest.get('field') or 'russian',
    }


def dependency_hashes(baseline):
    tracked = {row['path']: row.get('sha256') for row in baseline.get('tracked') or []}
    canonical = {row['label']: row.get('sha256') for row in baseline.get('canonical') or []}
    return {
        'tm': canonical.get('tm_card'),
        'denylist': canonical.get('tm_denylist'),
        'h2676_sample': tracked.get(
            'RussianTranslation/experiments/H2676_v4pro_q3_rematch/sample_keys.json'),
        'h2676_manifest': tracked.get(
            'RussianTranslation/experiments/H2676_v4pro_q3_rematch/h2676.manifest.json'),
        'h2676_payload': tracked.get(
            'RussianTranslation/experiments/H2676_v4pro_q3_rematch/slice_payload.json'),
        'det_gate': tracked.get('RussianTranslation/src/pilot/h1210/det_gate.py'),
    }


def compile_card(card, common, schema, extra):
    compiled = compiler.compile_deepseek_v0(card, common, schema, extra=extra)
    compiled['key1'] = card['key1']
    compiled['card'] = card
    return compiled


def compile_cohort(cohort, baseline):
    extra = {
        'provider': PROVIDER,
        'requested_model': REQUESTED_MODEL,
        'generation_parameters': {
            'temperature': TEMPERATURE,
            'max_tokens': MAX_TOKENS,
            'response_format': {'type': 'json_object'},
            'reasoning_effort': REASONING_EFFORT,
        },
        'dependency_hashes': dependency_hashes(baseline),
    }
    compiled = []
    for card in cohort['cards']:
        compiled.append(compile_card(
            card, cohort['common'], cohort['schema'], extra))
    ids = [row['request']['request_id'] for row in compiled]
    if len(set(ids)) != len(ids):
        raise GateStop('compiled request identities are not unique')
    prefixes = {row['bundle']['stable_prefix_sha256'] for row in compiled}
    return compiled, extra, prefixes


def expand_pairs(compiled):
    """Prefix-group the 22 cards, then emit cold+warm slots per card."""
    items = []
    for index, row in enumerate(compiled):
        items.append({
            'provider': row['bundle']['provider'],
            'requested_model': row['bundle']['requested_model'],
            'stable_prefix_sha256': row['bundle']['stable_prefix_sha256'],
            'request_id': row['request']['request_id'],
            'source_ordinal': index,
            'key1': row['key1'],
        })
    ordered = sched.schedule(items)
    slots = []
    for pair_index, item in enumerate(ordered):
        for position, label in enumerate(('cold', 'warm')):
            slot = dict(item)
            slot['cold_warm'] = label
            slot['pair_index'] = pair_index
            slot['pair_position'] = position
            slot['slot_ordinal'] = pair_index * 2 + position
            slots.append(slot)
    if len(slots) != MAX_BASE_CALLS:
        raise GateStop('pair expansion produced %d slots' % len(slots))
    return ordered, slots


def write_freeze(path, baseline):
    body = dict(baseline)
    body['handoff'] = 'H2703'
    body['experiment'] = 'exact-request generation cold/warm pairs'
    body['n_pairs'] = N_PAIRS
    body['max_base_calls'] = MAX_BASE_CALLS
    body['requested_model'] = REQUESTED_MODEL
    body['reasoning_effort'] = REASONING_EFFORT
    body['max_tokens'] = MAX_TOKENS
    body['retry_policy'] = 'exact_sealed_transport_only'
    body['max_transport_attempts_per_slot'] = 1
    body['cost_ceiling_usd'] = COST_CEILING_USD
    body.pop('manifest_sha256', None)
    body['manifest_sha256'] = ident.sha256_bytes(ident.canonical_bytes(body))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(ident.canonical_dumps(body))
    return body


def canonical_snapshot(baseline=None):
    """Rehash only the four canonical files. Do not reread the whole tracked tree."""
    rows = (baseline or {}).get('canonical') if baseline else None
    if not rows:
        payload = freeze.build_manifest()
        rows = payload.get('canonical') or []
    out = {}
    for row in rows:
        label = row.get('label')
        path = row.get('resolved')
        if not label:
            continue
        if path and os.path.isfile(path):
            out[label] = ident.sha256_file(path)
        else:
            out[label] = row.get('sha256')
    return out


def usage_from_rec(rec):
    if not rec or rec.get('error'):
        return None, 'transport_error'
    usage = {
        'prompt_tokens': rec.get('prompt_tokens'),
        'completion_tokens': rec.get('completion_tokens'),
        'input_tokens': rec.get('prompt_tokens'),
        'output_tokens': rec.get('completion_tokens'),
        'cache_hit_tokens': rec.get('cache_hit_tokens'),
        'cache_miss_tokens': rec.get('cache_miss_tokens'),
        'reasoning_tokens': rec.get('reasoning_tokens'),
    }
    cleaned, reason = ledger.normalize_usage(usage)
    return cleaned, reason


def rec_cost_usd(rec, usage):
    if usage is None:
        return None, False
    card = rec.get('price_card')
    _, prices = ds_arm.prices_for(REQUESTED_MODEL, card=card)
    miss = usage.get('cache_miss_tokens') or 0
    hit = usage.get('cache_hit_tokens') or 0
    out = usage.get('completion_tokens') or 0
    if not (miss or hit):
        miss = usage.get('prompt_tokens') or 0
    usd = (miss / 1e6 * prices['cache_miss_in']
           + hit / 1e6 * prices['cache_hit_in']
           + out / 1e6 * prices['out'])
    return round(usd, 8), True


def parse_and_gate(text, card, field):
    if not text:
        return {
            'parseable': False,
            'parse_error': 'empty_content',
            'obj': None,
            'card_out': None,
            'det': None,
            'det_clean': False,
            'final_status': 'worker-null-death',
        }
    try:
        obj, repair = ds_arm.extract_json(text)
    except ValueError as exc:
        return {
            'parseable': False,
            'parse_error': str(exc),
            'obj': None,
            'card_out': None,
            'det': None,
            'det_clean': False,
            'final_status': 'unparseable',
        }
    out_card = obj.get('card') if isinstance(obj, dict) else None
    if not isinstance(out_card, dict):
        return {
            'parseable': False,
            'parse_error': 'no_card_object',
            'obj': obj,
            'card_out': None,
            'det': None,
            'det_clean': False,
            'final_status': 'unparseable',
            'repair': repair,
        }
    det = det_gate.deterministic_audit(out_card, card, field)
    issues = list(det.get('issues') or [])
    return {
        'parseable': True,
        'parse_error': None,
        'obj': obj,
        'card_out': out_card,
        'det': det,
        'det_clean': not issues,
        'final_status': 'det_clean' if not issues else 'det_issues',
        'repair': repair,
    }


def expand_and_check_pairs(slots):
    by_pair = {}
    for slot in slots:
        by_pair.setdefault(slot['request_id'], []).append(slot)
    for rid, members in by_pair.items():
        if len(members) != 2:
            raise GateStop('request %s has %d slots' % (rid, len(members)))
        labels = [m['cold_warm'] for m in members]
        if labels != ['cold', 'warm']:
            raise GateStop('pair %s not contiguous cold/warm: %s' % (rid, labels))
        if members[0]['slot_ordinal'] + 1 != members[1]['slot_ordinal']:
            raise GateStop('pair %s slots are not contiguous' % rid)


class PairRunner:
    def __init__(self, run_dir, compiled, slots, cohort, freeze_body):
        self.run_dir = os.path.abspath(run_dir)
        self.compiled = {row['request']['request_id']: row for row in compiled}
        self.slots = slots
        self.cohort = cohort
        self.freeze_body = freeze_body
        self.led = ledger.EventLedger(self.run_dir)
        self.reservations = reserve.CallReservationLedger(
            os.path.join(self.run_dir, 'call_reservations.json'),
            RUN_ID, MAX_BASE_CALLS)
        self.canonical_before = canonical_snapshot(freeze_body)
        self.ds = None
        self.spent_usd = 0.0
        self.parseable = 0
        self.unparseable = 0
        self.slot_outputs = {}

    def seal(self, source_commit):
        cohort_sha = ident.sha256_file(os.path.join(
            H2676_DIR, 'sample_keys.json'))
        price_card = ds_arm.price_card_name()
        spec = {
            'run_id': RUN_ID,
            'source_commit': source_commit,
            'baseline_manifest_sha256': self.freeze_body.get('manifest_sha256'),
            'cohort_sha256': cohort_sha,
            'pricing_version': 'deepseek-v4-pro/%s' % price_card,
            'n': N_PAIRS,
            'call_ceiling': MAX_BASE_CALLS,
            'cost_ceiling_usd': COST_CEILING_USD,
            'schedule_window': (
                'pre-1608-authorized' if price_card == 'pre-1608'
                else 'after-1608-offpeak-only'
            ),
            'requested_model': REQUESTED_MODEL,
            'provider': PROVIDER,
            'retry_ladder': ['v0'],
            'acceptance': {
                'parseable_min': PARSEABLE_MIN,
                'parseable_denom': MAX_BASE_CALLS,
                'n_pairs': N_PAIRS,
                'served_model': REQUESTED_MODEL,
                'promotable': False,
                'controller_feedback_retries': False,
                'max_transport_attempts_per_slot': 1,
                'h2676_usd_per_clean': 0.01991,
                'h2676_det_clean': 21,
            },
            'schedule': [
                {
                    'slot_ordinal': slot['slot_ordinal'],
                    'source_ordinal': slot['source_ordinal'],
                    'request_id': slot['request_id'],
                    'cold_warm': slot['cold_warm'],
                    'key1': slot['key1'],
                    'prefix_group_id': slot['prefix_group_id'],
                }
                for slot in self.slots
            ],
        }
        manifest = self.led.seal(spec)
        for row in self.compiled.values():
            self.led.write_request(row['request'])
            self.led.append({
                'kind': 'compile',
                'request_id': row['request']['request_id'],
                'prefix_group_id': sched.prefix_group_id(
                    row['bundle']['provider'],
                    row['bundle']['requested_model'],
                    row['bundle']['stable_prefix_sha256']),
                'source_ordinal': next(
                    s['source_ordinal'] for s in self.slots
                    if s['request_id'] == row['request']['request_id']),
                'requested_model': REQUESTED_MODEL,
                'detail': {
                    'key1': row['key1'],
                    'request_sha256': row['request']['request_id'],
                    'stable_prefix_sha256': row['bundle']['stable_prefix_sha256'],
                    'volatile_tail_sha256': row['bundle']['volatile_tail_sha256'],
                    'promotable': False,
                },
            })
        return manifest

    def load_resume(self):
        events = self.led.load()
        done = ledger.completed_pair_slots(events)
        pending_cold = {}
        for event in events:
            if event.get('kind') != 'terminal_response':
                continue
            rid = event.get('request_id')
            cw = event.get('cold_warm')
            if not rid or cw not in ('cold', 'warm'):
                continue
            detail = event.get('detail') or {}
            slim = {
                'parseable': bool(detail.get('parseable')),
                'det_clean': bool(detail.get('det_clean')),
                'card': detail.get('card') if cw == 'cold' and (rid, 'warm') not in done else None,
            }
            self.slot_outputs[(rid, cw)] = slim
            if slim['parseable']:
                self.parseable += 1
            else:
                self.unparseable += 1
            cost = event.get('observed_cost_usd')
            if event.get('cost_evaluable') and cost is not None:
                self.spent_usd += float(cost)
            if cw == 'cold' and slim['card'] is not None:
                pending_cold[rid] = slim
        for rid, slim in pending_cold.items():
            if (rid, 'warm') in done:
                slim['card'] = None
        return done

    def assert_canonical_unchanged(self):
        now = canonical_snapshot()
        if now != self.canonical_before:
            raise GateStop('canonical_hash_change')

    def connect(self, env_file, dry_run=False):
        env = ds_arm.load_env_file(env_file)
        key = os.environ.get('DEEPSEEK_API_KEY') or env.get('DEEPSEEK_API_KEY')
        base = (os.environ.get('DEEPSEEK_BASE_URL') or env.get('DEEPSEEK_BASE_URL')
                or 'https://api.deepseek.com')
        if dry_run:
            return key, base
        if not key:
            raise GateStop('missing_DEEPSEEK_API_KEY')
        ds_arm.refuse_if_peak()
        self.ds = ds_arm.DeepSeek(
            base, key, REQUESTED_MODEL, MAX_TOKENS,
            timeout=TIMEOUT_S, reasoning_effort=REASONING_EFFORT,
            max_transport_attempts=1)
        return key, base

    def maybe_stop_before(self, slot):
        if self.reservations.spent() >= MAX_BASE_CALLS:
            raise GateStop('call_ceiling')
        if self.spent_usd >= COST_CEILING_USD:
            raise GateStop('cost_ceiling')
        remaining = MAX_BASE_CALLS - (self.parseable + self.unparseable)
        if self.parseable + remaining < PARSEABLE_MIN:
            raise GateStop('parseable_below_95')
        if self.unparseable >= (MAX_BASE_CALLS - PARSEABLE_MIN + 1):
            raise GateStop('parseable_below_95')
        self.assert_canonical_unchanged()
        now = ds_arm.utcnow()
        if now >= ds_arm.PEAK_BILLING_START:
            ds_arm.refuse_if_peak(now)

    def dispatch_slot(self, slot):
        compiled = self.compiled[slot['request_id']]
        bundle = compiled['bundle']
        if bundle['request_id'] != slot['request_id']:
            raise GateStop('undeclared_variant')
        if bundle['requested_model'] != REQUESTED_MODEL:
            raise GateStop('undeclared_variant')
        if bundle.get('promotable') is not False:
            raise GateStop('undeclared_variant')
        env = bundle['provider_envelope']
        if env.get('kind') != 'openai_chat':
            raise GateStop('undeclared_variant')
        self.maybe_stop_before(slot)
        reservation = self.reservations.reserve(
            purpose='h2703-generation',
            profile=REQUESTED_MODEL,
            detail='%s:%s' % (slot['key1'], slot['cold_warm']),
            idempotency_key='%s:%s' % (slot['request_id'], slot['cold_warm']),
        )
        attempt = reservation['ordinal']
        self.led.append({
            'kind': 'dispatch',
            'request_id': slot['request_id'],
            'prefix_group_id': slot['prefix_group_id'],
            'cold_warm': slot['cold_warm'],
            'source_ordinal': slot['source_ordinal'],
            'attempt': attempt,
            'requested_model': REQUESTED_MODEL,
            'detail': {
                'key1': slot['key1'],
                'reservation_id': reservation['reservation_id'],
                'slot_ordinal': slot['slot_ordinal'],
            },
        })
        system = compiled['system']
        user = compiled['user']
        label = '%s:%s' % (slot['key1'], slot['cold_warm'])
        t0 = time.time()
        text, rec = self.ds.chat(system, user, label)
        usage, usage_reason = usage_from_rec(rec)
        cost, evaluable = rec_cost_usd(rec, usage)
        if evaluable and cost is not None:
            self.spent_usd += cost
        served = (rec or {}).get('served_model')
        if text and served and served != REQUESTED_MODEL:
            self.finalize_bad(reservation, rec, usage, usage_reason, cost)
            raise GateStop('served_model_mismatch')
        if text and usage is None:
            self.finalize_bad(reservation, rec, usage, usage_reason, cost)
            raise GateStop('unevaluable_billing')
        parsed = parse_and_gate(text, compiled['card'], self.cohort['field'])
        if parsed['parseable']:
            self.parseable += 1
        else:
            self.unparseable += 1
        blind = None
        if slot['cold_warm'] == 'warm':
            cold_ev = self.slot_outputs.get((slot['request_id'], 'cold'))
            cold_card = (cold_ev or {}).get('card')
            if parsed['card_out'] is not None and cold_card is not None:
                blind = pair_compare.compare_blind(cold_card, parsed['card_out'])
        detail = {
            'key1': slot['key1'],
            'slot_ordinal': slot['slot_ordinal'],
            'reservation_id': reservation['reservation_id'],
            'parseable': parsed['parseable'],
            'parse_error': parsed.get('parse_error'),
            'det_clean': parsed['det_clean'],
            'det': parsed.get('det'),
            'final_status': parsed['final_status'],
            'repair': parsed.get('repair'),
            'transport': (rec or {}).get('transport'),
            'transport_attempts': (rec or {}).get('transport_attempts'),
            'price_card': (rec or {}).get('price_card'),
            'finish_reason': (rec or {}).get('finish_reason'),
            'promotable': False,
            'latency_s': (rec or {}).get('latency_s') or round(time.time() - t0, 2),
            'error': (rec or {}).get('error'),
            'card': parsed.get('card_out'),
            'self_report': (parsed.get('obj') or {}).get('self_report')
            if isinstance(parsed.get('obj'), dict) else None,
            'blind': blind,
            'blind_class': (blind or {}).get('class'),
        }
        event = self.led.append({
            'kind': 'terminal_response',
            'request_id': slot['request_id'],
            'prefix_group_id': slot['prefix_group_id'],
            'cold_warm': slot['cold_warm'],
            'source_ordinal': slot['source_ordinal'],
            'attempt': attempt,
            'transport_outcome': 'ok' if parsed['parseable'] else 'fail',
            'requested_model': REQUESTED_MODEL,
            'served_model': served,
            'usage': usage,
            'usage_reason': usage_reason,
            'pricing_table': (rec or {}).get('price_card'),
            'pricing_version': 'deepseek-v4-pro/%s' % ((rec or {}).get('price_card') or 'unknown'),
            'cost_evaluable': bool(evaluable and usage is not None),
            'observed_cost_usd': cost,
            'latency_ms': int(round(((rec or {}).get('latency_s') or 0) * 1000)),
            'output_termination': (rec or {}).get('finish_reason'),
            'audit_verdict': parsed['final_status'],
            'accepted_artifact': bool(parsed['det_clean'] and parsed['parseable']),
            'detail': detail,
        }, terminal=True)
        self.slot_outputs[(slot['request_id'], slot['cold_warm'])] = {
            'parseable': parsed['parseable'],
            'det_clean': parsed['det_clean'],
            'card': parsed.get('card_out') if slot['cold_warm'] == 'cold' else None,
        }
        if slot['cold_warm'] == 'warm':
            prior = self.slot_outputs.get((slot['request_id'], 'cold'))
            if prior:
                prior['card'] = None
        resp_path = os.path.join(
            self.run_dir, 'responses',
            '%s.%s.json' % (slot['request_id'], slot['cold_warm']))
        publishable = {
            'request_id': slot['request_id'],
            'cold_warm': slot['cold_warm'],
            'key1': slot['key1'],
            'served_model': served,
            'usage': usage,
            'usage_reason': usage_reason,
            'cost_usd': cost,
            'price_card': (rec or {}).get('price_card'),
            'parseable': parsed['parseable'],
            'det_clean': parsed['det_clean'],
            'card': parsed.get('card_out'),
            'blind': blind,
            'promotable': False,
            'raw_rec': {
                k: rec.get(k) for k in rec or {}
                if k not in ('content',)
            },
        }
        with open(resp_path, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(ident.canonical_dumps(publishable))
        telemetry = reserve.normalize_telemetry({
            'cost_evaluable': bool(evaluable and usage is not None),
            'input_tokens': (usage or {}).get('prompt_tokens') or 0,
            'output_tokens': (usage or {}).get('completion_tokens') or 0,
            'cache_read_tokens': (usage or {}).get('cache_hit_tokens') or 0,
            'cache_creation_tokens': (usage or {}).get('cache_miss_tokens') or 0,
            'subagent_tokens': 0,
            'observed_cost_usd': cost or 0,
            'duration_ms': int(round(((rec or {}).get('latency_s') or 0) * 1000)),
        })
        self.reservations.finalize(reservation, telemetry)
        print('  [%02d/44] %-16s %-4s parse=%s clean=%s usd=%s served=%s'
              % (slot['slot_ordinal'] + 1, slot['key1'], slot['cold_warm'],
                 parsed['parseable'], parsed['det_clean'], cost, served),
              flush=True)
        return event

    def finalize_bad(self, reservation, rec, usage, usage_reason, cost):
        telemetry = reserve.normalize_telemetry({
            'cost_evaluable': False,
            'input_tokens': (usage or {}).get('prompt_tokens') or 0,
            'output_tokens': (usage or {}).get('completion_tokens') or 0,
            'cache_read_tokens': (usage or {}).get('cache_hit_tokens') or 0,
            'cache_creation_tokens': (usage or {}).get('cache_miss_tokens') or 0,
            'subagent_tokens': 0,
            'observed_cost_usd': cost or 0,
        })
        self.reservations.finalize(reservation, telemetry)

    def write_summary(self, verdict_note=None):
        summary = report.load_and_derive(
            os.path.join(self.run_dir, 'run.manifest.json'),
            os.path.join(self.run_dir, 'events.jsonl'))
        if verdict_note:
            summary['runner_note'] = verdict_note
        path = os.path.join(self.run_dir, 'summary.json')
        with open(path, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(ident.canonical_dumps(summary))
        return summary


def is_parseable_event(event):
    return bool((event.get('detail') or {}).get('parseable'))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-dir', default=os.path.join(EXP_DIR, 'run'))
    ap.add_argument('--env-file', default=DEFAULT_ENV)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--compile-only', action='store_true')
    args = ap.parse_args(argv)

    os.makedirs(EXP_DIR, exist_ok=True)
    freeze_path = os.path.join(EXP_DIR, 'freeze.json')
    if os.path.isfile(freeze_path):
        with open(freeze_path, encoding='utf-8') as handle:
            freeze_body = json.loads(handle.read())
    else:
        freeze_body = write_freeze(freeze_path, freeze.build_manifest())
    cohort = load_cohort()
    compiled, extra, prefixes = compile_cohort(cohort, freeze_body)
    ordered, slots = expand_pairs(compiled)
    expand_and_check_pairs(slots)
    source_commit = freeze.git_commit() or freeze_body.get('source_commit')
    runner = PairRunner(args.run_dir, compiled, slots, cohort, freeze_body)
    if not os.path.isfile(os.path.join(args.run_dir, 'run.manifest.json')):
        runner.seal(source_commit)
        print('sealed n_pairs=%d slots=%d prefix_groups=%d commit=%s'
              % (N_PAIRS, len(slots), len(prefixes), (source_commit or '')[:12]),
              flush=True)
    done = runner.load_resume()
    if args.dry_run or args.compile_only:
        print('compile-only: %d requests, %d slots, done=%d'
              % (len(compiled), len(slots), len(done)))
        return 0
    runner.connect(args.env_file, dry_run=False)
    note = None
    try:
        for slot in slots:
            key = (slot['request_id'], slot['cold_warm'])
            if key in done:
                continue
            runner.dispatch_slot(slot)
            done.add(key)
        runner.led.append({
            'kind': 'completion',
            'detail': {'slots': len(done)},
        }, terminal=True)
    except GateStop as exc:
        note = exc.reason
        runner.led.append({
            'kind': 'stop',
            'detail': {'reason': exc.reason},
        }, terminal=True)
        print('STOP %s' % exc.reason, flush=True)
    except Exception as exc:
        note = '%s: %s' % (type(exc).__name__, exc)
        try:
            runner.led.append({
                'kind': 'stop',
                'detail': {'reason': 'runner_exception', 'error': note},
            }, terminal=True)
        except Exception:
            pass
        print('STOP runner_exception %s' % note, flush=True)
        raise
    summary = runner.write_summary(note)
    after_path = os.path.join(EXP_DIR, 'canonical_hash_after.json')
    after = freeze.build_manifest()
    after_body = {
        'schema': 'pwg.cache_economy_canonical_rehash.v1',
        'handoff': 'H2703',
        'compared_to': 'experiments/pwg_cache_economy/h2703_generation/freeze.json',
        'before': runner.canonical_before,
        'after': canonical_snapshot(after),
        'equal': canonical_snapshot(after) == runner.canonical_before,
    }
    with open(after_path, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(ident.canonical_dumps(after_body))
    print('verdict=%s parseable=%s unique_clean=%s usd=%s'
          % (summary['generation_lane_verdict'], summary['parseable'],
             summary['unique_clean_cards'], summary['total_usd']),
          flush=True)
    return 0 if summary['generation_lane_verdict'] != 'FAIL' else 2


if __name__ == '__main__':
    raise SystemExit(main())
