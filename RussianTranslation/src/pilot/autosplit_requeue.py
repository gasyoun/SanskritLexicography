#!/usr/bin/env python
r"""Per-card auto-split requeue — the permanent, tiered fix for dense-card retry-cap failures.

A sub-card whose senses+citations produce more JSON than one StructuredOutput call reliably
emits hits the retry cap and returns null. _pilot_gen_merged --root-split is NOT a post-hoc
fix (it deletes+regenerates a root's whole rootmap and orphans its translated cards). This
fixes ONE card in place, no rootmap churn, via a tier ladder — each tier a deterministic
(no-LLM) split; only the small resulting translations use the model:

  Tier 0  whole retry          card has <2 detectable (sub)senses -> re-translate whole
                               (recovers tiny cards that failed on stochastic variance)
  Tier 1  sense split          split at numbered AND lettered/greek (sub)sense boundaries
  Tier 2  citation split       a (sub)sense with > LS_BUDGET <ls> is split into citation
                               batches; the batches are stitched back into ONE sense
Fragments carry (sense_ord, part_ord); merge groups by sense_ord and concatenates parts,
so tier-2 batches rejoin into a single sense. A completeness guard emits a card only when
ALL its fragments came back (never a lossy partial), and a post-stitch fidelity check warns
if the reassembled <ls>/{#..#} counts drift from the source.

  python src/pilot/autosplit_requeue.py test  <root>       key1,key2,...   # plan only, no LLM
  python src/pilot/autosplit_requeue.py gen   <root> <lang> key1,key2,...  # frag inputs + harness
  # run the printed harness via the Workflow tool, then:
  python src/pilot/autosplit_requeue.py merge <root> <lang> <task_output>  # stitch -> wf file
  # then: promote_final_cards.py --glob 'wf_output.<tag>.<root>.autosplit.json' --merge

TOP-UP a partially-healed card (targeted, no full re-split). A card selfHeal could only
partially heal carries partial:true + missing_fragments (gN:fM ids) + frag_prov (the
resolved fragments). `topup` re-translates ONLY the missing fragments and stitches them
back onto the resolved ones — instead of re-planning the whole card from scratch:

  python src/pilot/autosplit_requeue.py topup       <root> <lang> <wf_output.json>  # missing frags + harness
  # run the printed harness via the Workflow tool, then:
  python src/pilot/autosplit_requeue.py topup-merge  <root> <lang> <task_output>     # stitch complete card
  # then: promote_final_cards.py --glob 'wf_output.<tag>.<root>.autosplit.json' --merge
"""
import datetime
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
REPO = os.path.dirname(SRC)
sys.path.insert(0, HERE)
sys.path.insert(0, SRC)
from window_common import input_paths, read_text, sha256_file  # noqa: E402
import pwg_mask                                            # noqa: E402
from safe_filename import safe_name                        # noqa: E402

LS_BUDGET = int(os.environ.get('AUTOSPLIT_LS_BUDGET', '18'))   # max <ls> per fragment (tier 2)
MANIFEST = os.path.join(HERE, 'output', 'autosplit_manifest.json')   # legacy shared path (pre per-root)


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec='seconds').replace('+00:00', 'Z')


def _stamp_input_hashes(orig_keys):
    """Per-original-card source hashes for autosplit provenance (H188 fix).

    An autosplit merge re-stitches fragments back under each ORIGINAL card key. The
    promoted store rows must still carry the same source provenance the harness stamps
    on a normal window — `input_raw_sha256` / `input_portrait_sha256`, keyed by that
    original sub-card key. Before this, both autosplit writers emitted a stripped meta
    with NO `input_hashes`, so `promote_final_cards.provenance()` read an empty map and
    every autosplit row landed SHA-less (`audit_translation_provenance` flagged them; the
    kAla/ka/SrI-class high-density roots run through exactly this path). Raw + portrait
    paths come from `window_common.input_paths`, hashed with the SAME canonical
    `sha256_file` the harness uses, so the address is byte-identical to a non-autosplit
    run of the same card. A key whose source file is absent (a fully-failed/ghost card)
    is skipped, never crashing the merge."""
    hashes = {}
    for k in orig_keys:
        try:
            rp, pp = input_paths(k)
        except Exception:
            continue
        entry = {}
        if rp and os.path.exists(rp):
            entry['raw_sha256'] = sha256_file(rp)
        if pp and os.path.exists(pp):
            entry['portrait_sha256'] = sha256_file(pp)
        if entry:
            hashes[k] = entry
    return hashes


