#!/usr/bin/env python
r"""Content-addressed translation memory (TM) sidecar for the PWG bulk translation harness.

WHY THIS EXISTS
---------------
`resumeFromRunId` REPLAYS a Workflow verbatim (it re-serves the cached failure, it does
NOT re-roll a stochastic StructuredOutput failure), and a FRESH Workflow run re-translates
the whole card from scratch — discarding every fragment that already succeeded in a prior
run. So neither path reuses a prior run's *good* work (brU's first failure burned ~860k
tokens re-doing 12 of 13 already-good fragments). Card-level `--merge` in
`save_and_audit`/`promote_final_cards` preserves an already-promoted card in the STORE, but
only if the operator scopes `--keys` to the missing ones by hand, and it is keyed on the
sub-card KEY (a rootmap reshape that renames a key defeats it).

This TM closes that gap. It is a **content-addressed** cache: a card is keyed by
`f"{lang}:{input_raw_sha256}"` — the SHA-256 of its exact masked-input source. Both sides
compute the same address:
  * harvest  : from each store row's recorded `provenance.input_raw_sha256`;
  * generate : `gen_opt_harness2.py --tm` computes `sha256_file(<key>.raw.txt)`.
So `gen_opt_harness2.py --tm` pre-resolves any card whose source is byte-identical to one
already translated — ZERO tokens, automatically, WITHOUT hand-scoping `--keys`, and
surviving key renames (the address is the source content, not the key). Two different
sub-cards with byte-identical source (a duplicated sub-entry) reuse one translation
(cross-card reuse).

Version safety is intrinsic: if a card's source changes, its SHA changes, the address
misses, and the card is re-translated — a stale translation can never be reused.

GRANULARITY (two levels)
------------------------
CARD level (`build` / `load_tm` / `frag_address`-less path): one address per sub-card, keyed
on the whole masked source. The coarsest unit whose source string is byte-identical at both
harvest and generation (the raw `.raw.txt`), so content-addressing is exact with no guesswork.

FRAGMENT level (`build_frags` / `load_frag_tm` / `frag_address`, added 2026-07-02): one address
per deterministic `autosplit_requeue.plan()` fragment, so a partially-failed giant flat headword
(kAla/ka/SrI) re-runs only its still-missing fragments and the same meaning shared byte-for-byte
across a root and its derived noun is reused. This does NOT try to align the store's per-sense
`de` to plan() fragments (the discarded approach — headers + citation-batching gave ~3/7 exact);
instead the harness's selfHeal records fragment→senses ground truth (`frag_prov`) at the instant
of a successful heal, and `build_frags` harvests it. See the fragment-TM section below.

USAGE
-----
  python src/pilot/translation_memory.py build        [--lang ru|en] [--store PATH] [--out PATH]
  python src/pilot/translation_memory.py stats        [--lang ru|en] [--tm PATH]
  python src/pilot/translation_memory.py lookup <input_raw_sha256> [--lang ru|en] [--tm PATH]
  python src/pilot/translation_memory.py build-frags  [--lang ru|en] [--glob 'wf_output*.json'] [--out PATH]
  python src/pilot/translation_memory.py frag-stats   [--lang ru|en] [--out PATH]
  python src/pilot/translation_memory.py selftest

The card TM file (default src/pilot/translation_memory.<lang>.json) is DERIVED from the
local-only, gitignored store; the fragment sidecar (translation_memory.frag.<lang>.jsonl) is
harvested from wf_output cards' `frag_prov`. Both are gitignored + regenerable — never a
deliverable. Refresh both after every promotion (card TM) / heal run (fragment TM), or they
go stale (stale = misses, never wrong reuse — you only lose the savings).
"""
import argparse
import datetime
import glob as _glob
import hashlib
import json
import os
import sys
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
REPO = os.path.dirname(SRC)

