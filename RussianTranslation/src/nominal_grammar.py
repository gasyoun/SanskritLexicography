#!/usr/bin/env python
"""Nominal grammar layer for pwg_ru — stem-class annotation for non-root headwords.

Companion to whitney_grammar.py (verb roots). Provides Whitney §§ and compound
segmentation for nouns, adjectives, compounds, and indeclinables.

Sources:
- Stem class: from the SLP1 final phoneme (the canonical Whitney criterion).
- Whitney §§: from src/whitney_sections.json (chapters IV–V, XVI–XVIII),
  materialized as a static concordance — no live sibling-repo dependency.
- Compound members: from the MW <k2> em-dash segmentation via mw_compounds.py.

  python src/nominal_grammar.py --show agni m.
  python src/nominal_grammar.py --show aMSakaraRa m.

Programmatic:
  from nominal_grammar import nominal_grammar_for
  nominal_grammar_for('agni', 'm.')         # {'stem_class': 'i-stem', ...}
  nominal_grammar_for('aMSakaraRa', 'm.')   # compound with members
"""
import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
# Ensure sibling src/ modules (mw_compounds, etc.) are importable regardless of cwd.
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# ---------------------------------------------------------------------------
# Stem-class → Whitney § concordance (hand-verified against whitney_sections.json)
# Key: stem class label; value: {'declension': str, 'notes': str}
# Whitney Sanskrit Grammar, 2nd ed. (1889), chapters IV–V, XVI–XVIII.
# ---------------------------------------------------------------------------
_STEM_SECTIONS = {
    'a-stem': {
        'declension': '§§326–334',
        'paradigm': '§330',
        'chapter': 'V (Nouns and Adjectives)',
        'notes': 'majority class; masc./neut.; adj. often tri-gender via §368',
    },
    'ā-stem': {
        'declension': '§§362–368',
        'paradigm': '§364',
        'chapter': 'V (Nouns and Adjectives)',
        'notes': 'derivative long-vowel stems; senā f. model',
    },
    'i-stem': {
        'declension': '§§335–345',
        'paradigm': '§339',
        'chapter': 'V (Nouns and Adjectives)',
        'notes': 'short i; agni m., gati f., vāri n.; monosyl. ī see §350',
    },
    'ī-stem': {
        'declension': '§§350–362',
        'paradigm': '§356',
        'chapter': 'V (Nouns and Adjectives)',
        'notes': 'long ī; polysyl.: nadī f. §356; monosyl.: dhī f. §351',
    },
    'u-stem': {
        'declension': '§§335–345',
        'paradigm': '§341',
        'chapter': 'V (Nouns and Adjectives)',
        'notes': 'short u; śatru m., dhenu f., madhu n.; monosyl. ū see §350',
    },
    'ū-stem': {
        'declension': '§§350–362',
        'paradigm': '§351',
        'chapter': 'V (Nouns and Adjectives)',
        'notes': 'long ū; monosyl.: bhū f. §351; polysyl.: tanū f. §356',
    },
    'ṛ-stem': {
        'declension': '§§369–376',
        'paradigm': '§373',
        'chapter': 'V (Nouns and Adjectives)',
        'notes': 'agent-nouns in tṛ/tā; pitṛ m., mātr̥ f.',
    },
    'consonant-stem': {
        'declension': '§§377–474',
        'paradigm': '§391',
        'chapter': 'V (Nouns and Adjectives)',
        'notes': 'vāc f. (c-final §391), manas n. (as-final §414), rājan m. (an-final §421)',
    },
    'indeclinable': {
        'declension': '§§1096–1135',
        'paradigm': None,
        'chapter': 'XVI (Indeclinables)',
        'notes': 'adverbs, particles, prefix-based',
    },
}

# Compound and derivation section references (always appended when applicable)
_COMPOUND_SECTIONS = '§§1246–1316'   # Ch. XVIII Formation of Compound Stems
_DERIV_SECTIONS    = '§§1136–1245'   # Ch. XVII Derivation of Declinable Stems

# ---------------------------------------------------------------------------
# SLP1 phoneme sets
# ---------------------------------------------------------------------------
# Vowel finals → stem class map (SLP1 encoding)
_VOWEL_FINAL = {
    'a': 'a-stem',
    'A': 'ā-stem',
    'i': 'i-stem',
    'I': 'ī-stem',
    'u': 'u-stem',
    'U': 'ū-stem',
    'f': 'ṛ-stem',   # SLP1 'f' = ṛ
    'F': 'ṛ-stem',   # SLP1 'F' = ṝ (treated as ṛ-class)
    'e': 'consonant-stem',  # rare diphthong finals → treat as consonant-class
    'E': 'consonant-stem',
    'o': 'consonant-stem',
    'O': 'consonant-stem',
}

