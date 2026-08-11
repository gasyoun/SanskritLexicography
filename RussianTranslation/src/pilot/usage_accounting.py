#!/usr/bin/env python
"""Truthful, billing-mode-aware accounting for PWG model calls.

Token usage is observable independently of whether a cash price is observable.
In particular, Claude CLI ``total_cost_usd`` on a Max Agent SDK allowance is a
credit/list-price equivalent; it is never evidence of incremental cash spend.
"""
from __future__ import annotations

import math


SCHEMA = 'pwg.usage_accounting.v1'
POLICY = 'anthropic-opus-5-2026-08-11.v1'

MAX_INTERACTIVE = 'max_interactive'
MAX_AGENT_SDK_CREDIT = 'max_agent_sdk_credit'
API_STANDARD = 'api_standard'
API_BATCH = 'api_batch'
UNKNOWN_GATEWAY = 'unknown_gateway'
BILLING_MODES = (
    MAX_INTERACTIVE, MAX_AGENT_SDK_CREDIT, API_STANDARD, API_BATCH,
    UNKNOWN_GATEWAY,
)

TOKEN_FIELDS = (
    'input_tokens', 'output_tokens', 'cache_creation_tokens',
    'cache_read_tokens',
)
ALIASES = {
    'input_tokens': ('input_tokens',),
    'output_tokens': ('output_tokens',),
    'cache_creation_tokens': (
        'cache_creation_tokens', 'cache_creation_input_tokens',
        'cache_write_tokens',
    ),
    'cache_read_tokens': ('cache_read_tokens', 'cache_read_input_tokens'),
}

# Direct Anthropic Opus 5 rates pinned for counterfactual accounting. Batch is
# represented explicitly as a 50% rate schedule so no caller can mistake the
# comparison figure for observed gateway or subscription cash.
STANDARD_PER_MTOK_USD = {
    'input_tokens': 5.0,
    'output_tokens': 25.0,
    'cache_creation_tokens': 10.0,  # one-hour write: 2x base input
    'cache_read_tokens': 0.5,
}
BATCH_PER_MTOK_USD = {
    name: rate * 0.5 for name, rate in STANDARD_PER_MTOK_USD.items()
}


def _number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value >= 0)


def _tokens(usage):
    if not isinstance(usage, dict):
        return None
    result = {}
    for target, aliases in ALIASES.items():
        found = [usage[name] for name in aliases if name in usage]
        if len(found) != 1 or not isinstance(found[0], int) \
                or isinstance(found[0], bool) or found[0] < 0:
            return None
        result[target] = found[0]
    return result


def equivalent_usd(tokens, billing_mode):
    """Calculate a pinned counterfactual; never claim that it was charged."""
    if tokens is None:
        return None
    rates = BATCH_PER_MTOK_USD if billing_mode == API_BATCH else STANDARD_PER_MTOK_USD
    return round(sum(tokens[name] * rates[name] for name in TOKEN_FIELDS) / 1_000_000, 9)


