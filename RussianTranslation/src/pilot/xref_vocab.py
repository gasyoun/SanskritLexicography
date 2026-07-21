#!/usr/bin/env python
"""Single source for the PWG cross-reference / degenerate-passthrough vocabulary (H1425 W2).

A "degenerate" sense carries no translatable gloss — only cross-reference apparatus
("s. {#foo#}", "Vgl. {#bar#} fgg.", "u.", "Nachträge"). Both the RU generation lane
(gen_opt_harness2.degenerate_passthrough_card, which routes such a sense to a zero-LLM
pass-through) and the EN auditor (audit_window_en.xref_only, which flags a sense as never a
translation target) key off THIS SAME word set. It used to be an independently-authored copy
in each — "two independently-authored derivations is the C-01 drift class" (the same reason
portrait_key_iast was consolidated). This module is deliberately dependency-free so the EN
auditor can import it WITHOUT pulling in gen_opt_harness2's heavy pwg_mask/corpus_gate stack.
"""

# Lower-cased, punctuation-included tokens. A residue made entirely of these (after stripping
# <ls>/{#..#}/tags and with no {%..%} gloss wrapper) is cross-reference apparatus, not a gloss.
DEGENERATE_XREF_WORDS = frozenset({
    's', 'siehe', 's.', 'vgl', 'vgl.', 'vergl', 'vergl.', 'u', 'und',
    'ff', 'fgg', 'fg', 'fg.', 'fgg.', 'nachtrage', 'nachträge',
})
