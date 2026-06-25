#!/usr/bin/env python
"""renou_register.py — resolve a Renou *register* (subsection) from an <ls> source.

Phase 2 of RENOU_SUBSECTIONS_PLAN.md: the citation route to the register axis,
complementing the DCS-corpus route in build_dcs_renou.py. Given one record from an
`ls_source_map*.json` (the curated siglum → {renou, genre, name, …} table), return
the set of registers that source belongs to. This is the only route for registers
the corpus barely has — **jaina** (Jaina sigla) and a second signal for **bhāṣya**
(commentary sigla: Sāyaṇa, Kāśikā-vṛtti, Mahābhāṣya).

A record can map to several registers (Kāśikā-vṛtti = vyākaraṇa **and** bhāṣya).

Note on `epig`: the curated maps are top-citation *literary* sources; inscriptions
are rarely top-cited, so `epig` is ~0 from this route too. Inscriptional sigla would
have to be added to the CANON in build_ls_map*.py — tracked as Phase 3.
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
