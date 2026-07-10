#!/usr/bin/env python
r"""Compile the PWG->RU(+EN) translations into human-readable articles.

Produces, under RussianTranslation/article_site/ :
  * md/<root>.md               -- one file per root article (DE source + RU + EN)
  * md/subcards/<subcard>.md   -- one file per sub-card (prefixed form)
  * articles.js                -- window.ARTICLES data (pre-rendered HTML), embedded
  * index.html                 -- self-contained browser (RU default, EN tab, IAST)

Data sources (both already exist; nothing regenerated):
  * src/pwg_ru_translated.jsonl -- RU spine, flat per-sense rows (de, ru, subcard,
    sense_tag, h, iast, dcs_freq, review_status, provenance). ~46 roots.
  * wf_output.en.<root>.json    -- EN per-root stores (records[].senses[] german+english).

Markup rendering (IAST, per MG 2026-07-01):
  {#SLP1#}   -> italic IAST (SLP1->IAST via corpus_gate._S2I; Vedic accents dropped)
  {%gloss%}  -> the translatable gloss, unwrapped
  <ls>..</ls>-> citation span   <ab>..</ab> -> abbreviation
  <lex>..>   -> grammar label    <is>/<hom>/<div>/[Page..] -> unwrapped / dropped

  python src/pilot/build_article_site.py            # build everything
  python src/pilot/build_article_site.py --root gam # one root (debug print)
"""
import argparse
import collections
import glob
import html
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
REPO = os.path.dirname(SRC)
sys.path.insert(0, SRC)
import corpus_gate as cg  # noqa: E402  (_S2I SLP1->IAST map)
import ls_resolver as lsr  # noqa: E402  (<ls> citation -> Cologne scan URL; PWG paths)
import pwg_ab  # noqa: E402  (<ab> grammar/usage abbreviation -> DE/EN expansion, for tooltips)
import pwg_ab_ru  # noqa: E402  (<ab> -> RU display text for the editorial/cross-ref bucket)
import pwg_sources as pwgsrc  # noqa: E402  (<ls> siglum -> full source title, for tooltips)
import iast_to_cyrillic as i2c  # noqa: E402  (<is> proper name -> Cyrillic, RU column only)

RU_STORE = os.path.join(SRC, 'pwg_ru_translated.jsonl')
OUT_DIR = os.path.join(REPO, 'article_site')

_ACCENT = re.compile(r'[\\/^~]')          # Vedic udatta/anudatta/svarita markers
_SK = re.compile(r'\{#(.*?)#\}', re.S)
_GL = re.compile(r'\{%(.*?)%\}', re.S)
_LS = re.compile(r'<ls\b([^>]*)>(.*?)</ls>', re.S)
_N_ATTR = re.compile(r'\bn\s*=\s*"([^"]*)"')


def _ls_href(attrs, visible):
    """Resolve one <ls> citation to a Cologne scan URL (PWG), or None.

    `attrs` is the raw attribute string of the <ls> tag; the `n=` attribute
    carries the normalized prefix (+ leading coords) that the source uses so
    bare-number continuation refs (e.g. `4,10,7.` after `AV. 11,4,26.`) resolve
    against the right work. `visible` is the inner text shown to the reader."""
    m = _N_ATTR.search(attrs or '')
    n_attr = m.group(1) if m else None
    try:
        return lsr.generate_href('pwg', n_attr, (visible or '').strip())
    except Exception:
        return None


def _ls_title(attrs, visible):
    """Resolve one <ls> citation to its full source title (pwgbib), for a hover
    tooltip -- e.g. 'ṚV.' -> 'Ṛgveda'. Tries the n= attribute first (normalized
    prefix), falls back to the visible text's own source_key."""
    m = _N_ATTR.search(attrs or '')
    n_attr = m.group(1) if m else None
    for cand in (n_attr, pwgsrc.source_key(visible or '')):
        if not cand:
            continue
        try:
            r = pwgsrc.resolve(cand)
        except Exception:
            r = None
        if r:
            return r
    return None
_AB = re.compile(r'<ab\b[^>]*>(.*?)</ab>', re.S)
_LEX = re.compile(r'<lex\b[^>]*>(.*?)</lex>', re.S)
_IS = re.compile(r'<is\b[^>]*>(.*?)</is>', re.S)
_HOM = re.compile(r'<hom\b[^>]*>(.*?)</hom>', re.S)
_PAGE = re.compile(r'\[Page[^\]]*\]')
_TAG = re.compile(r'<[^>]+>')             # any leftover tag


def slp1_iast(s):
    """SLP1 running text -> IAST (drop Vedic accent marks for readability)."""
    s = _ACCENT.sub('', s or '')
    return ''.join(cg._S2I.get(c, c) for c in s)


_CYR_VOWELS = 'аеёиоуыэюя'
_STRIP_MARKUP = re.compile(r'[{}<>#%]|\x01|\x02')


def _ab_display(token, lang, pre_ctx=''):
    """(visible, title) for one <ab> token, language-aware.

    DE/EN columns: visible = the original abbreviation as printed; title = its
    authoritative German/English expansion (pwg_ab), a straight tooltip.
    RU column: visible = the curated Russian equivalent when the token is in
    the editorial/cross-reference bucket (pwg_ab_ru.RU_MAP; MG's own examples,
    e.g. Bein.->эпит., s.u.->см.); grammatical-category tokens (Acc., caus.,
    aor., sg. ...) are DELIBERATELY kept as the international Latin siglum per
    MG's 10-07-2026 decision -- those just gain the same tooltip as DE/EN.

    `pre_ctx` = raw text immediately preceding this tag in the SAME field. Some
    already-translated cards paraphrase the abbreviation in the surrounding RU
    prose AND leave the tag (e.g. stored ru = "см. <ab>s. u.</ab> menā" -- the
    translator wrote "см." by hand, then left the tag) -- rendering our own
    "см." there too doubles it ("см. см."). If the RU_MAP text is already the
    last word before the tag, drop the redundant visible text (title/tooltip
    is kept off too -- there is nothing left to hang it on)."""
    tok = token.strip()
    r = pwg_ab.resolve(tok)
    title = ('%s — %s' % (r['de'], r['en'])) if r else None
    if lang == 'ru':
        vis, _ = pwg_ab_ru.display(tok)
        if vis != tok:
            pre = _STRIP_MARKUP.sub(' ', pre_ctx)
            pre = re.sub(r'\s+', ' ', pre).strip(' .').lower()
            if pre.endswith(vis.rstrip('.').lower()):
                return '', None
        return vis, title
    return tok, title