def _autosplit_meta(root, lang, generator, orig_keys, generated_at=None):
    """The workflow-meta block written by both autosplit merge writers.

    Carries the provenance a normal harness window carries (`input_hashes` +
    `generated_at`) so promoted autosplit rows are NOT provenance-incomplete (H188)."""
    return {'root': root, 'safe_root': safe_name(root), 'lang': lang,
            'generator': generator, 'schema_version': 'pwg_ru.workflow_meta.v1',
            'selected_keys': sorted(orig_keys),
            'input_hashes': _stamp_input_hashes(orig_keys),
            'generated_at': generated_at or _utc_now()}


def manifest_path(lang, root):
    """Per-root+lang manifest. The old single shared autosplit_manifest.json was a race:
    two concurrent sessions running `gen` for different roots overwrote each other's
    manifest, so the later `merge` silently used the WRONG fragment map — every fragment
    key missed and the cards were 'skipped' with no hint why (branch/account contention
    is a documented reality in this repo)."""
    return os.path.join(HERE, 'output', 'autosplit_manifest_%s_%s.json' % (lang, safe_name(root)))

# A (sub)sense starts at a line like "1)", "— 2)", "<div n="1"> 3)", "a)", "— b)", "α)".
_SENSE = re.compile(r'^(?:<div[^>]*>)?\s*(?:—\s*)?(?:\d+|[a-zA-Zα-ωΑ-Ω])\s*[\)〉]')


def _blocks(raw):
    """(header, [sense/subsense blocks]) or None if <2 boundaries."""
    lines = raw.split('\n')
    starts = [i for i, l in enumerate(lines) if _SENSE.match(l.strip())]
    if len(starts) < 2:
        return None
    header = '\n'.join(lines[:starts[0]]).rstrip()
    blocks = ['\n'.join(lines[a:b]).rstrip()
              for a, b in zip(starts, starts[1:] + [len(lines)])]
    return header, blocks


def _span_open(text):
    """True if `text` ends with an unterminated <ls>...</ls> or {#...#} span (a paired
    span opened but not yet closed). Citation/Sanskrit spans can legitimately run across
    several lines; cutting a fragment in the middle of one leaves BOTH halves holding an
    unbalanced tag that pwg_mask.mask() can no longer match (its PAIRED regex requires a
    complete open+close pair even with re.S), so the Sanskrit/citation text passes through
    UNMASKED as ordinary translatable prose — the model then paraphrases or drops it,
    producing LS-LOSS/SAN-LOSS specifically on the giant citation-dense heads that need
    tier-2 splitting (see PIPELINE_HISTORY.md)."""
    return text.count('<ls') > text.count('</ls>') or text.count('{#') > text.count('#}')


def _dense_line_parts(line, ls_budget):
    """Split a single citation-dense physical line at complete <ls>...</ls> spans.

    _cit_parts normally cuts on line boundaries. The H189 monster-fragment audit found
    some "one sense, one long line" shapes where one physical line can carry far more
    citations than the budget, so a line-boundary splitter still emits an over-budget
    fragment. This keeps every citation span intact and only flushes when the accumulated
    chunk is balanced for both <ls> and {#...#}.
    """
    if line.count('<ls') <= ls_budget:
        return [line]
    pieces = re.split(r'(<ls\b[^>]*>.*?</ls>)', line, flags=re.S)
    if len(pieces) == 1:
        return [line]
    parts, cur, c = [], [], 0
    for piece in pieces:
        if piece == '':
            continue
        n = piece.count('<ls')
        text = ''.join(cur)
        if cur and c and c + n > ls_budget and not _span_open(text):
            parts.append(text); cur, c = [], 0
        cur.append(piece); c += n
    if cur:
        parts.append(''.join(cur))
    return parts or [line]


def _cit_parts(block, ls_budget):
    """Split one (sub)sense block into parts each <= ls_budget <ls>, on line boundaries —
    but never inside an open <ls>/{#...#} span (see _span_open); the budget cut is deferred
    to the next line where the accumulated text is tag-balanced."""
    lines = block.split('\n')
    parts, cur, c = [], [], 0
    for l in lines:
        for chunk in _dense_line_parts(l, ls_budget):
            n = chunk.count('<ls')
            if cur and c + n > ls_budget and not _span_open('\n'.join(cur)):
                parts.append('\n'.join(cur)); cur, c = [], 0
            cur.append(chunk); c += n
    if cur:
        parts.append('\n'.join(cur))
    return parts


