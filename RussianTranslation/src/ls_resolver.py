# -*- coding: utf-8 -*-
"""Cologne <ls> citation -> scan-URL resolver, PWG-only Python port.

Faithful mechanical port of csl-app/lib/core/ls_service.dart +
csl-app/lib/core/ls_patterns.dart (LsPatterns.pwg), scoped to dict 'pwg'.

Entry point:
    generate_href(dict_code, n_attribute, visible) -> str | None

Mirrors Dart:
    generateHref(dict, key, nAttribute, data)
where `key` is computed internally via extractFirstKey (as the Dart caller does).
"""

import re
import sys

# ---------------------------------------------------------------------------
# Roman numeral helpers  (LsService.romanInt / romanInt20)
# ---------------------------------------------------------------------------

_ROMAN_MAP = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100, 'd': 500, 'm': 1000}


def roman_int(roman: str) -> int:
    if not roman:
        return 0
    s = roman.lower()
    result = 0
    for i in range(len(s)):
        if s[i] not in _ROMAN_MAP:
            return 0
        current = _ROMAN_MAP[s[i]]
        nxt = _ROMAN_MAP[s[i + 1]] if (i + 1 < len(s) and s[i + 1] in _ROMAN_MAP) else 0
        if current < nxt:
            result -= current
        else:
            result += current
    return result


_ROMAN20 = {
    'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7, 'viii': 8,
    'ix': 9, 'x': 10, 'xi': 11, 'xii': 12, 'xiii': 13, 'xiv': 14, 'xv': 15,
    'xvi': 16, 'xvii': 17, 'xviii': 18, 'xix': 19, 'xx': 20,
}


def roman_int20(roman: str) -> int:
    return _ROMAN20.get(roman.lower(), 0)


# ---------------------------------------------------------------------------
# Prefix maps (LsService._codeToPfx / _dictSpecificPrefixes)
# ---------------------------------------------------------------------------

_CODE_TO_PFX = {
    'RV.': 'rv',
    'AV.': 'av',
    'Pāṇ.': 'p',
    'MBh.': 'MBH.',
    'Hariv.': 'hariv',
    'MBh. (ed. Calc.)': 'MBHC',
    'MBh. (ed. Bomb.)': 'MBHB',
    'R.': 'R',
    'R. G.': 'RG',
    'R. (G)': 'RG',
    'R. (ed. Gorr.)': 'RG',
    'R. [G]': 'RG',
    'R. ed. Gorresio': 'RG',
    'R. ed. Bomb.': 'ramayanabom',
    'R. (B.)': 'ramayanabom',
    'R. (ed. Bomb.)': 'ramayanabom',
    'R. B.': 'ramayanabom',
    'R. [B.]': 'ramayanabom',
    'R. [B]': 'ramayanabom',
    'R. ed. Bombay': 'ramayanabom',
    'Dhātup.': 'dp',
    'Dhāt.': 'dp',
    'Kathās.': 'kathas',
    'Mn.': 'M.',
    'BhP.': 'bhp',
    'Yājñ.': 'yajn',
    'Ragh.': 'ragh',
    'Sāh.': 'sahitya',
    'Vop.': 'vop',
    'Halāy.': 'halay',
    'VarBṛS.': 'brihatsam',
    'MārkP.': 'markandeyap',
    'Mārk P.': 'markandeyap',
    'H. an.': 'anekarthaS',
    'Śāk.': 'shakuntala',
    'Śak.': 'shakuntalamw',
    'Śat. Br.': 'shatapathabr',
    'ŚBr.': 'shatapathabr',
    'Sāh. D.': 'sahityadarpana',
    'Bhag.': 'bhagavadgita',
    'Pañcat.': 'pantankose',
    'VS.': 'vajasasa',
    'TS.': 'taittiriyas',
    'Ragh. ed. Calc.': 'raghuvamsacalc',
    'Raghuv.': 'raghuvamsacalc',
    'Ragh. (C)': 'raghuvamsacalc',
    'Rājat.': 'rajatar',
    'Rājat. (C)': 'rajatarcalc',
    'Bhaṭṭ.': 'bhattikavya',
    'TBr.': 'taittiriyabr',
    'KātyŚr.': 'katyasr',
    'Kāty. Śr.': 'katyasr1',
    'Kumāras.': 'kumaras',
    'Kum.': 'kumaras',
    'Mālav.': 'malavikagni',
    'Śṛṅgār.': 'srnga',
    'Śṛṅgt.': 'srnga',
    'Megh.': 'meghaduta',
    'Caurap. (A.)': 'Caurapañcāśikā',
    'Caurap.': 'Caurapañcāśikā',
    'Bhartṛ.': 'Bhartṛhariśataka',
    'Hit.': 'Hit.',
    'AK.': 'AK.',
    'Gīt.': 'Gīt.',
    'Pañcar.': 'pancar',
    'Vikr.': 'vikramor',
    'Vikram.': 'vikramor',
    'Ait. Br.': 'aitbr',
    'AitBr.': 'aitbr',
    'Nir.': 'nir',
    'Naigh.': 'naigh',
    'Nigh.': 'naigh',
    # PWG-specific uppercase abbreviations
    'H.': 'h',
    'an.': 'an',
    'MED.': 'med',
    'ŚĀK.': 'shakuntala_pwg',
    'RĀJA-TAR.': 'rajatar_pwg',
    'RĀJAT.': 'rajatar_pwg',
    'RAGH.': 'ragh_pwg',
    'RAGH. ed. ST.': 'ragh_st',
    'RAGH. ed. Calc.': 'ragh_pwg',
    'MĀRK. P.': 'markp_pwg',
    'BHAG.': 'bhag_pwg',
    'YĀJÑ.': 'yajn_pwg',
    'AIT. BR.': 'aitbr_pwg',
}

_DICT_SPECIFIC_PREFIXES = {
    'pwg': {
        'P.': 'p_pwg',
        'ṚV.': 'rv_pwg',
        'AV.': 'av_pwg',
    },
}


def extract_first_key(data: str):
    """LsService.extractFirstKey."""
    complex_prefixes = [
        'R. ed. Bomb.',
        'Bhāg. P.',
        'Varāh. Bṛh. S.',
        'Mārk. P.',
        'Śat. Br.',
        'Sāh. D.',
        'Verz. d. Oxf. H.',
    ]
    for complx in complex_prefixes:
        if data.startswith(complx):
            return complx
    m = re.match(r"^([^ .,']+\.?)", data)
    return m.group(1) if m else None


def get_prefix(dict_code: str, key: str):
    """LsService.getPrefix."""
    if dict_code in _DICT_SPECIFIC_PREFIXES:
        dp = _DICT_SPECIFIC_PREFIXES[dict_code]
        if key in dp:
            return dp[key]
    return _CODE_TO_PFX.get(key)


# ---------------------------------------------------------------------------
# Pattern list (LsPatterns.pwg).  urlTemplate uses $1,$2,... group refs.
# ---------------------------------------------------------------------------