def _is_display(inner, lang, post_ctx=''):
    """<is> proper-name span: Cyrillicize only for the RU column (see
    iast_to_cyrillic.py -- DE/EN keep the IAST spelling untouched).

    `post_ctx` = the raw character(s) immediately following the closing tag.
    The translated store sometimes glues a bare Russian case-vowel directly
    onto the tag with no space (e.g. "<is>Vṛṣaṇaśva</is>а." for the genitive)
    -- since our transliteration of an a-stem name already ends in that same
    vowel ("Вришанашва"), the two would concatenate into a mis-declined
    double-vowel ("Вришанашваа"). When the transliteration ends in a Cyrillic
    vowel and the very next stored character is also one (no space between --
    i.e. a glued-on case ending), drop our trailing vowel so the store's own
    ending lands on the consonant stem instead, matching how these names were
    evidently declined by the translator."""
    if lang != 'ru':
        return inner
    cyr = i2c.name_for_ru_prose(inner)
    nxt = (post_ctx[:1] or '').lower()
    if cyr and cyr[-1].lower() in _CYR_VOWELS and nxt in _CYR_VOWELS:
        cyr = cyr[:-1]
    return cyr


def _render(text, mode, lang=None):
    """Render one stored field (de/ru/en) to `html` or `md`.

    Sanskrit LEXICAL spans ({#..#}) -> italic IAST in every language (headword/
    cited-form convention, deliberately unchanged — mirrors the mw_ru rule that
    Sanskrit forms are left untouched). <is> PROPER NAMES and <ab> EDITORIAL
    abbreviations are language-aware: `lang` ('de'/'ru'/'en') controls whether
    they get RU-specific treatment (Cyrillic name, Russian abbreviation) — see
    _ab_display/_is_display. Citations/abbrevs kept in a light wrapper;
    structural tags dropped. The two modes differ only in the emphasis/needed-
    escaping syntax."""
    if not text:
        return ''
    t = _PAGE.sub('', text)
    # XML/source metalanguage that must never reach the web (Cologne drops it too):
    #  ¦ (U+00A6) = lemma-terminator after the head-word; ⌊..⌋ hidden text.
    t = t.replace('¦', '')
    if mode == 'html':
        # Convert the tags we KEEP into sentinel-wrapped tags first (LT/GT are
        # placeholder chars, unquoted class= so html.escape won't mangle them),
        # then strip leftover SOURCE structural tags (<div>, <sic/>, ...), then
        # html-escape the plain text, then restore our sentinels to real tags.
        # (The old generic <[^>]+> strip removed our own generated spans too.)
        LT, GT = '\x01', '\x02'
        t = _SK.sub(lambda m: '%si class=sa%s%s%s/i%s' % (LT, GT, slp1_iast(m.group(1)), LT, GT), t)

        def _ls_html(m):
            # Resolved citation -> clickable <a class=ls href=..> (scan page);
            # unresolved -> plain <span class=ls> (kept dim so gaps stay visible).
            # Attribute values are left unquoted so the later html.escape (which
            # escapes " ' & < >) cannot mangle them; scan URLs contain none of the
            # quote/space chars that would require quoting.
            vis = m.group(2).strip()
            url = _ls_href(m.group(1), vis)
            title = _ls_title(m.group(1), vis)
            tattr = ' title=%s' % title.replace(' ', '\xa0') if title else ''
            if url:
                # <a class=ls href=URL title=T target=_blank rel=noopener>VIS</a>
                return '%sa class=ls href=%s%s target=_blank rel=noopener%s%s%s/a%s' % (
                    LT, url, tattr, GT, vis, LT, GT)
            return '%sspan class=ls%s%s%s%s/span%s' % (LT, tattr, GT, vis, LT, GT)
        t = _LS.sub(_ls_html, t)

        def _ab_html(m):
            vis, title = _ab_display(m.group(1), lang, m.string[:m.start()])
            if not vis:
                return ''  # deduped against a preceding hand-written RU paraphrase
            tattr = ' title=%s' % title.replace(' ', '\xa0') if title else ''
            return '%sspan class=ab%s%s%s%s/span%s' % (LT, tattr, GT, vis, LT, GT)
        t = _AB.sub(_ab_html, t)
        t = _LEX.sub(lambda m: '%sspan class=lex%s%s%s/span%s' % (LT, GT, m.group(1).strip(), LT, GT), t)
        t = _IS.sub(lambda m: '%si%s%s%s/i%s' % (
            LT, GT, _is_display(m.group(1), lang, m.string[m.end():m.end() + 2]), LT, GT), t)
        t = _HOM.sub(lambda m: '%sb%s%s%s/b%s' % (LT, GT, m.group(1), LT, GT), t)
        t = _GL.sub(lambda m: m.group(1), t)
        t = _TAG.sub('', t)               # drop leftover source structural tags
        t = html.escape(t)                # escape &,<,> in the remaining plain text
        t = t.replace('\n', '<br>')       # real <br> (added after escape)
        t = t.replace(LT, '<').replace(GT, '>')   # restore our kept tags
        # NOTE: title=... attributes are intentionally left UNQUOTED (matching
        # href=/class= elsewhere in this renderer) with internal spaces shielded
        # as U+00A0 (renders identically to a normal space in the tooltip) —
        # do NOT unshield back to ' ' here, a literal space would split an
        # unquoted attribute into bogus extra tokens.
    else:  # md
        t = _SK.sub(lambda m: '*%s*' % slp1_iast(m.group(1)), t)
        t = _GL.sub(lambda m: m.group(1), t)

        def _ls_md(m):
            vis = m.group(2).strip()
            url = _ls_href(m.group(1), vis)
            return '[%s](%s)' % (vis, url) if url else '[%s]' % vis
        t = _LS.sub(_ls_md, t)
        t = _AB.sub(lambda m: _ab_display(m.group(1), lang, m.string[:m.start()])[0], t)
        t = _LEX.sub(lambda m: '_%s_' % m.group(1).strip(), t)
        t = _IS.sub(lambda m: _is_display(m.group(1), lang, m.string[m.end():m.end() + 2]), t)
        t = _HOM.sub(lambda m: '**%s**' % m.group(1), t)
        t = _TAG.sub('', t)
    t = re.sub(r'[ \t]{2,}', ' ', t)
    return t.strip()


