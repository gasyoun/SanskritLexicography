"""H3876 — regression tests for tier `marker-head`: recovering marker-residual forms
whose rightmost element is itself INFLECTED.

Before H3876 `marker_recover` probed the rightmost element only against the bare-root
and bare-lemma inventories, so `A-brahma-BuvanAt` (head `BuvanAt`, an ablative of
`Buvana`) fell through to the unresolved bucket — 1,389 forms / 2,312 tokens of the
published typology. The new probe runs that head through the same form->lemma map that
resolves whole corpus forms, under two measured guards:

  * DCS form keys only — the vidyut supplement measured 35/42 on compound-internal
    heads against ~99 % for DCS (see the report linked from `marker_recover`);
  * head length >= 3 — every 1-2 char head in the residual resolved to a wrong
    pronoun/particle homograph (`zA` -> `tad`).

The tier is tagged `marker-head`, distinct from `marker`, so the weaker evidence stays
filterable downstream.

Run: `pytest tests/test_h3876_marker_head_recovery.py` (working dir RussianTranslation).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

import build_rollup_glossaries as brg          # noqa: E402


def _maps():
    """A miniature of the real join tables, keyed exactly as load_maps() builds them."""
    f2l = {
        # DCS-attested inflected forms whose lemma is what the head probe must find
        'BuvanAt': [('Buvana', 'NOUN', 12, 'dcs')],
        'gatam': [('gam', 'VERB', 40, 'dcs')],
        'rohase': [('ruh', 'VERB', 3, 'dcs')],
        # a DCS form key that is ALSO a bare lemma -> probe (2) must win, tier `marker`
        'kAla': [('kAla', 'NOUN', 99, 'dcs')],
        # whole joined form known -> probe (1) must win
        'Agam': [('Agam', 'VERB', 7, 'dcs')],
        # vidyut-only head: correct-looking, but out of the head probe's trust boundary
        'vart': [('varDi', 'noun', 1, 'vidyut')],
        # 2-char head: DCS-attested but below the minimum-evidence floor
        'zA': [('tad', 'PRON', 5, 'dcs')],
    }
    l2r = {'gam': 'gam', 'ruh': 'ruh', 'Agam': 'gam'}
    roots_set = set(l2r.values())
    lemmas_set = {lem for cands in f2l.values() for (lem, _, _, _) in cands}
    return f2l, l2r, roots_set, lemmas_set


def _recover(slp1):
    return brg.marker_recover(slp1, *_maps())


# --- the defect this handoff closes -----------------------------------------

def test_inflected_head_is_recovered_as_marker_head():
    """`A-brahma-BuvanAt`: head `BuvanAt` is neither a bare root nor a bare lemma, but
    DCS lemmatizes it. Before H3876 this returned None."""
    assert _recover('A-brahma-BuvanAt') == ('Buvana', 'NOUN', None, 'marker-head')


def test_inflected_verbal_head_carries_its_root():
    """A participial head rolls up to the verb root, so the form reaches Layer 3."""
    assert _recover('Aditya-gatam') == ('gam', 'VERB', 'gam', 'marker-head')
    assert _recover('A-rohase') == ('ruh', 'VERB', 'ruh', 'marker-head')


# --- the guards, each pinned to its measured justification ------------------

def test_vidyut_only_head_is_refused():
    """`anu-vart`: vidyut maps the head to the bogus lemma `varDi`. The head probe
    trusts DCS form keys only, so this stays unresolved rather than resolving wrong."""
    assert _recover('anu-vart') is None


def test_two_char_head_is_refused():
    """`aSva-zA`: `zA` is DCS-attested but resolves to the pronoun `tad`. Heads shorter
    than MIN_HEAD_LEN are below the minimum-evidence floor."""
    assert brg.MIN_HEAD_LEN == 3
    assert _recover('aSva-zA') is None


# --- the pre-existing tiers must be untouched -------------------------------

def test_joined_form_still_wins_and_stays_tier_marker():
    """Probe (1) is unchanged and keeps the original tier tag."""
    assert _recover('A+gam') == ('Agam', 'VERB', 'gam', 'marker')


def test_bare_root_head_still_wins_and_stays_tier_marker():
    """Probe (2a) is unchanged: a head that IS a root never reaches the head probe."""
    assert _recover('sam+gam') == ('gam', 'verb', 'gam', 'marker')


def test_bare_lemma_head_still_wins_and_stays_tier_marker():
    """Probe (2b) beats the head probe even though `kAla` is also a DCS form key —
    otherwise the new tier would silently relabel already-resolved forms."""
    assert _recover('mahA-kAla') == ('kAla', 'noun', None, 'marker')


def test_unmarked_form_is_ignored():
    assert _recover('BuvanAt') is None


def test_unknown_head_stays_unresolved():
    assert _recover('kim-cid-apUrvakam') is None


# --- the caller contract ----------------------------------------------------

def test_return_arity_is_four_so_the_tier_reaches_the_source_column():
    """main() unpacks four values and writes the 4th into surface_resolution.tsv's
    tier column and the per-entry provenance sidecar the site renders."""
    rec = _recover('A-brahma-BuvanAt')
    assert len(rec) == 4
    assert rec[3] in ('marker', 'marker-head')


def test_new_tier_is_registered_with_the_wave2_precision_machinery():
    """A tier absent from TIERS is invisible to the per-tier precision report, so the
    panel would never measure the weakest evidence in the layer."""
    import saru_gloss_aggregate                # noqa: E402
    import saru_gloss_sample                   # noqa: E402

    for mod in (saru_gloss_sample, saru_gloss_aggregate):
        assert 'marker-head' in mod.TIERS, mod.__name__
        assert 'marker' in mod.TIERS, mod.__name__   # not renamed, added alongside