class LsPattern:
    __slots__ = ('regex', 'url_template', 'dicts')

    def __init__(self, regex, url_template, dicts=None):
        self.regex = regex
        self.url_template = url_template
        self.dicts = dicts


PWG_PATTERNS = [
    # Spr. 1st edition (pwg)
    LsPattern(r'^(Spr[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/boesp1/app1/?$2',
              ['pwg']),
    # Spr. 2nd edition (pw, pwkvn)
    LsPattern(r'^(Spr[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/boesp2/web1/boesp.html?$2',
              ['pw', 'pwkvn']),
    # Spr. (II) 2nd edition (pwg)
    LsPattern(r'^(Spr[.]) *\(II\) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/boesp2/web1/boesp.html?$2',
              ['pwg']),
    # Spr. (I) 1st edition (pwg)
    LsPattern(r'^(Spr[.] *\(I\)) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/boesp1/app1/?$2'),
    # Spr. 2nd edition (pwg)
    LsPattern(r'^(Spr[.]) *\(II\) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/boesp2/web1/boesp.html?$2'),
    # Spr. 1st edition (pwg)
    LsPattern(r'^(Spr[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/boesp1/app1/?$2',
              ['pwg']),
    # MBH. Bombay edition - 3 parms
    LsPattern(r'^(MBH[.] ed. Bomb.) *([0-9]+) *, *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/mbhbomb/app1?$2,$3,$4'),
    LsPattern(r'^(MBH[.]) *([0-9]+) *, *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/mbhbomb/app1?$2,$3,$4'),
    # MBH. Calcutta edition - 2 parms
    LsPattern(r'^(MBH[.] ed. Calc.) *([0-9]+) *, *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/mbhcalc?$2.$3'),
    LsPattern(r'^(MBH[.]) *([0-9]+) *, *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/mbhcalc?$2.$3'),
    # Harivamsa
    LsPattern(r'^(HARIV[.]) *([0-9]+)[.]?',
              'https://sanskrit-lexicon-scans.github.io/hariv?$2'),
    # Verz. d. Oxf. H.
    LsPattern(r'^(Verz\. der Oxf\. H\.) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/Oxf_Cat_Aufrecht/index.html?$2'),
    LsPattern(r'^(Verz\. d\. Oxf\. H\.) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/Oxf_Cat_Aufrecht/index.html?$2'),
    # Kathasaritsagara
    LsPattern(r'^(KATHĀS[.|,] *|KATHĀS\.?) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/kss/index.html?$2,$3'),
    # Vajasaneyi Samhita
    LsPattern(r'^(VS[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/vajasasa/app1?$2,$3'),
    # Rajatar (Troyer) - conditional 7/8 -> calc
    LsPattern(r'^(RĀJA-TAR[.|]RĀJAT[.]) *([0-9]+), *([0-9]+)',
              '($2 == "7" || $2 == "8") ? "https://sanskrit-lexicon-scans.github.io/rajatarcalc/app1?$2,$3" : "https://sanskrit-lexicon-scans.github.io/rajatar/app1?$2,$3"'),
    # Rajatar Calcutta
    LsPattern(r'^(RĀJA-TAR\. ed\. Calc\.?|RĀJAT\. ed\. Calc\.?) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/rajatarcalc/app1?$2,$3'),
    # Yajnavalkya
    LsPattern(r'^(YĀJÑ[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/yajnavalkya/app1?$2,$3'),
    # Raghuvamsa (ST)
    LsPattern(r'^(RAGH[.] ed[.] ST[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/raghuvamsa/app1?$2,$3'),
    # Raghuvamsa Calcutta
    LsPattern(r'^(RAGH[.] ed[.] Calc[.|]RAGH[.] \(ed[.] Calc\)[.|]RAGH[.] \(Calc\)[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/raghuvamsacalc/app1?$2,$3'),
    # Generic RAGH.
    LsPattern(r'^(RAGH[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/raghuvamsa/app1?$2,$3'),
    # Markandeya Purana
    LsPattern(r'^(MĀRK[.] P[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/markandeyapurana/app1?$2,$3'),
    # Bhagavad Gita
    LsPattern(r'^(BHAG[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/bhagavadgita/app1?$2,$3'),
    # Anekartha - H. an.
    LsPattern(r'^(H[.] an[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/anekarthasamgraha/app1?$2,$3'),
    # Anekartha - an.
    LsPattern(r'^(an[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/anekarthasamgraha/app1?$2,$3'),
    # Shakuntala (Bohtlingk)
    LsPattern(r'^(ŚĀK[.]) *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/shakuntala/app2?$2,$3,$4'),
    LsPattern(r'^(ŚĀK[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/shakuntala/app2?$2,$3'),
    LsPattern(r'^(ŚĀK[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/shakuntala/app1?$2'),
    # Aitareya Brahmana
    LsPattern(r'^(AIT[.] BR[.]) *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/aitbr_auf/app1?$2,$3,$4'),
    LsPattern(r'^(AIT[.] BR[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/aitbr/app1?$2,$3'),
    # Malavikagni
    LsPattern(r'^(MĀLAV[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/malavikagni/app2?$2,$3'),
    LsPattern(r'^(MĀLAV[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/malavikagni/app1?$2'),
    # Pancatantra Kosegarten - uppercase Roman numerals
    LsPattern(r'^(PAÑCAT[.]) *([IVXL]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/pantankose/app1?$2,$3'),
    LsPattern(r'^(PAÑCAT[.]) ([VI]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/pantankose/app1?$2_lc,$3'),
    LsPattern(r'^(PAÑCAT[.]) *(Pr[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/pantankose/app1?0,$3'),
    LsPattern(r'^(PAÑCAT[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/pantankose/app2?$2,$3'),
    # Pancatantra ed. orn.
    LsPattern(r'^(PAÑCAT\.? ed\.? orn\.?|ed\.? orn\.?) *([VI]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/pantankoseorn/app2?$2,$3'),
    LsPattern(r'^(PAÑCAT\.? ed\.? orn\.?|ed\.? orn\.?) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/pantankoseorn/app1?$2,$3'),
    # Hitopadesha
    LsPattern(r'^(HIT[.]) *([IVXL]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/hitopadesha/app1?$2,$3'),
    LsPattern(r'^(HIT[.]) ([IV]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/hitopadesha/app1?$2_lc,$3'),
    LsPattern(r'^(HIT[.]) *(Pr[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/hitopadesha/app1?0,$3'),
    LsPattern(r'^(HIT[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/hitopadesha/app2?$2,$3'),
    # Amarakosha deslongchamp
    LsPattern(r'^(AK[.]) *([0-9]+), *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/amara_dlc/app1?$2,$3,$4,$5'),
    LsPattern(r'^(AK[.]) *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/amara_dlc/app1?$2,$3,$4'),
    # Amarakosha Colebrooke - 4 params
    LsPattern(r'^(COL|COLEBR)[.] *([0-9]+), *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/amara_col/app1?$2,$3,$4,$5'),
    LsPattern(r'^(AK[.] ed[.] COLEBR[.]?) *([0-9]+), *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/amara_col/app1?$2,$3,$4,$5'),
    LsPattern(r'^(AK[.] ed[.] COLEBR[.]?) *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/amara_col/app1?$2,$3,$4'),
    LsPattern(r'^(COL|COLEBR)[.] *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/amara_col/app1?$2,$3,$4'),
    # Gitagovinda
    LsPattern(r'^(GĪT[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/gitagov/app1?$2,$3'),
    # Nirukta
    LsPattern(r'^(NIR[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/nirukta/app1?$2,$3'),
    LsPattern(r'^(NIR[.]) *([IVXL]+)',
              'https://sanskrit-lexicon-scans.github.io/nirukta/app0?$2_lc'),
    # Nighantuka
    LsPattern(r'^(NAIGH[.]?) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/nirukta/app2?$2,$3'),
    # Mugdhabodha
    LsPattern(r'^(VOP[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/mugdhabodha/app1?$2,$3'),
    # Bhattikavya
    LsPattern(r'^(BHAṬṬ[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/bhattikavya/app1?$2,$3'),
    # Kumara Sambhava
    LsPattern(r'^(KUMĀRAS[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/kumaras/app1?$2,$3'),
    # Satapatha Brahmana
    LsPattern(r'^(ŚAT[.] BR[.]) *([0-9]+), *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/shatapathabr/app1?$2,$3,$4,$5'),
    # Taittiriya Samhita
    LsPattern(r'^(TS[.]) *([0-9]+), *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/taittiriyas/app1?$2,$3,$4,$5'),
    # Taittiriya Brahmana
    LsPattern(r'^(TBR[.]) *([0-9]+), *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/taittiriyabr/app1?$2,$3,$4,$5'),
    # Katyayana Shrauta Sutra
    LsPattern(r'^(KĀTY[.] ŚR[.]) *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/katyasr/app1?$2,$3,$4'),
    LsPattern(r'^(KĀTY[.] ŚR[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/katyasr/app2?$2,$3'),
    # Pancaratra
    LsPattern(r'^(PAÑCAR[.]) *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/pancar/app1?$2,$3,$4'),
    LsPattern(r'^(PAÑCAR[.]) *S\. *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/pancar/app0?$2'),
    # Vikramorvashiya
    LsPattern(r'^(VIKR[.]|VIKRAM[.]?) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/vikramor/app2?$2,$3'),
    LsPattern(r'^(VIKR[.]|VIKRAM[.]?) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/vikramor/app1?$2'),
    # Nalopakhyana
    LsPattern(r'^(N[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/bchrest1/app1?$2,$3'),
    # Dasharatha's death
    LsPattern(r'^(DAŚ[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/bchrest1/app2?$2,$3'),
    # Vidushaka
    LsPattern(r'^(VID[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/bchrest1/app3?$2'),
    # Caurapancashika
    LsPattern(r'^(CAURAP[.]?) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/bhartrhari/app1?$2'),
    # Vishvamitra's battle
    LsPattern(r'^(VIŚV[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/bchrest1/app4?$2,$3'),
    # Bhartrihari Shataka
    LsPattern(r'^(BHARTṚ[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/bhartrhari/app2?$2,$3'),
    # Bhartrihari Shataka Suppl.
    LsPattern(r'^(BHARTṚ[.] Suppl[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/bhartrhari/app3?$2'),
    # Meghaduta
    LsPattern(r'^(MEGH[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/meghasrnga/app1?$2'),
    # Shringara Tilaka
    LsPattern(r'^(ŚṚṄGĀRAT[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/meghasrnga/app2?$2'),
    # Medinikosha
    LsPattern(r'^(MED[.]) *([a-zA-Z]+)[.] *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/medini/app1?$2_lc,$3'),
    LsPattern(r'^(MED[.]) *([a-zA-Zāīūēōṇṭḍṇñṅśṣḥḍhṭh]+)[.] *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/medini/app1?$2_lc,$3'),
    # Ramayana SCHL prefix - conditional
    LsPattern(r'^(R[.] SCHL[.]) *([0-9]+), *([0-9]+), *([0-9]+)',
              '($2 == "1" || $2 == "2") ? "https://sanskrit-lexicon-scans.github.io/ramayanaschl/?$2,$3,$4" : "https://sanskrit-lexicon-scans.github.io/ramayanagorr/?$2,$3,$4"'),
    # Abhidhana Chintamani Parisishta - standalone ś
    LsPattern(r'^(ś[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/abch2/app2?$2'),
    # Trikandashesha
    LsPattern(r'^(TRIK[.]) *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/medini/app2?$2,$3,$4'),
    # Haravali
    LsPattern(r'^(HĀR[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/medini/app3?$2'),
    # Abhidhana Chintamani Parisishta - with special ś character
    LsPattern(r'^(H\. ś\.) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/abch2/app2?$2'),
    # Abhidhana Chintamani Parisishta
    LsPattern(r'^(H[.] ś[.|]ś[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/abch2/app2?$2'),
    # Abhidhana Chintamani
    LsPattern(r'^(H[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/abch2/app1?$2'),
    # Halayudha
    LsPattern(r'^(HALĀY[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/armh2/app1?$2,$3'),
    # Manu
    LsPattern(r'^(M[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/manu/index.html?$2,$3'),
    # Varaha Brihat Samhita
    LsPattern(r'^(VARĀH[.] BṚH[.] S[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/brihatsam/app1?$2,$3'),
    # Sahitya Darpana
    LsPattern(r'^(SĀH[.] D[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/sahityadarpana/app1?$2,$3'),
    LsPattern(r'^(SĀH[.] D[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/sahityadarpana/app1?$2'),
    # Benfey Chrestomathie (Chr. / BENF. Chr.) -> bchrest2 page viewer (?ipage,
    # 1-372). PWG cites "Chr. page,line" / "BENF. Chr. page,line"; the viewer
    # keys on the printed page only (first number), matching the pw mapping.
    LsPattern(r'^(BENF[.] Chr[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/bchrest2/index.html?$2',
              ['pwg']),
    # Chrestomathie (pw + pwg)
    LsPattern(r'^(Chr[.]) *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/bchrest2/index.html?$2',
              ['pw', 'pwg']),
    # Dhatupatha
    LsPattern(r'^(DHĀTUP[.]) *([0-9]+)(.*)$',
              'https://www.sanskrit-lexicon.uni-koeln.de/scans/csl-westergaard/disp/index.php?section=$2'),
    # Bhagavata Purana - conditional 10/11/12 -> bom
    LsPattern(r'^(BHĀG[.] P[.]) *([0-9]+)[ ,]+([0-9]+)[ ,]+([0-9]+)(.*)$',
              '($2 == "10" || $2 == "11" || $2 == "12") ? "https://sanskrit-lexicon-scans.github.io/bhagp_bom/app1/?$2,$3,$4" : "https://sanskrit-lexicon-scans.github.io/bhagp_bur/app1/?$2,$3,$4"'),
    # Bhagavata Purana Bombay edition
    LsPattern(r'^(BHĀG[.] P[.] ed[.] Bomb[.]) *([0-9]+)[ ,]+([0-9]+)[ ,]+([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/bhagp_bom/app1/?$2,$3,$4'),
    # Ramayana with 4 params - conditional
    LsPattern(r'^(R[.]) *([0-9]+), *([0-9]+), *([0-9]+), *([0-9]+)',
              '($2 == "7") ? "https://sanskrit-lexicon-scans.github.io/ramayanabom/app1/?$2,$3,$4,$5" : ($2 == "1" || $2 == "2") ? "https://sanskrit-lexicon-scans.github.io/ramayanaschl/?$2,$3,$4" : "https://sanskrit-lexicon-scans.github.io/ramayanagorr/?$2,$3,$4"'),
    # Ramayana with 3 params - conditional
    LsPattern(r'^(R[.]) *([0-9]+), *([0-9]+), *([0-9]+)',
              '($2 == "1" || $2 == "2") ? "https://sanskrit-lexicon-scans.github.io/ramayanaschl/?$2,$3,$4" : ($2 == "7") ? "https://sanskrit-lexicon-scans.github.io/ramayanabom/app1/?$2,$3,$4" : "https://sanskrit-lexicon-scans.github.io/ramayanagorr/?$2,$3,$4"'),
    # Ramayana Gorresio - uppercase GORR
    LsPattern(r'^(R[.] GORR[.]) *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/ramayanagorr/?$2,$3,$4'),
    LsPattern(r'^(R[.] GORR[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/ramayanagorr/?$2,$3,1'),
    # Ramayana ed. Gorresio
    LsPattern(r'^(R[.] ed[.] GORR[.]) *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/ramayanagorr/?$2,$3,$4'),
    # Ramayana Gorresio - standalone GORR
    LsPattern(r'^(GORR[.]) *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/ramayanagorr/?$2,$3,$4'),
    LsPattern(r'^(GORR[.]) *([0-9]+), *([0-9]+)',
              'https://sanskrit-lexicon-scans.github.io/ramayanagorr/?$2,$3,1'),
    # Ramayana Bombay - fallback method
    LsPattern(r'^(R[.] ed[.] Bomb[.]|R[.] ed[.] Bombay[.]) *(.*)$',
              'ramayanaBombayUrl'),
    # Ramayana with 2 params (pwg) - conditional
    LsPattern(r'^(R[.]) *([0-9]+), *([0-9]+)',
              '($2 == "1" || $2 == "2") ? "https://sanskrit-lexicon-scans.github.io/ramayanaschl/?$2,$3,1" : ($2 == "7") ? "https://sanskrit-lexicon-scans.github.io/ramayanabom/app1/?$2,$3,1" : "https://sanskrit-lexicon-scans.github.io/ramayanagorr/?$2,$3,1"',
              ['pwg']),
    # Ramayana with 2 params (pw) - conditional
    LsPattern(r'^(R[.]) *([0-9]+), *([0-9]+)',
              '($2 == "1" || $2 == "2") ? "https://sanskrit-lexicon-scans.github.io/ramayanaschl/?$2,$3,1" : "https://sanskrit-lexicon-scans.github.io/ramayanagorr/?$2,$3,1"',
              ['pw']),
    # Panini - Ashtadhyayi
    LsPattern(r'^(P[.]) *([0-9]+), *([0-9]+), *([0-9]+)',
              'https://ashtadhyayi.com/sutraani/$2/$3/$4'),
    # Rig Veda Pratisthana
    LsPattern(r'^(ṚV[.] PRĀTIŚ[.]) *([0-9]+), *([0-9]+)',
              'rvAvHymnUrl2'),
    # Rig Veda - 3 params
    LsPattern(r'^(ṚV[.]) *([0-9]+), *([0-9]+), *([0-9]+)',
              'rvAvHymnUrl'),
    # Rig Veda - 2 params
    LsPattern(r'^(ṚV[.]) *([0-9]+), *([0-9]+)',
              'rvAvHymnUrl2'),
    # Atharva Veda - 3 params
    LsPattern(r'^(AV[.]) *([0-9]+), *([0-9]+), *([0-9]+)',
              'rvAvHymnUrl'),
    # Atharva Veda - 2 params
    LsPattern(r'^(AV[.]) *([0-9]+), *([0-9]+)',
              'rvAvHymnUrl2'),
]


