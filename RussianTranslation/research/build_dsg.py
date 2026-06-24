#-*- coding:utf-8 -*-
"""build_dsg.py — ingest Abhyankar's *Dictionary of Sanskrit Grammar* (DSG) and emit a
deep-linkable static site + crosswalks, so DSG (samskrtam.ru/sanskrit-lexicon/dsg/) can be
reused and interlinked with the affix tooling, the WhitneyRoots reader, and the CDSL spine.

STABLE PER-TERM LINK SCHEME (the thing to standardise):
  each DSG entry gets an SLP1 anchor on a single static page →  …/dsg/#t-<slp1>
  e.g. ghañ → #t-GaY, ṇvul → #t-Rvul, kta → #t-kta. SLP1 is ASCII (URL-safe, no %-encoding),
  unique, and reversible — the same key the whole sanskrit-lexicon ecosystem uses (<k1>), so
  DSG↔MW↔Apte↔roots all join on it. No server needed: one page + #anchors = durable deep links.

  python build_dsg.py anchors
      (no source needed) -> affix_dsg_anchors.tsv : the 27 affix pratyayas -> SLP1 anchor + URL,
      the crosswalk seed that lets the affix explorer/poster/quiz link to DSG the moment it ships.

  python build_dsg.py ingest <dsg_source.txt>
      parse the CDSL <L>/<k1> digitization (drop it under research/external/ or pass a path) ->
        dsg.json                 structured {k1(slp1), term_iast, term_deva, body, slug}
        dsg.html                 deep-linkable static page (id="t-<slp1>" per entry) for samskrtam.ru
        dsg_affix_crosswalk.tsv  affix pratyaya -> DSG entry (verified present), for live linking
"""
from __future__ import print_function
import os, re, sys, json

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'WhitneyRoots', 'scripts'))
from sanskrit_util import to_slp1, iast_to_devanagari   # noqa: E402

DSG_BASE = 'https://samskrtam.ru/sanskrit-lexicon/dsg/'


def slp1(iast):
    try:
        return to_slp1(iast)
    except Exception:
        return ''


def anchors():
    """Crosswalk SEED: affix pratyaya (IAST) -> SLP1 anchor + DSG deep-link. No DSG file needed."""
    ped = json.load(open(os.path.join(HERE, 'affix_pedagogy.json'), encoding='utf-8'))
    out = os.path.join(HERE, 'affix_dsg_anchors.tsv')
    n = 0
    with open(out, 'w', encoding='utf-8') as f:
        f.write('pratyaya\tpratyaya_deva\tslp1_anchor\tdsg_url\n')
        for a in ped['affixes']:
            anc = slp1(a['pratyaya'])
            f.write('%s\t%s\t%s\t%s#t-%s\n' % (a['pratyaya'], a['pratyaya_deva'], anc, DSG_BASE, anc))
            n += 1
    print('wrote %s (%d affix→DSG anchors). Verify against dsg.json once the source lands.' % (out, n))


def read_records(path):
    """Parse CDSL <L>…<LEND> records -> list of {k1, k2, body}."""
    recs = []
    with open(path, encoding='utf-8') as fh:
        lines = [ln.rstrip('\r\n') for ln in fh]
    i = 0
    while i < len(lines):
        if lines[i].startswith('<L>'):
            j = i + 1
            while j < len(lines) and not lines[j].startswith('<LEND>'):
                j += 1
            meta = lines[i]
            k1 = (re.search(r'<k1>([^<]*)', meta) or [None, ''])[1]
            k2 = (re.search(r'<k2>([^<]*)', meta) or [None, ''])[1]
            recs.append({'k1': k1, 'k2': k2, 'body': '\n'.join(lines[i + 1:j])})
            i = j + 1
        else:
            i += 1
    return recs


def ingest(path):
    if not os.path.exists(path):
        sys.exit('DSG source not found: %s\nDrop the CDSL DSG digitization (<L>/<k1> .txt) there '
                 'or pass its path. Then: python build_dsg.py ingest <path>' % path)
    recs = read_records(path)
    if not recs:
        sys.exit('No <L> records parsed from %s — is it the CDSL-format DSG digitization?' % path)
    entries = []
    for r in recs:
        k1 = r['k1']
        if not k1:
            continue
        entries.append({'k1': k1, 'slug': 't-' + k1,
                        'term_deva': iast_to_devanagari(r['k2'] or k1) if (r['k2'] or k1) else '',
                        'term_iast': r['k2'] or k1, 'body': r['body']})
    json.dump(entries, open(os.path.join(HERE, 'dsg.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    # deep-linkable static page
    rows = []
    for e in entries:
        body = re.sub(r'\{[#%][^}]*\}|<[^>]+>', lambda m: m.group(0), e['body'])  # keep markup verbatim for now
        rows.append('<section class="dsg-entry" id="%s"><h3>%s <span class="d">%s</span> '
                    '<a class="pl" href="#%s">#</a></h3><div class="b">%s</div></section>'
                    % (e['slug'], e['term_iast'], e['term_deva'], e['slug'],
                       body.replace('\n', '<br>')))
    html = ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>'
            '<meta name="viewport" content="width=device-width, initial-scale=1"/>'
            '<title>Abhyankar — A Dictionary of Sanskrit Grammar (DSG)</title><style>'
            'body{font-family:system-ui,sans-serif;max-width:780px;margin:1.5rem auto;padding:0 1rem;}'
            '.dsg-entry{border-bottom:1px solid #ddd;padding:.5rem 0;}.dsg-entry h3{margin:.2rem 0;font-size:16px;}'
            '.dsg-entry .d{color:#534ab7;}.pl{color:#aaa;text-decoration:none;font-size:12px;}'
            '.dsg-entry:target{background:#fff7e0;}#q{width:100%;padding:8px;margin-bottom:1rem;}'
            '</style></head><body><h1>A Dictionary of Sanskrit Grammar — Abhyankar (1961)</h1>'
            '<input id="q" placeholder="filter…" oninput="for(const s of document.querySelectorAll(\'.dsg-entry\'))'
            's.style.display=s.textContent.toLowerCase().includes(this.value.toLowerCase())?\'\':\'none\'"/>'
            + '\n'.join(rows) + '</body></html>')
    open(os.path.join(HERE, 'dsg.html'), 'w', encoding='utf-8').write(html)
    # affix crosswalk (verified present)
    ped = json.load(open(os.path.join(HERE, 'affix_pedagogy.json'), encoding='utf-8'))
    have = {e['k1'] for e in entries}
    out = os.path.join(HERE, 'dsg_affix_crosswalk.tsv')
    hit = 0
    with open(out, 'w', encoding='utf-8') as f:
        f.write('pratyaya\tslp1\tin_dsg\tdsg_url\n')
        for a in ped['affixes']:
            anc = slp1(a['pratyaya'])
            present = anc in have
            hit += present
            f.write('%s\t%s\t%s\t%s\n' % (a['pratyaya'], anc, 'Y' if present else 'N',
                    (DSG_BASE + '#t-' + anc) if present else ''))
    print('DSG ingest: %d entries -> dsg.json + dsg.html (deep-linkable #t-<slp1>) + %s'
          % (len(entries), os.path.basename(out)))
    print('  affix pratyayas found in DSG: %d / %d' % (hit, len(ped['affixes'])))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'anchors'
    if cmd == 'ingest':
        ingest(sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'external', 'dsg.txt'))
    else:
        anchors()
