#!/usr/bin/env python
r"""h4530_window_id_collision_selftest.py — the `headless window id already exists` stall
cannot come back, whatever prefix a regenerated launcher uses.

H4342 stall cause 4 / H4530. Three `h4213can` launch attempts (06–07-09-2026) died on
`FAIL: headless window id already exists: h4213can02`. The launcher's static
`--prefix h4213can` was blamed and a per-run timestamp stamped into the prefix — a real
fix for that one file, but a *gitignored* one: `output/h4213_wave_launch.ps1` is not in
git, so any regenerated or hand-rewritten launcher reintroduces the collision.

The defect is one level down. `plan_window` decides a headless root exists by
`<coord_dir>/artifacts/<root>/execution_manifest.<root>.json`, while
`used_window_indices` only ever scanned `run_pilot_wf.<root>.js` in `src/pilot` and
`wf_output.<root>.json` in `src/pilot/output`. A run that prepared a window and then died
(partial cleanup, an in-flight lock, an auto-restarted retry) leaves the artifacts
directory with neither of those two files — invisible to the index picker, fatal to the
existence guard. Every retry re-picked the same index and failed identically.

Test 1 pins the regression directly: with `h4213can02` sitting in `artifacts/`, auto-index
must skip to 3. Test 2 proves the launcher-level property the handoff asks for — two
consecutive re-arms with a STATIC prefix and no manual id bump produce two different roots.
Test 3 keeps the H809 collision refusal honest against the same id space. Test 4 pins the
bound on the index run, so a timestamp-prefixed leftover cannot be misread as a giant
index. Test 5 pins the pre-existing disk scans (H809 W3) so this change cannot quietly
narrow them.

  python src/pilot/h4530_window_id_collision_selftest.py
"""
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import no_pwg_scale_plan as plan  # noqa: E402


def _mk(*parts):
    path = os.path.join(*parts)
    os.makedirs(path, exist_ok=True)
    return path


def _prepared_root(coord_dir, root):
    """The on-disk shape `plan_window` refuses to re-use: artifacts/<root>/manifest."""
    base = _mk(coord_dir, 'artifacts', root)
    with open(os.path.join(base, 'execution_manifest.%s.json' % root), 'w',
              encoding='utf-8') as f:
        f.write('{}')
    return base


def test_prepared_headless_root_is_counted(td):
    here, out, coord = _mk(td, 'pilot'), _mk(td, 'out'), _mk(td, 'coordinator')
    _prepared_root(coord, 'h4213can02')

    blind = plan.next_free_index('h4213can', here=here, out=out)
    assert blind == 2, 'precondition: without the coordinator dir the picker is blind (%r)' % blind

    got = plan.next_free_index('h4213can', here=here, out=out, coord_dir=coord)
    assert got == 3, ('a prepared-but-unfinished headless root must consume its index, '
                      'else every retry re-picks it and dies on the existence guard: %r' % got)
    assert plan.used_window_indices('h4213can', here, out, coord_dir=coord) == {2}


def test_two_rearms_with_a_static_prefix_do_not_collide(td):
    """The handoff's acceptance property, at the layer that survives a regenerated launcher."""
    here, out, coord = _mk(td, 'pilot'), _mk(td, 'out'), _mk(td, 'coordinator')
    roots = []
    for _attempt in range(2):
        idx = plan.next_free_index('h4213can', here=here, out=out, coord_dir=coord)
        root = 'h4213can%02d' % idx
        assert root not in roots, 're-arm %d re-picked %s' % (_attempt + 1, root)
        _prepared_root(coord, root)          # the attempt prepares, then dies
        roots.append(root)
    assert roots == ['h4213can02', 'h4213can03'], roots


def test_explicit_start_index_collision_still_refused(td):
    here, out, coord = _mk(td, 'pilot'), _mk(td, 'out'), _mk(td, 'coordinator')
    _prepared_root(coord, 'no_pwg_w07')
    used = plan.used_window_indices('no_pwg_w', here, out, coord_dir=coord)
    assert used == {7}, used
    assert 7 in used, 'an explicit --start-index 7 must now be refusable (H809 W3 path)'


def test_timestamped_leftover_does_not_hijack_the_index(td):
    """A `h4213can<stamp>NN` leftover must not read as a giant index under the bare prefix."""
    here, out, coord = _mk(td, 'pilot'), _mk(td, 'out'), _mk(td, 'coordinator')
    _prepared_root(coord, 'h4213can091023345702')     # the 10-09 launcher's own leftover
    assert plan.used_window_indices('h4213can', here, out, coord_dir=coord) == set()
    assert plan.next_free_index('h4213can', here=here, out=out, coord_dir=coord) == 2
    # under the prefix that actually produced it, the index is read normally
    assert plan.used_window_indices('h4213can0910233457', here, out, coord_dir=coord) == {2}


def test_legacy_disk_scans_unchanged(td):
    """H809 W3's two scans keep working, with and without a coordinator dir."""
    here, out = _mk(td, 'pilot'), _mk(td, 'out')
    open(os.path.join(here, 'run_pilot_wf.no_pwg_w06_rq1.js'), 'w').close()
    open(os.path.join(out, 'wf_output.no_pwg_w09.json'), 'w').close()
    assert plan.used_window_indices('no_pwg_w', here, out) == {6, 9}
    assert plan.next_free_index('no_pwg_w', here=here, out=out) == 10
    # an unrelated prefix must not be captured by either scan
    assert plan.used_window_indices('h4213can', here, out) == set()


def main():
    tests = [
        test_prepared_headless_root_is_counted,
        test_two_rearms_with_a_static_prefix_do_not_collide,
        test_explicit_start_index_collision_still_refused,
        test_timestamped_leftover_does_not_hijack_the_index,
        test_legacy_disk_scans_unchanged,
    ]
    for test in tests:
        with tempfile.TemporaryDirectory() as td:
            test(td)
        print('  PASS %s' % test.__name__)
    print('h4530 window-id collision selftest: PASS (%d checks — prepared headless roots '
          'consume their index, two static-prefix re-arms cannot collide, H809 refusal and '
          'the legacy disk scans intact)' % len(tests))
    return 0


if __name__ == '__main__':
    sys.exit(main())