def get_patterns_for_dict(dict_code: str):
    """LsPatterns.getPatternsForDict (pwg branch only reachable here)."""
    d = dict_code.lower()
    if d in ('pwg', 'pw', 'pwkvn'):
        return PWG_PATTERNS
    # Non-pwg dicts intentionally not ported.
    return PWG_PATTERNS


# ---------------------------------------------------------------------------
# Special URL generators (reachable from pwg pattern list)
# ---------------------------------------------------------------------------

def href_rv_av2(pfx: str, data1: str, dict_code: str):
    """LsService.hrefRvAv2."""
    m = re.match(r'^(.*?)\. *PRĀTIŚ\. *([0-9]+), *([0-9]+)(.*)$', data1)
    if m is None:
        m = re.match(r'^(.*?)\. *([^ ,]+)[ ,]+([0-9]+)(.*)$', data1)
    if m is None:
        return None
    mandala = m.group(2)
    imandala = roman_int20(mandala)
    if imandala == 0:
        try:
            imandala = int(mandala)
        except ValueError:
            imandala = 0
    if imandala == 0:
        return None
    ihymn = int(m.group(3))
    iverse = 1
    p = 'rv' if pfx == 'rv' else 'av'
    hymn_file_pfx = '%s%02d.%03d' % (p, imandala, ihymn)
    anchor = '%s.%02d' % (hymn_file_pfx, iverse)
    dir_ = 'https://sanskrit-lexicon.github.io/%slinks/%shymns' % (pfx, pfx)
    return '%s/%s.html#%s' % (dir_, hymn_file_pfx, anchor)


