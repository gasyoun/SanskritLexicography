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

import re as _re

# Lower-cased, punctuation-included tokens. A residue made entirely of these (after stripping
# <ls>/{#..#}/tags and with no {%..%} gloss wrapper) is cross-reference apparatus, not a gloss.
DEGENERATE_XREF_WORDS = frozenset({
    's', 'siehe', 's.', 'vgl', 'vgl.', 'vergl', 'vergl.', 'u', 'und',
    'ff', 'fgg', 'fg', 'fg.', 'fgg.', 'nachtrage', 'nachträge',
})


# --------------------------------------------------------------- H3658: RU rendering
# A degenerate xref stub used to be emitted with an EMPTY russian field (H1422 P3: "there is
# nothing here to translate, so the target field stays empty rather than silently carrying
# verbatim German"). The consequence was that EVERY such card failed the window audit on
# `empty_russian` + `dropped_sanskrit_span` and landed on requeue.defect.keys.txt — permanently
# unpromotable, and (because the defect guard is all-or-nothing) able to block a whole batch.
# `pa_tin` in the H3654 window is exactly that case.
#
# The apparatus IS renderable without inventing gloss content, because the classifier has
# already proven the residue is nothing but this closed vocabulary:
#   * `{#...#}` Sanskrit spans and `<ls>`/`<hom>` markup are never translated in either column,
#     so they are copied verbatim — which is also what restores the dropped Sanskrit spans;
#   * an `<ab>` token stays verbatim: the article site resolves it to Russian at RENDER time
#     via pwg_ab_ru.RU_MAP (`s. u.` -> `см.`, MG 10-07-2026, ABBREVIATIONS_RU.md §1), and
#     rewriting it here would double-translate it;
#   * only a BARE, untagged apparatus word is rewritten, using the map below.
# So no German survives into the Russian column and no gloss content is fabricated.

# Bare (untagged) German apparatus -> Russian. Phrases are matched BEFORE single words, because
# `s. u.` is "siehe unter" (-> «см.»), while a standalone `u.` is "und" (-> «и»); mapping word
# by word would render "s. u." as «см. и». Keys are lower-cased and matched on whole tokens.
DEGENERATE_XREF_RU_PHRASES = (
    ('s. u. d.', 'см.'),
    ('s. u.', 'см.'),
    ('s. d.', 'см.'),
    ('s. v.', 'см.'),
)

DEGENERATE_XREF_RU_WORDS = {
    's': 'см.', 's.': 'см.', 'siehe': 'см.',
    'vgl': 'ср.', 'vgl.': 'ср.', 'vergl': 'ср.', 'vergl.': 'ср.',
    'u': 'и', 'und': 'и',
    'ff': 'и сл.', 'fg': 'и сл.', 'fg.': 'и сл.', 'fgg': 'и сл.', 'fgg.': 'и сл.',
    'nachtrage': 'Дополнения', 'nachträge': 'Дополнения',
}

# Whole tagged REGIONS are protected, not just the tags: the content of an <ab> is the German
# token the article site itself resolves to Russian (pwg_ab_ru.RU_MAP), so rewriting it here
# would double-translate it; <ls> is a source reference and <hom> a homonym number.
_XREF_PROTECTED = _re.compile(
    r'(\{#.*?#\}|\{%.*?%\}'
    r'|<ab\b[^>]*>.*?</ab>|<ls\b[^>]*>.*?</ls>|<hom\b[^>]*>.*?</hom>'
    r'|<[^>]+>)', _re.S)
_XREF_WORD = _re.compile(r'[A-Za-zÄÖÜäöüß]+\.?')


def render_xref_ru(body):
    """Render a degenerate cross-reference stub's German body as Russian apparatus.

    Returns None when some residue word is NOT in the closed vocabulary — the caller must then
    fall back to the H1422 P3 empty field rather than leak an unrecognised German word into the
    Russian column. Protected regions (`{#..#}` spans, `{%..%}` wrappers, and any tag, `<ab>`
    included) are copied byte-for-byte.
    """
    if not body:
        return None
    out, ok = [], True

    def rewrite(chunk):
        pieces, idx = [], 0
        low = chunk.lower()
        while idx < len(chunk):
            for phrase, ru in DEGENERATE_XREF_RU_PHRASES:
                if low.startswith(phrase, idx):
                    pieces.append(ru)
                    idx += len(phrase)
                    break
            else:
                m = _XREF_WORD.match(chunk, idx)
                if m:
                    word = m.group(0)
                    ru = DEGENERATE_XREF_RU_WORDS.get(word.lower())
                    if ru is None:
                        ru = DEGENERATE_XREF_RU_WORDS.get(word.lower().strip('.:,;()'))
                    if ru is None:
                        return None
                    pieces.append(ru)
                    idx = m.end()
                else:
                    pieces.append(chunk[idx])
                    idx += 1
        return ''.join(pieces)

    for part in _XREF_PROTECTED.split(body):
        if not part:
            continue
        if _XREF_PROTECTED.fullmatch(part):
            out.append(part)                      # span / wrapper / tag -> verbatim
            continue
        done = rewrite(part)
        if done is None:
            ok = False
            break
        out.append(done)
    if not ok:
        return None
    text = ''.join(out).strip()
    return text or None