_A_LS = re.compile(r'<a class=ls href=(\S+) target')   # resolved citation link
_SPAN_LS = re.compile(r'<span class=ls>')              # unresolved citation


def ls_stats(de_html_list):
    """Count citations across a root's DE (source) senses: total <ls>, how many
    are linked, and the scan/HTML split. RU/EN mirror the same citations, so the
    DE surface is the authoritative reference set."""
    tot = lnk = scan = html = 0
    for h in de_html_list:
        for m in _A_LS.finditer(h or ''):
            tot += 1
            lnk += 1
            t = lsr.link_type(m.group(1))
            if t == 'scan':
                scan += 1
            elif t == 'html':
                html += 1
        tot += len(_SPAN_LS.findall(h or ''))
    return {'ls': tot, 'ls_linked': lnk, 'ls_scan': scan, 'ls_html': html}


def ab_frequency(model):
    """Corpus-wide <ab> token frequency, from the DE (source) senses -- the
    authoritative reference set (RU/EN mirror the same abbreviations; same
    convention as ls_stats above). One row per distinct token: count, roots it
    appears in, the authoritative DE/EN expansion (pwg_ab), whether the RU
    column translates it (pwg_ab_ru.RU_MAP) or keeps it as international Latin,
    and the RU display text. Powers the abbreviations.html dashboard."""
    freq = collections.Counter()
    roots_of = collections.defaultdict(set)
    for r in model:
        for sc in r['subcards']:
            for s in sc['senses']:
                for tok in _AB.findall(s.get('de_raw') or ''):
                    tok = tok.strip()
                    freq[tok] += 1
                    roots_of[tok].add(r['root'])
    rows = []
    for tok, count in freq.most_common():
        res = pwg_ab.resolve(tok)
        ru_vis = pwg_ab_ru.RU_MAP.get(tok)
        rows.append({
            'token': tok, 'count': count, 'n_roots': len(roots_of[tok]),
            'de': res['de'] if res else None, 'en': res['en'] if res else None,
            'resolved': bool(res), 'ru_display': ru_vis,
            'bucket': 'translated' if ru_vis else ('latin' if res else 'unresolved'),
        })
    return rows


def _root_of(key1):
    return (key1 or '').split('~~')[0]


