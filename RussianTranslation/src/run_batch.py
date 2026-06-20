#!/usr/bin/env python
"""pwg_ru production driver — batch the De→Ru translate+judge run.

The deterministic half of the scaled run (mask, harvest, restore, append-only
store). The LLM half (Sonnet translate + Opus judge) runs as a Claude Code
workflow on the Max subscription; this driver prepares its input and collects
its output. Resumable: `build` skips records already in the store.

  python run_batch.py build   <N>            → _batch_in.jsonl (next N undone)
  python run_batch.py collect <wf-output>    → restore + provenance + append to store
  python run_batch.py status                 → progress + pass rate + review state
  python run_batch.py review                 → emit _review_queue.jsonl (human worklist)
  python run_batch.py review_csv             → emit _review_queue.csv (spreadsheet view)
  python run_batch.py validate_review [csv]  → validate reviewer decisions
  python run_batch.py review_report [csv]    → write review_readiness_report.md
  python run_batch.py apply_review <csv>     → apply reviewer decisions to store
  python run_batch.py migrate_legacy         → backfill old store rows safely

Files (all gitignored, in this dir):
  _batch_in.jsonl          current batch input (one record per line, with i, placeholders)
  pwg_ru_translated.jsonl  append-only store: {i,key1,ru,verdict,ok,...}
"""
import csv, json, os, re, sys, glob, hashlib, subprocess, datetime, shutil
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import pwg_mask
import corpus_gate as cg
import assemble

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
BATCH_IN = os.path.join(HERE, '_batch_in.jsonl')
STORE = os.environ.get('PWG_RU_STORE') or os.path.join(HERE, 'pwg_ru_translated.jsonl')
REVIEW_Q = os.environ.get('PWG_RU_REVIEW_Q') or os.path.join(HERE, '_review_queue.jsonl')
REVIEW_CSV = os.environ.get('PWG_RU_REVIEW_CSV') or os.path.join(HERE, '_review_queue.csv')
REVIEW_REPORT = os.environ.get('PWG_RU_REVIEW_REPORT') or os.path.join(ROOT, 'review_readiness_report.md')
GERMAN = re.compile(r'[A-Za-zÄÖÜäöüß]{3,}')
REVIEW_DECISIONS = {'approved', 'human_reviewed', 'needs_review', 'reject'}
PRINT_READY = {'approved', 'human_reviewed'}

# --- provenance (FAIR R1.2 / PROV-O): every card records how it was produced,
# so the edition is reproducible and bisectable. ----------------------------
SCHEMA_VERSION = 'pwg_ru.card.v1'
TRANSLATE_MODEL = 'claude-sonnet-4-6'        # Max-subscription translate stage
JUDGE_MODEL = 'claude-opus-4-8'              # Max-subscription judge stage
PROMPTS_DIR = os.path.normpath(os.path.join(HERE, '..', 'pwg_ru_prompts'))


def _prompt_set_sha():
    files = sorted(glob.glob(os.path.join(PROMPTS_DIR, '*.txt')))
    if not files:
        return 'na'
    h = hashlib.sha256()
    for f in files:
        h.update(open(f, 'rb').read())
    return h.hexdigest()[:16]