# POS tags that mark indeclinables
_INDECL_POS = {'adv.', 'indecl.', 'ind.', 'interj.'}

# Gender → lex tag normalisation
_LEX_M = {'m.', 'mm.'}
_LEX_F = {'f.', 'fem.', 'femin.', 'ff.'}
_LEX_N = {'n.', 'neutr.'}
_LEX_ADJ = {'adj.', 'm.f.n.', 'm.f.', 'f.n.'}
_LEX_MN = {'m.n.'}


# ---------------------------------------------------------------------------
# vidyut subanta paradigm (display only — lazy import so the core annotation
# path has no hard vidyut dependency). Reuses the WhitneyRoots design: vidyut is
# the morphology engine, rendered SLP1→IAST via vidyut.lipi (no new dependency).
# ---------------------------------------------------------------------------
# lex tag → vidyut Linga (representative gender for the paradigm)
_LEX_LINGA = {
    'm.': 'Pum', 'mm.': 'Pum',
    'f.': 'Stri', 'fem.': 'Stri', 'femin.': 'Stri', 'ff.': 'Stri',
    'n.': 'Napumsaka', 'neutr.': 'Napumsaka',
    'm.n.': 'Pum', 'm.f.': 'Pum', 'f.n.': 'Stri', 'm.f.n.': 'Pum',
    'adj.': 'Pum',                      # adjectives decline in all genders; show masc.
}
# (vibhakti label, vidyut Vibhakti name)
_VIBHAKTI = [
    ('nom', 'Prathama'), ('acc', 'Dvitiya'), ('ins', 'Trtiya'),
    ('dat', 'Caturthi'), ('abl', 'Panchami'), ('gen', 'Sasthi'),
    ('loc', 'Saptami'), ('voc', 'Sambodhana'),
]
_VACANA = [('sg', 'Eka'), ('du', 'Dvi'), ('pl', 'Bahu')]


def paradigm_for(slp1, lex, scheme='iast'):
    """Generate the subanta declension for an SLP1 stem via vidyut-prakriya.

    Returns {vibhakti: {sg, du, pl}} with forms rendered in `scheme` ('iast' or
    'slp1'), or None if the gender is unsupported or vidyut is unavailable. The
    gender is representative (adjectives shown in the masculine).
    """
    linga_name = _LEX_LINGA.get((lex or '').strip())
    if not slp1 or linga_name is None:
        return None
    try:
        from vidyut import prakriya as P
        from vidyut import lipi
    except Exception:
        return None

    def render(forms):
        if scheme == 'slp1':
            return forms
        return [lipi.transliterate(f, lipi.Scheme.Slp1, lipi.Scheme.Iast) for f in forms]

    v = P.Vyakarana()
    linga = getattr(P.Linga, linga_name)
    # Feminine long-vowel stems (ā/ī/ū, the nyāp class) decline via vidyut's
    # nyap pratipadika; basic() wrongly adds a visarga (senā → *senāḥ). All other
    # stems (a/i/u masc-neut, consonant) use basic(). Verified senā/nadī/vadhū.
    if linga_name == 'Stri' and slp1[-1:] in ('A', 'I', 'U'):
        pp = P.Pratipadika.nyap(slp1)
    else:
        pp = P.Pratipadika.basic(slp1)
    table = {}
    for vlabel, vname in _VIBHAKTI:
        cells = {}
        for nlabel, nname in _VACANA:
            pada = P.Pada.Subanta(pp, linga,
                                  getattr(P.Vibhakti, vname), getattr(P.Vacana, nname))
            forms = sorted({x.text for x in v.derive(pada)})
            cells[nlabel] = ' / '.join(render(forms)) if forms else ''
        table[vlabel] = cells
    return {'gender': lex, 'linga': linga_name, 'scheme': scheme, 'cases': table}


def _stem_class(slp1, lex):
    """Detect stem class from SLP1 final phoneme and lex tag."""
    if lex in _INDECL_POS:
        return 'indeclinable'
    if not slp1:
        return 'a-stem'
    final = slp1[-1]
    return _VOWEL_FINAL.get(final, 'consonant-stem')


def _irregularities(slp1, lex, stem_class, compound_members):
    """Derive notable annotation flags (parallel to whitney_grammar.irregularities)."""
    flags = []
    if compound_members:
        n = len(compound_members)
        flags.append('compound:%d_members' % n)
    # Multi-gender nominals (common adjective class)
    if lex in _LEX_ADJ:
        flags.append('tri_gender_adj')
    if lex in _LEX_MN:
        flags.append('m_n_common')
    # Monosyllabic long-vowel stems follow stricter Vedic rules (§§350-362)
    if stem_class in ('ī-stem', 'ū-stem') and slp1 and len(slp1) <= 2:
        flags.append('monosyllabic_long_vowel(§350)')
    # ā-stem feminine — very common but a distinct paradigm
    if stem_class == 'ā-stem' and lex in _LEX_F:
        flags.append('ā_stem_f(§364)')
    return flags


