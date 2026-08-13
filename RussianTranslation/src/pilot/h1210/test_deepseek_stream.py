#!/usr/bin/env python
"""Hermetic mock-stream test for H2674 W0 — no network, no API key.

Proves accumulate_stream holds >8192 thinking tokens without urllib
IncompleteRead, and that DeepSeek.chat uses the injected OpenAI-style
stream client (stream=True).
"""
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import deepseek_arm as ds  # noqa: E402


def main():
    ds._selftest_peak()
    ds._selftest_price()
    ds._selftest_stream()
    assert ds.DEFAULT_MODEL == 'deepseek-v4-flash'
    assert ds.DEFAULT_MAX_TOKENS == 32768
    assert ds.TRANSPORT == 'openai-sdk-stream'
    print('test_deepseek_stream: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
