#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H1650 — shared screening block + citation_tm evidence panel for review sheets.

MG (pramuc / H1649 / H1650): no card reaches a human without stating what was
screened, and every resolvable <ls> citation must show attested SA/RU or the
typed miss reason.

Usage from generators::

    from sheet_screening import screening_block, citation_evidence_panel, extract_ls

    panels.append(citation_evidence_panel(de_text))
    html = render_review_sheet(items, config, extras=True,
                               screening=screening_block(
                                   deterministic=n_a, lookup=n_b, agent=n_c,
                                   human=len(items),
                                   evidence_path="review/screening_h1650.md",
                                   rules=["citation_tm", "dup-id-vs-h178_da"]))
"""
from __future__ import annotations

import html as html_lib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

try:
    from citation_tm import lookup, _LS, _N_ATTR, _split_citation
except ImportError:  # pragma: no cover
    from src.citation_tm import lookup, _LS, _N_ATTR, _split_citation  # type: ignore


def esc(s):
    return html_lib.escape("" if s is None else str(s))


def screening_block(*, deterministic=0, lookup=0, agent=0, human=0,
                    evidence_path="review/screening_h1650.md",
                    rules=None):
    """csl-pyutil ≥0.8.0 required screening= mapping (H1649)."""
    return {
        "deterministic": int(deterministic),
        "lookup": int(lookup),
        "agent": int(agent),
        "human": int(human),
        "evidence_path": evidence_path,
        "rules": list(rules or []),
    }


def extract_ls(text):
    """Yield (prefix, locus, visible) for each distinct <ls> in text."""
    seen = set()
    for m in _LS.finditer(text or ""):
        nm = _N_ATTR.search(m.group(1) or "")
        visible = (m.group(2) or "").strip()
        parsed = _split_citation(nm.group(1) if nm else None, visible)
        if not parsed:
            continue
        key = parsed
        if key in seen:
            continue
        seen.add(key)
        yield parsed[0], parsed[1], visible


def citation_evidence_panel(*fields, heading="Citation TM (H1650)"):
    """Panel HTML: every <ls> with lookup status + SA/RU when available.

    Rights: never commit RU from hits into tracked files; gitignored sheets only.
    When corpus.db is absent, status is evidence_unavailable (honest).
    """
    lines = []
    n = 0
    for fld in fields:
        for prefix, locus, visible in extract_ls(fld):
            n += 1
            rec = lookup(prefix, locus)
            status = rec.get("status") or "?"
            reason = rec.get("reason") or ""
            cid = rec.get("canonical_id") or "—"
            sa = rec.get("sa") or rec.get("sanskrit") or ""
            ru = rec.get("ru") or ""
            # Only surface RU in the panel when present (generation-time consult);
            # never invent it.
            if status == "hit" and ru:
                body = (
                    f"<b>{esc(visible)}</b> → <code>{esc(cid)}</code><br>"
                    f"<span class='muted'>status=hit · {esc(rec.get('source') or '')}</span><br>"
                    f"<pre>SA: {esc(sa)}\nRU: {esc(ru)}</pre>"
                )
            else:
                detail = reason or status
                body = (
                    f"<b>{esc(visible)}</b> → <code>{esc(cid)}</code><br>"
                    f"<span class='muted'>status={esc(status)}"
                    f"{(' · ' + esc(detail)) if detail else ''}</span>"
                )
            lines.append(f"<div class='cite-ev'>{body}</div>")
    if not lines:
        return (heading,
                "<span class='muted'>No &lt;ls&gt; citations on this card "
                "(or none parseable).</span>")
    note = (
        f"<p class='muted'>{n} citation(s). "
        "Hit = reuse published RU (in-copyright — consult only). "
        "Miss reasons are typed (text-not-covered · locus-not-in-corpus · "
        "unmapped_locus_scheme · evidence_unavailable when corpus.db absent).</p>"
    )
    return (heading, note + "\n".join(lines))


def count_resolvable_citations(*fields):
    """How many distinct <ls> get a non-empty consult (any status)."""
    return sum(1 for fld in fields for _ in extract_ls(fld))
