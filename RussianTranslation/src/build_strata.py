#!/usr/bin/env python
"""Build corpus_strata.json — genre (Renou) + chronology (Dharmamitra) per text.

Classifies each verse-aligned corpus text in SamudraManthanam by:
  - genre   : Renou's taxonomy of Sanskrit literature (Veda / Epic / Kāvya /
              Śāstra:{darśana,dharma,kāma,jyotiṣa,āyurveda,yoga} / Tantra-Āgama /
              Purāṇa), aligned to Dharmamitra's genre-group codes;
  - date    : Dharmamitra absolute-date posterior median (Gibbs sampler,
              dharmamitra/sanskrit-dating), with a 95% credible interval;
  - period  : a coarse chronological bucket for grouping.

The pwg_ru harvest uses this so a sense PWG cites from the Ṛgveda harvests the
*Vedic* Russian, a sense cited from the Mahābhārata the *Epic* Russian, etc.

Output corpus_strata.json is committed metadata (small, auditable). Dates are
Dharmamitra medians (rounded); refine against dated_gibbs_full.tsv as needed.
"""
import json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SM = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'SamudraManthanam',
                                   'web', 'corpus_builder', 'jsonl'))
OUT = os.path.join(HERE, 'corpus_strata.json')

# Files that are dictionaries / indices, not verse-aligned corpus → skip.
SKIP = re.compile(r'^(kochergina|kossovich|knauer|frish|slovar|dic_|warnemyr|'
                  r'ramayana-3-slovar|ukazateli|stati|kommentarii|pandey|toporov|'
                  r'fasmer|mify|induizm|stepanyants|biruni|iliada|kewa|dsg|'
                  r'yoga-bessmertie)', re.I)

# period buckets by Dharmamitra median date (year; negative = BCE)
def period(d):
    if d < -1000: return 'Ṛgvedic'
    if d < -300:  return 'Vedic (Brāhmaṇa–Upaniṣad)'
    if d < 400:   return 'Epic / early-Classical'
    if d < 1000:  return 'Classical'
    return 'Medieval'

# (filename regex, genre [Renou], Dharmamitra genre-code, median, lo95, hi95)
RULES = [
    (r'rigveda',                 'Veda — Saṃhitā',            'GV', -1125, -1390, -860),
    (r'atharvaveda',             'Veda — Saṃhitā',            'GV',  -940, -1160, -720),
    (r'mahabharata',             'Epic — Itihāsa (MBh)',      'GE',    80,  -230,  390),
    (r'ramayana(?!-3)',          'Epic — Itihāsa (Rām)',      'GE',    70,  -250,  410),
    (r'bhagavadg',               'Epic — Gītā',               'GE',   200,    15,  350),
    (r'erman-temkin|mify_759',   'Epic — retelling',          'GE',   200,  -200,  400),
    # Upaniṣads (Dharmamitra dates per text; Vedic genre)
    (r'^br-up|brb-up|^brahad',   'Veda — Upaniṣad',           'GV',  -585,  -700,  -460),
    (r'^ch-up|chag-up|chandog',  'Veda — Upaniṣad',           'GV',  -585,  -700,  -460),
    (r'^ait-up|aitareya',        'Veda — Upaniṣad',           'GV',  -483,  -600,  -365),
    (r'^kat-up|^kath|katha',     'Veda — Upaniṣad',           'GV',  -273,  -498,   -51),
    (r'^isha-up|^isa|^ish',      'Veda — Upaniṣad',           'GV',  -245,  -470,   -10),
    (r'^kena-up|kena',           'Veda — Upaniṣad',           'GV',  -250,  -470,   -30),
    (r'^shv-up|shvet|svet',      'Veda — Upaniṣad',           'GV',  -244,  -470,   -20),
    (r'^mun-up|munda',           'Veda — Upaniṣad',           'GV',  -150,  -380,    80),
    (r'^pr-up|prashna|^pai-up',  'Veda — Upaniṣad',           'GV',   -54,  -227,   118),
    (r'^man-up|^mai-up|mandukya|maitr', 'Veda — Upaniṣad',    'GV',    50,  -210,   300),
    (r'-up$|-up\.|upanish|^kai-up|^jab|^atma|^nr-up|^sub-up|'
     r'^chag|^kau-up|^tai-up|^vajs|^yotat|^rampt|^mnar|^jab-up', 'Veda — Upaniṣad (later)', 'GV', 300, 0, 700),
    (r'syrkin',                  'Veda — Upaniṣad (Syrkin tr.)','GV', -100, -500, 300),
    # Kāvya
    (r'buddhacharita',           'Kāvya — Buddhist mahākāvya','GK',   118,    70,   168),
    (r'kumarasambhava|raghuvamsha|megha-duta', 'Kāvya — Mahākāvya (Kālidāsa)', 'GK', 420, 370, 468),
    (r'amaru|chaurapanchashika', 'Kāvya — lyric',             'GK',   450,   350,   600),
    (r'shatakatrayam|shataka',   'Kāvya — gnomic (śataka)',   'GK',   550,   490,   670),
    (r'gitagovinda',             'Kāvya — lyric (Jayadeva)',  'GK',  1048,   988,  1106),
    (r'shukasaptati|kama-sutra', 'Śāstra — Kāma / kathā',     'GS',   388,   290,   519),
    # Śāstra — darśana / dharma / jyotiṣa / āyurveda / yoga
    (r'manavadharmashastra|manu','Śāstra — Dharma (Manu)',    'GSD',  150,  -100,   350),
    (r'yoga-sutry_vyasa|yoga-sutry_zagumennov|yoga-sutry$|yoga-sutry_sharma',
                                 'Śāstra — Darśana (Yoga-sūtra)','GSP', 210,    95,   330),
    (r'sankhya-karika',          'Śāstra — Darśana (Sāṃkhya)','GSP',  370,   200,   520),
    (r'nyaya-bhashya',           'Śāstra — Darśana (Nyāya)',  'GSP',  450,   300,   600),
    (r'vedanga_jyotisha',        'Śāstra — Jyotiṣa',          'GS',   403,   290,   519),
    (r'hatha-yoga-pradipika|yoga-sutry_vyasa-bhashya', 'Śāstra — Yoga (Haṭha)', 'GS', 1374, 1260, 1490),
    (r'vishnu-purana',           'Purāṇa',                    'GP',   450,   350,   700),
    # Tantra / Āgama / Śaiva
    (r'shiva-sutry|pratyabhijna|paramarthasara|devi-gita|vedanga_jyotisha', 'Āgama / Tantra (Śaiva)', 'GR', 950, 700, 1200),
    # commentaries (date ~ commentator)
    (r'gitartha-samgraha_yamun', 'Śāstra — Commentary (Yāmuna)','GSP', 950,  900, 1000),
    (r'abhinavagupta|gitartha-samgraha', 'Śāstra — Commentary (Abhinavagupta)', 'GSP', 1000, 950, 1050),
    (r'ramanuja|vedartha',       'Śāstra — Commentary (Rāmānuja)','GSP', 1120, 1050, 1200),
    (r'vyasa-bhashya|yoga-sutry_vyasa', 'Śāstra — Commentary (Vyāsa-bhāṣya)','GSP', 511, 354, 670),
]


