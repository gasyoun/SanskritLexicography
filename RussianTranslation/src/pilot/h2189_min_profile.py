#!/usr/bin/env python
"""H2189 Phase 1-2 -- inventory what a CLAUDE_CONFIG_DIR injects, and build a minimal twin.

Why this exists
---------------
`headless_worker.bare_cli_cwd()` (H2158) removed the **project** context from every paid
spawn: no repo `CLAUDE.md`, no git state. It did NOT remove the **profile** root bound as
`CLAUDE_CONFIG_DIR`. H2158 measured a probe under the operator profile still carrying a
six-figure prefix against a ~6-8 k task prompt, and -- worse than cost -- the model
REFUSED its own task instruction, citing a `Next:` operator rule that reached it through
the profile rather than through the prompt. Both are profile-surface problems, so this
script makes that surface countable and then builds a profile without it.

What actually reaches the model from a profile (the four channels)
------------------------------------------------------------------
1. **User memory** -- a `CLAUDE.md` the CLI auto-discovers. Reported for BOTH the config
   dir and the real home `~/.claude`, because a minimal `CLAUDE_CONFIG_DIR` does not by
   itself prove the home-dir copy stopped being read; the A/B is what settles that.
2. **Skills / commands / agents** -- each is advertised to the model by name and
   description in the system prompt, so a 200-command profile is a five-figure token
   surface before a single card is sent.
3. **Hooks** -- `SessionStart` / `UserPromptSubmit` hooks inject text directly into the
   conversation. This is the channel that carries the operator GTD callout, and the most
   likely origin of the H2158 instruction override: a hook-injected rule arrives as
   context, not as a prompt the caller wrote.
4. **Plugins / MCP servers** -- more tool and skill definitions on the same budget.

Only channel 1 is a file you can see by opening the profile; the other three are why an
eyeball check of the directory understates it.

Credential note (read before running --build)
---------------------------------------------
The minimal profile is a SIBLING of the paid profile, not a replacement: it copies
`.credentials.json` so it authenticates as the SAME billing identity. Consequences,
stated rather than discovered later:

* The copy is a second on-disk OAuth token. It lives under the operator profile root
  (outside every clone) and must never be committed. `--build` refuses to write into a
  git working tree for exactly this reason.
* After a token refresh the two copies diverge; re-run `--build --refresh-creds` to
  re-sync. A stale copy fails as an auth error, not as a silent wrong-account call.
* Because `execution_contract.ActiveCallClaim` is keyed by the config-directory
  FINGERPRINT, the minimal profile takes a DIFFERENT lock from the profile it clones.
  Two runs -- one per directory -- would therefore not serialise against each other while
  billing the same account. `--build` prints this; any production wiring must treat the
  minimal profile as a distinct roster slot, never as an alias of the one it copies.

Offline. Spends nothing. The paid comparison is `h2189_profile_ab.py`.

    python src/pilot/h2189_min_profile.py --inventory
    python src/pilot/h2189_min_profile.py --build

Model: authored by Opus 5 (`claude-opus-5[1m]`) for handoff H2189.
"""
import argparse
import json
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from execution_contract import config_dir_fingerprint                # noqa: E402

# The profile-bound config dir the paid CLI lane runs under today. Same constant as
# h2158_route_ab.CONFIG_DIR and cache_prefix_stability_probe.CONFIG_DIR -- do not fork it.
PAID_CONFIG_DIR = r'D:\ClaudeTools\profiles\claude4\.claude'
MIN_CONFIG_DIR = r'D:\ClaudeTools\profiles\claude4-min\.claude'

# Keys of `.claude.json` that carry per-project state rather than machine/account
# identity. Dropped from the minimal copy: they name repositories, which is precisely the
# project context bare_cli_cwd() went to the trouble of removing.
PROJECT_STATE_KEYS = ('projects', 'tipsHistory', 'promptQueueUseCount')