def plan(raw, ls_budget=LS_BUDGET):
    """[(sense_ord, part_ord, text)]. Tier 0 = whole; tier 1 = per (sub)sense; tier 2 =
    citation batches within an oversized (sub)sense. Header attaches to (0,0) only —
    but the header ITSELF is budgeted together with that first block, not glued on
    unconditionally (a verb's conjugation-table header can carry all of a card's citation
    density with almost no glossable text of its own, e.g. brU pwg00's header alone had 28
    <ls>/26 {#..#} vs 0 <ls> in the actual first sense — see PROCESS_AUDIT dev note #7)."""
    b = _blocks(raw)
    if not b:
        # <2 detectable (sub)senses. If it is nonetheless citation-dense, it is a SINGLE giant
        # sense (e.g. hi/banD heads, 160-205 <ls>) — tier 2 still applies: split its citations
        # into batches (one sense_ord, many part_ord). Otherwise tier 0 = whole-card retry.
        if raw.count('<ls') > ls_budget:
            return [(0, pi, p) for pi, p in enumerate(_cit_parts(raw, ls_budget))]
        return [(0, 0, raw)]
    header, blocks = b
    out = []
    for si, blk in enumerate(blocks):
        if si == 0 and header:
            combined = header + '\n' + blk
            parts = _cit_parts(combined, ls_budget) if combined.count('<ls') > ls_budget else [combined]
        else:
            parts = _cit_parts(blk, ls_budget) if blk.count('<ls') > ls_budget else [blk]
        for pi, p in enumerate(parts):
            out.append((si, pi, p))
    return out


def fk_of(orig, si, pi):
    return '%s__s%dp%d' % (orig, si, pi)


# --------------------------------------------------------------------------- topup
# A card the harness selfHeal could only PARTIALLY heal comes back with partial:true +
# missing_fragments (exact 'gN:fM' ids, N=1-based group, M=0-based fragment-in-group) +
# frag_prov (freshly-resolved fragments, content-addressed by fsha). The inline path recorded
# WHICH fragments failed but nothing consumed them, so `autosplit_requeue.py test ka ka` only
# re-planned the whole 81-fragment card. `topup` closes that: it maps the missing_fragments
# ids back to their plan() fragments, re-translates ONLY those, and stitches them back onto the
# already-resolved fragments (from frag_prov / the fragment TM) — a targeted fix, not a re-split.

def topup_manifest_path(lang, root):
    return os.path.join(HERE, 'output', 'autosplit_topup_%s_%s.json' % (lang, safe_name(root)))


def missing_file_path(lang, root):
    # Same name/location cmd_merge already writes its missing-fragment file to (one persistence
    # channel for both the standalone-merge and the topup path).
    return os.path.join(HERE, 'output', 'autosplit_missing_%s_%s.json' % (lang, safe_name(root)))


def frag_groups(raw, meta=None, key=None):
    """Reconstruct the EXACT selfHeal fragment-group partition gen_opt_harness2 builds for a
    card, so a 'gN:fM' missing-fragment id maps back to a plan() fragment. Returns
    [[(si, pi, text), ...], ...] — groups in document order, the same partition as FRAGS[k].
    Lazy-imports the harness grouper (a) to stay byte-identical to the producer of the ids and
    (b) to avoid the autosplit<->harness circular import at module load.

    H304: the harness groups a PRESPLIT card at PRESPLIT_GROUP_CITE_BUDGET with a sense
    count_cap (H189 re-batching), not at SELFHEAL_GROUP_BUDGET — so reconstructing every card
    with the heal budget mis-maps gN:fM ids for exactly the giant cards topup exists for.
    Pass the wf_output `meta` + the card's `key`: the lane and its budgets are read from the
    run that MINTED the ids (falling back to current constants for older metas)."""
    from gen_opt_harness2 import (_group_by_budget, SELFHEAL_GROUP_BUDGET,
                                  PRESPLIT_GROUP_CITE_BUDGET, PRESPLIT_GROUP_SENSE_CAP)
    pl = plan(raw)
    meta = meta or {}
    if key is not None and key in (meta.get('presplit_keys') or []):
        cite = meta.get('presplit_group_cite_budget') or PRESPLIT_GROUP_CITE_BUDGET
        cap = meta.get('presplit_group_sense_cap') or PRESPLIT_GROUP_SENSE_CAP
        return _group_by_budget(pl, lambda f: 1 + f[2].count('<ls'), cite, count_cap=cap)
    heal = meta.get('selfheal_group_budget') or SELFHEAL_GROUP_BUDGET
    return _group_by_budget(pl, lambda f: 1 + f[2].count('<ls'), heal)


