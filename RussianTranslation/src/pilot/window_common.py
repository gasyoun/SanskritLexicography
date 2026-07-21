#!/usr/bin/env python
"""Shared helpers for PWG RussianTranslation frequency-window operations."""
import datetime
import hashlib
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
REPO = os.path.dirname(SRC)
# H1386 P3f: PWG_INPUT_DIR lets a hermetic harness (h1339_offline_bench) point every
# pipeline stage at a SANDBOX input dir instead of the live shared src/pilot/input/.
# Unset (production) resolves exactly as before.
INP = os.environ.get('PWG_INPUT_DIR') or os.path.join(HERE, 'input')
OUT = os.path.join(HERE, 'output')
# Canonical live production harness (batched + masked, gen_opt_harness2.py).
# The legacy per-card run_pilot_wf.opt.js is deprecated; consumers point here.
OPT_HARNESS = os.path.join(HERE, 'run_pilot_wf.opt2.js')

if SRC not in sys.path:
    sys.path.insert(0, SRC)

from safe_filename import safe_name


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


# Cap-and-defer monster ledger (H304, MG ruling 07-07-2026). A card/window the
# perf_preflight cost gate flags over-ceiling is never bulk-run; it is appended here
# and excluded, accumulating for an occasional dedicated human-budgeted session.
# Committed (not gitignored): the ledger IS the queue of deferred work — losing it
# silently drops the most expensive (usually highest-value) entries.
DEFERRED_MONSTERS = os.path.join(HERE, 'deferred_monsters.jsonl')


def defer_monster(target, reason, estimate=None, source='perf_preflight', keys=None,
                  path=None):
    """Append one cap-and-defer row, deduped on (target, reason, UTC day) so a daily
    coordinator sweep can't flood the ledger. Returns the row, or None if deduped.
    Best-effort like failure_capture: a ledger write must never break a claim/prepare."""
    p = path or DEFERRED_MONSTERS
    today = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
    try:
        if os.path.exists(p):
            with open(p, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if (row.get('target') == target and row.get('reason') == reason
                            and row.get('date') == today):
                        return None
        row = {'schema': 'pwg.deferred_monsters.v1', 'date': today, 'target': target,
               'reason': reason, 'source': source, 'status': 'deferred'}
        if estimate:
            row['estimate'] = estimate
        if keys:
            row['keys'] = list(keys)
        with open(p, 'a', encoding='utf-8') as f:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
        return row
    except OSError as e:
        print('warning: deferred_monsters ledger write failed: %s' % e, file=sys.stderr)
        return None


def append_jsonl_line(path, obj):
    """Append ONE JSONL row as a single os.write() of a fully-encoded line (H336/H-3).

    A buffered text-mode 'a' handle can split one logical line across more than one
    underlying write() syscall (large lines, buffer-full flush), so two processes
    appending concurrently can interleave PARTWAY through a line and tear it — and
    translation_memory.load_denylist used to silently DROP a torn line, silently
    re-enabling TM reuse of gate-rejected content. A single write() to an O_APPEND
    fd is the OS-level append primitive: each row lands whole, even if another
    writer's row lands immediately before or after it."""
    data = (json.dumps(obj, ensure_ascii=False) + '\n').encode('utf-8')
    fd = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o644)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)


def atomic_write_text(path, content, encoding='utf-8'):
    """Replace ``path`` only after a complete, durable same-directory write."""
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.%s.' % os.path.basename(path),
                               suffix='.tmp', dir=directory)
    try:
        with os.fdopen(fd, 'w', encoding=encoding) as f:
            fd = None
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        if fd is not None:
            os.close(fd)
        try:
            os.remove(tmp)
        except FileNotFoundError:
            pass
        raise


def atomic_write_json(path, payload, indent=1):
    atomic_write_text(path, json.dumps(payload, ensure_ascii=False, indent=indent))


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def read_json(path, default=None):
    if not os.path.exists(path):
        return default
    try:
        return load_json(path)
    except Exception as e:
        return {'_error': str(e), '_path': path}


def write_json(path, payload, indent=1):
    atomic_write_json(path, payload, indent=indent)


