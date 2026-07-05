#!/usr/bin/env python
"""Local read-only dashboard server for RussianTranslation operations."""
import argparse
import datetime
import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from dashboard_events import read_events
import window_common
import evolution_stats

# Evolution stats are derived from the full logs (10k+ cards); cache on the
# newest source mtime so the 5s status poll never triggers a recompute and a
# separate, slower /api/evolution poll only rebuilds when a source file changes.
_evo_cache = {'mtime': None, 'data': None}


def evolution_payload(root):
    paths = evolution_stats.source_paths(root)
    mtime = evolution_stats.newest_mtime(paths)
    if _evo_cache['data'] is None or _evo_cache['mtime'] != mtime:
        _evo_cache['data'] = evolution_stats.build_evolution_stats(root)
        _evo_cache['mtime'] = mtime
    return _evo_cache['data']

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
STATIC_DIR = os.path.join(HERE, 'dashboard')


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec='seconds').replace('+00:00', 'Z')


def combined_status(root, refresh_ms):
    out_dir = os.path.join(root, 'src', 'pilot', 'output')
    release_dir = os.path.join(root, 'release')
    paths = {
        'window_status': os.path.join(out_dir, 'window_status.json'),
        'audit_report': os.path.join(out_dir, 'audit_window.report.json'),
        'window_ledger': os.path.join(out_dir, 'window_ledger.jsonl'),
        'dashboard_events': os.path.join(out_dir, 'dashboard_events.jsonl'),
        'coordinator': os.path.join(out_dir, 'coordinator', 'dashboard.json'),
        'gate_snapshot': os.path.join(release_dir, 'gate_status_snapshot.json'),
        'requeue': os.path.join(out_dir, 'requeue.keys.txt'),
        'judge_sample': os.path.join(out_dir, 'judge_sample.keys.txt'),
    }
    window_status = window_common.read_json(paths['window_status'])
    audit_report = window_common.read_json(paths['audit_report'])
    gate_snapshot = window_common.read_json(paths['gate_snapshot'])
    coordinator = window_common.read_json(paths['coordinator'])
    requeue_result = window_common.read_lines_result(paths['requeue'])
    judge_sample_result = window_common.read_lines_result(paths['judge_sample'])
    requeue = [line for line in requeue_result['lines'] if line.strip()]
    judge_sample = [line for line in judge_sample_result['lines'] if line.strip()]
    return {
        'generated_at': utc_now(),
        'root': root,
        'refresh_ms': refresh_ms,
        'run_status': window_status,
        'audit_report': audit_report,
        'print_gates': gate_snapshot,
        'requeue_keys': requeue,
        'judge_sample_keys': judge_sample,
        'queue_read_errors': {
            'requeue': requeue_result.get('error'),
            'judge_sample': judge_sample_result.get('error'),
        },
        'ledger': window_common.tail_jsonl(paths['window_ledger'], limit=30),
        'events': read_events(limit=80, log_path=paths['dashboard_events']),
        'coordinator': coordinator,
        'freshness': {name: window_common.file_info(path) for name, path in paths.items()},
    }


class DashboardHandler(BaseHTTPRequestHandler):
    server_version = 'RussianTranslationDashboard/0.1'

    def log_message(self, fmt, *args):
        print('%s - - [%s] %s' %
              (self.address_string(), self.log_date_time_string(), fmt % args))

    def send_bytes(self, content, content_type, status=200):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path == '/api/status':
            payload = combined_status(self.server.dashboard_root,
                                      self.server.refresh_ms)
            self.send_bytes(json.dumps(payload, ensure_ascii=False, indent=1).encode('utf-8'),
                            'application/json; charset=utf-8')
            return
        if path == '/api/evolution':
            payload = evolution_payload(self.server.dashboard_root)
            self.send_bytes(json.dumps(payload, ensure_ascii=False, indent=1).encode('utf-8'),
                            'application/json; charset=utf-8')
            return
        if path == '/':
            path = '/index.html'
        rel = path.lstrip('/').replace('/', os.sep)
        full = os.path.abspath(os.path.join(STATIC_DIR, rel))
        static_root = os.path.abspath(STATIC_DIR)
        if full != static_root and not full.startswith(static_root + os.sep):
            self.send_bytes(b'not found\n', 'text/plain; charset=utf-8', 404)
            return
        if not os.path.exists(full) or not os.path.isfile(full):
            self.send_bytes(b'not found\n', 'text/plain; charset=utf-8', 404)
            return
        ctype = mimetypes.guess_type(full)[0] or 'application/octet-stream'
        with open(full, 'rb') as f:
            self.send_bytes(f.read(), ctype)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--root', default=DEFAULT_ROOT)
    ap.add_argument('--refresh-ms', type=int, default=5000)
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    server.dashboard_root = root
    server.refresh_ms = args.refresh_ms
    print('dashboard: http://%s:%d/' % (args.host, args.port))
    print('root     : %s' % root)
    server.serve_forever()


if __name__ == '__main__':
    main()
