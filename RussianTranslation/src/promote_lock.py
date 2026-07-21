#!/usr/bin/env python
"""H336/H-1 — O_EXCL claim file guarding the promotion read-guard-write window.

Two concurrent `promote_final_cards.py --merge` runs (or a `--merge` overlapping a
full rebuild) are last-writer-wins on the canonical store: nothing serializes the
read-existing-store / merge-in-new-rows / os.replace window, and both runs also
write the same fixed `.premerge.bak` name, so the loser's promoted rows AND the
recovery backup of the loser's prior state are both gone. This is the single
unrecoverable-loss path in the H335 collision matrix (PIPELINE_CAPABILITY_AUDIT_
2026-07-08.md, W1).

This is deliberately NOT coordinator.py's DirLock: DirLock's staleness check calls
os.kill(pid, 0), which is meaningless once the "other" process is a different
account's clone on the same box (three accounts, one machine, three trees) or a
genuinely different machine — a stale claim from a dead run on one clone would
never look stale to a PID check running in a different process table (or would
collide with an unrelated live PID on the reader's own machine, which is worse:
a false "still held"). So staleness here is TTL-only, and an operator gets an
explicit `--steal-lock` escape hatch instead of PID guessing.
"""
import datetime
import json
import os
import socket
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

DEFAULT_TTL_SECONDS = 30 * 60          # a promote run is seconds; 30 min covers a hang


class ClaimBusy(SystemExit):
    """Raised (as a SystemExit subclass) when a live claim is held by someone else."""


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec='seconds').replace('+00:00', 'Z')


def _parse_ts(value):
    if not value:
        return None
    try:
        return datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None


def claim_path(store_path):
    return store_path + '.promote.lock'


class PromoteClaim:
    """O_EXCL claim file at ``<store>.promote.lock``, held across the whole promotion
    read-guard-write window. NO PID-liveness check (see module docstring) — staleness
    is TTL-only, and ``steal`` bypasses it entirely for a deliberate operator override."""

    def __init__(self, store_path, ttl_seconds=DEFAULT_TTL_SECONDS, steal=False):
        self.path = claim_path(store_path)
        self.ttl_seconds = ttl_seconds
        self.steal = steal
        self._acquired = False

    def _payload(self):
        return {'schema': 'pwg.promote_claim.v1', 'pid': os.getpid(),
                'host': socket.gethostname(), 'claimed_at': _utc_now()}

    def _read(self):
        try:
            with open(self.path, encoding='utf-8') as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return None

    def _ts_stale(self, claimed_at):
        claimed = _parse_ts(claimed_at)
        if not claimed:
            return True                 # unreadable/corrupt claim file -> treat as stale
        age = (datetime.datetime.now(datetime.timezone.utc) - claimed).total_seconds()
        return age > self.ttl_seconds

    def _reclaim(self, judged_claimed_at):
        """H1386 D2: identity-checked, rename-based reclaim of a claim judged stale.

        The pre-fix read-then-os.remove pair was a TOCTOU: two cross-clone promoters could
        both judge the crashed run's old claim stale, then the slower one os.remove'd the
        FASTER one's fresh claim -- both 'held' the lock and the loser's promoted rows
        vanished (the exact last-writer-wins loss this lock exists to prevent). Instead:
        atomically rename the claim aside (os.replace), re-read what was actually captured,
        and verify its claimed_at matches the stale value we judged. Capturing a
        contender's FRESH claim restores it and loses the reclaim; FileNotFoundError on the
        rename means another contender already reclaimed -- return True so the caller
        retries the O_EXCL create and re-evaluates whatever claim now exists."""
        import uuid
        aside = self.path + '.reclaimed.' + uuid.uuid4().hex
        try:
            os.replace(self.path, aside)
        except FileNotFoundError:
            return True                 # another contender already reclaimed it
        except OSError:
            return False
        try:
            with open(aside, encoding='utf-8') as f:
                moved = json.load(f)
        except (OSError, json.JSONDecodeError):
            moved = {}
        moved_at = (moved or {}).get('claimed_at')
        if moved_at != judged_claimed_at and not self._ts_stale(moved_at):
            # We captured a CONTENDER'S fresh claim (it reclaimed between our read and our
            # rename) -- restore it and lose the reclaim.
            try:
                os.replace(aside, self.path)
            except OSError:
                pass
            return False
        try:
            os.remove(aside)
        except OSError:
            pass
        return True

    def _try_remove_stale_or_stolen(self):
        if self.steal:
            try:
                os.remove(self.path)
            except OSError:
                pass
            return True
        meta = self._read()
        claimed_at = (meta or {}).get('claimed_at')
        if not self._ts_stale(claimed_at):
            return False
        return self._reclaim(claimed_at)

    def __enter__(self):
        while True:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                if self._try_remove_stale_or_stolen():
                    continue            # retry the O_EXCL create against the now-empty slot
                meta = self._read() or {}
                raise ClaimBusy(
                    'promotion claim held by pid=%s host=%s since %s (< %ds old) — another '
                    'promote run is in flight against this store. Wait for it to finish, or '
                    'pass --steal-lock if you are certain it is dead (crashed process, no '
                    'PID-liveness check is possible across clones/machines).'
                    % (meta.get('pid'), meta.get('host'), meta.get('claimed_at'), self.ttl_seconds))
            else:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(self._payload(), f)
                self._acquired = True
                return self

    def __exit__(self, exc_type, exc, tb):
        if self._acquired:
            try:
                os.remove(self.path)
            except OSError:
                pass
        return False


