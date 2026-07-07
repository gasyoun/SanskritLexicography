#!/usr/bin/env python
r"""H290 (H215 Slice 4a) -- oral-corpus TEXT + PDF ingest for the Sa->Ru TM.

Slice 4 (ingest_oral.py) turns a PRE-ALIGNED pair of timecoded subtitle tracks
(parallel Sanskrit + Russian VTT/SRT of one recording) into oral corpus rows. That
covers only one shape. This module -- Slice 4a -- is the TEXT + PDF front-end for the
transcripts that are NOT a clean parallel subtitle pair, per MG's 07-07-2026 split of
the oral slice. It reads ONE lecture transcript (however dirty) plus its optional PDF/
DOC companion(s) and produces the SAME corpus_builder seg-row schema ingest_oral emits
(`{group, seg, passage, text, modality:oral, ...}`) so everything downstream --
build_l0.py -> tm_grade.py -> build_tmx.py -- consumes it unchanged. No audio, no ASR
(that is Slice 4b, H174 coordination, deferred ~1 week).

MG design rulings (07-07-2026), all honored:

  1. Source structure VARIES per transcript -- DETECT which of three shapes it is:
       (bi)     bilingual: spoken Sanskrit + its Russian interleaved   -> Sa<->Ru
       (sa+pdf) Sanskrit-only recitation, Russian only in a PDF handout -> Sa(txt)<->Ru(pdf)
       (ru+cit) Russian lecture quoting Sanskrit inline                -> citation<->gloss
     Ambiguous -> FLAG for the reviewable sample, never guess silently.
  2. PDFs are heterogeneous -- classify each companion's ROLE first:
       edited-ru | sanskrit-source | commentary  (a lecture may have several).
     The edited-ru case becomes a MULTI-REFERENCE pair (spoken vs written of one verse)
     -- emitted as a SEPARATE work sharing the verse `passage`, so tm_grade's
     seg_key=(passage,slp1) computes the two as a consensus signal.
  3. Home = RussianTranslation/src, beside ingest_oral/build_l0; oral rows -> same TM.
  4. Grade = source-weight PENALTY only (NOT a hard cap): oral units carry the lowered
     base grade already set in Slice 4 (tm_grade.ORAL_PENALTY). MG ruling 4 further
     wants an oral unit to reach A when it AGREES WITH A WRITTEN translation (consensus
     promotes). NOTE: the merged Slice-4 build_tmx.oral_cap() currently BARS oral from
     A unless human-adjudicated -- these conflict. This scaffold does NOT silently flip
     that merged publication-grade gate; the policy reconciliation is deferred to the
     real-data step (needs oral graded output to validate) and tracked as an @DECIDE.
     See ORAL_INGEST.md "Slice 4a" + the FINDINGS caveat.

STATUS: data-independent SCAFFOLD. The source-type detector, the PDF-role classifier,
the docx-to-md companion wiring, the three per-shape extractors and the multi-reference
keying are all exercised on a synthetic fixture (`selftest`). The ONE open prerequisite
is a representative real sample (one transcript + its PDF) -- until it arrives the
(sa+pdf) sentence aligner is a labelled index-pairing PLACEHOLDER (the real LaBSE+
Vecalign backend is Slice-4a step 3, gated), and the detector/classifier heuristics are
uncalibrated. Real ingest of a series is step 4.

  python build_oral_l0.py detect   <transcript.txt> [--pdf companion.mdx]  source-type
  python build_oral_l0.py classify <companion.mdx>                          PDF role
  python build_oral_l0.py ingest   <transcript.txt> --work W --out OUT \
                          [--pdf companion.mdx]                             -> seg rows
  python build_oral_l0.py selftest                                         fixture asserts

RIGHTS: oral consent != text copyright (heavier gate -- H174). Emitted rows stay under
the gitignored corpus tree; run /publish-safety-check before anything third-party
leaves it. Only this generator + docs are committed.

Model provenance: deterministic heuristics, no LLM call, no clock in the record.
Companion PDF/DOC -> .mdx is delegated to the /docx-to-md skill (never a flat .md).
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import build_tmx     # has_cyr() -- the one canonical never-invent guard
import ingest_oral    # to_corpus_rows(), MODALITY_ORAL -- reuse the emitter + guards

HERE = os.path.dirname(os.path.abspath(__file__))

# orality sub-type -> ; ordering recited > interpreted > handout is the trust order MG
# gave (recited faithful text > live interpretation > unverified handout). Carried as
# metadata now; a per-subtype weight is a real-data-calibration step, not scaffold.
ORALITY_RECITED = 'recited'          # (bi)/(sa+pdf) transcript: faithful recitation
ORALITY_INTERPRETED = 'interpreted'  # (ru+cit): live spoken gloss/interpretation
ORALITY_HANDOUT = 'handout'          # PDF handout side of a (sa+pdf) pair

# --------------------------------------------------------------- script detection
DEVA = re.compile('[ऀ-ॿ]')                       # Devanagari block U+0900..097F
IAST = re.compile('[Ā-ſḀ-ỿāīūṛṝḷṅñṇśṣṭḍṃḥ]')     # precomposed IAST diacritics
LATIN = re.compile('[A-Za-z]')                    # ASCII incl. SLP1/HK romanization


def _has(rx, s):
    return bool(s) and bool(rx.search(s))


def script_ratios(text):
    """Fraction of *alphabetic word tokens* that are Russian (Cyrillic) vs Sanskrit,
    over one blob. In this bilingual corpus the only two languages are Russian and
    Sanskrit, and Sanskrit appears in ANY of three scripts -- Devanagari, IAST-
    diacritic romanization, OR SLP1/HK ASCII romanization (`yogaH`, `karmaR`). So a
    non-Cyrillic alphabetic token counts as Sanskrit; digits/punct (verse numbers) are
    excluded from the denominator. Token-level, so a lone citation in a Russian line
    still registers. (Heuristic -- assumes ~no stray English; calibrated on the real
    sample per the Slice-4a prerequisite.)"""
    toks = re.findall(r'\S+', text or '')
    alpha = [t for t in toks
             if build_tmx.has_cyr(t) or _has(DEVA, t) or _has(IAST, t) or _has(LATIN, t)]
    if not alpha:
        return {'cyr': 0.0, 'sa': 0.0, 'n': 0}
    cyr = sum(1 for t in alpha if build_tmx.has_cyr(t))
    sa = len(alpha) - cyr        # non-Cyrillic alphabetic = Sanskrit (native or romanized)
    n = len(alpha)
    return {'cyr': cyr / n, 'sa': sa / n, 'n': n}


def _line_lang(line):
    """Dominant language of ONE transcript line: 'ru', 'sa', or '' (neither)."""
    r = script_ratios(line)
    if r['n'] == 0:
        return ''
    if r['cyr'] >= 0.5:
        return 'ru'
    if r['sa'] > r['cyr']:
        return 'sa'
    return 'ru' if r['cyr'] > 0 else ''


# ---------------------------------------------------------- (1) source-type detect
def detect_source_type(transcript_text, has_companion_pdf=False):
    """Return (source_type, evidence). source_type in {'bi','sa+pdf','ru+cit',
    'ambiguous'}. Cheap signals only (MG ruling 1): per-line dominant script, the
    Sa/Ru line balance, and whether a companion PDF exists. Ambiguous is a first-class
    outcome -- it routes the transcript to the human reviewable sample, never a guess."""
    lines = [ln for ln in (transcript_text or '').splitlines() if ln.strip()]
    langs = [_line_lang(ln) for ln in lines]
    n_sa = langs.count('sa')
    n_ru = langs.count('ru')
    n_lines = n_sa + n_ru
    ev = {'n_lines': len(lines), 'sa_lines': n_sa, 'ru_lines': n_ru,
          'has_pdf': bool(has_companion_pdf)}
    if n_lines == 0:
        return 'ambiguous', {**ev, 'why': 'no language-bearing lines'}

    ru_share = n_ru / n_lines
    sa_share = n_sa / n_lines

    # (bi) bilingual: BOTH scripts substantially present as whole lines (interleaved).
    if n_sa >= 2 and n_ru >= 2 and 0.25 <= ru_share <= 0.75:
        return 'bi', {**ev, 'why': 'both scripts as full lines, balanced'}

    # (ru+cit) Russian lecture quoting Sanskrit: Russian dominant, Sanskrit a minority
    # (whole-line OR inline citations inside otherwise-Russian lines).
    inline_cit = sum(1 for ln, lg in zip(lines, langs)
                     if lg == 'ru' and (_has(DEVA, ln) or script_ratios(ln)['sa'] > 0))
    if ru_share >= 0.6 and (sa_share > 0 or inline_cit > 0):
        return 'ru+cit', {**ev, 'inline_citations': inline_cit,
                          'why': 'Russian dominant with Sanskrit citations'}

    # (sa+pdf) Sanskrit-only recitation: Sanskrit dominant, little/no Russian in the
    # transcript -- Russian expected in the companion PDF.
    if sa_share >= 0.6 and ru_share <= 0.15:
        if has_companion_pdf:
            return 'sa+pdf', {**ev, 'why': 'Sanskrit-only transcript + companion PDF'}
        return 'ambiguous', {**ev,
                             'why': 'Sanskrit-only transcript but NO companion PDF -> '
                                    'no Russian side to align; needs the handout/sample'}

    return 'ambiguous', {**ev, 'why': 'no clear Sa/Ru shape (ru_share=%.2f sa_share=%.2f)'
                                      % (ru_share, sa_share)}


# ------------------------------------------------------------ (2) PDF-role classify
_VERSE_NUM = re.compile(r'(?m)^\s*\(?\d+[.,]\d+\)?[.)\s]')   # 2.47 / (2.47) verse refs
_FOOTNOTE = re.compile(r'(?m)^\s*(\[\d+\]|\*+\s|Прим\.|прим\.|сноск)')


def classify_pdf_role(mdx_text):
    """Return (role, evidence). role in {'edited-ru','sanskrit-source','commentary'}
    (MG ruling 2). Language mix + structure only; run AFTER /docx-to-md turned the
    companion into .mdx (tables preserved). A handout may need several calls on its
    sections; this classifies one blob."""
    r = script_ratios(mdx_text)
    verses = len(_VERSE_NUM.findall(mdx_text or ''))
    notes = len(_FOOTNOTE.findall(mdx_text or ''))
    ev = {'cyr': round(r['cyr'], 3), 'sa': round(r['sa'], 3),
          'verse_refs': verses, 'note_markers': notes, 'n_tokens': r['n']}

    # sanskrit-source: Sanskrit-dominant, verse-numbered -> the source text itself.
    if r['sa'] >= 0.5 and r['cyr'] <= 0.2:
        return 'sanskrit-source', {**ev, 'why': 'Sanskrit-dominant, verse-shaped'}

    # commentary: Russian prose whose structure is note/footnote-heavy rather than a
    # clean verse-parallel translation.
    if r['cyr'] >= 0.5 and notes >= 2 and notes >= verses:
        return 'commentary', {**ev, 'why': 'Russian prose, footnote/notes-shaped'}

    # edited-ru: Russian-dominant, verse-parallel -> an edited written translation of
    # the passage (the MULTI-REFERENCE case vs the spoken rendering).
    if r['cyr'] >= 0.5:
        return 'edited-ru', {**ev, 'why': 'Russian-dominant, verse-parallel translation'}

    role = 'sanskrit-source' if r['sa'] > r['cyr'] else 'commentary'
    return role, {**ev, 'why': 'low-confidence fallback -- flag for review'}


def companion_to_mdx(path):
    """Load a companion's text for classify_pdf_role. A .pdf/.doc/.docx MUST first be
    converted by the /docx-to-md skill (-> .mdx, tables preserved) -- we never
    reimplement that pipeline nor accept a flat .md. An already-converted .mdx (or a
    plain .md/.txt) is read directly."""
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.mdx', '.md', '.txt'):
        with open(path, encoding='utf-8') as f:
            return f.read()
    raise RuntimeError(
        'convert %s with the /docx-to-md skill first (-> .mdx); build_oral_l0 does not '
        're-implement PDF/DOCX extraction' % path)


# --------------------------------------------------- (3) per-shape pair extractors
_CIT_SPLIT = re.compile(r'[:—–-]')          # ru gloss usually follows a colon/dash
_PASSAGE_RX = re.compile(r'\b(\d+[.,]\d+)\b')  # a verse ref like 2.47 in a ru line


def pairs_bilingual(text):
    """(bi) interleaved transcript -> [{sa, ru, passage}]. Pair each Sanskrit line
    with the Russian line that follows it (the interleave order MG described). A
    Sanskrit line with no following Russian, or vice versa, is left unpaired (dropped
    downstream by the guard) -- never cross-paired."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    pairs = []
    i = 0
    idx = 0
    while i < len(lines) - 1:
        if _line_lang(lines[i]) == 'sa' and _line_lang(lines[i + 1]) == 'ru':
            idx += 1
            pairs.append({'sa': lines[i], 'ru': lines[i + 1], 'passage': str(idx)})
            i += 2
        else:
            i += 1
    return pairs