def selftest():
    """H3658. Fixtures are real PWG bodies, `pa_tin` first (the H3654 window's only
    degenerate_passthrough, and the card whose empty russian field put it on
    requeue.defect.keys.txt as `empty_russian` + `dropped_sanskrit_span`)."""
    ok = [0, 0]

    def check(name, cond):
        ok[1] += 1
        ok[0] += bool(cond)
        print('  %-56s %s' % (name, 'ok' if cond else 'FAIL'))

    # 1. pa_tin: every token is protected, so the RU apparatus equals the German one.
    body = '{#paTin#}\u00a6 <ab>s. u.</ab> <hom>2.</hom> {#paT#}.'
    got = render_xref_ru(body)
    check('pa_tin renders (not empty)', got)
    check('pa_tin keeps BOTH Sanskrit spans',
          got and '{#paTin#}' in got and '{#paT#}' in got)
    check('pa_tin leaves the <ab> token for the site to resolve',
          got and '<ab>s. u.</ab>' in got)
    check('pa_tin keeps the homonym number', got and '<hom>2.</hom>' in got)

    # 2. a BARE apparatus word is rewritten; `s. u.` as a phrase must not become «см. и».
    got = render_xref_ru('Vgl. {#agni#} und {#vAyu#}.')
    check('bare Vgl. -> ср.', got == '\u0441\u0440. {#agni#} \u0438 {#vAyu#}.')
    got = render_xref_ru('s. u. {#paT#}.')
    check('bare phrase `s. u.` -> см. (never «см. и»)',
          got == '\u0441\u043c. {#paT#}.')
    check('bare fgg. -> и сл.',
          render_xref_ru('{#a#} fgg.') == '{#a#} \u0438 \u0441\u043b.')

    # 3. fail closed: an unknown German word must return None so the caller keeps the
    #    H1422 P3 empty field rather than leaking German into the Russian column.
    check('unknown German word -> None (fail closed)',
          render_xref_ru('Bedeutung {#agni#}') is None)
    check('empty body -> None', render_xref_ru('') is None)
    check('markup-only body -> the markup, never None-by-accident',
          render_xref_ru('{#agni#}') == '{#agni#}')

    # 4. every bare word this module claims to render is one the CLASSIFIER admits, and
    #    vice versa — otherwise a stub passes the classifier and then renders as None.
    stripped = set(w.rstrip('.') for w in DEGENERATE_XREF_RU_WORDS)
    check('RU map covers the whole classifier vocabulary',
          all(w.rstrip('.') in stripped for w in DEGENERATE_XREF_WORDS))

    # 5. drift guard against the site-side map (lazy import: this module stays
    #    dependency-free for the EN auditor).
    try:
        import os as _os, sys as _sys                          # noqa: PLC0415
        _src = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
        if _src not in _sys.path:
            _sys.path.insert(0, _src)
        from pwg_ab_ru import RU_MAP                            # noqa: PLC0415
    except Exception as exc:                                  # pragma: no cover
        print('  (pwg_ab_ru unavailable, drift guard skipped: %s)' % exc)
    else:
        shared = [(de, ru) for de, ru in DEGENERATE_XREF_RU_PHRASES if de in RU_MAP]
        check('phrase map agrees with pwg_ab_ru.RU_MAP (%d shared)' % len(shared),
              all(RU_MAP[de] == ru for de, ru in shared))

    print('xref_vocab selftest: %d/%d' % (ok[0], ok[1]))
    return 0 if ok[0] == ok[1] else 1


if __name__ == '__main__':
    import sys as _sys
    _sys.stdout.reconfigure(encoding='utf-8')
    _sys.exit(selftest())
