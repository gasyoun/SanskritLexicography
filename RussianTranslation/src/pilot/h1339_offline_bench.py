#!/usr/bin/env python
r"""h1339_offline_bench.py — frozen offline prepare→audit→promote benchmark (H1339 Phase 1).

Measures the OFFLINE factory path end-to-end on a committed hermetic fixture, with zero
model calls and zero canonical-store access: every run gets a fresh sandbox (scratch
coordinator dir + scratch store + scratch TM sidecars via the PWG_COORDINATOR_DIR /
PWG_RU_STORE / PWG_RU_TM_DIR env overrides), drives the REAL production commands, and
records per-stage wall-clock:

  prepare        coordinator claim-injection + REAL `coordinator.prepare` per lease
                 (perf_preflight cost gate + gen_opt_harness2 harness/manifest generation
                 over the committed real-key inputs)
  normalize      deterministic wf_output construction from the prepared manifest (the
                 fake-model stand-in: german := exact per-sense source text, russian :=
                 deterministic copy — restored-markup counts match source BY CONSTRUCTION)
                 + `normalize_workflow_result`
  audit          REAL `coordinator record-output` per lease (begin-run + audit_window
                 subprocess with --execution-manifest + pending-backlog accounting)
  promotion-plan diagnostic: `promote_final_cards --dry-run --merge` over all clean outputs
  store-write    REAL `coordinator promote-ready` over ALL ready leases in one call — the
                 multi-lease promotion transaction (per-lease promote subprocess + backup +
                 atomic store replacement + TM rebuild + TM validate). THE Phase 3 target.
  total          prepare + normalize + audit + store-write (the production path; the
                 promotion-plan diagnostic is excluded from total)

Fixture (committed): src/pilot/fixtures/h1339_offline_bench/ — 12 REAL PWG keys' generated
raw/portrait inputs (real density/markup), split across 5 leases covering the mandated
cases: clean (fx1, fx5), requeue (fx2: one transient null + one defect), TM-hit (fx3: one
key pre-seeded in the scratch store so gen's TM auto-serve resolves it), presplit/heal
(fx4: ADAna, 22 senses → the sense-presplit fragment lane), multi-lease (all five promoted
in one promote-ready call). External model latency is EXCLUDED by construction (the
normalize stage is deterministic local work).

Protocol: --warmups 5 --runs 10 (H1339 Phase 1 contract); median + p95 per stage;
Python/platform identity, fixture content hash, seeded-store hash, and per-run output
hashes (semantic: volatile fields stripped) — all 10 measured runs must agree or the
report marks the run non-deterministic. Report: JSON (schema pwg.h1339_offline_bench.v1)
under src/pilot/output/ (gitignored), path printed.

Usage (from RussianTranslation/):
  python src/pilot/h1339_offline_bench.py --warmups 5 --runs 10 --json src/pilot/output/h1339_bench_baseline.json
  python src/pilot/h1339_offline_bench.py --runs 1            # smoke
"""
import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
REPO = os.path.dirname(SRC)
FIXTURE = os.path.join(HERE, 'fixtures', 'h1339_offline_bench')
INPUT_DIR = os.path.join(HERE, 'input')

for p in (HERE, SRC):
    if p not in sys.path:
        sys.path.insert(0, p)

from safe_filename import safe_name  # noqa: E402

# lease -> (case, [SLP1 keys]) — safe stems derived below. Every fixture case the handoff
# mandates is present; ADAna (22 senses) presplits via the sense budget (20).
LEASES = [
    ('fx1', 'clean',    ['ABAsa', 'AKu', 'ARava']),
    ('fx2', 'requeue',  ['AGAta', 'ADikya', 'ADI']),
    ('fx3', 'tm-hit',   ['AKyA', 'ADyAtmika']),
    ('fx4', 'presplit', ['ADAna']),
    ('fx5', 'clean',    ['ABIra', 'ADmAna', 'ADAra']),
]
TM_SEED_KEY = 'AKyA'            # pre-promoted into the scratch store -> gen TM auto-serves it
NULL_KEY = 'AGAta'              # the fake model returns no card -> transient requeue
DEFECT_KEY = 'ADikya'           # the fake model drops a sense -> coverage defect requeue
SEED_ROWS = 11600               # synthetic store rows ≈ live store scale (26 MB I/O realism)
GEN_MODEL_VERSION = 'claude-sonnet-5'

