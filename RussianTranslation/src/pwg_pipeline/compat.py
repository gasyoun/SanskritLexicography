"""Compatibility shims for the legacy PWG-TM operator surface (step 7).

The strangler rule is that old commands keep working while the facade becomes
the only *supported* entry point.  This module owns that mapping in one place,
so an operator, a runbook and a test all read the same table:

``pwg_tm_generate.py``
    ``run``/``drain -> execute``, ``needed -> plan``,
    ``refill -> apply --intent refill``, ``reconcile -> audit``.

``pwg_tm_w2_run.py``
    ``--probe -> canary --provider deepseek``, and ``--all`` becomes an
    explicit ``plan``/``execute``/``audit`` sequence.

Wave 1 does **not** disable the old writer.  Per R3.5 that happens only after
both provider canaries, a production-equivalent replay, and two exact
shim-parity runs -- so :func:`writer_disabled` reports ``False`` here and the
gate that would flip it is spelled out in :data:`WRITER_DISABLE_CRITERION`.
"""
from __future__ import annotations

import warnings
from typing import Any, Mapping, Sequence

SCHEMA = 'pwg.pipeline.compat.v1'

# legacy module -> {legacy verb: facade invocation}
SHIM_MAP: dict[str, dict[str, tuple[str, ...]]] = {
    'pwg_tm_generate.py': {
        'run': ('execute',),
        'drain': ('execute',),
        'needed': ('plan',),
        'refill': ('apply', '--intent', 'refill'),
        'reconcile': ('audit',),
    },
    'pwg_tm_w2_run.py': {
        '--probe': ('canary', '--provider', 'deepseek'),
        '--all': ('plan', 'execute', 'audit'),
    },
}

# Legacy verbs that are offline-only helpers and stay exactly as they are.
PRESERVED_OFFLINE: dict[str, tuple[str, ...]] = {
    'pwg_tm_generate.py': ('extract', '--verify', 'selftest'),
    'pwg_tm_w2_run.py': ('--gold-limit', '--n-per-class'),
}

# Legacy verbs whose *live/mutating* path must refuse rather than shim.
REFUSED_DIRECT_MUTATION: dict[str, tuple[str, ...]] = {
    'pwg_tm_generate.py': ('refill',),
}

WRITER_DISABLE_CRITERION = (
    'two non-promotable provider canaries (one xAI, one DeepSeek), one '
    'production-equivalent replay, and two exact shim-parity runs'
)


class ShimRefusal(RuntimeError):
    """A legacy live/refill path was invoked directly after the cutover."""


def facade_invocation(module: str, verb: str) -> tuple[str, ...]:
    """The facade command a legacy verb maps to."""
    table = SHIM_MAP.get(module)
    if table is None:
        raise ShimRefusal('no shim table for %r' % (module,))
    if verb not in table:
        raise ShimRefusal('%s has no facade mapping for %r' % (module, verb))
    return table[verb]


def deprecation_notice(module: str, verb: str) -> str:
    target = ' '.join(facade_invocation(module, verb))
    return ('%s %s is a Wave-1 compatibility shim; the supported entry point is'
            ' `python -m pwg_pipeline %s`' % (module, verb, target))


def warn_deprecated(module: str, verb: str) -> str:
    """Emit the deprecation notice and return it (tests assert on the text)."""
    message = deprecation_notice(module, verb)
    warnings.warn(message, DeprecationWarning, stacklevel=2)
    return message


def writer_disabled() -> bool:
    """Whether the old PWG-TM writer is disabled.  False for the whole of Wave 1."""
    return False


def shim_parity(legacy: Mapping[str, Any],
                facade: Mapping[str, Any]) -> dict[str, Any]:
    """Compare a legacy invocation result with the facade's, key by key."""
    keys = sorted(set(legacy) | set(facade))
    mismatches = [key for key in keys if legacy.get(key) != facade.get(key)]
    return {
        'schema': 'pwg.pipeline.shim_parity.v1',
        'compared_keys': len(keys),
        'mismatches': mismatches,
        'exact': not mismatches,
    }


def coverage() -> dict[str, Any]:
    """Every legacy live verb, and what it maps to.  Used by the compat test."""
    return {
        'schema': SCHEMA,
        'modules': sorted(SHIM_MAP),
        'mapped_verbs': {module: sorted(table)
                         for module, table in sorted(SHIM_MAP.items())},
        'preserved_offline': {module: list(verbs) for module, verbs
                              in sorted(PRESERVED_OFFLINE.items())},
        'refused_direct_mutation': {module: list(verbs) for module, verbs
                                    in sorted(REFUSED_DIRECT_MUTATION.items())},
        'writer_disabled': writer_disabled(),
        'writer_disable_criterion': WRITER_DISABLE_CRITERION,
    }


def describe(argv: Sequence[str]) -> dict[str, Any]:
    """Map a legacy argv onto its facade invocation, for a runbook or a test."""
    if not argv:
        raise ShimRefusal('empty legacy invocation')
    module = argv[0]
    verb = argv[1] if len(argv) > 1 else ''
    return {
        'module': module,
        'legacy_verb': verb,
        'facade': list(facade_invocation(module, verb)),
        'notice': deprecation_notice(module, verb),
    }


__all__ = [
    'SCHEMA', 'SHIM_MAP', 'PRESERVED_OFFLINE', 'REFUSED_DIRECT_MUTATION',
    'WRITER_DISABLE_CRITERION', 'ShimRefusal', 'facade_invocation',
    'deprecation_notice', 'warn_deprecated', 'writer_disabled', 'shim_parity',
    'coverage', 'describe',
]
