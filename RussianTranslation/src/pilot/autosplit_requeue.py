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
"""
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
from window_common import input_paths, read_text          # noqa: E402
import pwg_mask                                            # noqa: E402
from safe_filename import safe_name                        # noqa: E402

LS_BUDGET = int(os.environ.get('AUTOSPLIT_LS_BUDGET', '18'))   # max <ls> per fragment (tier 2)
MANIFEST = os.path.join(HERE, 'output', 'autosplit_manifest.json')

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


def _cit_parts(block, ls_budget):
    """Split one (sub)sense block into parts each <= ls_budget <ls>, on line boundaries."""
    lines = block.split('\n')
    parts, cur, c = [], [], 0
    for l in lines:
        n = l.count('<ls')
        if cur and c + n > ls_budget:
            parts.append('\n'.join(cur)); cur, c = [], 0
        cur.append(l); c += n
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
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
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
              open(MANIFEST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    out = os.path.join(HERE, 'run_pilot_wf.%s_%s_autosplit.js' % (lang, safe_name(root)))
    # --no-grammar: supplement fragments carry an empty portrait ([]) that nominal grammar
    # lookup can't key on; the fragment header already carries prefix/root context.
    subprocess.run([sys.executable, os.path.join(HERE, 'gen_opt_harness2.py'), root,
                    '--nominal', '--no-grammar', '--lang=%s' % lang,
                    '--keys=' + ','.join(fragkeys), '--budget=1', '--out=' + out], check=True)
    data = open(out, 'rb').read().replace(b'\r\n', b'\n').replace(b'\r', b'\n')  # LF for Workflow
    open(out, 'wb').write(data)
    print('\n%d fragment(s) from %d card(s); manifest %s' % (len(fragkeys), len(keys), MANIFEST))
    print('RUN via Workflow tool: %s' % out)


def cmd_merge(root, lang, task_file):
    field = 'russian' if lang == 'ru' else 'english'
    man = json.load(open(MANIFEST, encoding='utf-8'))['frags']
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
            skipped.append(orig); continue     # nothing at all resolved -> truly skip
        if missing_si:
            partial.append(orig)
            missing_frags[orig] = [fk for si in missing_si for fk in senses_map[si].values()]
        # post-stitch fidelity: reassembled counts vs the source card. Only meaningful on a
        # COMPLETE card — a partial merge legitimately has fewer <ls> than the source.
        src = read_text(input_paths(orig)[0])
        got_ls = sum(s['german'].count('<ls') for s in senses)
        if not missing_si and got_ls != src.count('<ls'):
            print('  ! %s fidelity drift: <ls> %d vs source %d' % (orig, got_ls, src.count('<ls')))
        results.append({'key': orig, 'card': {'key1': orig, 'iast': iast,
                                              'records': [{'h': h, 'senses': senses}]},
                         'partial': bool(missing_si),
                         'missing_senses': len(missing_si), 'total_senses': len(senses_map)})
    tag = 'en' if lang == 'en' else 'sc'
    out = os.path.join(REPO, 'wf_output.%s.%s.autosplit.json' % (tag, root))
    meta = {'root': root, 'safe_root': safe_name(root), 'lang': lang,
            'generator': 'autosplit_requeue', 'schema_version': 'pwg_ru.workflow_meta.v1'}
    json.dump({'meta': meta, 'results': results}, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
    print('stitched %d card(s) (%d fully complete, %d partial); skipped %d fully-empty %s -> %s'
          % (len(results), len(results) - len(partial), len(partial), len(skipped), skipped or '', out))
    if partial:
        mf = os.path.join(HERE, 'output', 'autosplit_missing_%s_%s.json' % (lang, safe_name(root)))
        os.makedirs(os.path.dirname(mf), exist_ok=True)
        json.dump(missing_frags, open(mf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('  partial cards: %s -- missing fragment keys written to %s for a follow-up requeue'
              % (partial, mf))
    print("then: python src/promote_final_cards.py --glob 'wf_output.%s.%s.autosplit.json' --merge"
          % (tag, root))


def main():
    a = sys.argv[1:]
    if len(a) < 3:
        sys.exit(__doc__)
    if a[0] == 'test':
        cmd_test(a[1], [k for k in a[2].split(',') if k])
    elif a[0] == 'gen':
        cmd_gen(a[1], a[2], [k for k in a[3].split(',') if k])
    elif a[0] == 'merge':
        cmd_merge(a[1], a[2], a[3])
    else:
        sys.exit('unknown mode %r' % a[0])


if __name__ == '__main__':
    main()