def resolve_frag_ids(groups, missing_fragments):
    """Map each 'gN:fM' id to its (si, pi, text) plan fragment. Raises loudly on an out-of-range
    id rather than silently mis-mapping (the whole point is a TRUSTWORTHY targeted requeue)."""
    out = []
    for mid in missing_fragments:
        try:
            g, f = mid.split(':')
            gi, fi = int(g[1:]) - 1, int(f[1:])
        except (ValueError, IndexError):
            raise ValueError('malformed missing-fragment id %r (want gN:fM)' % mid)
        if not (0 <= gi < len(groups) and 0 <= fi < len(groups[gi])):
            raise ValueError('missing-fragment id %r out of range (%d groups; group has %d)'
                             % (mid, len(groups), len(groups[gi]) if 0 <= gi < len(groups) else -1))
        out.append(groups[gi][fi])
    return out


def topup_fragments(wf_file, lang):
    """Read a wf_output and return, per partial card carrying missing_fragments, everything a
    targeted top-up needs: the full plan (each fragment's fsha + fk + missing flag), the senses
    of every ALREADY-resolved fragment (harvested from the card's frag_prov, backfilled from the
    fragment TM sidecar), the (si,pi,text) list of the missing fragments to re-translate, and the
    card's iast/h. Pure (no writes). A card with no frag_prov cannot be topped up in place — its
    resolved fragments are unrecoverable — and is skipped with a warning; use full `gen` for it."""
    from translation_memory import frag_address, load_frag_tm
    d = json.load(open(wf_file, encoding='utf-8'))
    res = d.get('result') or d
    if isinstance(res, str):
        res = json.loads(res)
    frag_cache = load_frag_tm(lang)
    wf_meta = res.get('meta') or {}
    cards = []
    for r in res.get('results') or []:
        card = (r or {}).get('card')
        if not card or not card.get('partial') or not card.get('missing_fragments'):
            continue
        orig = r.get('key') or card.get('key1')
        resolved = {}
        for fp in card.get('frag_prov') or []:
            if fp.get('fsha') and fp.get('senses'):
                resolved.setdefault(fp['fsha'], fp['senses'])
        raw = read_text(input_paths(orig)[0])
        groups = frag_groups(raw, meta=wf_meta, key=orig)
        missing = resolve_frag_ids(groups, card['missing_fragments'])
        missing_set = {(si, pi) for si, pi, _ in missing}
        planrows, unresolvable = [], []
        for g in groups:
            for (si, pi, text) in g:
                fsha = frag_address(lang, text)
                if (si, pi) not in missing_set and fsha not in resolved:
                    cached = frag_cache.get(fsha)
                    if cached and cached.get('senses'):
                        resolved[fsha] = cached['senses']
                    else:
                        unresolvable.append((si, pi))
                planrows.append({'s': si, 'p': pi, 'fsha': fsha, 'fk': fk_of(orig, si, pi),
                                 'missing': (si, pi) in missing_set, 'text': text})
        if unresolvable:
            print('  ! %s: %d resolved fragment(s) not in frag_prov/frag-TM — cannot top up in '
                  'place (use full `gen`); skipping' % (orig, len(unresolvable)))
            continue
        h = None
        for rec in card.get('records') or []:
            h = h or rec.get('h')
        cards.append({'orig': orig, 'iast': card.get('iast'), 'h': h,
                      'plan': planrows, 'resolved': resolved, 'missing': missing})
    return cards


def _stitch_tree(tree, field):
    """tree: {sense_ord: {part_ord: senses_list_or_None}} -> (senses, missing_sense_ords).
    Mirrors cmd_merge's stitch: one merged sense per sense_ord, concatenating every part and
    sub-sense; a sense with any missing part is left out and reported."""
    senses, missing_si = [], []
    for si in sorted(tree):
        parts = tree[si]
        if any(parts[pi] is None for pi in parts):
            missing_si.append(si)
            continue
        g_txt, t_txt, tag, extra = [], [], None, {}
        for pi in sorted(parts):
            for s in parts[pi]:
                g_txt.append(s.get('german') or '')
                t_txt.append(s.get(field) or '')
                if tag is None:
                    tag = s.get('tag')
                    extra = {kk: s.get(kk) for kk in
                             ('equivalence_type', 'source_type', 'stratum', 'differentia')}
        merged = {'tag': tag, 'german': '\n'.join(x for x in g_txt if x),
                  field: '\n'.join(x for x in t_txt if x)}
        merged.update({kk: vv for kk, vv in extra.items() if vv is not None})
        senses.append(merged)
    return senses, missing_si


