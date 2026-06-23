#!/usr/bin/env python
"""build_dcs_renou.py — DCS corpus → per-lemma Renou language-state index.

Enrichment beyond the dictionary's own <ls> citations: where a lemma is *actually
attested* across the Digital Corpus of Sanskrit (DCS, 2026 CoNLL-U snapshot), we
read off the Renou language-state(s) of those texts. A word the dictionary only
cites classically but that DCS attests in the Ṛgveda thereby gains state I.

Two steps:
  1. resolve each DCS text → a Renou state (I–V) from its genre/date;
  2. scan the corpus (lemma = CoNLL-U column 3) → for each lemma the union of
     states of the texts it occurs in, plus the oldest (earliest-dated) text.

Text→state genre source priority: (a) DCS genre from VisualDCS
visual/dcs_texts_clean.json (authoritative, incl. Buddhist/Vyākaraṇa); (b) curated
name hints for the Buddhist (V) / grammar (II) texts that file misses; (c) a
date fallback (timeslot/clean date → I/III/IV) for the rest, flagged low-confidence.

  python build_dcs_renou.py --texts            # text→state coverage table, no scan
  python build_dcs_renou.py [--out PATH] [--limit N]   # build the lemma index
"""
import json, os, re, sys, collections, statistics
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
DCS = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'VisualDCS', 'src',
                                    'DCS-data-2026', 'conllu'))
FILES = os.path.join(DCS, 'files')
CHAPTER_INFO = os.path.join(DCS, 'lookup', 'chapter-info.xml')
CLEAN = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'VisualDCS',
                                      'visual', 'dcs_texts_clean.json'))
OUT = os.path.join(HERE, 'dcs_lemma_renou.json')

STATES = ('I', 'II', 'III', 'IV', 'V')
_ORDER = {s: i for i, s in enumerate(STATES)}

# DCS genre (dcs_texts_clean.json) → Renou state. 'Sūtra/Dharma' and 'Other' are
# resolved by date (Dharmasūtra is Vedic, Dharma-/Smṛti-śāstra is Epic-prolongement).
GENRE_RENOU = {
    'Vedic Saṃhitā': 'I', 'Brāhmaṇa': 'I', 'Upaniṣad': 'I',
    'Vyākaraṇa': 'II',
    'Epic': 'III', 'Purāṇa': 'III', 'Tantra/Āgama': 'III',
    'Kāvya': 'IV', 'Nāṭya': 'IV', 'Narrative Prose': 'IV', 'Kośa/Lexicon': 'IV',
    'Arthaśāstra': 'IV', 'Medical': 'IV', 'Philosophy': 'IV', 'Ritual': 'IV',
    'Buddhist': 'V',
}
# Name substrings → state, for texts absent from dcs_texts_clean.json. Lowercased,
# diacritics kept. Buddhist (V) and the grammatical tradition (II) cannot be read
# off a date, so they must be caught by name.
NAME_HINTS = [
    ('V', ('abhidharma', 'avadāna', 'avadāna', 'jātaka', 'lalitavistara',
           'prajñāpāramitā', 'laṅkāvatāra', 'saddharma', 'divyāvadāna', 'mahāvastu',
           'vimalakīrti', 'śikṣāsamuccaya', 'bodhicaryāvatāra', 'bodhisattva',
           'tattvasaṃgraha', 'tattvasaṅgraha', 'pramāṇavārttika', 'pramāṇaviniścaya',
           'madhyamaka', 'mūlamadhyamaka', 'vigrahavyāvartanī', 'suvarṇabhāsa',
           'kāraṇḍavyūha', 'daśabhūmika', 'samādhirāja', 'ratnagotra', 'nyāyabindu',
           'catuḥśataka', 'śatasāhasrikā', 'aṣṭasāhasrikā', 'buddhacarita')),
    ('II', ('aṣṭādhyāyī', 'mahābhāṣya', 'kāśikā', 'dhātupāṭha', 'vārttika',
            'gaṇapāṭha', 'liṅgānuśāsana', 'paribhāṣ', 'mugdhabodha', 'sārasvata',
            'vākyapadīya', 'vyākaraṇa', 'prakriyā', 'siddhāntakaumudī')),
    # I — Vedic by genre/name (NOT bare 'saṃhitā'/'veda': those also name medical
    # saṃhitās / Āyurveda-Dhanurveda; use only unambiguous Vedic morphemes).
    ('I', ('brāhmaṇa', 'āraṇyaka', 'upaniṣad', 'upaniṣat', 'śrautasūtra',
           'gṛhyasūtra')),
    # III — Epic prolongements named transparently.
    ('III', ('purāṇa', 'harivaṃśa')),
]


def _norm(name):
    """Match key: strip a trailing parenthetical recension ('(Śaunaka)') + spaces."""
    return re.sub(r'\s*\([^)]*\)\s*$', '', name).strip()


def load_clean():
    """text name → {date, genre}; also a normalised-name index for fuzzy match."""
    rows = json.load(open(CLEAN, encoding='utf-8'))
    exact = {r['name']: r for r in rows}
    norm = {}
    for r in rows:
        norm.setdefault(_norm(r['name']), r)
    return exact, norm


def load_timeslot_dates():
    """text → fallback date, via dcsTimeSlot calibrated against the dated texts."""
    if not os.path.exists(CHAPTER_INFO):
        return {}, {}
    xml = open(CHAPTER_INFO, encoding='utf-8').read()
    t2slot = {}
    for ch in re.findall(r'<chapter>(.*?)</chapter>', xml, re.S):
        nm = re.search(r'<textName>(.*?)</textName>', ch)
        ts = re.search(r'<dcsTimeSlot>(.*?)</dcsTimeSlot>', ch)
        if nm and ts:
            t2slot.setdefault(nm.group(1).strip(), ts.group(1).strip())
    return t2slot


