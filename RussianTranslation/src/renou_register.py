#!/usr/bin/env python
"""renou_register.py — the Renou *register* (subsection) axis: codes + citation routes.

Companion to the DCS-corpus route in build_dcs_renou.py (which imports `REGISTERS`
from here so the two never drift). Holds the canonical 20-code register lattice and
the `<ls>`-citation detectors that complement the corpus:

  • `ls_registers(rec)` — one `ls_source_map*.json` record → its register(s), from the
    PWG structured `genre` and the source `name`. The only route for **jaina** (Jaina
    sigla) and a second signal for **bhāṣya** (Sāyaṇa, Kāśikā-vṛtti, Mahābhāṣya). One
    record can map to several (Kāśikā-vṛtti = vyākaraṇa **and** bhāṣya).
  • `dedicated_registers(block)` — citation-text detectors not keyed on the siglum map.
    Currently **`epig`**: an inscription marker (`Insch?r` — PWG German 'Inschr.',
    MW/Apte 'Inscr.') in any <ls>. This is the only route to épig (no inscription text
    in DCS, no inscription sigla in the curated CANON), so coverage is sparse by nature.

The inline dicts (ap/ben/bhs), which use renou_sigla not the ls maps, get their
registers from renou_sigla.SIGLUM_REGISTER (+ bhs→bauddha wholesale). See
RENOU_SUBSECTIONS_PLAN.md (Phases 0–5, all done) and RENOU.md.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Canonical register code list (ordered by the Renou chapter that introduces each;
# a register can still attach across states). Imported by build_dcs_renou.py so the
# corpus and citation routes never drift. See RENOU_SUBSECTIONS_PLAN.md.
REGISTERS = ('rgveda', 'atharva', 'yajus', 'brahmana', 'upanisad', 'sutra',   # I
             'vyakarana', 'epig',                                             # II
             'epic', 'purana', 'tantra', 'smrti', 'karika',                   # III
             'bhasya', 'katha', 'natya', 'kavya',                             # IV
             'bauddha', 'jaina', 'hors_inde')                                 # V
_RORDER = {r: i for i, r in enumerate(REGISTERS)}


def sort_registers(regs):
    """Stable chronological-by-chapter order for a register collection."""
    return sorted(regs, key=lambda r: _RORDER.get(r, 99))

# PWG carries a structured genre ('Veda — Brāhmaṇa', 'Kāvya — kathā', …). Map its
# stable left/right parts to a register. 'Veda — Saṃhitā' and bhāṣya/jaina are left to
# the name rules (genre doesn't distinguish RV/AV/YV, nor mark commentary/Jaina).
GENRE_REGISTER = {
    'Veda — Brāhmaṇa': 'brahmana',
    'Veda — Sūtra': 'sutra',
    'Epic': 'epic',            # 'Epic — Gītā/Itihāsa/appendix'
    'Purāṇa': 'purana',
    'Kāvya — kathā': 'katha',
    'Kāvya — drama': 'natya',
    'Kāvya': 'kavya',          # lyric / Mahākāvya / gnomic / historical
    'Śāstra — Dharma': 'smrti',
    'Śāstra — Vyākaraṇa': 'vyakarana',
    # Kośa / Śāstra — Āyurveda|Jyotiṣa|poetics, Veda — Vedāṅga → no Renou register.
}

# Substring rules on the source NAME (lowercased). The only route for MW (its genre
# is empty) and for splits PWG genre can't make. Order doesn't matter — all that match
# fire. Keep specific: a generic '-sūtra' would wrongly catch the Jaina Kalpasūtra.
NAME_RULES = [
    ('atharva',   ('atharvaveda',)),
    ('rgveda',    ('ṛgveda',)),
    ('yajus',     ('taittirīya-saṃhitā', 'vājasaneyi', 'maitrāyaṇī-saṃhitā', 'kāṭhaka')),
    ('brahmana',  ('brāhmaṇa',)),
    ('upanisad',  ('upaniṣad', 'upaniṣat', 'upaniṣ')),
    ('sutra',     ('śrautasūtra', 'gṛhyasūtra', 'dharmasūtra', 'kauśika-sūtra')),
    ('vyakarana', ('aṣṭādhyāyī', 'mahābhāṣya', 'kāśikā', 'mugdhabodha', 'dhātupāṭha',
                   'uṇādi', 'vyākaraṇa')),
    ('bhasya',    ('bhāṣya', 'ṭīkā', 'vṛtti', '(comm.)', 'sāyaṇa')),
    ('epic',      ('mahābhārata', 'rāmāyaṇa', 'harivaṃśa', 'bhagavadgītā')),
    ('purana',    ('purāṇa',)),
    ('smrti',     ('smṛti', 'manusmṛti', 'dharmaśāstra', 'dharma (manu)')),
    ('katha',     ('hitopadeśa', 'pañcatantra', 'kathāsaritsāgara', 'daśakumāra',
                   'kādambarī')),
    ('natya',     ('śākuntala', 'mṛcchakaṭikā', 'vikramorvaśīya', 'bālarāmāyaṇa')),
    ('kavya',     ('meghadūta', 'raghuvaṃśa', 'kumārasambhava', 'bhaṭṭikāvya',
                   'gītagovinda', 'rājataraṅgiṇī', 'śataka', 'amaru-śataka', 'kāvya')),
    ('bauddha',   ('buddhist', 'lalitavistara', 'divyāvadāna', 'saddharma',
                   'kāraṇḍavyūha', 'avadāna')),
    ('jaina',     ('jaina',)),
]


def _genre_register(genre):
    if not genre:
        return None
    # longest-prefix match so 'Kāvya — kathā' beats the 'Kāvya' fallback
    for key in sorted(GENRE_REGISTER, key=len, reverse=True):
        if genre.startswith(key):
            return GENRE_REGISTER[key]
    return None


import re
# Dedicated epigraphic detector: an inscription marker inside an <ls> citation. The
# only route to `epig` (no inscription text in DCS, none in the curated sigla CANON).
# PWG uses German 'Inschr.', MW/Apte 'Inscr.' — 'Insch?r' covers both.
_LS_BLOCK = re.compile(r'<ls\b[^>]*>(.*?)</ls>', re.S)
_INSCRIPTION = re.compile(r'Insch?r')


def dedicated_registers(block):
    """{register codes} from direct citation-text detectors (not the siglum map).
    Currently just `epig` — any <ls> citation carrying an inscription marker."""
    for m in _LS_BLOCK.finditer(block or ''):
        if _INSCRIPTION.search(m.group(1)):
            return {'epig'}
    return set()


def ls_registers(rec):
    """{register codes} for one ls_source_map record. Genre route (PWG) ∪ name route."""
    regs = set()
    gr = _genre_register(rec.get('genre'))
    if gr:
        regs.add(gr)
    name = (rec.get('name') or '').lower()
    for code, subs in NAME_RULES:
        if any(s in name for s in subs):
            regs.add(code)
    return regs


if __name__ == '__main__':
    # self-dump: register assignment for every key in both ls maps (manual sanity)
    import json, os
    HERE = os.path.dirname(os.path.abspath(__file__))
    for f in ('ls_source_map.json', 'ls_source_map_mw.json'):
        m = json.load(open(os.path.join(HERE, f), encoding='utf-8'))
        print('=== %s ===' % f)
        for k, v in sorted(m.items()):
            print('  %-14s %-3s %s' % (k[:14], v.get('renou'),
                                       sorted(ls_registers(v)) or '—'))
