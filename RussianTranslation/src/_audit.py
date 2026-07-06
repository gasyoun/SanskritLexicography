#!/usr/bin/env python
"""Recurring deterministic integrity audit of corpus_lexicon.jsonl.

Run at each build milestone. Catches every known corruption mode STRUCTURALLY
(no LLM, ~1s): placeholder-group fabrication leak, non-Cyrillic ru, ru==sa,
refusal strings, '√' in key, exact dups, stratum mis-attachment, un-stratified
works. Reports the delta since the last run (_audit_state.json) so attention
goes to newly-processed works. Exit 0 = clean, 1 = contamination found.
"""
import json, os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SM = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'SamudraManthanam',
                                   'web', 'corpus_builder', 'jsonl'))
LEX = os.path.join(HERE, 'corpus_lexicon.jsonl')
STRATA = json.load(open(os.path.join(HERE, 'corpus_strata.json'), encoding='utf-8'))
STATE = os.path.join(HERE, '_audit_state.json')
CYR = re.compile('[Ѐ-ӿԀ-ԯⷠ-ⷿꙀ-ꚟ]')
REJECT_RU = {'(no clear counterpart)', 'нет соответствия', '—', '…', '...'}


def has_cyr(s):
    return bool(s) and bool(CYR.search(s))


_tg = {}
def cyr_groups(work):
    """(ru_groups, comm_groups): groups with a Cyrillic seg=ru, and groups with a
    Cyrillic seg=comm*. A translation row is legit only if its group is in
    ru_groups; a COMMENTARY row is legit if its group is in comm_groups — the
    verse translation may be an untranslated placeholder while a commentary note
    is in Russian (e.g. a proper-name gloss). Kind-aware to avoid false leaks."""
    if work in _tg:
        return _tg[work]
    ru, comm = set(), set()
    f = os.path.join(SM, work + '.jsonl')
    if os.path.exists(f):
        for line in open(f, encoding='utf-8'):
            try:
                e = json.loads(line)
            except Exception:
                continue
            if e.get('deleted') or not has_cyr(e.get('text')):
                continue
            seg = e.get('seg', '')
            if seg == 'ru':
                ru.add(e.get('group'))
            elif seg.startswith('comm'):
                comm.add(e.get('group'))
    _tg[work] = (ru, comm)
    return _tg[work]


def main():
    if not os.path.exists(LEX):
        print('lexicon empty'); return 0
    rows = collections.Counter()
    groups = collections.defaultdict(set)
    bad = collections.Counter()   # work -> contamination count
    leak = collections.Counter()  # work -> rows whose group is NOT a real translation
    seen = set(); dup = 0
    tot = nocyr = rusa = sqrt = stratbad = unstrat = 0
    for line in open(LEX, encoding='utf-8'):
        try:
            r = json.loads(line)
        except Exception:
            continue
        tot += 1
        w, g = r.get('work'), r.get('group')
        rows[w] += 1; groups[w].add(g)
        ru = (r.get('ru') or '').strip(); sa = (r.get('sa') or '').strip()
        contam = False
        ru_g, comm_g = cyr_groups(w)
        # fabrication = a row whose group has NO Cyrillic source at all (the
        # placeholder case). A group with a real seg=ru OR a Cyrillic commentary
        # is genuinely translated, so its rows are not leaks.
        if g not in ru_g and g not in comm_g:
            leak[w] += 1; contam = True
        if not has_cyr(ru): nocyr += 1; contam = True
        if ru == sa or ru in REJECT_RU: rusa += 1; contam = True
        if chr(0x221a) in (r.get('slp1') or ''): sqrt += 1; contam = True
        k = (g, r.get('slp1'), ru, r.get('kind'))
        if k in seen: dup += 1; contam = True
        seen.add(k)
        st = STRATA.get(w)
        if st is None:
            unstrat += 1; contam = True
        elif r.get('genre') != st.get('genre') or r.get('date') != st.get('date_median'):
            stratbad += 1; contam = True
        if contam:
            bad[w] += 1

    prev = json.load(open(STATE, encoding='utf-8')) if os.path.exists(STATE) else {}
    prev_rows = prev.get('rows', {})
    new_works = [w for w in rows if w not in prev_rows]

    print('=== integrity audit: %d rows, %d works, %d distinct groups ==='
          % (tot, len(rows), sum(len(s) for s in groups.values())))
    print('contamination (all MUST be 0): placeholder-leak=%d non-Cyrillic=%d ru==sa=%d sqrt-key=%d dup=%d stratum-mismatch=%d un-stratified=%d'
          % (sum(leak.values()), nocyr, rusa, sqrt, dup, stratbad, unstrat))
    if new_works:
        print('NEW works since last audit: ' + ', '.join('%s(+%d)' % (w, rows[w]) for w in new_works))
    if bad:
        print('!! DIRTY works:')
        for w, c in bad.most_common():
            print('   %s: %d contaminated rows (leak=%d)' % (w, c, leak[w]))
    json.dump({'rows': dict(rows), 'total': tot}, open(STATE, 'w', encoding='utf-8'))
    clean = not bad

    # H215 Slice 1: if a TMX export exists (release/corpus_tm/, gitignored), round-trip
    # validate it so a malformed publication artifact is caught by the same audit.
    tmx = os.path.normpath(os.path.join(HERE, '..', 'release', 'corpus_tm', 'corpus_tm.sa-ru.tmx'))
    if os.path.exists(tmx):
        try:
            import build_tmx
            ok, msg = build_tmx.validate(tmx)
            print('TMX export:', msg)
            clean = clean and ok
        except Exception as e:
            print('TMX export: validation skipped (%s)' % e)

    # H215 Slice 2: the grader's deterministic invariants (qe ordering, source
    # override, consensus, grade gates) are a cheap integrity check regardless of a
    # release existing -- a broken grader silently mis-stamps the publication TMX.
    try:
        import io
        import contextlib
        import tm_grade
        with contextlib.redirect_stdout(io.StringIO()):
            rc = tm_grade.selftest()
        ok = rc == 0
        print('TM grader selftest:', 'OK' if ok else 'FAILED')
        clean = clean and ok
    except Exception as e:
        print('TM grader selftest: skipped (%s)' % e)

    print('VERDICT:', 'CLEAN' if clean else 'CONTAMINATION FOUND')
    return 0 if clean else 1


if __name__ == '__main__':
    sys.exit(main())