def pairs_ru_citation(text):
    """(ru+cit) Russian lecture -> [{sa, ru, passage}]. For each Russian line that
    carries a Sanskrit citation, take the citation as `sa` and the surrounding Russian
    (after the citation, else the whole line) as the `ru` gloss. Commentary-style: one
    unit per cited verse, `passage` from a verse ref in the line when present."""
    pairs = []
    idx = 0
    cur_passage = None    # a verse ref announced on ANY recent line persists (the
    #                       lecturer says "стих 2.47" then quotes it on the next line)
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        m = _PASSAGE_RX.search(ln)
        if m:
            cur_passage = m.group(1)
        r = script_ratios(ln)
        if not (r['cyr'] > 0 and r['sa'] > 0):
            continue
        # split the line into runs; the Sanskrit run is the citation, the Cyrillic
        # remainder is the gloss.
        sa_toks = [t for t in re.findall(r'\S+', ln)
                   if not build_tmx.has_cyr(t) and (_has(DEVA, t) or _has(IAST, t)
                                                    or _has(LATIN, t))]
        ru_toks = [t for t in re.findall(r'\S+', ln) if build_tmx.has_cyr(t)]
        sa = ' '.join(sa_toks).strip(' .,:;—–-')
        ru = ' '.join(ru_toks).strip()
        if len(sa) < ingest_oral.MIN_CUE_CHARS or not build_tmx.has_cyr(ru):
            continue
        idx += 1
        pairs.append({'sa': sa, 'ru': ru, 'passage': cur_passage or str(idx)})
    return pairs


