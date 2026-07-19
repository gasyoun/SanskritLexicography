#!/usr/bin/env python
"""Deterministic cleanup of stray German connectives left in the Russian field.

The translator occasionally leaves a lone German function word (und, mit, auch,
ohne) or the fixed phrase "fehlerhaft für" in a cross-reference / corrigendum
tail. These are a small CLOSED set with unambiguous Russian equivalents, so they
are fixed deterministically here rather than by spending another LLM re-run
(Python owns the markup/cleanup; the model only translates).

Substitutions apply ONLY to free text — never inside retained markup
({%German%}, {#Sanskrit#}, <ab>/<ls>/<is>) or inside «…» verbatim German quotes
(which a corrigendum may be pointing at and must keep). Ambiguous multi-word
German phrases (e.g. "aber nur in der Saṃhitā") are deliberately left for review.

  python src/pilot/fix_german_connectives.py wf_output.json [--dry-run]
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Spans that must never be touched: retained markup + «…» German quotes.
PROTECTED = re.compile(
    r'\{%.*?%\}|\{#.*?#\}|<(?:ab|ls|is)\b[^>]*>.*?</(?:ab|ls|is)>'
    r'|<(?:ab|ls|is)\b[^>]*>|«[^»]*»', re.S | re.I)

# Phrase substitutions first (longest match wins), then lone connectives. Each is
# a whole-word ASCII match so it can never land inside a Cyrillic or Sanskrit word.
PHRASES = [
    (re.compile(r'\bfehlerhaft\s+für\b'), 'ошибочно вместо'),
]
CONNECTIVES = [
    (re.compile(r'\bund\b'), 'и'),
    (re.compile(r'\bmit\b'), 'с'),
    (re.compile(r'\bohne\b'), 'без'),
    (re.compile(r'\bauch\b'), 'также'),
    (re.compile(r'\boder\b'), 'или'),
]


def fix_text(text):
    if not text:
        return text, 0
    out, n, last = [], 0, 0
    for m in PROTECTED.finditer(text):
        seg = text[last:m.start()]
        seg, c = _sub_segment(seg)
        n += c
        out.append(seg)
        out.append(m.group(0))
        last = m.end()
    tail, c = _sub_segment(text[last:])
    n += c
    out.append(tail)
    return ''.join(out), n


def _sub_segment(seg):
    n = 0
    for pat, repl in PHRASES + CONNECTIVES:
        seg, c = pat.subn(repl, seg)
        n += c
    return seg, n


# ---------------------------------------------------------------------------
# Store mode (H1302): apply the DETERMINISTIC German-prose-residue subs (class 'a')
# directly to the RU field of every row in the canonical pwg_ru store. The
# context-sensitive patterns (citation zu/bei, "Mit {#prefix#}" header, fixed
# phrases) are imported from german_residue_scan so the detector and the fixer can
# never drift; the lone connectives run in free text only (protected spans masked).
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
_SRC = os.path.dirname(_HERE)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

# lone connectives with an unambiguous single Russian equivalent (bare "mit" is
# deliberately EXCLUDED here -- store-wide it collides with grammatical "mit dem
# <ab>acc.</ab>"; capital "Mit {#prefix#}" headers are handled by MIT_HEADER instead).
LONE_STORE = [
    (re.compile(r'\bund\b'), 'и'),
    (re.compile(r'\boder\b'), 'или'),
    (re.compile(r'\bohne\b'), 'без'),
    (re.compile(r'\bauch\b'), 'также'),
]


def _sub_free_only(text, subs, protected):
    """Apply (pattern, repl) subs ONLY to text outside protected spans."""
    out, n, last = [], 0, 0
    for m in protected.finditer(text):
        seg = text[last:m.start()]
        for pat, repl in subs:
            seg, c = pat.subn(repl, seg)
            n += c
        out.append(seg)
        out.append(m.group(0))
        last = m.end()
    seg = text[last:]
    for pat, repl in subs:
        seg, c = pat.subn(repl, seg)
        n += c
    out.append(seg)
    return ''.join(out), n


def fix_ru_store(text):
    """Return (fixed_text, n_subs) applying the H1302 deterministic class-'a' residue subs."""
    from german_residue_scan import (
        CITATION_ZU, CITATION_BEI, MIT_HEADER, MIT_ERGAENZUNG, FEHLERHAFT_FUER,
        PROTECTED as SCAN_PROTECTED)
    if not text:
        return text, 0
    n = 0
    # 1) context-sensitive subs on the FULL text (tags intact, needed by the patterns).
    text, c = MIT_ERGAENZUNG.subn('с восполнением', text); n += c
    text, c = FEHLERHAFT_FUER.subn('ошибочно вместо', text); n += c
    text, c = CITATION_ZU.subn(r'\1к\2', text); n += c
    text, c = CITATION_BEI.subn(r'у\1', text); n += c
    text, c = MIT_HEADER.subn('С', text); n += c
    # 2) lone connectives in free text only (protected spans masked).
    text, c = _sub_free_only(text, LONE_STORE, SCAN_PROTECTED); n += c
    return text, n


def run_store(dry=False):
    from store_path import canonical_store
    default_local = os.path.join(_SRC, 'pwg_ru_translated.jsonl')
    store = canonical_store(default_local)
    if not os.path.exists(store):
        sys.exit('STORE ABSENT: %s' % store)
    rows = []
    with open(store, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line:
                rows.append(json.loads(line))
    total, touched = 0, []
    for r in rows:
        new, n = fix_ru_store(r.get('ru', '') or '')
        if n:
            total += n
            touched.append(('%s|%s|%s' % (r.get('key1'), r.get('subcard'), r.get('sense_tag')), n))
            if not dry:
                r['ru'] = new
    print('STORE MODE %s' % ('(DRY RUN)' if dry else ''))
    print('store           : %s' % store)
    print('rows            : %d' % len(rows))
    print('rows touched    : %d' % len(touched))
    print('substitutions   : %d' % total)
    for k, n in touched[:30]:
        print('  %-40s %d' % (k, n))
    if len(touched) > 30:
        print('  … (%d more rows)' % (len(touched) - 30))
    if not dry and total:
        bak = store + '.h1302.bak'
        if not os.path.exists(bak):
            import shutil
            shutil.copyfile(store, bak)
            print('backup          : %s' % bak)
        tmp = store + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        os.replace(tmp, store)
        print('wrote           : %s' % store)


def main():
    if '--store' in sys.argv:
        run_store(dry='--dry-run' in sys.argv)
        return
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    if not args:
        sys.exit('usage: python src/pilot/fix_german_connectives.py wf_output.json [--dry-run]\n'
                 '   or: python src/pilot/fix_german_connectives.py --store [--dry-run]')
    path = args[0]
    data = json.load(open(path, encoding='utf-8'))
    total, touched = 0, []
    for r in data.get('results', []):
        card = r.get('card') or {}
        for rec in card.get('records', []):
            for s in rec.get('senses', []):
                new, n = fix_text(s.get('russian', '') or '')
                if n:
                    total += n
                    touched.append((r.get('key'), n))
                    if not dry:
                        s['russian'] = new
    print('cards touched : %d | substitutions : %d%s'
          % (len(touched), total, ' (DRY RUN)' if dry else ''))
    for k, n in touched:
        print('  %-26s %d' % (k, n))
    if not dry and total:
        json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False)
        print('wrote', path)


if __name__ == '__main__':
    main()