SENSE_SPLIT = re.compile(r'(?=\d+〉)')          # PWG sense marker '1〉' (U+3009)
LAYER_SPLIT = re.compile(r'^=== LAYER: .*$', re.M)

# Deterministic ASCII/umlaut -> Cyrillic transliteration for the fake "translation": the
# result is genuinely Cyrillic prose (CYR gate), contains no German words (residue
# detectors), and deliberately maps nothing to ё (H1305 no-ё gate). Latin diacritics
# (IAST/sigla like ṚV.) stay Latin — they are source markers, not prose.
_TR = {'a': 'а', 'b': 'б', 'c': 'ц', 'd': 'д', 'e': 'е', 'f': 'ф', 'g': 'г', 'h': 'х',
       'i': 'и', 'j': 'й', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о', 'p': 'п',
       'q': 'к', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у', 'v': 'в', 'w': 'в', 'x': 'кс',
       'y': 'ы', 'z': 'з', 'ä': 'я', 'ö': 'о', 'ü': 'ю', 'ß': 'сс'}
_TR.update({k.upper(): v.upper() for k, v in list(_TR.items())})
_PROTECTED = re.compile(r'(\{#.*?#\}|<ls\b.*?</ls>|<[^>]*>)', re.S)


def translit_ru(text):
    """Cyrillic-ify prose OUTSIDE protected markup spans ({#..#}, <ls>..</ls>, tags)."""
    out = []
    for i, part in enumerate(_PROTECTED.split(text)):
        if i % 2:                       # a protected span — byte-verbatim
            out.append(part)
        else:
            out.append(''.join(_TR.get(ch, ch) for ch in part))
    return ''.join(out)


def _span_depth_zero_points(text):
    """Character positions where {#..#} / <ls..</ls> / <..> spans are all closed."""
    points, depth_br, depth_ls, in_tag = set(), 0, 0, False
    i = 0
    while i < len(text):
        two = text[i:i + 2]
        if two == '{#':
            depth_br += 1; i += 2; continue
        if two == '#}':
            depth_br = max(0, depth_br - 1); i += 2; continue
        if text.startswith('<ls', i):
            depth_ls += 1; in_tag = True; i += 3; continue
        if text.startswith('</ls>', i):
            depth_ls = max(0, depth_ls - 1); i += 5; continue
        if text[i] == '<':
            in_tag = True; i += 1; continue
        if text[i] == '>':
            in_tag = False; i += 1
            if depth_br == 0 and depth_ls == 0:
                points.add(i)
            continue
        i += 1
        if depth_br == 0 and depth_ls == 0 and not in_tag and text[i - 1] in '.; ':
            points.add(i)
    return sorted(points)


def split_balanced(text, n):
    """Split `text` into EXACTLY n contiguous chunks whose concatenation is `text`, cutting
    first at sense markers, then padding at span-balanced sentence points, then merging
    from the tail. Never cuts inside a protected span, so no chunk carries torn markup."""
    n = max(1, n)
    cuts = [m.start() for m in SENSE_SPLIT.finditer(text) if m.start() > 0]
    cuts = sorted(set(cuts))[:n - 1]
    while len(cuts) < n - 1:
        # pad: bisect the largest gap at its nearest balanced point
        bounds = [0] + cuts + [len(text)]
        gaps = [(bounds[i + 1] - bounds[i], bounds[i], bounds[i + 1])
                for i in range(len(bounds) - 1)]
        gaps.sort(reverse=True)
        placed = False
        balanced = _span_depth_zero_points(text)
        for _size, lo, hi in gaps:
            mid = (lo + hi) // 2
            candidates = [p for p in balanced if lo < p < hi]
            if candidates:
                cut = min(candidates, key=lambda p: abs(p - mid))
                cuts = sorted(set(cuts + [cut]))
                placed = True
                break
        if not placed:
            break                        # cannot place more balanced cuts — accept fewer
    cuts = cuts[:n - 1]
    bounds = [0] + cuts + [len(text)]
    return [text[bounds[i]:bounds[i + 1]] for i in range(len(bounds) - 1)]


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def fixture_hash():
    rows = []
    for name in sorted(os.listdir(os.path.join(FIXTURE, 'input'))):
        rows.append('%s\t%s' % (name, sha256_file(os.path.join(FIXTURE, 'input', name))))
    return sha256_bytes('\n'.join(rows).encode('utf-8'))


