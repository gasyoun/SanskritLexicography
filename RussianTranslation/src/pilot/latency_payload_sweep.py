#!/usr/bin/env python3
"""H898 diagnostic: exact-model latency probe sweep + foreign/home route comparison.

Reuses ``max_account_orchestrator._probe_call`` (the SAME exact-model
``claude-sonnet-5`` probe the D-K acceptance gate uses) with a scripted
payload-bytes ladder. This is DIAGNOSTIC only -- it does NOT re-roll the
acceptance gate, does NOT weaken the 30000 ms ceiling, and never imports/claims a
job, promotes a result, or writes the canonical store / translation memory. It
only measures wall-clock latency.

Each ``_probe_call`` sends a fixed tiny-output request whose INPUT is
``PREFIX + padding_bytes*'x'``. Two byte counts are reported and must not be
conflated (sol.md #4):
  * ``padding_bytes``       -- the ``--ladder`` / ``MEASURED_SIZE`` argument (the 'x' count).
  * ``actual_prompt_bytes`` -- the real encoded prompt = len(PREFIX) + padding_bytes
                               (== ``total_input_bytes``; kept under both names).
For the D-K measured acceptance size, padding_bytes=6491 -> actual_prompt_bytes=6554.
Output is validated by result-envelope structure ({"ok": true}); only its BYTE
COUNT is recorded -- never the output content, never credentials.

Warm-up policy (sol.md #5): each invocation runs ``--warmups`` priming calls
FIRST (tagged ``warmup=true``) which are EXCLUDED from the summary; then
``--samples`` measured calls. Use the SAME policy on both hosts.

Home usage (Windows):
  python latency_payload_sweep.py --mode diurnal --samples 5 --warmups 1 \
      --route home-windows --window W1 --account-label acctA \
      --config-dir "D:/ClaudeTools/profiles/claude1/.claude" \
      --claude-bin "C:/Users/user/AppData/Roaming/npm/claude" --out home_W1.jsonl
Foreign usage (Linux): same flags, --route foreign-linux, --config-dir the
owner-authenticated foreign profile, --claude-bin "$(command -v claude)".
Crossover (sol.md #2): run --samples 1 invocations alternating routes A-B-B-A,
bumping --seq-start each turn; the analyzer groups by route+window.
"""
import argparse
import json
import os
import statistics
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from max_account_orchestrator import _probe_call, EXACT_GEN_MODEL  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
# Must match _probe_call's prompt prefix exactly to report true total input bytes.
PREFIX = 'Return JSON {"ok":true}. Preserve this padding as inert input.\n'
PREFIX_LEN = len(PREFIX.encode('utf-8'))  # 63 bytes
MEASURED_SIZE = 6491  # padding_bytes of the D-K measured acceptance probe (-> 6554 actual)


def _iso_utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def _git_sha():
    try:
        out = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=HERE,
                             capture_output=True, text=True, encoding='utf-8', timeout=15)
        return out.stdout.strip() or 'unknown'
    except Exception:
        return 'unknown'


def _cli_version(claude):
    try:
        out = subprocess.run([claude, '--version'], capture_output=True, text=True,
                             encoding='utf-8', timeout=30)
        return (out.stdout or out.stderr or '').strip() or 'unknown'
    except Exception:
        return 'unknown'


def one_call(config_dir, claude, padding_bytes, *, route, window, account_label,
             sample_index, warmup, git_sha, cli_version):
    t0 = time.monotonic()
    ts = _iso_utc()
    latency_ms, cls, output_bytes = _probe_call(config_dir, claude, padding_bytes, EXACT_GEN_MODEL)
    row = {
        'ts_utc': ts,
        'route': route,                          # host/route label (sol.md #5)
        'window': window,                        # run/window ID
        'sample_index': sample_index,            # crossover sequence position (None for warm-ups)
        'warmup': warmup,                        # excluded from measured stats
        'account_label': account_label,          # pseudonym -- NEVER the real account/credential
        'model': EXACT_GEN_MODEL,                # exact generation model under test
        'git_sha': git_sha,
        'cli_version': cli_version,
        'padding_bytes': padding_bytes,          # the 'x' padding argument
        'actual_prompt_bytes': PREFIX_LEN + padding_bytes,  # real encoded prompt bytes
        'total_input_bytes': PREFIX_LEN + padding_bytes,    # alias (analyzer key; == actual)
        'latency_ms': latency_ms,
        'classification': cls,
        'output_bytes': output_bytes,            # BYTE COUNT only -- never the output content
        'wall_s': round(time.monotonic() - t0, 2),
    }
    tag = 'warmup' if warmup else 'seq=%s' % sample_index
    print('%s route=%s window=%s %s pad=%dB actual=%dB -> %d ms %s'
          % (ts, route, window, tag, padding_bytes, PREFIX_LEN + padding_bytes,
             latency_ms, cls), flush=True)
    return row