# Directories/files whose whole purpose is to advertise capability to the model. A
# minimal profile omits them; a profile that "looks empty" but still symlinks these is
# not minimal at all (the operator profiles here symlink skills/commands/agents to a
# shared ~/.claude, so `ls` on the profile shows four harmless-looking links).
CAPABILITY_DIRS = ('skills', 'commands', 'agents', 'plugins', 'references', 'rules')

# Hook events that inject text into the conversation rather than merely gating a tool.
# These are the ones that can hand the model an instruction the caller never wrote.
INJECTING_HOOK_EVENTS = ('SessionStart', 'UserPromptSubmit')


# Files an ancestor of the spawn cwd can hand to the model as "project" memory. The CLI
# walks UP from cwd; `bare_cli_cwd()` only rejects an ancestor carrying a bare `CLAUDE.md`
# or a `.git`, so an ancestor carrying `.claude\CLAUDE.md` passes its check and is loaded
# anyway. On a Windows box whose bare dir is under %TEMP% -- i.e. under the Windows user
# profile -- that is exactly where the operator's global CLAUDE.md lives.
ANCESTOR_MEMORY_RELPATHS = (
    'CLAUDE.md',
    os.path.join('.claude', 'CLAUDE.md'),
    os.path.join('.claude', 'CLAUDE.local.md'),
)
ANCESTOR_MEMORY_DIRS = (os.path.join('.claude', 'rules'),)


def cwd_ancestry_scan(cwd):
    """Every memory file an ancestor walk from `cwd` can inject, with byte sizes.

    Free, offline, and the cheapest possible check that a "bare" spawn directory is
    actually bare: a directory with nothing in it still inherits whatever its PARENTS
    advertise, and that inheritance is invisible from an `ls` of the directory itself.
    """
    hits = []
    probe = os.path.abspath(cwd)
    while True:
        for rel in ANCESTOR_MEMORY_RELPATHS:
            path = os.path.join(probe, rel)
            if os.path.exists(path):
                hits.append({'path': path, 'bytes': os.path.getsize(path), 'kind': 'file'})
        for rel in ANCESTOR_MEMORY_DIRS:
            path = os.path.join(probe, rel)
            if os.path.isdir(path):
                total = 0
                for name in os.listdir(path):
                    full = os.path.join(path, name)
                    if os.path.isfile(full):
                        total += os.path.getsize(full)
                if total:
                    hits.append({'path': path, 'bytes': total, 'kind': 'dir'})
        if os.path.exists(os.path.join(probe, '.git')):
            hits.append({'path': os.path.join(probe, '.git'), 'bytes': 0, 'kind': 'git'})
        parent = os.path.dirname(probe)
        if parent == probe:
            return hits
        probe = parent


def clean_cwd(preferred):
    """A spawn directory whose ANCESTRY carries no memory files -- not merely an empty dir.

    Fails SAFE like `bare_cli_cwd()`: returns None rather than handing back a directory
    that still inherits project memory, because a silent fallback would reintroduce the
    tax with no signal that it had.
    """
    try:
        os.makedirs(preferred, exist_ok=True)
    except OSError:
        return None
    return preferred if not cwd_ancestry_scan(preferred) else None


def _count_entries(path):
    try:
        return len(os.listdir(path))
    except OSError:
        return None


def _load_settings(config_dir):
    path = os.path.join(config_dir, 'settings.json')
    if not os.path.exists(path):
        return {}, path
    try:
        with open(path, encoding='utf-8') as fh:
            return json.load(fh), path
    except (OSError, ValueError):
        return {}, path


