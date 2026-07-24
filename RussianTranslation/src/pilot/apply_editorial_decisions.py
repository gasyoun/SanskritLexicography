#!/usr/bin/env python
"""Dry-run / gated apply of human editorial decisions over the PWG→RU store (H1556 Track D).

Wave-1 contract (IMPLEMENTATION Track D + VERIFICATION D1–D3):

  * Default is dry-run. Real apply requires env ``PWG_RU_ALLOW_EDITORIAL_APPLY=1``.
  * Missing decisions files → ``status: pending_votes``, exit 0 (not a failure).
  * Store is read-only unless the env gate is set AND ``--dry-run`` is false.
  * Never invents votes. Offline only — no paid generation.

Decision JSON shape (csl-pyutil / review-sheet export)::

  {"sheet_id": "...", "items": [{"id": "...", "decision": "approve|reject|defer", "note": "..."}]}

Item ``id`` formats seen in the house sheets: ``root|key|sense`` or a bare key.
This tool extracts the store key (middle field when pipe-delimited) and matches
``key`` / ``key1`` / ``headword`` on store rows.

Authored for H1556 by Grok 4.5. Offline only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Sequence

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from store_path import canonical_store  # noqa: E402

SCHEMA = 'pwg_ru.editorial_apply.v1'
ENV_ALLOW_APPLY = 'PWG_RU_ALLOW_EDITORIAL_APPLY'

DEFAULT_ABBREV = os.path.join(
    os.path.dirname(SRC), 'pwg_ru', 'eval', 'h1303_abbrev.decisions.json'
)
DEFAULT_STYLE = os.path.join(
    os.path.dirname(SRC), 'pwg_ru', 'eval', 'h1306_style.decisions.json'
)
DEFAULT_STORE = canonical_store(os.path.join(SRC, 'pwg_ru_translated.jsonl'))


def extract_store_key(item_id: str) -> str:
    """Best-effort store key from a sheet item id."""
    if not item_id or not isinstance(item_id, str):
        return ''
    parts = item_id.split('|')
    if len(parts) >= 2 and parts[1].strip():
        return parts[1].strip()
    return item_id.strip()


def load_decisions(path: str | None) -> dict[str, Any] | None:
    """Load a decisions.json; return None if path is missing/unreadable."""
    if not path:
        return None
    if not os.path.isfile(path):
        return None
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError('decisions file must be a JSON object: %s' % path)
    items = data.get('items')
    if items is None:
        data['items'] = []
    elif not isinstance(items, list):
        raise ValueError('decisions.items must be a list: %s' % path)
    return data


def iter_store_rows(store_path: str) -> list[dict[str, Any]]:
    """Read store JSONL (read-only). Missing file → empty list."""
    if not store_path or not os.path.isfile(store_path):
        return []
    rows: list[dict[str, Any]] = []
    with open(store_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def store_key_of(row: Mapping[str, Any]) -> str:
    for field in ('key', 'key1', 'headword'):
        val = row.get(field)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ''


def index_store(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    idx: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        k = store_key_of(row)
        if not k:
            continue
        idx.setdefault(k, []).append(dict(row))
    return idx


def normalize_decision(raw: Any) -> str:
    if raw is None:
        return ''
    s = str(raw).strip().lower()
    if s in ('approve', 'approved', 'accept', 'yes', 'y'):
        return 'approve'
    if s in ('reject', 'rejected', 'no', 'n'):
        return 'reject'
    if s in ('defer', 'deferred', 'skip', 'pending', ''):
        return 'defer'
    return s


def plan_delta(
    decision_sources: Sequence[tuple[str, Mapping[str, Any]]],
    store_index: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, Any]:
    """Pure plan: what would change given votes + observed store keys."""
    counts = {
        'approve': 0,
        'reject': 0,
        'defer': 0,
        'other': 0,
        'in_store': 0,
        'missing_from_store': 0,
        'would_stamp': 0,
    }
    samples_in: list[str] = []
    samples_missing: list[str] = []
    would_touch: list[dict[str, Any]] = []
    sources_summary: list[dict[str, Any]] = []

    for label, payload in decision_sources:
        items = list(payload.get('items') or [])
        src_counts = {'approve': 0, 'reject': 0, 'defer': 0, 'other': 0, 'n_items': len(items)}
        for item in items:
            if not isinstance(item, Mapping):
                continue
            decision = normalize_decision(item.get('decision'))
            if decision in src_counts:
                src_counts[decision] += 1
                counts[decision] += 1
            else:
                src_counts['other'] += 1
                counts['other'] += 1
            key = extract_store_key(str(item.get('id') or ''))
            if not key:
                continue
            present = key in store_index
            if present:
                counts['in_store'] += 1
                if len(samples_in) < 12:
                    samples_in.append(key)
            else:
                counts['missing_from_store'] += 1
                if len(samples_missing) < 12:
                    samples_missing.append(key)
            if decision in ('approve', 'reject') and present:
                counts['would_stamp'] += 1
                if len(would_touch) < 50:
                    would_touch.append({
                        'key': key,
                        'decision': decision,
                        'source': label,
                        'item_id': item.get('id'),
                        'note_preview': (str(item.get('note') or ''))[:120],
                    })
        sources_summary.append({
            'label': label,
            'sheet_id': payload.get('sheet_id'),
            'counts': src_counts,
        })

    return {
        'schema': SCHEMA,
        'counts': counts,
        'sources': sources_summary,
        'sample_keys_in_store': samples_in,
        'sample_keys_missing': samples_missing,
        'would_touch': would_touch,
        'tokens_that_would_change': counts['would_stamp'],
    }


def apply_stamps(
    store_path: str,
    plan: Mapping[str, Any],
    *,
    dry_run: bool,
) -> dict[str, Any]:
    """Stamp editorial_decision on matching rows. Refuses without env when not dry-run."""
    if dry_run:
        return {
            'status': 'dry_run',
            'written': 0,
            'store_path': store_path,
            'plan_counts': plan.get('counts'),
        }

    if os.environ.get(ENV_ALLOW_APPLY) != '1':
        raise SystemExit(
            'refuse store write: set %s=1 to apply (wave-1 default is dry-run only)'
            % ENV_ALLOW_APPLY
        )

    touch_by_key = {t['key']: t for t in (plan.get('would_touch') or []) if t.get('key')}
    if not touch_by_key:
        return {
            'status': 'applied',
            'written': 0,
            'store_path': store_path,
            'note': 'no matching keys to stamp',
        }

    rows = iter_store_rows(store_path)
    written = 0
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    out_lines: list[str] = []
    for row in rows:
        k = store_key_of(row)
        if k in touch_by_key:
            row = dict(row)
            row['editorial_decision'] = touch_by_key[k]['decision']
            row['editorial_decision_at'] = now
            row['editorial_decision_source'] = touch_by_key[k].get('source')
            written += 1
        out_lines.append(json.dumps(row, ensure_ascii=False))

    tmp = store_path + '.editorial.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out_lines))
        if out_lines:
            f.write('\n')
    os.replace(tmp, store_path)
    return {
        'status': 'applied',
        'written': written,
        'store_path': store_path,
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    counts = report.get('counts') or {}
    lines = [
        '# Editorial decisions delta',
        '',
        '- status: `%s`' % report.get('status'),
        '- dry_run: `%s`' % report.get('dry_run'),
        '- tokens_that_would_change: **%s**' % report.get('tokens_that_would_change', counts.get('would_stamp', 0)),
        '- approve/reject/defer: %s / %s / %s'
        % (counts.get('approve', 0), counts.get('reject', 0), counts.get('defer', 0)),
        '- in_store / missing: %s / %s'
        % (counts.get('in_store', 0), counts.get('missing_from_store', 0)),
        '',
        '## Sample keys in store',
        '',
    ]
    samples = report.get('sample_keys_in_store') or []
    if samples:
        for k in samples:
            lines.append('- `%s`' % k)
    else:
        lines.append('- _(none)_')
    lines.extend(['', '## Sample keys missing from store', ''])
    missing = report.get('sample_keys_missing') or []
    if missing:
        for k in missing:
            lines.append('- `%s`' % k)
    else:
        lines.append('- _(none)_')
    lines.append('')
    return '\n'.join(lines)


def build_report(
    *,
    abbrev_path: str | None,
    style_path: str | None,
    store_path: str,
    dry_run: bool,
    extra_paths: Sequence[str] | None = None,
) -> dict[str, Any]:
    sources: list[tuple[str, Mapping[str, Any]]] = []
    missing_paths: list[str] = []

    for label, path in (
        ('h1303_abbrev', abbrev_path),
        ('h1306_style', style_path),
    ):
        data = load_decisions(path)
        if data is None:
            if path:
                missing_paths.append(path)
            continue
        sources.append((label, data))

    if extra_paths:
        for i, path in enumerate(extra_paths):
            data = load_decisions(path)
            if data is None:
                missing_paths.append(path)
                continue
            sources.append(('extra_%d' % i, data))

    if not sources:
        return {
            'schema': SCHEMA,
            'status': 'pending_votes',
            'dry_run': dry_run,
            'missing_paths': missing_paths,
            'message': 'no decisions files present; human votes still outstanding',
            'counts': {
                'approve': 0,
                'reject': 0,
                'defer': 0,
                'other': 0,
                'in_store': 0,
                'missing_from_store': 0,
                'would_stamp': 0,
            },
            'tokens_that_would_change': 0,
            'sample_keys_in_store': [],
            'sample_keys_missing': [],
            'would_touch': [],
            'sources': [],
            'store_path': store_path,
        }

    store_index = index_store(iter_store_rows(store_path))
    plan = plan_delta(sources, store_index)
    apply_result = apply_stamps(store_path, plan, dry_run=dry_run)
    report = {
        **plan,
        'status': apply_result.get('status', 'dry_run'),
        'dry_run': dry_run,
        'store_path': store_path,
        'missing_paths': missing_paths,
        'apply': apply_result,
        'tokens_that_would_change': plan['counts']['would_stamp'],
    }
    return report


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description='Dry-run (default) editorial decisions over pwg_ru store (H1556).',
    )
    ap.add_argument(
        '--abbrev-decisions',
        default=DEFAULT_ABBREV,
        help='path to h1303_abbrev.decisions.json (default: pwg_ru/eval/...)',
    )
    ap.add_argument(
        '--style-decisions',
        default=DEFAULT_STYLE,
        help='path to h1306_style.decisions.json (default: pwg_ru/eval/...)',
    )
    ap.add_argument(
        '--decisions',
        action='append',
        default=[],
        help='extra decisions.json path (repeatable)',
    )
    ap.add_argument(
        '--store',
        default=DEFAULT_STORE,
        help='store JSONL path (read-only unless apply gate set)',
    )
    ap.add_argument(
        '--dry-run',
        dest='dry_run',
        action='store_true',
        default=True,
        help='plan only (default)',
    )
    ap.add_argument(
        '--no-dry-run',
        dest='dry_run',
        action='store_false',
        help='attempt apply (requires %s=1)' % ENV_ALLOW_APPLY,
    )
    ap.add_argument('--json-out', default='', help='write full JSON report here')
    ap.add_argument('--md-out', default='', help='write markdown delta here')
    args = ap.parse_args(list(argv) if argv is not None else None)

    report = build_report(
        abbrev_path=args.abbrev_decisions,
        style_path=args.style_decisions,
        store_path=args.store,
        dry_run=args.dry_run,
        extra_paths=args.decisions,
    )

    if args.json_out:
        parent = os.path.dirname(os.path.abspath(args.json_out))
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(args.json_out, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            f.write('\n')
    if args.md_out:
        parent = os.path.dirname(os.path.abspath(args.md_out))
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(args.md_out, 'w', encoding='utf-8') as f:
            f.write(render_markdown(report))

    print(json.dumps({
        'status': report.get('status'),
        'dry_run': report.get('dry_run'),
        'tokens_that_would_change': report.get('tokens_that_would_change'),
        'counts': report.get('counts'),
        'missing_paths': report.get('missing_paths'),
    }, ensure_ascii=False, indent=2))

    # pending_votes and dry_run success are exit 0; apply refusal raises SystemExit earlier.
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