def build(usage, *, billing_mode=UNKNOWN_GATEWAY, observed_cash_usd=None,
          reported_equivalent_usd=None, credit_claimed=False,
          credit_claim_evidence=None,
          pricing_policy=POLICY):
    """Build and validate one accounting envelope.

    ``reported_equivalent_usd`` is the CLI/provider's list-price counter. For a
    claimed Max Agent SDK allowance it becomes both list and credit consumption,
    while observed cash remains null. Without claim evidence the billing mode is
    deliberately downgraded to unknown.
    """
    if billing_mode not in BILLING_MODES:
        raise ValueError('unsupported billing_mode: %r' % billing_mode)
    if observed_cash_usd is not None and not _number(observed_cash_usd):
        raise ValueError('observed_cash_usd must be null or non-negative finite number')
    if reported_equivalent_usd is not None and not _number(reported_equivalent_usd):
        raise ValueError('reported_equivalent_usd must be null or non-negative finite number')
    tokens = _tokens(usage)
    evaluable = tokens is not None
    clean = tokens or {name: 0 for name in TOKEN_FIELDS}

    effective_mode = billing_mode
    list_equivalent = equivalent_usd(tokens, API_STANDARD)
    credit_equivalent = None
    cash = observed_cash_usd
    if billing_mode == MAX_AGENT_SDK_CREDIT:
        cash = None
        if credit_claimed is not True or not isinstance(credit_claim_evidence, str) \
                or not credit_claim_evidence.strip():
            effective_mode = UNKNOWN_GATEWAY
            list_equivalent = None
        else:
            if reported_equivalent_usd is not None:
                list_equivalent = round(float(reported_equivalent_usd), 9)
            credit_equivalent = list_equivalent
    elif billing_mode == MAX_INTERACTIVE:
        cash = None
        if reported_equivalent_usd is not None:
            list_equivalent = round(float(reported_equivalent_usd), 9)
    elif billing_mode == API_BATCH:
        list_equivalent = equivalent_usd(tokens, API_STANDARD)
        cash = equivalent_usd(tokens, API_BATCH) if cash is None else round(float(cash), 9)
    elif billing_mode == API_STANDARD:
        cash = list_equivalent if cash is None else round(float(cash), 9)
    else:
        cash = None if cash is None else round(float(cash), 9)
        list_equivalent = None

    value = {
        'schema': SCHEMA,
        'usage_evaluable': evaluable,
        **clean,
        'billing_mode': effective_mode,
        'observed_cash_usd': cash,
        'list_equivalent_usd': list_equivalent,
        'credit_equivalent_usd': credit_equivalent,
        'pricing_policy': pricing_policy,
    }
    if billing_mode == MAX_AGENT_SDK_CREDIT:
        value['credit_claim_evidence'] = (
            credit_claim_evidence.strip()
            if credit_claimed is True and isinstance(credit_claim_evidence, str)
            and credit_claim_evidence.strip() else None)
    return validate(value)


def validate(value):
    if not isinstance(value, dict) or value.get('schema') != SCHEMA:
        raise ValueError('usage accounting schema mismatch')
    if not isinstance(value.get('usage_evaluable'), bool):
        raise ValueError('usage_evaluable must be boolean')
    for name in TOKEN_FIELDS:
        token = value.get(name)
        if not isinstance(token, int) or isinstance(token, bool) or token < 0:
            raise ValueError('%s must be a non-negative integer' % name)
    if value.get('billing_mode') not in BILLING_MODES:
        raise ValueError('usage accounting billing_mode mismatch')
    for name in ('observed_cash_usd', 'list_equivalent_usd', 'credit_equivalent_usd'):
        if value.get(name) is not None and not _number(value[name]):
            raise ValueError('%s must be null or non-negative finite number' % name)
    if not isinstance(value.get('pricing_policy'), str) or not value['pricing_policy']:
        raise ValueError('pricing_policy must be non-empty text')
    if 'credit_claim_evidence' in value and value['credit_claim_evidence'] is not None \
            and (not isinstance(value['credit_claim_evidence'], str)
                 or not value['credit_claim_evidence']):
        raise ValueError('credit_claim_evidence must be null or non-empty text')
    return value


def legacy_telemetry(accounting):
    """Map v1 accounting into the byte-stable legacy ledger telemetry shape."""
    validate(accounting)
    cash = accounting['observed_cash_usd']
    return {
        'cost_evaluable': cash is not None,
        'input_tokens': accounting['input_tokens'],
        'output_tokens': accounting['output_tokens'],
        'cache_read_tokens': accounting['cache_read_tokens'],
        'cache_creation_tokens': accounting['cache_creation_tokens'],
        'subagent_tokens': sum(accounting[name] for name in TOKEN_FIELDS),
        'observed_cost_usd': 0 if cash is None else cash,
        'accounting': accounting,
    }
