#!/usr/bin/env python
"""Pilot input — the FULL layered card (PWG + PW + SCH + PWKVN + NWS net-new).

Extends _pilot_gen.py from PWG-only to the whole supplement chain, so the translator
produces ONE Russian entry that is the union of all layers. Per card key:
  • PWG base record(s) + their Nachträge   → microstructure portrait + labeled raw
  • PW (revision) / SCH (Schmidt) / PWKVN   → raw, layer-labeled (from dict_merge)
  • NWS net-new fragment                    → the ~2013 cumulative addendum (if any)

Output: src/pilot/input/<safe>.portrait.json + <safe>.raw.txt (gitignored), where
<safe> = safe_name(key) — the shared reversible Windows-safe stem, so SLP1's
case-sensitive keys (api/Api/ApI, as/As/aS) and PWG keys containing characters
like "|" don't collide or become unwritable on Windows.

  python _pilot_gen_merged.py [key ...]              default: a small NWS-exercising batch
  python _pilot_gen_merged.py --manifest a           whole a-section, coverage-first order
  python _pilot_gen_merged.py --manifest a --limit 300   first 300 of that order (scale slice)
  python _pilot_gen_merged.py --root-split BU gam        explode giant roots into per-prefix sub-cards
  python _pilot_gen_merged.py --manifest freq --root-split   freq queue, auto-splitting giant roots

--manifest reads scale_route.py's scale_manifest.<section>.json (run scale_route first),
so input generation follows the same coverage-first HEAVY/LIGHT ordering the scale driver
uses. Resumable: keys whose .raw.txt already exists are skipped.
"""
import json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import microstructure as M
import dict_merge as dm
import corpus_gate as cg
import nws_split
from safe_filename import safe_name

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'pilot', 'input')

sys.path.insert(0, os.path.join(HERE, '..', 'research'))
import root_segment_proto as RS                 # the lossless <div n="p"> root slicer

# Only explode genuinely GIANT roots (the ones that kill a single-pass translation);
# small records with 1-2 prefix divisions stay whole.
MIN_SPLIT = int(os.environ.get('ROOT_SPLIT_MIN', '8'))
# Head-card sense-splitter: a head still over HEAD_BUDGET lines is split further — its
# simple-verb senses chunked at top-level sense boundaries, each supplement layer its own
# unit, and the NWS owner map batched NWS_BATCH entries at a time. (The 820-line bhū head
# overflowed a single 32k-token translation pass; these parts are single-pass-sized.)
HEAD_BUDGET = int(os.environ.get('HEAD_SPLIT_BUDGET', '100'))
HEAD_CIT_BUDGET = int(os.environ.get('HEAD_CIT_BUDGET', '18'))   # max <ls> per head sense-part
HEAD_CIT_BATCH_BUDGET = int(os.environ.get('HEAD_CIT_BATCH_BUDGET', str(HEAD_CIT_BUDGET)))
NWS_BATCH = int(os.environ.get('NWS_OWNER_BATCH', '25'))
SENSE_BOUND = re.compile(r'^<div n="\d+"> *\d+\)')

DEFAULT = ['arTa', 'agni', 'amfta', 'aMSa', 'anna', 'akzara']


ROLE = {'pw': 'PW — Böhtlingk kürzere Fassung (revision of PWG; may correct gender/sense)',
        'sch': 'SCH — Schmidt Nachträge 1928 (pure addenda to PW; °=new vs pw, *=first attestation)',
        'pwkvn': 'PWKVN — PWK variant supplement (keyed to PW sense numbers)',
        'nws': 'NWS — Nachtragswörterbuch (Halle, cumulative addendum; condensed "Kleines Zitat" '
               '— render the new lemma/sense/grammar + keep its sigla)'}


# A roman-numeral co-owner cite (e.g. `Hillebrandt 1885 : IV`) that nws_split's
# digit-only OWNER can't tag rides onto the next entry — into the gloss as a
# leading `<tag> ; Name : page > …` bleed, into the tag as a stray `; Name :
# page`, and leaving a punctuation-only lemma. The owner stays correct; these
# strip the cosmetic contamination so the translator sees a clean gloss/tag
# (mirrors compile_translatable.mask_nws_gloss for the owner-map consumer path).
_BLEED_LEAD = re.compile(r'^[\s,;]*[^>]*?;\s*[A-ZÀ-ÖØ-ÞĀ-ỿ][^>:]*?\s:\s[\dIVXLCDM]+[A-Za-z]?\s*>\s*')
_BLEED_TAG = re.compile(r'\s*[;,]?\s*[A-ZÀ-ÖØ-ÞĀ-ỿ][^;,]*?\s:\s(?:\d+[A-Za-z]?|[IVXLCDM]+)')


