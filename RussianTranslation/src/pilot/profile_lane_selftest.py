#!/usr/bin/env python3
r"""Selftest for profile_lane (the one-knob .env profile resolver).

    python src/pilot/profile_lane_selftest.py

Covers the resolution ladder (env > legacy alias > .env files), the .env parser
edge cases, and the roster rotation contract. Pure-offline: tmp files only.
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.dirname(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import profile_lane as pl  # noqa: E402


def _env_file(tmp, text, name='.env'):
    path = os.path.join(tmp, name)
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)
    return path


def test_parser():
    with tempfile.TemporaryDirectory() as tmp:
        p = _env_file(tmp, (
            '# comment\n'
            '\n'
            'export PWG_PROFILE_SLOT=c1\n'
            "PWG_Q='quoted # not comment'\n"
            'PWG_D="dq"\n'
            'PLAIN=val # trailing\n'
            'EMPTY=\r\n'
            'NO_EQUALS_LINE\n'
            '=nokey\n'
        ))
        data = pl.load_env_file(p)
        assert data['PWG_PROFILE_SLOT'] == 'c1', data
        assert data['PWG_Q'] == 'quoted # not comment', data
        assert data['PWG_D'] == 'dq', data
        assert data['PLAIN'] == 'val', data
        assert data.get('EMPTY') == '', data
        assert 'NO_EQUALS_LINE' not in data and '' not in data, data
        assert pl.load_env_file(os.path.join(tmp, 'missing.env')) == {}
    print('ok  parser')


def test_candidate_order():
    with tempfile.TemporaryDirectory() as tmp:
        a = _env_file(tmp, 'PWG_PROFILE_SLOT=a\n', name='a.env')
        b = _env_file(tmp, 'PWG_PROFILE_SLOT=b\n', name='b.env')
        env = {pl.ENV_FILE_OVERRIDE_KEY: a}
        cands = pl.candidate_env_files(env)
        assert cands[0] == a and cands.count(a) == 1, cands
        # explicit file wins over repo defaults even when they define a slot
        assert pl.active_profile(env) == 'a'
        assert pl.active_profile({pl.ENV_FILE_OVERRIDE_KEY: b}) == 'b'
    print('ok  candidate order')


def test_ladder():
    assert pl.active_profile({'PWG_PROFILE_SLOT': 'c1'}) == 'c1'
    assert pl.active_profile({'PWG_PROFILE_SLOT': '  c2  '}) == 'c2'
    # legacy alias used only when the primary key is absent
    assert pl.active_profile({'PWG_PROFILE': 'c3'}) == 'c3'
    assert pl.active_profile({'PWG_PROFILE_SLOT': '', 'PWG_PROFILE': 'c4'}) == 'c4'
    assert pl.active_profile({}) is None
    with tempfile.TemporaryDirectory() as tmp:
        f = _env_file(tmp, 'PWG_PROFILE=c9\n')
        assert pl.active_profile({pl.ENV_FILE_OVERRIDE_KEY: f}) == 'c9'
        # real environment beats any file
        assert pl.active_profile({'PWG_PROFILE_SLOT': 'cX',
                                  pl.ENV_FILE_OVERRIDE_KEY: f}) == 'cX'
    print('ok  resolution ladder')


def test_roster():
    defaults = ('c4', 'c1', 'c5', 'c6')
    # explicit roster wins outright
    got = pl.active_roster({'PWG_PROFILE_ROSTER': 'c6,c4'}, default_roster=defaults)
    assert got == ['c6', 'c4'], got
    # active slot rotates to the front, relative order preserved
    got = pl.active_roster({'PWG_PROFILE_SLOT': 'c1'}, default_roster=defaults)
    assert got == ['c1', 'c4', 'c5', 'c6'], got
    # nothing set ⇒ caller keeps its own default untouched
    assert pl.active_roster({}, default_roster=defaults) is None
    # slot outside the roster does NOT rotate (explicit config governs)
    assert pl.active_roster({'PWG_PROFILE_SLOT': 'zz'}, default_roster=defaults) is None
    # roster via .env file
    with tempfile.TemporaryDirectory() as tmp:
        f = _env_file(tmp, 'PWG_PROFILE_ROSTER=c5, c1 ,\n')
        got = pl.active_roster({pl.ENV_FILE_OVERRIDE_KEY: f}, default_roster=defaults)
        assert got == ['c5', 'c1'], got
    print('ok  roster')


def main():
    test_parser()
    test_candidate_order()
    test_ladder()
    test_roster()
    # documented fallback stays pinned until a human changes it on purpose
    assert pl.DEFAULT_FALLBACK_SLOT == 'c4'
    print('ALL GREEN: profile_lane_selftest')


if __name__ == '__main__':
    main()