def state_by_date(d):
    """Diachronic fallback (cannot yield II/V — those need genre/name)."""
    if d is None:
        return None
    if d < -200:
        return 'I'
    if d < 400:
        return 'III'
    return 'IV'


def build_text_states():
    """Resolve every corpus text dir → {state, genre, date, source, confidence}."""
    exact, norm = load_clean()
    t2slot = load_timeslot_dates()
    # calibrate slot → median date from texts that have both
    slot_dates = collections.defaultdict(list)
    for t, s in t2slot.items():
        r = exact.get(t) or norm.get(_norm(t))
        if r:
            slot_dates[s].append(r['date'])
    slot_med = {s: int(statistics.median(v)) for s, v in slot_dates.items() if v}

    dirs = sorted(d for d in os.listdir(FILES)
                  if os.path.isdir(os.path.join(FILES, d)))
    out = {}
    for name in dirs:
        r = exact.get(name) or norm.get(_norm(name))
        genre = r['genre'] if r else None
        date = r['date'] if r else slot_med.get(t2slot.get(name))
        low = name.lower()

        state = source = None
        # (a) authoritative DCS genre
        if genre and genre in GENRE_RENOU:
            state, source = GENRE_RENOU[genre], 'clean-genre'
        elif genre == 'Sūtra/Dharma':
            state, source = (state_by_date(date) or 'I'), 'clean-genre+date'
        # (b) name hints (catch Buddhist V / grammar II the genre file misses)
        if state is None or state in ('III', 'IV', None):
            for st, subs in NAME_HINTS:
                if any(sub in low for sub in subs):
                    state, source = st, 'name-hint'
                    break
        # (c) date fallback
        if state is None:
            state = state_by_date(date)
            source = 'date' if state else None
        conf = {'clean-genre': 'high', 'clean-genre+date': 'high',
                'name-hint': 'medium', 'date': 'low'}.get(source, 'none')
        out[name] = {'renou': state, 'genre': genre, 'date': date,
                     'source': source, 'confidence': conf}
    return out


def lemmas_in_file(path):
    """Distinct CoNLL-U lemmas (column 3) in one chapter file."""
    out = set()
    with open(path, encoding='utf-8') as f:
        for line in f:
            if not line or line[0] in '#\n':
                continue
            c = line.split('\t')
            if len(c) > 3 and c[0].isdigit() and c[2] != '_':
                out.add(c[2])
    return out


def build_index(limit=None):
    texts = build_text_states()
    idx = {}  # lemma → {states:set, oldest_date, oldest_text, n_texts}
    scanned = 0
    names = sorted(texts)
    if limit:
        names = names[:limit]
    for name in names:
        ts = texts[name]
        state, date = ts['renou'], ts['date']
        if not state:
            continue
        d = os.path.join(FILES, name)
        lemmas = set()
        for fn in os.listdir(d):
            if fn.endswith('.conllu'):
                lemmas |= lemmas_in_file(os.path.join(d, fn))
        for lem in lemmas:
            e = idx.get(lem)
            if e is None:
                e = idx[lem] = {'states': set(), 'oldest_date': None,
                                'oldest_text': None, 'n_texts': 0}
            e['states'].add(state)
            e['n_texts'] += 1
            if date is not None and (e['oldest_date'] is None or date < e['oldest_date']):
                e['oldest_date'] = date
                e['oldest_text'] = name
        scanned += 1
        if scanned % 25 == 0:
            print('  scanned %d/%d texts, %d lemmas so far'
                  % (scanned, len(names), len(idx)), file=sys.stderr)
    # finalise: sets → ordered lists; derive oldest state from oldest_text
    final = {}
    for lem, e in idx.items():
        states = sorted(e['states'], key=_ORDER.get)
        oldest_state = texts[e['oldest_text']]['renou'] if e['oldest_text'] else ''
        final[lem] = {'renou': states, 'renou_oldest': oldest_state,
                      'oldest_date': e['oldest_date'], 'oldest_text': e['oldest_text'],
                      'n_texts': e['n_texts']}
    return final, texts


def report_texts(texts):
    by_state = collections.Counter(t['renou'] for t in texts.values())
    by_src = collections.Counter(t['source'] for t in texts.values())
    print('DCS texts resolved: %d' % len(texts))
    print('by Renou state:', {k: by_state.get(k, 0) for k in STATES},
          '· unresolved:', by_state.get(None, 0))
    print('by source:', dict(by_src))
    print('\nname-hint / unresolved texts (spot-check):')
    for n, t in sorted(texts.items()):
        if t['source'] in ('name-hint', None) or t['confidence'] == 'low':
            print('  %-3s %-10s %s' % (t['renou'] or '?', t['source'] or 'none', n))


def main():
    args = sys.argv[1:]
    if '--texts' in args:
        report_texts(build_text_states())
        return
    out = OUT
    limit = None
    i = 0
    while i < len(args):
        if args[i] == '--out':
            out = args[i + 1]; i += 2
        elif args[i] == '--limit':
            limit = int(args[i + 1]); i += 2
        else:
            raise SystemExit('unknown option: %s' % args[i])
    final, texts = build_index(limit)
    tmp = out + '.tmp'
    json.dump(final, open(tmp, 'w', encoding='utf-8'),
              ensure_ascii=False, sort_keys=True)
    os.replace(tmp, out)
    cov = collections.Counter()
    for e in final.values():
        for s in e['renou']:
            cov[s] += 1
    print('lemmas indexed: %d' % len(final))
    print('lemmas carrying each state:', {k: cov.get(k, 0) for k in STATES})
    print('→ %s' % os.path.basename(out))


if __name__ == '__main__':
    main()