def stratum_for(name):
    for pat, genre, code, d, lo, hi in RULES:
        if re.search(pat, name, re.I):
            return {'genre': genre, 'genre_code': code, 'date_median': d,
                    'date_lo95': lo, 'date_hi95': hi, 'period': period(d),
                    'source': 'Dharmamitra (date) + Renou (genre)'}
    return None


_CYR = re.compile('[Ѐ-ӿԀ-ԯⷠ-ⷿꙀ-ꚟ]')


def count_groups(f):
    """Verse-groups that have a Sanskrit verse AND a REAL (Cyrillic) translation.
    A ru segment of only '…' is an untranslated placeholder — excluded, so the
    size/ordering reflect genuinely-translated material, not stubs."""
    sa, ru = set(), set()
    for line in open(os.path.join(SM, f), encoding='utf-8'):
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get('deleted') or not e.get('text'):
            continue
        if e.get('seg') == 'sa':
            sa.add(e.get('group'))
        elif e.get('seg') == 'ru' and _CYR.search(e.get('text') or ''):
            ru.add(e.get('group'))
    return len(sa & ru)


def size_rating(g):
    """1 (tiny) … 5 (huge), by verse-group count."""
    return 5 if g >= 5000 else 4 if g >= 2000 else 3 if g >= 500 else 2 if g >= 100 else 1


def main():
    files = sorted(f for f in os.listdir(SM) if f.endswith('.jsonl'))
    strata, unmatched, skipped = {}, [], []
    for f in files:
        work = f[:-6]
        if SKIP.match(work):
            skipped.append(work); continue
        s = stratum_for(work)
        if s:
            g = count_groups(f)
            s['groups'] = g
            s['size'] = size_rating(g)
            strata[work] = s
        else:
            unmatched.append(work)
    json.dump(strata, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    print('classified %d corpus texts → %s' % (len(strata), os.path.basename(OUT)))
    print('skipped (dict/index): %d' % len(skipped))
    import collections
    by_g = collections.Counter(s['genre'].split(' —')[0] for s in strata.values())
    print('by top genre:', dict(by_g))
    bysz = collections.Counter(s['size'] for s in strata.values())
    print('by size 1–5:', dict(sorted(bysz.items(), reverse=True)))
    print('biggest works (processed first):')
    for w, s in sorted(strata.items(), key=lambda x: -x[1]['groups'])[:8]:
        print('  size %d · %5d groups · %s' % (s['size'], s['groups'], w))
    if unmatched:
        print('\nUNMATCHED (need a rule): %d' % len(unmatched))
        for u in unmatched:
            print('  ', u)


if __name__ == '__main__':
    main()
