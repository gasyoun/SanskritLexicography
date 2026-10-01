#!/usr/bin/env python3
r"""deterministic_lane_census.py — Phase 0 of the deterministic-first remake (MG 24-08-2026).

Classifies every prepared untranslated card input into the lanes a NO-LLM route
could serve, reusing the production classifiers verbatim (no reimplementation, no
drift):

    A  exact-TM      raw-SHA hit in translation_memory.load_tm(lang) — the same
                     content-addressed lookup gen_opt_harness2 uses for its
                     zero-agent pre-resolution
    B  xref stub     degenerate_passthrough_card() — the production no-LLM lane
    C  short-residue candidate — after the production mask + the degenerate
                     probe's stripping, <= --max-residue-words translatable words
                     remain: composable from a future DE->RU term table
                     (the H2876 metalanguage library, grown to gloss vocabulary)
    E  prose         everything else: needs a model call today

Plus two health facts the census exists to surface:
  * TM sidecar size / hit rate as-found (a drained sidecar = lane A is dry);
  * the residue Zipf head — how many distinct German lemmas a term table must
    carry to cover X% of lane-C tokens.

Read-only over inputs; writes one dated .md + .json report pair.

    python src/pilot/deterministic_lane_census.py            # census + report
    python src/pilot/deterministic_lane_census.py --json     # stdout JSON only
"""
import argparse
import collections
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(RT, 'src')
for p in (HERE, SRC):
    if p not in sys.path:
        sys.path.insert(0, p)

import pwg_mask                                   # noqa: E402
import translation_memory as tm_mod               # noqa: E402
from window_common import INP, input_paths        # noqa: E402
from xref_vocab import DEGENERATE_XREF_WORDS      # noqa: E402
from gen_opt_harness2 import degenerate_passthrough_card  # noqa: E402

_REPORT_DIR = os.path.join(RT, 'reports')
_LAYER_LINE_RE = re.compile(r'^===\s*LAYER:.*$', re.M)
_OWNER_MAP_RE = re.compile(r'^===\s*LAYER:\s*NWS\s*—\s*PRE-PARSED OWNER MAP.*$',
                           re.M | re.I)
_OWNER_ENTRY_RE = re.compile(r'^\s*\d+\.\s*\[')
_EN_MARKERS = frozenset(('the', 'and', 'of', 'to', 'in', 'with', 'for'))


def _drop_owner_map_directive(skeleton):
    """Remove the OWNER MAP's English directive paragraph.

    The ``NWS — PRE-PARSED OWNER MAP`` layer embeds model-facing INSTRUCTIONS
    ('Emit EXACTLY one card row...') before its numbered entries. Those lines
    are prompt plumbing, not gloss — counting them as residue would inflate
    both the E-lane and the vocabulary head with harness prose.
    """
    m = _OWNER_MAP_RE.search(skeleton)
    if not m:
        return skeleton
    lines = skeleton[m.end():].splitlines(keepends=True)
    kept, in_directive = [], True
    for line in lines:
        if in_directive and _OWNER_ENTRY_RE.match(line):
            in_directive = False
        if not in_directive:
            kept.append(line)
    return skeleton[:m.start()] + ''.join(kept)


def strip_to_residue(skeleton):
    """Translatable-word residue of a masked skeleton.

    Mask semantics (pwg_mask): untranslatable spans (Sanskrit {#..#}, sigla
    <ls>/<ab>, grammar) become {Tn} placeholder tokens; the natural-language
    gloss stays inline — bare prose AND {%..%}-wrapped glosses alike. So the
    residue UNWRAPS {%..%}, drops {Tn}/tags/[..]/{#..#} (defensive), and removes
    the structural ``=== LAYER:`` header lines before scanning. Words in the
    closed degenerate-xref vocabulary and bare digits are dropped; everything
    else is translatable content (German or an NWS sub-source's English/French).
    """
    probe = _drop_owner_map_directive(skeleton)
    probe = _LAYER_LINE_RE.sub(' ', probe)
    probe = probe.replace('{%', ' ').replace('%}', ' ')
    for pattern in (r'\{#[^}]*#\}', r'<[^>]+>', r'\[[^\]]+\]', r'\{T\d+\}'):
        probe = re.sub(pattern, ' ', probe)
    words = [w.lower().strip('.:,;()"\'') for w in re.findall(
        r'[A-Za-zÄÖÜäöüß]+', probe)]
    out = []
    for w in words:
        if not w or w.isdigit():
            continue
        norm = (w.replace('ä', 'a').replace('ö', 'o')
                 .replace('ü', 'u').replace('ß', 'ss'))
        if w in DEGENERATE_XREF_WORDS or norm in DEGENERATE_XREF_WORDS:
            continue
        out.append(w)
    return out


