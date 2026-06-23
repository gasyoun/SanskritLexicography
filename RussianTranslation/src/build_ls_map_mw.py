#!/usr/bin/env python
"""Build ls_source_map_mw.json — Monier-Williams <ls> source → Renou state.

The MW sibling of build_ls_map.py. MW <ls> sigla differ from PWG's: there is no
n="" attribute and the citation embeds a lowercase-roman volume reference
(e.g. <ls>RV. v, 86, 5</ls>), so the siglum is the leading token(s) up to the
first lowercase roman numeral or digit. Note MW's 'L.' (uppercase = the native
lexicographers) is NOT a roman numeral and stays a siglum.

Each curated source carries its Renou language-state (I–V) and an approximate
date (for the oldest-citation flag), mirroring ls_source_map.json so
annotate_renou.py can consume either with --dict pwg|mw. MW is where state V
(Buddhist/Jaina) actually populates.

  python build_ls_map_mw.py
"""
import json, os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
MW = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02', 'mw', 'mw.txt'))
OUT = os.path.join(HERE, 'ls_source_map_mw.json')

LS = re.compile(r'<ls\b[^>]*>(.*?)</ls>', re.S)
ROMAN = re.compile(r'^[ivxlcdm]+[.,]?$')   # lowercase roman = volume/verse ref


def source_key(inner):
    """Leading siglum token(s) of an MW <ls>, before any digit/lowercase-roman ref."""
    raw = re.sub(r'<[^>]+>', '', inner).strip()
    out = []
    for t in raw.split():
        if any(ch.isdigit() for ch in t):
            break
        if ROMAN.match(t):
            break
        out.append(t)
        if len(out) >= 3:
            break
    return re.sub(r'\s+', ' ', ' '.join(out)).strip().rstrip('.').strip()


# Meta sigla that are not a Sanskrit text in an era (cross-refs / modern works) — dropped.
SKIP = {'ib', 'W', 'MW', 'Cat', 'Gal', 'ind', 'comm', 'sft', ''}