def run(mode, config_dir, claude, ladder, samples, warmups, out_path,
        route, window, account_label, seq_start):
    git_sha = _git_sha()
    cli_version = _cli_version(claude)
    sizes = ladder if mode == 'sweep' else [MEASURED_SIZE]
    rows = []
    kw = dict(route=route, window=window, account_label=account_label,
              git_sha=git_sha, cli_version=cli_version)
    for pb in sizes:
        for _ in range(max(0, warmups)):
            rows.append(one_call(config_dir, claude, pb, sample_index=None, warmup=True, **kw))
        for i in range(max(0, samples)):
            rows.append(one_call(config_dir, claude, pb, sample_index=seq_start + i,
                                 warmup=False, **kw))
    if out_path:
        with open(out_path, 'a', encoding='utf-8') as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    # summary per size over MEASURED (non-warmup) SUCCESS reads only
    print('\n=== SUMMARY (measured, warm-ups excluded; latency_ms over SUCCESS reads) ===',
          flush=True)
    measured = [r for r in rows if not r['warmup']]
    by_size = {}
    for r in measured:
        by_size.setdefault(r['actual_prompt_bytes'], []).append(r)
    for tib in sorted(by_size):
        rs = by_size[tib]
        ok = [r['latency_ms'] for r in rs if r['classification'] == 'success']
        classes = {}
        for r in rs:
            classes[r['classification']] = classes.get(r['classification'], 0) + 1
        breach = sum(1 for r in rs if r['latency_ms'] > 30000)
        if ok:
            print('%6d B (actual)  n=%d  min=%d  median=%d  mean=%d  max=%d  breach>30s=%d/%d  classes=%s'
                  % (tib, len(rs), min(ok), int(statistics.median(ok)),
                     int(statistics.mean(ok)), max(ok), breach, len(rs), classes), flush=True)
        else:
            print('%6d B (actual)  n=%d  NO SUCCESS  breach>30s=%d/%d  classes=%s'
                  % (tib, len(rs), breach, len(rs), classes), flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--mode', choices=['sweep', 'diurnal'], default='sweep')
    ap.add_argument('--config-dir', required=True)
    ap.add_argument('--claude-bin', required=True,
                    help='FULL path to the npm claude shim (never the bare name)')
    ap.add_argument('--ladder', default='30,970,2470,4970,6491',
                    help='comma-separated padding_bytes values (sweep mode)')
    ap.add_argument('--samples', type=int, default=3, help='measured calls per size')
    ap.add_argument('--warmups', type=int, default=1,
                    help='priming calls per size, tagged warmup and excluded from stats (sol.md #5)')
    ap.add_argument('--route', default='home', help='host/route label, e.g. home-windows / foreign-linux')
    ap.add_argument('--window', default='W1', help='run/window ID (group probes by time window)')
    ap.add_argument('--account-label', default='acctA',
                    help='pseudonym only -- NEVER the real account name or any credential')
    ap.add_argument('--seq-start', type=int, default=0,
                    help='base sample_index for crossover sequence position')
    ap.add_argument('--out', default=None)
    args = ap.parse_args()
    ladder = [int(x) for x in args.ladder.split(',') if x.strip()]
    run(args.mode, args.config_dir, args.claude_bin, ladder, args.samples, args.warmups,
        args.out, args.route, args.window, args.account_label, args.seq_start)


if __name__ == '__main__':
    main()
