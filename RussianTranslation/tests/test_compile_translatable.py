"""Pin the NWS gloss masking in compile_translatable (H5707 R1/R7).

The owner-cite strip was a first-occurrence `.*$` cut with no re.S (H5707 L1):
a source named mid-gloss destroyed everything after it, and a cite followed by
a newline was not stripped at all. These tests pin the corrected semantics —
cut from the LAST occurrence of the cite to the end — plus the language
detector and the layer splitting that feed the translatable-unit manifest.
"""
import os
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

import compile_translatable as CT


def test_owner_cite_trailing_stripped():
    prose, _keep = CT.mask_nws_gloss(
        'opfernd, darbringend Geldner 1873 (1996) : 1', 'Geldner 1873 (1996) : 1')
    assert 'Geldner' not in prose and 'opfernd' in prose


def test_owner_named_mid_gloss_without_trailing_cite_not_cut():
    # The owner cited as a COMPARISON mid-gloss, never as the trailing
    # attribution: the old first-occurrence cut destroyed everything after the
    # cite; the tail-anchored cut keeps the prose (the cite stays as noise —
    # fail toward no data loss).
    gloss = ('wie Geldner 1873 (1996) : 1 es fasst, bedeutet es Anteil und '
             'Zuweisung an die Götter, soweit die Vedischen Dichter davon sprechen')
    prose, _keep = CT.mask_nws_gloss(gloss, 'Geldner 1873 (1996) : 1')
    assert 'Anteil' in prose and 'Götter' in prose and 'sprechen' in prose


def test_owner_cited_twice_cuts_only_the_trailing_one():
    gloss = ('Vgl. Geldner 1873 (1996) : 1 zu áṃśa; hier als Anteil gefasst '
             'Geldner 1873 (1996) : 1')
    prose, _keep = CT.mask_nws_gloss(gloss, 'Geldner 1873 (1996) : 1')
    # the trailing cite is gone, the prose around the mid-gloss mention survives
    assert 'Anteil gefasst' in prose
    assert '1996' not in prose            # no owner-cite residue anywhere


def test_owner_cite_followed_by_newline_residue_still_stripped():
    # split residue can leave a newline AFTER the cite; without re.S the old
    # pattern could not reach $ and stripped nothing.
    gloss = 'Anteil, Teil\nGeldner 1873 (1996) : 1\n'
    prose, _keep = CT.mask_nws_gloss(gloss, 'Geldner 1873 (1996) : 1')
    assert 'Geldner' not in prose and 'Anteil' in prose


def test_inline_sanskrit_masked_multiline():
    gloss = 'gloss before <is>a\nṃśa</is> and after'
    prose, keep = CT.mask_nws_gloss(gloss, '')
    assert '<is>' not in prose and 'gloss before' in prose and 'and after' in prose
    assert '<is>a\nṃśa</is>' in keep


def test_grammar_and_refs_pulled_to_keep():
    prose, keep = CT.mask_nws_gloss('Subst n das Feuer ; RV 7,2,1', '')
    assert 'Subst' not in prose
    assert any('RV 7,2,1' == k for k in keep)
    assert 'Feuer' in prose


def test_detect_language_priors():
    assert 'de' in CT.detect('der Anteil des Opfernden am Gotte')
    assert 'en' in CT.detect('the meaning of the word')
    assert 'fr' in CT.detect('le sens de la racine')
    # inconclusive text falls back to the owner prior (Renou = fr)
    assert CT.detect('ṛc', owner='Renou 1957 : 12') == ['fr']


def test_layer_blocks_split():
    raw = ('=== LAYER: PWG (v02) ===\nbody one\n=== LAYER: NWS — addendum ===\n'
           'body two\n')
    blocks = CT.layer_blocks(raw)
    assert [r for r, _b in blocks] == ['PWG', 'NWS']
    assert 'body two' in blocks[1][1]