def href_rv_av(pfx: str, data1: str, dict_code: str):
    """LsService.hrefRvAv."""
    match = None
    is3seg = True
    if dict_code == 'ap90':
        match = re.match(r'^(.*?)[.] *([0-9]+)[.] +([0-9]+)[.] +([0-9]+)(.*)$', data1)
    if match is None:
        match = re.match(r'^(.*?)\. *([^ ,]+)[ ,]+([0-9]+)[ ,]+([0-9]+)(.*)$', data1)
        if match is None:
            match = re.match(r'^(.*?)\. *([^ ,]+)[ ,]+([0-9]+)(.*)$', data1)
            is3seg = False
    if match is not None:
        mandala = match.group(2)
        imandala = roman_int20(mandala)
        if imandala == 0:
            try:
                imandala = int(mandala)
            except ValueError:
                imandala = 0
        ihymn = int(match.group(3))
        iverse = int(match.group(4)) if is3seg else 1
        is_mw = dict_code in ('mw', 'pw', 'pwg')
        force00 = is_mw and imandala == 0
        mandala_str = '00' if force00 else '%02d' % imandala
        p = 'rv' if pfx == 'rv' else 'av'
        hymn_file_pfx = '%s%s.%03d' % (p, mandala_str, ihymn)
        anchor = '%s.%02d' % (hymn_file_pfx, iverse)
        dir_ = 'https://sanskrit-lexicon.github.io/%slinks/%shymns' % (pfx, pfx)
        return '%s/%s.html#%s' % (dir_, hymn_file_pfx, anchor)
    return None