def pairs_sa_plus_pdf(sa_text, pdf_ru_text):
    """(sa+pdf) Sanskrit transcript + Russian handout -> [{sa, ru, passage}].

    PLACEHOLDER ALIGNMENT (Slice-4a step 3 is the real backend): pairs the Sanskrit
    verse lines with the handout's Russian verse lines by verse-number when both sides
    carry `N.N` refs, else by index. The real sentence aligner (LaBSE/LASER + Vecalign,
    behind ingest/tm_align's proxy-fallback pattern) lands with the calibration step
    once a real sample exists -- this deterministic pairing is honest scaffolding, not
    a trained alignment, and is labelled `align='placeholder-index'` on every pair."""
    sa_lines = [ln.strip() for ln in sa_text.splitlines()
                if ln.strip() and _line_lang(ln) == 'sa']
    ru_lines = [ln.strip() for ln in pdf_ru_text.splitlines()
                if ln.strip() and _line_lang(ln) == 'ru']

    def keyed(lines):
        out = {}
        for ln in lines:
            m = _PASSAGE_RX.search(ln)
            if m:
                out[m.group(1)] = ln
        return out

    sa_keyed, ru_keyed = keyed(sa_lines), keyed(ru_lines)
    pairs = []
    shared = [k for k in sa_keyed if k in ru_keyed]
    if shared:                                    # verse-number join (best available)
        for k in shared:
            pairs.append({'sa': sa_keyed[k], 'ru': ru_keyed[k], 'passage': k,
                          'align': 'placeholder-versekey'})
    elif len(sa_lines) == len(ru_lines):          # equal counts -> index pairing
        for i, (s, ru) in enumerate(zip(sa_lines, ru_lines), 1):
            pairs.append({'sa': s, 'ru': ru, 'passage': str(i),
                          'align': 'placeholder-index'})
    # unequal counts + no shared verse keys -> cannot align safely; emit nothing
    # (never zip-truncate -- the F1 fabrication lesson). Caller sees 0 pairs -> flag.
    return pairs


