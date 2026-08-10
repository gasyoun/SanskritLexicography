"""Emit one UTC boundary stamp for the H2539 attestation window.

The attestation window must be stamped from the same clock on both sides, so
started_at/ended_at are taken here rather than typed by hand.
Run: python pwg_ru/h2539/stamp_now.py [label]
"""
import datetime as dt
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

label = sys.argv[1] if len(sys.argv) > 1 else 'stamp'
now = dt.datetime.now(dt.timezone.utc)
iso = now.strftime('%Y-%m-%dT%H:%M:%S.') + '%03dZ' % (now.microsecond // 1000)
print(json.dumps({'label': label, 'iso': iso, 'ns': time.time_ns()}))