if HERE not in sys.path:
    sys.path.insert(0, HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

DEFAULT_STORE = os.path.join(SRC, 'pwg_ru_translated.jsonl')
FIELD = {'ru': 'ru', 'en': 'en'}                    # store column holding the translation


def tm_path(lang, out=None):
    return out or os.path.join(HERE, 'translation_memory.%s.json' % lang)


def _iter_store(store_path):
    with open(store_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def reconstruct_cards(store_path, lang):
    """Group store sense-rows back into per-sub-card card objects, addressed by source SHA.

    Returns { address: entry } where address == f"{lang}:{input_raw_sha256}" and entry is
    { 'card': <card obj shaped like a wf_output card>, 'src_key', 'raw_sha256', 'model',
      'model_version', 'root', 'n_senses' }.

    A sub-card is included only if EVERY one of its senses (a) has a non-empty translation in
    the requested `lang` and (b) shares one recorded `input_raw_sha256` — a card whose rows
    disagree on the source hash is ambiguous (mid-reshape) and is skipped, not guessed.
    Rows without a recorded `input_raw_sha256` cannot be content-addressed and are skipped.
    """
    field = FIELD[lang]
    by_sub = defaultdict(list)
    for row in _iter_store(store_path):
        sub = row.get('subcard')
        if sub:
            by_sub[sub].append(row)

    entries, skipped = {}, Counter()
    for sub, rows in by_sub.items():
        shas = {(r.get('provenance') or {}).get('input_raw_sha256') for r in rows}
        shas.discard(None)
        if not shas:
            skipped['no-raw-sha'] += 1
            continue
        if len(shas) > 1:
            skipped['sha-disagreement'] += 1
            continue
        raw_sha = next(iter(shas))
        if any(not (r.get(field) or '').strip() for r in rows):
            skipped['incomplete-%s' % lang] += 1
            continue
        # Rebuild records grouped by homonym head `h`, senses in stored order.
        recs = defaultdict(list)
        rec_order = []
        for r in rows:
            h = r.get('h')
            if h not in recs:
                rec_order.append(h)
            recs[h].append({
                'tag': r.get('sense_tag'),
                'german': r.get('de'),
                field if lang == 'en' else 'russian': r.get(field),
                'equivalence_type': r.get('equivalence_type'),
                'source_type': r.get('source_type'),
                'stratum': r.get('stratum'),
                'differentia': r.get('differentia'),
            })
        card = {
            'key1': sub,
            'iast': rows[0].get('iast'),
            'records': [{'h': h, 'senses': recs[h]} for h in rec_order],
        }
        prov0 = rows[0].get('provenance') or {}
        entries['%s:%s' % (lang, raw_sha)] = {
            'card': card,
            'src_key': sub,
            'raw_sha256': raw_sha,
            'model': prov0.get('model'),
            'model_version': prov0.get('model_version'),
            'root': prov0.get('root'),
            'n_senses': len(rows),
        }
    return entries, skipped


def build(store_path, lang, out=None):
    entries, skipped = reconstruct_cards(store_path, lang)
    payload = {
        'schema': 'pwg.translation_memory.v1',
        'lang': lang,
        'address': 'sha256(input raw) == provenance.input_raw_sha256',
        'built_at': datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec='seconds').replace('+00:00', 'Z'),
        'store': os.path.basename(store_path),
        'count': len(entries),
        'entries': entries,
    }
    path = tm_path(lang, out)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False)
    return path, len(entries), skipped


def load_tm(lang, tm=None):
    """Return the {address: entry} map for a built TM, or {} if none exists."""
    path = tm_path(lang, tm)
    if not os.path.exists(path):
        return {}
    with open(path, encoding='utf-8') as f:
        return (json.load(f) or {}).get('entries') or {}


def lookup(lang, raw_sha256, tm=None):
    return load_tm(lang, tm).get('%s:%s' % (lang, raw_sha256))


