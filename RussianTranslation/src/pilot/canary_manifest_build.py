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
"""
import argparse
import hashlib
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))    # RussianTranslation/ (src/pilot -> src -> repo)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

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


def build(profile_slot, config_dir, outdir, root, key=CANARY_KEY,
          fixture_dir=FIXTURE_DIR):
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

    return manifest, harness, preflight, sha256_file(manifest)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--profile-slot', required=True,
                    help='profile the canary is BOUND to; gate the same slot you spend on')
    ap.add_argument('--config-dir', help='CLAUDE_CONFIG_DIR for that profile slot')
    ap.add_argument('--outdir', required=True)
    ap.add_argument('--root', help='nominal root label (default nominal_<slot>canary)')
    args = ap.parse_args(argv)
    root = args.root or 'nominal_%scanary' % args.profile_slot

    manifest, harness, preflight, sha = build(
        args.profile_slot, args.config_dir, args.outdir, root)
    print('manifest  :', manifest)
    print('harness   :', harness)
    print('preflight :', preflight)
    print('sha256    :', sha)
    print()
    print('next (ONE paid call):')
    print('  python src/pilot/headless_worker.py %s \\' % manifest)
    print('      --output %s/out.canary.json \\' % args.outdir)
    print('      --status-out %s/status.canary.json \\' % args.outdir)
    print('      --only-profile %s --max-agents 1 --timeout 300 --max-calls 3 \\'
          % args.profile_slot)
    print('      --manifest-sha256 %s \\' % sha)
    print('      --preflight %s \\' % preflight)
    print('      --call-reservation %s/calls.canary.json --run-id <run-id>' % args.outdir)
    return 0


if __name__ == '__main__':
    sys.exit(main())
