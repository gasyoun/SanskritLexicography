"""Build an executable manifest v2 + synthetic preflight for the curated canary fixture.

H2174. Closes the gap [H2044](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2044-Opus_SanskritLexicography_g46-pwg-live-health-reprobe_31.07.26.md)
recorded as terminal ``HEALTH_GO_CANARY_UNSPENT``: the curated fixture existed but
"the manifest itself does not, and neither does anything that builds it", so firing
the canary meant hand-authoring a v2 manifest on the money contour -- the improvisation
the live-gate guardrail forbids. Every canary manifest before this was one-session
folklore rebuilt by hand.

It composes two things that already exist -- ``gen_opt_harness2.py`` (the manifest
generator, pointed at the fixture dir via ``PWG_INPUT_DIR``) and
``max_account_orchestrator.write_synthetic_preflight`` (explicit zero-work evidence for
a paid probe with no coordinator lease) -- and prints the manifest SHA-256 the worker's
``--manifest-sha256`` needs. It does NOT spend: it only prepares.

Usage (profile-bound, from RussianTranslation/):

    python src/pilot/canary_manifest_build.py --profile-slot c4 \
        --config-dir "D:\\ClaudeTools\\profiles\\claude4\\.claude" \
        --outdir src/pilot/output/h2174

Then run the printed headless_worker command. Judge the result with
``canary_gate.py judge`` -- never promote synthetic output (the promoter's C-05
refusal is expected).

PROMPT SHAPE -- the canary rides the PRODUCTION path, deliberately (H2245)
-------------------------------------------------------------------------
The canary is un-masked pure gloss (three line-opening senses, zero ``<ls>``, zero
``{#..#}``) while production runs the masked-inline regime, so "does the canary need its
own non-masked prompt variant?" is a real design question, not boilerplate: a silent
mismatch changes what the canary actually tests.

**Decision: reuse the production prompt path verbatim -- no canary-specific variant.**
The builder therefore passes the same ``--nominal`` (mode ``nominal_masked``) production
generation uses. The justification is empirical, not stylistic: on this fixture the mask is
an *identity transform*. ``pwg_mask.mask(raw)`` returns ``skel == raw`` with **zero**
placeholders (stats ``pct_de=3``, everything else 0), and the emitted manifest carries
``placeholder_maps[<key>] == []``. So the model sees exactly the pure gloss, reached through
the production code path -- which is the entire point of a synthetic *control*: a
canary-only prompt would exercise a path no paid window ever runs, and a green canary would
then say nothing about production.

SPAWN SHAPE -- ``--cli-safe-mode`` / ``--no-cli-safe-mode`` (H2251)
------------------------------------------------------------------
The same "a control must ride the path production rides" argument applies to the *spawn*,
not just the prompt. ``execution.cli_safe_mode`` decides whether the CLI child is spawned
with ``--safe-mode`` (H2189), and a canary judged on one spawn shape says nothing about a
lane running the other. So the builder can pin it explicitly:

* omitted (the default) -- the manifest carries no ``cli_safe_mode`` key and
  ``headless_worker.resolve_safe_mode`` applies the lane default. This is the shape the
  committed golden artifact pins, so an ordinary gate is byte-identical to before.
* ``--cli-safe-mode`` / ``--no-cli-safe-mode`` -- write ``true``/``false`` into the
  execution block, producing a receipt that is *attributable to one arm*. H2251 needed
  exactly this: a GO receipt on the safe-mode arm was the evidence H2189 §5.1 named as the
  precondition for flipping the default, and it could not be inherited from a baseline run.

The value is patched into the emitted manifest BEFORE the SHA-256 is taken, so the digest
the worker's ``--manifest-sha256`` checks still binds the arm the receipt claims.

The masked-regime preamble does still ride along, vacuously (it explains ``{Tn}`` tokens
when none exist). That is accepted deliberately: dropping it would fork the prompt and
re-introduce the mismatch this decision exists to avoid. Both properties are pinned by
``canary_manifest_build_selftest.py``, so a future mask change that started emitting a
placeholder here -- i.e. that quietly stopped the canary being pure gloss -- goes red
instead of silently degrading the control.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))    # RussianTranslation/ (src/pilot -> src -> repo)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from execution_contract import PRODUCTION_HARD_TIMEOUT_MS  # noqa: E402

# The curated H994 D-Q silent-sense-loss synthetic control. Its provenance_class is
# synthetic_control, so canary_gate refuses to judge a real window as a canary.
CANARY_KEY = 'dq_canary_puregloss~~h0_zz_pw'
FIXTURE_DIR = os.path.join(REPO, 'pwg_ru', 'h994', 'canary')


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def pin_safe_mode(manifest_path, cli_safe_mode):
    """Write ``execution.cli_safe_mode`` into an already-generated manifest (H2251).

    Called BEFORE the SHA-256 is taken, so the digest the worker verifies covers the arm
    the receipt will claim -- a receipt whose manifest could still be swapped for the other
    spawn shape would prove nothing about either.

    ``None`` is not "false": it leaves the key absent so the lane default applies, which is
    what keeps an ordinary gate byte-identical to the committed golden artifact.
    """
    if cli_safe_mode is None:
        return
    with open(manifest_path, encoding='utf-8') as fh:
        manifest = json.load(fh)
    execution = manifest.get('execution')
    if not isinstance(execution, dict):
        raise SystemExit(
            'cannot pin cli_safe_mode: this manifest has no v2 execution block (build it '
            'profile-bound, with --profile-slot and --config-dir)')
    execution['cli_safe_mode'] = bool(cli_safe_mode)
    with open(manifest_path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
        fh.write('\n')


def build(profile_slot, config_dir, outdir, root, key=CANARY_KEY,
          fixture_dir=FIXTURE_DIR, cli_safe_mode=None):
    raw = os.path.join(fixture_dir, key + '.raw.txt')
    portrait = os.path.join(fixture_dir, key + '.portrait.json')
    for path in (raw, portrait):
        if not os.path.exists(path):
            raise SystemExit('canary fixture missing: %s' % path)
    os.makedirs(outdir, exist_ok=True)
    manifest = os.path.join(outdir, 'execution_manifest.canary.json')
    harness = os.path.join(outdir, 'run_pilot_wf.canary.js')
    preflight = os.path.join(outdir, 'preflight.canary.json')

    env = dict(os.environ, PWG_INPUT_DIR=fixture_dir)
    cmd = [sys.executable, os.path.join(HERE, 'gen_opt_harness2.py'), root,
           '--nominal', '--no-grammar', '--keys=%s' % key,
           '--synthetic-keys=%s' % key,
           # H4054: pin the canary's call shape so the golden artifact stays diff-stable
           # against future generator-default drift (the one-key canary is one card per call
           # under any default).
           '--output-budget=1',
           '--profile-slot=%s' % profile_slot,
           '--execution-route=claude-cli-headless',
           '--executor-lane=serial-whole-card',
           '--validation-method=audit_window+final_schema',
           '--out=%s' % harness, '--manifest-out=%s' % manifest]
    if config_dir:
        cmd.append('--config-dir=%s' % config_dir)
    proc = subprocess.run(cmd, cwd=REPO, env=env, text=True,
                          encoding='utf-8', capture_output=True)
    if proc.returncode:
        raise SystemExit('gen_opt_harness2 failed:\n%s'
                         % (proc.stderr or proc.stdout)[-2000:])

    # The REAL lane preflight, not write_synthetic_preflight(): headless_worker refuses a
    # synthetic-probe preflight with "synthetic probe preflight cannot authorize manifest
    # execution" (that helper serves orchestrator probes that carry no manifest).
    pf = subprocess.run(
        [sys.executable, os.path.join(HERE, 'perf_preflight.py'), root,
         '--nominal', '--no-grammar', '--keys=%s' % key, '--json'],
        cwd=REPO, env=env, text=True, encoding='utf-8', capture_output=True)
    if pf.returncode:
        raise SystemExit('perf_preflight failed:\n%s'
                         % (pf.stderr or pf.stdout)[-2000:])
    with open(preflight, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(pf.stdout)

    pin_safe_mode(manifest, cli_safe_mode)
    return manifest, harness, preflight, sha256_file(manifest)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--profile-slot', required=True,
                    help='profile the canary is BOUND to; gate the same slot you spend on')
    ap.add_argument('--config-dir', help='CLAUDE_CONFIG_DIR for that profile slot')
    ap.add_argument('--outdir', required=True)
    ap.add_argument('--root', help='nominal root label (default nominal_<slot>canary)')
    # H2251: pin the SPAWN shape the receipt is attributable to. Omitted => the lane default
    # applies and the manifest stays byte-identical to the committed golden artifact.
    ap.add_argument('--cli-safe-mode', dest='cli_safe_mode', action='store_true',
                    default=None,
                    help='pin execution.cli_safe_mode=true (spawn with --safe-mode, H2189)')
    ap.add_argument('--no-cli-safe-mode', dest='cli_safe_mode', action='store_false',
                    help='pin execution.cli_safe_mode=false (spawn WITHOUT --safe-mode)')
    args = ap.parse_args(argv)
    root = args.root or 'nominal_%scanary' % args.profile_slot

    manifest, harness, preflight, sha = build(
        args.profile_slot, args.config_dir, args.outdir, root,
        cli_safe_mode=args.cli_safe_mode)
    print('manifest  :', manifest)
    print('harness   :', harness)
    print('preflight :', preflight)
    print('sha256    :', sha)
    print('safe mode : %s' % ('(lane default -- key absent)' if args.cli_safe_mode is None
                              else 'execution.cli_safe_mode=%s'
                                   % json.dumps(args.cli_safe_mode)))
    print()
    print('next (ONE paid call):')
    print('  python src/pilot/headless_worker.py %s \\' % manifest)
    print('      --output %s/out.canary.json \\' % args.outdir)
    print('      --status-out %s/status.canary.json \\' % args.outdir)
    print('      --only-profile %s --max-agents 1 --timeout %d --max-calls 3 \\'
          % (args.profile_slot, PRODUCTION_HARD_TIMEOUT_MS // 1000))
    print('      --manifest-sha256 %s \\' % sha)
    print('      --preflight %s \\' % preflight)
    print('      --call-reservation %s/calls.canary.json --run-id <run-id>' % args.outdir)
    return 0


if __name__ == '__main__':
    sys.exit(main())