def sha256_file(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def census(input_dir=INP, lang='ru', max_residue_words=3):
    cache = tm_mod.load_tm(lang)
    rows = []
    vocab = collections.Counter()
    lane_counts = collections.Counter()
    residue_len_hist = collections.Counter()
    names = sorted(f for f in os.listdir(input_dir) if f.endswith('.raw.txt')) \
        if os.path.isdir(input_dir) else []
    for fname in names:
        key = fname[:-len('.raw.txt')]
        rp, pp = input_paths(key, input_dir=input_dir)
        try:
            with open(rp, encoding='utf-8') as fh:
                raw = fh.read()
            with open(pp, encoding='utf-8') as fh:
                portrait = fh.read()
        except OSError as exc:
            rows.append({'key': key, 'lane': 'unreadable', 'why': str(exc)})
            lane_counts['unreadable'] += 1
            continue
        row = {'key': key}
        digest = sha256_file(rp)
        hit = cache.get('%s:%s' % (lang, digest))
        if hit and tm_card_sane(hit, lang, raw):
            row['lane'] = 'A_exact_tm'
        elif degenerate_passthrough_card(key, raw, portrait, 'russian'):
            row['lane'] = 'B_xref_stub'
        else:
            skel, _ph, _ok = pwg_mask.mask(raw)
            residue = strip_to_residue(skel)
            row['residue_words'] = len(residue)
            residue_len_hist[len(residue)] += 1
            vocab.update(residue)
            if _EN_MARKERS & set(residue):
                lane_counts['_cards_with_en_source_words'] += 1
            if len(residue) <= max_residue_words:
                row['lane'] = 'C_short_residue'
            else:
                row['lane'] = 'E_prose'
        lane_counts[row['lane']] += 1
        rows.append(row)
    return {'input_dir': input_dir, 'lang': lang,
            'tm_sidecar': tm_mod.tm_path(lang), 'tm_entries_loaded': len(cache),
            'cards': len(rows), 'lanes': dict(lane_counts),
            'residue_len_hist': dict(sorted(residue_len_hist.items())),
            'vocab_size': len(vocab), 'vocab_top': vocab.most_common(200),
            'rows': rows}


def tm_card_sane(hit, lang, raw):
    """Mirror gen_opt_harness2's tm_card_sane gate loosely: refuse entries whose
    card field for this lang is empty. The harness's full sanity gate runs again
    at generation time; the census only needs honest lane-A counts."""
    card = (hit or {}).get('card') or {}
    field = 'russian' if lang == 'ru' else 'english'
    senses = card.get('senses') or []
    return any((s or {}).get(field) for s in senses) if senses else bool(card.get(field))


def write_report(payload, out_dir=_REPORT_DIR, stamp=None):
    import datetime
    stamp = stamp or datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
    os.makedirs(out_dir, exist_ok=True)
    md_path = os.path.join(out_dir, 'DETERMINISTIC_LANE_CENSUS_%s.md' % stamp)
    js_path = os.path.join(out_dir, 'DETERMINISTIC_LANE_CENSUS_%s.json' % stamp)
    total = max(1, payload['cards'])
    lines = [
        '# Deterministic-lane census — %s (lang=%s)' % (stamp, payload['lang']),
        '',
        '_Phase 0 of the deterministic-first remake (MG 24-08-2026). Generated by '
        '`src/pilot/deterministic_lane_census.py` over `%s`; read-only._' % payload['input_dir'],
        '',
        '| lane | cards | share |',
        '|---|---|---|',
    ]
    labels = {
        'A_exact_tm': 'A — exact-TM (zero-token today)',
        'B_xref_stub': 'B — xref stub (degenerate pass-through)',
        'C_short_residue': 'C — short-residue candidate (term-table composable)',
        'E_prose': 'E — prose (needs a model today)',
        'unreadable': 'unreadable inputs',
    }
    for lane, label in labels.items():
        n = payload['lanes'].get(lane, 0)
        lines.append('| %s | %d | %.1f%% |' % (label, n, 100.0 * n / total))
    en_cards = payload['lanes'].get('_cards_with_en_source_words', 0)
    lines += [
        '',
        'Cards scanned: **%d** · TM entries loaded: **%d** (`%s`)'
        % (payload['cards'], payload['tm_entries_loaded'], payload['tm_sidecar']),
        '',
        'Language-mix caveat: %d card(s) carry English function words in their '
        'residue — NWS sub-source glosses are EN/FR, so a DE->RU table alone '
        'cannot cover them (compile_translatable already tags per-sense '
        'languages).' % en_cards,
        '',
        '## Residue vocabulary head (future DE->RU term table)',
        '',
        'Distinct residue lemmas: **%d**. Top of the Zipf head — a table covering '
        'these lemmas deterministically resolves the matching share of lane C/E '
        'tokens:' % payload['vocab_size'],
        '',
        '| lemma | count |',
        '|---|---|',
    ]
    for word, n in payload['vocab_top'][:40]:
        lines.append('| %s | %d |' % (word, n))
    with open(md_path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')
    slim = {k: v for k, v in payload.items() if k != 'rows'}
    slim['per_key'] = {r['key']: r.get('lane') for r in payload['rows']}
    with open(js_path, 'w', encoding='utf-8') as fh:
        json.dump(slim, fh, ensure_ascii=False, indent=1)
    return md_path, js_path


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--input-dir', default=os.environ.get('PWG_INPUT_DIR') or INP)
    ap.add_argument('--lang', default='ru', choices=('ru', 'en'))
    ap.add_argument('--max-residue-words', type=int, default=3)
    ap.add_argument('--json', action='store_true', help='print summary JSON to stdout')
    args = ap.parse_args()

    global _TAG_RE
    payload = census(input_dir=args.input_dir, lang=args.lang,
                     max_residue_words=args.max_residue_words)
    summary = {k: payload[k] for k in ('cards', 'lanes', 'residue_len_hist',
                                       'vocab_size', 'tm_entries_loaded')}
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    if not args.json:
        md_path, js_path = write_report(payload)
        print('report: %s\njson:   %s' % (md_path, js_path))


if __name__ == '__main__':
    main()
