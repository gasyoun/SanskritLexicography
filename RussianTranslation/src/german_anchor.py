#!/usr/bin/env python
r"""H858 Part B — source-anchored repair of `{Tn}` spans dropped from a card's `german` echo.

THE DEFECT
----------
The model is handed a MASKED German skeleton (`{Tn}` = one untranslatable span: an `<ls>`
citation, a `{#…#}` Sanskrit span, a stray tag) and must echo it back verbatim in each
sense's `german` while producing only the translation field. When it drops one `{Tn}` from
that echo, the restored card carries fewer `<ls>`/`{#` occurrences than the source, and the
fidelity guard (`headless_worker.count_card` / the JS `countOf`) nulls the WHOLE card —
every paid call on it is lost and the key is requeued to fail the same way.

Measured on the `no_pwg` windows (H858, 13-07-2026): `asaMskfta` `avyAhata` `avyagra`
`darvI` `glAna` `hasita` all nulled on `{# 0/1`, `1/2`, `1/3` — six of the seven residual
nulls in `no_pwg_w10` (H1283), and a `--max-wide` requeue provably cannot fix them: the
drop is a property of the echo, not of transport.

THE REPAIR
----------
The dropped span is not lost information — it is sitting in the source skeleton, and the
tokens the model DID echo say exactly where it belongs. So, pre-restore:

    want   = the skeleton's `{Tn}` in source order          (unique by construction: `pwg_mask.mask`
                                                             hands every span its own index)
    got    = the `{Tn}` in `sense.german`, document order
    missing= want - got

and every missing token is re-injected next to its NEAREST surviving neighbour — after the
preceding one or before the following one, whichever sits closer to it in the source
skeleton — inside that neighbour's own sense. Nearest-neighbour rather than
always-after-the-predecessor matters across a sense boundary: a citation dropped from the
end of sense 2 has its predecessor back in sense 1, and anchoring it there would file it
under the wrong sense. A card that dropped EVERY span has no neighbour to anchor to, so its
spans go to the head of the first sense (the headword-span case, `{# 0/1` — the single
largest measured sub-class).

WHY THIS IS NOT "TRUST THE MODEL LESS, GUESS MORE"
--------------------------------------------------
The repair refuses unless the card's echo is a strict ORDER-PRESERVING SUBSEQUENCE of the
source: no foreign token, no duplicate, no reordering. Under that precondition the only
possible defect IS a drop, and the source fixes it deterministically. Anything else —
paraphrased german, reordered senses, a fabricated `{Tn}` — is refused, and the caller
rejects the card exactly as before.

DELIBERATE SCOPE LIMITS
-----------------------
* **Repair-then-verify, never repair-by-default.** The caller runs the repair only on a card
  that ALREADY failed the german-side fidelity count, and re-runs that same count afterwards;
  a card that passes today is byte-untouched. This is why the change cannot regress the clean
  yield — the only cards it can reach are cards that were being thrown away.
* **The `german` field only.** The target-language field (`russian`/`english`) is NOT
  repaired: a span missing from the translation is a genuine translation loss with no
  deterministic home (`translation-fidelity-reject`, H1152 C1, still requeues it).
* **`record.grammar` is neither read nor written.** A token echoed into `grammar` is still
  MISSING from `german` as far as `count_card` is concerned (that count is german-only on
  purpose — see its docstring), so grammar plays no part in presence.
* **Not wired into the fragment lane.** `heal_group`'s guard is a MULTISET equality over
  `grammar` + `german` (C-17) — a different denominator with its own duplicate-echo
  semantics. Repairing there needs its own analysis; it is not this correction.

Every repaired card is STAMPED (`card['german_anchor']`) and the stamp is carried into the
promoted row's provenance, so a machine-patched german is never indistinguishable from one
the model got right.

The JS twin is emitted from `js_source()` in THIS module and interpolated into the harness —
authored once, not re-typed per lane (the C-01/C-17 drift lesson).
"""
import re

TOKEN_RE = re.compile(r'\{T\d+\}')

