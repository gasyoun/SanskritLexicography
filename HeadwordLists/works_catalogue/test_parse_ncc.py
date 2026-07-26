"""Regression tests for parse_ncc.py's match_key derivation (H1671 / issue #779).

The bug: `match_key_for` fed the CAPITALISED NCC headword to `su.to_slp1`, which
is case-preserving with no uppercase IAST keys -- so the capital survived into
the SLP1 string and `slp1_simplify` read it as a different phoneme. 60.0% of the
shipped keys were wrong. These tests pin the corrected behaviour, including the
exact letter-confusions the corruption produced, so a regression is caught as a
named failure rather than as a silent recall loss two pipeline stages later.

Run:  python HeadwordLists/works_catalogue/test_parse_ncc.py
  or: python -m pytest HeadwordLists/works_catalogue/test_parse_ncc.py
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_ncc import match_key_for  # noqa: E402


# (headword, expected key, the wrong key the pre-fix code produced)
CASES = [
    ('Rāmāyaṇa',          'ramayana',          'namayana'),      # R read as ṇ
    ('Śivastotra',        'sivastotra',        'śivastotra'),    # Ś not transliterated
    ('Bhāgavata',         'bhagavata',         'bhhagavata'),    # B read as bh
    ('Kalāpatattvārṇava', 'kalapatattvarnava', 'khalapatattvarnava'),  # K read as kh
    ('Yogasūtra',         'yogasutra',         'nogasutra'),     # Y read as ñ
    ('Ekāvalī',           'ekavali',           'aikavali'),      # E read as ai
]


def test_capitalised_headwords_key_correctly():
    for headword, expected, _ in CASES:
        assert match_key_for(headword) == expected, headword


def test_case_folding_is_the_only_difference():
    """An already-lowercase headword must key identically to its capitalised
    form -- the fix is a case-fold, not a second normalization pass."""
    for headword, expected, _ in CASES:
        assert match_key_for(headword.lower()) == expected, headword


def test_old_corrupt_keys_are_gone():
    for headword, _, corrupt in CASES:
        assert match_key_for(headword) != corrupt, headword


def test_keys_are_ascii():
    """No key may carry a non-ASCII character: 20,571 shipped keys did, and no
    ACC key (genuine lowercase SLP1) can ever match one."""
    for headword, _, _ in CASES:
        key = match_key_for(headword)
        assert key.isascii(), (headword, key)


def test_nfc_and_nfd_agree():
    """A decomposed headword (a + U+0304) must key like its precomposed twin."""
    import unicodedata
    for headword, expected, _ in CASES:
        nfd = unicodedata.normalize('NFD', headword)
        assert match_key_for(nfd) == expected, (headword, nfd)


def test_parenthetical_and_underscore_stripping_still_applies():
    """The P0 normalization the fix sits in front of must be unaffected."""
    assert match_key_for('Aṃśanāḍīphala(keralīya)') == match_key_for('Aṃśanāḍīphala')
    assert match_key_for('Aṃśādīni_Induphalāni') == match_key_for('AṃśādīniInduphalāni')


if __name__ == '__main__':
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith('test_') and callable(fn):
            try:
                fn()
                print(f'PASS {name}')
            except AssertionError as e:
                failures += 1
                print(f'FAIL {name}: {e}')
    print(f'\n{failures} failure(s)')
    sys.exit(1 if failures else 0)
