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

GRANULARITY (and the next increment)
------------------------------------
This TM is CARD-level (one address per sub-card). That is the coarsest unit whose source
string is byte-identical at both harvest and generation time (the raw `.raw.txt` on disk),
so content-addressing is exact with no normalization guesswork. Sub-CARD (sense/fragment)
reuse — reusing an already-translated sense inside a still-failing giant flat headword like
kAla/ka/SrI, or the same meaning across a root and its derived noun — is the higher-value
next increment, but the store's per-sense `de` does NOT align byte-for-byte with the
harness's `autosplit_requeue.plan()` fragments (headers + citation-batching → ~3/7 exact on
a sample), so it needs a fragment-provenance channel this first version deliberately does
not fake. See the handoff for the plan.

USAGE
-----
  python src/pilot/translation_memory.py build   [--lang ru|en] [--store PATH] [--out PATH]
  python src/pilot/translation_memory.py stats    [--lang ru|en] [--tm PATH]
  python src/pilot/translation_memory.py lookup <input_raw_sha256> [--lang ru|en] [--tm PATH]
  python src/pilot/translation_memory.py selftest

The TM file (default src/pilot/translation_memory.<lang>.json) is DERIVED from the
local-only, gitignored store and is itself gitignored + regenerable — never a deliverable.
"""
import argparse
import datetime
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
        print('translation_memory selftest OK')
    finally:
        for p in (store, out):
            try:
                os.remove(p)
            except OSError:
                pass


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build'); b.add_argument('--lang', default='ru'); b.add_argument('--store', default=DEFAULT_STORE); b.add_argument('--out', default=None)
    s = sub.add_parser('stats'); s.add_argument('--lang', default='ru'); s.add_argument('--tm', default=None)
    lk = sub.add_parser('lookup'); lk.add_argument('sha'); lk.add_argument('--lang', default='ru'); lk.add_argument('--tm', default=None)
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


if __name__ == '__main__':
    main()
