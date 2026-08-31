#!/usr/bin/env python
"""The gate-evidence contract: a PASS must name what it checked (W1, H3748).

[#1803](https://github.com/gasyoun/SanskritLexicography/issues/1803) found the same
shape repeated across nine gates: **a check whose PASS is indistinguishable from
"nothing was checked"**. A gate that reads an absent directory, an empty file or a
zero-row report prints its green line and exits 0, and no consumer downstream can
tell that apart from a gate that examined 120,000 rows and found nothing wrong.

This module is the one structural answer, rather than nine local patches. A gate
builds a ``GateEvidence`` record while it works:

    ev = GateEvidence('launch_ledger')
    ev.add_input('ledger', path=LEDGER_MD, units=len(entries))
    ev.add_predicate('required_fields', evaluations=len(entries), hits=len(violations))
    ev.set_verdict('pass' if not violations else 'fail')
    ev.assert_nonvacuous()          # a zero-work PASS raises here
    ev.emit(sidecar_for(report_path))

Three guarantees, and nothing else:

1. **Inputs are named and hashed.** ``inputs_examined`` carries, per input, the
   path, whether it existed, its byte size, its sha256 and how many *units* (rows,
   entries, cards, elements) the gate actually pulled out of it. A 0-byte input
   that a predicate nevertheless "accepted" is visible in the record even when the
   predicate itself never opened the file.
2. **Predicates are counted.** ``predicates_evaluated`` carries, per predicate, how
   many units it was applied to and how many hits (violations) it found. Zero
   *hits* is a fine PASS; zero *evaluations* is not.
3. **A vacuous PASS is a hard FAIL.** ``assert_nonvacuous()`` raises
   :class:`VacuousGateError` when the verdict is a pass and either no input unit
   was examined at all, or every predicate ran zero evaluations — unless the gate
   has *declared* that emptiness legitimate.

## Legitimate emptiness is declared, never silent

Some gates have real input classes that are legitimately empty: a launch-failure
ledger with no entries is a *good* day, not a broken gate. The W1 spike enumerated
those classes per gate up front (:data:`LEGITIMATE_EMPTY`, and the prose sibling
``docs/SPIKE_PWG_GATE_EVIDENCE_LEGITIMATE_EMPTY_CLASSES_31-08-2026.md``). A gate
reaching one of them calls::

    ev.declare_expected_empty('no_promotions_today', 'a day with zero auto-promotions')

which keeps the PASS but stamps ``vacuity='declared_empty'`` plus the reason into
the sidecar. The difference from the pre-W1 world is the whole point: the emptiness
is now *asserted by the gate author, in advance, with a name* — never inferred from
silence. An undeclared name raises, so the declaration cannot be improvised at the
call site to dodge a red.

## Sidecar

``emit()`` writes one JSON sidecar next to the gate's existing report
(``<report>.evidence.json`` via :func:`sidecar_for`). Consumers — ``window_selftest``,
``audit_store_gates``, the CI RussianTranslation-gates job — read it; after W1 a
**missing** sidecar means the gate did not run the contract, and that is itself a
FAIL (:func:`require_sidecar`).

Selftest: ``python src/pilot/gate_evidence.py --selftest``
"""
import argparse
import datetime as _dt
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SCHEMA = 'pwg.gate_evidence.v1'
SIDECAR_SUFFIX = '.evidence.json'

#: Verdicts a gate may record. ``inconclusive`` exists because the pre-existing
#: contract in ``spot_check_daily``/``lane_spotcheck_tick`` already distinguishes
#: "could not judge" from "clean", and this record must not flatten that.
VERDICTS = ('pass', 'fail', 'inconclusive')