def nws_owner_map(key):
    """The AUTHORITATIVE deterministic NWS (owner, gloss) pairing from nws_split —
    so the translator NEVER re-derives owners (kills F12 by construction). Reads the
    just-written <safe>.raw.txt so it sees exactly what `nws_split.py check` will."""
    frag = nws_split.nws_fragment(key)
    if not frag:
        return ''
    entries = nws_split.split(frag)
    if not entries:
        return ''
    lines = []
    for i, e in enumerate(entries, 1):
        owner = ' / '.join(e.get('owners') or []) or '?'
        gloss = _BLEED_LEAD.sub('', re.sub(r'\s+', ' ', e.get('gloss') or '').strip())
        for o in (e.get('owners') or []):            # drop a trailing copy of the cite
            if gloss.endswith(o):
                gloss = gloss[:-len(o)].rstrip(' .;,')
        lem = (e.get('lemma') or '').strip()
        lemma = (' {#%s#}' % lem) if re.search(r'[\wĀ-ỿ]', lem) else ''   # drop punct-only lemma
        tg = _BLEED_TAG.sub('', e.get('tag') or '').strip(' ;,')          # drop bled-in cite
        tag = (' [%s]' % tg) if tg else ''
        lines.append('%2d. [NWS: %s]%s%s %s' % (i, owner, lemma, tag, gloss))
    return '\n'.join(lines)


