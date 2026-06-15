#!/usr/bin/env python
"""pwg_ru stage-0 — PWG card extractor + placeholder masker (De→Ru, no API).

Walks csl-orig/v02/pwg/pwg.txt, splits it into <L>…<LEND> records, and masks
each record so a translator model sees ONLY translatable German. Everything
untranslatable — Sanskrit {#…#}, source refs <ls>, abbreviations <ab>, italic
Sanskrit <is>, grammar <lex>, foreign <lang>, structural tags — becomes a
{Tn} placeholder, restorable left-to-right after translation.

The hard case is `{%…%}`: in PWG it is overwhelmingly a GERMAN gloss (translate,
kept inline) — Latin is the rare exception (a cited cognate after "lat."/"griech."
or a Latin phrase like "De accentu comp."). The masker therefore DEFAULTS to
German and only masks high-confidence Latin, flagging anything ambiguous for the
LLM rather than guessing.

Modes:
  python pwg_mask.py stats  [N]        scan N records (default all) → counts
  python pwg_mask.py sample [N]        show N masked records (raw → skeleton + map)
  python pwg_mask.py card   <key1>     mask one record by key1
"""
import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PWG = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02', 'pwg', 'pwg.txt'))

# untranslatable PAIRED spans (tag + content both go) — order matters
PAIRED = [r'<ls>.*?</ls>', r'<ab>.*?</ab>', r'<is>.*?</is>', r'<lex>.*?</lex>',
          r'<lang\b[^>]*>.*?</lang>', r'\{#.*?#\}']
PAIRED_RE = re.compile('|'.join(PAIRED), re.S)
TAG_RE = re.compile(r'<[^>]+>')          # remaining structural/standalone tags
PCT_RE = re.compile(r'\{%(.*?)%\}', re.S)
HEADER_RE = re.compile(r'^<L>(\d+)<pc>(.*?)<k1>(.*?)<k2>(.*?)(?:<h>(\d+))?\s*$')
DE_CHARS = re.compile(r'[äöüßÄÖÜ]')
LATIN_CUE = re.compile(r'(lat\.|latein|griech|gr\.)\W{0,4}$', re.I)
LATIN_PHRASE = re.compile(r'^(De|Ab|Ex|In|Sub|Pro)\s+[a-z]', )  # Latin citation phrase
HOMOGRAPH = {'in', 'an', 'un', 'et', 'ut', 'a', 'i'}  # de/lat ambiguous short tokens


