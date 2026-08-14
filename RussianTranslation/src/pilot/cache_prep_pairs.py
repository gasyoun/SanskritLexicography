#!/usr/bin/env python
"""H2704 — Flash PREP exact-request cold/warm pairs.

Default: sealed 50-miss subset, 100 base calls, deepseek-v4-flash.
L3 mode: sealed 100 non-Q4/non-monster cards, 200 base calls, USD 25.
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
for path in (HERE, H1210):
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
import cache_prep_census as census  # noqa: E402
import cache_scheduler as sched  # noqa: E402
import call_reservation as reserve  # noqa: E402
import deepseek_arm as ds_arm  # noqa: E402
import prep_pack  # noqa: E402
import prompt_compiler as compiler  # noqa: E402

EXP_DIR = os.path.join(RT, 'experiments', 'pwg_cache_economy', 'h2704_prep')
DEFAULT_ENV = os.path.join(os.path.dirname(REPO), 'ORS-FAQ', '.env')
MAIN_STORE = r'C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src\pwg_ru_translated.jsonl'
MAIN_INPUT = r'C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src\pilot\input'

REQUESTED_MODEL = 'deepseek-v4-flash'
PROVIDER = 'deepseek'
MAX_TOKENS = 32768
TIMEOUT_S = 300


class GateStop(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def load_json(path):
    with open(path, encoding='utf-8') as handle:
        return json.loads(handle.read())


def mode_spec(mode):
    if mode == 'l3':
        return {
            'handoff': 'H2704',
            'mode': 'l3',
            'run_id': 'h2704-l3-flash-pairs',
            'n_pairs': 100,
            'max_base_calls': 200,
            'parseable_min': 190,
            'cost_ceiling_usd': 25.0,
            'manifest_name': 'l3.manifest.json',
            'purpose': 'h2704-l3',
        }
    if mode == 'h2756':
        return {
            'handoff': 'H2756',
            'mode': 'h2756',
            'run_id': 'h2756-prep-flash-pairs',
            'n_pairs': 50,
            'max_base_calls': 100,
            'parseable_min': 95,
            'cost_ceiling_usd': 1.0,
            'manifest_name': 'prep50.manifest.json',
            'purpose': 'h2756-prep',
            'exp_dir': os.path.join(
                RT, 'experiments', 'pwg_cache_economy', 'h2756_flash'),
        }
    return {
        'handoff': 'H2704',
        'mode': 'prep50',
        'run_id': 'h2704-prep-flash-pairs',
        'n_pairs': 50,
        'max_base_calls': 100,
        'parseable_min': 95,
        'cost_ceiling_usd': 5.0,
        'manifest_name': 'prep50.manifest.json',
        'purpose': 'h2704-prep',
    }


def dependency_hashes(baseline):
    tracked = {row['path']: row.get('sha256') for row in baseline.get('tracked') or []}
    canonical = {row['label']: row.get('sha256') for row in baseline.get('canonical') or []}
    return {
        'tm': canonical.get('tm_card'),
        'denylist': canonical.get('tm_denylist'),
        'prep_schema': tracked.get(
            'RussianTranslation/src/pilot/h1210/prep_pack.schema.json'),
        'prep_pack': tracked.get(
            'RussianTranslation/src/pilot/h1210/prep_pack.py'),
        'h2675_report': tracked.get(
            'RussianTranslation/experiments/H2675_w1_prep/REPORT.md'),
    }


def fill_packs(keys):
    store_path = MAIN_STORE
    if not os.path.isfile(store_path):
        store_path = os.path.join(SRC, 'pwg_ru_translated.jsonl')
    store_idx = prep_pack.load_store_index(store_path, wanted=set(keys))
    input_dir = MAIN_INPUT if os.path.isdir(MAIN_INPUT) else None
    packs = []
    for key1 in keys:
        pack = prep_pack.fill_one(
            key1,
            model=REQUESTED_MODEL,
            payload_idx={},
            store_idx=store_idx,
            mode='fill',
            input_dir=input_dir,
            run_gate=True,
            manifest_authoritative=False,
        )
        packs.append(pack)
    return packs


def compile_cohort(keys, baseline):
    extra = {
        'provider': PROVIDER,
        'requested_model': REQUESTED_MODEL,
        'generation_parameters': {
            'max_tokens': MAX_TOKENS,
            'response_format': {'type': 'json_object'},
            'reasoning_effort': None,
        },
        'dependency_hashes': dependency_hashes(baseline),
    }
    packs = fill_packs(keys)
    compiled = []
    for pack in packs:
        row = compiler.compile_prep_flash_v0(pack, extra=extra)
        row['key1'] = pack['key1']
        compiled.append(row)
    ids = [row['request']['request_id'] for row in compiled]
    if len(set(ids)) != len(ids):
        raise GateStop('compiled request identities are not unique')
    prefixes = {row['bundle']['stable_prefix_sha256'] for row in compiled}
    return compiled, extra, prefixes


def expand_pairs(compiled):
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
    return ordered, slots


def expand_and_check_pairs(slots, n_pairs):
    by_pair = {}
    for slot in slots:
        by_pair.setdefault(slot['request_id'], []).append(slot)
    if len(by_pair) != n_pairs:
        raise GateStop('pair count %d != %d' % (len(by_pair), n_pairs))
    for rid, members in by_pair.items():
        if len(members) != 2:
            raise GateStop('request %s has %d slots' % (rid, len(members)))
        labels = [m['cold_warm'] for m in members]
        if labels != ['cold', 'warm']:
            raise GateStop('pair %s not contiguous cold/warm: %s' % (rid, labels))
        if members[0]['slot_ordinal'] + 1 != members[1]['slot_ordinal']:
            raise GateStop('pair %s slots are not contiguous' % rid)


def canonical_snapshot(baseline=None):
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


def parse_prep(text, finish, pack):
    if not text:
        return {
            'parseable': False,
            'parse_error': 'empty_content',
            'obj': None,
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
            'det_clean': False,
            'final_status': 'unparseable',
        }
    parseable = finish != 'length' and isinstance(obj, dict)
    if not parseable:
        return {
            'parseable': False,
            'parse_error': 'length' if finish == 'length' else 'not_object',
            'obj': obj,
            'det_clean': False,
            'final_status': 'unparseable',
            'repair': repair,
        }
    live = dict(pack)
    if obj.get('ru_skeleton') is not None:
        live['ru_skeleton'] = obj.get('ru_skeleton')
    rh = obj.get('route_hint')
    if rh in ('controller_only', 'full_worker', 'prep_only', 'park'):
        live['route_hint'] = rh
    notes = obj.get('hard_flag_notes')
    if isinstance(notes, list):
        live.setdefault('hard_flags', {}).setdefault('notes', [])
        live['hard_flags']['notes'] = list(live['hard_flags'].get('notes') or [])
        live['hard_flags']['notes'].extend(str(n) for n in notes)
    live['store_write'] = False
    live['tm_fence'] = dict(pack.get('tm_fence') or {})
    live['tm_fence']['may_write'] = False
    try:
        prep_pack.apply_det_gate(live, payload_card=None, store_slot=None)
        det = live.get('det') or {}
        issues = list(det.get('issues') or [])
        det_clean = bool(det.get('ok')) and not issues
    except Exception as exc:
        det = {'ok': False, 'issues': [str(exc)]}
        det_clean = False
    fence_ok = (
        live.get('store_write') is False
        and (live.get('tm_fence') or {}).get('may_write') is False
    )
    return {
        'parseable': True,
        'parse_error': None,
        'obj': obj,
        'pack_out': {
            'ru_skeleton': live.get('ru_skeleton'),
            'route_hint': live.get('route_hint'),
            'store_write': live.get('store_write'),
            'tm_fence_may_write': (live.get('tm_fence') or {}).get('may_write'),
            'promotable': False,
        },
        'det': det,
        'det_clean': bool(det_clean and fence_ok),
        'final_status': 'det_clean' if det_clean and fence_ok else 'det_issues',
        'repair': repair,
        'fence_ok': fence_ok,
    }


class PairRunner:
    def __init__(self, run_dir, compiled, slots, spec, freeze_body):
        self.run_dir = os.path.abspath(run_dir)
        self.compiled = {row['request']['request_id']: row for row in compiled}
        self.slots = slots
        self.spec = spec
        self.freeze_body = freeze_body
        self.led = ledger.EventLedger(self.run_dir)
        self.reservations = reserve.CallReservationLedger(
            os.path.join(self.run_dir, 'call_reservations.json'),
            spec['run_id'], spec['max_base_calls'])
        self.canonical_before = canonical_snapshot(freeze_body)
        self.ds = None
        self.spent_usd = 0.0
        self.parseable = 0
        self.unparseable = 0
        self.slot_outputs = {}

    def seal(self, source_commit, cohort_sha):
        price_card = ds_arm.price_card_name()
        spec = {
            'run_id': self.spec['run_id'],
            'handoff': self.spec.get('handoff', 'H2704'),
            'source_commit': source_commit,
            'baseline_manifest_sha256': self.freeze_body.get('manifest_sha256'),
            'cohort_sha256': cohort_sha,
            'pricing_version': 'deepseek-v4-flash/%s' % price_card,
            'n': self.spec['n_pairs'],
            'call_ceiling': self.spec['max_base_calls'],
            'cost_ceiling_usd': self.spec['cost_ceiling_usd'],
            'schedule_window': (
                'pre-1608-authorized' if price_card == 'pre-1608'
                else 'after-1608-offpeak-only'
            ),
            'requested_model': REQUESTED_MODEL,
            'provider': PROVIDER,
            'retry_ladder': ['v0'],
            'promotable': False,
            'acceptance': {
                'handoff': self.spec.get('handoff', 'H2704'),
                'lane': self.spec['mode'],
                'parseable_min': self.spec['parseable_min'],
                'parseable_denom': self.spec['max_base_calls'],
                'n_pairs': self.spec['n_pairs'],
                'served_model': REQUESTED_MODEL,
                'promotable': False,
                'max_transport_attempts_per_slot': 1,
                'h2675_usd_per_card': 0.000873,
                'h2675_parseable': 200,
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
                'pack_out': detail.get('pack_out') if cw == 'cold' else None,
            }
            self.slot_outputs[(rid, cw)] = slim
            if slim['parseable']:
                self.parseable += 1
            else:
                self.unparseable += 1
            cost = event.get('observed_cost_usd')
            if event.get('cost_evaluable') and cost is not None:
                self.spent_usd += float(cost)
            if cw == 'cold' and slim['pack_out'] is not None:
                pending_cold[rid] = slim
        for rid, slim in pending_cold.items():
            if (rid, 'warm') in done:
                slim['pack_out'] = None
        return done

    def assert_canonical_unchanged(self):
        now = canonical_snapshot(self.freeze_body)
        if now != self.canonical_before:
            raise GateStop('canonical_hash_change')

    def connect(self, env_file):
        env = ds_arm.load_env_file(env_file)
        key = os.environ.get('DEEPSEEK_API_KEY') or env.get('DEEPSEEK_API_KEY')
        base = (os.environ.get('DEEPSEEK_BASE_URL') or env.get('DEEPSEEK_BASE_URL')
                or 'https://api.deepseek.com')
        if not key:
            raise GateStop('missing_DEEPSEEK_API_KEY')
        ds_arm.refuse_if_peak()
        self.ds = ds_arm.DeepSeek(
            base, key, REQUESTED_MODEL, MAX_TOKENS,
            timeout=TIMEOUT_S, reasoning_effort=None,
            max_transport_attempts=1)
        return key, base

    def maybe_stop_before(self, slot):
        if self.reservations.spent() >= self.spec['max_base_calls']:
            raise GateStop('call_ceiling')
        if self.spent_usd >= self.spec['cost_ceiling_usd']:
            raise GateStop('cost_ceiling')
        remaining = self.spec['max_base_calls'] - (self.parseable + self.unparseable)
        if self.parseable + remaining < self.spec['parseable_min']:
            raise GateStop('parseable_below_95')
        if self.unparseable >= (
                self.spec['max_base_calls'] - self.spec['parseable_min'] + 1):
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
        self.maybe_stop_before(slot)
        reservation = self.reservations.reserve(
            purpose=self.spec['purpose'],
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
        t0 = time.time()
        text, rec = self.ds.chat(
            system, user, 'prep:%s:%s' % (slot['key1'], slot['cold_warm']))
        usage, usage_reason = usage_from_rec(rec)
        cost, evaluable = rec_cost_usd(rec, usage)
        if evaluable and cost is not None:
            self.spent_usd += cost
        served = (rec or {}).get('served_model')
        if text and served and served != REQUESTED_MODEL:
            self.finalize_bad(reservation, rec, usage, cost)
            raise GateStop('served_model_mismatch')
        if text and usage is None:
            self.finalize_bad(reservation, rec, usage, cost)
            raise GateStop('unevaluable_billing')
        parsed = parse_prep(
            text, (rec or {}).get('finish_reason'), compiled['pack'])
        if parsed['parseable']:
            self.parseable += 1
        else:
            self.unparseable += 1
        blind = None
        if slot['cold_warm'] == 'warm':
            cold_ev = self.slot_outputs.get((slot['request_id'], 'cold'))
            cold_pack = (cold_ev or {}).get('pack_out')
            if parsed.get('pack_out') is not None and cold_pack is not None:
                blind = pair_compare.compare_prep_blind(
                    cold_pack, parsed['pack_out'])
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
            'price_card': (rec or {}).get('price_card'),
            'finish_reason': (rec or {}).get('finish_reason'),
            'promotable': False,
            'latency_s': (rec or {}).get('latency_s') or round(time.time() - t0, 2),
            'error': (rec or {}).get('error'),
            'pack_out': parsed.get('pack_out'),
            'blind': blind,
            'blind_class': (blind or {}).get('class'),
        }
        self.led.append({
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
            'pricing_version': 'deepseek-v4-flash/%s' % (
                (rec or {}).get('price_card') or 'unknown'),
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
            'pack_out': parsed.get('pack_out') if slot['cold_warm'] == 'cold' else None,
        }
        if slot['cold_warm'] == 'warm':
            prior = self.slot_outputs.get((slot['request_id'], 'cold'))
            if prior:
                prior['pack_out'] = None
        resp_path = os.path.join(
            self.run_dir, 'responses',
            '%s.%s.json' % (slot['request_id'], slot['cold_warm']))
        os.makedirs(os.path.dirname(resp_path), exist_ok=True)
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
            'pack_out': parsed.get('pack_out'),
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
        print('  [%03d/%d] %-16s %-4s parse=%s clean=%s usd=%s served=%s'
              % (slot['slot_ordinal'] + 1, self.spec['max_base_calls'],
                 slot['key1'], slot['cold_warm'],
                 parsed['parseable'], parsed['det_clean'], cost, served),
              flush=True)

    def finalize_bad(self, reservation, rec, usage, cost):
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
        summary['prep_lane_verdict'] = summary.get('generation_lane_verdict')
        if verdict_note:
            summary['runner_note'] = verdict_note
        path = os.path.join(self.run_dir, 'summary.json')
        with open(path, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(ident.canonical_dumps(summary))
        return summary


def write_freeze(path, extra):
    body = freeze.build_manifest()
    body['handoff'] = extra.get('handoff') or 'H2704'
    body.update(extra)
    body.pop('manifest_sha256', None)
    body['manifest_sha256'] = ident.sha256_bytes(ident.canonical_bytes(body))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(ident.canonical_dumps(body))
    return body


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=('prep50', 'l3', 'h2756'), default='prep50')
    ap.add_argument('--run-dir', default=None)
    ap.add_argument('--exp-dir', default=None)
    ap.add_argument('--env-file', default=DEFAULT_ENV)
    ap.add_argument('--compile-only', action='store_true')
    args = ap.parse_args(argv)

    spec = mode_spec(args.mode)
    exp_dir = args.exp_dir or spec.get('exp_dir') or EXP_DIR
    run_dir = args.run_dir or os.path.join(exp_dir, spec['mode'], 'run')
    os.makedirs(exp_dir, exist_ok=True)
    cohort_path = os.path.join(exp_dir, spec['manifest_name'])
    if not os.path.isfile(cohort_path):
        if spec.get('handoff') == 'H2756':
            raise GateStop('h2756 manifest missing; run cache_prep_h2756.py --seal')
        census.main(['--run-dir', os.path.join(exp_dir, 'tm')])
    cohort = load_json(cohort_path)
    keys = list(cohort['keys'])
    if len(keys) != spec['n_pairs']:
        raise GateStop('cohort n %d != %d' % (len(keys), spec['n_pairs']))

    freeze_path = os.path.join(exp_dir, spec['mode'], 'freeze.json')
    if os.path.isfile(freeze_path):
        freeze_body = load_json(freeze_path)
    else:
        freeze_body = write_freeze(freeze_path, {
            'handoff': spec.get('handoff', 'H2704'),
            'experiment': spec['mode'],
            'n_pairs': spec['n_pairs'],
            'max_base_calls': spec['max_base_calls'],
            'requested_model': REQUESTED_MODEL,
            'reasoning_effort': None,
            'max_tokens': MAX_TOKENS,
            'retry_policy': 'exact_sealed_transport_only',
            'max_transport_attempts_per_slot': 1,
            'cost_ceiling_usd': spec['cost_ceiling_usd'],
            'cohort_sha256': cohort.get('manifest_sha256'),
        })

    compiled, extra, prefixes = compile_cohort(keys, freeze_body)
    ordered, slots = expand_pairs(compiled)
    expand_and_check_pairs(slots, spec['n_pairs'])
    source_commit = freeze.git_commit() or freeze_body.get('source_commit')
    runner = PairRunner(run_dir, compiled, slots, spec, freeze_body)
    if not os.path.isfile(os.path.join(run_dir, 'run.manifest.json')):
        runner.seal(source_commit, cohort.get('manifest_sha256'))
        print('sealed mode=%s n_pairs=%d slots=%d prefix_groups=%d commit=%s'
              % (spec['mode'], spec['n_pairs'], len(slots),
                 len(prefixes), (source_commit or '')[:12]),
              flush=True)
    done = runner.load_resume()
    if args.compile_only:
        print('compile-only: %d requests, %d slots, done=%d'
              % (len(compiled), len(slots), len(done)))
        return 0
    runner.connect(args.env_file)
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
    summary = runner.write_summary(note)
    after_path = os.path.join(exp_dir, spec['mode'], 'canonical_hash_after.json')
    after_body = {
        'schema': 'pwg.cache_economy_canonical_rehash.v1',
        'handoff': spec.get('handoff', 'H2704'),
        'mode': spec['mode'],
        'before': runner.canonical_before,
        'after': canonical_snapshot(freeze_body),
        'equal': canonical_snapshot(freeze_body) == runner.canonical_before,
    }
    os.makedirs(os.path.dirname(after_path), exist_ok=True)
    with open(after_path, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(ident.canonical_dumps(after_body))
    print('lane=%s parseable=%s unique_clean=%s usd=%s'
          % (summary.get('prep_lane_verdict') or summary.get('generation_lane_verdict'),
             summary['parseable'], summary['unique_clean_cards'],
             summary['total_usd']),
          flush=True)
    return 0 if summary.get('generation_lane_verdict') != 'FAIL' else 2


if __name__ == '__main__':
    raise SystemExit(main())