def _pwg_commit():
    repo = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'csl-orig'))
    try:
        r = subprocess.run(['git', '-C', repo, 'rev-parse', '--short', 'HEAD'],
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or 'unknown'
    except Exception:
        return 'unknown'


def provenance(run_id, translate_model=None):
    return {'schema_version': SCHEMA_VERSION,
            'translate_model': translate_model or TRANSLATE_MODEL,
            'judge_model': JUDGE_MODEL,
            'prompt_set_sha': _prompt_set_sha(),
            'pwg_src_commit': _pwg_commit(),
            'run_id': run_id,
            'generated_at': datetime.datetime.now().isoformat(timespec='seconds')}


def done_ids():
    ids = set()
    if os.path.exists(STORE):
        with open(STORE, encoding='utf-8') as f:
            for line in f:
                try:
                    ids.add(json.loads(line)['ord'])
                except Exception:
                    pass
    return ids


def _clean(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()


def _ensure_parent(path):
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)


def attested_for(idx, key1, key2):
    indep, kow = cg.lookup(idx, key1, key2)
    att = [{'source': g['source'], 'code': g['code'], 'gloss': _clean(g['gloss'])[:110],
            'publishable': g.get('publishable', False)} for g in indep]
    if kow:
        att.append({'source': 'KOW (reference)', 'code': 'kow',
                    'gloss': _clean(kow[0])[:110], 'publishable': True})
    return att


def cmd_build(args):
    n = int(args[0]) if args else 30
    covered_only = 'covered' in args   # coverage-first: only records with dict/KOW reuse
    done = done_ids()
    idx = cg.load_index()
    written = skipped = 0
    with open(BATCH_IN, 'w', encoding='utf-8', newline='') as o:
        for ordi, buf in enumerate(pwg_mask.records()):
            if ordi in done:
                continue
            k1, k2, body = pwg_mask.parse(buf)
            sk, ph, st = pwg_mask.mask(body)
            translatable = GERMAN.search(re.sub(r'\{T\d+\}', ' ', sk))
            if pwg_mask.restore(sk, ph) != body or not translatable or len(sk) > 1600:
                skipped += 1
                continue
            indep, kow = cg.lookup(idx, k1, k2)
            if covered_only and not (indep or kow):
                skipped += 1
                continue
            att = attested_for(idx, k1, k2)
            o.write(json.dumps({'i': written, 'ord': ordi, 'key1': k1, 'key2': k2,
                                'iast': assemble.iast(k1), 'de_skeleton': sk,
                                'placeholders': ph, 'attested': att},
                               ensure_ascii=False) + '\n')
            written += 1
            if written >= n:
                break
    print('batch: %d records → %s (skipped %d lossy/no-German along the way)'
          % (written, os.path.basename(BATCH_IN), skipped))


def cmd_collect(args):
    wf = args[0]
    model = args[1] if len(args) > 1 else None      # optional translate-model override
    raw = json.load(open(wf, encoding='utf-8'))
    res = raw.get('result', raw).get('results', raw.get('results', []))
    by_i = {r['i']: r for r in res if 'i' in r}
    batch = {json.loads(l)['i']: json.loads(l) for l in open(BATCH_IN, encoding='utf-8')}
    prov = provenance(os.path.splitext(os.path.basename(wf))[0], model)
    appended = ok = bad = mism = needs = 0
    with open(STORE, 'a', encoding='utf-8', newline='') as out:
        for i, card in batch.items():
            r = by_i.get(i)
            if not r:
                continue
            ph = card['placeholders']
            src = set(re.findall(r'\{T(\d+)\}', card['de_skeleton']))
            got = set(re.findall(r'\{T(\d+)\}', r['ru_skeleton']))
            integrity = src == got
            ru = re.sub(r'\{T(\d+)\}',
                        lambda m: ph[int(m.group(1)) - 1] if 0 < int(m.group(1)) <= len(ph) else m.group(0),
                        r['ru_skeleton'])
            keymatch = r.get('key1') == card['key1']
            v = r.get('verdict') or {}   # judge may be null (e.g. rate-limited) → treat as pending
            good = bool(v.get('ok')) and integrity and keymatch
            sev = v.get('severity')
            # review state machine: an LLM verdict is never final for print —
            # anything failing or sev>=3 or with a structural mismatch queues for a human.
            review_status = 'judged' if (good and (sev or 0) < 3) else 'needs_review'
            rec = {'ord': card['ord'], 'key1': card['key1'], 'key2': card['key2'], 'ru': ru,
                   'placeholders_ok': integrity, 'key_match': keymatch, 'verdict': v,
                   'ok': good, 'severity': sev,
                   'review_status': review_status, 'reviewer': None,
                   'attested': card.get('attested', []),     # persist the reuse evidence (rec 1)
                   'provenance': prov}
            out.write(json.dumps(rec, ensure_ascii=False) + '\n')
            appended += 1
            ok += 1 if good else 0
            bad += 0 if good else 1
            mism += 0 if (integrity and keymatch) else 1
            needs += 1 if review_status == 'needs_review' else 0
    print('collected %d → %s  (ok %d, flagged %d, placeholder-mismatch %d, needs_review %d)'
          % (appended, os.path.basename(STORE), ok, bad, mism, needs))
    print('  provenance: %s @ %s (pwg %s, prompts %s)'
          % (prov['translate_model'], prov['generated_at'], prov['pwg_src_commit'], prov['prompt_set_sha']))


def cmd_status(args):
    if not os.path.exists(STORE):
        print('store empty'); return
    n = ok = final = 0
    sev = {}
    rs = {}
    for line in open(STORE, encoding='utf-8'):
        r = json.loads(line)
        n += 1
        machine_ok = bool(r.get('ok') and r.get('placeholders_ok') and r.get('key_match'))
        ok += 1 if machine_ok else 0
        status = r.get('review_status') or 'unstamped'
        rs[status] = rs.get(status, 0) + 1
        final += 1 if status in PRINT_READY and machine_ok else 0
        s = r.get('severity')
        if s:
            sev[s] = sev.get(s, 0) + 1
    print('translated cards in store: %d  | machine-ok (ok+placeholders+key): %d (%.0f%%)'
          % (n, ok, 100.0 * ok / max(n, 1)))
    print('print-ready (human-reviewed/approved + machine-ok): %d (%.0f%%)'
          % (final, 100.0 * final / max(n, 1)))
    print('judge severity histogram:', dict(sorted(sev.items())))
    print('review status:', dict(sorted(rs.items())))


def cmd_review(args):
    """Emit the human-review worklist: every card the LLM could not clear,
    sorted by severity, evidence inlined. The exporter gates print on a human
    advancing these to 'approved' (Human-in-the-loop QA; ELEXIS/Lexonomy)."""
    if not os.path.exists(STORE):
        print('store empty'); return
    items = []
    for line in open(STORE, encoding='utf-8'):
        r = json.loads(line)
        status = r.get('review_status')
        if status is None:                 # legacy card → derive from ok+severity
            status = 'judged' if (r.get('ok') and (r.get('severity') or 0) < 3) else 'needs_review'
        if status in ('judged', 'human_reviewed', 'approved'):
            continue                       # cleared (by LLM or human); not in the queue
        v = r.get('verdict') or {}
        items.append({'ord': r['ord'], 'key1': r['key1'], 'key2': r.get('key2'),
                      'severity': r.get('severity') or v.get('severity') or 0,
                      'reason': v.get('reason') or v.get('issues') or v.get('note') or '',
                      'key_match': r.get('key_match'), 'placeholders_ok': r.get('placeholders_ok'),
                      'review_status': r.get('review_status', 'unstamped'),
                      'ru': r.get('ru', ''), 'attested': r.get('attested', [])})
    items.sort(key=lambda x: -(x['severity'] or 0))
    _ensure_parent(REVIEW_Q)
    with open(REVIEW_Q, 'w', encoding='utf-8', newline='') as o:
        for it in items:
            o.write(json.dumps(it, ensure_ascii=False) + '\n')
    print('review queue: %d card(s) need a human → %s (sorted by severity)'
          % (len(items), os.path.basename(REVIEW_Q)))
    for it in items[:15]:
        print('  sev%s  ord=%s  %s  key_match=%s ph_ok=%s  %s'
              % (it['severity'], it['ord'], it['key1'], it['key_match'],
                 it['placeholders_ok'], (it['reason'] or '')[:60]))


def _attested_summary(attested):
    bits = []
    for a in attested or []:
        source = a.get('source') or a.get('code') or '?'
        gloss = _clean(a.get('gloss'))[:80]
        bits.append('%s: %s' % (source, gloss))
    return ' | '.join(bits)


def cmd_review_csv(args):
    """Emit a spreadsheet-friendly view of the existing human-review queue.
    Does not change review_status/reviewer/decision; those blank columns are for
    humans to fill in a copy of the CSV."""
    if not os.path.exists(REVIEW_Q):
        print('no %s — run: python run_batch.py review' % os.path.basename(REVIEW_Q))
        return
    fields = ['severity', 'ord', 'key1', 'key2', 'review_status',
              'key_match', 'placeholders_ok', 'reason', 'attested',
              'ru', 'reviewer_id', 'decision', 'edit', 'notes']
    n = 0
    _ensure_parent(REVIEW_CSV)
    with open(REVIEW_Q, encoding='utf-8') as inp, \
            open(REVIEW_CSV, 'w', encoding='utf-8-sig', newline='') as out:
        w = csv.DictWriter(out, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for line in inp:
            if not line.strip():
                continue
            r = json.loads(line)
            w.writerow({
                'severity': r.get('severity'),
                'ord': r.get('ord'),
                'key1': r.get('key1'),
                'key2': r.get('key2'),
                'review_status': r.get('review_status'),
                'key_match': r.get('key_match'),
                'placeholders_ok': r.get('placeholders_ok'),
                'reason': r.get('reason') or '',
                'attested': _attested_summary(r.get('attested')),
                'ru': r.get('ru') or '',
                'reviewer_id': '',
                'decision': '',
                'edit': '',
                'notes': '',
            })
            n += 1
    print('review CSV: %d card(s) → %s' % (n, os.path.basename(REVIEW_CSV)))


def _read_review_csv(path):
    rows = []
    with open(path, encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            if not any((v or '').strip() for v in row.values()):
                continue
            rows.append(row)
    return rows


def _load_store_rows():
    rows = []
    if not os.path.exists(STORE):
        return rows
    with open(STORE, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _review_validation(rows):
    errors = []
    decisions = {}
    for i, row in enumerate(rows, 2):  # header is line 1
        raw_ord = (row.get('ord') or '').strip()
        if not raw_ord.isdigit():
            errors.append('line %d: ord must be an integer' % i)
            continue
        ord_ = int(raw_ord)
        decision = (row.get('decision') or '').strip()
        reviewer = (row.get('reviewer_id') or '').strip()
        edit = (row.get('edit') or '').strip()
        if not decision:
            continue                    # blank = not reviewed yet
        if decision not in REVIEW_DECISIONS:
            errors.append('line %d ord=%d: bad decision %r' % (i, ord_, decision))
        if not reviewer:
            errors.append('line %d ord=%d: reviewer_id required for decision' % (i, ord_))
        if decision in PRINT_READY and (row.get('key_match') != 'True' or row.get('placeholders_ok') != 'True'):
            errors.append('line %d ord=%d: cannot mark non-integral row print-ready' % (i, ord_))
        if decision in PRINT_READY and edit:
            pass                        # edit is optional; accepted when reviewer fixed text
        decisions[ord_] = {'decision': decision, 'reviewer': reviewer,
                           'edit': edit, 'notes': (row.get('notes') or '').strip()}
    return errors, decisions


def _machine_ok(row):
    return bool(row.get('ok') and row.get('placeholders_ok') and row.get('key_match'))


def _csv_machine_ok(row):
    return (row.get('key_match') == 'True' and row.get('placeholders_ok') == 'True')


def _review_summary(rows, decisions, errors, store):
    by_ord = {r.get('ord'): r for r in store}
    counts = {
        'rows': len(rows),
        'blank': 0,
        'decisions': 0,
        'print_ready_candidate': 0,
        'reject': 0,
        'needs_review': 0,
        'malformed': len(errors),
        'non_machine_ok_approvals': 0,
        'applied_in_store': 0,
    }
    pending = []
    top = []
    for row in rows:
        raw_ord = (row.get('ord') or '').strip()
        decision = (row.get('decision') or '').strip()
        if not decision:
            counts['blank'] += 1
            try:
                sev = int(row.get('severity') or 0)
            except ValueError:
                sev = 0
            pending.append((sev, raw_ord, row.get('key1') or '', row.get('reason') or ''))
            continue
        counts['decisions'] += 1
        if decision in PRINT_READY:
            counts['print_ready_candidate'] += 1
            if not _csv_machine_ok(row):
                counts['non_machine_ok_approvals'] += 1
        elif decision == 'reject':
            counts['reject'] += 1
        elif decision == 'needs_review':
            counts['needs_review'] += 1

    for r in store:
        if r.get('review_status') in PRINT_READY and _machine_ok(r):
            counts['applied_in_store'] += 1
    top = sorted(pending, reverse=True)[:20]
    return counts, top, by_ord


def cmd_validate_review(args):
    path = args[0] if args else REVIEW_CSV
    if not os.path.exists(path):
        sys.exit('no %s — run: python run_batch.py review_csv' % path)
    rows = _read_review_csv(path)
    errors, decisions = _review_validation(rows)
    store = _load_store_rows()
    by_ord = {r.get('ord'): r for r in store}
    missing = sorted(o for o in decisions if o not in by_ord)
    errors.extend('ord=%d: not found in store' % o for o in missing)
    counts, _, _ = _review_summary(rows, decisions, errors, store)
    print('review CSV rows: %(rows)d | blank: %(blank)d | decisions: %(decisions)d' % counts)
    print('  print-ready candidates: %(print_ready_candidate)d | reject: %(reject)d | needs_review: %(needs_review)d' % counts)
    print('  malformed: %(malformed)d | non-machine-ok approvals: %(non_machine_ok_approvals)d | already applied print-ready: %(applied_in_store)d' % counts)
    if errors:
        for e in errors[:50]:
            print('  ERROR:', e)
        sys.exit('review validation failed: %d error(s)' % len(errors))
    machine_ok = {r.get('ord') for r in store
                  if r.get('ok') and r.get('placeholders_ok') and r.get('key_match')}
    approved = {o for o, d in decisions.items() if d['decision'] in PRINT_READY}
    print('review validation OK: %d print-ready decision(s), %d machine-ok row(s) in store'
          % (len(approved), len(machine_ok)))


def cmd_review_report(args):
    path = args[0] if args else REVIEW_CSV
    if not os.path.exists(path):
        sys.exit('no %s — run: python run_batch.py review_csv' % path)
    rows = _read_review_csv(path)
    errors, decisions = _review_validation(rows)
    store = _load_store_rows()
    by_ord = {r.get('ord'): r for r in store}
    missing = sorted(o for o in decisions if o not in by_ord)
    errors.extend('ord=%d: not found in store' % o for o in missing)
    counts, top, _ = _review_summary(rows, decisions, errors, store)
    lines = [
        '# Review readiness report',
        '',
        '| metric | count |',
        '|---|---:|',
        '| CSV rows | %(rows)d |' % counts,
        '| blank reviewer decisions | %(blank)d |' % counts,
        '| non-blank decisions | %(decisions)d |' % counts,
        '| print-ready candidates | %(print_ready_candidate)d |' % counts,
        '| reject | %(reject)d |' % counts,
        '| needs_review | %(needs_review)d |' % counts,
        '| malformed rows/errors | %(malformed)d |' % counts,
        '| non-machine-ok approvals | %(non_machine_ok_approvals)d |' % counts,
        '| already applied print-ready rows | %(applied_in_store)d |' % counts,
        '',
        '## Top Pending Rows',
        '',
        '| severity | ord | key1 | reason |',
        '|---:|---:|---|---|',
    ]
    for sev, ord_, key1, reason in top:
        lines.append('| %s | %s | %s | %s |' % (
            sev, ord_, key1, _clean(reason).replace('|', '\\|')[:140]))
    if errors:
        lines += ['', '## Validation Errors', '']
        lines.extend('- %s' % e for e in errors[:50])
    _ensure_parent(REVIEW_REPORT)
    open(REVIEW_REPORT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('review readiness report → %s' % REVIEW_REPORT)


def cmd_apply_review(args):
    if not args:
        sys.exit('usage: python run_batch.py apply_review <review_csv>')
    path = args[0]
    rows = _read_review_csv(path)
    errors, decisions = _review_validation(rows)
    store = _load_store_rows()
    by_ord = {r.get('ord'): r for r in store}
    missing = sorted(o for o in decisions if o not in by_ord)
    errors.extend('ord=%d: not found in store' % o for o in missing)
    if errors:
        for e in errors[:50]:
            print('  ERROR:', e)
        sys.exit('review validation failed: %d error(s)' % len(errors))

    changed = 0
    reviewed_at = datetime.datetime.now().isoformat(timespec='seconds')
    for r in store:
        d = decisions.get(r.get('ord'))
        if not d or not d['decision']:
            continue
        decision = d['decision']
        if decision == 'reject':
            status = 'needs_review'
        else:
            status = decision
        if d['edit']:
            r['ru'] = d['edit']
        r['review_status'] = status
        r['reviewer'] = d['reviewer']
        r['human_review'] = {'decision': decision, 'notes': d['notes'],
                             'reviewed_at': reviewed_at}
        changed += 1
    if not changed:
        print('no non-blank reviewer decisions to apply')
        return

    backup = STORE + '.backup.' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    shutil.copy2(STORE, backup)
    tmp = STORE + '.tmp'
    _ensure_parent(STORE)
    with open(tmp, 'w', encoding='utf-8', newline='') as out:
        for r in store:
            out.write(json.dumps(r, ensure_ascii=False) + '\n')
    os.replace(tmp, STORE)
    print('applied %d review decision(s) → %s; backup: %s'
          % (changed, os.path.basename(STORE), os.path.basename(backup)))


def _legacy_provenance(migrated_at):
    return {
        'schema_version': 'pwg_ru.card.v0_legacy',
        'legacy': True,
        'complete': False,
        'reason': 'migrated from a pre-provenance store; original run metadata unavailable',
        'translate_model': 'unknown-legacy',
        'judge_model': 'unknown-legacy',
        'prompt_set_sha_at_migration': _prompt_set_sha(),
        'pwg_src_commit_at_migration': _pwg_commit(),
        'run_id': 'legacy-migration',
        'migrated_at': migrated_at,
    }


def cmd_migrate_legacy(args):
    """Backfill old store rows without pretending they are publication-ready."""
    if not os.path.exists(STORE):
        print('store empty'); return
    dry = '--dry-run' in args
    idx = cg.load_index()
    migrated_at = datetime.datetime.now().isoformat(timespec='seconds')
    rows, changed = [], 0
    review_counts = {}
    with open(STORE, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            row_changed = False
            if 'review_status' not in r or not r.get('review_status'):
                r['review_status'] = 'legacy_needs_review'
                row_changed = True
            if 'reviewer' not in r:
                r['reviewer'] = None
                row_changed = True
            if 'attested' not in r:
                r['attested'] = attested_for(idx, r.get('key1'), r.get('key2'))
                row_changed = True
            if 'provenance' not in r:
                r['provenance'] = _legacy_provenance(migrated_at)
                row_changed = True
            if row_changed:
                changed += 1
            review_counts[r.get('review_status', 'unstamped')] = review_counts.get(r.get('review_status', 'unstamped'), 0) + 1
            rows.append(r)
    if dry:
        print('would migrate %d/%d row(s); review status after migration: %s'
              % (changed, len(rows), dict(sorted(review_counts.items()))))
        return
    if not changed:
        print('store already migrated; review status: %s' % dict(sorted(review_counts.items())))
        return
    backup = STORE + '.backup.' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    shutil.copy2(STORE, backup)
    tmp = STORE + '.tmp'
    _ensure_parent(STORE)
    with open(tmp, 'w', encoding='utf-8', newline='') as out:
        for r in rows:
            out.write(json.dumps(r, ensure_ascii=False) + '\n')
    os.replace(tmp, STORE)
    print('migrated %d/%d row(s) → %s; backup: %s'
          % (changed, len(rows), os.path.basename(STORE), os.path.basename(backup)))
    print('review status:', dict(sorted(review_counts.items())))


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    {'build': cmd_build, 'collect': cmd_collect, 'status': cmd_status,
     'review': cmd_review, 'review_csv': cmd_review_csv,
     'validate_review': cmd_validate_review, 'review_report': cmd_review_report,
     'apply_review': cmd_apply_review,
     'migrate_legacy': cmd_migrate_legacy}.get(
        sys.argv[1], lambda *_: print(__doc__))(sys.argv[2:])


if __name__ == '__main__':
    main()