# Why a card was refused repair. Reported verbatim in telemetry so a refusal is diagnosable
# without re-running the window.
REFUSALS = (
    'source-token-repeat',   # the skeleton itself repeats a {Tn} -- anchoring is ambiguous
    'no-senses',             # nothing to anchor into
    'foreign-token',         # german carries a {Tn} the source never had (fabrication)
    'duplicate-token',       # german repeats a {Tn} (expansion, not a drop)
    'reordered-token',       # german's tokens are not in source order (not a pure drop)
    'nothing-missing',       # every source token is present -- the counts failed for some
                             # other reason (a literal `<ls`/`{#` typed into the german)
)


def tokens(text):
    """The `{Tn}` placeholders in `text`, in order of appearance."""
    return TOKEN_RE.findall(text or '')


def card_senses(card):
    """Every sense of `card` in document order (records, then senses within each record)."""
    return [sense
            for record in card.get('records') or []
            for sense in record.get('senses') or []
            if isinstance(sense, dict)]


def plan(card, skeleton):
    """Decide whether `card`'s german echo is a repairable drop of `skeleton`'s spans.

    Returns `(ok, info)`. On `ok` the info carries `after` and `before` (surviving token ->
    the missing tokens to insert after / before it), `head` (used only when the card kept no
    span at all) and `missing` (all of them, source order). On refusal it carries `reason`
    (one of `REFUSALS`).
    """
    spans = [(m.group(0), m.start(), m.end()) for m in TOKEN_RE.finditer(skeleton or '')]
    want = [token for token, _s, _e in spans]
    if len(set(want)) != len(want):
        return False, {'reason': 'source-token-repeat'}
    senses = card_senses(card)
    if not senses:
        return False, {'reason': 'no-senses'}
    order = {token: index for index, token in enumerate(want)}
    seen, last = set(), -1
    for sense in senses:
        for token in tokens(sense.get('german')):
            if token not in order:
                return False, {'reason': 'foreign-token', 'token': token}
            if token in seen:
                return False, {'reason': 'duplicate-token', 'token': token}
            if order[token] <= last:
                return False, {'reason': 'reordered-token', 'token': token}
            seen.add(token)
            last = order[token]
    missing = [token for token in want if token not in seen]
    if not missing:
        return False, {'reason': 'nothing-missing'}
    after, before, head = {}, {}, []
    for index, (token, start, end) in enumerate(spans):
        if token in seen:
            continue
        prev = next((s for s in reversed(spans[:index]) if s[0] in seen), None)
        nxt = next((s for s in spans[index + 1:] if s[0] in seen), None)
        if prev is None:
            # Nothing survives BEFORE it in the source, so it belongs at the very start of
            # the card -- the dropped headword span (`{# 0/1`), the dominant sub-class. Filing
            # it just before the next surviving token would push it past that token's own
            # German prose instead.
            head.append(token)
        elif nxt is None:
            after.setdefault(prev[0], []).append(token)
        elif (start - prev[2]) <= (nxt[1] - end):
            after.setdefault(prev[0], []).append(token)
        else:
            before.setdefault(nxt[0], []).append(token)
    return True, {'after': after, 'before': before, 'head': head, 'missing': missing}


def reanchor(card, skeleton):
    """Re-inject every dropped source span into `card`'s `german` fields, in place.

    Returns `(ok, info)` from `plan`; on `ok` the card has been mutated and `info['missing']`
    lists exactly what was re-injected. The caller MUST re-run its fidelity count afterwards
    — this function never claims the card is now acceptable, only that it applied the plan.
    """
    ok, info = plan(card, skeleton)
    if not ok:
        return ok, info
    after, before, head = info['after'], info['before'], info['head']
    senses = card_senses(card)

    def expand(match):
        token = match.group(0)
        return (''.join(t + ' ' for t in before.get(token, ())) + token
                + ''.join(' ' + t for t in after.get(token, ())))

    for sense in senses:
        text = sense.get('german')
        if not isinstance(text, str) or not TOKEN_RE.search(text):
            continue
        sense['german'] = TOKEN_RE.sub(expand, text)
    if head:
        first = senses[0]
        text = first.get('german')
        first['german'] = ' '.join(head) + (' ' + text if isinstance(text, str) and text else '')
    return True, info


