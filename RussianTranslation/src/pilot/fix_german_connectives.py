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


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    if not args:
        sys.exit('usage: python src/pilot/fix_german_connectives.py wf_output.json [--dry-run]')
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
