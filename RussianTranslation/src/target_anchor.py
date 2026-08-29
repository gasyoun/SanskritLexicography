#!/usr/bin/env python
r"""Target-side twin of `german_anchor` — repair of `{Tn}` spans dropped from the TRANSLATION.

THE DEFECT
----------
`german_anchor` (H858 Part B) repairs a span the model dropped from its `german` SOURCE echo.
The other half of the same class was never repaired at all: the german echo comes back
faithful and the `russian`/`english` field drops a span. `headless_worker.count_card_field`
(H1152 parity C1) catches it and nulls the whole card — `translation-fidelity-reject` — and
because `count_card` already matched, `german_anchor` is never even reached (FINDINGS §605,
§608; the live shape is `hasita~~h0_zz_pw` on `no_pwg_w09`, german 2/2 · russian 1/2).

Measured on that class the two halves are NOT interchangeable: replaying `hasita` through
`german_anchor` returns `nothing-missing`, because every source span *is* present — in the
wrong field. So this needed its own repair, not a re-gated call site.

WHY THIS IS NOT THE PR #789 BOUNDARY GUESS
------------------------------------------
PR #789 refused to wrap a Russian gloss whose `{%…%}` boundary was merely *omitted*: there
the target text is prose, the span has no marker left in it, and finding where it starts and
ends means guessing inside a translated sentence. **That is a different problem.** Here the
`{Tn}` tokens are opaque, atomic, and — this is the load-bearing fact — the SAME sense's
`german` field is a surviving parallel that still carries every one of them in order. The
translation is not being parsed; a token is being restored to the position its own parallel
already names. The anchor is present evidence, not inference.

Concretely, per sense (senses pair 1:1 by card schema — one `german` and one target field on
the same object, so no alignment step exists to get wrong):

    want    = the `{Tn}` in THIS sense's `german`, document order
    got     = the `{Tn}` in THIS sense's target field, document order
    missing = want - got

and each missing token is re-injected next to its nearest surviving neighbour **in the same
sense**, after the preceding one or before the following one, whichever sits closer to it in
that sense's own german text — with the SENSE START and the SENSE END standing in as the
neighbours when nothing survives on that side. So a dropped headword span goes to the head, a
trailing span goes to the tail, and a leading-but-not-first span still anchors before its
successor rather than jumping the prose.

Scoping the anchor PER SENSE is the whole safety argument. `german_anchor` anchors against
the card-wide source skeleton and needs nearest-neighbour logic to avoid filing a span under
the wrong sense; here the sense is fixed before the search begins, so a span can never
migrate between senses no matter what the prose looks like.

DELIBERATE SCOPE LIMITS
-----------------------
* **Repair-then-verify, never repair-by-default.** The caller runs this only on a card that
  ALREADY failed `count_card_field`, and re-runs that same count afterwards; a card that
  passes today is byte-untouched. The only cards it can reach were being thrown away.
* **Refuses unless the target echo is a strict order-preserving SUBSEQUENCE of the sense's
  german.** No foreign token, no duplicate, no reordering — under that precondition the only
  possible defect is a drop. A rearranged or paraphrased target is refused and rejects
  exactly as before.
* **The german field is neither read for content nor written.** It is the anchor only. This
  runs AFTER `german_anchor` in `normalize_batch`, so when both fire the german echo has
  already been made source-faithful and is a sound parallel to anchor against.
* **`record.grammar` plays no part** — `count_card_field` is per-sense target-field-only, so
  the denominator here is exactly what that guard counts.

Every repaired card is STAMPED (`card['target_anchor']`), like the german twin, so a
machine-patched translation is never indistinguishable from one the model got right.

The JS twin is emitted from `js_source()` in THIS module and interpolated into the harness —
authored once, not re-typed per lane (the C-01/C-17 drift lesson).
"""
import re

TOKEN_RE = re.compile(r'\{T\d+\}')