def stamp(info):
    """The provenance stamp for a repaired card (`card['german_anchor']`).

    Brace-stripped exactly like the H1226 `tnmask` pairing, so the stamp can never be
    mistaken for a raw `{Tn}` residue by the C-01 placeholder scanners.
    """
    return {'reinjected': [t.strip('{}') for t in info['missing']],
            'head': [t.strip('{}') for t in info['head']]}


# ---------------------------------------------------------------------------
# The JS twin. Authored HERE and interpolated into the generated harness, so the two lanes
# cannot drift the way `restoreCard`/`restore_card` did (C-01) or `cardTokens` did (C-17).
_JS = r'''
// H858 Part B: source-anchored repair of {Tn} spans the model dropped from its `german`
// echo. Python twin: src/german_anchor.py (authored there and interpolated here — never
// re-typed per lane). Repair-then-verify: accept() calls this ONLY for a card that already
// failed the german-side fidelity count, and re-runs that count afterwards, so a card that
// passes today is byte-untouched. Refuses unless the echo is a strict order-preserving
// subsequence of the source (no foreign token, no duplicate, no reordering) — under that
// precondition the only possible defect is a drop, which the source fixes deterministically.
const GA_TOKEN_RE = /\{T\d+\}/g
const gaTokens = t => ((t || '').match(GA_TOKEN_RE) || [])
const gaSenses = card => { const out = []; for (const rec of (card.records || [])) for (const s of (rec.senses || [])) if (s && typeof s === 'object') out.push(s); return out }
const gaSpans = skeleton => { const out = []; let m; const re = new RegExp(GA_TOKEN_RE.source, 'g'); while ((m = re.exec(skeleton || '')) !== null) out.push([m[0], m.index, m.index + m[0].length]); return out }
const gaPlan = (card, skeleton) => {
  const spans = gaSpans(skeleton)
  const want = spans.map(s => s[0])
  if (new Set(want).size !== want.length) return { ok: false, reason: 'source-token-repeat' }
  const senses = gaSenses(card)
  if (!senses.length) return { ok: false, reason: 'no-senses' }
  const order = new Map(want.map((t, i) => [t, i]))
  const seen = new Set()
  let last = -1
  for (const s of senses) for (const t of gaTokens(s.german)) {
    if (!order.has(t)) return { ok: false, reason: 'foreign-token', token: t }
    if (seen.has(t)) return { ok: false, reason: 'duplicate-token', token: t }
    if (order.get(t) <= last) return { ok: false, reason: 'reordered-token', token: t }
    seen.add(t); last = order.get(t)
  }
  const missing = want.filter(t => !seen.has(t))
  if (!missing.length) return { ok: false, reason: 'nothing-missing' }
  const after = new Map(), before = new Map(), head = []
  const push = (map, key, t) => { if (!map.has(key)) map.set(key, []); map.get(key).push(t) }
  for (let i = 0; i < spans.length; i++) {
    const [token, start, end] = spans[i]
    if (seen.has(token)) continue
    let prev = null, nxt = null
    for (let j = i - 1; j >= 0; j--) if (seen.has(spans[j][0])) { prev = spans[j]; break }
    for (let j = i + 1; j < spans.length; j++) if (seen.has(spans[j][0])) { nxt = spans[j]; break }
    if (prev === null) head.push(token)                          // nothing survives before it
    else if (nxt === null) push(after, prev[0], token)
    else if ((start - prev[2]) <= (nxt[1] - end)) push(after, prev[0], token)
    else push(before, nxt[0], token)
  }
  return { ok: true, after: after, before: before, head: head, missing: missing }
}
const gaReanchor = (card, skeleton) => {
  const p = gaPlan(card, skeleton)
  if (!p.ok) return p
  const senses = gaSenses(card)
  const expand = m => (p.before.get(m) || []).map(t => t + ' ').join('') + m
                      + (p.after.get(m) || []).map(t => ' ' + t).join('')
  for (const s of senses) {
    if (typeof s.german !== 'string' || !s.german.match(GA_TOKEN_RE)) continue
    s.german = s.german.replace(GA_TOKEN_RE, expand)
  }
  if (p.head.length) {
    const first = senses[0]
    const text = typeof first.german === 'string' ? first.german : ''
    first.german = p.head.join(' ') + (text ? ' ' + text : '')
  }
  return p
}
const gaStamp = p => ({ reinjected: p.missing.map(t => t.replace(/[{}]/g, '')), head: p.head.map(t => t.replace(/[{}]/g, '')) })
'''


