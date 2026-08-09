#!/usr/bin/env python
"""Workflow-output parsing helpers for PWG frequency-window audits.

H2089: missing ``results`` is a hard failure (silent-empty clean zero is a
defect), and bare null cards get a synthetic failure_REASON so audits never
see an empty error field.

H2173/G5 completes that at ROW granularity. H2089 hardened the envelope (no
results list = raise) and the card slot (null card = synthetic REASON), but the
row slot in between still had a silent hole: a row that was not a dict, or whose
``key`` was falsy, hit a bare ``continue`` and landed in NEITHER ``keys`` NOR
``nulls``. That is the same silent-empty class one level down — the window was
billed for the call, and the card was invisible to every accounting surface that
reads those two lists (audit key counts, null counts, provenance coverage). Such
rows are now materialised as failures under a synthetic key, so a paid card can
no longer vanish between the envelope check and the card check.
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


MALFORMED_ROW_KEY_PREFIX = '__malformed_row_'
MALFORMED_NOT_A_DICT = 'malformed_result_row_not_a_dict'
MALFORMED_MISSING_KEY = 'malformed_result_row_missing_key'


def malformed_row_key(index):
    """The synthetic key a keyless/malformed result row is accounted under (G5)."""
    return '%s%d__' % (MALFORMED_ROW_KEY_PREFIX, index)


def is_malformed_row_key(key):
    return isinstance(key, str) and key.startswith(MALFORMED_ROW_KEY_PREFIX)


def _stamp_malformed_row(index, row, source=None):
    """Materialise an unaccountable result row as a visible failure (H2173 G5).

    A row that is not a dict, or that carries no usable ``key``, cannot be
    attributed to a headword — so it can never be promoted, and it used to be
    dropped silently. It is returned here as a dict standing in for the original,
    under a synthetic key, carrying the same ``error``/``failure_REASON`` shape
    ``_stamp_null_card_failure`` uses so downstream readers need no special case.
    The original row is preserved under ``malformed_row_raw`` — the evidence of
    what was actually billed must survive the accounting fix.
    """
    if isinstance(row, dict):
        stamped = dict(row)
        reason = MALFORMED_MISSING_KEY
        message = 'workflow result row has no usable key (H2173 synthetic)'
    else:
        stamped = {}
        reason = MALFORMED_NOT_A_DICT
        message = ('workflow result row is %s, not an object (H2173 synthetic)'
                   % type(row).__name__)
    message = '%s [%s row %d]' % (message, source or '<unknown source>', index)
    stamped['malformed_result_row'] = True
    stamped['malformed_row_index'] = index
    # H2252: the index alone does not locate the evidence. A window fans out over
    # many workflow artifacts and the stamped row travels into audit/requeue
    # surfaces detached from the file it came from, so "row 4 was unaccountable"
    # named nothing an operator could open. Carry the source path with the index;
    # every other refusal in this module already names the path it refused.
    stamped['malformed_row_source'] = source
    stamped['malformed_row_raw'] = repr(row)[:500]
    stamped['key'] = malformed_row_key(index)
    stamped['error'] = {
        'code': 'malformed_result_row',
        'failure_REASON': reason,
        'message': message,
    }
    stamped['failure_REASON'] = reason
    return stamped


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
    for index, row in enumerate(results):
        # G5 (H2173): an unaccountable row is a FAILURE, never a skip. It is rewritten
        # in place so `results` — which audit and requeue both read — carries the same
        # visible failure the counts now report, and it enters BOTH lists: `keys` so the
        # billed call shows up in the window's key count, `nulls` so it is never mistaken
        # for a clean card. A keyed row with a card is unaffected.
        if not isinstance(row, dict) or not row.get('key'):
            stamped = _stamp_malformed_row(index, row, source=path)
            results[index] = stamped
            keys.append(stamped['key'])
            nulls.append(stamped['key'])
            continue
        key = row['key']
        keys.append(key)
        if not row.get('card'):
            _stamp_null_card_failure(row)
            nulls.append(key)
    return payload, meta, results, keys, nulls


def workflow_keys(path):
    return workflow_payload(path)[3:5]