#: W1 spike output — the legitimate-empty input classes, enumerated per gate BEFORE
#: ``assert_nonvacuous`` was switched on, so a gate cannot invent an excuse at the
#: call site. Prose rationale (why each is legitimate, and what would make it stop
#: being legitimate) lives in
#: docs/SPIKE_PWG_GATE_EVIDENCE_LEGITIMATE_EMPTY_CLASSES_31-08-2026.md.
#:
#: An empty tuple is a deliberate claim, not an omission: that gate has NO
#: legitimately-empty input class, so any emptiness there is a defect.
LEGITIMATE_EMPTY = {
    # C2-2 — freshness of R4.1 surveillance reports. No legitimately-empty class: with
    # no candidate report this gate does not PASS on emptiness, it goes INCONCLUSIVE
    # (its own family's contract — see lane_spotcheck_tick's exit-code docstring), and
    # nonstop_scheduler then fails closed on auto-promote.
    'lane_spotcheck_freshness': (),
    # C6-01 — human gold precision + double-review agreement.
    'gold_agreement': (
        'no_double_reviewed_items',   # single-review corpus: kappa is n/a, precision still real
    ),
    # C6-05 — daily R4.1 spot check over what landed in the store.
    'spot_check_daily': (
        'no_promotions_for_date',  # a day with zero auto-promotions: nothing to sample
    ),
    # C3-4 — prompt-rule phrase audit over the committed template(s).
    'prompt_rule_audit': (),       # the template is committed; an absent one is a defect
    # C2-5 — external-dictionary coverage census.
    'corpus_gate_coverage': (),    # the PWG index is committed; zero scanned keys is a defect
    # C8-4 — launch-failure ledger completeness.
    'launch_ledger': (
        'no_launch_failures_recorded',   # an empty ledger is a good history, not a dead gate
        'no_runlog_launch_headings',     # --since window with no launch heading to cross-check
    ),
    # C8-3 — duplicated changelog entries.
    'changelog_duplicate_bullets': (
        'no_changelog_in_repo',    # a repo with no CHANGELOG.md has nothing to duplicate
    ),
    # C8-7 — run-observability census over the append-only events log.
    'run_observability_census': (
        'no_events_logged',        # a fresh box before the first run
    ),
    # C3-1 — prompt-compiler golden reconstruction.
    'prompt_compiler_golden': (),  # goldens are written by the selftest itself; never empty
    # G9 (#1798) — released interop artifact validity.
    'interop_validity': (),        # a release with zero entries is never valid
}


def utc_now():
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


class VacuousGateError(AssertionError):
    """A gate claimed PASS without examining anything (#1803)."""


class MissingEvidenceError(AssertionError):
    """A gate ran but left no evidence sidecar — after W1 that is a FAIL."""


def sha256_file(path, chunk=1024 * 1024):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(chunk), b''):
            h.update(block)
    return h.hexdigest()


def sha256_bytes(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def sidecar_for(report_path):
    """The sidecar path for a gate whose report is ``report_path``."""
    return str(report_path) + SIDECAR_SUFFIX


#: Where gates that have no report file of their own put their sidecar. Under
#: ``src/pilot/output/`` (gitignored telemetry, never a tracked artifact), and
#: redirectable so a selftest or a CI step can point the whole family at scratch.
EVIDENCE_DIR_ENV = 'PWG_GATE_EVIDENCE_DIR'
_DEFAULT_EVIDENCE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'output', 'gate_evidence')


def evidence_dir():
    return os.environ.get(EVIDENCE_DIR_ENV) or _DEFAULT_EVIDENCE_DIR


def default_sidecar(gate_id):
    """Sidecar path for a gate whose verdict is an exit code, not a report file."""
    return os.path.join(evidence_dir(), gate_id + SIDECAR_SUFFIX)


