"""Regression tests for the wave-1 Sa->Ru gloss-layer defect fixes (H1349 / W1.6).

Each test pins one of the three fixed defects via its extracted pure helper, so
the suite runs with NO heavy dependency (no DCS sqlite, no vidyut kosha, no
indic_transliteration) — the three build_*.py modules import cleanly because
those deps are now imported lazily inside main()/to_slp1().

  Fixture A (W1.1) — a prefixed verb lemma with no root suffix is routed to the
                     `unresolved` (pseudo-root) bucket, not the root layer.
  Fixture B (W1.2) — a form with three near-equal lemmas yields >=2 alternates.
  Fixture C (W1.3) — an ambiguous vidyut form produces its full competitor trail.

Run: `pytest tests/test_saru_gloss_pipeline.py` (working dir RussianTranslation).
"""
import collections
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

import build_dcs_maps          # noqa: E402
import build_rollup_glossaries  # noqa: E402
import build_vidyut_fallback    # noqa: E402


# --- Fixture A · W1.1 pseudo-root split -------------------------------------

def test_pseudo_root_excluded_from_root_layer():
    """A prefixed verb lemma whose stem is no known root self-maps -> it must
    land in the unresolved bucket and NOT the resolved (root-layer) rows."""
    # 'praBU' (pra + BU) has a preverb but no member of the root inventory {gam}
    # is a suffix of it -> pseudo-root. 'saMgam' resolves to 'gam'. 'gam' is a
    # simple root (self). Only 'praBU' should be unresolved.
    verb_lemmas = {'praBU': True, 'saMgam': True, 'gam': False}
    roots_by_len = sorted({'gam'}, key=len, reverse=True)

    resolved, unresolved, counts = build_dcs_maps.derive_lemma2root(
        verb_lemmas, roots_by_len)

    resolved_lemmas = {r[0] for r in resolved}
    unresolved_lemmas = {r[0] for r in unresolved}

    assert 'praBU' in unresolved_lemmas          # prefixed, no root suffix
    assert 'praBU' not in resolved_lemmas         # -> kept OUT of the root layer
    assert ('saMgam', 'gam', 'suffix') in resolved   # real derived root, retained
    assert ('gam', 'gam', 'self') in resolved        # simple root, retained
    assert counts['unresolved'] == 1                 # the delta-table exclusion count
    # every unresolved row is a self-map tagged 'unresolved'
    assert all(lemma == root and how == 'unresolved'
               for lemma, root, how in unresolved)


def test_rollup_parse_lemma2root_drops_unresolved_rows():
    """The rollup's map loader must exclude any legacy `unresolved` rows so a
    pseudo-root is never counted as a root even from an un-split file."""
    lines = [
        'lemma_slp1\troot_slp1\thow\n',
        'gam\tgam\tself\n',
        'saMgam\tgam\tsuffix\n',
        'praBU\tpraBU\tunresolved\n',
    ]
    l2r = build_rollup_glossaries.parse_lemma2root(lines)
    assert l2r['gam'] == 'gam'
    assert l2r['saMgam'] == 'gam'
    assert 'praBU' not in l2r                     # pseudo-root excluded from root layer


# --- Fixture B · W1.2 homograph completeness --------------------------------

def test_homograph_emits_all_qualifying_alternates():
    """Three near-equal lemmas for one form -> at least two alternates recorded,
    where the old code only ever inspected the single first runner-up."""
    cands = [
        ('A', 'NOUN', 100, 'dcs'),   # primary
        ('B', 'VERB', 90, 'dcs'),    # qualifies: different upos
        ('C', 'NOUN', 80, 'dcs'),    # qualifies: 80 >= 50% of 100
    ]
    alts = build_rollup_glossaries.homograph_alts(cands)
    assert len(alts) >= 2
    assert {a[0] for a in alts} == {'B', 'C'}


def test_homograph_ignores_minor_same_upos_alternate():
    """A same-upos candidate below the 50% threshold is not an alternate."""
    cands = [('A', 'NOUN', 100, 'dcs'), ('D', 'NOUN', 40, 'dcs')]
    assert build_rollup_glossaries.homograph_alts(cands) == []
    assert build_rollup_glossaries.homograph_alts([('A', 'NOUN', 100, 'dcs')]) == []


# --- Fixture C · W1.3 vidyut ambiguity trail --------------------------------