def read_text(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def write_text(path, content):
    atomic_write_text(path, content)


def read_lines_result(path, limit=None):
    if not os.path.exists(path):
        return {'ok': True, 'lines': [], 'error': None, 'path': path}
    try:
        with open(path, encoding='utf-8') as f:
            lines = [line.rstrip('\n') for line in f]
    except Exception as e:
        return {'ok': False, 'lines': [], 'error': str(e), 'path': path}
    return {'ok': True, 'lines': lines[-limit:] if limit else lines,
            'error': None, 'path': path}


def read_lines(path, limit=None):
    return read_lines_result(path, limit=limit)['lines']


def write_lines(path, lines):
    atomic_write_text(path, '\n'.join(lines) + ('\n' if lines else ''))


def tail_jsonl(path, limit=40):
    if not os.path.exists(path):
        return []
    rows = []
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    rows.append({'malformed': line[:240]})
    except Exception as e:
        return [{'read_error': str(e), 'path': path}]
    return rows[-limit:]


def file_info(path):
    if not os.path.exists(path):
        return {'path': path, 'exists': False, 'mtime': None,
                'age_seconds': None, 'size': None}
    st = os.stat(path)
    age = max(0, int(datetime.datetime.now().timestamp() - st.st_mtime))
    return {'path': path, 'exists': True,
            'mtime': datetime.datetime.fromtimestamp(
                st.st_mtime, datetime.timezone.utc).isoformat(
                    timespec='seconds').replace('+00:00', 'Z'),
            'age_seconds': age, 'size': st.st_size}


def exact_file_exists(directory, name):
    try:
        return name in set(os.listdir(directory))
    except OSError:
        return False


def rootmap_path(root, input_dir=INP):
    for stem in (safe_name(root), root):
        path = os.path.join(input_dir, stem + '.rootmap.json')
        if os.path.exists(path):
            return path, stem
    return None, safe_name(root)


def rootmap_for(root, input_dir=INP):
    path, _stem = rootmap_path(root, input_dir=input_dir)
    return path


def input_paths(key, input_dir=INP):
    return (os.path.join(input_dir, key + '.raw.txt'),
            os.path.join(input_dir, key + '.portrait.json'))


def portrait_key_iast(portrait_text, key):
    """The display IAST a card should carry, read from its portrait sidecar text.

    ONE helper for both stitch twins (H1339 B02) and the degenerate pass-through lane --
    two independently-authored derivations is the C-01 drift class. Falls back to the key
    when the portrait is absent or unparseable; never raises."""
    try:
        p = json.loads(portrait_text)
    except Exception:
        return key
    rows = p if isinstance(p, list) else [p]
    for row in rows:
        if isinstance(row, dict):
            return row.get('iast') or row.get('key1') or key
    return key


def latest_status(out_dir=OUT):
    return read_json(os.path.join(out_dir, 'window_status.json'), default=None)


def latest_audit_report(out_dir=OUT):
    return read_json(os.path.join(out_dir, 'audit_window.report.json'), default=None)


def harness_meta(path=None):
    path = path or OPT_HARNESS
    if not os.path.exists(path):
        return {'ok': False, 'path': path, 'error': 'missing harness'}
    try:
        text = read_text(path)
        match = re.search(r'\bconst META = (\{.*?\})\s*(?:\n|$)', text)
        if not match:
            return {'ok': False, 'path': path, 'error': 'missing const META block'}
        meta = json.loads(match.group(1))
        st = os.stat(path)
        return {
            'ok': True,
            'path': path,
            'root': meta.get('root'),
            'safe_root': meta.get('safe_root'),
            'mode': meta.get('mode'),
            'selected_keys': meta.get('selected_keys') or [],
            'selected_key_count': len(meta.get('selected_keys') or []),
            'rootmap_sha256': meta.get('rootmap_sha256'),
            'generated_at': meta.get('generated_at'),
            'mtime': datetime.datetime.fromtimestamp(
                st.st_mtime, datetime.timezone.utc).isoformat(
                    timespec='seconds').replace('+00:00', 'Z'),
            'meta': meta,
        }
    except Exception as e:
        return {'ok': False, 'path': path, 'error': str(e)}