# ------------------------------------------------------------------- fragment-level TM
# SUB-CARD reuse. The card-level TM above reuses a whole sub-card only when its ENTIRE
# masked source is byte-identical to a cached one. The fragment TM reuses ONE fragment
# inside a still-failing giant card (kAla/ka/SrI: one card, 40+ heal groups) and the same
# meaning across a root and its derived noun — the higher-value increment.
#
# ADDRESS. A fragment is keyed by the SHA-256 of the EXACT deterministic `plan()` chunk
# text that was translated — INCLUDING the header that `autosplit_requeue.plan()` attaches
# to fragment 0 (a verb's conjugation-table header is genuine translated source, not
# scaffolding). Both sides compute the SAME chunk: `split_plan(read_text(raw))` is
# deterministic, so harvest and generation see byte-identical fragment text -> identical
# address. (The earlier "3/7 exact" mismatch was an artifact of comparing to the store's
# per-sense `de`, which carries no header; we never do that here — we capture fragment ->
# senses at the moment of a successful heal, so there is no alignment guesswork and nothing
# to strip.) Version safety is intrinsic, exactly as for the card TM: a changed source ->
# a different chunk -> a different address -> a miss -> re-translation; a stale fragment can
# never be reused. LS_BUDGET is part of the chunking, so a changed AUTOSPLIT_LS_BUDGET
# re-chunks -> new addresses -> misses (correct: different chunking is a different fragment).
#
# GROUND TRUTH. The sidecar is harvested from wf_output cards' `frag_prov` channel, which
# `gen_opt_harness2`'s selfHeal emits per FRESHLY-resolved fragment ({fsha, restored
# senses}) — recorded at the instant of success, after the per-fragment {Tn}-multiset
# fidelity guard passed. The sidecar is DERIVED (gitignored + regenerable), never a
# deliverable, and append-only+deduped by fsha (first-seen wins).
FRAG_SEP = '\x00frag\x00'


def frag_address(lang, frag_source):
    """The content address of one plan() fragment: sha256(lang + NUL 'frag' NUL + source).

    The single source of truth for the address formula — imported by gen_opt_harness2 so
    the SHA embedded in the harness (and echoed into frag_prov at harvest) is computed the
    exact same way it is recomputed at injection time."""
    return hashlib.sha256((lang + FRAG_SEP + frag_source).encode('utf-8')).hexdigest()


def frag_tm_path(lang, out=None):
    return out or os.path.join(HERE, 'translation_memory.frag.%s.jsonl' % lang)


