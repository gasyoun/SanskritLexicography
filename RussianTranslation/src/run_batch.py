#!/usr/bin/env python
"""pwg_ru production driver — batch the De→Ru translate+judge run.

The deterministic half of the scaled run (mask, harvest, restore, append-only
store). The LLM half (Sonnet translate + Opus judge) runs as a Claude Code
workflow on the Max subscription; this driver prepares its input and collects
its output. Resumable: `build` skips records already in the store.

  python run_batch.py build   <N>            → _batch_in.jsonl (next N undone)
  python run_batch.py collect <wf-output>    → restore + append to the store
  python run_batch.py status                 → progress + pass rate

Files (all gitignored, in this dir):
  _batch_in.jsonl          current batch input (one record per line, with i, placeholders)
  pwg_ru_translated.jsonl  append-only store: {i,key1,ru,verdict,ok,...}
"""
import json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import pwg_mask
import corpus_gate as cg
import assemble

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH_IN = os.path.join(HERE, '_batch_in.jsonl')
STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')
GERMAN = re.compile(r'[A-Za-zÄÖÜäöüß]{3,}')


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
            att = [{'source': g['source'], 'gloss': _clean(g['gloss'])[:110]} for g in indep]
            if kow:
                att.append({'source': 'KOW (reference)', 'gloss': _clean(kow[0])[:110]})
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
    raw = json.load(open(wf, encoding='utf-8'))
    res = raw.get('result', raw).get('results', raw.get('results', []))
    by_i = {r['i']: r for r in res if 'i' in r}
    batch = {json.loads(l)['i']: json.loads(l) for l in open(BATCH_IN, encoding='utf-8')}
    appended = ok = bad = mism = 0
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
            v = r.get('verdict', {})
            rec = {'ord': card['ord'], 'key1': card['key1'], 'key2': card['key2'], 'ru': ru,
                   'placeholders_ok': integrity, 'key_match': keymatch, 'verdict': v,
                   'ok': bool(v.get('ok')) and integrity and keymatch, 'severity': v.get('severity')}
            out.write(json.dumps(rec, ensure_ascii=False) + '\n')
            appended += 1
            ok += 1 if rec['ok'] else 0
            bad += 0 if rec['ok'] else 1
            mism += 0 if (integrity and keymatch) else 1
    print('collected %d → %s  (ok %d, flagged %d, placeholder-mismatch %d)'
          % (appended, os.path.basename(STORE), ok, bad, mism))


def cmd_status(args):
    if not os.path.exists(STORE):
        print('store empty'); return
    n = ok = sevsum = 0
    sev = {}
    for line in open(STORE, encoding='utf-8'):
        r = json.loads(line)
        n += 1
        ok += 1 if r.get('ok') else 0
        s = r.get('severity')
        if s:
            sev[s] = sev.get(s, 0) + 1
    print('translated cards in store: %d  | publishable (ok+placeholders): %d (%.0f%%)'
          % (n, ok, 100.0 * ok / max(n, 1)))
    print('judge severity histogram:', dict(sorted(sev.items())))


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    {'build': cmd_build, 'collect': cmd_collect, 'status': cmd_status}.get(
        sys.argv[1], lambda *_: print(__doc__))(sys.argv[2:])


if __name__ == '__main__':
    main()
