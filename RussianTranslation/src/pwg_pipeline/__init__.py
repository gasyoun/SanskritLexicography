"""PWG translation control plane (H3714 Wave 1).

One package owns the PWG translation lifecycle: a transactional campaign
database, one shared paid-call kernel, pure audits, and coordinator-journaled
promotion.  Wave 1 is a strangler layer -- it wraps the proven Claude headless
engine and the PWG-TM/xAI route without rewriting prompts, gates, or canonical
data.

Layer documents live in ``RussianTranslation/docs/`` (PLAN / ARCHITECTURE /
IMPLEMENTATION / VERIFICATION ``_RussianTranslation_PWG_CONTROL_PLANE*``).
"""
from __future__ import annotations

SCHEMA_NAMESPACE = 'pwg.pipeline'
WAVE = 1
PACKAGE_VERSION = 'pwg_pipeline.v1'

__all__ = ['SCHEMA_NAMESPACE', 'WAVE', 'PACKAGE_VERSION']
