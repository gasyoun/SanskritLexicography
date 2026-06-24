#!/usr/bin/env python
"""renou_sigla.py — per-dictionary <ls> siglum → Renou state, for the inline dicts.

PWG/PW/PWK/SCH use Petersburg sigla (handled by build_ls_map.py + ls_source_map.json).
MW has its own (build_ls_map_mw.py). This module covers the remaining English-tradition
dictionaries whose sigla differ again:

  - APTE  (ap, ap90): Apte's own abbreviations — note R = *Raghuvaṃśa* (not Rāmāyaṇa),
                      Mv = *Mahāvīracarita* (not Mahāvastu).
  - BENFEY (ben):     Benfey's abbreviations.
  - BHS   (bhs):      Edgerton, Buddhist Hybrid Sanskrit — nearly every text citation is
                      Buddhist → V, so we use default-V + a blocklist of meta sigla
                      (editors / dictionaries / scholars, not texts).

Tables are the curated top sigla (cover the bulk of citations); unmapped sigla simply
don't contribute. Each maps siglum → (Renou state, approx date) for the oldest flag.
"""
import re

ROMAN = re.compile(r'^[IVXLCMivxlcm]+[.,]?$')   # a volume/verse roman ref, not a siglum
_LS = re.compile(r'<ls\b([^>]*)>(.*?)</ls>', re.S)
_NATTR = re.compile(r'\bn\s*=\s*"([^"]*)"')


def first_siglum(attr, inner):
    """Leading siglum of an inline <ls>: the n="" value if present, else the first
    1–2 text tokens before any digit or roman-numeral reference."""
    m = _NATTR.search(attr)
    raw = m.group(1) if (m and m.group(1).strip()) else re.sub(r'<[^>]+>', '', inner)
    out = []
    for tok in raw.strip().split():
        if ROMAN.match(tok) or any(c.isdigit() for c in tok):
            break
        out.append(tok)
        if len(out) >= 2:
            break
    return re.sub(r'\s+', ' ', ' '.join(out)).strip().rstrip('.').strip()


def sigla_in_block(block):
    return [first_siglum(m.group(1), m.group(2)) for m in _LS.finditer(block)]


# ---- APTE (ap, ap90) : siglum → (state, date) -------------------------------------
APTE = {
    'R': ('IV', 420),     'Ms': ('III', 150),  'Mb': ('III', 80),   'MBh': ('III', 80),
    'Bhāg': ('III', 950), 'Śi': ('IV', 650),   'Ś': ('IV', 420),    'Ku': ('IV', 420),
    'Rām': ('III', 70),   'Ki': ('IV', 550),   'Pt': ('IV', 300),   'U': ('IV', 700),
    'Rv': ('I', -1125),   'Māl': ('IV', 750),  'Bg': ('III', 200),  'Bk': ('IV', 650),
    'P': ('II', -400),    'Me': ('IV', 420),   'K': ('IV', 620),    'Bh': ('IV', 550),
    'Y': ('III', 300),    'Uṇ': ('II', -300),  'Mu': ('IV', 400),   'N': ('IV', 1150),
    'Dk': ('IV', 600),    'H': ('IV', 1000),   'Mk': ('IV', 400),   'Mv': ('IV', 700),
    'Bv': ('IV', 1450),   'Ve': ('IV', 700),   'Gīt': ('IV', 1100), 'Mal': ('IV', 420),
    'Amar': ('IV', 450),  'Megh': ('IV', 420), 'Rag': ('IV', 420),  'Ragh': ('IV', 420),
    'Nā': ('IV', 700),    'Pratimā': ('IV', 420), 'Av': ('I', -940), 'Mbh': ('III', 80),
    'Sk': ('IV', 1400),   'Śiś': ('IV', 650),  'Kir': ('IV', 550),  'Kum': ('IV', 420),
}

# ---- BENFEY (ben) -----------------------------------------------------------------
BENFEY = {
    'MBh': ('III', 80),       'Man': ('III', 150),    'Rām': ('III', 70),
    'Pañc': ('IV', 300),      'Bhāg. P': ('III', 950), 'Hit': ('IV', 1000),
    'Rājat': ('IV', 1150),    'Vikr': ('IV', 420),    'Śāk': ('IV', 420),
    'Daśak': ('IV', 600),     'Ragh': ('IV', 420),    'Bhartṛ': ('IV', 550),
    'Suśr': ('IV', 400),      'Rigv': ('I', -1125),   'Utt. Rāmac': ('IV', 700),
    'Kathās': ('IV', 1050),   'Hariv': ('III', 200),  'Megh': ('IV', 420),
    'Nal': ('III', 80),       'Yājñ': ('III', 300),   'Śiś': ('IV', 650),
    'Kir': ('IV', 550),       'Bhag': ('III', 200),   'Vedāntas': ('IV', 800),
    'Mālat': ('IV', 750),     'Amar': ('IV', 450),    'Pat': ('II', -150),
    'Śet': ('IV', 700),       'Kum': ('IV', 420),     'Vet': ('IV', 1100),
}

# ---- BHS (bhs) : default V (Buddhist) for any text; these sigla are NOT texts -----
BHS_META = {
    'Senart', 'Mironov', 'BR', 'PTSD', 'pw', 'CPD', 'Renou', 'BHSD', 'Edgerton',
    'Wogihara', 'Lévi', 'Levi', 'Kern', 'Burnouf', 'Speyer', 'Lefmann', 'Weller',
    'Régamey', 'Regamey', 'Finot', 'Bendall', 'Cowell', 'Müller', 'Muller',
    'Johnston', 'Tucci', 'Lüders', 'Luders', 'WZKM', 'BSOAS', 'JAOS', 'IHQ',
    'MW', 'Index', 'Sb', 'Foucaux', 'Jones', 'Thomas', 'Konow', 'Sten', 'ms', 'mss',
}
BHS_DATE = 200  # Buddhist Hybrid Sanskrit ~ early centuries CE

_TABLES = {'ap': APTE, 'ap90': APTE, 'ben': BENFEY}


def states_for_block(code, block):
    """({states}, (oldest_state, oldest_date)) for an inline-dict entry block."""
    states, oldest = set(), None  # oldest=(state,date)
    for sig in sigla_in_block(block):
        if not sig:
            continue
        if code == 'bhs':
            if sig in BHS_META:
                continue
            st, d = 'V', BHS_DATE
        else:
            hit = _TABLES.get(code, {}).get(sig)
            if not hit:
                continue
            st, d = hit
        states.add(st)
        if oldest is None or d < oldest[1]:
            oldest = (st, d)
    return states, oldest