# --------------------------------------------------- (4) emit corpus seg-rows
def ingest(transcript_path, work, out_path, pdf_path=None, sample=None):
    """Full text+PDF ingest of ONE lecture: detect the shape, route to the right
    extractor, emit corpus_builder seg-rows via ingest_oral.to_corpus_rows (the same
    guards + schema build_l0 consumes), tagging orality + source_type."""
    text = open(transcript_path, encoding='utf-8').read()
    pdf_text = companion_to_mdx(pdf_path) if pdf_path else None
    st, ev = detect_source_type(text, has_companion_pdf=bool(pdf_path))
    print('detect: %s -- %s' % (st, ev.get('why')))
    if st == 'ambiguous':
        sys.exit('ambiguous source shape -> route this transcript to the human '
                 'reviewable sample; not auto-ingested (%s)' % ev.get('why'))

    if st == 'bi':
        pairs, orality = pairs_bilingual(text), ORALITY_RECITED
    elif st == 'ru+cit':
        pairs, orality = pairs_ru_citation(text), ORALITY_INTERPRETED
    else:  # sa+pdf
        if not pdf_text:
            sys.exit('sa+pdf shape needs --pdf (the Russian handout)')
        role, rev = classify_pdf_role(pdf_text)
        print('pdf-role: %s -- %s' % (role, rev.get('why')))
        if role == 'sanskrit-source':
            sys.exit('companion is the Sanskrit source, not a Russian rendering -> no '
                     'Russian side to align from this PDF (needs an edited-ru handout)')
        pairs, orality = pairs_sa_plus_pdf(text, pdf_text), ORALITY_RECITED

    if sample is not None:
        pairs = pairs[:sample]
    extra = {'orality': orality, 'source_type': st}
    rows, kept, dropped = ingest_oral.to_corpus_rows(pairs, work, extra=extra)
    if not rows:
        sys.exit('0 valid oral pairs after the never-invent guards (shape=%s). Check '
                 'the Russian side carries Cyrillic / the alignment produced pairs.' % st)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as out:
        for r in rows:
            out.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('build_oral_l0: shape=%s orality=%s -> %s' % (st, orality, out_path))
    print('  %d pairs kept, %d dropped (guard), %d seg-rows, work=%s'
          % (kept, dropped, len(rows), work))
    print('  next: copy to SamudraManthanam/web/corpus_builder/jsonl/%s.jsonl, then '
          '`python build_l0.py build --work %s`' % (work, work))
    return 0


