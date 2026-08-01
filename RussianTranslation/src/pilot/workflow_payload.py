#!/usr/bin/env python
"""Workflow-output parsing helpers for PWG frequency-window audits.

H2089: missing ``results`` is a hard failure (silent-empty clean zero is a
defect), and bare null cards get a synthetic failure_REASON so audits never
see an empty error field.
"""
import json


class WorkflowPayloadError(ValueError):
    """Workflow JSON has no usable results list (H2089 silent-empty class)."""


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


def _stamp_null_card_failure(row):
    """Ensure a null-card row carries a visible failure reason (H2089).

    Mutates ``row`` in place when card is missing/null and no prior error is set.
    """
    if row.get('card'):
        return
    if row.get('error') or row.get('failure_REASON') or row.get('failure-REASON'):
        return
    # Prefer a structured error object callers already understand.
    row['error'] = {
        'code': 'null_card',
        'failure_REASON': 'null_card_no_card_object',
        'message': 'workflow result has no card object (H2089 synthetic)',
    }
    row['failure_REASON'] = 'null_card_no_card_object'


def workflow_payload(path, *, allow_missing_results=False):
    """Load workflow JSON and extract meta/results/keys/nulls.

    Parameters
    ----------
    allow_missing_results:
        When False (default, H2089), raise WorkflowPayloadError if no ``results``
        list exists anywhere in the payload — never treat that as a clean empty
        window. Pass True only for diagnostic inventory that intentionally
        accepts broken envelopes.
    """
    payload = load_json(path)
    container = find_results_container(payload)
    if container is None:
        if allow_missing_results:
            container = {}
            results = []
        else:
            raise WorkflowPayloadError(
                '%s: no results list found — refuse silent-empty zero (H2089)'
                % path
            )
    else:
        results = container.get('results')
        if results is None:
            if allow_missing_results:
                results = []
            else:
                raise WorkflowPayloadError(
                    '%s: results key present but null — refuse silent-empty (H2089)'
                    % path
                )
        if not isinstance(results, list):
            raise WorkflowPayloadError(
                '%s: results is %s, expected list' % (path, type(results).__name__)
            )

    if isinstance(container.get('meta'), dict):
        meta = container['meta']
    elif isinstance(payload, dict) and isinstance(payload.get('meta'), dict):
        meta = payload['meta']
    else:
        meta = {}
    keys, nulls = [], []
    for row in results:
        if not isinstance(row, dict):
            continue
        key = row.get('key')
        if not key:
            continue
        keys.append(key)
        if not row.get('card'):
            _stamp_null_card_failure(row)
            nulls.append(key)
    return payload, meta, results, keys, nulls


def workflow_keys(path):
    return workflow_payload(path)[3:5]
