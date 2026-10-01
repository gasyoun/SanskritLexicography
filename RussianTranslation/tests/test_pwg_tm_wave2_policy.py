"""H2721 — Wave-2 defaults from H2686 (denylist, class TM, next queue)."""
import os
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

import pwg_tm_generate as Gen  # noqa: E402
import pwg_tm_priority as P  # noqa: E402
import pwg_tm_wave2_policy as W2  # noqa: E402


def test_policy_selftest():
    assert W2.selftest() == 0


def test_source_lexicon_skips_denied_short_gloss(tmp_path):
    pub = tmp_path / 'empty.jsonl'
    pub.write_text('', encoding='utf-8')
    extra = tmp_path / 'lex.jsonl'
    extra.write_text(
        '\n'.join([
            '{"fragment_class":"definition_gloss","source_string":"{%Jmd%}","target_string":"{%поручать кому-л.%}"}',
            '{"fragment_class":"definition_gloss","source_string":"{%Feuer.%}","target_string":"{%огонь.%}"}',
        ]) + '\n',
        encoding='utf-8')
    lex = Gen.build_source_lexicon(str(pub), [str(extra)])
    assert Gen.source_lexicon_key('definition_gloss', '{%Jmd%}') not in lex
    assert lex[Gen.source_lexicon_key('definition_gloss', '{%Feuer.%}')] == '{%огонь.%}'


def test_apply_targets_does_not_reuse_jmd():
    """H3299: a poisoned lexicon entry for {%Jmd%} must never leak the verb
    phrase — since the placeholder-fill fix the fragment renders as
    placeholder-style RU (deterministic rule shadows the lexicon), it does
    not stay unfilled any more."""
    frags = [{
        'fragment_id': 'g1',
        'fragment_class': 'definition_gloss',
        'source_string': '{%Jmd%}',
        'reuse_key': 'x',
    }]
    lexicon = {Gen.source_lexicon_key('definition_gloss', '{%Jmd%}'): '{%поручать кому-л.%}'}
    filled, stats = Gen.apply_targets(frags, {}, {}, lexicon)
    assert filled[0].get('target_string') == '{%кто-л.%}'
    assert (filled[0].get('generation') or {}).get('origin') == 'placeholder'
    assert '{%поручать' not in str(filled[0].get('target_string'))
    assert stats['source_reuse'] == 0


def test_priority_skips_wave1_keys():
    scored = [
        {'k1': 'aaa', 'score': 1.0, 'attested': True, 'count_all': 10,
         'core_membership': False, 'complex': False},
        {'k1': 'bbb', 'score': 0.9, 'attested': True, 'count_all': 9,
         'core_membership': False, 'complex': False},
        {'k1': 'ccc', 'score': 0.8, 'attested': True, 'count_all': 8,
         'core_membership': False, 'complex': False},
    ]
    chosen, excluded = P.select(scored, 2, exclude_keys={'aaa'})
    keys = [r['k1'] for r in chosen]
    assert 'aaa' not in keys
    assert keys == ['bbb', 'ccc']
    assert any(r['k1'] == 'aaa' and r['reason'] == 'wave1_immutable' for r in excluded)