# siglum (as source_key returns it, '.'-stripped) → (name, renou, approx date)
CANON = {
    # ---- I  Vedic: Saṃhitā / Brāhmaṇa / Upaniṣad / Sūtra / Vedāṅga ----
    'RV': ('Ṛgveda', 'I', -1125),         'AV': ('Atharvaveda', 'I', -940),
    'ŚBr': ('Śatapatha-Brāhmaṇa', 'I', -800), 'TS': ('Taittirīya-Saṃhitā', 'I', -1000),
    'VS': ('Vājasaneyi-Saṃhitā', 'I', -900), 'KātyŚr': ('Kātyāyana-Śrautasūtra', 'I', -400),
    'AitBr': ('Aitareya-Brāhmaṇa', 'I', -700), 'TBr': ('Taittirīya-Brāhmaṇa', 'I', -800),
    'TāṇḍyaBr': ('Tāṇḍya-Brāhmaṇa', 'I', -700), 'VBr': ('Vaṃśa-Brāhmaṇa', 'I', -700),
    'Br': ('Brāhmaṇa (gen.)', 'I', -800),  'Nir': ('Nirukta', 'I', -500),
    'MaitrS': ('Maitrāyaṇī-Saṃhitā', 'I', -1000), 'MaitrUp': ('Maitrī-Upaniṣad', 'I', 50),
    'ChUp': ('Chāndogya-Upaniṣad', 'I', -585), 'Kāṭh': ('Kāṭhaka', 'I', -900),
    'Kauś': ('Kauśika-Sūtra', 'I', -600), 'Lāṭy': ('Lāṭyāyana-Śrautasūtra', 'I', -400),
    'ŚāṅkhŚr': ('Śāṅkhāyana-Śrautasūtra', 'I', -500), 'ĀpŚr': ('Āpastamba-Śrautasūtra', 'I', -450),
    'ĀśvŚr': ('Āśvalāyana-Śrautasūtra', 'I', -450), 'ŚrS': ('Śrautasūtra (gen.)', 'I', -450),
    'Gaut': ('Gautama-Dharmasūtra', 'I', -450), 'Up': ('Upaniṣad (gen.)', 'I', -400),
    # ---- II  Pāṇinian / grammarians' Sanskrit ----
    'Pāṇ': ('Pāṇini, Aṣṭādhyāyī', 'II', -400), 'Pat': ('Patañjali, Mahābhāṣya', 'II', -150),
    'Dhātup': ('Dhātupāṭha', 'II', -350), 'Uṇ': ('Uṇādisūtra', 'II', -300),
    'Kāś': ('Kāśikā-vṛtti', 'II', 650),    'Vop': ('Vopadeva, Mugdhabodha', 'II', 1250),
    # ---- III  Epic & its prolongements (Itihāsa, Purāṇa, Smṛti) ----
    'MBh': ('Mahābhārata', 'III', 80),     'R': ('Rāmāyaṇa', 'III', 70),
    'Hariv': ('Harivaṃśa', 'III', 200),    'BhP': ('Bhāgavata-Purāṇa', 'III', 950),
    'VP': ('Viṣṇu-Purāṇa', 'III', 450),    'MārkP': ('Mārkaṇḍeya-Purāṇa', 'III', 550),
    'Pur': ('Purāṇa (gen.)', 'III', 700),  'Mn': ('Manusmṛti', 'III', 150),
    'Yājñ': ('Yājñavalkya-Smṛti', 'III', 300),
    # ---- IV  Classical: kāvya, drama, kathā, classical śāstra, kośa ----
    'L': ('lexicographers (kośa tradition)', 'IV', 1100),
    'Kathās': ('Kathāsaritsāgara', 'IV', 1050), 'Kāv': ('Kāvya / poetics', 'IV', 600),
    'VarBṛS': ('Varāhamihira, Bṛhatsaṃhitā', 'IV', 550), 'Rājat': ('Rājataraṅgiṇī', 'IV', 1150),
    'Pañcat': ('Pañcatantra', 'IV', 300),  'Ragh': ('Raghuvaṃśa', 'IV', 420),
    'Sāh': ('Sāhityadarpaṇa', 'IV', 1400), 'Car': ('Caraka-Saṃhitā', 'IV', 100),
    'Suśr': ('Suśruta-Saṃhitā', 'IV', 400), 'Śiś': ('Śiśupālavadha', 'IV', 650),
    'Hit': ('Hitopadeśa', 'IV', 1000),     'Bhpr': ('Bhāvaprakāśa', 'IV', 1550),
    'Daś': ('Daśakumāracarita', 'IV', 600), 'Hcat': ('Hemādri, Caturvargacintāmaṇi', 'IV', 1300),
    'Kād': ('Kādambarī', 'IV', 620),       'Sarvad': ('Sarvadarśanasaṃgraha', 'IV', 1350),
    'Mṛcch': ('Mṛcchakaṭikā', 'IV', 400),  'Bālar': ('Bālarāmāyaṇa', 'IV', 900),
    'Kum': ('Kumārasambhava', 'IV', 420),  'Pañcar': ('Pañcarātra', 'IV', 800),
    'Bhartṛ': ('Bhartṛhari, Śatakatraya', 'IV', 550), 'Kām': ('Kāmandakīya-Nītisāra', 'IV', 750),
    'Bhaṭṭ': ('Bhaṭṭikāvya', 'IV', 650),   'Śak': ('Abhijñānaśākuntala', 'IV', 420),
    'Var': ('Varāhamihira', 'IV', 550),    'Sāy': ('Sāyaṇa (comm.)', 'IV', 1350),
    'Amar': ('Amarakośa', 'IV', 450),      'Megh': ('Meghadūta', 'IV', 420),
    'Gīt': ('Gītagovinda', 'IV', 1100),    'Vikr': ('Vikramorvaśīya', 'IV', 420),
    # ---- V  Buddhist & Jaina / Hybrid Sanskrit ----
    'Buddh': ('Buddhist Sanskrit (gen.)', 'V', 200), 'Lalit': ('Lalitavistara', 'V', 200),
    'Divyāv': ('Divyāvadāna', 'V', 250),   'Kāraṇḍ': ('Kāraṇḍavyūha', 'V', 400),
    'SaddhP': ('Saddharmapuṇḍarīka', 'V', 200), 'Jain': ('Jaina Sanskrit (gen.)', 'V', 400),
    'Kalpas': ('Kalpasūtra (Jaina)', 'V', -100),
}


def main():
    assert all(v[1] in ('I', 'II', 'III', 'IV', 'V') for v in CANON.values())
    data = open(MW, encoding='utf-8').read()
    freq = collections.Counter()
    for m in LS.finditer(data):
        k = source_key(m.group(1))
        if k and k not in SKIP:
            freq[k] += 1
    total = sum(freq.values())

    out = {}
    for key, (name, state, date) in CANON.items():
        out[key] = {'name': name, 'renou': state, 'date': date,
                    'citations': freq.get(key, 0)}
    json.dump(out, open(OUT, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1, sort_keys=True)

    mapped = sum(r['citations'] for r in out.values())
    print('MW <ls>: %d citations, %d distinct sigla' % (total, len(freq)))
    print('mapped sources: %d  (%.1f%% of all citations)'
          % (len(out), 100.0 * mapped / total if total else 0))
    RENOU_NAME = {'I': 'Vedic', 'II': 'Pāṇinian', 'III': 'Epic',
                  'IV': 'Classical', 'V': 'Buddhist/Jaina'}
    by_src = collections.Counter(r['renou'] for r in out.values())
    by_cit = collections.Counter()
    for r in out.values():
        by_cit[r['renou']] += r['citations']
    print('Renou language-state (I–V) — mapped sources / citations:')
    for st in ('I', 'II', 'III', 'IV', 'V'):
        print('  %-3s %-15s %3d sources · %7d citations'
              % (st, RENOU_NAME[st], by_src.get(st, 0), by_cit.get(st, 0)))
    print('→ %s' % os.path.basename(OUT))


if __name__ == '__main__':
    main()