def inventory(config_dir):
    """Return a dict describing every channel this profile can push into the prompt."""
    settings, settings_path = _load_settings(config_dir)
    hooks = settings.get('hooks') or {}
    hook_counts = {}
    for event, matchers in hooks.items():
        if not isinstance(matchers, list):
            continue
        hook_counts[event] = sum(len(m.get('hooks') or []) for m in matchers
                                 if isinstance(m, dict))
    memory = os.path.join(config_dir, 'CLAUDE.md')
    home_memory = os.path.join(os.path.expanduser('~'), '.claude', 'CLAUDE.md')
    rec = {
        'config_dir': config_dir,
        'exists': os.path.isdir(config_dir),
        'fingerprint': config_dir_fingerprint(config_dir),
        'memory_bytes': os.path.getsize(memory) if os.path.exists(memory) else 0,
        # Reported even though it is outside the config dir: if the CLI resolves user
        # memory from the real home rather than from CLAUDE_CONFIG_DIR, a minimal profile
        # does not strip it and the A/B must show that in the token counts.
        'home_memory_path': home_memory,
        'home_memory_bytes': (os.path.getsize(home_memory)
                              if os.path.exists(home_memory) else 0),
        'settings_path': settings_path,
        'settings_bytes': (os.path.getsize(settings_path)
                           if os.path.exists(settings_path) else 0),
        'hooks_total': sum(hook_counts.values()),
        'hooks_injecting': sum(hook_counts.get(e, 0) for e in INJECTING_HOOK_EVENTS),
        'hooks_by_event': hook_counts,
        'capability_counts': {name: _count_entries(os.path.join(config_dir, name))
                              for name in CAPABILITY_DIRS},
        'has_credentials': os.path.exists(os.path.join(config_dir, '.credentials.json')),
        'mcp_servers': len((settings.get('mcpServers') or {})),
    }
    rec['capability_total'] = sum(v for v in rec['capability_counts'].values() if v)
    return rec


def print_inventory(rec):
    caps = ', '.join('%s=%s' % (k, '-' if v is None else v)
                     for k, v in sorted(rec['capability_counts'].items()))
    print('config dir        : %s%s' % (rec['config_dir'],
                                        '' if rec['exists'] else '  (MISSING)'))
    print('fingerprint       : %s' % rec['fingerprint'])
    print('profile CLAUDE.md : %d bytes' % rec['memory_bytes'])
    print('home  CLAUDE.md   : %d bytes  (%s)'
          % (rec['home_memory_bytes'], rec['home_memory_path']))
    print('settings.json     : %d bytes' % rec['settings_bytes'])
    print('hooks             : %d total, %d injecting (%s)  %s'
          % (rec['hooks_total'], rec['hooks_injecting'],
             '/'.join(INJECTING_HOOK_EVENTS),
             json.dumps(rec['hooks_by_event'], sort_keys=True)))
    print('capability dirs   : %d entries  [%s]' % (rec['capability_total'], caps))
    print('mcp servers       : %d' % rec['mcp_servers'])
    print('credentials       : %s' % ('present' if rec['has_credentials'] else 'ABSENT'))


def _refuse_if_inside_repo(dest):
    """A profile holds a live OAuth token; it must not be born inside a working tree."""
    probe = os.path.abspath(dest)
    while True:
        if os.path.exists(os.path.join(probe, '.git')):
            raise SystemExit(
                'REFUSING to build a credential-bearing profile inside the git working '
                'tree at %s -- choose a --dest outside every clone.' % probe)
        parent = os.path.dirname(probe)
        if parent == probe:
            return
        probe = parent