class GateEvidence(object):
    """What one gate examined, what it evaluated, and what it concluded."""

    def __init__(self, gate_id, description=None):
        if gate_id not in LEGITIMATE_EMPTY:
            raise KeyError(
                'gate_id %r is not registered in LEGITIMATE_EMPTY. Register it with its '
                'legitimate-empty classes (an empty tuple is a valid, deliberate claim) '
                'so the spike stays the single list of what may legally be empty.' % gate_id)
        self.gate_id = gate_id
        self.description = description
        self.started_at = utc_now()
        self.inputs = []
        self.predicates = []
        self.expected_empty = []
        self.warnings = []
        self.notes = {}
        self.verdict = None

    # -- inputs ---------------------------------------------------------------

    def add_input(self, name, path=None, units=0, content=None, exists=None):
        """Record one examined input.

        ``units`` is how many *units the gate actually pulled out* — rows parsed,
        entries found, elements matched — not the file's line count. ``content``
        hashes an in-memory payload for inputs that are not files.
        """
        record = {'name': name, 'units': int(units)}
        if path is not None:
            path = str(path)
            present = os.path.exists(path) if exists is None else bool(exists)
            record['path'] = path
            record['exists'] = present
            if present and os.path.isfile(path):
                record['size_bytes'] = os.path.getsize(path)
                record['sha256'] = sha256_file(path)
                if record['size_bytes'] == 0:
                    # Not a failure by itself — but a predicate that "accepted" a
                    # 0-byte input (C2-2's mtime-only freshness check is exactly this)
                    # can no longer hide that fact behind a green line.
                    self.warnings.append(
                        '%s: examined a 0-byte input (%s)' % (name, os.path.basename(path)))
            elif present:
                record['size_bytes'] = None
                record['sha256'] = None
            else:
                record['size_bytes'] = None
                record['sha256'] = None
        elif exists is not None:
            record['exists'] = bool(exists)
        if content is not None:
            record['sha256'] = sha256_bytes(content)
            record['size_bytes'] = len(content if isinstance(content, bytes)
                                       else content.encode('utf-8'))
        self.inputs.append(record)
        return record

    @property
    def units_examined(self):
        return sum(i['units'] for i in self.inputs)

    @property
    def inputs_examined(self):
        """Inputs that existed AND yielded at least one unit."""
        return sum(1 for i in self.inputs
                   if i.get('exists', True) and i['units'] > 0)

    # -- predicates -----------------------------------------------------------

    def add_predicate(self, name, evaluations, hits=0, detail=None):
        """Record one predicate: how many units it ran over, how many it flagged."""
        record = {'name': name, 'evaluations': int(evaluations), 'hits': int(hits)}
        if detail is not None:
            record['detail'] = detail
        self.predicates.append(record)
        return record

    @property
    def evaluations(self):
        return sum(p['evaluations'] for p in self.predicates)

    @property
    def hits(self):
        return sum(p['hits'] for p in self.predicates)

    # -- declared emptiness ---------------------------------------------------

    def declare_expected_empty(self, name, reason):
        """Declare that this run legitimately examined nothing, by pre-registered name."""
        allowed = LEGITIMATE_EMPTY[self.gate_id]
        if name not in allowed:
            raise KeyError(
                '%s: %r is not a declared legitimate-empty class for this gate '
                '(declared: %s). Emptiness a gate did not anticipate is a FAIL, not a '
                'silence — add it to LEGITIMATE_EMPTY with its rationale in the spike '
                'doc, or fix the input.'
                % (self.gate_id, name, ', '.join(allowed) or 'none — this gate has no '
                   'legitimately-empty input class'))
        self.expected_empty.append({'class': name, 'reason': reason})

    # -- verdict --------------------------------------------------------------

    def set_verdict(self, verdict):
        if verdict not in VERDICTS:
            raise ValueError('verdict must be one of %s, got %r' % (VERDICTS, verdict))
        self.verdict = verdict
        return verdict

    def note(self, key, value):
        self.notes[key] = value

    @property
    def vacuity(self):
        """``'worked'`` | ``'declared_empty'`` | ``'vacuous'``."""
        worked = self.inputs_examined > 0 and self.evaluations > 0
        if worked:
            return 'worked'
        return 'declared_empty' if self.expected_empty else 'vacuous'

    def assert_nonvacuous(self):
        """Turn a zero-work PASS into a hard FAIL.

        Raises unless the gate examined at least one input unit AND ran at least one
        predicate evaluation — or declared the emptiness legitimate up front. Only a
        *pass* is policed: a gate that already says fail/inconclusive is telling the
        truth about having found nothing.
        """
        if self.verdict is None:
            raise VacuousGateError(
                '%s: set_verdict() must be called before assert_nonvacuous()' % self.gate_id)
        if self.verdict != 'pass':
            return self
        if self.vacuity == 'vacuous':
            raise VacuousGateError(
                '%s: PASS is vacuous — %d input(s) with content out of %d named, %d '
                'predicate evaluation(s) over %d predicate(s). A gate that examined '
                'nothing has not passed; it has not run (#1803). Either point it at real '
                'input, or declare the emptiness with declare_expected_empty() using one '
                'of: %s'
                % (self.gate_id, self.inputs_examined, len(self.inputs),
                   self.evaluations, len(self.predicates),
                   ', '.join(LEGITIMATE_EMPTY[self.gate_id]) or 'none (this gate has no '
                   'legitimately-empty input class)'))
        return self

    # -- serialization --------------------------------------------------------

    def to_dict(self):
        return {
            'schema': SCHEMA,
            'gate_id': self.gate_id,
            'description': self.description,
            'started_at': self.started_at,
            'emitted_at': utc_now(),
            'verdict': self.verdict,
            'vacuity': self.vacuity,
            'inputs_examined': self.inputs,
            'input_count': len(self.inputs),
            'inputs_with_content': self.inputs_examined,
            'units_examined': self.units_examined,
            'predicates_evaluated': self.predicates,
            'evaluations': self.evaluations,
            'hits': self.hits,
            'expected_empty': self.expected_empty,
            'warnings': self.warnings,
            'notes': self.notes,
        }

    def emit(self, path):
        """Write the JSON sidecar atomically. Returns the path written."""
        path = str(path)
        parent = os.path.dirname(os.path.abspath(path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        tmp = '%s.tmp.%d' % (path, os.getpid())
        with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=1, sort_keys=False)
            f.write('\n')
        os.replace(tmp, path)
        return path

    def summary(self):
        return ('%s: %s (%s) — %d input(s)/%d unit(s), %d evaluation(s), %d hit(s)'
                % (self.gate_id, (self.verdict or 'no-verdict').upper(), self.vacuity,
                   len(self.inputs), self.units_examined, self.evaluations, self.hits))


def load_sidecar(path):
    with open(path, encoding='utf-8') as f:
        payload = json.load(f)
    if payload.get('schema') != SCHEMA:
        raise MissingEvidenceError('%s: not a %s sidecar (schema=%r)'
                                   % (path, SCHEMA, payload.get('schema')))
    return payload


def require_sidecar(path, gate_id=None, verdict='pass'):
    """Consumer side: a gate with no sidecar did not run the contract — FAIL.

    Returns the loaded payload. Raises :class:`MissingEvidenceError` when the
    sidecar is absent, when it names a different gate, when the verdict is not the
    expected one, or when it records a vacuous run.
    """
    if not os.path.exists(path):
        raise MissingEvidenceError(
            'no gate-evidence sidecar at %s — after W1 a gate that leaves no evidence '
            'has not passed, it has not run (#1803)' % path)
    payload = load_sidecar(path)
    if gate_id is not None and payload.get('gate_id') != gate_id:
        raise MissingEvidenceError('%s: expected gate_id %r, found %r'
                                   % (path, gate_id, payload.get('gate_id')))
    if verdict is not None and payload.get('verdict') != verdict:
        raise MissingEvidenceError('%s: verdict is %r, expected %r'
                                   % (path, payload.get('verdict'), verdict))
    if payload.get('vacuity') == 'vacuous':
        raise MissingEvidenceError('%s: sidecar records a vacuous run' % path)
    return payload


# --------------------------------------------------------------------------- #
# selftest
# --------------------------------------------------------------------------- #

def _stub_gate_without_contract(rows):
    """The pre-W1 shape: PASS is indistinguishable from 'nothing was checked'."""
    violations = [r for r in rows if not r.get('ok')]
    return 0 if not violations else 1


def _stub_gate_with_contract(rows, path=None):
    ev = GateEvidence('launch_ledger', 'stub gate for the W1 RED-pin')
    ev.add_input('rows', path=path, units=len(rows))
    violations = [r for r in rows if not r.get('ok')]
    ev.add_predicate('ok_flag', evaluations=len(rows), hits=len(violations))
    ev.set_verdict('pass' if not violations else 'fail')
    ev.assert_nonvacuous()
    return ev


def selftest():
    import tempfile

    # (1) THE RED PIN. The pre-W1 stub returns 0 — a clean PASS — over zero rows.
    #     That is the whole defect class of #1803 reproduced in four lines.
    assert _stub_gate_without_contract([]) == 0, 'stub gate should be vacuously green'
    assert _stub_gate_without_contract([{'ok': True}]) == 0
    assert _stub_gate_without_contract([{'ok': False}]) == 1

    # ...and the same gate built THROUGH the contract refuses the vacuous PASS.
    try:
        _stub_gate_with_contract([])
    except VacuousGateError as exc:
        assert 'vacuous' in str(exc), exc
    else:
        raise AssertionError('a zero-input PASS must raise VacuousGateError')

    # A real PASS over real rows still passes, and carries its counts.
    ev = _stub_gate_with_contract([{'ok': True}, {'ok': True}])
    assert ev.verdict == 'pass' and ev.vacuity == 'worked'
    assert ev.units_examined == 2 and ev.evaluations == 2 and ev.hits == 0

    # A FAIL is never policed for vacuity — a gate saying "fail" is already honest.
    ev_fail = GateEvidence('launch_ledger')
    ev_fail.set_verdict('fail')
    ev_fail.assert_nonvacuous()
    ev_inc = GateEvidence('launch_ledger')
    ev_inc.set_verdict('inconclusive')
    ev_inc.assert_nonvacuous()

    # (2) Declared emptiness keeps the PASS, but stamps the record.
    ev_empty = GateEvidence('launch_ledger')
    ev_empty.add_input('ledger', units=0)
    ev_empty.add_predicate('required_fields', evaluations=0)
    ev_empty.set_verdict('pass')
    ev_empty.declare_expected_empty('no_launch_failures_recorded', 'clean history')
    ev_empty.assert_nonvacuous()
    assert ev_empty.vacuity == 'declared_empty'
    assert ev_empty.to_dict()['expected_empty'][0]['class'] == 'no_launch_failures_recorded'

    # ...and an UNDECLARED excuse cannot be improvised at the call site.
    try:
        ev_empty.declare_expected_empty('because_reasons', 'nope')
    except KeyError as exc:
        assert 'not a declared legitimate-empty class' in str(exc), exc
    else:
        raise AssertionError('an unregistered empty class must raise')

    # A gate whose registry entry is an empty tuple has NO legal emptiness at all.
    ev_none = GateEvidence('interop_validity')
    ev_none.set_verdict('pass')
    try:
        ev_none.declare_expected_empty('anything', 'nope')
    except KeyError:
        pass
    else:
        raise AssertionError('a gate with no legitimate-empty class must refuse one')

    # An unregistered gate_id cannot construct a record at all.
    try:
        GateEvidence('gate_that_never_did_the_spike')
    except KeyError as exc:
        assert 'LEGITIMATE_EMPTY' in str(exc), exc
    else:
        raise AssertionError('an unregistered gate_id must raise')

    # (3) Inputs are hashed, 0-byte inputs are surfaced, sidecars round-trip.
    with tempfile.TemporaryDirectory() as td:
        real = os.path.join(td, 'report.json')
        with open(real, 'w', encoding='utf-8', newline='\n') as f:
            f.write('{"rows": 3}\n')
        empty = os.path.join(td, 'empty.json')
        open(empty, 'w', encoding='utf-8').close()
        absent = os.path.join(td, 'nope.json')

        ev2 = GateEvidence('launch_ledger', 'hashing')
        rec = ev2.add_input('report', path=real, units=3)
        assert rec['exists'] and rec['size_bytes'] == 12
        assert rec['sha256'] == sha256_file(real)
        ev2.add_input('empty', path=empty, units=0)
        assert any('0-byte' in w for w in ev2.warnings), ev2.warnings
        miss = ev2.add_input('absent', path=absent, units=0)
        assert miss['exists'] is False and miss['sha256'] is None
        ev2.add_input('in_memory', content='abc', units=1)
        assert ev2.inputs[-1]['sha256'] == sha256_bytes('abc')
        ev2.add_predicate('shape', evaluations=4, hits=1)
        ev2.set_verdict('pass')
        ev2.assert_nonvacuous()

        side = sidecar_for(real)
        assert side == real + SIDECAR_SUFFIX
        written = ev2.emit(side)
        payload = load_sidecar(written)
        assert payload['gate_id'] == 'launch_ledger'
        assert payload['units_examined'] == 4 and payload['inputs_with_content'] == 2
        assert payload['hits'] == 1 and payload['vacuity'] == 'worked'
        assert not os.path.exists(written + '.tmp.%d' % os.getpid())

        # (4) Consumer side: present sidecar OK, absent sidecar FAILS.
        assert require_sidecar(side, gate_id='launch_ledger')['verdict'] == 'pass'
        try:
            require_sidecar(sidecar_for(absent), gate_id='launch_ledger')
        except MissingEvidenceError as exc:
            assert 'no gate-evidence sidecar' in str(exc), exc
        else:
            raise AssertionError('a missing sidecar must FAIL for the consumer')
        try:
            require_sidecar(side, gate_id='interop_validity')
        except MissingEvidenceError:
            pass
        else:
            raise AssertionError('a sidecar for another gate must FAIL')
        try:
            require_sidecar(side, gate_id='launch_ledger', verdict='fail')
        except MissingEvidenceError:
            pass
        else:
            raise AssertionError('a verdict mismatch must FAIL')

    print('gate_evidence selftest: PASS (RED-pin — the contract-free stub is green over '
          'zero rows and the contract-carrying one raises; declared-empty keeps the PASS '
          'and an undeclared excuse cannot; inputs hashed incl. 0-byte + absent; sidecar '
          'round-trip; a missing/foreign/wrong-verdict sidecar FAILS the consumer)')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--show', metavar='SIDECAR', help='pretty-print one evidence sidecar')
    ap.add_argument('--registry', action='store_true',
                    help='print the legitimate-empty registry (the W1 spike output)')
    ap.add_argument('--require', action='append', metavar='GATE_ID[=PATH]', default=[],
                    help='CI consumer check: fail unless this gate left a passing, '
                         'non-vacuous sidecar. PATH defaults to the gate default_sidecar.')
    ap.add_argument('--require-verdict', default='pass',
                    help='verdict --require expects (default: pass)')
    args = ap.parse_args(argv)
    if args.require:
        # ARCHITECTURE §1: after W1, a missing sidecar means the gate did not run the
        # contract — itself a FAIL. This is the CI half of that sentence.
        failures = []
        for spec in args.require:
            gate_id, _, path = spec.partition('=')
            path = path or default_sidecar(gate_id)
            try:
                payload = require_sidecar(path, gate_id=gate_id,
                                          verdict=args.require_verdict)
            except (MissingEvidenceError, KeyError) as exc:
                failures.append(str(exc))
            else:
                print('evidence OK  %-30s %s (%d unit(s), %d evaluation(s), %d hit(s))'
                      % (gate_id, payload['vacuity'], payload['units_examined'],
                         payload['evaluations'], payload['hits']))
        for line in failures:
            print('MISSING GATE EVIDENCE: %s' % line, file=sys.stderr)
        return 1 if failures else 0
    if args.show:
        print(json.dumps(load_sidecar(args.show), ensure_ascii=False, indent=2))
        return 0
    if args.registry:
        for gate_id in sorted(LEGITIMATE_EMPTY):
            classes = LEGITIMATE_EMPTY[gate_id]
            print('%-30s %s' % (gate_id, ', '.join(classes) if classes
                                else '(none — no legitimately-empty input class)'))
        return 0
    return selftest()


if __name__ == '__main__':
    sys.exit(main())