def gen_card(key, pwg_idx, verbose=True):
    """Write <key>.portrait.json + <key>.raw.txt for one headword. Returns the
    per-layer record counts (incl. 'nws'), or None if the key is absent from PWG."""
    fk = cg.form_key(key)
    pwg_bufs = pwg_idx.get(fk, [])
    if not pwg_bufs:
        if verbose:
            print('  MISSING in PWG: %s' % key)
        return None

    # 1) PWG portrait (corpus evidence) + labeled raw records (main + Nachträge)
    portraits = [M.portrait(buf) for buf in pwg_bufs]
    json.dump(portraits, open(os.path.join(OUT, safe_name(key) + '.portrait.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    sections = []
    for i, buf in enumerate(pwg_bufs):
        role = ('PWG — MAIN ENTRY (Böhtlingk-Roth, large)' if i == 0 else
                'PWG — NACHTRÄGE/ADDENDA #%d — patches keyed to the main sense numbers; '
                'render in full' % i)
        sections.append('=== LAYER: %s ===\n\n%s' % (role, '\n'.join(buf[1:])))

    # 2) PW / SCH / PWKVN + NWS net-new layers (all from the merge), each labeled.
    #    dm.merged() now owns the NWS fold — it appends the external addendum last
    #    when (and only when) it adds beyond pw/Schmidt (has_nws_extra).
    layer_counts = {'pwg': len(pwg_bufs)}
    for L in dm.merged(key):
        code = L['layer']
        if code == 'pwg':
            continue
        layer_counts[code] = len(L['records'])
        for r in L['records']:
            sections.append('=== LAYER: %s ===\n\n%s' % (ROLE.get(code, code.upper()), r))

    raw_path = os.path.join(OUT, safe_name(key) + '.raw.txt')
    open(raw_path, 'w', encoding='utf-8').write('\n\n'.join(sections))

    # 3) append the AUTHORITATIVE deterministic NWS owner map (reads the file just
    #    written, so it matches the F12 gate exactly). The translator emits one row
    #    per entry with the owner verbatim — it does NOT re-derive owners.
    if layer_counts.get('nws'):
        omap = nws_owner_map(key)
        if omap:
            n_entries = omap.count('\n') + 1
            sections.append(
                '=== LAYER: NWS — PRE-PARSED OWNER MAP (AUTHORITATIVE, %d entries) ===\n\n'
                'Deterministic owner-to-gloss pairing (kills F12). Emit EXACTLY one card row\n'
                'per numbered entry below, in this order; copy its [NWS: OWNER] VERBATIM as the\n'
                'row’s last citation; translate the gloss from its own language; keep IAST/sigla.\n'
                'Do NOT re-derive owners from the raw fragment above.\n\n%s' % (n_entries, omap))
            open(raw_path, 'w', encoding='utf-8').write('\n\n'.join(sections))
            layer_counts['nws_map'] = n_entries
    if verbose:
        ns = sum(len([s for s in p['senses'] if s['n'] != '0']) for p in portraits)
        print('  %-10s PWG rec=%d senses=%d | PW=%d SCH=%d PWKVN=%d | NWS-extra=%s'
              % (key, len(pwg_bufs), ns, layer_counts.get('pw', 0), layer_counts.get('sch', 0),
                 layer_counts.get('pwkvn', 0), 'yes' if layer_counts.get('nws') else 'no'))
    return layer_counts


def chunk_lines(lines, budget):
    """Split lines into <= budget-line chunks, breaking only at <div / blank boundaries once
    the chunk reaches budget (hard cap at 2x budget so a boundary-less run can't overflow)."""
    cap = int(1.5 * budget)
    chunks, cur = [], []
    for ln in lines:
        brk = (len(cur) >= budget and (ln.startswith('<div') or not ln.strip())) or len(cur) >= cap
        if cur and brk:
            chunks.append(cur); cur = []
        cur.append(ln)
    if cur:
        chunks.append(cur)
    return chunks


def chunk_records(records, budget):
    """Group whole records so each group is <= budget lines; a single over-budget record is
    itself line-chunked rather than left to overflow."""
    groups, cur, n = [], [], 0
    for r in records:
        rl = r.count('\n') + 1
        if rl > budget:                              # huge single record -> line-chunk it alone
            if cur:
                groups.append(cur); cur, n = [], 0
            for piece in chunk_lines(r.split('\n'), budget):
                groups.append(['\n'.join(piece)])
            continue
        if cur and n + rl > budget:
            groups.append(cur); cur, n = [], 0
        cur.append(r); n += rl
    if cur:
        groups.append(cur)
    return groups


_SENSE_NUM = re.compile(r'<div n="[^"]*">\s*[—\-]?\s*(\d+)[〉)]')
# A secondary-conjugation section header (— <ab>caus.</ab> …) trailing the previous sense line.
_SEC_TAIL = re.compile(r'(\s*[—\-]\s*<ab>(?:caus|pass|desid|intens|partic|inf)\.?</ab>.*)$', re.I)
_SEC_HEAD = re.compile(r'^\s*[—\-]?\s*<ab>(caus|pass|desid|intens|partic|inf)\.?</ab>', re.I)
_SEC_LABEL = {'caus': 'CAUSATIVE', 'pass': 'PASSIVE', 'desid': 'DESIDERATIVE',
              'intens': 'INTENSIVE', 'partic': 'PARTICIPIAL', 'inf': 'INFINITIVE'}


def _sec_kind(chunk):
    """If a head chunk opens with a relocated secondary-conjugation marker, return its kind."""
    for ln in chunk:
        if ln.strip():
            m = _SEC_HEAD.match(ln)
            return m.group(1).lower() if m else None
    return None


def _sense_no(block):
    """The leading top-level sense number of a <div> block (the N in `N〉` / `N)`), or None."""
    m = _SENSE_NUM.search(block[0]) if block else None
    return int(m.group(1)) if m else None


# Any <div n=> sense marker — a top-level NUMBER (1, 2, …) or a lettered SUB-sense (a, b, …).
_SENSE_MARK = re.compile(r'<div n="[^"]*">\s*[—\-]?\s*([0-9]+|[a-z])\s*[〉)]')
_LS_CITE = re.compile(r'<ls\b.*?</ls>')


def _marker_tags(lines, top):
    """Canonical sense tags for the <div n=> markers in `lines`, threading the running
    top-level sense number `top` in from the preceding chunks. A NUMBER marker is a new
    top-level sense (tag = the number, and it becomes the new `top`); a LETTER marker is a
    SUB-sense of the current top-level sense (tag = "<top><letter>", e.g. under sense 9 the
    marker `c〉` → "9c"). This disambiguates the two separate <div n="2"> letter-blocks a PWG
    head can carry (sub-senses of different numbered senses), which collide under bare-letter
    or n-attribute tagging (TOKEN_OPTIMIZATION_2026-06-27.md Finding 10). Returns (tags, top)."""
    tags = []
    for ln in lines:
        m = _SENSE_MARK.search(ln)
        if not m:
            continue
        lab = m.group(1)
        if lab.isdigit():
            top = int(lab)
            tags.append(str(top))
        else:
            tags.append('%d%s' % (top, lab) if top else lab)
    return tags, top


def _split_text_by_cites(text, budget, first_budget=None):
    """Split `text` after <ls> citations so each piece has <= budget citations.
    Non-citation text rides with the nearest preceding citation; a final citation-free
    tail rides with the last piece."""
    if budget <= 0:
        return [text]
    first_budget = budget if first_budget is None else max(1, first_budget)
    pieces, start, count = [], 0, 0
    for m in _LS_CITE.finditer(text):
        count += 1
        limit = first_budget if not pieces else budget
        if count >= limit:
            pieces.append(text[start:m.end()])
            start, count = m.end(), 0
    if start < len(text):
        if count == 0 and pieces:
            pieces[-1] += text[start:]
        else:
            pieces.append(text[start:])
    return [p for p in pieces if p.strip()]


def _citation_batches(block, tag, budget):
    """Split one over-budget sense block into citation batches.

    The original <div> marker is repeated on every batch so each translated sub-card
    remains self-contained and the per-card coverage gate still sees one expected sense.
    Introductory grammar/paradigm lines before the first <div> ride only with batch 1."""
    if not tag or '\n'.join(block).count('<ls') <= budget:
        return [block]
    div_i = None
    div_m = None
    for i, ln in enumerate(block):
        div_m = _SENSE_MARK.search(ln)
        if div_m:
            div_i = i
            break
    if div_i is None:
        return [block]
    intro = block[:div_i]
    marker = block[div_i][:div_m.end()]
    intro_cites = '\n'.join(intro).count('<ls')
    body = block[div_i][div_m.end():]
    if div_i + 1 < len(block):
        body += '\n' + '\n'.join(block[div_i + 1:])
    pieces = _split_text_by_cites(body, budget, budget - intro_cites)
    if len(pieces) <= 1:
        return [block]
    batches = []
    for i, piece in enumerate(pieces):
        lines = []
        if i == 0:
            lines.extend(intro)
        plines = piece.split('\n')
        lines.append(marker + plines[0])
        lines.extend(plines[1:])
        batches.append(lines)
    return batches


def sense_chunks(head_lines, cit_budget):
    """Split a PWG head at <div n=…> SENSE boundaries (NOT line count) and group consecutive
    senses until their combined <ls> citation count exceeds cit_budget — so every part is
    citation-LIGHT and renders single-pass without the model abridging the apparatus. A single
    sense heavier than the budget stays its own part (it cannot be split further). The grammar
    intro (lines before the first <div n=) rides with the first sense block. Falls back to the
    line chunker when the head has no <div n=> structure. (TOKEN_OPTIMIZATION_2026-06-27.md
    Finding 5: heads fail by citation DENSITY, not line length.)"""
    blocks, intro, cur = [], [], None
    for ln in head_lines:
        if ln.lstrip().startswith('<div n='):
            if cur is not None:
                blocks.append(cur)
            cur = [ln]
        elif cur is None:
            intro.append(ln)
        else:
            cur.append(ln)
    if cur is not None:
        blocks.append(cur)
    if not blocks:                                   # no sense divs → old line chunker
        return [{'lines': ch, 'batch_of': None} for ch in chunk_lines(head_lines, HEAD_BUDGET)]
    if intro:
        blocks[0] = intro + blocks[0]
    # A secondary-conjugation section (caus./pass./desid./intens.) RESTARTS sense
    # numbering at 1, and its <ab>caus.</ab> marker sits ONLY on its first sub-sense.
    # If a later chunk boundary falls inside that section, the orphaned sub-senses lose
    # the marker and the model mis-tags them as simple-verb senses (tyaj caus.2/3 → "2"/"3").
    # So merge everything from the first numbering reset into one trailing block.
    nums, prev, reset = [_sense_no(b) for b in blocks], 0, None
    for i, n in enumerate(nums):
        if n is not None:
            if prev >= 1 and n <= prev:              # numbering went backwards → secondary section
                reset = i
                break
            prev = n
    if reset is not None:
        tail = [ln for b in blocks[reset:] for ln in b]
        # The section marker (— <ab>caus.</ab> etc.) often rides at the END of the block just
        # before the reset (here on sense 9's line). Relocate it to the head of the merged tail
        # so the sub-senses keep their caus/pass/desid label and are not mis-tagged as 1/2/3.
        if reset > 0 and blocks[reset - 1]:
            m = _SEC_TAIL.search(blocks[reset - 1][-1])
            if m:
                blocks[reset - 1][-1] = blocks[reset - 1][-1][:m.start()].rstrip()
                tail = [m.group(1).strip()] + tail
        blocks = blocks[:reset] + [tail]
    chunks, g, gc = [], [], 0
    top = 0
    for b in blocks:
        bc = '\n'.join(b).count('<ls')
        btags, top = _marker_tags(b, top)
        if bc > cit_budget and len(btags) == 1:
            for batch in _citation_batches(b, btags[0], HEAD_CIT_BATCH_BUDGET):
                if g:
                    chunks.append({'lines': g, 'batch_of': None}); g, gc = [], 0
                chunks.append({'lines': batch, 'batch_of': btags[0]})
            continue
        if g and gc + bc > cit_budget:               # close the group before it overflows
            chunks.append({'lines': g, 'batch_of': None}); g, gc = [], 0
        g += b; gc += bc
    if g:
        chunks.append({'lines': g, 'batch_of': None})
    return chunks


def head_sense_parts(key, head_lines, hom, n_hom):
    """The PWG simple-verb head, split at sense boundaries to citation-light single-pass parts.
    hom = homonym index (0-based); when a headword has >1 homonym the label says so.
    -> [(section_label, blob), ...]."""
    parts = []
    chunks = sense_chunks(head_lines, HEAD_CIT_BUDGET)
    batch_counts = {}
    for ch in chunks:
        if ch.get('batch_of'):
            batch_counts[ch['batch_of']] = batch_counts.get(ch['batch_of'], 0) + 1
    batch_seen = {}
    htag = (' homonym %d' % (hom + 1)) if n_hom > 1 else ''
    top = 0                                           # running top-level sense number across chunks
    for i, chunk in enumerate(chunks):
        ch = chunk['lines']
        ptag = (' part %d/%d' % (i + 1, len(chunks))) if len(chunks) > 1 else ''
        kind = _sec_kind(ch)                          # caus/pass/desid/intens tail, or None
        ctags, top = _marker_tags(ch, top)            # canonical tags for this chunk's senses
        meta = {}
        label = 'pwg%02d' % i
        if chunk.get('batch_of'):
            bo = chunk['batch_of']
            bi = batch_seen.get(bo, 0)
            batch_seen[bo] = bi + 1
            bc = batch_counts[bo]
            label = 'pwg%02db%02d' % (i - bi, bi)
            meta = {'batch_of': bo, 'batch_index': bi, 'batch_count': bc}
            ptag += ' citation batch %d/%d for sense %s' % (bi + 1, bc, bo)
        if kind:
            tag = ('PWG-ROOT HEAD%s%s — root=%s (%s SECONDARY-CONJUGATION senses; PWG restarts '
                   'numbering at 1 here, so tag EACH sense "%s. N" (%s. 1, %s. 2 …), NEVER bare '
                   '1/2/3, and keep the <ab>%s.</ab> marker in the German)'
                   % (htag, ptag, key, _SEC_LABEL.get(kind, kind.upper()), kind, kind, kind, kind))
        else:
            # Explicit canonical sense tag(s) for this part — render EXACTLY these, no more, no
            # fewer, tag each verbatim. Stops prefix-drift / fabricated sub-letters across the two
            # <div n="2"> letter-blocks a head can carry (Finding 10).
            directive = ''
            if ctags:
                if meta:
                    directive = (' — CITATION BATCH %d/%d for canonical sense %s: render ONLY '
                                 'sense %s, tag it VERBATIM as "%s", preserve EVERY literary-source '
                                 'tag and EVERY Sanskrit brace span present in this batch, add no '
                                 'other senses, and do not summarize the citation apparatus'
                                 % (meta['batch_index'] + 1, meta['batch_count'], meta['batch_of'],
                                    meta['batch_of'], meta['batch_of']))
                else:
                    directive = (' — render EXACTLY these %d sense(s), tag each VERBATIM as listed, '
                                 'add no others and split none: [%s]. A lettered sub-sense is tagged '
                                 '<enclosing sense number><letter> (e.g. under sense 9, "c" -> "9c"); '
                                 'never tag it bare, never use the <div n=> attribute as the number, '
                                 'never invent a sub-letter not listed'
                                 % (len(ctags), ', '.join(ctags)))
            tag = ('PWG-ROOT HEAD%s%s — root=%s (simple verb + senses; same root_key)%s'
                   % (htag, ptag, key, directive))
        parts.append((label, '=== LAYER: %s ===\n\n%s' % (tag, '\n'.join(ch)), meta))
    return parts


def supplement_parts(key):
    """The headword-level supplement layers (PW / SCH / PWKVN chunked, NWS owner map batched).
    These attach ONCE to the whole headword, not per homonym. -> [(section_label, blob), ...]."""
    parts = []
    supp = {}
    for L in dm.merged(key):                        # group supplement records by layer
        if L['layer'] == 'pwg':
            continue
        supp.setdefault(L['layer'], []).extend(L['records'])
    for code in ('pw', 'sch', 'pwkvn'):
        if not supp.get(code):
            continue
        groups = chunk_records(supp[code], HEAD_BUDGET)
        for i, grp in enumerate(groups):
            label = code if len(groups) == 1 else '%s%02d' % (code, i)
            blob = '\n\n'.join('=== LAYER: %s ===\n\n%s' % (ROLE.get(code, code.upper()), r)
                               for r in grp)
            parts.append((label, blob))
    omap = nws_owner_map(key)
    if omap:
        rows = omap.split('\n')
        nb = (len(rows) + NWS_BATCH - 1) // NWS_BATCH
        for i in range(0, len(rows), NWS_BATCH):
            hdr = ('NWS — PRE-PARSED OWNER MAP (AUTHORITATIVE, batch %d/%d) — emit EXACTLY one '
                   'card row per numbered entry; copy its [NWS: OWNER] VERBATIM; translate the '
                   'gloss from its own language; keep IAST/sigla; do NOT re-derive owners.'
                   % (i // NWS_BATCH + 1, nb))
            parts.append(('nws%02d' % (i // NWS_BATCH),
                          '=== LAYER: %s ===\n\n%s' % (hdr, '\n'.join(rows[i:i + NWS_BATCH]))))
    return parts


def subcard_portrait(root_key, upasarga):
    """Apresjan corpus evidence for a root sub-card (interim: keeps split sub-cards from
    translating evidence-blind). A PREFIX sub-card is keyed on the prefixed SURFACE form
    (upasarga+root) — the corpus distinguishes them (anu+BU → «переживать», aBi+BU →
    «победитель», unlike bare BU → «быть»). If that form is absent from the corpus, fall
    back to the bare root's candidates as a hint. HEAD / SECONDARY (upasarga='') → the root."""
    if upasarga:
        form = upasarga + root_key
        cs = M.corpus_synonyms(form)
        if cs:
            return [{'key1': form, 'iast': ''.join(cg._S2I.get(c, c) for c in cg.form_key(form)),
                     'evidence_scope': 'prefixed-form', 'corpus_synonyms': cs}]
    cs = M.corpus_synonyms(root_key)
    if not cs:
        return []
    scope = ('root-fallback (prefixed form %s+%s not in corpus — hint only, defer to the German gloss)'
             % (upasarga, root_key)) if upasarga else 'root'
    return [{'key1': root_key, 'iast': ''.join(cg._S2I.get(c, c) for c in cg.form_key(root_key)),
             'evidence_scope': scope, 'corpus_synonyms': cs}]


def gen_root_split(key, pwg_idx, verbose=True):
    """--root-split: explode a GIANT root record into single-pass-sized sub-cards. Handles
    MULTIPLE homonyms: EACH homonym record is segmented; a giant one (>=MIN_SPLIT prefix
    <div n="p"> divisions) becomes head-sense-parts + one chunked sub-card per prefix; a
    small homonym is kept whole (still chunked if long) so nothing is dropped. Supplement
    layers (PW/SCH/PWKVN/NWS) attach ONCE to the headword. Writes <safe>~~h<H>_*.raw.txt +
    <safe>.rootmap.json (hom / seg_index / part / section / upasarga) so root_glue reassembles.
    Returns sub-card count, or None if the key is absent / no homonym is giant (caller falls back)."""
    fk = cg.form_key(key)
    bufs = pwg_idx.get(fk, [])
    if not bufs:
        return None
    segmented = []
    for buf in bufs:
        dl = [l for l in buf if not (l.startswith('<L>') or l.startswith('<LEND>'))]
        cards = RS.segment(dl)
        npfx = sum(1 for c in cards if c['kind'] == 'prefix')
        segmented.append((dl, cards, npfx))
    if not any(npfx >= MIN_SPLIT for _, _, npfx in segmented):
        return None                                 # no giant homonym — let gen_card handle it whole
    root = safe_name(key)
    n_hom = len(bufs)
    submap = []
    npfx_total = 0

    def clean_old_subcards():
        """Remove stale generated sub-card inputs for this root before rewriting them."""
        prefix = root + '~~'
        for fn in os.listdir(OUT):
            if fn.startswith(prefix) and (fn.endswith('.raw.txt') or fn.endswith('.portrait.json')):
                os.remove(os.path.join(OUT, fn))

    def write(sub, text, portrait=None):
        open(os.path.join(OUT, sub + '.raw.txt'), 'w', encoding='utf-8').write(text)
        json.dump(portrait or [], open(os.path.join(OUT, sub + '.portrait.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False)

    clean_old_subcards()

    for hom, (dl, cards, npfx) in enumerate(segmented):
        if npfx >= MIN_SPLIT:                       # giant homonym -> head parts + prefix sub-cards
            npfx_total += npfx
            head_pf = subcard_portrait(key, '')   # simple-verb head -> root corpus evidence
            for part, (label, blob, meta) in enumerate(head_sense_parts(key, cards[0]['lines'], hom, n_hom)):
                sub = '%s~~h%d_00_%s' % (root, hom, label)
                write(sub, blob, head_pf)
                entry = {'subkey': sub, 'hom': hom, 'seg_index': 0, 'part': part,
                         'kind': 'head', 'section': label, 'upasarga': '', 'root_key': key}
                entry.update(meta)
                submap.append(entry)
            for seg, c in enumerate(cards[1:], start=1):
                # c['kind'] is 'prefix' (<div n="p">) or 'secondary' (<div n="m"> caus/desid/
                # intens) — preserve it so root_glue nests secondary stems with the simple verb,
                # not under the last prefix. (PWG marks secondary inline → 0 in practice; latent.)
                kind, upa, label = c['kind'], c['upasarga'], c.get('label', '')
                tok = safe_name(upa) if upa else ('sec_%s' % seg)
                # prefix -> prefixed-form corpus evidence; secondary (no upasarga) -> root
                sub_pf = subcard_portrait(key, upa)
                chunks = chunk_lines(c['lines'], HEAD_BUDGET)
                for part, ch in enumerate(chunks):
                    sub = '%s~~h%d_%02d_%s%s' % (root, hom, seg, tok,
                                                 '_%d' % part if len(chunks) > 1 else '')
                    pp = ' part %d/%d' % (part + 1, len(chunks)) if len(chunks) > 1 else ''
                    htag = (' homonym %d' % (hom + 1)) if n_hom > 1 else ''
                    if kind == 'secondary':
                        hdr = ('PWG-ROOT SUBCARD%s — root=%s SECONDARY %s%s (caus./desid./intens. '
                               'of the simple verb)' % (htag, key, label, pp))
                    else:
                        hdr = ('PWG-ROOT SUBCARD%s — root=%s upasarga=%s%s (prefixed verb nested in '
                               'the %s root article; root_key links it back)' % (htag, key, upa, pp, key))
                    write(sub, '=== LAYER: %s ===\n\n%s' % (hdr, '\n'.join(ch)), sub_pf)
                    submap.append({'subkey': sub, 'hom': hom, 'seg_index': seg, 'part': part,
                                   'kind': kind, 'section': kind, 'upasarga': upa,
                                   'label': label, 'root_key': key})
        else:                                       # small homonym -> keep whole (chunked if long)
            small_pf = subcard_portrait(key, '')
            for part, (label, blob, meta) in enumerate(head_sense_parts(key, dl, hom, n_hom)):
                sub = '%s~~h%d_00_%s' % (root, hom, label)
                write(sub, blob, small_pf)
                entry = {'subkey': sub, 'hom': hom, 'seg_index': 0, 'part': part,
                         'kind': 'head', 'section': label, 'upasarga': '', 'root_key': key}
                entry.update(meta)
                submap.append(entry)
    head_parts = [s for s in submap if s['kind'] == 'head']   # for the verbose line
    # headword-level supplements: attach once, tagged to homonym 0
    for part, (label, blob) in enumerate(supplement_parts(key)):
        sub = '%s~~h0_zz_%s' % (root, label)
        write(sub, blob)
        submap.append({'subkey': sub, 'hom': 0, 'seg_index': 99, 'part': part,
                       'kind': 'supplement', 'section': label, 'upasarga': '', 'root_key': key})
    npfx = npfx_total
    json.dump({'root': key, 'safe': root, 'sub_cards': submap},
              open(os.path.join(OUT, root + '.rootmap.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    stale = os.path.join(OUT, root + '.raw.txt')   # drop a superseded whole-card input so the
    if os.path.exists(stale):                      # translator never sees both the whole + the split
        os.remove(stale)
    if verbose:
        nhead = len(head_parts)
        ngiant = sum(1 for _, _, p in segmented if p >= MIN_SPLIT)
        htag = ' across %d homonyms (%d giant)' % (n_hom, ngiant) if n_hom > 1 else ''
        print('  %-10s ROOT-SPLIT → %d sub-cards (%d head-parts + %d prefix)%s → %s~~*.raw.txt + rootmap'
              % (key, len(submap), nhead, npfx, htag, root))
    return len(submap)


def manifest_keys(section):
    p = os.path.join(HERE, 'pilot', 'output', 'scale_manifest.%s.json' % section)
    if not os.path.exists(p):
        sys.exit('no manifest %s — run: python scale_route.py %s' % (os.path.basename(p), section))
    return [e['key1'] for e in json.load(open(p, encoding='utf-8'))]


def main():
    args = sys.argv[1:]
    limit = None
    root_split = '--root-split' in args
    if root_split:
        args.remove('--root-split')
    if '--limit' in args:
        i = args.index('--limit'); limit = int(args[i + 1]); del args[i:i + 2]
    if '--manifest' in args:
        i = args.index('--manifest'); section = args[i + 1]; del args[i:i + 2]
        keys = manifest_keys(section)
        scaled = True
    else:
        keys = args or DEFAULT
        scaled = False
    if limit is not None:
        keys = keys[:limit]

    os.makedirs(OUT, exist_ok=True)
    pwg_idx = dm.index('pwg')

    def is_merged(key):
        """Done (skip) iff a current MERGED input exists AND (it has no NWS layer
        or it already carries the owner map). Regenerate: (a) superseded PWG-only
        _pilot_gen.py outputs ('=== RECORD' format, no '=== LAYER:'), and (b) merged
        inputs written before the owner-map feed (have an NWS layer but no map)."""
        p = os.path.join(OUT, safe_name(key) + '.raw.txt')
        try:
            with open(p, encoding='utf-8') as f:
                t = f.read()
        except OSError:
            return False
        if '=== LAYER:' not in t[:200]:
            return False
        has_nws = '=== LAYER: NWS' in t
        return (not has_nws) or ('PRE-PARSED OWNER MAP' in t)

    def is_giant(key):
        """Would --root-split explode this key? True if ANY homonym record has >=MIN_SPLIT
        prefix divisions (matches gen_root_split, which splits every giant homonym)."""
        for buf in pwg_idx.get(cg.form_key(key), []):
            dl = [l for l in buf if not (l.startswith('<L>') or l.startswith('<LEND>'))]
            if sum(1 for c in RS.segment(dl) if c['kind'] == 'prefix') >= MIN_SPLIT:
                return True
        return False

    def is_done(key):
        """Resumability. In --root-split mode a GIANT root counts as done only once its
        rootmap exists — a stale whole-card input must NOT mask it, or it never gets split."""
        if root_split:
            if os.path.exists(os.path.join(OUT, safe_name(key) + '.rootmap.json')):
                return True                        # already split
            return is_merged(key) and not is_giant(key)   # non-giant whole-card is fine
        return is_merged(key)

    # resumable in scaled runs: skip only keys already finished in the active mode
    todo = [k for k in keys if not (scaled and is_done(k))]
    print('merged pilot: %d key(s)%s, %d to generate'
          % (len(keys), ' [scaled, resumable]' if scaled else '', len(todo)))

    n = missing = with_nws = split_roots = split_subcards = 0
    errored = []                       # keys unwritable on this FS (e.g. '|' in arI|a)
    lc_tot = {'pw': 0, 'sch': 0, 'pwkvn': 0, 'nws': 0}
    for j, key in enumerate(todo, 1):
        try:
            if root_split:
                nsub = gen_root_split(key, pwg_idx, verbose=not scaled)
                if nsub is not None:   # giant root -> exploded into sub-cards; skip whole-card gen
                    split_roots += 1
                    split_subcards += nsub
                    continue
            lc = gen_card(key, pwg_idx, verbose=not scaled)
        except OSError as e:           # one bad key must not kill an 11k-card run
            errored.append(key)
            print('  SKIP (unwritable: %s): %r' % (e.strerror or e, key))
            continue
        if lc is None:
            missing += 1
            continue
        n += 1
        for code in lc_tot:
            lc_tot[code] += 1 if lc.get(code) else 0
        if lc.get('nws'):
            with_nws += 1
        if scaled and j % 200 == 0:
            print('  [%d/%d] generated; NWS-extra so far %d' % (j, len(todo), with_nws))
            sys.stdout.flush()

    print('wrote %d merged pilot inputs → %s%s%s'
          % (n, OUT, (' (%d missing in PWG)' % missing) if missing else '',
             (' (%d unwritable: %s)' % (len(errored), errored)) if errored else ''))
    if root_split and split_roots:
        print('  ROOT-SPLIT: %d giant root(s) exploded into %d sub-cards (+ rootmap.json each)'
              % (split_roots, split_subcards))
    if scaled and n:
        print('  layer coverage: PW %d (%.0f%%)  SCH %d (%.0f%%)  PWKVN %d (%.0f%%)  NWS-extra %d (%.0f%%)'
              % (lc_tot['pw'], 100 * lc_tot['pw'] / n, lc_tot['sch'], 100 * lc_tot['sch'] / n,
                 lc_tot['pwkvn'], 100 * lc_tot['pwkvn'] / n, with_nws, 100 * with_nws / n))


if __name__ == '__main__':
    main()
