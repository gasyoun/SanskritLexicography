#!/usr/bin/env python
"""pwg_ru microstructure — parse a PWG card into an Apresjan 'lexicographic portrait'.

Deterministic (no LLM). Turns a flat PWG record into:
  - a HOMONYM-keyed card (key1, h) — homographs no longer pool;
  - GRAMMAR (POS/gender from <lex>) + DIASYSTEM labels (<ab> ved./ep. …);
  - a SENSE TREE: numbered senses 1)/2), lettered sub-senses a)/b), each with its
    German equivalent(s) {%…%}, its <ls> citations resolved to STRATA, an
    equivalence-type tag (equivalent vs explanatory), and Sanskrit examples;
  - the corpus-attested NEAR-SYNONYM SET (stratified, translation-weighted) for the
    headword, ready for Apresjan discrimination.

  python microstructure.py card <key1> [h]
  python microstructure.py sample [N]      first N a-section homonym cards
  python microstructure.py export_sense_loci [out.tsv] [--limit N]
      H1456 — per-leaf-sense <ls>-loci export consumed by kosha's sense-
      reconciliation join (docs/PLAN_KOSHA_SENSE_RECONCILIATION_2026H2.md).
"""
import json, os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import pwg_mask
import corpus_gate as cg
import corpus_harvest as ch
import pwg_sources as ps   # authoritative <ls> abbreviation resolver (pwgbib)
import pwg_ab as pab       # authoritative <ab> abbreviation resolver (pwgab)
from government_census import extract_government  # H1624 G2: DE-side Rektion on portrait senses
from form_labels import extract_form_labels, extract_form_notes  # H1624 form layer
from citation_edges import extract_citation_edges               # H1624 G3

HERE = os.path.dirname(os.path.abspath(__file__))
LSMAP = json.load(open(os.path.join(HERE, 'ls_source_map.json'), encoding='utf-8'))
SCHEMA_VERSION = 'pwg_ru.lexicographic_portrait.v1'

LS = re.compile(r'<ls\b[^>]*>(.*?)</ls>', re.S)
LEX = re.compile(r'<lex>(.*?)</lex>', re.S)
ABFULL = re.compile(r'<ab\b([^>]*)>(.*?)</ab>', re.S)
NATTR_AB = re.compile(r'\bn\s*=\s*"([^"]*)"')
SA = re.compile(r'\{#(.*?)#\}', re.S)
PCT = re.compile(r'\{%(.*?)%\}', re.S)
# protect full citation/italic-Sanskrit spans too — a sense marker must never be
# found inside <ls>…</ls> (e.g. 'Lebensb. 233 (3).' is not a sense '3)').
PROT = re.compile(r'<ls\b[^>]*>.*?</ls>|<is\b[^>]*>.*?</is>|<[^>]+>|\{#.*?#\}|\{%.*?%\}', re.S)
# '〉' (RIGHT ANGLE BRACKET, "〉") is PWG's own closing sense-marker glyph --
# 87,680 occurrences in v02/pwg/pwg.txt (H879), overwhelmingly "digit〉"/"letter〉"
# (e.g. "1〉", "a〉"). ASCII ')' was the only variant ever matched here; senses
# marked with the angle form fell through to a single un-split segment (§447).
#
# H3948 / FINDINGS §453 -- PWG nests FOUR enumeration tiers, not two. The two
# added here follow §447's shape (one regex, one split_senses pass), but NOT
# §453's draft pattern `([0-9]{1,3}|[a-z]|[α-ωϑϰ]|[IVU])[)〉]`, which the
# corpus census refutes on three counts. Measured over all 123,366 <L> records
# with this module's own lookbehind + protected() spans applied
# (`python pwg_enum_tier_census.py`):
#
#   class        raw    lookbehind_ok   genuine   verdict
#   greek/glyph  1,516      1,426        1,426    real tier 3
#   greek/ascii     27          4            4    FALSE -- cross-refs ("u. δ)")
#   roman/glyph     48         29           29    real division tier
#   roman/ascii 21,537          5            0    FALSE -- "(Volume I)" &c.
#   digit3/ascii   340        241           22    FALSE -- "S. 367)", "(1917)"
#   digit3/glyph     0          0            0    the class does not exist
#
# Hence: (a) both new tiers are GLYPH-ONLY -- admitting ASCII ')' would inject
# ~11k false roman splits into live segmentation; (b) digit width stays {1,2},
# since no 3-digit glyph marker exists at all and widening buys only 22 false
# splits off page/year references; (c) roman markers are multi-character
# ([IV]+, attested I II III IV V), so §453's single-char [IVU] class misses 18
# of the 29 -- and its 'U' is a phantom: the corpus's one "U〉" sits inside a
# {#…#} Sanskrit span and is not a marker.
GREEK = 'α-ωϑϰ'
MARK = re.compile(
    r'(?<![^\s—])(?:(?P<t>\d{1,2}|[a-z])[)〉]|(?P<g>[' + GREEK + r']|[IV]+)〉)'
)   # preceded by space/—/start (NOT '(': that's citation-internal)
ROMAN_TOK = re.compile(r'^[IV]+$')
GREEK_TOK = re.compile(r'^[' + GREEK + r']$')