def href_ramayana(data1: str, dict_code: str):
    """LsService.hrefRamayana."""
    data2 = re.sub(r'^R\. *', '', data1, count=1)
    m = re.search(r' *([iv]+)[ ,]+([0-9]+)[ ,]+([0-9]+)(.*)$', data2)
    if m is None:
        return None
    ic = roman_int(m.group(1))
    is1 = int(m.group(2))
    iv = int(m.group(3))
    dir_ = 'https://sanskrit-lexicon-scans.github.io/ramayanagorr'
    if dict_code == 'mw' and (ic == 1 or ic == 2):
        dir_ = 'https://sanskrit-lexicon-scans.github.io/ramayanaschl'
    return '%s/?%d,%d,%d' % (dir_, ic, is1, iv)


def href_ramayana_bombay(data1: str):
    """LsService.hrefRamayanaBombay."""
    data2 = re.sub(r'^R\.?.*? *', '', data1, count=1)
    m = re.search(r' *([iv]+)[ ,]+([0-9]+)[ ,]+([0-9]+)(.*)$', data2)
    if m is not None:
        k = roman_int(m.group(1))
        s = int(m.group(2))
        v = int(m.group(3))
        return 'https://sanskrit-lexicon-scans.github.io/ramayanabom/app1/?%d,%d,%d' % (k, s, v)
    m = re.search(r' *([0-9]+)[ ,]+([0-9]+)[ ,]+([0-9]+)[ ,]*([0-9]+)?', data2)
    if m is not None:
        k = m.group(1)
        s = m.group(2)
        v = m.group(3)
        v4 = m.group(4)
        if v4 is not None:
            return 'https://sanskrit-lexicon-scans.github.io/ramayanabom/app1/?%s,%s,%s,%s' % (k, s, v, v4)
        return 'https://sanskrit-lexicon-scans.github.io/ramayanabom/app1/?%s,%s,%s' % (k, s, v)
    return None


# ---------------------------------------------------------------------------
# href* helper chain (pfx-fallback dispatch); pwg-reachable helpers ported.
# ---------------------------------------------------------------------------

def href_panini(data1: str, dict_code: str):
    """LsService.hrefPanini."""
    if dict_code == 'ap90':
        m = re.match(r'^(.*?)[.] *([IV]+)[.] +([0-9]+)[.] +([0-9]+)(.*)$', data1)
        if m is not None:
            ic = roman_int(m.group(2).lower())
            is1 = int(m.group(3))
            iv = int(m.group(4))
            if ic > 0:
                return 'https://ashtadhyayi.com/sutraani/%d/%d/%d' % (ic, is1, iv)
    m = re.match(r'^(.*?)\. *([iv]+)[ ,]+([0-9]+)[ ,]+([0-9]+)(.*)$', data1)
    if m is None:
        return None
    ic = roman_int(m.group(2))
    is1 = int(m.group(3))
    iv = int(m.group(4))
    if ic > 0:
        return 'https://ashtadhyayi.com/sutraani/%d/%d/%d' % (ic, is1, iv)
    return None


def href_ramayana_gorresio(data1: str):
    """LsService.hrefRamayanaGorresio."""
    data2 = re.sub(r'^R\.?.*? *', '', data1, count=1)
    m = re.search(r' *([iv]+)[ ,]+([0-9]+)[ ,]+([0-9]+)(.*)$', data2)
    if m is None:
        return None
    k = roman_int(m.group(1))
    s = int(m.group(2))
    v = int(m.group(3))
    return 'https://sanskrit-lexicon-scans.github.io/ramayanagorr/?%d,%d,%d' % (k, s, v)


def href_mahabharata(data1: str, pfx: str):
    """LsService.hrefMahabharata."""
    m = re.search(r'([0-9]+)[ ,]+([0-9]+)[ ,]+([0-9]+)', data1)
    if m is None:
        return None
    adhyaya, bhaga, shloka = m.group(1), m.group(2), m.group(3)
    if pfx == 'MBHC':
        return 'https://sanskrit-lexicon-scans.github.io/mahabharata/calc/?%s,%s,%s' % (adhyaya, bhaga, shloka)
    elif pfx == 'MBHB':
        return 'https://sanskrit-lexicon-scans.github.io/mahabharata/bomb/?%s,%s,%s' % (adhyaya, bhaga, shloka)
    return None


def href_pancatantra(data1: str):
    m = re.match(r'^(Pañcat\.) *([0-9]+), *([0-9]+)', data1)
    if m is not None:
        return 'https://sanskrit-lexicon-scans.github.io/pantankose/app2?%s,%s' % (m.group(2), m.group(3))
    m = re.match(r'^(Pañcat\.) ([vi]+), *([0-9]+), *([0-9]+)', data1)
    if m is not None:
        adhyaya = roman_int(m.group(2))
        if adhyaya > 0:
            return 'https://sanskrit-lexicon-scans.github.io/pantankose/app1?%d,%s,%s' % (adhyaya, m.group(3), m.group(4))
    return None


def href_harivamsa(data1: str):
    m = re.search(r'([0-9]+)[ ,]+([0-9]+)[ ,]+([0-9]+)', data1)
    if m is None:
        return None
    return 'https://sanskrit-lexicon-scans.github.io/harivamsa/app1?%s,%s,%s' % (m.group(1), m.group(2), m.group(3))


def href_bhagavata_purana(data1: str):
    m = re.search(r'([0-9]+)[ ,]+([0-9]+)[ ,]+([0-9]+)', data1)
    if m is None:
        return None
    return 'https://sanskrit-lexicon-scans.github.io/bhagavatapurana/app1?%s,%s,%s' % (m.group(1), m.group(2), m.group(3))


def href_raghuvamsa(data1: str, pfx: str):
    m = re.search(r'([0-9]+)[ ,]+([0-9]+)[ ,]+([0-9]+)', data1)
    if m is None:
        return None
    if pfx == 'raghuvamsacalc':
        return 'https://sanskrit-lexicon-scans.github.io/raghuvamsacalc/app1?%s,%s,%s' % (m.group(1), m.group(2), m.group(3))
    return None


def href_vajasansamhita(data1: str):
    m = re.search(r'([0-9]+)[ ,]+([0-9]+)[ ,]+([0-9]+)', data1)
    if m is None:
        return None
    return 'https://sanskrit-lexicon-scans.github.io/vajasasa/app1?%s,%s,%s' % (m.group(1), m.group(2), m.group(3))