def test_vidyut_ambiguity_trail_lists_competitors():
    """An ambiguous form (two candidate lemmas) yields a non-empty alts trail,
    primary chosen by most-entries-then-shortest-lemma."""
    lp = collections.Counter({('gam', 'verb'): 3, ('gA', 'verb'): 2})
    lemma, pos, cnt, alts = build_vidyut_fallback.pick_primary_and_alts(lp)
    assert (lemma, pos, cnt) == ('gam', 'verb', 3)
    assert alts == [('gA', 'verb', 2)]


def test_vidyut_primary_tiebreak_prefers_shorter_lemma():
    """Equal entry counts -> the shorter lemma (the root) wins the primary slot."""
    lp = collections.Counter({('gamana', 'noun'): 2, ('gam', 'verb'): 2})
    lemma, pos, cnt, alts = build_vidyut_fallback.pick_primary_and_alts(lp)
    assert lemma == 'gam'                          # shorter wins on a tie
    assert [a[0] for a in alts] == ['gamana']


def test_vidyut_single_candidate_has_no_trail():
    lp = collections.Counter({('BU', 'verb'): 5})
    lemma, pos, cnt, alts = build_vidyut_fallback.pick_primary_and_alts(lp)
    assert (lemma, pos, cnt) == ('BU', 'verb', 5)
    assert alts == []
    assert build_vidyut_fallback.pick_primary_and_alts(collections.Counter()) is None


# --- Fixture D · H2194 krdanta-collapse guard (wave-2 defect class 2) --------
# Tallies below are the REAL kosha-0.4.0 entry counts observed for the panel's
# failing examples (janitf, liNgin) and for rAmeRa, the same collapse on the
# commonest of nouns.

def test_krdanta_collapse_repicks_basic_stem():
    """janitf: 12 krdanta entries say lemma 'jan', 3 Basic entries say 'janitf'.
    With the Basic set the nominal stem must win; the dhatu stays an alternate."""
    lp = collections.Counter({('jan', 'noun'): 12, ('janitf', 'noun'): 3})
    basic = {('janitf', 'noun')}
    lemma, pos, cnt, alts = build_vidyut_fallback.pick_primary_and_alts(lp, basic)
    assert (lemma, pos, cnt) == ('janitf', 'noun', 3)
    assert ('jan', 'noun', 12) in alts            # demoted, not dropped (trail intact)


def test_krdanta_guard_beats_shortest_tiebreak():
    """liNgin: krdanta collapses liNg/liNgi outnumber the Basic stem liNgin;
    the old count-then-shortest pick chose liNg. Basic must now win."""
    lp = collections.Counter(
        {('liNg', 'noun'): 4, ('liNgi', 'noun'): 4, ('liNgin', 'noun'): 2})
    basic = {('liNgin', 'noun')}
    lemma, pos, cnt, alts = build_vidyut_fallback.pick_primary_and_alts(lp, basic)
    assert lemma == 'liNgin'
    assert {a[0] for a in alts} == {'liNg', 'liNgi'}


def test_no_basic_candidate_keeps_old_pick():
    """viDunvAna: every candidate is a krdanta collapse (no Basic entry exists);
    nothing better is available, so the pre-guard pick stands unchanged."""
    lp = collections.Counter({('viDu', 'noun'): 4})
    assert build_vidyut_fallback.pick_primary_and_alts(lp, set()) == \
        build_vidyut_fallback.pick_primary_and_alts(lp)


def test_krdanta_guard_never_demotes_verb_candidates():
    """A genuine Tinanta parse outnumbering a Basic noun still wins by count —
    the guard demotes only krdanta-collapsed NOUN candidates."""
    lp = collections.Counter({('gam', 'verb'): 3, ('gamana', 'noun'): 2})
    basic = {('gamana', 'noun')}
    lemma, pos, cnt, alts = build_vidyut_fallback.pick_primary_and_alts(lp, basic)
    assert (lemma, pos) == ('gam', 'verb')


def test_krdanta_guard_none_is_backward_compatible():
    """basic=None (the legacy call shape) reproduces the pre-H2194 ranking."""
    lp = collections.Counter({('jan', 'noun'): 12, ('janitf', 'noun'): 3})
    lemma, pos, cnt, alts = build_vidyut_fallback.pick_primary_and_alts(lp)
    assert lemma == 'jan'                          # old behavior, deliberately