def build(src, dest, refresh_creds=False):
    """Create (or re-sync) a minimal profile that authenticates as `src` and injects nothing."""
    if not os.path.isdir(src):
        raise SystemExit('source profile does not exist: %s' % src)
    _refuse_if_inside_repo(dest)
    os.makedirs(dest, exist_ok=True)

    # `.claude.json` minus per-project state. The client-side caches (growthbook flags,
    # model lists) are carried over deliberately: they never enter the prompt, and
    # dropping them would make the minimal arm re-fetch them at startup, charging the A/B
    # a network delay that has nothing to do with the prompt surface under test.
    src_json = os.path.join(src, '.claude.json')
    if os.path.exists(src_json):
        with open(src_json, encoding='utf-8') as fh:
            data = json.load(fh)
        dropped = [k for k in PROJECT_STATE_KEYS if k in data]
        for key in dropped:
            data.pop(key, None)
        with open(os.path.join(dest, '.claude.json'), 'w', encoding='utf-8') as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    else:
        dropped = []

    creds_src = os.path.join(src, '.credentials.json')
    creds_dest = os.path.join(dest, '.credentials.json')
    copied_creds = False
    if os.path.exists(creds_src) and (refresh_creds or not os.path.exists(creds_dest)):
        shutil.copyfile(creds_src, creds_dest)
        copied_creds = True

    # An EMPTY settings object, not a trimmed copy of the operator's: every hook,
    # statusLine and permission entry in the paid profile is an operator convenience that
    # a headless translation call does not use. `--permission-mode plan` supplies the
    # only permission posture this lane needs.
    with open(os.path.join(dest, 'settings.json'), 'w', encoding='utf-8') as fh:
        json.dump({}, fh, indent=2)

    print('built minimal profile: %s' % dest)
    print('  cloned identity from: %s' % src)
    print('  .claude.json keys dropped: %s' % (', '.join(dropped) or 'none'))
    print('  credentials: %s' % ('copied' if copied_creds
                                 else ('already present (use --refresh-creds to re-sync)'
                                       if os.path.exists(creds_dest) else 'ABSENT')))
    print('  settings.json: {} (no hooks, no statusLine, no permissions)')
    print('  no CLAUDE.md, no skills/commands/agents/plugins/references/rules')
    print('')
    print('  fingerprint (source) : %s' % config_dir_fingerprint(src))
    print('  fingerprint (minimal): %s' % config_dir_fingerprint(dest))
    print('  NOTE: different fingerprints => execution_contract.ActiveCallClaim takes a')
    print('        DIFFERENT kernel lock for each. They bill the SAME account, so running')
    print('        both at once bypasses the one-active-call guard. Treat the minimal')
    print('        profile as its own roster slot, never as an alias.')
    return dest


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--src', default=PAID_CONFIG_DIR,
                    help='the paid profile to clone identity from')
    ap.add_argument('--dest', default=MIN_CONFIG_DIR,
                    help='where the minimal profile lives (outside every clone)')
    ap.add_argument('--inventory', action='store_true',
                    help='report the injection surface of --src and --dest, build nothing')
    ap.add_argument('--build', action='store_true', help='create/re-sync the minimal profile')
    ap.add_argument('--refresh-creds', action='store_true',
                    help='re-copy .credentials.json even if the minimal profile has one')
    ap.add_argument('--json', action='store_true', help='machine-readable inventory')
    ap.add_argument('--scan-cwd', metavar='DIR', default=None,
                    help='report the memory files an ancestor walk from DIR would inject '
                         '(pass the bare spawn dir to check it is actually bare)')
    args = ap.parse_args()

    if args.scan_cwd:
        hits = cwd_ancestry_scan(args.scan_cwd)
        print('ancestor scan from: %s' % os.path.abspath(args.scan_cwd))
        if not hits:
            print('  (clean -- no ancestor memory files)')
        for hit in hits:
            print('  %-6s %8d bytes  %s' % (hit['kind'], hit['bytes'], hit['path']))
        print('  total injectable: %d bytes' % sum(h['bytes'] for h in hits))
        return 0

    if not args.inventory and not args.build:
        args.inventory = True

    if args.build:
        build(args.src, args.dest, refresh_creds=args.refresh_creds)
        print('')

    if args.inventory:
        recs = [inventory(args.src), inventory(args.dest)]
        if args.json:
            print(json.dumps(recs, ensure_ascii=False, indent=2))
        else:
            for label, rec in zip(('PAID PROFILE', 'MINIMAL PROFILE'), recs):
                print('== %s ==' % label)
                print_inventory(rec)
                print('')
    return 0


if __name__ == '__main__':
    sys.exit(main())
