#!/usr/bin/env python
"""Upstream-change watcher — monthly Cologne (git) + NWS (scrape) drift → stale worklist.

The pwg_ru source is the 5-layer all-in-one over LIVE upstreams: csl-orig (git —
PWG/PW/SCH/PWKVN, maintained by Jim/Dhaval) and NWS (Halle web resource). Either can
change a headword AFTER we translated it. This watcher DETECTS such changes and FLAGS
the affected promoted rows for re-run; it NEVER re-translates (guardrail — re-runs go
through the H179/H151 drain discipline: branch+PR, --no-tm, <=3-wide).

  python watch_upstream.py cologne            # cheap: git-diff the 4 csl-orig layers
  python watch_upstream.py cologne --baseline # (re)seed the per-layer last-seen state, no diff
  python watch_upstream.py nws                # heavier: re-fetch the PROMOTED headwords from Halle
  python watch_upstream.py nws --update-cache # also overwrite the cached NWS json when changed
  python watch_upstream.py report             # print the latest monthly report path + stale count
  python watch_upstream.py --selftest

Change detection reuses the H170 primitive: each promoted store row records
``provenance.input_raw_sha256`` (the sha of the exact raw input it was translated from).
When a headword's upstream layer moves, we emit its promoted rows + their stamped
input_raw_sha256 into ``upstream_changes/<YYYY-MM>.stale.json`` — the drain re-hashes the
regenerated input and re-runs the mismatches. csl-orig is READ-ONLY here (git log/show only).

Outputs (under ``pilot/upstream_changes/``):
  _state.json              per-layer last-seen commit + last nws run (incremental anchor)
  <YYYY-MM>.md             human report: per-layer changed-headword counts + stale worklist
  <YYYY-MM>.stale.json     machine worklist consumed by the drain handoffs
"""
import argparse
import collections
import datetime
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import dict_merge as dm            # noqa: E402
import pwg_mask                    # noqa: E402
import corpus_gate as cg          # noqa: E402

STORE = os.path.join(SRC, 'pwg_ru_translated.jsonl')
OUTDIR = os.path.join(HERE, 'upstream_changes')
STATE = os.path.join(OUTDIR, '_state.json')
CSL_ORIG = os.environ.get('PWG_RU_CSL_ORIG') or os.path.dirname(dm.V02)   # .../csl-orig (env-overridable for CI)
COLOGNE_CODES = [code for code, _, _ in dm.LAYERS]   # pwg, pw, sch, pwkvn
NWS_DIR = dm.NWS_DIR


# --- git (csl-orig read-only) -----------------------------------------------
def _git(*args):
    r = subprocess.run(['git', '-C', CSL_ORIG, *args],
                       capture_output=True, text=True, encoding='utf-8', timeout=60)
    return r


def git_head():
    r = _git('rev-parse', 'HEAD')
    return r.stdout.strip() if r.returncode == 0 else ''


def show_file(sha, rel):
    """File content at a commit, or None if the path/sha is absent there."""
    r = _git('show', '%s:%s' % (sha, rel))
    return r.stdout if r.returncode == 0 else None


# --- record parsing (mirrors dict_merge; operates on a string, not a path) --
def index_text(text):
    """{form_key: joined-record-text} for one csl-orig layer file's content.

    A headword may own several <L>..<LEND> records; we join them (sorted) so the
    comparison is order-stable. Header line is dropped from the body (like
    dict_merge.merged) so a pure header-id shuffle does not read as content drift."""
    if text is None:
        return {}
    buf, recs = [], collections.defaultdict(list)
    for line in text.split('\n'):
        line = line.rstrip('\r')
        if line.startswith('<L>'):
            buf = [line]
        elif line.startswith('<LEND>'):
            if buf:
                m = pwg_mask.HEADER_RE.match(buf[0])
                if m:
                    recs[cg.form_key(m.group(3))].append('\n'.join(buf[1:]))
            buf = []
        elif buf:
            buf.append(line)
    return {k: '\n'.join(sorted(v)) for k, v in recs.items()}