# --------------------------------------------------------------------- fixture
FIX_BI = (
    "yogaH karmasu kOSalam\n"
    "йога есть искусность в действиях\n"
    "samatvaM yoga ucyate\n"
    "равновесие именуется йогой\n"
)
FIX_SA_ONLY = (
    "2.47 karmaRy evADikAras te mA PaleShu kadAcana\n"
    "2.48 yogasTaH kuru karmARi saNgaM tyaktvA DanaMjaya\n"
)
FIX_RU_CIT = (
    "Сегодня разберём знаменитый стих 2.47 из Гиты.\n"
    "Кришна говорит karmaRy evADikAras te — у тебя есть право лишь на действие.\n"
    "Здесь ключевое слово aDikAra то есть право или полномочие человека.\n"
    "Дальше учитель подробно поясняет смысл этого стиха ученикам своим.\n"
)
FIX_PDF_EDITED_RU = (
    "2.47 Ты имеешь право лишь на действие, но никогда на его плоды.\n"
    "2.48 Утвердившись в йоге, совершай действия, оставив привязанность.\n"
)
FIX_PDF_SA_SOURCE = (
    "2.47 karmaRy evADikAras te mA PaleShu kadAcana\n"
    "2.48 yogasTaH kuru karmARi saNgaM tyaktvA DanaMjaya\n"
)
FIX_PDF_COMMENTARY = (
    "[1] Прим. переводчика: слово adhikara здесь означает не право а сфера долга.\n"
    "[2] Прим.: сравни с трактовкой Шанкары в его известном комментарии к главе.\n"
    "Это замечание очень важно для верного понимания всей второй главы поэмы.\n"
)