# Why a card was refused repair. Reported verbatim in telemetry so a refusal is diagnosable
# without re-running the window.
REFUSALS = (
    'anchor-token-repeat',   # a sense's own german repeats a {Tn} -- anchoring is ambiguous
    'no-senses',             # nothing to anchor into
    'foreign-token',         # the target carries a {Tn} that sense's german never had
    'duplicate-token',       # the target repeats a {Tn} (expansion, not a drop)
    'reordered-token',       # the target's tokens are not in the german's order
    'nothing-missing',       # every anchor token is present -- the count failed for some
                             # other reason (a literal `<ls`/`{#` typed into the translation)
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


def plan(card, field):
    """Decide whether `card`'s `field` echo is a repairable per-sense drop of its own german.

    Returns `(ok, info)`. On `ok` the info carries `senses` — one entry per sense that needs
    work, each `{'index', 'after', 'before', 'head', 'tail'}` — and `missing` (every re-injected
    token, document order). On refusal it carries `reason` (one of `REFUSALS`), and `sense`
    /`token` where they narrow it down.
    """
    senses = card_senses(card)
    if not senses:
        return False, {'reason': 'no-senses'}
    plans, missing_all = [], []
    for index, sense in enumerate(senses):
        spans = [(m.group(0), m.start(), m.end())
                 for m in TOKEN_RE.finditer(sense.get('german') or '')]
        want = [token for token, _s, _e in spans]
        if len(set(want)) != len(want):
            return False, {'reason': 'anchor-token-repeat', 'sense': index}
        order = {token: position for position, token in enumerate(want)}
        seen, last = set(), -1
        for token in tokens(sense.get(field)):
            if token not in order:
                return False, {'reason': 'foreign-token', 'sense': index, 'token': token}
            if token in seen:
                return False, {'reason': 'duplicate-token', 'sense': index, 'token': token}
            if order[token] <= last:
                return False, {'reason': 'reordered-token', 'sense': index, 'token': token}
            seen.add(token)
            last = order[token]
        missing = [token for token in want if token not in seen]
        if not missing:
            continue
        after, before, head, tail = {}, {}, [], []
        for position, (token, start, end) in enumerate(spans):
            if token in seen:
                continue
            prev = next((s for s in reversed(spans[:position]) if s[0] in seen), None)
            nxt = next((s for s in spans[position + 1:] if s[0] in seen), None)
            # Nearest surviving neighbour, with the SENSE START and the SENSE END standing
            # in as virtual anchors when nothing survives on that side. Those two virtual
            # anchors are what make the rule work per sense, and they are why this is not a
            # copy of `german_anchor`'s branch:
            #   * a dropped headword span sits at offset 0, beats its successor, and goes to
            #     the head (`{T1} Feuer {T2}` -> `{T1} огонь {T2}`);
            #   * a leading-but-not-first span has prose ahead of it and loses to its
            #     successor (`b {T3} {T4}` -> `б {T3} {T4}`, never `{T3} б {T4}`);
            #   * a trailing span sits at the end, beats its predecessor, and goes to the tail
            #     (`{T1} unverwirrt {T2}` -> `{T1} невозмутимый {T2}`, never
            #     `{T1} {T2} невозмутимый`, which is what an after-the-predecessor rule gives).
            # `german_anchor` anchors against the card-wide SOURCE skeleton, where the first
            # span really is the headword and there is no per-sense end to measure to, so it
            # takes the unconditional head branch instead. A per-sense german parallel offers
            # both edges, and using them is strictly more faithful.
            left = start - (prev[2] if prev is not None else 0)
            right = (nxt[1] - end) if nxt is not None else (len(sense.get('german') or '') - end)
            if left <= right:
                if prev is None:
                    head.append(token)
                else:
                    after.setdefault(prev[0], []).append(token)
            else:
                if nxt is None:
                    tail.append(token)
                else:
                    before.setdefault(nxt[0], []).append(token)
        plans.append({'index': index, 'after': after, 'before': before,
                      'head': head, 'tail': tail})
        missing_all.extend(missing)
    if not missing_all:
        return False, {'reason': 'nothing-missing'}
    return True, {'senses': plans, 'missing': missing_all}


def reanchor(card, field):
    """Re-inject every dropped span into `card`'s per-sense `field`, in place.

    Returns `(ok, info)` from `plan`; on `ok` the card has been mutated and `info['missing']`
    lists exactly what was re-injected. The caller MUST re-run its fidelity count afterwards
    — this function never claims the card is now acceptable, only that it applied the plan.
    """
    ok, info = plan(card, field)
    if not ok:
        return ok, info
    senses = card_senses(card)
    for entry in info['senses']:
        sense = senses[entry['index']]
        after, before = entry['after'], entry['before']
        head, tail = entry['head'], entry['tail']

        def expand(match, after=after, before=before):
            token = match.group(0)
            return (''.join(t + ' ' for t in before.get(token, ())) + token
                    + ''.join(' ' + t for t in after.get(token, ())))

        text = sense.get(field)
        if isinstance(text, str) and TOKEN_RE.search(text):
            sense[field] = TOKEN_RE.sub(expand, text)
        if head:
            text = sense.get(field)
            sense[field] = ' '.join(head) + (' ' + text if isinstance(text, str) and text else '')
        if tail:
            text = sense.get(field)
            sense[field] = (text + ' ' if isinstance(text, str) and text else '') + ' '.join(tail)
    return True, info


def stamp(info):
    """The provenance stamp for a repaired card (`card['target_anchor']`).

    Brace-stripped exactly like the H1226 `tnmask` pairing and the `german_anchor` stamp, so
    it can never be mistaken for a raw `{Tn}` residue by the C-01 placeholder scanners.

    Deliberately the SAME two keys as the german twin's stamp, so a downstream reader can
    treat the two provenance blocks identically. Tokens re-injected at a sense TAIL are in
    `reinjected` like every other one; `head` stays the head-specific detail it is on the
    german side.
    """
    return {'reinjected': [t.strip('{}') for t in info['missing']],
            'head': [t.strip('{}')
                     for entry in info['senses'] for t in entry['head']]}


# ---------------------------------------------------------------------------
# The JS twin. Authored HERE and interpolated into the generated harness, so the two lanes
# cannot drift the way `restoreCard`/`restore_card` did (C-01) or `cardTokens` did (C-17).
_JS = r'''
// Target-side twin of the german-anchor repair: re-injects {Tn} spans the model dropped from
// the TRANSLATION field while echoing `german` faithfully (FINDINGS 605/608; the live shape is
// hasita~~h0_zz_pw, german 2/2 target 1/2). Python twin: src/target_anchor.py (authored there
// and interpolated here — never re-typed per lane). Repair-then-verify: accept() calls this
// ONLY for a card that already failed the TARGET-field fidelity count, and re-runs that count
// afterwards. The anchor is the SAME sense's german, which still carries every token in order —
// so this restores a token to a position its own parallel names, it does not parse prose.
const TA_TOKEN_RE = /\{T\d+\}/g
const taTokens = t => ((t || '').match(TA_TOKEN_RE) || [])
const taSenses = card => { const out = []; for (const rec of (card.records || [])) for (const s of (rec.senses || [])) if (s && typeof s === 'object') out.push(s); return out }
const taSpans = text => { const out = []; let m; const re = new RegExp(TA_TOKEN_RE.source, 'g'); while ((m = re.exec(text || '')) !== null) out.push([m[0], m.index, m.index + m[0].length]); return out }
const taPlan = (card, field) => {
  const senses = taSenses(card)
  if (!senses.length) return { ok: false, reason: 'no-senses' }
  const plans = [], missingAll = []
  for (let i = 0; i < senses.length; i++) {
    const s = senses[i]
    const spans = taSpans(s.german)
    const want = spans.map(x => x[0])
    if (new Set(want).size !== want.length) return { ok: false, reason: 'anchor-token-repeat', sense: i }
    const order = new Map(want.map((t, n) => [t, n]))
    const seen = new Set()
    let last = -1
    for (const t of taTokens(s[field])) {
      if (!order.has(t)) return { ok: false, reason: 'foreign-token', sense: i, token: t }
      if (seen.has(t)) return { ok: false, reason: 'duplicate-token', sense: i, token: t }
      if (order.get(t) <= last) return { ok: false, reason: 'reordered-token', sense: i, token: t }
      seen.add(t); last = order.get(t)
    }
    const missing = want.filter(t => !seen.has(t))
    if (!missing.length) continue
    const after = new Map(), before = new Map(), head = [], tail = []
    const push = (map, key, t) => { if (!map.has(key)) map.set(key, []); map.get(key).push(t) }
    for (let n = 0; n < spans.length; n++) {
      const [token, start, end] = spans[n]
      if (seen.has(token)) continue
      let prev = null, nxt = null
      for (let j = n - 1; j >= 0; j--) if (seen.has(spans[j][0])) { prev = spans[j]; break }
      for (let j = n + 1; j < spans.length; j++) if (seen.has(spans[j][0])) { nxt = spans[j]; break }
      // Sense start AND sense end are the virtual anchors when nothing survives on that
      // side — see the Python twin's comment. Without them a leading-but-not-first span jumps
      // in front of its own prose and a trailing span lands behind it.
      const left = start - (prev === null ? 0 : prev[2])
      const right = nxt === null ? (s.german || '').length - end : nxt[1] - end
      if (left <= right) { if (prev === null) head.push(token); else push(after, prev[0], token) }
      else { if (nxt === null) tail.push(token); else push(before, nxt[0], token) }
    }
    plans.push({ index: i, after: after, before: before, head: head, tail: tail })
    for (const t of missing) missingAll.push(t)
  }
  if (!missingAll.length) return { ok: false, reason: 'nothing-missing' }
  return { ok: true, senses: plans, missing: missingAll }
}
const taReanchor = (card, field) => {
  const p = taPlan(card, field)
  if (!p.ok) return p
  const senses = taSenses(card)
  for (const entry of p.senses) {
    const s = senses[entry.index]
    const expand = m => (entry.before.get(m) || []).map(t => t + ' ').join('') + m
                        + (entry.after.get(m) || []).map(t => ' ' + t).join('')
    if (typeof s[field] === 'string' && s[field].match(TA_TOKEN_RE)) {
      s[field] = s[field].replace(TA_TOKEN_RE, expand)
    }
    if (entry.head.length) {
      const text = typeof s[field] === 'string' ? s[field] : ''
      s[field] = entry.head.join(' ') + (text ? ' ' + text : '')
    }
    if (entry.tail.length) {
      const text = typeof s[field] === 'string' ? s[field] : ''
      s[field] = (text ? text + ' ' : '') + entry.tail.join(' ')
    }
  }
  return p
}
// ONE LINE, like gaStamp: the JS test harness extracts it with a single-line matcher.
const taStamp = p => ({ reinjected: p.missing.map(t => t.replace(/[{}]/g, '')), head: p.senses.reduce((a, e) => a.concat(e.head), []).map(t => t.replace(/[{}]/g, '')) })
'''


def js_source():
    """The JS twin of `plan`/`reanchor`/`stamp`, for interpolation into the harness."""
    return _JS


# ---------------------------------------------------------------------------
def _card(*pairs):
    """`_card(('german', 'russian'), ...)` -- one sense per pair."""
    return {'key1': 'k', 'records': [{'h': 'k', 'grammar': '',
                                      'senses': [{'tag': str(i + 1), 'german': g, 'russian': r}
                                                 for i, (g, r) in enumerate(pairs)]}]}


def selftest():
    """Fail-loud, no I/O. Mirrored by `target_anchor_test.js` on the JS lane."""
    # 1. head drop -- the headword span, the largest measured sub-class of the german twin and
    #    the same shape here.
    card = _card(('{T1} Feuer {T2}', 'огонь {T2}'))
    ok, info = reanchor(card, 'russian')
    assert ok and info['missing'] == ['{T1}'], info
    assert card_senses(card)[0]['russian'] == '{T1} огонь {T2}', card

    # 2. mid drop, anchored after its surviving predecessor.
    card = _card(('{T1} a {T2} Feuer {T3}', '{T1} огонь {T3}'))
    ok, info = reanchor(card, 'russian')
    assert ok and info['missing'] == ['{T2}'], info
    assert card_senses(card)[0]['russian'] == '{T1} {T2} огонь {T3}', card

    # 3. THE property the german twin cannot offer: the anchor is per SENSE, so a span can
    #    never migrate between senses however the prose is arranged. Sense 2 drops {T3}; its
    #    card-wide predecessor {T2} lives in sense 1 and is irrelevant here. It also pins the
    #    virtual-left-anchor rule: {T3} has no surviving predecessor but DOES have prose ahead
    #    of it, so it anchors before {T4} instead of jumping to the head of the sense.
    card = _card(('{T1} {T2} a', '{T1} {T2} а'), ('b {T3} {T4}', 'б {T4}'))
    ok, info = reanchor(card, 'russian')
    assert ok and info['missing'] == ['{T3}'], info
    assert [s['russian'] for s in card_senses(card)] == ['{T1} {T2} а', 'б {T3} {T4}'], card

    # 4. tail drop -- the SENSE END is nearer than the surviving predecessor, so it lands at
    #    the tail. An after-the-predecessor rule (what `german_anchor` does, having no per-sense
    #    end to measure to) would give `{T1} {T2} огонь` -- the citation on the wrong side of
    #    the prose it belongs to.
    card = _card(('{T1} Feuer {T2}', '{T1} огонь'))
    ok, info = reanchor(card, 'russian')
    assert ok and info['missing'] == ['{T2}'], info
    assert card_senses(card)[0]['russian'] == '{T1} огонь {T2}', card

    # 4b. a sense that kept no span at all still splits head/tail by the same measure.
    card = _card(('{T1} a {T2}', 'а'))
    ok, info = reanchor(card, 'russian')
    assert ok and info['missing'] == ['{T1}', '{T2}'], info
    assert card_senses(card)[0]['russian'] == '{T1} а {T2}', card

    # 5. refusals -- anything that is not a pure drop is left to the existing reject.
    for german, russian, reason in (
            ('{T1} {T2}', '{T1} {T9}', 'foreign-token'),
            ('{T1} {T2}', '{T1} {T1}', 'duplicate-token'),
            ('{T1} {T2}', '{T2} {T1}', 'reordered-token'),
            ('{T1} {T2}', '{T1} {T2}', 'nothing-missing'),
            ('{T1} {T1}', '{T1}', 'anchor-token-repeat')):
        ok, info = reanchor(_card((german, russian)), 'russian')
        assert not ok and info['reason'] == reason, (german, russian, info)
    ok, info = reanchor({'key1': 'k', 'records': []}, 'russian')
    assert not ok and info['reason'] == 'no-senses', info

    # 6. the repair is exactly a drop-repair: the target multiset now equals the german's.
    card = _card(('{T1} a {T2} b {T3}', 'а {T2} б'), ('{T4} c', 'в'))
    ok, _ = reanchor(card, 'russian')
    assert ok
    for sense in card_senses(card):
        assert tokens(sense['russian']) == tokens(sense['german']), sense

    # 7. a sense that kept NO span at all: everything goes to the head of THAT sense, never
    #    to the head of the card.
    card = _card(('{T1} Feuer', 'огонь'), ('{T2} Glut', '{T2} жар'))
    ok, info = reanchor(card, 'russian')
    assert ok and info['missing'] == ['{T1}'], info
    assert [s['russian'] for s in card_senses(card)] == ['{T1} огонь', '{T2} жар'], card

    # 8. the german field is the anchor and is never written.
    card = _card(('{T1} Feuer {T2}', 'огонь {T2}'))
    before = [s['german'] for s in card_senses(card)]
    reanchor(card, 'russian')
    assert [s['german'] for s in card_senses(card)] == before, card

    # 9. the stamp never carries braces (it must not read as a {Tn} residue downstream).
    _ok, info = plan(_card(('{T1} a', 'а')), 'russian')
    assert stamp(info) == {'reinjected': ['T1'], 'head': ['T1']}, stamp(info)

    # 10. `english` is not a special case -- the field is a parameter, never a literal.
    card = {'key1': 'k', 'records': [{'h': 'k', 'grammar': '', 'senses': [
        {'tag': '1', 'german': '{T1} Feuer {T2}', 'english': 'fire {T2}'}]}]}
    ok, info = reanchor(card, 'english')
    assert ok and card_senses(card)[0]['english'] == '{T1} fire {T2}', card
    print('target_anchor selftest: 10/10 OK')


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    selftest()