def selftest():
    import tempfile
    d = tempfile.mkdtemp()
    store = os.path.join(d, 'store.jsonl')
    open(store, 'w', encoding='utf-8').close()

    # A held claim blocks a second claimant (two processes, one wins).
    first = PromoteClaim(store, ttl_seconds=DEFAULT_TTL_SECONDS)
    with first:
        assert os.path.exists(claim_path(store)), 'claim file must exist while held'
        try:
            with PromoteClaim(store, ttl_seconds=DEFAULT_TTL_SECONDS):
                raise AssertionError('a second claimant must not acquire a live claim')
        except ClaimBusy:
            pass                        # the second claimant must retry/error cleanly
    assert not os.path.exists(claim_path(store)), 'claim file must be removed on release'

    # After release, a fresh claim succeeds immediately.
    with PromoteClaim(store, ttl_seconds=DEFAULT_TTL_SECONDS):
        pass

    # A STALE claim (age > ttl) is reclaimed automatically — no PID check involved.
    stale_meta = {'schema': 'pwg.promote_claim.v1', 'pid': 999999999, 'host': 'some-other-host',
                  'claimed_at': '2000-01-01T00:00:00Z'}
    with open(claim_path(store), 'w', encoding='utf-8') as f:
        json.dump(stale_meta, f)
    with PromoteClaim(store, ttl_seconds=DEFAULT_TTL_SECONDS):
        assert True, 'a stale claim (age > ttl) must be reclaimed without any PID check'
    assert not os.path.exists(claim_path(store))

    # A FRESH claim (age < ttl) from a bogus/unreachable pid+host is NOT reclaimed
    # without --steal-lock: staleness is TTL-only, never PID-liveness.
    fresh_meta = {'schema': 'pwg.promote_claim.v1', 'pid': 999999999, 'host': 'some-other-host',
                  'claimed_at': _utc_now()}
    with open(claim_path(store), 'w', encoding='utf-8') as f:
        json.dump(fresh_meta, f)
    try:
        with PromoteClaim(store, ttl_seconds=DEFAULT_TTL_SECONDS):
            raise AssertionError('a fresh claim from an unreachable pid must still block '
                                 '(no PID-liveness check across clones/machines)')
    except ClaimBusy:
        pass
    # --steal-lock bypasses even a fresh claim.
    with PromoteClaim(store, ttl_seconds=DEFAULT_TTL_SECONDS, steal=True):
        assert True, '--steal-lock must bypass a live claim unconditionally'
    assert not os.path.exists(claim_path(store))

    # H1386 D2: identity-checked reclaim (the read->remove TOCTOU). Promoter A judged the
    # claim stale, but BETWEEN A's read and A's reclaim a contender already reclaimed and
    # recreated a FRESH claim. A's reclaim must capture-and-RESTORE the fresh claim (lose
    # the race), never delete it -- the pre-fix os.remove deleted whatever was there.
    stale_at = '2000-01-01T00:00:00Z'
    fresh_contender = {'schema': 'pwg.promote_claim.v1', 'pid': 4242, 'host': 'contender',
                       'claimed_at': _utc_now()}
    with open(claim_path(store), 'w', encoding='utf-8') as f:
        json.dump(fresh_contender, f)
    a = PromoteClaim(store, ttl_seconds=DEFAULT_TTL_SECONDS)
    assert a._reclaim(stale_at) is False, 'reclaim must LOSE against a contender fresh claim'
    survived = json.load(open(claim_path(store), encoding='utf-8'))
    assert survived.get('pid') == 4242, 'the contender fresh claim must survive a losing reclaim'
    os.remove(claim_path(store))
    # A claim matching the judged-stale timestamp is reclaimed; a vanished claim means
    # another contender won the reclaim (return True -> retry the O_EXCL create).
    with open(claim_path(store), 'w', encoding='utf-8') as f:
        json.dump({'schema': 'pwg.promote_claim.v1', 'claimed_at': stale_at}, f)
    assert a._reclaim(stale_at) is True and not os.path.exists(claim_path(store))
    assert a._reclaim(stale_at) is True, 'a vanished claim = contender already reclaimed'
    assert not [p for p in os.listdir(d) if '.reclaimed.' in p], 'reclaim residue left behind'
    print('promote_lock selftest OK')


if __name__ == '__main__':
    if '--selftest' in sys.argv[1:]:
        selftest()
    else:
        sys.exit('usage: python promote_lock.py --selftest')