def selftest():
    import tempfile

    # (1) source-type detector -- 3 shapes + ambiguous guards
    assert detect_source_type(FIX_BI)[0] == 'bi', detect_source_type(FIX_BI)
    assert detect_source_type(FIX_SA_ONLY, has_companion_pdf=True)[0] == 'sa+pdf', \
        detect_source_type(FIX_SA_ONLY, has_companion_pdf=True)
    assert detect_source_type(FIX_SA_ONLY, has_companion_pdf=False)[0] == 'ambiguous'
    assert detect_source_type(FIX_RU_CIT)[0] == 'ru+cit', detect_source_type(FIX_RU_CIT)
    assert detect_source_type('')[0] == 'ambiguous'

    # (2) PDF-role classifier -- 3 roles
    assert classify_pdf_role(FIX_PDF_EDITED_RU)[0] == 'edited-ru', \
        classify_pdf_role(FIX_PDF_EDITED_RU)
    assert classify_pdf_role(FIX_PDF_SA_SOURCE)[0] == 'sanskrit-source', \
        classify_pdf_role(FIX_PDF_SA_SOURCE)
    assert classify_pdf_role(FIX_PDF_COMMENTARY)[0] == 'commentary', \
        classify_pdf_role(FIX_PDF_COMMENTARY)

    # (3) per-shape extractors -> pairs
    bp = pairs_bilingual(FIX_BI)
    assert len(bp) == 2 and bp[0]['sa'].startswith('yogaH') \
        and build_tmx.has_cyr(bp[0]['ru']), bp
    cp = pairs_ru_citation(FIX_RU_CIT)
    assert len(cp) >= 2 and all(build_tmx.has_cyr(p['ru']) for p in cp), cp
    assert any(p['passage'] == '2.47' for p in cp), 'verse ref not captured: %s' % cp
    sp = pairs_sa_plus_pdf(FIX_SA_ONLY, FIX_PDF_EDITED_RU)
    assert len(sp) == 2 and sp[0]['passage'] == '2.47' \
        and sp[0]['align'] == 'placeholder-versekey', sp
    # unequal counts + no shared verse keys -> emit nothing, never zip-truncate
    assert pairs_sa_plus_pdf("agni indra soma\nvaruna mitra",
                             "только одна строка перевода здесь") == []

    # (4) emit -> corpus seg-rows in the ingest_oral schema, guards applied, orality
    # + source_type tagged; build_l0 then consumes them into L0 units.
    d = tempfile.mkdtemp(prefix='oral_l0a_selftest_')
    out = os.path.join(d, 'lecture01.jsonl')
    open(os.path.join(d, 't.txt'), 'w', encoding='utf-8').write(FIX_BI)
    ingest(os.path.join(d, 't.txt'), 'lecture01', out)
    rows = [json.loads(l) for l in open(out, encoding='utf-8') if l.strip()]
    assert rows and all(r['modality'] == 'oral' for r in rows), rows
    assert all(r.get('orality') == ORALITY_RECITED for r in rows), 'orality not tagged'
    assert all(r.get('source_type') == 'bi' for r in rows), 'source_type not tagged'
    sa_rows = [r for r in rows if r['seg'] == 'sa']
    ru_rows = [r for r in rows if r['seg'] == 'ru']
    assert len(sa_rows) == len(ru_rows) == 2, rows

    # build_l0 consumes them unchanged -> L0 units carrying modality/orality
    import build_l0
    groups = dict(build_l0.iter_groups(out))
    units = []
    for g, dd in groups.items():
        units.extend(build_l0.units_for_group(g, dd, 'lecture01', {}))
    assert units and all(u.get('modality') == 'oral' for u in units), units
    assert all(u.get('orality') == ORALITY_RECITED for u in units), \
        'orality lost through build_l0'

    # (5) MULTI-REFERENCE invariant (MG ruling 2): a spoken rendering and the edited-ru
    # handout of the SAME verse are DISTINCT works sharing the verse `passage`, so
    # tm_grade.seg_key=(passage,slp1) computes them as a consensus signal.
    spoken = ingest_oral.to_corpus_rows(
        [{'sa': 'aDikAras', 'ru': 'право', 'passage': '2.47'}],
        'lecture01', extra={'orality': ORALITY_RECITED, 'source_type': 'bi'})[0]
    handout = ingest_oral.to_corpus_rows(
        [{'sa': 'aDikAras', 'ru': 'право', 'passage': '2.47'}],
        'lecture01_handout', extra={'orality': ORALITY_HANDOUT, 'source_type': 'sa+pdf'})[0]
    sp_ru = [r for r in spoken if r['seg'] == 'ru'][0]
    hd_ru = [r for r in handout if r['seg'] == 'ru'][0]
    assert sp_ru['group'] != hd_ru['group'], 'multi-ref must be distinct groups/works'
    assert sp_ru['passage'] == hd_ru['passage'] == '2.47', 'multi-ref shares the verse'

    print('build_oral_l0 selftest OK -- 3/3 source-types (+2 ambiguous guards), 3/3 '
          'pdf-roles, 3 extractors, no-zip-truncate guard, seg-rows->build_l0 carry '
          'modality+orality, multi-reference verse shared')
    return 0


