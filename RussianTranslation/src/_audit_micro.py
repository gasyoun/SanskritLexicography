#!/usr/bin/env python
"""Quality audit of the microstructure parser over the a-section.

Reports parse health: cards, homonym split, sense-tree extraction, equivalence-type
distribution, authoritative <ls>/<ab> resolution rates, and anomalies (empty cards,
senses with neither gloss nor citation). No LLM.

  python _audit_micro.py [N]   scan first N records (default 2500, ~the a-section)
"""
import sys, collections, re
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import pwg_mask
import microstructure as M
import pwg_sources as ps
import pwg_ab as pab


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2500
    recs = cards = homonyms = senses = 0
    eq = collections.Counter()
    cite_tot = cite_res = ab_tot = ab_res = 0
    no_sense = []
    empty_sense = 0
    key1s = collections.Counter()
    parsefail = 0
    for buf in pwg_mask.records(n):
        recs += 1
        try:
            p = M.portrait(buf)
        except Exception as e:
            parsefail += 1
            continue
        cards += 1
        key1s[p['key1']] += 1
        if p['h']:
            homonyms += 1
        real = [s for s in p['senses'] if s['n'] != '0']
        if not real:
            no_sense.append(p['key1'])
        for s in real:
            senses += 1
            eq[s['equivalence_type']] += 1
            if not s['equivalents_de'] and not s['gloss_de'] and not s['citations']:
                empty_sense += 1
            for c in s['citations']:
                cite_tot += 1
                if ps.resolve(c):
                    cite_res += 1
        # <ab> resolution over the raw body
        for attrs, content in M.ABFULL.findall('\n'.join(buf[1:])):
            if M.NATTR_AB.search(attrs):
                continue
            tok = re.sub(r'<[^>]+>', '', content).strip()
            if tok:
                ab_tot += 1
                if pab.resolve(tok):
                    ab_res += 1

    multi = sum(1 for k, c in key1s.items() if c > 1)
    print('=== microstructure audit: first %d records ===' % recs)
    print('parsed cards: %d  (parse failures: %d)' % (cards, parsefail))
    print('homonym-numbered cards: %d  | headwords with >1 homonym: %d' % (homonyms, multi))
    print('senses parsed: %d  (%.1f per card)' % (senses, senses / max(cards, 1)))
    print('equivalence-type: %s' % dict(eq))
    print('<ls> citations: %d, resolved %d (%.1f%%)'
          % (cite_tot, cite_res, 100.0 * cite_res / max(cite_tot, 1)))
    print('<ab> abbrevs: %d, resolved %d (%.1f%%)'
          % (ab_tot, ab_res, 100.0 * ab_res / max(ab_tot, 1)))
    print('ANOMALIES: cards with no real sense: %d %s | senses with no gloss+no cite: %d'
          % (len(no_sense), no_sense[:8], empty_sense))


if __name__ == '__main__':
    main()