def href_taittiriya_samhita(data1: str):
    m = re.search(r'([0-9]+)[ ,]+([0-9]+)[ ,]+([0-9]+)', data1)
    if m is None:
        return None
    return 'https://sanskrit-lexicon-scans.github.io/taittiriyas/app1?%s,%s,%s' % (m.group(1), m.group(2), m.group(3))


def href_satapatha_brahmana(data1: str):
    m = re.search(r'([0-9]+)[ ,]+([0-9]+)[ ,]+([0-9]+)', data1)
    if m is None:
        return None
    return 'https://sanskrit-lexicon-scans.github.io/shatapathabr/app1?%s,%s,%s' % (m.group(1), m.group(2), m.group(3))


def href_meghaduta(data1: str):
    m = re.search(r'([0-9]+)[ ,]+([0-9]+)', data1)
    if m is None:
        return None
    return 'https://sanskrit-lexicon-scans.github.io/meghaduta/app1?%s,%s' % (m.group(1), m.group(2))


def href_kumarasambhava(data1: str):
    m = re.search(r'([0-9]+)[ ,]+([0-9]+)[ ,]+([0-9]+)', data1)
    if m is None:
        return None
    return 'https://sanskrit-lexicon-scans.github.io/kumaras/app1?%s,%s,%s' % (m.group(1), m.group(2), m.group(3))


def href_malavikagnimitra(data1: str):
    m = re.search(r'([0-9]+)[ ,]+([0-9]+)', data1)
    if m is None:
        return None
    return 'https://sanskrit-lexicon-scans.github.io/malavikagni/app1?%s,%s' % (m.group(1), m.group(2))


def href_vikramorvashiya(data1: str):
    m = re.search(r'([0-9]+)[ ,]+([0-9]+)', data1)
    if m is None:
        return None
    return 'https://sanskrit-lexicon-scans.github.io/vikramor/app1?%s,%s' % (m.group(1), m.group(2))


def href_bhagavadgita(data1: str):
    m = re.search(r'([0-9]+)[ ,]+([0-9]+)', data1)
    if m is None:
        return None
    return 'https://sanskrit-lexicon-scans.github.io/bhagavadgita/app1?%s,%s' % (m.group(1), m.group(2))


def href_manu(data1: str):
    m = re.search(r'([0-9]+)[ ,]+([0-9]+)', data1)
    if m is None:
        return None
    return 'https://sanskrit-lexicon-scans.github.io/manusmriti/app1?%s,%s' % (m.group(1), m.group(2))


def href_nirukta(data1: str):
    m = re.search(r'([0-9]+)[ ,]+([0-9]+)', data1)
    if m is None:
        return None
    return 'https://sanskrit-lexicon-scans.github.io/nirukta/app1?%s,%s' % (m.group(1), m.group(2))


def href_kathasaritsagara(data1: str):
    m = re.match(r'^(Kathās\.) *([0-9]+), *([0-9]+)', data1)
    if m is not None:
        return 'https://sanskrit-lexicon-scans.github.io/kss/index.html?%s,%s' % (m.group(2), m.group(3))
    return None


def href_spruch(data1: str):
    m = re.match(r'^(Spr\.) *([0-9]+)', data1)
    if m is not None:
        return 'https://sanskrit-lexicon-scans.github.io/boesp2/web1/boesp.html?%s' % m.group(2)
    return None


def href_verz_oxf(data1: str):
    m = re.match(r'^(Verz\. d\. Oxf\. H\.?) *([0-9]+)', data1)
    if m is not None:
        return 'https://sanskrit-lexicon-scans.github.io/Oxf_Cat_Aufrecht/index.html?%s' % m.group(2)
    return None


# --- PWG-specific href generators ---

def href_amarakosa(data1: str):
    m = re.match(r'^AK\. *([0-9]+), *([0-9]+), *([0-9]+), *([0-9]+)', data1)
    if m is not None:
        return 'https://sanskrit-lexicon-scans.github.io/amarakosha/app1?%s,%s,%s' % (m.group(1), m.group(2), m.group(3))
    return None


def href_hemacandra(data1: str):
    m = re.match(r'^H\. *([0-9]+)', data1)
    if m is not None:
        return 'https://sanskrit-lexicon-scans.github.io/anekarthasamgraha/app1?%s' % m.group(1)
    return None


def href_anekartha(data1: str):
    m = re.match(r'^an\. *([0-9]+), *([0-9]+)', data1)
    if m is not None:
        return 'https://sanskrit-lexicon-scans.github.io/anekarthasamgraha/app1?%s,%s' % (m.group(1), m.group(2))
    return None


def href_medini(data1: str):
    m = re.match(r'^MED\. *([a-z]), *([0-9]+)', data1)
    if m is not None:
        return 'https://sanskrit-lexicon-scans.github.io/medini/app1?%s,%s' % (m.group(1), m.group(2))
    return None


def href_shakuntala_pwg(data1: str):
    m = re.match(r'^ŚĀK\. *([0-9]+), *([0-9]+), *([0-9]+)', data1)
    if m is not None:
        return 'https://sanskrit-lexicon-scans.github.io/shakuntala/app2?%s,%s,%s' % (m.group(1), m.group(2), m.group(3))
    m = re.match(r'^ŚĀK\. *([0-9]+)', data1)
    if m is not None:
        return 'https://sanskrit-lexicon-scans.github.io/shakuntala/app1?%s' % m.group(1)
    return None


def href_rajatar_pwg(data1: str):
    m = re.match(r'^(RĀJA-TAR\.|RĀJAT\.) *([0-9]+), *([0-9]+)', data1)
    if m is not None:
        taranga = m.group(2)
        shloka = m.group(3)
        if taranga == '7' or taranga == '8':
            return 'https://sanskrit-lexicon-scans.github.io/rajatarcalc/app1?%s,%s' % (taranga, shloka)
        return 'https://sanskrit-lexicon-scans.github.io/rajatar/app1?%s,%s' % (taranga, shloka)
    return None


def href_ragh_pwg(data1: str, pfx: str):
    m = re.match(r'^(RAGH\..*?) *([0-9]+), *([0-9]+)', data1)
    if m is not None:
        sarga = m.group(2)
        shloka = m.group(3)
        if pfx == 'ragh_st' or 'ST.' in data1:
            return 'https://sanskrit-lexicon-scans.github.io/raghuvamsa/app1?%s,%s' % (sarga, shloka)
        return 'https://sanskrit-lexicon-scans.github.io/raghuvamsacalc/app1?%s,%s' % (sarga, shloka)
    return None


def href_markandeya_purana_pwg(data1: str):
    m = re.match(r'^(MĀRK\. P\.) *([0-9]+), *([0-9]+)', data1)
    if m is not None:
        return 'https://sanskrit-lexicon-scans.github.io/markandeyapurana/app1?%s,%s' % (m.group(2), m.group(3))
    return None


