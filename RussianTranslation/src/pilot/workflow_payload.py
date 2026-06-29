#!/usr/bin/env python
"""Workflow-output parsing helpers for PWG frequency-window audits."""
import json


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def find_results_container(obj):
    if isinstance(obj, dict):
        if isinstance(obj.get('results'), list):
            return obj
        for value in obj.values():
            found = find_results_container(value)
            if found is not None:
                return found
    if isinstance(obj, list):
        for value in obj:
            found = find_results_container(value)
            if found is not None:
                return found
    return None


def find_results(obj):
    container = find_results_container(obj)
    return container.get('results') if container else None


def workflow_payload(path):
    payload = load_json(path)
    container = find_results_container(payload) or {}
    results = container.get('results') or []
    if isinstance(container.get('meta'), dict):
        meta = container['meta']
    elif isinstance(payload, dict) and isinstance(payload.get('meta'), dict):
        meta = payload['meta']
    else:
        meta = {}
    keys, nulls = [], []
    for row in results:
        key = row.get('key')
        if not key:
            continue
        keys.append(key)
        if not row.get('card'):
            nulls.append(key)
    return payload, meta, results, keys, nulls


def workflow_keys(path):
    return workflow_payload(path)[3:5]