def mark_token(m):
    """The bare marker token of a MARK match, whichever tier matched."""
    return m.group('t') or m.group('g')


def header(buf):
    m = pwg_mask.HEADER_RE.match(buf[0])
    if not m:
        return '', '', ''
    return m.group(3), m.group(4), (m.group(5) or '')


def source_key(inner):
    out = []
    for t in re.sub(r'<[^>]+>', '', inner).strip().split():
        if any(c.isdigit() for c in t):
            break
        out.append(t)
        if len(out) >= 4:
            break
    return re.sub(r'\s+', ' ', ' '.join(out)).strip().rstrip('.').strip()


def strata_of(citations):
    # HARVEST stratum: only CORPUS-BACKED text sources, so the reader's corpus
    # Russian is pulled from a stratum we actually have. (A grammarian/lexicon
    # form-citation must not select a harvest stratum.)
    seen = {}
    for c in citations:
        rec = LSMAP.get(c)
        if rec and rec.get('harvestable') and rec.get('period'):
            seen[ch.norm_period(rec['period'])] = rec['name']
    return seen


# form-citation genres attest the WORD, not a dated usage → never a diasystem label
_FORM_CIT = ('Kośa', 'Vyākaraṇa', 'lexicon', 'nighaṇṭu')


def diasystem_of(citations):
    """Reader-facing diachronic label from ALL dated TEXT citations — including
    Vedic texts not in our corpus (Brāhmaṇas, Saṃhitās) — but excluding
    form-citation sources (grammars, kośas) so a Pāṇini form-cite cannot mislabel."""
    seen = set()
    for c in citations:
        rec = LSMAP.get(c)
        if not (rec and rec.get('period')):
            continue
        if any(t in (rec.get('genre') or '') for t in _FORM_CIT):
            continue
        seen.add(ch.norm_period(rec['period']))
    return seen


def clean_de(seg):
    s = re.sub(r'<[^>]+>', ' ', seg)
    s = SA.sub(' ', s)
    s = PCT.sub(lambda m: m.group(1), s)
    s = re.sub(r'\{T\d+\}', '', s)
    s = re.sub(r'\b(\d{1,2}|[a-z])\)', '', s)
    return re.sub(r'\s+', ' ', s).strip(' ,;—-.')


def protected(body):
    return [(m.start(), m.end()) for m in PROT.finditer(body)]


def _division_is_childless(marks, i):
    """True when the roman division at marks[i] has no deeper marker under it.

    16 of the corpus's 29 roman divisions are childless (measured, H3948) -- e.g.
    {#sahas#} I〉/II〉/III〉 carry their sense text directly. Emitting those as
    n='0' heads the way a parent division is emitted would silently drop 16
    divisions of real content out of leaf_senses(), so the head/leaf decision is
    made per occurrence from the structure actually present, never guessed.
    """
    for _, tok in marks[i + 1:]:
        if ROMAN_TOK.match(tok):
            break
        return False
    return True


def split_senses(body):
    """Slice the body at sense markers that are NOT inside a protected span.

    Four tiers (H3948 / FINDINGS §453), outermost first:

        I〉      roman division -- ABOVE the digit tier, not a fourth sub-level
        1〉 1)   digit sense
        a〉 a)   latin sub-sense
        α〉      greek sub-sub-sense

    A node is {'div', 'n', 'sub', 'sub2', 'text'}. 'div' and 'sub2' are None for
    the two tiers that existed before this change, so every pre-existing (n, sub)
    consumer keeps its exact old values on every pre-existing record.
    """
    spans = protected(body)
    def inside(p):
        return any(a <= p < b for a, b in spans)
    marks = [(m.start(), mark_token(m)) for m in MARK.finditer(body) if not inside(m.start())]
    if not marks:
        return [{'div': None, 'n': '1', 'sub': None, 'sub2': None, 'text': body}]
    out, cur_div, cur_n, cur_sub = [], None, '1', None
    head = body[:marks[0][0]].strip()
    if clean_de(head):
        # pre-sense head (grammar/general)
        out.append({'div': None, 'n': '0', 'sub': None, 'sub2': None, 'text': head})
    for i, (pos, tok) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(body)
        text = body[pos:end]
        if ROMAN_TOK.match(tok):
            cur_div, cur_n, cur_sub = tok, '1', None
            childless = _division_is_childless(marks, i)
            out.append({'div': tok, 'n': None if childless else '0',
                        'sub': None, 'sub2': None, 'text': text})
        elif tok.isdigit():
            cur_n, cur_sub = tok, None
            out.append({'div': cur_div, 'n': tok, 'sub': None, 'sub2': None, 'text': text})
        elif GREEK_TOK.match(tok):
            out.append({'div': cur_div, 'n': cur_n, 'sub': cur_sub, 'sub2': tok, 'text': text})
        else:
            cur_sub = tok
            out.append({'div': cur_div, 'n': cur_n, 'sub': tok, 'sub2': None, 'text': text})
    return out


