#!/usr/bin/env python
"""Build ls_source_map.json — PWG <ls> source → corpus stratum.

For each PWG sense, its <ls> citation names the work PWG quotes. This map links
the high-frequency sources to (a) the genre/period stratum and (b) the corpus
texts that actually carry a Russian translation, so a sense cited from the
Ṛgveda harvests *Vedic* Russian from the corpus lexicon, an MBh sense *Epic*
Russian, etc. Sources with no verse-corpus translation are stratum-tagged but
harvestable=false (they fall back to the dict signals).

CANON below is curated (top sources by citation count); corpus_works are
auto-linked from corpus_strata.json by prefix. Reports citation coverage.

  python build_ls_map.py
"""
import json, os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PWG = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02', 'pwg', 'pwg.txt'))
STRATA = json.load(open(os.path.join(HERE, 'corpus_strata.json'), encoding='utf-8'))
OUT = os.path.join(HERE, 'ls_source_map.json')

LS = re.compile(r'<ls\b([^>]*)>(.*?)</ls>', re.S)
NATTR = re.compile(r'\bn\s*=\s*"([^"]*)"')


def source_key(attr, inner):
    m = NATTR.search(attr)
    raw = m.group(1) if (m and m.group(1).strip()) else re.sub(r'<[^>]+>', '', inner)
    out = []
    for t in raw.strip().split():
        if any(ch.isdigit() for ch in t):
            break
        out.append(t)
        if len(out) >= 4:
            break
    return re.sub(r'\s+', ' ', ' '.join(out)).strip().rstrip('.').strip()