def stitch_topup(manifest_cards, got, field):
    """Reassemble each card from its resolved fragments (senses baked into the manifest) plus the
    freshly-recovered missing fragments (`got`: fk -> senses list, or None if still failed).
    Returns (results, still_missing) — results rows shaped exactly like cmd_merge's."""
    results, still_missing = [], {}
    for c in manifest_cards:
        orig, resolved = c['orig'], c.get('resolved') or {}
        tree, missing_fk = defaultdict(dict), []
        for row in c['plan']:
            si, pi = row['s'], row['p']
            if row['missing']:
                senses = got.get(row['fk'])
                if senses is None:
                    missing_fk.append(row['fk'])
                tree[si][pi] = senses
            else:
                tree[si][pi] = resolved.get(row['fsha'])
        senses, missing_si = _stitch_tree(tree, field)
        total_senses = len(tree)
        if not senses:
            still_missing[orig] = missing_fk
            results.append({'key': orig, 'card': None,
                            'error': 'topup-merge: 0/%d senses resolved' % total_senses,
                            'partial': True, 'missing_senses': total_senses,
                            'total_senses': total_senses})
            continue
        if missing_si:
            still_missing[orig] = missing_fk
        results.append({'key': orig,
                        'card': {'key1': orig, 'iast': c.get('iast'),
                                 'records': [{'h': c.get('h'), 'senses': senses}]},
                        'partial': bool(missing_si),
                        'missing_senses': len(missing_si), 'total_senses': total_senses})
    return results, still_missing