def sense_path(seg):
    """Flat sense id for a split_senses/sense_node node: div + n + sub + sub2.

    Pre-H3948 nodes carry div=sub2=None, so this returns exactly the old
    ``n + (sub or '')`` string for every sense the old parser could see -- the
    ids of the 11.6k already-promoted store rows do not move.
    """
    return ''.join(seg.get(k) or '' for k in ('div', 'n', 'sub', 'sub2'))


FUNC_DE = set('der die das den dem des ein eine einen einem eines und oder aber auf in an zu von '
              'mit bei nach für so als wie am im zum zur ist sind war auch nur noch nicht wo wenn '
              'dass vor über unter durch ohne um bis'.split())


def _is_func(s):
    toks = [t for t in re.sub(r'[^\wäöüßÄÖÜ ]', ' ', s.lower()).split() if t]
    return bool(toks) and all(t in FUNC_DE for t in toks)


def sense_node(seg):
    # headword equivalent(s) = {%German%} in the sub-sense HEAD: before the first
    # citation, outside (...) cross-refs, before a compound {#…#} interrupts the run,
    # and not a bare function word. (audit: anna≠'zubereiteter Reis', agni≠'der/auf/
    # und', arjuna≠ parenthetical 'die Morgenröthe'.)
    head = re.sub(r'\([^)]*\)', ' ', seg['text'].split('<ls', 1)[0])
    de, gl = [], list(PCT.finditer(head))
    if gl:
        nxt = SA.search(head, gl[0].end())          # first Sanskrit form after the first gloss
        cut = nxt.start() if nxt else len(head)
        for m in gl:
            g = clean_de(m.group(1))
            if m.start() < cut and g and not _is_func(g):
                de.append(g)
    gloss = clean_de(seg['text'])
    cites = [source_key(c) for c in LS.findall(seg['text'])]
    cites = [c for c in cites if c]
    examples = [s for s in SA.findall(seg['text'])][:4]
    grammar = [g.strip() for g in LEX.findall(seg['text'])]
    ab_labels, dia = [], set()
    for attrs, content in ABFULL.findall(seg['text']):
        nm = NATTR_AB.search(attrs)
        tok = re.sub(r'<[^>]+>', '', content).strip()
        lab = nm.group(1) if nm else (pab.label(tok) or tok)
        if lab:
            ab_labels.append(lab)
            if pab.is_diasystem(lab):
                dia.add(lab)
    dia |= diasystem_of(cites)          # + diachronic label from dated text citations
    eq = 'equivalent' if (de and all(len(d.split()) <= 2 for d in de)) else \
         ('explanatory' if gloss else 'none')
    # H1624 G2: structured government from the full DE segment (not gloss_de[:200]).
    # Floor only — same extract_government as store/promote/government.html.
    government = extract_government(seg['text'])
    # H1624 form-layer: number / gender / voice (+ case_form in multi-axis list);
    # form_notes = dedicated nom/voc field.
    form_labels = extract_form_labels(seg['text'])
    form_notes = extract_form_notes(seg['text'])
    # H1624 G3: full citation edges (additive; raw <ls> stays in DE / gloss).
    citation_edges = extract_citation_edges(seg['text'])
    return {'div': seg.get('div'), 'n': seg['n'], 'sub': seg['sub'],
            'sub2': seg.get('sub2'), 'equivalents_de': de,
            'gloss_de': gloss[:200], 'equivalence_type': eq, 'grammar': grammar,
            'ab_labels': sorted(set(ab_labels)), 'diasystem': sorted(dia),
            'citations': sorted(set(cites)),
            'citations_resolved': {c: ps.resolve(c) for c in sorted(set(cites))},
            'strata': strata_of(cites), 'examples_sa': examples,
            'government': government,
            'form_labels': form_labels,
            'form_notes': form_notes,
            'citation_edges': citation_edges}