# curated source → {name, corpus prefix (links to strata works), or explicit genre/period/date}
# corpus_prefix present → harvestable from the verse corpus; else dict-only stratum tag.
#
# 'renou' = Louis Renou's language-state of Sanskrit (Histoire de la langue
# sanskrite, the 5 chapters), the diachronic "which era of Sanskrit" axis:
#   I   Vedic       — Saṃhitā, Brāhmaṇa, Upaniṣad, Sūtra, Vedāṅga
#   II  Pāṇinian    — the classical norm & grammarians' Sanskrit (Pāṇini, Patañjali)
#   III Epic        — Mbh, Rām, Harivaṃśa, Bhagavadgītā, Purāṇa, Smṛti, Tantra (+ prolongements)
#   IV  Classical   — kāvya, drama, kathā, classical śāstra (āyurveda/jyotiṣa/poetics), kośa, later grammar
#   V   Buddhist/Jaina — Buddhist Hybrid & Jaina Sanskrit
# Every CANON entry MUST carry a 'renou' value (asserted in main()).
CANON = {
    # ---- corpus-backed (verse translations exist in SamudraManthanam) ----
    'ṚV':          {'name': 'Ṛgveda', 'corpus_prefix': 'rigveda', 'renou': 'I'},
    'AV':          {'name': 'Atharvaveda', 'corpus_prefix': 'atharvaveda', 'renou': 'I'},
    'MBH':         {'name': 'Mahābhārata', 'corpus_prefix': 'mahabharata', 'renou': 'III'},
    'R':           {'name': 'Rāmāyaṇa', 'corpus_prefix': 'ramayana', 'renou': 'III'},
    'R. GORR':     {'name': 'Rāmāyaṇa (Gorresio rec.)', 'corpus_prefix': 'ramayana', 'renou': 'III'},
    'R. SCHL':     {'name': 'Rāmāyaṇa (Schlegel rec.)', 'corpus_prefix': 'ramayana', 'renou': 'III'},
    'M':           {'name': 'Manusmṛti', 'corpus_prefix': 'manavadharmashastra', 'renou': 'III'},
    'RAGH':        {'name': 'Raghuvaṃśa', 'corpus_prefix': 'raghuvamsha', 'renou': 'IV'},
    'KUMĀRAS':     {'name': 'Kumārasambhava', 'corpus_prefix': 'kumarasambhava', 'renou': 'IV'},
    'MEGH':        {'name': 'Meghadūta', 'corpus_prefix': 'megha-duta', 'renou': 'IV'},
    'VP':          {'name': 'Viṣṇu-Purāṇa', 'corpus_prefix': 'vishnu-purana', 'renou': 'III'},
    'BHAG':        {'name': 'Bhagavadgītā', 'corpus_prefix': 'bhagavadgita', 'renou': 'III'},
    'GĪT':         {'name': 'Bhagavadgītā', 'corpus_prefix': 'bhagavadgita', 'renou': 'III'},
    'AMAR':        {'name': 'Amaru-śataka', 'corpus_prefix': 'amaru-shataka', 'renou': 'IV'},
    'GĪT. GOV':    {'name': 'Gītagovinda', 'corpus_prefix': 'gitagovinda', 'renou': 'IV'},
    # ---- Veda (Brāhmaṇa/Saṃhitā/Sūtra) — not in the verse corpus ----
    'ŚAT. BR':     {'name': 'Śatapatha-Brāhmaṇa', 'genre': 'Veda — Brāhmaṇa', 'period': 'Vedic (Brāhmaṇa–Upaniṣad)', 'date': -800, 'renou': 'I'},
    'AIT. BR':     {'name': 'Aitareya-Brāhmaṇa', 'genre': 'Veda — Brāhmaṇa', 'period': 'Vedic (Brāhmaṇa–Upaniṣad)', 'date': -700, 'renou': 'I'},
    'TS':          {'name': 'Taittirīya-Saṃhitā', 'genre': 'Veda — Saṃhitā', 'period': 'Vedic (Brāhmaṇa–Upaniṣad)', 'date': -1000, 'renou': 'I'},
    'VS':          {'name': 'Vājasaneyi-Saṃhitā', 'genre': 'Veda — Saṃhitā', 'period': 'Vedic (Brāhmaṇa–Upaniṣad)', 'date': -900, 'renou': 'I'},
    'KĀTY. ŚR':    {'name': 'Kātyāyana-Śrautasūtra', 'genre': 'Veda — Sūtra', 'period': 'Vedic (Brāhmaṇa–Upaniṣad)', 'date': -400, 'renou': 'I'},
    'NIR':         {'name': 'Nirukta', 'genre': 'Veda — Vedāṅga', 'period': 'Vedic (Brāhmaṇa–Upaniṣad)', 'date': -500, 'renou': 'I'},
    'P':           {'name': 'Pāṇini, Aṣṭādhyāyī', 'genre': 'Śāstra — Vyākaraṇa', 'period': 'Vedic (Brāhmaṇa–Upaniṣad)', 'date': -400, 'renou': 'II'},
    # ---- Epic-adjacent / Purāṇa — no corpus translation ----
    'HARIV':       {'name': 'Harivaṃśa', 'genre': 'Epic — appendix (MBh)', 'period': 'Epic / early-Classical', 'date': 200, 'renou': 'III'},
    'BHĀG. P':     {'name': 'Bhāgavata-Purāṇa', 'genre': 'Purāṇa', 'period': 'Classical', 'date': 950, 'renou': 'III'},
    'MĀRK. P':     {'name': 'Mārkaṇḍeya-Purāṇa', 'genre': 'Purāṇa', 'period': 'Classical', 'date': 550, 'renou': 'III'},
    # ---- Kāvya / kathā — no corpus translation ----
    'ŚĀK':         {'name': 'Abhijñānaśākuntala', 'genre': 'Kāvya — drama (Kālidāsa)', 'period': 'Classical', 'date': 420, 'renou': 'IV'},
    'KATHĀS':      {'name': 'Kathāsaritsāgara', 'genre': 'Kāvya — kathā', 'period': 'Medieval', 'date': 1050, 'renou': 'IV'},
    'PAÑCAT':      {'name': 'Pañcatantra', 'genre': 'Kāvya — kathā', 'period': 'Classical', 'date': 300, 'renou': 'IV'},
    'HIT':         {'name': 'Hitopadeśa', 'genre': 'Kāvya — kathā', 'period': 'Medieval', 'date': 1000, 'renou': 'IV'},
    'RĀJA-TAR':    {'name': 'Rājataraṅgiṇī', 'genre': 'Kāvya — historical', 'period': 'Medieval', 'date': 1150, 'renou': 'IV'},
    'SĀH. D':      {'name': 'Sāhityadarpaṇa', 'genre': 'Śāstra — poetics', 'period': 'Medieval', 'date': 1400, 'renou': 'IV'},
    'Spr':         {'name': 'Indische Sprüche (gnomic anthology)', 'genre': 'Kāvya — gnomic (mixed)', 'period': 'Classical', 'date': 600, 'renou': 'IV'},
    # ---- Śāstra: āyurveda / dharma / jyotiṣa ----
    'SUŚR':        {'name': 'Suśruta-Saṃhitā', 'genre': 'Śāstra — Āyurveda', 'period': 'Classical', 'date': 400, 'renou': 'IV'},
    'YĀJÑ':        {'name': 'Yājñavalkya-Smṛti', 'genre': 'Śāstra — Dharma', 'period': 'Classical', 'date': 300, 'renou': 'III'},
    'VARĀH. BṚH. S': {'name': 'Varāhamihira, Bṛhatsaṃhitā', 'genre': 'Śāstra — Jyotiṣa', 'period': 'Classical', 'date': 550, 'renou': 'IV'},
    'VARĀH':       {'name': 'Varāhamihira', 'genre': 'Śāstra — Jyotiṣa', 'period': 'Classical', 'date': 550, 'renou': 'IV'},
    # ---- lexica / grammar (kośa, nighaṇṭu) — Sanskrit-side, no Russian verse ----
    'AK':          {'name': 'Amarakośa', 'genre': 'Kośa (lexicon)', 'period': 'Classical', 'date': 450, 'renou': 'IV'},
    'TRIK':        {'name': 'Trikāṇḍaśeṣa', 'genre': 'Kośa (lexicon)', 'period': 'Medieval', 'date': 1150, 'renou': 'IV'},
    'MED':         {'name': 'Medinīkośa', 'genre': 'Kośa (lexicon)', 'period': 'Medieval', 'date': 1200, 'renou': 'IV'},
    'H':           {'name': 'Hemacandra, Abhidhānacintāmaṇi', 'genre': 'Kośa (lexicon)', 'period': 'Medieval', 'date': 1150, 'renou': 'IV'},
    'H. an':       {'name': 'Hemacandra, Anekārthasaṃgraha', 'genre': 'Kośa (lexicon)', 'period': 'Medieval', 'date': 1150, 'renou': 'IV'},
    'HALĀY':       {'name': 'Halāyudha, Abhidhānaratnamālā', 'genre': 'Kośa (lexicon)', 'period': 'Medieval', 'date': 950, 'renou': 'IV'},
    'RĀJAN':       {'name': 'Rājanighaṇṭu', 'genre': 'Kośa (nighaṇṭu)', 'period': 'Medieval', 'date': 1300, 'renou': 'IV'},
    'VOP':         {'name': 'Vopadeva, Mugdhabodha', 'genre': 'Śāstra — Vyākaraṇa', 'period': 'Medieval', 'date': 1250, 'renou': 'II'},
    'ŚKDR':        {'name': 'Śabdakalpadruma (= SKD)', 'genre': 'Kośa (modern compilation)', 'period': 'Medieval', 'date': 1830, 'renou': 'IV'},
}


