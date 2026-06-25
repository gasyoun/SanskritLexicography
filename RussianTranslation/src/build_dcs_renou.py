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

# ── Register axis (Renou's subsections; orthogonal to the state) ──────────────
# See RENOU_SUBSECTIONS_PLAN.md. The canonical code list lives in renou_register.py
# (shared with the <ls> citation route) so the two never drift.
from renou_register import REGISTERS, _RORDER

# DCS genre → register (the clean, high-confidence route). 'Vedic Saṃhitā' is split
# by name (RV/AV/YV) and 'Sūtra/Dharma' by date (Vedic sūtra vs later smṛti); both
# handled in registers_for_text. Medical/Arthaśāstra/Philosophy/Kośa have no distinct
# Renou register (classical śāstra prose) → None.
GENRE_REGISTER = {
    'Brāhmaṇa': 'brahmana', 'Upaniṣad': 'upanisad', 'Ritual': 'sutra',
    'Vyākaraṇa': 'vyakarana',
    'Epic': 'epic', 'Purāṇa': 'purana', 'Tantra/Āgama': 'tantra',
    'Kāvya': 'kavya', 'Nāṭya': 'natya', 'Narrative Prose': 'katha',
    'Buddhist': 'bauddha',
}
# Name substrings → register, additive (medium confidence). The key one is **bhasya**
# (commentary) — DCS has no commentary genre, so name-stems are the only corpus route.
# Buddhist name hints (for V-texts the genre file misses) are appended from NAME_HINTS.
NAME_REGISTER = [
    ('bhasya', ('bhāṣya', 'bhāsya', 'ṭīkā', 'ṭippaṇ', 'vṛtti', 'vārttika',
                'vivaraṇa', 'vyākhyā', 'pañjikā', 'dīpikā')),
    ('vyakarana', ('aṣṭādhyāyī', 'kāśikā', 'vyākaraṇa', 'siddhāntakaumudī', 'prakriyā')),
    ('jaina', ('jaina',)),
    ('karika', ('kārikā',)),
    ('purana', ('purāṇa', 'harivaṃśa')),
    ('sutra', ('śrautasūtra', 'gṛhyasūtra', 'dharmasūtra', 'kalpasūtra', 'śrauta', 'gṛhya')),
    ('smrti', ('smṛti', 'dharmaśāstra')),
    ('upanisad', ('upaniṣad', 'upaniṣat')),
    ('brahmana', ('brāhmaṇa', 'āraṇyaka')),
    ('bauddha', dict(NAME_HINTS)['V']),
]
_VEDA_SPLIT = (('atharva', ('atharva',)),
               ('yajus', ('yajur', 'yajus', 'taittirīya', 'vājasaneyi',
                          'maitrāyaṇī', 'kāṭhaka')))


def registers_for_text(genre, date, low, conf_rank):
    """{register_code: confidence_rank} for one text. Genre route = the text's own
    confidence; name route = medium; both are unioned (a text can be several registers)."""
    regs = {}
    base = GENRE_REGISTER.get(genre)
    if genre == 'Vedic Saṃhitā':
        base = 'rgveda'
        for code, subs in _VEDA_SPLIT:
            if any(s in low for s in subs):
                base = code
                break
    elif genre == 'Sūtra/Dharma':
        base = 'sutra' if (date is not None and date < -200) else 'smrti'
    if base:
        regs[base] = conf_rank
    for code, subs in NAME_REGISTER:
        if any(s in low for s in subs):
            regs[code] = max(regs.get(code, 0), _CONF_RANK['medium'])
    return regs


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
        regs = registers_for_text(genre, date, low, _CONF_RANK.get(conf, 0))
        out[name] = {'renou': state, 'genre': genre, 'date': date,
                     'source': source, 'confidence': conf, 'registers': regs}
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


# text-state confidence → rank (for per-state "best evidence" tracking). A state
# resting only on low-confidence date-fallback texts is the over-tag thin tail.
_CONF_RANK = {'high': 2, 'medium': 1, 'low': 0, 'none': 0}
_RANK_CONF = {2: 'high', 1: 'medium', 0: 'low'}


def build_index(limit=None):
    texts = build_text_states()
    idx = {}  # lemma → per-state evidence + oldest
    scanned = 0
    names = sorted(texts)
    if limit:
        names = names[:limit]
    for name in names:
        ts = texts[name]
        state, date = ts['renou'], ts['date']
        if not state:
            continue
        conf = _CONF_RANK.get(ts['confidence'], 0)
        d = os.path.join(FILES, name)
        lemmas = set()
        for fn in os.listdir(d):
            if fn.endswith('.conllu'):
                lemmas |= lemmas_in_file(os.path.join(d, fn))
        regs = ts['registers']
        for lem in lemmas:
            e = idx.get(lem)
            if e is None:
                e = idx[lem] = {'state_n': collections.Counter(),
                                'state_conf': {}, 'reg_n': collections.Counter(),
                                'reg_conf': {}, 'oldest_date': None,
                                'oldest_text': None, 'n_texts': 0}
            e['state_n'][state] += 1                 # texts of this state for this lemma
            e['state_conf'][state] = max(e['state_conf'].get(state, 0), conf)
            for rc, rrank in regs.items():           # registers of this text
                e['reg_n'][rc] += 1
                e['reg_conf'][rc] = max(e['reg_conf'].get(rc, 0), rrank)
            e['n_texts'] += 1
            if date is not None and (e['oldest_date'] is None or date < e['oldest_date']):
                e['oldest_date'] = date
                e['oldest_text'] = name
        scanned += 1
        if scanned % 25 == 0:
            print('  scanned %d/%d texts, %d lemmas so far'
                  % (scanned, len(names), len(idx)), file=sys.stderr)
    # finalise: ordered state list + per-state support (n_texts, best confidence).
    # The index is LOSSLESS — the min-support policy is applied by the tagger, so
    # the threshold is tunable without rescanning the corpus.
    final = {}
    for lem, e in idx.items():
        states = sorted(e['state_n'], key=_ORDER.get)
        oldest_state = texts[e['oldest_text']]['renou'] if e['oldest_text'] else ''
        support = {st: {'n': e['state_n'][st], 'conf': _RANK_CONF[e['state_conf'][st]]}
                   for st in states}
        regs = sorted(e['reg_n'], key=lambda c: _RORDER.get(c, 99))
        reg_support = {c: {'n': e['reg_n'][c], 'conf': _RANK_CONF[e['reg_conf'][c]]}
                       for c in regs}
        final[lem] = {'renou': states, 'state_support': support,
                      'register': regs, 'register_support': reg_support,
                      'renou_oldest': oldest_state,
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
    rcov = collections.Counter()
    for e in final.values():
        for s in e['renou']:
            cov[s] += 1
        for r in e.get('register', ()):
            rcov[r] += 1
    print('lemmas indexed: %d' % len(final))
    print('lemmas carrying each state:', {k: cov.get(k, 0) for k in STATES})
    print('lemmas carrying each register:', {k: rcov.get(k, 0) for k in REGISTERS})
    print('→ %s' % os.path.basename(out))


if __name__ == '__main__':
    main()