_CHIDX = None
def chidx():
    global _CHIDX
    if _CHIDX is None:
        _CHIDX = ch.index()
    return _CHIDX


def corpus_synonyms(key1):
    rows = chidx().get(cg.form_key(key1), [])
    if not rows:
        return None
    strata = ch.harvest(rows)
    # translation-weighted candidate set (precision: translation 87% > commentary 82%)
    cand = collections.Counter()
    for s in strata:
        for r in s['renderings']:
            if r.get('pos') == 'func':
                continue
            w = 1.0 if 'translation' in r.get('kinds', []) else 0.5
            cand[r['lemma']] += r['count'] * w
    return {'n': len(rows),
            'by_stratum': {s['period']: [r['lemma'] for r in s['renderings'][:5]
                                         if r.get('pos') != 'func'] for s in strata},
            'candidates': [w for w, _ in cand.most_common(12)]}


def portrait(buf):
    k1, k2, h = header(buf)
    body = '\n'.join(buf[1:])
    senses = [sense_node(s) for s in split_senses(body)]
    pos = sorted({g for s in senses for g in s['grammar']})
    dia = sorted({d for s in senses for d in s['diasystem']})
    labels = sorted({l for s in senses for l in s.get('ab_labels', []) if l not in dia})
    return {'schema_version': SCHEMA_VERSION,
            'key1': k1, 'key2': k2, 'h': h, 'iast': ''.join(cg._S2I.get(c, c) for c in cg.form_key(k1)),
            'pos': pos, 'diasystem': dia, 'labels': labels, 'senses': senses,
            'corpus_synonyms': corpus_synonyms(k1)}


def pretty(p):
    print('=' * 78)
    hh = ('  ·  homonym %s' % p['h']) if p['h'] else ''
    print('%s  (%s)%s   pos=%s   diasystem=%s' % (p['key1'], p['iast'], hh,
          '/'.join(p['pos']) or '–', '/'.join(p['diasystem']) or '–'))
    if p.get('labels'):
        print('  labels: %s' % ', '.join(p['labels'][:14]))
    print('  SENSE TREE:')
    for s in p['senses']:
        if s['n'] == '0':
            print('   · [head] %s' % s['gloss_de'][:120])
            continue
        tag = sense_path(s)
        strat = (' {%s}' % ', '.join(sorted(s['diasystem']))) if s.get('diasystem') else ''
        eqs = ' = ' + ' · '.join(s['equivalents_de']) if s['equivalents_de'] else ''
        print('   %-4s [%s]%s%s' % (tag + ')', s['equivalence_type'], eqs, strat))
        if s['equivalence_type'] == 'explanatory' and s['gloss_de']:
            print('         %s' % s['gloss_de'][:110])
        if s['citations']:
            cr = s.get('citations_resolved', {})
            print('         cited: %s' % ', '.join(
                '%s=%s' % (c, (cr.get(c) or '?').split(',')[0].split('(')[0].strip()[:22])
                for c in s['citations'][:6]))
    cs = p['corpus_synonyms']
    if cs:
        print('  CORPUS NEAR-SYNONYM SET (%d attestations, translation-weighted):' % cs['n'])
        print('    candidates: %s' % ' · '.join(cs['candidates']))
        for per, rends in cs['by_stratum'].items():
            if rends:
                print('    %-26s %s' % (per, ', '.join(rends)))
    else:
        print('  (no corpus attestation)')


# ---- H1456: PWG per-sense <ls>-loci export (kosha sense-reconciliation input) ----
# Contract (ARCHITECTURE_KOSHA_SENSE_RECONCILIATION.md, this export's sole external
# consumer): one row `slp1 hom sense_id gloss_de ls_loci` per leaf sense, `ls_loci`
# = that sense's <ls> citations `;`-joined VERBATIM (raw abbrev + locus). Resolving
# the abbreviation to a bibliographic source name is the *downstream* (kosha step 2)
# job, reusing this same pwg_sources.py — not done here.
LS_ATTR = re.compile(r'<ls\b([^>]*)>(.*?)</ls>', re.S)