def href_bhagavadgita_pwg(data1: str):
    m = re.match(r'^(BHAG\.) *([0-9]+), *([0-9]+)', data1)
    if m is not None:
        return 'https://sanskrit-lexicon-scans.github.io/bhagavadgita/app1?%s,%s' % (m.group(2), m.group(3))
    return None


def href_yajnavalkya(data1: str):
    m = re.match(r'^(YĀJÑ\.) *([0-9]+), *([0-9]+)', data1)
    if m is not None:
        return 'https://sanskrit-lexicon-scans.github.io/yajnavalkya/app1?%s,%s' % (m.group(2), m.group(3))
    return None


def href_aitareya_brahmana(data1: str):
    m = re.match(r'^(AIT\. BR\.) *([0-9]+), *([0-9]+), *([0-9]+)', data1)
    if m is not None:
        return 'https://sanskrit-lexicon-scans.github.io/aitbr_auf/app1?%s,%s,%s' % (m.group(2), m.group(3), m.group(4))
    m = re.match(r'^(AIT\. BR\.) *([0-9]+), *([0-9]+)', data1)
    if m is not None:
        return 'https://sanskrit-lexicon-scans.github.io/aitbr_auf/app1?%s,%s' % (m.group(2), m.group(3))
    return None


# ---------------------------------------------------------------------------
# Conditional-ternary evaluator (LsService._evaluateConditional)
# ---------------------------------------------------------------------------

def _replace_groups_roman(url_tpl: str, match, roman_convert: bool):
    result = url_tpl
    for i in range(1, match.re.groups + 1):
        replacement = match.group(i) or ''
        if roman_convert:
            rv = roman_int(replacement)
            if rv > 0:
                replacement = str(rv)
        result = result.replace('$' + str(i), replacement)
    return result


def _evaluate_conditional(expr: str, match):
    """LsService._evaluateConditional."""
    try:
        outer = re.match(r'^\(([^)]+)\)\s*\?\s*"([^"]+)"\s*:\s*(.+)$', expr)
        if outer is not None:
            outer_condition = outer.group(1)
            url_true = outer.group(2)
            rest = outer.group(3)
            if rest.endswith(')'):
                rest = rest[:-1]

            or_parts = outer_condition.split('||')
            for part in or_parts:
                cond = re.search(r'\$([0-9]+)\s*==\s*"([^"]+)"', part)
                if cond is not None:
                    try:
                        var_num = int(cond.group(1))
                    except ValueError:
                        var_num = None
                    compare_val = cond.group(2)
                    if var_num is not None and var_num <= match.re.groups:
                        actual_val = match.group(var_num)
                        if actual_val == compare_val:
                            return _replace_groups_roman(url_true, match, True)

            if rest.startswith('('):
                nested = _evaluate_conditional(rest, match)
                if nested:
                    return nested

            if '? "' in rest:
                else_m = re.search(r':\s*"([^"]+)"$', rest)
                if else_m is not None:
                    result_url = else_m.group(1)
                    for i in range(1, match.re.groups + 1):
                        result_url = result_url.replace('$' + str(i), match.group(i) or '')
                    return result_url

            plain_else = re.match(r'^"([^"]+)"$', rest.strip())
            if plain_else is not None:
                return _replace_groups_roman(plain_else.group(1), match, True)

        url_m = re.search(r'\(([^)]+)\)\s*\?\s*"([^"]+)"\s*:\s*"([^"]+)"', expr)
        if url_m is not None:
            condition = url_m.group(1)
            url_true = url_m.group(2)
            url_false = url_m.group(3)
            or_parts = condition.split('||')
            for part in or_parts:
                cond = re.search(r'\$([0-9]+)\s*==\s*"([^"]+)"', part)
                if cond is not None:
                    try:
                        var_num = int(cond.group(1))
                    except ValueError:
                        var_num = None
                    compare_val = cond.group(2)
                    if var_num is not None and var_num <= match.re.groups:
                        actual_val = match.group(var_num)
                        if actual_val == compare_val:
                            result_url = url_true
                            for i in range(1, match.re.groups + 1):
                                result_url = result_url.replace('$' + str(i), match.group(i) or '')
                            return result_url
            result_url = url_false
            for i in range(1, match.re.groups + 1):
                result_url = result_url.replace('$' + str(i), match.group(i) or '')
            return result_url
    except Exception:
        pass
    return ''


# ---------------------------------------------------------------------------
# Pattern engine (LsService._generateHrefFromPatterns)
# ---------------------------------------------------------------------------

_SPECIAL_GENERATORS = {
    'rvAvHymnUrl', 'rvAvHymnUrl2', 'ramayanaUrl', 'ramayanaSchUrl',
    'ramayanaBombSchUrl', 'ramayanaBombayUrl', 'bhagSchUrl', 'bhagSchUrl2',
    'bhagApUrl', 'rvAvApUrl', 'paniniApUrl', 'avGraUrl', 'dhatuUrl',
}


def _generate_href_from_patterns(dict_code: str, data1: str):
    patterns = get_patterns_for_dict(dict_code)
    dlow = dict_code.lower()

    for pattern in patterns:
        if pattern.dicts is not None and dlow not in pattern.dicts:
            continue
        try:
            match = re.search(pattern.regex, data1)
            if match is not None:
                url = pattern.url_template

                # Special URL generators reachable from pwg list.
                if url == 'rvAvHymnUrl':
                    key = extract_first_key(data1)
                    kl = (key or '').lower()
                    is_rv = ('rv' in kl) or ('ṛ' in kl) or kl.startswith('ṛ')
                    pfx = 'rv' if is_rv else 'av'
                    return href_rv_av(pfx, data1, dict_code)
                elif url == 'rvAvHymnUrl2':
                    key = extract_first_key(data1)
                    kl = (key or '').lower()
                    is_rv = ('rv' in kl) or ('ṛ' in kl) or kl.startswith('ṛ')
                    pfx = 'rv' if is_rv else 'av'
                    return href_rv_av2(pfx, data1, dict_code)
                elif url == 'ramayanaUrl':
                    return href_ramayana(data1, dict_code)
                elif url == 'ramayanaBombayUrl':
                    return href_ramayana_bombay(data1)
                elif url == 'dhatuUrl':
                    return href_dhatu(data1)
                # (other special generators are non-pwg-reachable)

                # Conditional-ternary detection.
                url_for_check = url  # Dart replaceAll(r'\$', r'$') is a no-op here
                if '(' in url_for_check and '? "' in url_for_check:
                    url = _evaluate_conditional(url, match)
                else:
                    ngroups = match.re.groups
                    for i in range(1, ngroups + 1):
                        replacement = match.group(i) or ''
                        placeholder = '$' + str(i)
                        lc_placeholder = placeholder + '_lc'
                        r20_placeholder = placeholder + '_r20'
                        lowercase = False
                        r20 = False
                        if lc_placeholder in url:
                            lowercase = True
                            url = url.replace(lc_placeholder, placeholder)
                        elif r20_placeholder in url:
                            r20 = True
                            url = url.replace(r20_placeholder, placeholder)
                        if lowercase:
                            replacement = replacement.lower()
                        elif r20:
                            replacement = str(roman_int20(replacement))
                        else:
                            rv = roman_int(replacement)
                            if rv > 0:
                                replacement = str(rv)
                            # else single lowercase letter kept as-is
                        url = url.replace(placeholder, replacement)

                if url:
                    return url
        except Exception:
            pass
    return None