def link_corpus(prefix):
    return sorted(w for w in STRATA if prefix in w)


def main():
    data = open(PWG, encoding='utf-8').read()
    freq = collections.Counter()
    for m in LS.finditer(data):
        k = source_key(m.group(1), m.group(2))
        if k:
            freq[k] += 1
    total = sum(freq.values())

    out = {}
    cov_corpus = cov_tag = 0
    for key, meta in CANON.items():
        assert meta.get('renou') in ('I', 'II', 'III', 'IV', 'V'), \
            'CANON[%r] missing a valid renou state (I–V)' % key
        n = freq.get(key, 0)
        rec = {'name': meta['name'], 'citations': n, 'renou': meta['renou']}
        if 'corpus_prefix' in meta:
            works = link_corpus(meta['corpus_prefix'])
            rec['corpus_works'] = works
            rec['harvestable'] = bool(works)
            if works:
                st = STRATA[works[0]]
                rec['genre'] = st['genre']; rec['period'] = st['period']; rec['date'] = st['date_median']
                cov_corpus += n
            else:
                rec['harvestable'] = False
        else:
            rec.update({'genre': meta['genre'], 'period': meta['period'],
                        'date': meta['date'], 'corpus_works': [], 'harvestable': False})
            cov_tag += n
        out[key] = rec

    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    mapped = sum(r['citations'] for r in out.values())
    print('PWG <ls>: %d citations, %d distinct keys' % (total, len(freq)))
    print('mapped sources: %d  (%.1f%% of all citations)' % (len(out), 100.0 * mapped / total))
    print('  corpus-harvestable citations: %d (%.1f%%)' % (cov_corpus, 100.0 * cov_corpus / total))
    print('  stratum-tagged only (dict harvest): %d (%.1f%%)' % (cov_tag, 100.0 * cov_tag / total))
    print('corpus-backed sources:')
    for k, r in sorted(out.items(), key=lambda x: -x[1]['citations']):
        if r.get('harvestable'):
            print('  %-12s %7d → %-22s %d works' % (k, r['citations'], r['genre'], len(r['corpus_works'])))
    # Renou language-state (I–V) breakdown: sources and citations per state.
    RENOU_NAME = {'I': 'Vedic', 'II': 'Pāṇinian', 'III': 'Epic',
                  'IV': 'Classical', 'V': 'Buddhist/Jaina'}
    by_state_src = collections.Counter(r['renou'] for r in out.values())
    by_state_cit = collections.Counter()
    for r in out.values():
        by_state_cit[r['renou']] += r['citations']
    print('Renou language-state (I–V) — mapped sources / citations:')
    for st in ('I', 'II', 'III', 'IV', 'V'):
        print('  %-3s %-15s %3d sources · %7d citations'
              % (st, RENOU_NAME[st], by_state_src.get(st, 0), by_state_cit.get(st, 0)))
    print('→ %s' % os.path.basename(OUT))


if __name__ == '__main__':
    main()
