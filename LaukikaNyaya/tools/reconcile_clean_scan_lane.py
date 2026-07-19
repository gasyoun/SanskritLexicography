# -*- coding: utf-8 -*-
"""
One-time reconciliation (19-07-2026, H803 continuation): merges the
clean-scan lane (data/laukika_nyaya_clean_scan.jsonl, 301 records, built
by build_laukika_nyaya_clean_scan.py from the UC Libraries scans) into the
existing data/laukika_nyaya.jsonl (302 records after the same-day dedup +
false-positive correction -- itself already a manual
union of two earlier independent extraction lanes from the garbled
YKTn_... scan; see README.md "Two-lane reconciliation, 19-07-2026").

Matching: normalize each headword to a bare-consonant-ish skeleton
(strip vowel signs/anusvara/visarga -- exactly what differs most between
independent OCR passes of the same word) and compare via difflib ratio,
corroborated by a gloss_en prefix match. On a match, the clean-scan lane's
real page citation always wins (the existing 302-set has none); its
explanation body replaces the existing one only when comparably long
(>=80% of the existing body's length) -- in the spot-checked cases this
lane's headwords/citations are strictly better but its body text (which
embeds Sanskrit block-quotes) is not reliably cleaner, so length is used
as a floor against picking a truncated body, not as a quality signal.

NOT idempotent against a re-run from a *different* state of
data/laukika_nyaya.jsonl -- this script documents what WAS done to reach
431 records; it is not a repeatable one-command pipeline (same caveat the
existing two-lane union already carries). Re-running it against the
already-reconciled 431-record file would try to match lane 3 against
itself and is not meaningful.
"""
import re
import sys
import json
import difflib
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE.parent / "data"
EXISTING_PATH = DATA_DIR / "laukika_nyaya.jsonl"
CLEAN_SCAN_PATH = DATA_DIR / "laukika_nyaya_clean_scan.jsonl"

VOWEL_SIGNS = re.compile(r'[ािीुूृेैोौंःँ्]')
# "न्याय" (nyaya) is the coined-compound suffix on the majority of headwords --
# comparing skeletons WITH it included inflates the similarity ratio for any
# two unrelated "X-nyaya" maxims (a real false-match found by spot-check: the
# 302-set's प्रपानकरसन्यायः and the clean-scan lane's unrelated नर्तकन्यायः
# scored >0.55 on skeleton alone, purely from sharing this suffix). Strip it
# before comparing so only the distinctive part counts.
NYAYA_SUFFIX = re.compile(r'न्याय')
# Similarly, "the simile of" / "the maxim of" is Jacob's own boilerplate
# opener on most glosses -- comparing raw gloss prefixes inflates similarity
# for any two entries sharing that template. Strip it before comparing.
GLOSS_BOILERPLATE = re.compile(r'^(the (simile|maxim) of a?n?\s*|it is |this )')


def skeleton(deva):
    s = VOWEL_SIGNS.sub('', unicodedata.normalize('NFC', deva or ''))
    return NYAYA_SUFFIX.sub('', s)


def gloss_key(g):
    s = re.sub(r'[^a-z ]', '', (g or '').lower())
    s = GLOSS_BOILERPLATE.sub('', s).strip()
    return s[:40]


def load(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(l) for l in f]


def best_match(rec, pool_skel, pool_gloss, used):
    """Require BOTH signals to corroborate (a high skeleton match with no
    supporting gloss overlap, or vice versa, is exactly the false-positive
    class found above) -- not either signal alone crossing a low bar."""
    sk, gk = skeleton(rec.get('nyaya_deva', '')), gloss_key(rec.get('gloss_en', ''))
    best_i, best_score = None, 0.0
    for i, (osk, ogk) in enumerate(zip(pool_skel, pool_gloss)):
        if i in used:
            continue
        s_score = difflib.SequenceMatcher(None, sk, osk).ratio() if sk and osk else 0.0
        g_score = difflib.SequenceMatcher(None, gk, ogk).ratio() if gk and ogk else 0.0
        if sk and osk and gk and ogk:
            # both signals present: require corroboration, not either alone
            score = (s_score + g_score) / 2 if (s_score > 0.7 and g_score > 0.55) else 0.0
        elif sk and osk:
            # only the headword signal is available: demand a much higher bar
            score = s_score if s_score > 0.85 else 0.0
        else:
            score = g_score if g_score > 0.85 else 0.0
        if score > best_score:
            best_score, best_i = score, i
    return best_i, best_score