def changed_headwords(old_text, new_text):
    """form_keys whose record content differs between two versions of a layer file.
    Returns (changed, added, removed) sets of form_keys."""
    old, new = index_text(old_text), index_text(new_text)
    ok, nk = set(old), set(new)
    added = nk - ok
    removed = ok - nk
    changed = {k for k in (ok & nk) if old[k] != new[k]}
    return changed, added, removed


# --- promoted store index ---------------------------------------------------
def load_promoted():
    """{form_key: {layer: [(lineno, key1, input_raw_sha256), ...]}} over the promoted store."""
    idx = collections.defaultdict(lambda: collections.defaultdict(list))
    if not os.path.exists(STORE):
        return idx
    with open(STORE, encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            key1 = row.get('key1')
            if not key1:
                continue
            layer = row.get('layer') or 'pwg'
            prov = row.get('provenance') or {}
            idx[cg.form_key(key1)][layer].append(
                (lineno, key1, prov.get('input_raw_sha256')))
    return idx


# --- state / output ---------------------------------------------------------
def load_state():
    if os.path.exists(STATE):
        with open(STATE, encoding='utf-8') as f:
            return json.load(f)
    return {'schema': 'pwg_ru.upstream_watch_state.v1', 'cologne': {}, 'nws': {}}


def save_state(state):
    os.makedirs(OUTDIR, exist_ok=True)
    tmp = STATE + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write('\n')
    os.replace(tmp, STATE)


def month_paths(month=None):
    month = month or datetime.date.today().strftime('%Y-%m')
    os.makedirs(OUTDIR, exist_ok=True)
    return (os.path.join(OUTDIR, month + '.md'),
            os.path.join(OUTDIR, month + '.stale.json'), month)


def write_worklist(worklist, source, month=None, extra_md=None):
    """Emit / merge the monthly human report + machine stale-worklist.

    Idempotent per (source, month): re-running `cologne` in the same month replaces
    the cologne section of the stale.json, leaving an `nws` run's section intact."""
    md_path, json_path, month = month_paths(month)
    payload = {'schema': 'pwg_ru.upstream_stale.v1', 'month': month,
               'generated_at': datetime.datetime.now().isoformat(timespec='seconds'),
               'sources': {}}
    if os.path.exists(json_path):
        try:
            payload = json.load(open(json_path, encoding='utf-8'))
            payload['generated_at'] = datetime.datetime.now().isoformat(timespec='seconds')
        except Exception:
            pass
    payload.setdefault('sources', {})[source] = worklist
    tmp = json_path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write('\n')
    os.replace(tmp, json_path)
    _render_md(md_path, payload, extra_md)
    return md_path, json_path


def _render_md(md_path, payload, extra_md):
    today = datetime.date.today().strftime('%d-%m-%Y')
    total_stale = sum(len(wl.get('stale') or [])
                      for wl in payload['sources'].values())
    lines = ['# Upstream drift — %s' % payload['month'], '',
             '_Created: %s · Last updated: %s_' % (today, today), '',
             'Auto-generated by [`watch_upstream.py`](https://github.com/gasyoun/'
             'SanskritLexicography/blob/master/RussianTranslation/src/pilot/watch_upstream.py). '
             'Flags promoted pwg_ru rows whose upstream source changed since the last run; '
             'the watcher never re-translates — re-runs go through the drain handoffs.', '',
             '_Last run: %s_' % payload['generated_at'], '',
             '**%d promoted row-group(s) flagged stale this month.**' % total_stale, '']
    for source in ('cologne', 'nws'):
        wl = payload['sources'].get(source)
        if wl is None:
            continue
        lines.append('## %s' % source)
        lines.append('')
        if wl.get('note'):
            lines.append('> %s' % wl['note'])
            lines.append('')
        per = wl.get('per_layer') or {}
        if per:
            lines.append('| layer | changed | added | removed | promoted-rows flagged |')
            lines.append('|---|--:|--:|--:|--:|')
            for layer, c in sorted(per.items()):
                lines.append('| %s | %d | %d | %d | %d |'
                             % (layer, c.get('changed', 0), c.get('added', 0),
                                c.get('removed', 0), c.get('flagged_rows', 0)))
            lines.append('')
        stale = wl.get('stale') or []
        if stale:
            lines.append('### Stale worklist (re-translate via drain)')
            lines.append('')
            lines.append('| key1 | layer | store lines | input_raw_sha256 (stamped) |')
            lines.append('|---|---|---|---|')
            for s in stale:
                lines.append('| `%s` | %s | %s | `%s` |'
                             % (s['key1'], s['layer'], ','.join(map(str, s['lines'])),
                                (s.get('input_raw_sha256') or 'none')[:16]))
            lines.append('')
        else:
            lines.append('No promoted rows affected.')
            lines.append('')
    if extra_md:
        lines.append(extra_md)
    lines.append('')
    lines.append('_Dr. Mārcis Gasūns_')
    tmp = md_path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    os.replace(tmp, md_path)


def _stale_for(changed_keys, layer, promoted):
    """Promoted rows of `layer` whose form_key changed upstream → worklist entries."""
    stale = []
    for fk in sorted(changed_keys):
        rows = promoted.get(fk, {}).get(layer)
        if not rows:
            continue
        stale.append({
            'key1': rows[0][1],
            'form_key': fk,
            'layer': layer,
            'lines': [r[0] for r in rows],
            'input_raw_sha256': rows[0][2],
        })
    return stale


# --- cologne ----------------------------------------------------------------
def run_cologne(baseline=False, month=None):
    state = load_state()
    head = git_head()
    if not head:
        sys.exit('watch_upstream: cannot read csl-orig HEAD at %r' % CSL_ORIG)
    promoted = load_promoted()
    per_layer, all_stale = {}, []
    seeded = []
    for code in COLOGNE_CODES:
        rel = 'v02/%s/%s.txt' % (code, code)
        last = state['cologne'].get(code)
        if baseline or not last:
            state['cologne'][code] = head
            seeded.append(code)
            per_layer[code] = {'changed': 0, 'added': 0, 'removed': 0,
                               'flagged_rows': 0, 'baseline': True}
            continue
        if last == head:
            per_layer[code] = {'changed': 0, 'added': 0, 'removed': 0, 'flagged_rows': 0}
            continue
        old_text = show_file(last, rel)
        new_text = show_file(head, rel)
        changed, added, removed = changed_headwords(old_text, new_text)
        stale = _stale_for(changed | added, code, promoted)
        all_stale.extend(stale)
        per_layer[code] = {'changed': len(changed), 'added': len(added),
                           'removed': len(removed),
                           'flagged_rows': sum(len(s['lines']) for s in stale)}
        state['cologne'][code] = head
    worklist = {'per_layer': per_layer, 'stale': all_stale,
                'csl_orig_head': head}
    if seeded:
        worklist['note'] = ('Baseline seeded for %s at csl-orig %s — first future run '
                            'diffs against this.' % (', '.join(seeded), head[:12]))
    md_path, json_path = write_worklist(worklist, 'cologne', month)
    save_state(state)
    print('watch_upstream cologne: csl-orig HEAD %s' % head[:12])
    for code in COLOGNE_CODES:
        c = per_layer[code]
        tag = ' [baseline]' if c.get('baseline') else ''
        print('  %-6s changed=%d added=%d removed=%d → %d row(s) flagged%s'
              % (code, c['changed'], c['added'], c['removed'], c['flagged_rows'], tag))
    print('  stale worklist: %d headword-group(s) → %s' % (len(all_stale), os.path.basename(json_path)))
    return 0


# --- nws (promoted set only — polite; Halle may be down) --------------------
def diff_nws_card(fresh, cached):
    """True if the net-new NWS content changed between a fresh fetch and the cache.
    Compares the fragments we actually consume: nws text, has_nws_extra, sch text."""
    if cached is None:
        return True
    for k in ('nws', 'sch', 'has_nws_extra'):
        if (fresh.get(k) or '') != (cached.get(k) or ''):
            return True
    return False


def run_nws(update_cache=False, delay=None, month=None):
    promoted = load_promoted()
    # promoted key1 set (any layer) — the small, polite re-fetch scope
    key1s = sorted({r[1] for fk in promoted for layer in promoted[fk]
                    for r in promoted[fk][layer]})
    try:
        import nws_scrape
        import safe_filename
    except Exception as e:
        sys.exit('watch_upstream nws: cannot import nws_scrape (%s)' % e)
    delay = 3.0 if delay is None else delay
    try:
        sess, token = nws_scrape.session()
    except Exception as e:
        note = ('Halle NWS unreachable (%s) — skipped. Log to Uprava/SERVER_OUTAGES.md '
                'and retry later; Cologne diff is unaffected.' % e)
        write_worklist({'per_layer': {}, 'stale': [], 'note': note}, 'nws', month)
        print('watch_upstream nws: ' + note)
        return 2
    import time
    changed_keys, checked, errors = set(), 0, 0
    for i, key1 in enumerate(key1s):
        try:
            html = nws_scrape.fetch(sess, token, nws_scrape.iast(key1))
            nws_f = nws_scrape.frag('nws', html)
            pw_f = nws_scrape.frag('pw', html)
            sch_f = nws_scrape.frag('sch', html)
            # match nws_scrape's own has_nws_extra: net-new iff nws differs from pw AND sch
            fresh = {'nws': nws_f, 'sch': sch_f,
                     'has_nws_extra': bool(nws_f) and nws_f not in (pw_f, sch_f)}
            cached = _load_cached_nws(key1, safe_filename)
            if diff_nws_card(fresh, cached):
                changed_keys.add(cg.form_key(key1))
                if update_cache:
                    _save_cached_nws(key1, fresh, cached, safe_filename)
            checked += 1
        except Exception:
            errors += 1
        if i < len(key1s) - 1:
            time.sleep(delay)
    stale = _stale_for(changed_keys, 'nws', promoted)
    # a changed NWS headword may also carry non-nws promoted rows using that fragment;
    # flag the nws-layer rows (the ones sourced from NWS) — the conservative, correct set.
    worklist = {'per_layer': {'nws': {'changed': len(changed_keys), 'added': 0,
                                      'removed': 0, 'flagged_rows': sum(len(s['lines']) for s in stale)}},
                'stale': stale,
                'note': 'Re-fetched %d promoted headword(s); %d changed, %d fetch error(s). '
                        'Cache %s.' % (checked, len(changed_keys), errors,
                                       'updated' if update_cache else 'left untouched (read-only diff)')}
    md_path, json_path = write_worklist(worklist, 'nws', month)
    state = load_state()
    state['nws']['last_run'] = datetime.datetime.now().isoformat(timespec='seconds')
    state['nws']['checked'] = checked
    save_state(state)
    print('watch_upstream nws: checked %d, changed %d, errors %d → %d row-group(s) flagged'
          % (checked, len(changed_keys), errors, len(stale)))
    return 0


def _cached_nws_path(key1, safe_filename):
    for stem in safe_filename.candidate_names(cg.form_key(key1)):
        p = os.path.join(NWS_DIR, stem + '.json')
        if os.path.exists(p):
            return p
    # canonical target path (first candidate) for a new write
    return os.path.join(NWS_DIR, safe_filename.candidate_names(cg.form_key(key1))[0] + '.json')


def _load_cached_nws(key1, safe_filename):
    p = _cached_nws_path(key1, safe_filename)
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding='utf-8'))
        except Exception:
            return None
    return None


