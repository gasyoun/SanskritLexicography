#!/usr/bin/env python
"""Map a corpus_lexicon attestation (its `work` + `genre`) to a Renou register.

REUSES the canonical genre→register map already in `renou_register._genre_register`
(same PWG genre taxonomy the corpus uses). It only adds: (a) an ASCII work-name override
for the splits the dict map deliberately leaves to source-name rules (Ṛgveda vs Atharvaveda
Saṃhitā, Buddhist kāvya), since corpus `work` slugs are ASCII (`01_rigveda`) not the
diacritic names `NAME_RULES` expects; and (b) a small supplement for genres that appear in
the parallel corpus but not in PWG's dictionary genre (full Upaniṣads, commentary, darśana,
tantra, kāma). Bridges every corpus-attested Russian meaning to an attestation-level Renou
register (vs the headword-level `*.renou.jsonl`). Codes validated against the canonical list.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from renou_register import REGISTERS, _genre_register

# ASCII work-slug substring → register (RV/AV Saṃhitā split + Buddhist kāvya)
WORK_OVERRIDE = (
    ('atharvaveda', 'atharva'),
    ('rigveda', 'rgveda'),
    ('buddhacharita', 'bauddha'),
)
# genres present in the parallel corpus but not in PWG's dictionary genre map
GENRE_SUPPLEMENT = (
    ('Upaniṣad', 'upanisad'),
    ('Saṃhitā', 'rgveda'),       # any non-RV/AV Saṃhitā fallback (RV/AV via WORK_OVERRIDE)
    ('Commentary', 'bhasya'),
    ('Bhāṣya', 'bhasya'),
    ('Darśana', 'karika'),       # philosophical kārikā/sūtra/bhāṣya — coarse
    ('Jyotiṣa', 'karika'),
    ('Haṭha', 'tantra'),
    ('Tantra', 'tantra'),
    ('Āgama', 'tantra'),
    ('Kāma', 'katha'),
    ('kathā', 'katha'),
)


def to_register(genre, work=''):
    w = (work or '').lower()
    for sub, reg in WORK_OVERRIDE:
        if sub in w:
            return reg
    reg = _genre_register(genre)        # canonical dict-genre map (Epic, Kāvya, Dharma, …)
    if reg:
        return reg
    g = genre or ''
    for sub, supp in GENRE_SUPPLEMENT:
        if sub in g:
            return supp
    return 'other'


_emitted = {r for _, r in WORK_OVERRIDE} | {r for _, r in GENRE_SUPPLEMENT}
_bad = _emitted - set(REGISTERS)
assert not _bad, 'non-canonical register codes: %s' % _bad


if __name__ == '__main__':
    import json
    import collections
    sys.stdout.reconfigure(encoding='utf-8')
    LEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'corpus_lexicon.jsonl')
    by = collections.Counter()
    other_genres = collections.Counter()
    for line in open(LEX, encoding='utf-8'):
        r = json.loads(line)
        reg = to_register(r.get('genre'), r.get('work'))
        by[reg] += 1
        if reg == 'other':
            other_genres[r.get('genre')] += 1
    total = sum(by.values())
    print('corpus attestations by Renou register (%d total):' % total)
    for reg, n in by.most_common():
        print('  %-10s %9d  %4.1f%%' % (reg, n, 100 * n / total))
    if other_genres:
        print('\nUNMAPPED genres:', dict(other_genres))