def cmd_topup(root, lang, wf_file):
    cards = topup_fragments(wf_file, lang)
    if not cards:
        print('no partial cards with missing_fragments (and recoverable frag_prov) in %s — '
              'nothing to top up' % wf_file)
        return
    fragkeys, missing_persist = [], {}
    for c in cards:
        orig = c['orig']
        _rp0, pp0 = input_paths(orig)
        portrait = read_text(pp0) if os.path.exists(pp0) else '[]'
        miss_fks = []
        for (si, pi, text) in c['missing']:
            fk = fk_of(orig, si, pi)
            rp2, pp2 = input_paths(fk)
            open(rp2, 'w', encoding='utf-8', newline='\n').write(text)
            open(pp2, 'w', encoding='utf-8', newline='\n').write(portrait)
            fragkeys.append(fk)
            miss_fks.append(fk)
        missing_persist[orig] = miss_fks
    # persistence mechanism: the missing-fragment file (same channel cmd_merge uses)
    mf = missing_file_path(lang, root)
    os.makedirs(os.path.dirname(mf), exist_ok=True)
    json.dump(missing_persist, open(mf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # topup manifest: self-contained for merge (full plan + resolved senses baked in)
    man = {'root': root, 'lang': lang, 'mode': 'topup',
           'field': 'russian' if lang == 'ru' else 'english',
           'cards': [{'orig': c['orig'], 'iast': c['iast'], 'h': c['h'],
                      'plan': [{'s': r['s'], 'p': r['p'], 'fsha': r['fsha'],
                                'fk': r['fk'], 'missing': r['missing']} for r in c['plan']],
                      'resolved': c['resolved']} for c in cards]}
    mpath = topup_manifest_path(lang, root)
    json.dump(man, open(mpath, 'w', encoding='utf-8'), ensure_ascii=False)
    out = os.path.join(HERE, 'run_pilot_wf.%s_%s_topup.js' % (lang, safe_name(root)))
    subprocess.run([sys.executable, os.path.join(HERE, 'gen_opt_harness2.py'), root,
                    '--nominal', '--no-grammar', '--lang=%s' % lang,
                    '--keys=' + ','.join(fragkeys), '--budget=1', '--out=' + out],
                   check=True, timeout=600)
    data = open(out, 'rb').read().replace(b'\r\n', b'\n').replace(b'\r', b'\n')  # LF for Workflow
    open(out, 'wb').write(data)
    total = sum(len(c['plan']) for c in cards)
    print('\ntopup: %d missing fragment(s) across %d partial card(s) — the other %d fragment(s) '
          'are reused from frag_prov/frag-TM (NOT re-translated)'
          % (len(fragkeys), len(cards), total - len(fragkeys)))
    print('manifest %s ; missing-file %s' % (mpath, mf))
    print('RUN via Workflow tool: %s' % out)
    print('then: python src/pilot/autosplit_requeue.py topup-merge %s %s <task_output>'
          % (root, lang))


def cmd_topup_merge(root, lang, task_file):
    field = 'russian' if lang == 'ru' else 'english'
    mpath = topup_manifest_path(lang, root)
    if not os.path.exists(mpath):
        sys.exit('no topup manifest %s — run `topup` first' % mpath)
    man = json.load(open(mpath, encoding='utf-8'))
    d = json.load(open(task_file, encoding='utf-8'))
    res = d.get('result') or d
    if isinstance(res, str):
        res = json.loads(res)
    got = {}
    for r in res.get('results') or []:
        if not r:
            continue
        c = r.get('card')
        got[r['key']] = ([s for rec in (c.get('records') or []) for s in (rec.get('senses') or [])]
                         if c else None)
    results, still_missing = stitch_topup(man['cards'], got, field)
    tag = 'en' if lang == 'en' else 'sc'
    out = os.path.join(REPO, 'wf_output.%s.%s.autosplit.json' % (tag, root))
    meta = _autosplit_meta(root, lang, 'autosplit_requeue.topup',
                           [c['orig'] for c in man['cards']])
    json.dump({'meta': meta, 'results': results}, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
    complete = [r for r in results if r.get('card') and not r['partial']]
    partial = [r['key'] for r in results if r['partial']]
    print('topup-merge: %d card(s) -> %d complete, %d still partial -> %s'
          % (len(results), len(complete), len(partial), out))
    if still_missing:
        mf = missing_file_path(lang, root)
        os.makedirs(os.path.dirname(mf), exist_ok=True)
        json.dump(still_missing, open(mf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('  still-missing fragment keys -> %s (re-run `topup` to target again)' % mf)
    print("then: python src/promote_final_cards.py --glob 'wf_output.%s.%s.autosplit.json' --merge"
          % (tag, root))


def cmd_test(root, keys):
    for k in keys:
        raw = read_text(input_paths(k)[0])
        pl = plan(raw)
        tier = ('0 whole' if len(pl) == 1 and pl[0][:2] == (0, 0) and _blocks(raw) is None
                else ('1/2 split -> %d frags' % len(pl)))
        print('%-24s raw=%-6d ls=%-3d senses=%s -> tier %s'
              % (k, len(raw), raw.count('<ls'), len({s for s, _, _ in pl}), tier))
        for si, pi, t in pl:
            sk, ph, _ = pwg_mask.mask(t)
            print('   s%dp%d: %d B, ls=%d, roundtrip=%s'
                  % (si, pi, len(t), t.count('<ls'), pwg_mask.restore(sk, ph) == t))


def cmd_gen(root, lang, keys):
    mpath = manifest_path(lang, root)
    os.makedirs(os.path.dirname(mpath), exist_ok=True)
    manifest, fragkeys = {}, []
    for k in keys:
        rp, pp = input_paths(k)
        raw = read_text(rp)
        portrait = read_text(pp) if os.path.exists(pp) else '[]'
        for si, pi, t in plan(raw):
            fk = fk_of(k, si, pi)
            rp2, pp2 = input_paths(fk)
            open(rp2, 'w', encoding='utf-8', newline='\n').write(t)
            open(pp2, 'w', encoding='utf-8', newline='\n').write(portrait)
            manifest[fk] = {'orig': k, 's': si, 'p': pi}
            fragkeys.append(fk)
    json.dump({'root': root, 'lang': lang, 'frags': manifest},
              open(mpath, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    out = os.path.join(HERE, 'run_pilot_wf.%s_%s_autosplit.js' % (lang, safe_name(root)))
    # --no-grammar: supplement fragments carry an empty portrait ([]) that nominal grammar
    # lookup can't key on; the fragment header already carries prefix/root context.
    subprocess.run([sys.executable, os.path.join(HERE, 'gen_opt_harness2.py'), root,
                    '--nominal', '--no-grammar', '--lang=%s' % lang,
                    '--keys=' + ','.join(fragkeys), '--budget=1', '--out=' + out],
                   check=True, timeout=600)
    data = open(out, 'rb').read().replace(b'\r\n', b'\n').replace(b'\r', b'\n')  # LF for Workflow
    open(out, 'wb').write(data)
    print('\n%d fragment(s) from %d card(s); manifest %s' % (len(fragkeys), len(keys), mpath))
    print('RUN via Workflow tool: %s' % out)


def cmd_merge(root, lang, task_file):
    field = 'russian' if lang == 'ru' else 'english'
    mpath = manifest_path(lang, root)
    if not os.path.exists(mpath):
        mpath = MANIFEST                        # legacy fallback: pre-per-root shared manifest
        legacy = json.load(open(mpath, encoding='utf-8'))
        if legacy.get('root') not in (root, safe_name(root)):
            sys.exit('MANIFEST MISMATCH: %s was generated for root %r, not %r — regenerate '
                     'with `gen` (the shared legacy manifest is a concurrency race; per-root '
                     'manifests fix this)' % (mpath, legacy.get('root'), root))
    man = json.load(open(mpath, encoding='utf-8'))['frags']
    d = json.load(open(task_file, encoding='utf-8'))
    res = d.get('result') or d
    if isinstance(res, str):
        res = json.loads(res)
    got = {r['key']: r.get('card') for r in (res.get('results') or []) if r}
    # regroup manifest by orig -> {sense_ord: {part_ord: fragkey}}
    tree = defaultdict(lambda: defaultdict(dict))
    for fk, info in man.items():
        tree[info['orig']][info['s']][info['p']] = fk
    results, skipped, partial, missing_frags = [], [], [], {}
    for orig, senses_map in tree.items():
        # Completeness guard is per SENSE, not per whole card — a giant flat headword (no
        # rootmap, e.g. large nominal stems like kAla/ka/SrI) can split into 100+ fragments,
        # where requiring ALL of them to succeed before keeping ANY drives joint success
        # probability toward zero even at a high per-fragment success rate (0.9^100 << 1%).
        # Skip only the senses whose fragments are still missing; keep the rest as partial
        # credit, and persist the missing fragment keys for a targeted follow-up requeue
        # (not a from-scratch re-run of the whole card).
        senses, iast, h, missing_si = [], None, None, []
        for si in sorted(senses_map):
            parts = senses_map[si]
            frs = [parts[pi] for pi in sorted(parts)]
            if any(got.get(fk) is None for fk in frs):
                missing_si.append(si)
                continue
            g_txt, t_txt, tag, extra = [], [], None, {}
            for pi in sorted(parts):
                card = got[parts[pi]]
                iast = iast or card.get('iast')
                for rec in card.get('records') or []:
                    h = h or rec.get('h')
                    for s in rec.get('senses') or []:
                        g_txt.append(s.get('german') or '')
                        t_txt.append(s.get(field) or '')
                        if tag is None:
                            tag = s.get('tag')
                            extra = {kk: s.get(kk) for kk in
                                     ('equivalence_type', 'source_type', 'stratum', 'differentia')}
            merged = {'tag': tag, 'german': '\n'.join(x for x in g_txt if x),
                      field: '\n'.join(x for x in t_txt if x)}
            merged.update({kk: vv for kk, vv in extra.items() if vv is not None})
            senses.append(merged)
        if not senses:
            # nothing at all resolved — but do NOT let the card exit the recovery funnel
            # unrecorded: persist its fragment keys exactly like a partial's (previously
            # they were only console-printed, so a fully-failed card had no
            # machine-readable requeue trail), and keep an accounted null row in results.
            skipped.append(orig)
            missing_frags[orig] = [fk for si in senses_map for fk in senses_map[si].values()]
            results.append({'key': orig, 'card': None,
                            'error': 'autosplit-merge: 0/%d senses resolved' % len(senses_map)})
            continue
        if missing_si:
            partial.append(orig)
            missing_frags[orig] = [fk for si in missing_si for fk in senses_map[si].values()]
        # post-stitch fidelity: reassembled counts vs the source card. Only meaningful on a
        # COMPLETE card — a partial merge legitimately has fewer <ls> than the source.
        src = read_text(input_paths(orig)[0])
        got_ls = sum(s['german'].count('<ls') for s in senses)
        drift = (not missing_si) and got_ls != src.count('<ls')
        if drift:
            print('  ! %s fidelity drift: <ls> %d vs source %d' % (orig, got_ls, src.count('<ls')))
        row = {'key': orig, 'card': {'key1': orig, 'iast': iast,
                                     'records': [{'h': h, 'senses': senses}]},
               'partial': bool(missing_si),
               'missing_senses': len(missing_si), 'total_senses': len(senses_map)}
        if drift:
            row['fidelity_drift'] = True       # kept, not dropped — but marked so audits can see it
        results.append(row)
    tag = 'en' if lang == 'en' else 'sc'
    out = os.path.join(REPO, 'wf_output.%s.%s.autosplit.json' % (tag, root))
    # selected_keys = the original cards this merge covers — audits reconstruct scope from
    # it (earlier autosplit outputs carried no key list, so a dropped card was invisible).
    # input_hashes/generated_at (H188): stamp the same source provenance a normal window
    # carries, so promoted autosplit rows are not SHA-less in the store.
    meta = _autosplit_meta(root, lang, 'autosplit_requeue', list(tree.keys()))
    json.dump({'meta': meta, 'results': results}, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
    ok = [r for r in results if r.get('card')]
    print('stitched %d card(s) (%d fully complete, %d partial); %d fully-empty kept as '
          'accounted nulls %s -> %s'
          % (len(ok), len(ok) - len(partial), len(partial), len(skipped), skipped or '', out))
    if missing_frags:
        mf = os.path.join(HERE, 'output', 'autosplit_missing_%s_%s.json' % (lang, safe_name(root)))
        os.makedirs(os.path.dirname(mf), exist_ok=True)
        json.dump(missing_frags, open(mf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('  partial: %s; fully-failed: %s -- missing fragment keys written to %s '
              'for a targeted follow-up requeue' % (partial or '-', skipped or '-', mf))
    print("then: python src/promote_final_cards.py --glob 'wf_output.%s.%s.autosplit.json' --merge"
          % (tag, root))


def cmd_selftest():
    """Pin the H188 provenance fix: both autosplit writers stamp per-card input_hashes
    (keyed by the original sub-card key) + generated_at, so promoted rows are not SHA-less."""
    import hashlib
    import tempfile
    global input_paths
    d = tempfile.mkdtemp()
    rawp = os.path.join(d, 'raw.bin')
    portp = os.path.join(d, 'port.bin')
    with open(rawp, 'wb') as f:
        f.write(b'RAW-SOURCE-vid')
    with open(portp, 'wb') as f:
        f.write(b'PORTRAIT-vid')
    orig_ip = input_paths
    try:
        input_paths = lambda k: (rawp, portp)                      # noqa: E731
        h = _stamp_input_hashes(['vid~~h0_10_ni'])
        assert 'vid~~h0_10_ni' in h, 'stamp must key by the ORIGINAL sub-card key'
        e = h['vid~~h0_10_ni']
        assert e['raw_sha256'] == hashlib.sha256(b'RAW-SOURCE-vid').hexdigest(), \
            'raw hash must match the canonical sha256_file the harness uses'
        assert e['portrait_sha256'] == hashlib.sha256(b'PORTRAIT-vid').hexdigest(), \
            'portrait hash must be stamped too'
        meta = _autosplit_meta('vid', 'ru', 'autosplit_requeue', ['vid~~h0_10_ni'])
        assert meta['input_hashes'] == h, 'meta must carry per-card input_hashes (H188)'
        assert meta['generated_at'], 'autosplit meta must stamp generated_at (was None before H188)'
        assert meta['selected_keys'] == ['vid~~h0_10_ni'] and meta['root'] == 'vid'
        # a ghost card whose source files are absent is skipped, never crashes the merge
        input_paths = lambda k: (os.path.join(d, 'nope.bin'), os.path.join(d, 'nope2.bin'))  # noqa: E731
        assert _stamp_input_hashes(['ghost']) == {}, 'absent source files -> no hash, no crash'
    finally:
        input_paths = orig_ip
    print('autosplit_requeue selftest OK')


def main():
    a = sys.argv[1:]
    if a[:1] == ['selftest']:
        return cmd_selftest()
    if len(a) < 3:
        sys.exit(__doc__)
    if a[0] == 'test':
        cmd_test(a[1], [k for k in a[2].split(',') if k])
    elif a[0] == 'gen':
        cmd_gen(a[1], a[2], [k for k in a[3].split(',') if k])
    elif a[0] == 'merge':
        cmd_merge(a[1], a[2], a[3])
    elif a[0] == 'topup':
        cmd_topup(a[1], a[2], a[3])
    elif a[0] == 'topup-merge':
        cmd_topup_merge(a[1], a[2], a[3])
    else:
        sys.exit('unknown mode %r' % a[0])


if __name__ == '__main__':
    main()