def _save_cached_nws(key1, fresh, cached, safe_filename):
    p = _cached_nws_path(key1, safe_filename)
    out = dict(cached or {})
    out['key1'] = key1
    out['iast'] = ''.join(cg._S2I.get(c, c) for c in cg.form_key(key1))
    out.update({'nws': fresh['nws'], 'sch': fresh['sch'],
                'has_nws_extra': fresh['has_nws_extra']})
    tmp = p + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False)
    os.replace(tmp, p)


def cmd_report(_args):
    md_path, json_path, month = month_paths()
    if not os.path.exists(json_path):
        print('watch_upstream: no report for %s yet' % month); return 0
    payload = json.load(open(json_path, encoding='utf-8'))
    n = sum(len(payload['sources'][s].get('stale', [])) for s in payload['sources'])
    print('latest report: %s' % md_path)
    print('  month=%s sources=%s stale-groups=%d'
          % (month, ','.join(payload['sources']), n))
    return 0


def selftest():
    # index_text: two <L> records, header shuffle vs body change
    v1 = '<L>1<pc>1<k1>agni<k2>agni\nbody-A\n<LEND>\n<L>2<pc>1<k1>vAyu<k2>vAyu\nbody-B\n<LEND>\n'
    v2 = '<L>1<pc>1<k1>agni<k2>agni\nbody-A-EDITED\n<LEND>\n<L>2<pc>1<k1>vAyu<k2>vAyu\nbody-B\n<LEND>\n'
    idx = index_text(v1)
    assert set(idx) == {cg.form_key('agni'), cg.form_key('vAyu')}, idx
    changed, added, removed = changed_headwords(v1, v2)
    assert changed == {cg.form_key('agni')} and not added and not removed, (changed, added, removed)
    # add + remove
    v3 = '<L>1<pc>1<k1>agni<k2>agni\nbody-A\n<LEND>\n<L>3<pc>1<k1>soma<k2>soma\nbody-C\n<LEND>\n'
    changed, added, removed = changed_headwords(v1, v3)
    assert added == {cg.form_key('soma')} and removed == {cg.form_key('vAyu')}, (added, removed)
    assert changed_headwords(v1, v1) == (set(), set(), set())
    # empty / None sides
    assert changed_headwords(None, v1)[1] == set(idx)   # all added
    # _stale_for: only rows of the matching layer are flagged
    promoted = {cg.form_key('agni'): {'pwg': [(10, 'agni', 'SHA_A')],
                                      'pw': [(11, 'agni', 'SHA_B')]}}
    stale = _stale_for({cg.form_key('agni')}, 'pwg', promoted)
    assert len(stale) == 1 and stale[0]['lines'] == [10] and stale[0]['input_raw_sha256'] == 'SHA_A', stale
    assert _stale_for({cg.form_key('agni')}, 'sch', promoted) == []   # no sch row → nothing
    # diff_nws_card
    assert diff_nws_card({'nws': 'x'}, None) is True
    assert diff_nws_card({'nws': 'x', 'sch': 's', 'has_nws_extra': True},
                         {'nws': 'x', 'sch': 's', 'has_nws_extra': True}) is False
    assert diff_nws_card({'nws': 'x2', 'sch': 's', 'has_nws_extra': True},
                         {'nws': 'x', 'sch': 's', 'has_nws_extra': True}) is True
    # markdown render round-trip (temp dir)
    import tempfile
    global OUTDIR, STATE
    _saved = (OUTDIR, STATE)
    OUTDIR = tempfile.mkdtemp(); STATE = os.path.join(OUTDIR, '_state.json')
    wl = {'per_layer': {'pwg': {'changed': 1, 'added': 0, 'removed': 0, 'flagged_rows': 1}},
          'stale': [{'key1': 'agni', 'form_key': 'agni', 'layer': 'pwg', 'lines': [10],
                     'input_raw_sha256': 'deadbeefdeadbeef'}]}
    md_path, json_path = write_worklist(wl, 'cologne', month='2026-07')
    body = open(md_path, encoding='utf-8').read()
    assert 'Upstream drift — 2026-07' in body and '`agni`' in body, body[:200]
    assert '1 promoted row-group(s) flagged stale' in body
    # nws section merges without dropping cologne
    write_worklist({'per_layer': {'nws': {'changed': 0, 'added': 0, 'removed': 0,
                                          'flagged_rows': 0}}, 'stale': []}, 'nws', month='2026-07')
    payload = json.load(open(json_path, encoding='utf-8'))
    assert set(payload['sources']) == {'cologne', 'nws'}, payload['sources']
    OUTDIR, STATE = _saved
    print('watch_upstream selftest OK')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd')
    c = sub.add_parser('cologne')
    c.add_argument('--baseline', action='store_true')
    c.add_argument('--month')
    n = sub.add_parser('nws')
    n.add_argument('--update-cache', action='store_true')
    n.add_argument('--delay', type=float)
    n.add_argument('--month')
    sub.add_parser('report')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.cmd == 'cologne':
        return run_cologne(baseline=args.baseline, month=args.month)
    if args.cmd == 'nws':
        return run_nws(update_cache=args.update_cache, delay=args.delay, month=args.month)
    if args.cmd == 'report':
        return cmd_report(args)
    ap.print_help(); return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