def load_ru():
    """root -> ordered list of (subcard, h, iast, tag, de, ru, dcs, extra)."""
    roots = {}
    with open(RU_STORE, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            root = _root_of(r.get('key1') or r.get('subcard'))
            roots.setdefault(root, []).append(r)
    return roots


def _norm(s):
    """Whitespace-insensitive key for joining RU `de` to EN `german` (same source text)."""
    return re.sub(r'\s+', '', s or '')


def load_en(root):
    """Return two EN indices for a root, both keyed within the sub-card:
      by_text[(subcard, norm(german))] -> english   (primary; de==german join)
      by_tag[(subcard, tag)]           -> english   (fallback)
    The German source is identical in the RU and EN stores, so the text join is
    far more reliable than the tag join (RU sense_tag != EN tag conventions)."""
    fp = os.path.join(REPO, 'wf_output.en.%s.json' % root)
    if not os.path.exists(fp):
        return {}, {}
    by_text, by_tag = {}, {}
    for e in json.load(open(fp, encoding='utf-8')).get('results') or []:
        c = e.get('card')
        if not c:
            continue
        for i, s in enumerate(rec_senses(c)):
            if not s.get('english'):
                continue
            tag = str(s.get('tag') if s.get('tag') is not None else i)
            by_tag.setdefault((e['key'], tag), s['english'])
            if s.get('german'):
                by_text.setdefault((e['key'], _norm(s['german'])), s['english'])
    return by_text, by_tag


def rec_senses(card):
    for rec in (card.get('records') or []):
        for s in (rec.get('senses') or []):
            yield s


def dcs_count(dcs):
    if isinstance(dcs, dict):
        return dcs.get('count')
    return None


def load_en_full(root):
    """EN store as ordered structure: (selected_key_order, {subcard: {iast,h,senses:[{tag,german,english}]}})."""
    fp = os.path.join(REPO, 'wf_output.en.%s.json' % root)
    if not os.path.exists(fp):
        return [], {}
    d = json.load(open(fp, encoding='utf-8'))
    by_sub = {}
    for e in d['results']:
        c = e.get('card')
        if not c:
            continue
        rec0 = (c.get('records') or [{}])[0]
        senses = []
        for i, s in enumerate(rec_senses(c)):
            senses.append({'tag': str(s.get('tag') if s.get('tag') is not None else i),
                           'german': s.get('german') or '', 'english': s.get('english') or ''})
        by_sub[e['key']] = {'iast': c.get('iast') or '', 'h': rec0.get('h') or '', 'senses': senses}
    return list(d['meta'].get('selected_keys') or []), by_sub


def make_sense(tag, de, ru, en, dcs, src):
    return {
        'tag': str(tag), 'has_ru': bool(ru), 'has_en': bool(en),
        'de_raw': de or '',   # raw DE source (keeps <ls n=..>); not emitted, used for citation analysis
        'de_html': _render(de, 'html', 'de'), 'ru_html': _render(ru, 'html', 'ru'), 'en_html': _render(en, 'html', 'en'),
        'de_md': _render(de, 'md', 'de'), 'ru_md': _render(ru, 'md', 'ru'), 'en_md': _render(en, 'md', 'en'),
        'dcs': dcs_count(dcs), 'src': src or '',
    }


def build_model():
    """UNION spine: every EN sub-card/sense (the full per-root set) with RU attached
    where present, plus any RU-only sub-cards/senses appended. So EN-complete roots
    (e.g. gam, 127 sub-cards) show fully even where RU is partial, and the gap is
    visible per sense (has_ru / has_en)."""
    ru = load_ru()
    en_files = {os.path.basename(f).replace('wf_output.en.', '').replace('.json', '')
                for f in glob.glob(os.path.join(REPO, 'wf_output.en.*.json'))}
    model = []
    for root in sorted(set(ru) | en_files, key=lambda s: slp1_iast(s).lower()):
        ru_rows = ru.get(root, [])
        ru_by_sub = {}
        for r in ru_rows:
            ru_by_sub.setdefault(r.get('subcard') or r.get('key1'), []).append(r)
        ru_bytext, ru_bytag = {}, {}
        for sub, rows in ru_by_sub.items():
            for i, r in enumerate(rows):
                ru_bytext.setdefault((sub, _norm(r.get('de'))), r)
                tg = str(r.get('sense_tag') if r.get('sense_tag') is not None else i)
                ru_bytag.setdefault((sub, tg), r)
        en_order, en_by_sub = load_en_full(root)
        sub_order = list(en_order)
        seen = set(sub_order)
        for r in ru_rows:
            sub = r.get('subcard') or r.get('key1')
            if sub not in seen:
                sub_order.append(sub)
                seen.add(sub)
        subcards = []
        n_sense = n_ru = n_en = 0
        for sub in sub_order:
            en_entry = en_by_sub.get(sub)
            en_senses = en_entry['senses'] if en_entry else []
            ru_sub_rows = ru_by_sub.get(sub, [])
            used = set()
            senses = []
            for i, es in enumerate(en_senses):
                rrow = (ru_bytext.get((sub, _norm(es['german'])))
                        or ru_bytag.get((sub, es['tag'])))
                if rrow is not None:
                    used.add(id(rrow))
                senses.append(make_sense(
                    tag=es['tag'], de=(rrow.get('de') if rrow else es['german']),
                    ru=(rrow.get('ru') if rrow else None), en=es['english'],
                    dcs=(rrow.get('dcs_freq') if rrow else None),
                    src=(rrow.get('source_type') if rrow else '')))
            for i, r in enumerate(ru_sub_rows):
                if id(r) in used:
                    continue
                senses.append(make_sense(
                    tag=(r.get('sense_tag') if r.get('sense_tag') is not None else i),
                    de=r.get('de'), ru=r.get('ru'), en=None,
                    dcs=r.get('dcs_freq'), src=r.get('source_type')))
            if not senses:
                continue
            # Grammatical head block (tag 'header'/'head') is the entry preamble
            # (√root, Dhātup. reference, tense stems) and must LEAD the sub-card,
            # even when the source store lists it after sense 1 (the bug that made
            # e.g. bandh open on sense 1). Stable sort keeps all other senses in
            # their original order.
            senses.sort(key=lambda s: 0 if str(s['tag']).lower() in ('header', 'head') else 1)
            ru0 = ru_sub_rows[0] if ru_sub_rows else None
            iast = (ru0.get('iast') if ru0 else '') or (en_entry.get('iast') if en_entry else '') or ''
            h = (ru0.get('h') if ru0 else '') or (en_entry.get('h') if en_entry else '') or ''
            for s in senses:
                n_sense += 1
                n_ru += 1 if s['has_ru'] else 0
                n_en += 1 if s['has_en'] else 0
            subcards.append({'key': sub, 'h': h, 'iast': iast, 'senses': senses})
        st = ls_stats([s['de_html'] for sc in subcards for s in sc['senses']])
        model.append({
            'root': root, 'iast': slp1_iast(root),
            'en_available': bool(en_by_sub), 'ru_available': bool(ru_rows),
            'n_subcards': len(subcards), 'n_senses': n_sense,
            'n_ru_senses': n_ru, 'n_en_senses': n_en,
            'ls': st['ls'], 'ls_linked': st['ls_linked'],
            'ls_scan': st['ls_scan'], 'ls_html': st['ls_html'],
            'subcards': subcards,
        })
    return model


# ---------------- markdown emitters ----------------
def sense_md(s, with_en):
    # The grammatical head block carries no sense number, so drop the "N)" chip.
    lead = '' if str(s['tag']).lower() in ('header', 'head') else '**%s)** ' % s['tag']
    out = ['', '%s%s' % (lead, s['de_md'])]
    if s['ru_md']:
        out.append('')
        out.append('- **RU:** %s' % s['ru_md'])
    if with_en and s['en_md']:
        out.append('- **EN:** %s' % s['en_md'])
    badge = []
    if s['dcs'] is not None:
        badge.append('DCS %s' % s['dcs'])
    if s['src']:
        badge.append(s['src'])
    if badge:
        out.append('  <sub>%s</sub>' % ' · '.join(badge))
    return '\n'.join(out)


def subcard_md(sub):
    head = sub['iast'] or slp1_iast(sub['h']) or sub['key']
    lines = ['## %s' % head, '', '`%s`' % sub['key'], '']
    for s in sub['senses']:
        lines.append(sense_md(s, with_en=True))
    return '\n'.join(lines) + '\n'


def _pwg_scan(colnum):
    return ('https://sanskrit-lexicon.uni-koeln.de/scans/PWGScan/2020/'
            'web/webtc/servepdf.php?page=%d' % int(colnum))


def load_colocation(model_roots):
    """PWG print co-location by PRINTED LEAF: for each article root, the physical
    page(s) it sits on — BOTH columns of the leaf (Böhtlingk-Roth prints two
    columns per page) — read from the committed src/pwg_columns.tsv (H429).

    Returns {root_slp1: [ {leaf, vol, cols:[{col, side, scan, words:[...] }]} ]},
    side 'L' (column 2P-1) / 'R' (column 2P), P = ceil(colnum/2). Each word:
    {iast, root, linked, self} — `linked` = a translated article (clickable
    in-site); non-linked non-self words link out to the kosha co-location browser
    (built by the JS render). `self` = the article's own entry, highlighted, in
    printed order."""
    cols_path = os.path.join(SRC, 'pwg_columns.tsv')
    if not os.path.exists(cols_path):
        sys.stderr.write('  [coloc] %s absent — run pwg_page_index.py first; '
                         'skipping co-location\n' % cols_path)
        return {}
    col_words = {}   # 'V-CCCC' -> [(Lid, headword_slp1), ...] in printed order
    hw_cols = {}     # headword_slp1 -> [columns it starts in], first-seen order
    with open(cols_path, encoding='utf-8') as f:
        next(f, None)  # header row
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if len(parts) < 6:
                continue
            column, _vol, _page, _n, lids, heads = parts[:6]
            pairs = list(zip(lids.split(','), [h.strip() for h in heads.split(', ')]))
            col_words[column] = pairs
            for _lid, h in pairs:
                hw_cols.setdefault(h, [])
                if column not in hw_cols[h]:
                    hw_cols[h].append(column)

    coloc = {}
    for root in model_roots:
        touched = hw_cols.get(root)
        if not touched:
            continue

        def words_of(column):
            out = []
            for _lid, hw in col_words.get(column, []):
                out.append({'iast': slp1_iast(hw), 'root': hw,
                            'linked': hw in model_roots and hw != root,
                            'self': hw == root})
            return out

        leaves, seen = [], set()
        for column in touched:
            vol, colnum = column.split('-')
            vol, colnum = int(vol), int(colnum)
            leaf = (colnum + 1) // 2            # physical leaf within the volume
            key = (vol, leaf)
            if key in seen:
                continue
            seen.add(key)
            left_n, right_n = 2 * leaf - 1, 2 * leaf   # the leaf's two columns
            cols = []
            for cn, side in ((left_n, 'L'), (right_n, 'R')):
                ckey = '%d-%04d' % (vol, cn)
                cols.append({'col': ckey, 'side': side, 'scan': _pwg_scan(cn),
                             'words': words_of(ckey)})
            leaves.append({'leaf': leaf, 'vol': vol, 'cols': cols})
        coloc[root] = leaves
    return coloc


def root_md(r):
    lines = ['# %s' % r['iast'], '',
             '_PWG article — %d sub-card(s), %d sense(s) · RU %d/%d · EN %d/%d_' % (
                 r['n_subcards'], r['n_senses'],
                 r['n_ru_senses'], r['n_senses'], r['n_en_senses'], r['n_senses']),
             '']
    for sub in r['subcards']:
        lines.append(subcard_md(sub))
    return '\n'.join(lines)


# ---------------- html emitter ----------------
INDEX_HTML = r"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PWG — переводы статей (RU / EN)</title>
<style>
:root{--bg:#fff;--fg:#1a1a1a;--mut:#6a6a6a;--line:#e4e4e4;--accent:#7a1f1f;--sa:#0b5;--card:#fafafa}
@media(prefers-color-scheme:dark){:root{--bg:#161616;--fg:#e8e8e8;--mut:#9a9a9a;--line:#333;--accent:#e6928a;--sa:#7ddda0;--card:#1e1e1e}}
*{box-sizing:border-box}body{margin:0;font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;color:var(--fg);background:var(--bg)}
#wrap{display:flex;min-height:100vh}
#side{width:250px;border-right:1px solid var(--line);padding:10px;overflow-y:auto;height:100vh;position:sticky;top:0}
#side h1{font-size:15px;margin:4px 6px 8px}
#q{width:100%;padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);margin-bottom:8px}
.rlink{display:flex;justify-content:space-between;gap:6px;padding:4px 8px;border-radius:6px;cursor:pointer;font-size:14px}
.rlink:hover{background:var(--card)}.rlink.active{background:var(--accent);color:#fff}
.rlink .en{font-size:11px;color:var(--mut)}.rlink.active .en{color:#fff}
.cov{font-size:10px;color:var(--mut)}.cov.low{color:#c46b00;font-weight:600}
.rlink.active .cov,.rlink.active .cov.low{color:#ffd9a8}
#main{flex:1;padding:20px 28px;max-width:900px}
.iast{font-style:italic}
h2.root{font-size:26px;margin:0 0 2px}.meta{color:var(--mut);font-size:13px;margin-bottom:14px}
#arthead{position:relative}
.lsstats{position:absolute;top:0;right:0;text-align:right;font-size:12px;line-height:1.4;max-width:48%}
.lsstats .lsn{color:var(--fg)}.lsstats .lsn b{color:var(--accent)}
.lsstats .lssub{color:var(--mut);font-size:11px}
@media(max-width:620px){.lsstats{position:static;text-align:left;max-width:none;margin-bottom:8px}}
.tabs{display:inline-flex;border:1px solid var(--line);border-radius:8px;overflow:hidden;margin-bottom:16px}
.tabs .tab{border:0;border-right:1px solid var(--line);background:var(--bg);color:var(--fg);padding:6px 16px;cursor:pointer;font-size:14px}
.tabs .tab:last-child{border-right:0}
.tabs .tab.on{background:var(--accent);color:#fff}
.sub{margin:18px 0;padding-bottom:6px;border-bottom:1px solid var(--line)}
.sub h3{margin:0 0 2px;font-size:19px}.sub .k{color:var(--mut);font-size:12px;font-family:ui-monospace,monospace}
.sense{margin:12px 0;padding:10px 12px;background:var(--card);border-radius:8px}
.tag{font-weight:700;color:var(--accent);margin-right:4px}
.de{margin-bottom:6px}.tr{padding-top:6px;margin-top:6px;border-top:1px dashed var(--line)}
.lbl{font-size:10px;letter-spacing:.05em;color:#fff;background:var(--mut);border-radius:3px;padding:0 5px;text-transform:uppercase;margin-right:6px;vertical-align:1px}
i.sa{font-style:italic;color:var(--sa)}
.ls{color:var(--mut);font-size:.92em}
.ls[title]{cursor:help;border-bottom:1px dotted var(--mut)}
a.ls{color:var(--accent);font-size:.92em;text-decoration:none;border-bottom:1px dotted var(--accent)}
a.ls:hover{text-decoration:underline;border-bottom-color:transparent}
.ab{font-style:italic;color:var(--mut);cursor:help;border-bottom:1px dotted var(--mut)}.lex{font-variant:small-caps;color:var(--mut)}
.badges{margin-top:6px}.badge{display:inline-block;font-size:11px;color:var(--mut);border:1px solid var(--line);border-radius:10px;padding:0 7px;margin-right:5px}
.na{color:var(--mut);font-style:italic}
/* language switch: show German always as reference in ru/en; German-only in de mode */
#artbody.lang-ru .tr.en{display:none}
#artbody.lang-en .tr.ru{display:none}
#artbody.lang-de .tr{display:none}
#artbody.lang-de .de{font-size:16px}
#artbody:not(.lang-de) .de{color:var(--mut)}   /* dim the source when a translation is primary */
#artbody:not(.lang-de) .de i.sa{color:var(--sa)}
.coloc{margin:26px 0 8px;padding:14px 16px;background:var(--card);border:1px solid var(--line);border-radius:10px}
.coloc h4{margin:0 0 4px;font-size:15px}
.coloc .hint{color:var(--mut);font-size:12px;margin-bottom:10px}
.coloc .hint a{color:var(--accent)}
.leaf{margin:12px 0;padding-top:8px;border-top:1px solid var(--line)}
.leaf .llab{font-size:12px;color:var(--mut);margin-bottom:6px}
.leaf .llab b{color:var(--fg)}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:620px){.pair{grid-template-columns:1fr}}
.colcol{border:1px solid var(--line);border-radius:8px;padding:8px 10px}
.colcol .clab{font-size:12px;color:var(--mut);font-family:ui-monospace,monospace}
.colcol .side{font-size:10px;text-transform:uppercase;letter-spacing:.05em;color:#fff;background:var(--mut);border-radius:3px;padding:0 5px;margin-left:5px}
.colcol a.scan{color:var(--accent);font-size:12px;text-decoration:none;border-bottom:1px dotted var(--accent);margin-left:6px}
.colcol a.scan:hover{border-bottom-color:transparent}
.cwords{margin-top:6px;display:flex;flex-wrap:wrap;gap:5px}
.cw{font-style:italic;font-size:13px;padding:1px 8px;border:1px solid var(--line);border-radius:11px;color:var(--fg);white-space:nowrap;text-decoration:none;cursor:pointer}
.cw:hover{background:var(--accent);color:#fff;border-color:var(--accent)}
.cw.lnk{color:var(--accent);border-color:var(--accent);font-weight:500}
.cw.self{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:600}
.cw.empty{color:var(--mut);font-style:italic;border:0;cursor:default}
.cw.empty:hover{background:none;color:var(--mut)}
</style></head><body><div id="wrap">
<nav id="side"><h1>PWG статьи</h1><a href="abbreviations.html" style="display:block;font-size:12px;color:var(--mut);margin:-4px 0 10px 6px">📖 словарь сокращений</a><input id="q" placeholder="фильтр корней…"><div id="list"></div></nav>
<main id="main"><div id="arthead"></div><div id="artbody" class="lang-ru"><p class="na">Загрузка…</p></div></main></div>
<script src="articles.js"></script>
<script>
var A=window.ARTICLES||{roots:[]}, lang='ru', cur=null;
var list=document.getElementById('list'), q=document.getElementById('q');
var arthead=document.getElementById('arthead'), artbody=document.getElementById('artbody');
function esc(x){return x==null?'':(''+x);}
function renderList(f){list.innerHTML='';A.roots.filter(function(r){return !f||r.iast.toLowerCase().indexOf(f)>=0||r.root.toLowerCase().indexOf(f)>=0;}).forEach(function(r){
 var d=document.createElement('div');d.className='rlink'+(cur===r.root?' active':'');
 var ruf=r.n_senses?Math.round(100*r.n_ru_senses/r.n_senses):0;
 d.innerHTML='<span class="iast">'+r.iast+'</span><span class="en" title="senses; RU / EN coverage">'+r.n_senses+' <span class="cov'+(ruf<100?' low':'')+'">RU'+ruf+'%</span></span>';
 d.onclick=function(){cur=r.root;renderList(q.value.toLowerCase());renderRoot(r);};list.appendChild(d);});}
// Language is a CSS class on #artbody (lang-de|lang-ru|lang-en). All three blocks
// are always in the DOM; the class shows/hides them, so switching cannot silently no-op.
function applyLang(){
 artbody.className='lang-'+lang;
 var t=document.querySelectorAll('.tab');for(var i=0;i<t.length;i++){t[i].classList.toggle('on',t[i].getAttribute('data-lang')===lang);}
}
function trBlock(cls,label,txt){
 return '<div class="tr '+cls+'"><span class="lbl">'+label+'</span>'+(txt?txt:'<span class="na">— нет / n/a —</span>')+'</div>';
}
function renderBody(r){
 var subs=(window.ROOT||{})[r.root]||[]; var h='';
 subs.forEach(function(sub){
  h+='<div class="sub"><h3 class="iast">'+esc(sub.iast||sub.h||sub.key)+'</h3><div class="k">'+esc(sub.key)+'</div></div>';
  sub.senses.forEach(function(s){
   var b='';if(s.dcs!=null)b+='<span class="badge">DCS '+s.dcs+'</span>';if(s.src)b+='<span class="badge">'+s.src+'</span>';
   var tg=(s.tag==='header'||s.tag==='head')?'':'<span class="tag">'+esc(s.tag)+')</span>';
   h+='<div class="sense">'
    +'<div class="de">'+tg+'<span class="lbl">DE</span>'+esc(s.de_html)+'</div>'
    +trBlock('ru','RU',s.ru_html)+trBlock('en','EN',s.en_html)
    +(b?'<div class="badges">'+b+'</div>':'')+'</div>';
  });
 });
 artbody.innerHTML=(h||'<p class="na">нет данных</p>')+colocHtml(r.root); applyLang();
}
// Print co-location by LEAF: the printed page (two columns) this article sits on.
var KOSHA_COLOC='https://gasyoun.github.io/kosha/colocation/';
function koshaHref(col,slp1){return KOSHA_COLOC+'#pwg/'+encodeURIComponent(col)+'?w='+encodeURIComponent(slp1);}
function colWords(c){
 if(!c.words.length)return '<div class="cwords"><span class="cw empty">— здесь ни одна статья не начинается —</span></div>';
 var h='<div class="cwords">';
 c.words.forEach(function(w){
  if(w.self){h+='<span class="cw self">'+esc(w.iast)+'</span>';}
  else if(w.linked){h+='<span class="cw lnk" data-root="'+esc(w.root)+'">'+esc(w.iast)+'</span>';}
  else{h+='<a class="cw" href="'+koshaHref(c.col,w.root)+'" target="_blank" rel="noopener" title="открыть в словаре kosha">'+esc(w.iast)+'</a>';}
 });
 return h+'</div>';
}
function colBox(c){
 return '<div class="colcol"><span class="clab">'+esc(c.col)
  +' <span class="side">'+(c.side==='L'?'левая колонка':'правая колонка')+'</span></span>'
  +'<a class="scan" href="'+esc(c.scan)+'" target="_blank" rel="noopener">🖼 скан</a>'
  +colWords(c);
}
function colocHtml(root){
 var leaves=(window.COLOC||{})[root]||[]; if(!leaves.length)return '';
 var h='<div class="coloc"><h4>🖇 На том же печатном листе PWG</h4>'
  +'<div class="hint">Печатный словарь Бётлингка–Рота набран в <b>две колонки на страницу</b>; ниже — весь лист (левая + правая колонка). '
  +'Красным — уже переведённые статьи (открываются здесь), остальные ведут в '
  +'<a href="'+KOSHA_COLOC+'" target="_blank" rel="noopener">листалку колонок kosha</a>. '
  +'Оговорка: в источнике есть номера <i>колонок</i>, но не книжной страницы, поэтому лево/право <i>колонки</i> точны, а recto/verso листа не выводимы.</div>';
 leaves.forEach(function(lf){
  h+='<div class="leaf"><div class="llab">Печатный лист · том <b>'+esc(lf.vol)+'</b>, лист <b>'+esc(lf.leaf)+'</b> (колонки '+esc(lf.cols[0].col)+' + '+esc(lf.cols[1].col)+')</div>'
   +'<div class="pair">'+colBox(lf.cols[0])+colBox(lf.cols[1])+'</div></div>';
 });
 return h+'</div>';
}
function renderRoot(r){
 cur=r.root;
 var ls=r.ls||0, lsp=ls?Math.round(100*r.ls_linked/ls):0, lsu=ls-(r.ls_linked||0);
 var stats=ls?('<div class="lsstats"><div class="lsn"><b>'+ls+'</b> цитат · <b>'+lsp+'%</b> со ссылками</div>'
  +'<div class="lssub">🖼 сканы '+(r.ls_scan||0)+' · 📄 HTML '+(r.ls_html||0)+' · ✗ без ссылки '+lsu+'</div></div>'):'';
 arthead.innerHTML=stats+'<h2 class="root iast">'+r.iast+'</h2>'
  +'<div class="meta">PWG-статья · '+r.n_subcards+' под-карт., '+r.n_senses+' знач.'
  +' · <b>RU '+r.n_ru_senses+'/'+r.n_senses+'</b> · EN '+r.n_en_senses+'/'+r.n_senses
  +(r.n_ru_senses<r.n_senses?' <span class="cov low">RU неполный</span>':'')+'</div>'
  +'<div class="tabs">'
  +'<button class="tab" data-lang="de">Deutsch (оригинал)</button>'
  +'<button class="tab" data-lang="ru">Русский</button>'
  +'<button class="tab" data-lang="en">English</button></div>';
 // lazy-load this root's data (window.ROOT[root]) via <script src> — works from file:// too
 if((window.ROOT||{})[r.root]){renderBody(r);return;}
 artbody.innerHTML='<p class="na">Загрузка…</p>';
 var sc=document.createElement('script'); sc.src='roots/'+r.safe+'.js';
 sc.onload=function(){ if(cur===r.root) renderBody(r); };
 sc.onerror=function(){ if(cur===r.root) artbody.innerHTML='<p class="na">ошибка загрузки</p>'; };
 document.head.appendChild(sc);
}
// delegated tab handler (survives per-root re-render)
document.getElementById('main').addEventListener('click',function(e){
 var cw=e.target.closest?e.target.closest('.cw.lnk'):null;
 if(cw){var rt=cw.getAttribute('data-root');for(var i=0;i<A.roots.length;i++){if(A.roots[i].root===rt){cur=rt;renderList(q.value.toLowerCase());renderRoot(A.roots[i]);window.scrollTo(0,0);return;}}return;}
 var b=e.target.closest?e.target.closest('.tab'):null;if(!b)return;lang=b.getAttribute('data-lang');applyLang();
});
q.oninput=function(){renderList(q.value.toLowerCase());};
renderList('');if(A.roots.length){renderList('');renderRoot(A.roots[0]);}
</script></body></html>
"""


ABBREV_HTML = r"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PWG — словарь сокращений</title>
<style>
:root{--bg:#fff;--fg:#1a1a1a;--mut:#6a6a6a;--line:#e4e4e4;--accent:#7a1f1f;--card:#fafafa}
@media(prefers-color-scheme:dark){:root{--bg:#161616;--fg:#e8e8e8;--mut:#9a9a9a;--line:#333;--accent:#e6928a;--card:#1e1e1e}}
*{box-sizing:border-box}body{margin:0;font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;color:var(--fg);background:var(--bg)}
#wrap{max-width:1000px;margin:0 auto;padding:20px 24px 60px}
a{color:var(--accent)}
h1{font-size:24px;margin:4px 0 4px}
.back{font-size:13px;color:var(--mut);text-decoration:none;margin-bottom:10px;display:inline-block}
.summary{color:var(--mut);font-size:13px;margin:6px 0 16px;line-height:1.6}
.summary b{color:var(--fg)}
#q{width:100%;max-width:360px;padding:7px 10px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);margin-bottom:14px}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th,td{text-align:left;padding:6px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--mut);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.03em;position:sticky;top:0;background:var(--bg)}
tr:hover td{background:var(--card)}
.tok{font-family:ui-monospace,monospace;white-space:nowrap}
.bucket{display:inline-block;font-size:10px;border-radius:9px;padding:1px 7px;letter-spacing:.02em}
.bucket.translated{background:#1a7a3a;color:#fff}
.bucket.latin{background:var(--mut);color:#fff}
.bucket.unresolved{background:#a04000;color:#fff}
.ru{color:var(--fg)}.ru.na{color:var(--mut);font-style:italic}
.count{text-align:right;font-variant-numeric:tabular-nums}
</style></head><body><div id="wrap">
<a class="back" href="index.html">← к статьям</a>
<h1>Словарь сокращений PWG</h1>
<div class="summary" id="summary">Загрузка…</div>
<input id="q" placeholder="фильтр по сокращению / расшифровке…">
<table><thead><tr><th>Сокращение</th><th>×</th><th>Статей</th><th>DE</th><th>EN</th><th>RU (в тексте)</th><th>Статус</th></tr></thead>
<tbody id="rows"></tbody></table>
</div>
<script src="abbreviations.js"></script>
<script>
var ROWS=window.AB_ROWS||[];
var tbody=document.getElementById('rows'), q=document.getElementById('q');
var BUCKET_LABEL={translated:'переведено на RU',latin:'международный (лат.)',unresolved:'не найдено в pwgab'};
function esc(x){return x==null?'':(''+x);}
function render(filter){
 tbody.innerHTML='';
 var f=(filter||'').toLowerCase();
 ROWS.filter(function(r){
  if(!f)return true;
  return r.token.toLowerCase().indexOf(f)>=0||(r.de||'').toLowerCase().indexOf(f)>=0
   ||(r.en||'').toLowerCase().indexOf(f)>=0||(r.ru_display||'').toLowerCase().indexOf(f)>=0;
 }).forEach(function(r){
  var tr=document.createElement('tr');
  var ru = r.ru_display ? '<span class="ru">'+esc(r.ru_display)+'</span>' : '<span class="ru na">— (как в DE)</span>';
  tr.innerHTML='<td class="tok">'+esc(r.token)+'</td>'
   +'<td class="count">'+r.count+'</td>'
   +'<td class="count">'+r.n_roots+'</td>'
   +'<td>'+esc(r.de)+'</td>'
   +'<td>'+esc(r.en)+'</td>'
   +'<td>'+ru+'</td>'
   +'<td><span class="bucket '+r.bucket+'">'+BUCKET_LABEL[r.bucket]+'</span></td>';
  tbody.appendChild(tr);
 });
}
var total=ROWS.reduce(function(a,r){return a+r.count;},0);
var translated=ROWS.filter(function(r){return r.bucket==='translated';}).reduce(function(a,r){return a+r.count;},0);
var latin=ROWS.filter(function(r){return r.bucket==='latin';}).reduce(function(a,r){return a+r.count;},0);
var unresolved=ROWS.filter(function(r){return r.bucket==='unresolved';}).reduce(function(a,r){return a+r.count;},0);
document.getElementById('summary').innerHTML=
 '<b>'+ROWS.length+'</b> различных сокращений · <b>'+total+'</b> употреблений во всём корпусе PWG→RU.<br>'
 +'В колонке RU: <b>'+translated+'</b> ('+Math.round(100*translated/total)+'%) переведены на русский (Bein.→эпит., s.u.→см. и т.п.); '
 +'<b>'+latin+'</b> ('+Math.round(100*latin/total)+'%) — грамматические категории (падеж/наклонение/залог/часть речи), '
 +'оставлены международным латинским сокращением по решению 10-07-2026 (только подсказка при наведении); '
 +(unresolved?('<b>'+unresolved+'</b> ('+Math.round(100*unresolved/total)+'%) не найдены в таблице pwgab (791 запись) — редкие/нестандартные формы.'):'все распознаны таблицей pwgab.');
q.oninput=function(){render(q.value);};
render('');
</script></body></html>
"""


def emit_abbreviations(model):
    """abbreviations.html + abbreviations.js — the site-wide abbreviation
    dashboard (per-article tooltips live inline in each root's rendered HTML;
    this is the corpus-wide view MG asked for: every distinct <ab> token, its
    frequency, how many articles use it, its authoritative DE/EN expansion,
    and whether/how it renders in the RU column)."""
    rows = ab_frequency(model)
    with open(os.path.join(OUT_DIR, 'abbreviations.js'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('window.AB_ROWS=')
        json.dump(rows, f, ensure_ascii=False)
        f.write(';\n')
    with open(os.path.join(OUT_DIR, 'abbreviations.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(ABBREV_HTML)
    return rows


def emit(model):
    coloc = load_colocation({r['root'] for r in model})
    os.makedirs(os.path.join(OUT_DIR, 'md', 'subcards'), exist_ok=True)
    # per-root + per-subcard markdown
    for r in model:
        with open(os.path.join(OUT_DIR, 'md', '%s.md' % r['root']), 'w',
                  encoding='utf-8', newline='\n') as f:
            f.write(root_md(r))
        for sub in r['subcards']:
            safe = re.sub(r'[^A-Za-z0-9_.~-]', '_', sub['key'])
            with open(os.path.join(OUT_DIR, 'md', 'subcards', '%s.md' % safe), 'w',
                      encoding='utf-8', newline='\n') as f:
                f.write(subcard_md(sub))
    # index markdown
    with open(os.path.join(OUT_DIR, 'md', 'INDEX.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# PWG articles — RU (+EN)\n\n')
        for r in model:
            f.write('- [%s](%s.md) — %d senses%s\n' % (
                r['iast'], r['root'], r['n_senses'],
                ', EN %d' % r['n_en_senses'] if r['en_available'] else ''))
    # LAZY-LOAD: articles.js carries only a tiny per-root INDEX (no senses); each root's
    # heavy pre-rendered HTML goes to roots/<safe>.js as window.ROOT["<root>"] = [...]. The
    # page loads the index (KB) up front and injects one root file on click via <script src>
    # (works from file:// too, unlike fetch). First paint drops from ~13 MB to a few KB + 1 root.
    os.makedirs(os.path.join(OUT_DIR, 'roots'), exist_ok=True)
    index = {'roots': []}
    for r in model:
        safe = re.sub(r'[^A-Za-z0-9_.~-]', '_', r['root'])
        index['roots'].append({
            'root': r['root'], 'safe': safe, 'iast': r['iast'], 'en_available': r['en_available'],
            'n_subcards': r['n_subcards'], 'n_senses': r['n_senses'],
            'n_ru_senses': r['n_ru_senses'], 'n_en_senses': r['n_en_senses'],
            'ls': r['ls'], 'ls_linked': r['ls_linked'],
            'ls_scan': r['ls_scan'], 'ls_html': r['ls_html']})
        subs = [{'key': s['key'], 'h': s['h'], 'iast': s['iast'], 'senses': [
            {'tag': x['tag'], 'de_html': x['de_html'], 'ru_html': x['ru_html'],
             'en_html': x['en_html'], 'dcs': x['dcs'], 'src': x['src']}
            for x in s['senses']]} for s in r['subcards']]
        with open(os.path.join(OUT_DIR, 'roots', '%s.js' % safe), 'w', encoding='utf-8', newline='\n') as f:
            f.write('window.ROOT=window.ROOT||{};window.ROOT[%s]=' % json.dumps(r['root'], ensure_ascii=False))
            json.dump(subs, f, ensure_ascii=False)
            f.write(';\n')
            f.write('window.COLOC=window.COLOC||{};window.COLOC[%s]=' % json.dumps(r['root'], ensure_ascii=False))
            json.dump(coloc.get(r['root'], []), f, ensure_ascii=False)
            f.write(';\n')
    with open(os.path.join(OUT_DIR, 'articles.js'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('window.ARTICLES=')
        json.dump(index, f, ensure_ascii=False)
        f.write(';\n')
    with open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(INDEX_HTML)
    ab_rows = emit_abbreviations(model)
    return ab_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', help='debug: print one root and exit')
    args = ap.parse_args()
    model = build_model()
    if args.root:
        r = next((x for x in model if x['root'] == args.root), None)
        if not r:
            sys.exit('no root %r (have %d)' % (args.root, len(model)))
        print(root_md(r))
        return
    emit(model)
    roots = len(model)
    senses = sum(r['n_senses'] for r in model)
    en_roots = sum(1 for r in model if r['en_available'])
    print('article_site/: %d roots, %d senses, %d roots with EN' % (roots, senses, en_roots))
    print('  index.html + articles.js + md/%d root files + md/subcards/' % roots)
    print('  open: %s' % os.path.join(OUT_DIR, 'index.html'))


if __name__ == '__main__':
    main()
