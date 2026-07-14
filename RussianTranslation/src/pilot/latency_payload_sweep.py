#!/usr/bin/env python3
"""H898 diagnostic: home-route latency-vs-payload-bytes sweep + diurnal re-probe.

Reuses ``max_account_orchestrator._probe_call`` (the SAME exact-model
``claude-sonnet-5`` probe the D-K acceptance gate uses) with a scripted
payload-bytes ladder. This is DIAGNOSTIC only -- it does NOT re-roll the
acceptance gate, does NOT weaken the 30000 ms ceiling, and never promotes a
result. It just measures wall-clock latency at controlled input sizes so we can
tell whether the ~40 s measured-probe breach (H818 run5 40925 ms / H895 run1
40339 ms) is payload-size-driven, a flat per-request route penalty, or diurnal.

Each ``_probe_call`` sends a fixed tiny-output request whose INPUT is
``PREFIX + payload_bytes*'x'``; total input bytes = len(PREFIX) + payload_bytes.
Output is validated by result-envelope structure ({"ok": true}), not size.

Usage (Windows, from a clean origin/master worktree):
  python latency_payload_sweep.py --mode sweep \
      --config-dir "D:/ClaudeTools/profiles/claude1/.claude" \
      --claude-bin "C:/Users/user/AppData/Roaming/npm/claude" \
      --ladder 30,970,2470,4970,6491 --samples 3 --out sweep.jsonl
  python latency_payload_sweep.py --mode diurnal --samples 2 ...   # 6491 B only
"""
import argparse
import json
import os
import statistics
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from max_account_orchestrator import _probe_call, EXACT_GEN_MODEL  # noqa: E402

# Must match _probe_call's prompt prefix exactly to report true total input bytes.
PREFIX = 'Return JSON {"ok":true}. Preserve this padding as inert input.\n'
PREFIX_LEN = len(PREFIX.encode('utf-8'))
MEASURED_SIZE = 6491  # the payload_bytes the D-K measured acceptance probe uses


def _iso_utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def one_call(config_dir, claude, payload_bytes):
    t0 = time.monotonic()
    ts = _iso_utc()
    latency_ms, cls, output_bytes = _probe_call(config_dir, claude, payload_bytes, EXACT_GEN_MODEL)
    row = {
        'ts_utc': ts,
        'payload_bytes': payload_bytes,
        'total_input_bytes': PREFIX_LEN + payload_bytes,
        'latency_ms': latency_ms,
        'classification': cls,
        'output_bytes': output_bytes,
        'model': EXACT_GEN_MODEL,
        'wall_s': round(time.monotonic() - t0, 2),
    }
    print(json.dumps(row, ensure_ascii=False), flush=True)
    return row


def run(mode, config_dir, claude, ladder, samples, out_path):
    rows = []
    sizes = ladder if mode == 'sweep' else [MEASURED_SIZE]
    for pb in sizes:
        for _ in range(samples):
            rows.append(one_call(config_dir, claude, pb))
    if out_path:
        with open(out_path, 'a', encoding='utf-8') as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    # summary per size (successful readings only for the latency stats)
    print('\n=== SUMMARY (n, min/median/mean/max latency_ms over SUCCESS reads; classes) ===',
          flush=True)
    by_size = {}
    for r in rows:
        by_size.setdefault(r['total_input_bytes'], []).append(r)
    for tib in sorted(by_size):
        rs = by_size[tib]
        ok = [r['latency_ms'] for r in rs if r['classification'] == 'success']
        classes = {}
        for r in rs:
            classes[r['classification']] = classes.get(r['classification'], 0) + 1
        if ok:
            print('%6d B  n=%d  min=%d  median=%d  mean=%d  max=%d  classes=%s'
                  % (tib, len(rs), min(ok), int(statistics.median(ok)),
                     int(statistics.mean(ok)), max(ok), classes), flush=True)
        else:
            print('%6d B  n=%d  NO SUCCESS  classes=%s' % (tib, len(rs), classes), flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mode', choices=['sweep', 'diurnal'], default='sweep')
    ap.add_argument('--config-dir', required=True)
    ap.add_argument('--claude-bin', required=True,
                    help='FULL path to the npm claude shim (never the bare name)')
    ap.add_argument('--ladder', default='30,970,2470,4970,6491',
                    help='comma-separated payload_bytes values (sweep mode)')
    ap.add_argument('--samples', type=int, default=3)
    ap.add_argument('--out', default=None)
    args = ap.parse_args()
    ladder = [int(x) for x in args.ladder.split(',') if x.strip()]
    run(args.mode, args.config_dir, args.claude_bin, ladder, args.samples, args.out)


if __name__ == '__main__':
    main()