def main():
    existing = load(EXISTING_PATH)
    clean = load(CLEAN_SCAN_PATH)
    print(f"existing: {len(existing)}, clean-scan lane: {len(clean)}")

    ex_skel = [skeleton(e.get('nyaya_deva', '')) for e in existing]
    ex_gloss = [gloss_key(e.get('gloss_en', '')) for e in existing]
    used, matched, augmented, new = set(), 0, 0, 0
    merged = []

    for c in clean:
        idx, _score = best_match(c, ex_skel, ex_gloss, used)
        if idx is not None:
            used.add(idx)
            matched += 1
            base = existing[idx]
            take_clean_body = len(c.get('explanation') or '') >= len(base.get('explanation') or '') * 0.8
            rec = dict(base)
            rec['source'] = c['source']
            rec['_clean_scan_leaf'] = c['_scan_leaf']
            if take_clean_body:
                rec.update(nyaya_deva=c['nyaya_deva'], nyaya_iast=c['nyaya_iast'],
                           nyaya_slp1=c['nyaya_slp1'], gloss_en=c['gloss_en'] or base.get('gloss_en'),
                           explanation=c['explanation'], _match_method='clean-scan-lane-preferred')
                augmented += 1
            else:
                rec['_match_method'] = f"{base.get('_match_method', 'unknown')}+clean-scan-citation"
            merged.append(rec)
        else:
            new += 1
            rec = dict(c)
            rec['_match_method'] = 'clean-scan-lane-new'
            merged.append(rec)

    merged.extend(e for i, e in enumerate(existing) if i not in used)

    # Final safety net: the 302-set itself carries a handful of pre-existing
    # near-duplicate pairs that differ only by a trailing visarga/whitespace
    # (different nyaya_slp1, so the org's own exact-slp1 dedup pass didn't
    # catch them) -- when THIS reconciliation's headword upgrade converges
    # one of such a pair onto the clean-scan lane's spelling, it can newly
    # collide with its untouched twin. Detected AFTER merging (skeleton
    # matching against a moving target mid-loop is not reliable); resolved by
    # keeping whichever copy has the richer `_match_method` (prefers a
    # clean-scan-lane real citation over a bare original-lane tag) and
    # dropping the other, logged rather than silently vanished.
    by_slp1 = {}
    for r in merged:
        k = r.get('nyaya_slp1')
        if not k:
            continue
        by_slp1.setdefault(k, []).append(r)
    dropped = []
    for k, group in by_slp1.items():
        if len(group) < 2:
            continue

        def rank(rec):
            m = rec.get('_match_method', '')
            return (1 if 'clean-scan' in m else 0, len(rec.get('explanation') or ''))
        group.sort(key=rank, reverse=True)
        for loser in group[1:]:
            dropped.append(loser)
    if dropped:
        dropped_ids = {id(r) for r in dropped}
        merged = [r for r in merged if id(r) not in dropped_ids]
        print(f"post-merge dedup: dropped {len(dropped)} pre-existing near-duplicate(s) "
              f"exposed by the headword upgrade (e.g. visarga/whitespace pairs the "
              f"302-set's own dedup missed): "
              + "; ".join(f"{r['nyaya_deva']!r}" for r in dropped))

    for n, r in enumerate(merged, start=1):
        r['num'] = n

    print(f"matched={matched} (body-augmented={augmented}), clean-scan-new={new}, "
          f"existing-unmatched-kept={len(existing) - len(used)}, "
          f"post-merge-dedup-dropped={len(dropped)}")
    print(f"TOTAL: {len(merged)}")

    with open(EXISTING_PATH, 'w', encoding='utf-8') as out:
        for r in merged:
            out.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f"Wrote {EXISTING_PATH}")


if __name__ == '__main__':
    main()
