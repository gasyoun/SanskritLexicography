#!/usr/bin/env python3
r"""profile_lane — ONE .env / env-var knob for the active Claude profile slot.

MG ask (24-08-2026): re-pointing the live lane (c1 today; c4 back alongside c1,
or either alone, later) must be a one-line config edit, never a code sweep.

Resolution order for the ACTIVE slot:

    1. real environment ``PWG_PROFILE_SLOT``
       (process-scoped — two shells may drive two profiles simultaneously;
       each manifest still binds its own config_dir_fingerprint and the
       kernel ActiveCallClaim keeps one call per fingerprint)
    2. legacy alias ``PWG_PROFILE`` (the same key
       window_reports.resolve_profile already reads as last fallback)
    3. the first existing .env file that defines either key:
       ``$PWG_ENV_FILE`` → ``RussianTranslation/.env`` → ``RussianTranslation/src/.env``

Precedence contract (unchanged, load-bearing): an explicit CLI flag
(``--account``, ``--only-profile``, ``--bind-profile``) and a bound manifest-v2
``execution.profile_slot`` ALWAYS win over this resolver. The knob fills
DEFAULTS only — the H963 probe's account fallback, the nonstop scheduler's
roster order. It can never silently redirect a bound production window.

Roster: ``PWG_PROFILE_ROSTER=c1,c4`` (comma list, same lookup ladder) overrides
the scheduler's R5.1 default order outright. When only the active slot is set,
the scheduler rotates that slot to the front of its default roster (relative
order preserved), so "one at a time" and "both, c1 first" are both config edits.

This module is stdlib-only and side-effect-free: no reads happen outside the
explicit accessors, so importing it cannot mutate process state.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
RUSSIAN_TRANSLATION = os.path.dirname(SRC)

ENV_KEYS = ('PWG_PROFILE_SLOT', 'PWG_PROFILE')
ROSTER_KEY = 'PWG_PROFILE_ROSTER'
ENV_FILE_OVERRIDE_KEY = 'PWG_ENV_FILE'

# Historical probe fallback (H963/H3443-verified claim: "default c4"). Never
# auto-flipped here — a lane change is made in .env / the environment, not code.
DEFAULT_FALLBACK_SLOT = 'c4'


def load_env_file(path):
    """Parse a KEY=VALUE .env file (stdlib only).

    Accepts ``#`` comments, blank lines, optional ``export `` prefix, single or
    double quotes around values, inline ``# comment`` after unquoted values,
    and CRLF line endings. Returns {} for a missing/unreadable file — a broken
    config degrades to "unset", it never raises into a gate/probe path.
    """
    try:
        with open(path, 'r', encoding='utf-8-sig') as fh:
            raw = fh.read()
    except OSError:
        return {}
    out = {}
    for line in raw.splitlines():
        text = line.strip()
        if not text or text.startswith('#'):
            continue
        if text.startswith('export '):
            text = text[len('export '):].strip()
        if '=' not in text:
            continue
        key, _, value = text.partition('=')
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        else:
            hash_pos = value.find(' #')
            if hash_pos != -1:
                value = value[:hash_pos].strip()
        out[key] = value
    return out


def candidate_env_files(env=None):
    """Ordered .env candidates: $PWG_ENV_FILE → repo-root .env → src/.env."""
    env = os.environ if env is None else env
    paths = []
    override = env.get(ENV_FILE_OVERRIDE_KEY)
    if override:
        paths.append(override)
    paths.append(os.path.join(RUSSIAN_TRANSLATION, '.env'))
    paths.append(os.path.join(SRC, '.env'))
    seen, out = set(), []
    for p in paths:
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _from_env_files(env=None):
    for path in candidate_env_files(env):
        data = load_env_file(path)
        for key in ENV_KEYS:
            val = data.get(key)
            if val not in (None, ''):
                return str(val).strip() or None
    return None


def active_profile(env=None):
    """The active profile slot per the resolution order, or None if unset."""
    env = os.environ if env is None else env
    for key in ENV_KEYS:
        val = env.get(key)
        if val not in (None, ''):
            return str(val).strip() or None
    return _from_env_files(env)


def active_roster(env=None, default_roster=()):
    """Roster order per the knob, or None when nothing is configured.

    ``PWG_PROFILE_ROSTER=a,b,c`` wins outright. Otherwise, when an active slot
    is set and appears in ``default_roster``, returns the default rotated so
    the active slot leads (relative order preserved). None ⇒ caller uses its
    own default unchanged.
    """
    env = os.environ if env is None else env
    raw = env.get(ROSTER_KEY)
    if raw in (None, ''):
        for path in candidate_env_files(env):
            data = load_env_file(path)
            raw = data.get(ROSTER_KEY)
            if raw not in (None, ''):
                break
    if raw not in (None, ''):
        roster = [part.strip() for part in str(raw).split(',') if part.strip()]
        return roster or None
    slot = active_profile(env)
    if not slot or not default_roster or slot not in default_roster:
        return None
    rest = [s for s in default_roster if s != slot]
    return [slot] + rest


if __name__ == '__main__':
    slot = active_profile()
    print(slot if slot else '(no PWG_PROFILE_SLOT configured)')
