#!/usr/bin/env python3
r"""Selftest for the tm-build canonical-source guard.

    python src/pilot/tm_build_guard_selftest.py

26-07-2026 incident: a scratch store was built with out=None; tm_path()
resolved the CANONICAL sidecar and one synthetic entry replaced the
production TM (lane A dry for a month). Guard contract tested here:

    * out=None + non-canonical store  -> TmBuildRefused (fail loud)
    * escape env set                  -> allowed, deliberately
    * explicit out=                   -> always allowed (scratch builds)
    * out=None + canonical store      -> allowed (the coordinator close path)
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.dirname(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import translation_memory as tm  # noqa: E402

_ROW = {
    'key1': 'k', 'iast': 'k', 'layer': None, 'subcard': 'k~~h0_zz_pw',
    'h': '', 'sense_tag': '1', 'de': 'Feuer', 'ru': 'огонь',
    'review_status': 'approved', 'reviewer': 'selftest',
    'equivalence_type': 'equivalent', 'source_type': 'lexicographic',
    'stratum': '', 'differentia': '',
    'provenance': {'input_raw_sha256': 'abc123', 'root': 't',
                   'generator': 'selftest', 'schema_version': 'pwg_ru.workflow_meta.v1'},
}


def _scratch_store(d, name='scratch_store.jsonl'):
    path = os.path.join(d, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(_ROW, ensure_ascii=False) + '\n')
    return path


def _with_env(**kv):
    saved = {k: os.environ.get(k) for k in kv}
    os.environ.update({k: v for k, v in kv.items() if v is not None})
    return lambda: [os.environ.pop(k, None) for k in kv] or [
        os.environ.__setitem__(k, v) for k, v in saved.items() if v is not None]


def main():
    restore = None
    try:
        with tempfile.TemporaryDirectory() as d:
            tm_dir = os.path.join(d, 'tm')
            os.makedirs(tm_dir)
            foreign = _scratch_store(d, 'window_selftest_scratch_store.jsonl')
            restore = _with_env(PWG_RU_TM_DIR=tm_dir)

            # 1. out=None + foreign store -> REFUSED (the 26-07 accident shape)
            try:
                tm.build(foreign, 'ru')
                raise AssertionError('out=None foreign-store build must be refused')
            except tm.TmBuildRefused as exc:
                assert 'non-canonical store' in str(exc), exc

            # 2. explicit out= -> always fine, writes exactly there
            out_path = os.path.join(d, 'tm.scratch.ru.json')
            path, count, _sk = tm.build(foreign, 'ru', out=out_path)
            assert path == out_path and count == 1, (path, count)

            # 3. deliberate escape -> allowed even with out=None
            os.environ['PWG_TM_BUILD_ALLOW_FOREIGN_STORE'] = '1'
            try:
                path, count, _sk = tm.build(foreign, 'ru')
                assert count == 1 and os.path.dirname(
                    os.path.abspath(path)) == os.path.abspath(tm_dir), (path, count)
            finally:
                os.environ.pop('PWG_TM_BUILD_ALLOW_FOREIGN_STORE', None)

            # 4. out=None + CANONICAL store (env-pinned) -> allowed, closes the loop
            canonical_like = _scratch_store(d, 'canonical_store.jsonl')
            os.environ['PWG_RU_STORE'] = canonical_like
            try:
                path, count, _sk = tm.build(canonical_like, 'ru')
                assert count == 1, (path, count)
            finally:
                os.environ.pop('PWG_RU_STORE', None)

            # 5. load_tm round-trips the guarded artifact
            cache = tm.load_tm('ru')
            assert len(cache) == 1, list(cache)
            entry = next(iter(cache.values()))
            assert entry['card']['records'][0]['senses'][0]['russian'] == 'огонь', entry
        print('ALL GREEN: tm_build_guard_selftest')
    finally:
        if restore:
            restore()


if __name__ == '__main__':
    main()