def _cite_clean(s):
    s = re.sub(r'<lb[^>]*>', ' ', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', s).strip().rstrip('.').strip()


def ls_citations(text):
    """Verbatim <ls> citation strings for one sense segment. A continuation
    citation like <ls n="PAÑCAT.">252,10</ls> carries its source in the `n=`
    attribute, not the inner text (PWG convention for repeated-source runs) —
    reattach it so the citation stays self-contained rather than a bare,
    sourceless locus."""
    out = []
    for attrs, inner in LS_ATTR.findall(text):
        nm = NATTR_AB.search(attrs)
        src = _cite_clean(nm.group(1)) if nm else ''
        loc = _cite_clean(inner)
        cite = ('%s %s' % (src, loc)).strip() if src else loc
        if cite:
            out.append(cite)
    return out


# A PWG Nachträge (supplement) back-reference glues two markers directly
# together with no separating space — "1〉b〉 <ls>…</ls>." pointing at an
# EXISTING sense 1b of the main entry (2,273 occurrences in pwg.txt). MARK's
# lookbehind requires whitespace/—/start before a marker, so the second
# marker (immediately after the first's closing glyph) is invisible to
# split_senses and the whole addendum silently falls into sense '1' instead
# of '1b' — misattributing its <ls> locus to the wrong sense. Insert the
# missing space so split_senses sees both markers; scoped to this export's
# own body copy only, never touching the shared split_senses/MARK used by
# sense_node/portrait elsewhere in this file.
# H3948: the lookahead must know all four tiers, or a glued chain splits only
# as far as the tiers it recognises — the corpus carries 'c〉α〉', '4〉b〉α〉',
# 'II〉1〉a〉'. Mirrors MARK's own closer rules: ASCII ')' for digit/latin only.
ADJACENT_MARKERS = re.compile(
    r'([)〉])(?=(?:\d{1,2}|[a-z])[)〉]|(?:[' + GREEK + r']|[IV]+)〉)')


def leaf_senses(buf):
    """Yield (slp1, hom, sense_id, gloss_de, ls_loci) for one PWG record's
    numbered/lettered leaf senses. `sense_id` = the microstructure sense path
    (div + n + sub + sub2, e.g. '1a'/'1b'/'3a', and since H3948 also '2aα',
    'II1a', or a bare 'III' for a childless roman division). Note: PWG
    Nachträge (supplement) entries
    reference an existing sense by number in their OWN <L> record (e.g. a
    bare "1〉b〉 <ls>…</ls>" addendum) — such a record contributes an
    ADDITIONAL row under the same (slp1, hom, sense_id) key, not a merge; a
    consumer wanting the full loci set for a sense must group by that key."""
    k1, k2, h = header(buf)
    if not k1:
        return
    slp1 = cg.form_key(k1)
    body = ADJACENT_MARKERS.sub(r'\1 ', '\n'.join(buf[1:]))
    for seg in split_senses(body):
        if seg['n'] == '0':
            continue  # pre-sense head text — not a numbered/lettered leaf sense
        sense_id = sense_path(seg)
        gloss_de = clean_de(seg['text'])[:200]
        ls_loci = ';'.join(ls_citations(seg['text']))
        yield slp1, h, sense_id, gloss_de, ls_loci


def cmd_export_sense_loci(args):
    args = list(args)
    limit = None
    if '--limit' in args:
        i = args.index('--limit')
        limit = int(args[i + 1])
        del args[i:i + 2]
    out_path = args[0] if args else os.path.join(HERE, 'pwg_sense_loci.tsv')
    n_records = n_rows = 0
    headwords = set()
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('slp1\thom\tsense_id\tgloss_de\tls_loci\n')
        for buf in pwg_mask.records(limit):
            n_records += 1
            for slp1, hom, sense_id, gloss_de, ls_loci in leaf_senses(buf):
                f.write('%s\t%s\t%s\t%s\t%s\n' % (slp1, hom, sense_id, gloss_de, ls_loci))
                n_rows += 1
                headwords.add(slp1)
    print('records scanned: %d' % n_records, file=sys.stderr)
    print('leaf-sense rows: %d' % n_rows, file=sys.stderr)
    print('distinct headwords (slp1): %d' % len(headwords), file=sys.stderr)
    print('written: %s' % out_path, file=sys.stderr)


def cmd_card(args):
    target = args[0]
    h = args[1] if len(args) > 1 else None
    for buf in pwg_mask.records():
        k1, k2, hh = header(buf)
        if k1 == target and (h is None or hh == h):
            pretty(portrait(buf))
            if h is None:
                continue   # show all homonyms
    return


def cmd_sample(args):
    n = int(args[0]) if args else 6
    shown = 0
    for buf in pwg_mask.records(400):
        pretty(portrait(buf))
        shown += 1
        if shown >= n:
            break


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    {'card': cmd_card, 'sample': cmd_sample,
     'export_sense_loci': cmd_export_sense_loci}.get(
        sys.argv[1], lambda *_: print(__doc__))(sys.argv[2:])


if __name__ == '__main__':
    main()
