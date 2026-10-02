"""Pin root_glue_translated.glue stitching (H5707 R7): split-root sub-cards
reassemble into one NESTED article, homonym blocks appear in order, missing
translations become explicit pending placeholders, and body_of drops the
leading '# title' so sub-cards nest cleanly. Zero coverage before.
"""
import json
import os
import sys
import tempfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

import root_glue_translated as RG  # noqa: E402
from safe_filename import safe_name  # noqa: E402


import pytest  # noqa: E402


@pytest.fixture
def tmp_cfg(tmp_path):
    inp = str(tmp_path / 'input')
    out = str(tmp_path / 'output')
    os.makedirs(inp), os.makedirs(out)
    return inp, out


def test_body_of_drops_leading_title():
    body = RG.body_of('# BU — что-то\n\nтело статьи\n')
    assert body.startswith('тело статьи') and '#' not in body


def test_glue_orders_and_nests(tmp_cfg):
    inp, out = tmp_cfg
    rm = {'sub_cards': [
        {'kind': 'head', 'section': 'pwg', 'hom': 0, 'seg_index': 0, 'part': 0,
         'subkey': 'BU_0'},
        {'kind': 'prefixed', 'upasarga': 'pra', 'hom': 0, 'seg_index': 1, 'part': 0,
         'subkey': 'pra_BU', 'section': 'pwg'},
        {'kind': 'supplement', 'section': 'nws.1', 'seg_index': 9, 'subkey': 'BU_nws'},
    ]}
    with open(os.path.join(inp, safe_name('BU') + '.rootmap.json'), 'w',
              encoding='utf-8') as f:
        json.dump(rm, f)
    with open(os.path.join(out, 'BU_0.merged.md'), 'w', encoding='utf-8') as f:
        f.write('# BU\n\nпростой глагол — текст\n')
    with open(os.path.join(out, 'pra_BU.merged.md'), 'w', encoding='utf-8') as f:
        f.write('# pra-BU\n\nприставочный текст\n')
    # BU_nws.merged.md deliberately absent -> pending placeholder

    RG.INP, RG.OUT = inp, out
    nested = RG.glue('BU', out)
    text = open(nested, encoding='utf-8').read()
    assert os.path.basename(nested) == safe_name('BU') + '.NESTED.md'
    assert text.index('Простой глагол') < text.index('приставка pra') < text.index('NWS')
    assert 'простой глагол — текст' in text and 'приставочный текст' in text
    assert '\n# BU\n' not in text                    # sub-card titles dropped
    assert 'ещё не готов' in text                 # the missing sub-card is explicit


def test_glue_homonym_blocks(tmp_cfg):
    inp, out = tmp_cfg
    rm = {'sub_cards': [
        {'kind': 'head', 'section': 'pwg', 'hom': 1, 'seg_index': 0, 'part': 0,
         'subkey': 'As_1'},
        {'kind': 'head', 'section': 'pwg', 'hom': 0, 'seg_index': 5, 'part': 0,
         'subkey': 'As_0'},
    ]}
    with open(os.path.join(inp, safe_name('As') + '.rootmap.json'), 'w',
              encoding='utf-8') as f:
        json.dump(rm, f)
    for sub in ('As_0', 'As_1'):
        with open(os.path.join(out, sub + '.merged.md'), 'w', encoding='utf-8') as f:
            f.write('# %s\n\nтекст\n' % sub)
    RG.INP, RG.OUT = inp, out
    text = open(RG.glue('As', out), encoding='utf-8').read()
    assert 'Омоним 1' in text and 'Омоним 2' in text
    assert text.index('Омоним 1') < text.index('Омоним 2')   # hom 0 sorts first


def test_glue_missing_rootmap_exits_with_pointer(tmp_cfg):
    inp, out = tmp_cfg
    RG.INP, RG.OUT = inp, out
    try:
        RG.glue('ZZZ', out)
        raised = None
    except SystemExit as exc:
        raised = exc
    assert raised is not None and 'rootmap' in str(raised)
