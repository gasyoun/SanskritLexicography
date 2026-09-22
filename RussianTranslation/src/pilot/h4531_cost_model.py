#!/usr/bin/env python
"""H4531: projected batch cost for the built request bundle, from prompt bytes.

An ESTIMATE, explicitly labelled: bytes/4 is not a tokenizer. It exists so the report
can state the order of magnitude the ceiling was sized against without a paid call, and
so the live run can be compared against the estimate afterwards.
"""
from __future__ import annotations

import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from usage_accounting import (  # noqa: E402
    API_BATCH, API_STANDARD, SONNET_STANDARD_PER_MTOK_USD, equivalent_usd)

bundle = json.load(open(sys.argv[1], encoding='utf-8'))
rows = bundle['rows']
prompt_bytes = [len(row['request']['prompt']) for row in rows]
est_input = sum(prompt_bytes) // 4
est_output = len(rows) * 1200  # one-card PWG outputs measured at ~1-2k tokens
tokens = {'input_tokens': est_input, 'output_tokens': est_output,
          'cache_creation_tokens': 0, 'cache_read_tokens': 0}
print('cards: %d' % len(rows))
print('prompt bytes: total=%d min=%d max=%d mean=%d'
      % (sum(prompt_bytes), min(prompt_bytes), max(prompt_bytes),
         sum(prompt_bytes) // len(prompt_bytes)))
print('ESTIMATED tokens (bytes/4): input=%d output=%d' % (est_input, est_output))
print('ESTIMATED standard USD: %.4f' % equivalent_usd(
    tokens, API_STANDARD, SONNET_STANDARD_PER_MTOK_USD))
print('ESTIMATED batch USD (50%%): %.4f' % equivalent_usd(
    tokens, API_BATCH, SONNET_STANDARD_PER_MTOK_USD))