def _cmd_detect(a):
    text = open(a.transcript, encoding='utf-8').read()
    st, ev = detect_source_type(text, has_companion_pdf=bool(a.pdf))
    print(json.dumps({'source_type': st, 'evidence': ev}, ensure_ascii=False, indent=2))
    return 0


def _cmd_classify(a):
    st, ev = classify_pdf_role(companion_to_mdx(a.companion))
    print(json.dumps({'role': st, 'evidence': ev}, ensure_ascii=False, indent=2))
    return 0


def main():
    ap = argparse.ArgumentParser(
        description='Oral-corpus TEXT+PDF ingest for the Sa->Ru TM (H290 / Slice 4a)')
    sub = ap.add_subparsers(dest='cmd', required=True)

    d = sub.add_parser('detect', help='source-type of one transcript')
    d.add_argument('transcript')
    d.add_argument('--pdf', default=None, help='companion path (presence flags sa+pdf)')

    c = sub.add_parser('classify', help='role of one companion (.mdx/.md/.txt)')
    c.add_argument('companion')

    g = sub.add_parser('ingest', help='transcript(+pdf) -> corpus_builder seg-rows')
    g.add_argument('transcript')
    g.add_argument('--work', required=True, help='work name (unique group prefix)')
    g.add_argument('--pdf', default=None, help='companion Russian handout (.mdx)')
    g.add_argument('--out', required=True, help='output <work>.jsonl')
    g.add_argument('--sample', type=int, default=None)

    sub.add_parser('selftest', help='fixture -> detect/classify/extract/emit, assert')

    a = ap.parse_args()
    if a.cmd == 'detect':
        return _cmd_detect(a)
    if a.cmd == 'classify':
        return _cmd_classify(a)
    if a.cmd == 'ingest':
        return ingest(a.transcript, a.work, a.out, pdf_path=a.pdf, sample=a.sample)
    if a.cmd == 'selftest':
        return selftest()
    return 1


if __name__ == '__main__':
    sys.exit(main())