def href_dhatu(data1: str):
    """LsService.hrefDhatu (not reachable from pwg list, kept for parity)."""
    m = re.match(r'^(.*?[.]) *([0-9ivxlcmIVXLCM]+)([ ,]+([0-9]+))?.*', data1, re.IGNORECASE)
    if m is None:
        return None
    section_val = m.group(2)
    try:
        section = int(section_val)
    except ValueError:
        section = roman_int(section_val)
    if section == 0:
        return None
    dir_ = 'https://www.sanskrit-lexicon.uni-koeln.de/scans/csl-westergaard/disp/index.php'
    return '%s?section=%d' % (dir_, section)


# ---------------------------------------------------------------------------
# Main entry (LsService.generateHref, dict='pwg')
# ---------------------------------------------------------------------------

_BORDER = 'a-zA-Z0-9āīūēōṇṭḍṇñṅśṣḥḍhṭh'


def generate_href(dict_code: str, n_attribute, visible: str):
    """Python port of Dart LsService.generateHref(dict, key, nAttribute, data).

    `key` (Dart param) is computed internally from data1 via extract_first_key,
    matching what the Dart caller (processLs) constructs from n_attribute+data.
    """
    dict_code = dict_code.lower()
    data = visible

    if n_attribute is not None and n_attribute != '':
        is_ap = dict_code in ('ap', 'ap90')
        if is_ap or (
            not n_attribute.endswith(' ')
            and not data.startswith(' ')
            and re.search(r'[' + _BORDER + r']$', n_attribute)
            and re.match(r'^[' + _BORDER + r']', data)
        ):
            data1 = '%s %s' % (n_attribute, data)
        else:
            data1 = '%s%s' % (n_attribute, data)
    else:
        data1 = data

    # (gra-braces branch is non-pwg; skipped)

    # First try pattern-driven approach.
    pattern_result = _generate_href_from_patterns(dict_code, data1)
    if pattern_result is not None:
        return pattern_result

    # Fall back to old helper methods.
    key = extract_first_key(data1)
    pfx = get_prefix(dict_code, key) if key is not None else None
    if pfx is None:
        return None

    if pfx in ('rv', 'av'):
        return href_rv_av(pfx, data1, dict_code)
    elif pfx == 'p':
        return href_panini(data1, dict_code)
    elif pfx in ('R', 'ramayana'):
        return href_ramayana(data1, dict_code)
    elif pfx == 'ramayanabom':
        return href_ramayana_bombay(data1)
    elif pfx in ('RG', 'rgorr'):
        return href_ramayana_gorresio(data1)
    elif pfx in ('MBH.', 'MBHC', 'MBHB', 'MBH'):
        return href_mahabharata(data1, pfx)
    elif pfx == 'Pañcat.':
        return href_pancatantra(data1)
    elif pfx == 'Hariv.':
        return href_harivamsa(data1)
    elif pfx in ('BhP.', 'bhagp'):
        return href_bhagavata_purana(data1)
    elif pfx in ('Ragh.', 'raghuvamsacalc'):
        return href_raghuvamsa(data1, pfx)
    elif pfx == 'VS.':
        return href_vajasansamhita(data1)
    elif pfx == 'TS.':
        return href_taittiriya_samhita(data1)
    elif pfx in ('ŚBr.', 'Śat. Br.', 'shatapathabr'):
        return href_satapatha_brahmana(data1)
    elif pfx == 'Megh.':
        return href_meghaduta(data1)
    elif pfx in ('Kum.', 'Kumāras.', 'kumaras'):
        return href_kumarasambhava(data1)
    elif pfx == 'Mālav.':
        return href_malavikagnimitra(data1)
    elif pfx in ('Vikr.', 'vikramor'):
        return href_vikramorvashiya(data1)
    elif pfx == 'Bhag.':
        return href_bhagavadgita(data1)
    elif pfx in ('Mn.', 'M.'):
        return href_manu(data1)
    elif pfx == 'Nir.':
        return href_nirukta(data1)
    elif pfx == 'kathas':
        return href_kathasaritsagara(data1)
    elif pfx == 'spr':
        return href_spruch(data1)
    elif pfx == 'verzoxf':
        return href_verz_oxf(data1)
    elif pfx == 'AK.':
        return href_amarakosa(data1)
    elif pfx == 'h':
        return href_hemacandra(data1)
    elif pfx == 'an':
        return href_anekartha(data1)
    elif pfx == 'med':
        return href_medini(data1)
    elif pfx == 'shakuntala_pwg':
        return href_shakuntala_pwg(data1)
    elif pfx == 'rajatar_pwg':
        return href_rajatar_pwg(data1)
    elif pfx in ('ragh_pwg', 'ragh_st'):
        return href_ragh_pwg(data1, pfx)
    elif pfx == 'markp_pwg':
        return href_markandeya_purana_pwg(data1)
    elif pfx == 'bhag_pwg':
        return href_bhagavadgita_pwg(data1)
    elif pfx == 'yajn_pwg':
        return href_yajnavalkya(data1)
    elif pfx == 'aitbr_pwg':
        return href_aitareya_brahmana(data1)

    return None


def link_type(url):
    """Classify a resolved citation URL by target kind:

      'scan' -> a page-image scan viewer (photographed book pages):
                sanskrit-lexicon-scans.github.io/* and the Cologne
                /scans/csl-westergaard Dhātupāṭha viewer.
      'html' -> a rendered digital-text page:
                sanskrit-lexicon.github.io/{rv,av}links hymn pages and
                external ashtadhyayi.com Pāṇini sūtras.

    Returns None for a falsy/unknown URL."""
    if not url:
        return None
    if 'sanskrit-lexicon-scans.github.io' in url or '/scans/' in url:
        return 'scan'
    if 'sanskrit-lexicon.github.io' in url or 'ashtadhyayi.com' in url:
        return 'html'
    return 'html'


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

    cases = [
        ('VS. ', '4,19'),
        ('RĀJA-TAR. ', '4,520'),
        ('ṚV. ', '10,85,24'),
        ('AV. ', '11,4,26'),
        ('HARIV. ', '14325'),
        ('YĀJÑ. ', '2,278'),
        ('MBH. ', '3,16765'),
        ('P. ', '3,4,41'),
        ('BHĀG. P. ', '3,9,35'),
        ('', 'Spr. 1415'),
        ('', 'garbage xyz'),
    ]
    for n_attr, visible in cases:
        url = generate_href('pwg', n_attr, visible)
        print('%r | %r => %s' % (n_attr, visible, url))
