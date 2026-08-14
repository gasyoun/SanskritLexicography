#!/usr/bin/env python
"""Exact-prefix grouping and deterministic scheduling (H2702).

Group by (provider, requested_model, prefix_group_id). Groups stay
contiguous. Within a group the original source ordinal is preserved.
The first real request of a group is cold — no paid warm-up is bought.
Cold/warm position is stored on the item and restored on resume.
"""
from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def prefix_group_id(provider, requested_model, stable_prefix_sha256):
    return '%s|%s|%s' % (provider, requested_model, stable_prefix_sha256)


def schedule(items, resume=None):
    """Return a new list of scheduled items.

    ``items`` are dicts with at least provider, requested_model,
    stable_prefix_sha256, and a stable ``source_ordinal`` (int). Missing
    ordinals are assigned from input order (0-based).
    """
    resume = resume or {}
    prepared = []
    for index, raw in enumerate(items):
        item = dict(raw)
        if 'source_ordinal' not in item:
            item['source_ordinal'] = index
        item['prefix_group_id'] = prefix_group_id(
            item['provider'], item['requested_model'], item['stable_prefix_sha256'])
        prepared.append(item)

    groups = {}
    order = []
    for item in prepared:
        gid = item['prefix_group_id']
        if gid not in groups:
            groups[gid] = []
            order.append(gid)
        groups[gid].append(item)

    # Contiguous groups, group key sorted for determinism, members by source ordinal.
    scheduled = []
    for gid in sorted(order):
        members = sorted(groups[gid], key=lambda row: row['source_ordinal'])
        for position, item in enumerate(members):
            prior = resume.get(item.get('request_id'))
            if prior and prior.get('cold_warm') in ('cold', 'warm'):
                item['cold_warm'] = prior['cold_warm']
                item['group_position'] = prior.get('group_position', position)
            else:
                item['group_position'] = position
                item['cold_warm'] = 'cold' if position == 0 else 'warm'
            scheduled.append(item)
    return scheduled


def selftest():
    items = [
        {'provider': 'deepseek', 'requested_model': 'pro',
         'stable_prefix_sha256': 'aa', 'request_id': 'r3', 'source_ordinal': 3},
        {'provider': 'deepseek', 'requested_model': 'pro',
         'stable_prefix_sha256': 'bb', 'request_id': 'r1', 'source_ordinal': 1},
        {'provider': 'deepseek', 'requested_model': 'flash',
         'stable_prefix_sha256': 'aa', 'request_id': 'r2', 'source_ordinal': 2},
        {'provider': 'deepseek', 'requested_model': 'pro',
         'stable_prefix_sha256': 'aa', 'request_id': 'r0', 'source_ordinal': 0},
    ]
    shuffled = [items[2], items[0], items[3], items[1]]
    a = schedule(shuffled)
    b = schedule(list(reversed(items)))
    ids_a = [row['request_id'] for row in a]
    ids_b = [row['request_id'] for row in b]
    if ids_a != ids_b:
        raise AssertionError('schedule is not deterministic: %s vs %s' % (ids_a, ids_b))
    # Groups contiguous.
    seen = []
    last = None
    for row in a:
        gid = row['prefix_group_id']
        if gid != last:
            if gid in seen:
                raise AssertionError('group %s is not contiguous' % gid)
            seen.append(gid)
            last = gid
    # First of prefix aa/pro is ordinal 0 = cold; ordinal 3 = warm.
    by_id = {row['request_id']: row for row in a}
    if by_id['r0']['cold_warm'] != 'cold' or by_id['r3']['cold_warm'] != 'warm':
        raise AssertionError('cold/warm assignment wrong: %s' % by_id)
    if by_id['r0']['source_ordinal'] != 0 or by_id['r3']['source_ordinal'] != 3:
        raise AssertionError('source ordinal lost')
    # Resume preserves cold/warm even if the remaining set would reassign.
    resume = {'r3': {'cold_warm': 'warm', 'group_position': 1}}
    only_warm = schedule([items[0]], resume=resume)
    if only_warm[0]['cold_warm'] != 'warm':
        raise AssertionError('resume lost warm position')
    # Different worker counts are a caller concern; the order itself is a
    # pure function of the item set.
    print('cache_scheduler selftest: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(selftest())