def records(limit=None):
    buf, n = [], 0
    with open(PWG, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('<L>'):
                buf = [line]
            elif line.startswith('<LEND>'):
                if buf:
                    yield buf
                    n += 1
                    if limit and n >= limit:
                        return
                buf = []
            elif buf:
                buf.append(line)


def parse(buf):
    m = HEADER_RE.match(buf[0])
    key1 = m.group(3) if m else ''
    key2 = m.group(4) if m else ''
    body = '\n'.join(buf[1:])
    return key1, key2, body


def classify_pct(content, preceding):
    """Return 'de' (translate, keep inline), 'la' (leave, placeholder),
    or 'ambig' (default-translate but flag)."""
    if LATIN_CUE.search(preceding.strip()):        # "…das lat. " / "griech. "
        return 'la'
    if LATIN_PHRASE.match(content) and not DE_CHARS.search(content):
        return 'la'
    toks = [t.strip('.,;') for t in content.lower().split()]
    if toks and all(t in HOMOGRAPH for t in toks) and not DE_CHARS.search(content):
        return 'ambig'
    return 'de'


def mask(body):
    ph = []
    stats = {'sanskrit_ls_ab': 0, 'tags': 0, 'pct_de': 0, 'pct_la': 0, 'pct_ambig': 0}

    def take(m):
        ph.append(m.group(0))
        return '{T%d}' % len(ph)

    # 1) paired untranslatable spans (Sanskrit / refs / abbrev / italic / foreign)
    def paired(m):
        stats['sanskrit_ls_ab'] += 1
        return take(m)
    body = PAIRED_RE.sub(paired, body)

    # 2) {%…%}: German kept inline, Latin masked, ambiguous flagged-but-kept
    out, last = [], 0
    for m in PCT_RE.finditer(body):
        out.append(body[last:m.start()])
        kind = classify_pct(m.group(1).strip(), body[max(0, m.start() - 35):m.start()])
        if kind == 'la':
            stats['pct_la'] += 1
            ph.append(m.group(0))
            out.append('{T%d}' % len(ph))
        else:
            stats['pct_de' if kind == 'de' else 'pct_ambig'] += 1
            out.append(m.group(0))          # keep inline for translation
        last = m.end()
    out.append(body[last:])
    body = ''.join(out)

    # 3) any remaining standalone tags (<div>, <H>, <F>, strays)
    def tag(m):
        stats['tags'] += 1
        return take(m)
    body = TAG_RE.sub(tag, body)
    return body, ph, stats


def restore(skeleton, ph):
    def back(m):
        return ph[int(m.group(1)) - 1]
    return re.sub(r'\{T(\d+)\}', back, skeleton)


# ---- CLI -----------------------------------------------------------------
def cmd_stats(args):
    n = int(args[0]) if args else None
    tot = 0
    agg = {'sanskrit_ls_ab': 0, 'tags': 0, 'pct_de': 0, 'pct_la': 0, 'pct_ambig': 0}
    roundtrip_ok = 0
    for buf in records(n):
        tot += 1
        key1, key2, body = parse(buf)
        sk, ph, st = mask(body)
        for k in agg:
            agg[k] += st[k]
        if restore(sk, ph) == body:
            roundtrip_ok += 1
    print('records scanned: %d' % tot)
    print('round-trip lossless (restore==original): %d/%d (%.2f%%)'
          % (roundtrip_ok, tot, 100.0 * roundtrip_ok / max(tot, 1)))
    print('placeholders by class:')
    for k, v in agg.items():
        print('  %-16s %d' % (k, v))
    pct = agg['pct_de'] + agg['pct_la'] + agg['pct_ambig']
    if pct:
        print('{%%..%%} German(translate) %d (%.1f%%) | Latin(leave) %d (%.1f%%) | ambiguous %d (%.1f%%)'
              % (agg['pct_de'], 100.0 * agg['pct_de'] / pct, agg['pct_la'],
                 100.0 * agg['pct_la'] / pct, agg['pct_ambig'], 100.0 * agg['pct_ambig'] / pct))


def cmd_sample(args):
    n = int(args[0]) if args else 5
    shown = 0
    for buf in records(2000):
        key1, key2, body = parse(buf)
        if '{%' not in body and '{#' not in body:
            continue
        sk, ph, st = mask(body)
        print('=' * 72)
        print('key1=%s key2=%s' % (key1, key2))
        print('--- raw ---\n%s' % body[:500])
        print('--- skeleton (model sees only this German) ---\n%s' % sk[:500])
        print('--- %d placeholders, e.g. ---' % len(ph))
        for i, p in enumerate(ph[:6], 1):
            print('  {T%d} = %s' % (i, p[:60]))
        shown += 1
        if shown >= n:
            break


def cmd_card(args):
    target = args[0]
    for buf in records():
        key1, key2, body = parse(buf)
        if key1 == target:
            sk, ph, st = mask(body)
            print('key1=%s key2=%s\n--- raw ---\n%s\n--- skeleton ---\n%s\n--- map ---' % (key1, key2, body, sk))
            for i, p in enumerate(ph, 1):
                print('  {T%d} = %s' % (i, p))
            print('round-trip OK:', restore(sk, ph) == body)
            return
    print('not found:', target)


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    {'stats': cmd_stats, 'sample': cmd_sample, 'card': cmd_card}.get(
        sys.argv[1], lambda *_: print(__doc__))(sys.argv[2:])


if __name__ == '__main__':
    main()