def js_source():
    """The JS twin of `plan`/`reanchor`/`stamp`, for interpolation into the harness."""
    return _JS


# ---------------------------------------------------------------------------
def _card(*germans):
    return {'key1': 'k', 'records': [{'h': 'k', 'grammar': '',
                                      'senses': [{'tag': str(i + 1), 'german': g, 'russian': 'x'}
                                                 for i, g in enumerate(germans)]}]}


def selftest():
    """Fail-loud, no I/O. Mirrored by `german_anchor_test.js` on the JS lane."""
    # 1. head drop -- the headword span, the largest measured sub-class ({# 0/1).
    card = _card('Feuer {T2}')
    ok, info = reanchor(card, '{T1} Feuer {T2}')
    assert ok and info['missing'] == ['{T1}'], info
    assert card_senses(card)[0]['german'] == '{T1} Feuer {T2}', card

    # 2. mid drop, anchored after its surviving predecessor.
    card = _card('{T1} Feuer {T3}')
    ok, info = reanchor(card, '{T1} a {T2} Feuer {T3}')
    assert ok and info['missing'] == ['{T2}'], info
    assert card_senses(card)[0]['german'] == '{T1} {T2} Feuer {T3}', card

    # 3. multi-sense: nearest-neighbour keeps each drop in the RIGHT sense. {T2} is adjacent
    #    to {T1} (sense 1); {T3} is adjacent to {T4} (sense 2). An always-after-the-predecessor
    #    rule would file {T3} under sense 1, because its predecessor {T2} is itself missing.
    card = _card('{T1} a', 'b {T4}')
    ok, info = reanchor(card, '{T1} {T2} a — b {T3} {T4}')
    assert ok and info['missing'] == ['{T2}', '{T3}'], info
    germans = [s['german'] for s in card_senses(card)]
    assert germans == ['{T1} {T2} a', 'b {T3} {T4}'], germans

    # 4. tail drop -- no successor, so it anchors after the last surviving span.
    card = _card('{T1} Feuer')
    ok, info = reanchor(card, '{T1} Feuer {T2}')
    assert ok and info['missing'] == ['{T2}'], info
    assert card_senses(card)[0]['german'] == '{T1} {T2} Feuer', card

    # 5. refusals -- anything that is not a pure drop is left to the existing reject.
    for german, skeleton, reason in (
            ('{T1} {T9}', '{T1} {T2}', 'foreign-token'),
            ('{T1} {T1}', '{T1} {T2}', 'duplicate-token'),
            ('{T2} {T1}', '{T1} {T2}', 'reordered-token'),
            ('{T1} {T2}', '{T1} {T2}', 'nothing-missing'),
            ('{T1}', '{T1} {T1}', 'source-token-repeat')):
        ok, info = reanchor(_card(german), skeleton)
        assert not ok and info['reason'] == reason, (german, skeleton, info)
    ok, info = reanchor({'key1': 'k', 'records': []}, '{T1}')
    assert not ok and info['reason'] == 'no-senses', info

    # 6. the repair is exactly a drop-repair: the token multiset now equals the source's.
    skeleton = '{T1} a {T2} b {T3} c {T4}'
    card = _card('a {T2} b', 'c')
    ok, _ = reanchor(card, skeleton)
    assert ok
    got = [t for s in card_senses(card) for t in tokens(s['german'])]
    assert sorted(got) == sorted(tokens(skeleton)), got

    # 7. a card that kept NO span at all: everything goes to the head of the first sense.
    card = _card('Feuer', 'Glut')
    ok, info = reanchor(card, '{T1} Feuer {T2} Glut')
    assert ok and info['head'] == ['{T1}', '{T2}'], info
    assert [s['german'] for s in card_senses(card)] == ['{T1} {T2} Feuer', 'Glut'], card

    # 8. the stamp never carries braces (it must not read as a {Tn} residue downstream).
    _ok, info = plan(_card('a'), '{T1} a')
    assert stamp(info) == {'reinjected': ['T1'], 'head': ['T1']}, stamp(info)
    print('german_anchor selftest: 8/8 OK')


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    selftest()
