#!/usr/bin/env python
"""H4531: zero-token credential/model reachability probe (no batch, no spend).

Separated from the probe driver so a credential verdict can be re-taken for $0 after a
key rotation, without re-entering the reserve-then-submit path.
"""
from __future__ import annotations

import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import anthropic_batches_route as abr  # noqa: E402
import anthropic_messages_route as amr  # noqa: E402


def main():
    client, _ = abr.api_client()
    print('credential source: %s' % abr.credential_note())
    verdict = amr.check_auth_and_model(client, model=abr.MODEL)
    print(json.dumps(verdict, ensure_ascii=False, sort_keys=True))
    return 0 if verdict.get('authenticated') and verdict.get('model_available') else 4


if __name__ == '__main__':
    raise SystemExit(main())