def load_frag_tm(lang, path=None):
    """Return { fsha: {'senses': [...], 'src_key', 'root', ...} } for the fragment sidecar,
    or {} if none exists. First-seen fsha wins (append-only dedupe)."""
    p = frag_tm_path(lang, path)
    out = {}
    if not os.path.exists(p):
        return out
    with open(p, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            fsha = row.get('fsha')
            if fsha and fsha not in out and row.get('senses'):
                out[fsha] = row
    return out


def build_frags(glob_pattern, lang, out=None):
    """Harvest per-fragment ground truth from wf_output cards' `frag_prov` channel into the
    append-only fragment sidecar. Idempotent: a fragment already present (by fsha) is never
    duplicated. Returns (path, added, total)."""
    path = frag_tm_path(lang, out)
    seen = set(load_frag_tm(lang, path))
    files = sorted(_glob.glob(os.path.join(REPO, glob_pattern)))
    new_rows, added = [], 0
    for fp in files:
        try:
            with open(fp, encoding='utf-8') as f:
                wrapper = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        res = wrapper.get('result')
        if isinstance(res, str):
            res = json.loads(res)
        if res is None:
            res = wrapper
        meta = res.get('meta') or {}
        if (meta.get('lang') or 'ru') != lang:
            continue
        root = meta.get('root')
        for r in res.get('results') or []:
            card = (r or {}).get('card')
            if not card:
                continue
            for fpv in card.get('frag_prov') or []:
                fsha, senses = fpv.get('fsha'), fpv.get('senses')
                if not fsha or not senses or fsha in seen:
                    continue
                seen.add(fsha)
                added += 1
                new_rows.append({
                    'schema': 'pwg.translation_memory.frag.v1', 'lang': lang, 'fsha': fsha,
                    'src_key': r.get('key'), 'root': root, 'n_senses': len(senses),
                    'senses': senses, 'wf_file': os.path.basename(fp),
                    'harvested_at': datetime.datetime.now(datetime.timezone.utc).isoformat(
                        timespec='seconds').replace('+00:00', 'Z'),
                })
    if new_rows:
        with open(path, 'a', encoding='utf-8') as f:
            for row in new_rows:
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
    return path, added, len(seen)


# --------------------------------------------------------------------------- selftest
def selftest():
    import tempfile
    # Two sub-cards; the second row-set disagrees on the source sha (must be skipped),
    # the third is missing a translation (must be skipped), the fourth has no sha (skipped).
    rows = [
        {'subcard': 'x~~h0_1', 'key1': 'x', 'iast': 'xa', 'h': 'xa', 'sense_tag': '1',
         'ru': 'один', 'de': 'eins', 'equivalence_type': 'equivalent', 'source_type': 'attested',
         'stratum': '', 'differentia': '',
         'provenance': {'input_raw_sha256': 'AAA', 'model': 'sonnet', 'model_version': 'claude-sonnet-5', 'root': 'x'}},
        {'subcard': 'x~~h0_1', 'key1': 'x', 'iast': 'xa', 'h': 'xa', 'sense_tag': '2',
         'ru': 'два', 'de': 'zwei', 'equivalence_type': 'equivalent', 'source_type': 'attested',
         'stratum': '', 'differentia': '',
         'provenance': {'input_raw_sha256': 'AAA', 'model': 'sonnet', 'model_version': 'claude-sonnet-5', 'root': 'x'}},
        {'subcard': 'y~~h0_1', 'key1': 'y', 'iast': 'ya', 'h': 'ya', 'sense_tag': '1',
         'ru': 'три', 'de': 'drei', 'provenance': {'input_raw_sha256': 'BBB'}},
        {'subcard': 'y~~h0_1', 'key1': 'y', 'iast': 'ya', 'h': 'ya', 'sense_tag': '2',
         'ru': 'четыре', 'de': 'vier', 'provenance': {'input_raw_sha256': 'CCC'}},   # sha disagreement
        {'subcard': 'z~~h0_1', 'key1': 'z', 'iast': 'za', 'h': 'za', 'sense_tag': '1',
         'ru': '', 'de': 'fuenf', 'provenance': {'input_raw_sha256': 'DDD'}},         # missing ru
        {'subcard': 'w~~h0_1', 'key1': 'w', 'iast': 'wa', 'h': 'wa', 'sense_tag': '1',
         'ru': 'шесть', 'de': 'sechs', 'provenance': {}},                             # no sha
    ]
    fd, store = tempfile.mkstemp(suffix='.jsonl'); os.close(fd)
    fd, out = tempfile.mkstemp(suffix='.json'); os.close(fd)
    try:
        with open(store, 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        entries, skipped = reconstruct_cards(store, 'ru')
        assert set(entries) == {'ru:AAA'}, entries
        e = entries['ru:AAA']
        assert e['n_senses'] == 2, e
        assert e['card']['key1'] == 'x~~h0_1', e['card']
        senses = e['card']['records'][0]['senses']
        assert [s['tag'] for s in senses] == ['1', '2'], senses
        assert senses[0]['russian'] == 'один' and senses[0]['german'] == 'eins', senses
        assert skipped['sha-disagreement'] == 1, skipped
        assert skipped['incomplete-ru'] == 1, skipped
        assert skipped['no-raw-sha'] == 1, skipped
        # build + load + lookup round-trip
        path, n, _ = build(store, 'ru', out=out)
        assert n == 1, n
        assert lookup('ru', 'AAA', tm=out)['src_key'] == 'x~~h0_1'
        assert lookup('ru', 'ZZZ', tm=out) is None
        _frag_selftest()
        print('translation_memory selftest OK')
    finally:
        for p in (store, out):
            try:
                os.remove(p)
            except OSError:
                pass


def _frag_selftest():
    import tempfile
    # 1) Address is deterministic, lang-separated, and header-sensitive (no stripping).
    src = '=== header ===\n1) foo <ls>ṚV.</ls>'
    assert frag_address('ru', src) == frag_address('ru', src), 'address not deterministic'
    assert frag_address('ru', src) != frag_address('en', src), 'lang must separate the address'
    assert frag_address('ru', src) != frag_address('ru', src.split('\n', 1)[1]), \
        'header is part of the fragment source — the address must change if it is stripped'
    # 2) build_frags harvests frag_prov from wf_output, dedups by fsha, is idempotent.
    d = tempfile.mkdtemp()
    fsha = frag_address('ru', src)
    senses = [{'tag': '1', 'german': 'foo <ls>ṚV.</ls>', 'russian': 'фу', 'source_type': 'attested'}]
    wf = {'meta': {'lang': 'ru', 'root': 'zz'}, 'results': [
        {'key': 'zz~~h0_00_pwg00', 'card': {'key1': 'zz', 'records': [{'senses': senses}],
                                            'frag_prov': [{'fsha': fsha, 'senses': senses}]}},
        {'key': 'zz~~h0_01', 'card': None},                       # null card: no frag_prov
    ]}
    en_wf = {'meta': {'lang': 'en', 'root': 'zz'}, 'results': [
        {'key': 'zz~~h9', 'card': {'frag_prov': [{'fsha': 'EN', 'senses': senses}]}}]}
    old_repo = globals()['REPO']
    try:
        globals()['REPO'] = d                                    # build_frags globs under REPO
        with open(os.path.join(d, 'wf_output.sc.zz.json'), 'w', encoding='utf-8') as f:
            json.dump(wf, f, ensure_ascii=False)
        with open(os.path.join(d, 'wf_output.en.zz.json'), 'w', encoding='utf-8') as f:
            json.dump(en_wf, f, ensure_ascii=False)
        sidecar = os.path.join(d, 'frag.ru.jsonl')
        _p, added, total = build_frags('wf_output*.json', 'ru', out=sidecar)
        assert added == 1 and total == 1, (added, total)          # EN wf must not leak into RU
        cache = load_frag_tm('ru', sidecar)
        assert set(cache) == {fsha}, cache
        assert cache[fsha]['senses'][0]['russian'] == 'фу', cache
        # idempotent re-harvest adds nothing
        _p, added2, total2 = build_frags('wf_output*.json', 'ru', out=sidecar)
        assert added2 == 0 and total2 == 1, (added2, total2)
    finally:
        globals()['REPO'] = old_repo
        import shutil
        shutil.rmtree(d, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build'); b.add_argument('--lang', default='ru'); b.add_argument('--store', default=DEFAULT_STORE); b.add_argument('--out', default=None)
    s = sub.add_parser('stats'); s.add_argument('--lang', default='ru'); s.add_argument('--tm', default=None)
    lk = sub.add_parser('lookup'); lk.add_argument('sha'); lk.add_argument('--lang', default='ru'); lk.add_argument('--tm', default=None)
    bf = sub.add_parser('build-frags'); bf.add_argument('--lang', default='ru'); bf.add_argument('--glob', default='wf_output*.json'); bf.add_argument('--out', default=None)
    fs = sub.add_parser('frag-stats'); fs.add_argument('--lang', default='ru'); fs.add_argument('--out', default=None)
    sub.add_parser('selftest')
    args = ap.parse_args()

    if args.cmd == 'selftest':
        return selftest()
    if args.lang not in FIELD:
        sys.exit('unknown --lang %r (ru|en)' % args.lang)
    if args.cmd == 'build':
        if not os.path.exists(args.store):
            sys.exit('store not found: %s' % args.store)
        path, n, skipped = build(args.store, args.lang, out=args.out)
        print('wrote %s (%d content-addressed cards, lang=%s)' % (path, n, args.lang))
        if skipped:
            print('  skipped sub-cards:', dict(skipped))
    elif args.cmd == 'stats':
        entries = load_tm(args.lang, args.tm)
        senses = sum(e.get('n_senses', 0) for e in entries.values())
        roots = Counter(e.get('root') for e in entries.values())
        print('TM lang=%s: %d cards, %d senses, %d roots' % (args.lang, len(entries), senses, len(roots)))
        for root, c in roots.most_common(12):
            print('  %-10s %d cards' % (root, c))
    elif args.cmd == 'lookup':
        e = lookup(args.lang, args.sha, args.tm)
        print(json.dumps(e, ensure_ascii=False, indent=2) if e else '(miss)')
    elif args.cmd == 'build-frags':
        path, added, total = build_frags(args.glob, args.lang, out=args.out)
        print('wrote %s (+%d new fragment(s), %d total, lang=%s)' % (path, added, total, args.lang))
    elif args.cmd == 'frag-stats':
        cache = load_frag_tm(args.lang, args.out)
        senses = sum(len(e.get('senses') or []) for e in cache.values())
        roots = Counter(e.get('root') for e in cache.values())
        print('frag TM lang=%s: %d fragments, %d senses, %d roots' % (args.lang, len(cache), senses, len(roots)))
        for root, c in roots.most_common(12):
            print('  %-10s %d fragments' % (root, c))


if __name__ == '__main__':
    main()