def install_inputs():
    os.makedirs(INPUT_DIR, exist_ok=True)
    for name in os.listdir(os.path.join(FIXTURE, 'input')):
        shutil.copy2(os.path.join(FIXTURE, 'input', name), os.path.join(INPUT_DIR, name))


def build_seed_store(path, tm_seed_rows):
    """Deterministic synthetic store at live scale + the TM-seed key's real rows."""
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        for i in range(SEED_ROWS):
            f.write(json.dumps({
                'key1': 'seed%05d' % (i // 4), 'subcard': 'seed%05d~~h0_%02d_pwg00' % (i // 4, i % 4),
                'layer': 'pwg', 'iast': 'seed', 'h': 's', 'grammar': 'm.',
                'sense_tag': str(i % 4 + 1), 'ru': 'семя %d' % i, 'de': 'Same %d' % i,
                'review_status': 'ai_translated', 'reviewer': None,
                'provenance': {'model': 'sonnet', 'model_version': GEN_MODEL_VERSION,
                               'input_raw_sha256': sha256_bytes(b'seed%d' % (i // 4))},
            }, ensure_ascii=False) + '\n')
        for row in tm_seed_rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def fake_card(key, drop_last_sense=False):
    """One deterministic post-restore card for a committed input key.

    Sense COUNT comes from the coverage gate's own counter (audit_coverage.raw_markers),
    so raw-vs-card coverage matches BY CONSTRUCTION; german := contiguous span-balanced
    slices of the exact source text (all markup counts preserved); russian := the
    deterministic Cyrillic transliteration of the same slice (genuine Cyrillic, zero
    German residue, markup spans byte-verbatim)."""
    import audit_coverage as ac
    raw = open(os.path.join(INPUT_DIR, key + '.raw.txt'), encoding='utf-8').read()
    portrait = open(os.path.join(INPUT_DIR, key + '.portrait.json'), encoding='utf-8').read()
    expected = ac.raw_markers(key) or 1
    chunks = split_balanced(raw, expected)
    if drop_last_sense and len(chunks) > 2:
        # a REAL coverage defect: drop enough senses to cross the LOW band (gap >= 2)
        chunks = chunks[:max(1, len(chunks) - 3)] + [''.join(chunks[max(1, len(chunks) - 3):])]
        chunks = chunks[:-1]
    iast = key
    try:
        prow = json.loads(portrait)
        prow = prow[0] if isinstance(prow, list) else prow
        iast = prow.get('iast') or key
    except Exception:
        pass
    senses = [{'tag': str(i + 1), 'german': text, 'russian': translit_ru(text)}
              for i, text in enumerate(chunks)]
    return {'key1': key, 'iast': iast, 'notes': '', 'records': [{
        'h': '', 'grammar': '', 'senses': senses}]}


def fake_cards_for(manifest, drop_sense_key=None, null_key=None):
    """Deterministic wf result rows for a prepared manifest (see fake_card)."""
    results = []
    presplit = set(manifest['meta'].get('presplit_keys') or [])
    for key in manifest['meta']['selected_keys']:
        if null_key and key == null_key:
            results.append({'key': key, 'card': None})
            continue
        row = {'key': key, 'card': fake_card(key, drop_last_sense=(key == drop_sense_key))}
        if key in presplit:
            # the coverage gate exempts presplit rows from LOW/OVER (granular fragment rows)
            row['presplit'] = True
        results.append(row)
    return results


def store_semantic_hash(path):
    """Content hash of the store with per-run volatile provenance (generated_at — freshly
    stamped at every manifest generation) stripped; row order preserved (byte-stability of
    everything non-volatile is part of the claim)."""
    h = hashlib.sha256()
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            prov = row.get('provenance')
            if isinstance(prov, dict):
                prov.pop('generated_at', None)
            h.update(json.dumps(row, ensure_ascii=False, sort_keys=True).encode('utf-8'))
            h.update(b'\n')
    return h.hexdigest()


def semantic_hash(obj, volatile=('generated_at', 'ts', 'recorded_at', 'prepared_at',
                                 'promoted_at', 'claimed_at', 'expires_at', 'wf_file',
                                 'pipeline', 'cost', 'blocked_at', 'unblocked_at')):
    def strip(o):
        if isinstance(o, dict):
            return {k: strip(v) for k, v in sorted(o.items())
                    if k not in volatile and not (isinstance(v, str) and os.path.isabs(v))}
        if isinstance(o, list):
            return [strip(v) for v in o]
        return o
    return sha256_bytes(json.dumps(strip(obj), ensure_ascii=False,
                                   sort_keys=True).encode('utf-8'))


def run_cli(argv, env, cwd=REPO, check=True):
    proc = subprocess.run([sys.executable] + argv, cwd=cwd, env=env, text=True,
                          encoding='utf-8', capture_output=True)
    if check and proc.returncode:
        raise SystemExit('bench step failed (%s):\n%s' % (
            ' '.join(argv[:3]), (proc.stderr or proc.stdout)[-3000:]))
    return proc


def one_run(tag, keep=False):
    """One full pipeline pass in a fresh sandbox. Returns (timings, outputs) dicts."""
    sandbox = tempfile.mkdtemp(prefix='h1339bench_%s_' % tag)
    coord_dir = os.path.join(sandbox, 'coordinator')
    profile_dir = os.path.join(sandbox, 'profile')
    tm_dir = os.path.join(sandbox, 'tm')
    store = os.path.join(sandbox, 'store.jsonl')
    for d in (coord_dir, profile_dir, tm_dir):
        os.makedirs(d)
    env = dict(os.environ,
               PWG_COORDINATOR_DIR=coord_dir, PWG_RU_STORE=store, PWG_RU_TM_DIR=tm_dir,
               PYTHONIOENCODING='utf-8')

    # --- setup (untimed): seed store incl. the TM-seed key's rows, then build the TM ---
    tm_stem = safe_name(TM_SEED_KEY)
    tm_raw_sha = sha256_file(os.path.join(INPUT_DIR, tm_stem + '.raw.txt'))
    tm_card = fake_card(tm_stem)
    seed_rows = []
    for rec in tm_card['records']:
        for sense in rec['senses']:
            seed_rows.append({
                'key1': TM_SEED_KEY, 'subcard': tm_stem, 'layer': 'pwg',
                'iast': tm_card['iast'], 'h': rec['h'], 'grammar': rec['grammar'],
                'sense_tag': sense['tag'], 'ru': sense['russian'], 'de': sense['german'],
                'review_status': 'ai_translated', 'reviewer': None,
                'provenance': {'model': 'sonnet', 'model_version': GEN_MODEL_VERSION,
                               'input_raw_sha256': tm_raw_sha}})
    build_seed_store(store, seed_rows)
    run_cli([os.path.join(HERE, 'translation_memory.py'), 'build', '--lang', 'ru'], env)

    timings, outputs = {}, {'leases': {}}

    # --- prepare: claim-inject + REAL coordinator.prepare per lease -------------------
    t0 = time.perf_counter()
    inject = os.path.join(sandbox, 'inject.py')
    lease_specs = [(lid, [safe_name(k) for k in keys], keys) for lid, _case, keys in LEASES]
    with open(inject, 'w', encoding='utf-8') as f:
        f.write(
            'import json, os, sys\n'
            'sys.path.insert(0, %r)\n' % HERE
            + 'import coordinator\n'
            'coordinator.ensure_dirs()\n'
            'with coordinator.DirLock(coordinator.paths()["lock"]):\n'
            '    state = coordinator.load_state()\n'
            '    for lid, run_keys, keys in %r:\n' % lease_specs
            + '        state["leases"].append({"id": lid, "lane": "bench", "kind": "nominal",\n'
            '            "owner": "h1339bench", "target": "nominal:" + keys[0], "state": "claimed",\n'
            '            "claimed_at": coordinator.utc_now(), "expires_at": "2099-01-01T00:00:00Z",\n'
            '            "artifact_dir": coordinator.artifact_dir(lid),\n'
            '            "details": {"keys": keys, "run_keys": run_keys,\n'
            '                        "keymap": dict(zip(run_keys, keys))}})\n'
            '    save = coordinator.save_state(state)\n'
            'print("injected", len(coordinator.load_state()["leases"]))\n')
    run_cli([inject], env)
    for lid, _case, _keys in LEASES:
        run_cli([os.path.join(HERE, 'coordinator.py'), 'prepare', lid,
                 '--profile-slot', 'bench', '--config-dir', profile_dir,
                 '--executor-lane', 'serial-whole-card'], env)
    timings['prepare'] = time.perf_counter() - t0

    # --- normalize: deterministic wf_output per lease + canonical reorder -------------
    t0 = time.perf_counter()
    state = json.load(open(os.path.join(coord_dir, 'state.json'), encoding='utf-8'))
    by_id = {l['id']: l for l in state['leases']}
    wf_paths = {}
    for lid, case, _keys in LEASES:
        manifest = json.load(open(by_id[lid]['execution_manifest'], encoding='utf-8'))
        results = fake_cards_for(
            manifest,
            drop_sense_key=safe_name(DEFECT_KEY) if case == 'requeue' else None,
            null_key=safe_name(NULL_KEY) if case == 'requeue' else None)
        # TM-resolved / degenerate cards are pre-answered by the harness; carry them too.
        resolved = {r['key'] for r in results}
        for key, entry in (manifest.get('tm_resolved') or {}).items():
            if key not in resolved:
                results.append({'key': key, 'card': entry.get('card')})
        payload = {'meta': manifest['meta'], 'summary': {'cards': len(results)},
                   'results': sorted(results, key=lambda r: manifest['meta']['selected_keys'].index(r['key'])
                                     if r['key'] in manifest['meta']['selected_keys'] else 999)}
        wf = os.path.join(sandbox, 'wf_output.%s.json' % lid)
        with open(wf, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(payload, f, ensure_ascii=False)
        wf_paths[lid] = wf
    timings['normalize'] = time.perf_counter() - t0

    # --- audit: REAL begin-run + record-output per lease ------------------------------
    t0 = time.perf_counter()
    for lid, _case, _keys in LEASES:
        run_cli([os.path.join(HERE, 'coordinator.py'), 'begin-run', '--lease-id', lid], env)
        run_cli([os.path.join(HERE, 'coordinator.py'), 'record-output', lid, wf_paths[lid]],
                env, check=False)
    timings['audit'] = time.perf_counter() - t0

    state = json.load(open(os.path.join(coord_dir, 'state.json'), encoding='utf-8'))
    for lease in state['leases']:
        outputs['leases'][lease['id']] = {
            'state': lease.get('state'), 'audit_state': lease.get('audit_state'),
            'clean_count': lease.get('clean_count'),
            'pending_requeue': {k: sorted(v) for k, v in
                                (lease.get('pending_requeue') or {}).items()
                                if isinstance(v, list)},
        }

    # --- promotion-plan (diagnostic; excluded from total) -----------------------------
    t0 = time.perf_counter()
    clean_glob = os.path.join(coord_dir, 'artifacts', '*', 'wf_output.clean.*.json')
    run_cli([os.path.join(SRC, 'promote_final_cards.py'), '--dry-run', '--merge',
             '--glob', clean_glob, '--gen-model-version', GEN_MODEL_VERSION], env,
            check=False)
    timings['promotion-plan'] = time.perf_counter() - t0

    # --- store-write: REAL multi-lease promote-ready (incl. TM rebuild) ---------------
    t0 = time.perf_counter()
    promote = run_cli([os.path.join(HERE, 'coordinator.py'), 'promote-ready',
                       '--gen-model-version', GEN_MODEL_VERSION], env, check=False)
    timings['store-write'] = time.perf_counter() - t0
    outputs['promote_rc'] = promote.returncode
    outputs['promote_tail'] = (promote.stderr or promote.stdout)[-400:]

    timings['total'] = (timings['prepare'] + timings['normalize'] + timings['audit']
                        + timings['store-write'])

    outputs['store_sha256'] = sha256_file(store)
    outputs['store_semantic_sha256'] = store_semantic_hash(store)
    outputs['store_rows'] = sum(1 for ln in open(store, encoding='utf-8') if ln.strip())
    tm_path = os.path.join(tm_dir, 'translation_memory.ru.json')
    outputs['tm_sha256'] = (semantic_hash(json.load(open(tm_path, encoding='utf-8')))
                            if os.path.exists(tm_path) else None)
    state = json.load(open(os.path.join(coord_dir, 'state.json'), encoding='utf-8'))
    for lease in state['leases']:
        outputs['leases'][lease['id']]['final_state'] = lease.get('state')
    outputs['signature'] = semantic_hash({'leases': outputs['leases'],
                                          'store': outputs['store_semantic_sha256'],
                                          'rows': outputs['store_rows']})
    if not keep:
        shutil.rmtree(sandbox, ignore_errors=True)
    else:
        outputs['sandbox'] = sandbox
    return timings, outputs


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--warmups', type=int, default=5)
    ap.add_argument('--runs', type=int, default=10)
    ap.add_argument('--json', help='write the machine-readable report here')
    ap.add_argument('--keep-last', action='store_true', help='keep the last sandbox for inspection')
    a = ap.parse_args()

    install_inputs()
    fx_hash = fixture_hash()
    print('fixture: %d files, content hash %s' % (
        len(os.listdir(os.path.join(FIXTURE, 'input'))), fx_hash[:16]))

    for i in range(a.warmups):
        t, o = one_run('warm%d' % i)
        print('warmup %d/%d: total %.2fs (promote rc=%s)' % (
            i + 1, a.warmups, t['total'], o['promote_rc']))

    measured, signatures = [], set()
    last_outputs = None
    for i in range(a.runs):
        t, o = one_run('run%d' % i, keep=(a.keep_last and i == a.runs - 1))
        measured.append(t)
        signatures.add(o['signature'])
        last_outputs = o
        print('run %d/%d: prepare %.2f normalize %.2f audit %.2f plan %.2f store %.2f '
              'TOTAL %.2f  sig %s' % (i + 1, a.runs, t['prepare'], t['normalize'],
                                      t['audit'], t['promotion-plan'], t['store-write'],
                                      t['total'], o['signature'][:10]))

    stages = ['prepare', 'normalize', 'audit', 'promotion-plan', 'store-write', 'total']
    stats = {}
    for s in stages:
        xs = sorted(t[s] for t in measured)
        stats[s] = {'median_s': round(statistics.median(xs), 3),
                    'p95_s': round(xs[max(0, int(len(xs) * 0.95) - 1)]
                                   if len(xs) > 1 else xs[0], 3),
                    'min_s': round(xs[0], 3), 'max_s': round(xs[-1], 3)}
    deterministic = len(signatures) == 1
    print('\n=== H1339 offline bench (%d runs after %d warmups) ===' % (a.runs, a.warmups))
    for s in stages:
        print('  %-15s median %7.3fs   p95 %7.3fs' % (s, stats[s]['median_s'], stats[s]['p95_s']))
    print('  deterministic outputs: %s (%d signature(s))' % (deterministic, len(signatures)))
    if last_outputs:
        for lid, row in sorted(last_outputs['leases'].items()):
            print('  %s: audit=%s clean=%s final=%s pending=%s' % (
                lid, row.get('audit_state'), row.get('clean_count'),
                row.get('final_state'), row.get('pending_requeue')))

    if a.json:
        report = {
            'schema': 'pwg.h1339_offline_bench.v1',
            'protocol': {'warmups': a.warmups, 'runs': a.runs},
            'python': sys.version, 'platform': platform.platform(),
            'fixture_sha256': fx_hash, 'seed_rows': SEED_ROWS,
            'stages': stats, 'runs': measured,
            'deterministic': deterministic,
            'output_signatures': sorted(signatures),
            'last_outputs': last_outputs,
        }
        os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
        with open(a.json, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(report, f, ensure_ascii=False, indent=1)
        print('report: %s' % a.json)


if __name__ == '__main__':
    main()