def nominal_grammar_for(slp1, lex, pos=None, paradigm=False):
    """Return the nominal grammar block for an SLP1 headword.

    Args:
        slp1: SLP1-encoded headword key (k1 from PWG).
        lex:  <lex> tag from PWG, e.g. 'm.', 'f.', 'n.', 'adj.', 'adv.', ...
        pos:  optional override POS string (unused, reserved for DCS CoNLL-U input).
        paradigm: if True, attach a vidyut-generated subanta declension table.

    Returns dict with keys:
        slp1, gender, stem_class, declension_sections, paradigm_section,
        compound_members, compound_sections, derivation_sections,
        irregularities, source.
    """
    from mw_compounds import compound_for

    lex = (lex or '').strip()
    stem_class = _stem_class(slp1, lex)
    sec = _STEM_SECTIONS.get(stem_class, _STEM_SECTIONS['consonant-stem'])

    compound_members = compound_for(slp1)
    is_compound = compound_members is not None

    result = {
        'slp1': slp1,
        'gender': lex,
        'stem_class': stem_class,
        'declension_sections': sec['declension'],
        'paradigm_section': sec.get('paradigm'),
        'chapter': sec['chapter'],
        'notes': sec['notes'],
        'compound_members': compound_members,
        'compound_sections': _COMPOUND_SECTIONS if is_compound else None,
        'derivation_sections': _DERIV_SECTIONS,
        'irregularities': _irregularities(slp1, lex, stem_class, compound_members),
        'source': (
            'nominal_grammar.py: Whitney §§ (whitney_sections.json ch. IV–V, XVI–XVIII) '
            '+ MW k2 compound segmentation (csl-orig/mw.txt, read-only)'
        ),
    }
    if paradigm:
        result['paradigm'] = paradigm_for(slp1, lex)
    return result


def selftest():
    """Lock the stem-class detector, compound join, and vidyut paradigm rule."""
    # stem class from SLP1 final
    cases = [
        ('agni', 'm.', 'i-stem'), ('senA', 'f.', 'ā-stem'),
        ('deva', 'm.', 'a-stem'), ('nadI', 'f.', 'ī-stem'),
        ('manas', 'n.', 'consonant-stem'), ('pitf', 'm.', 'ṛ-stem'),
        ('ca', 'adv.', 'indeclinable'),
    ]
    for slp1, lex, want in cases:
        got = nominal_grammar_for(slp1, lex)['stem_class']
        assert got == want, 'stem_class(%s,%s)=%s want %s' % (slp1, lex, got, want)
    # compound join
    rec = nominal_grammar_for('aMSakaraRa', 'm.')
    assert rec['compound_members'] == ['aMSa', 'karaRa'], rec['compound_members']
    # vidyut paradigm — feminine long-vowel must use nyap (senā not *senāḥ)
    p = paradigm_for('senA', 'f.')
    if p is not None:                       # skip if vidyut unavailable
        assert p['cases']['nom']['sg'] == 'senā', p['cases']['nom']
        assert paradigm_for('agni', 'm.')['cases']['nom']['sg'] == 'agniḥ'
        assert paradigm_for('ca', 'adv.') is None
    print('selftest OK')


def main():
    args = sys.argv[1:]
    if '--selftest' in args:
        selftest()
        return
    want_paradigm = '--paradigm' in args
    if '--show' in args:
        idx = args.index('--show')
        rest = [a for a in args[idx + 1:] if not a.startswith('--')]
        if len(rest) < 1:
            print('Usage: --show <SLP1> <lex_tag> [--paradigm]')
            return
        slp1 = rest[0]
        lex = rest[1] if len(rest) > 1 else 'm.'
        rec = nominal_grammar_for(slp1, lex, paradigm=want_paradigm)
        print(json.dumps(rec, ensure_ascii=False, indent=2))
        return
    if '--paradigm' in args:
        idx = args.index('--paradigm')
        rest = [a for a in args[idx + 1:] if not a.startswith('--')]
        if len(rest) < 1:
            print('Usage: --paradigm <SLP1> <lex_tag>')
            return
        slp1 = rest[0]
        lex = rest[1] if len(rest) > 1 else 'm.'
        tab = paradigm_for(slp1, lex)
        if tab is None:
            print('no paradigm (unsupported gender %r or vidyut unavailable)' % lex)
            return
        print(json.dumps(tab, ensure_ascii=False, indent=2))
        return
    print(__doc__)


if __name__ == '__main__':
    main()
