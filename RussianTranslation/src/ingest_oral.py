#!/usr/bin/env python
r"""H215 Slice 4 -- oral-corpus ingest: timecoded transcript -> corpus jsonl.

The written TM (Slices 1-3) turns verse-aligned scholarly translations into a
graded TMX. Slice 4 adds the **oral register**: recorded/spoken Sanskrit with a
Russian rendering, carrying time anchors and a `modality: oral` mark, ingested
into the *same* L0 pipeline (build_l0.py -> tm_grade.py -> build_tmx.py) rather
than a forked one.

This is the **Sa->Ru-alignment half of H174** (spoken-sanskrit-corpus): H174 owns
sourcing + ASR-transcript cleaning of the raw material; this owns turning a
*cleaned, timecoded* transcript into a graded parallel-corpus unit. The schema
emitted here is the shared contract -- see ORAL_INGEST.md.

No ASR call happens here: per H174's interview the material is *existing*
machine-transcripts (VTT/SRT subtitles, yt-dlp/Whisper output), not raw audio
needing fresh recognition. This tool parses those subtitle formats, pairs the
Sanskrit cues with their Russian rendering, applies the never-invent guards, and
emits the corpus_builder `<work>.jsonl` format build_l0.py already consumes --
plus `modality=oral`, `t_start`/`t_end` time anchors, `source_media`, and (when
the transcript carried it) a per-cue `asr_conf`.

  python ingest_oral.py convert --sa lecture.sa.vtt --ru lecture.ru.vtt \
         --work induizm-lecture-01 --media lecture01.mp3 --out <work>.jsonl
  python ingest_oral.py convert --pairs prealigned.jsonl --work W --out OUT
  python ingest_oral.py inspect lecture.sa.vtt      parse + show cue stats
  python ingest_oral.py selftest                    fixture -> convert, assert

The emitted `<work>.jsonl` goes in SamudraManthanam/web/corpus_builder/jsonl/
exactly like a written source (ADDING_TEXTS.md), then:
  python build_l0.py build --work <work>            -> corpus_l0.jsonl (modality carried)
  python tm_grade.py grade ...                        -> oral units get the lowered base grade
  python build_tmx.py build --l0 corpus_l0.jsonl     -> TMX with modality/time props

RIGHTS: recorded third-party speech is consent/rights-gated MORE than written
sources (H174 guardrail) -- no public release before /publish-safety-check +
per-source clearance (H215 Slice 5). Emitted jsonl stays under the gitignored
corpus tree.

Model provenance: deterministic parser (no LLM, no clock in the record) -- the
same transcript yields byte-identical output.
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import build_tmx  # has_cyr() -- reuse the one canonical never-invent guard

HERE = os.path.dirname(os.path.abspath(__file__))

MODALITY_ORAL = 'oral'

# A cue whose Sanskrit or Russian is shorter than this (stripped) is transcription
# noise (a stray timecode fragment, a lone punctuation mark) -- dropped, not paired.
MIN_CUE_CHARS = 2


def _to_slp1(iast):
    """IAST Sanskrit verse -> SLP1, using the SAME canonical transcoder the written
    corpus path uses (build_src.iast_to_slp1), so oral units carry a real SLP1 key
    (matches the written L0 `slp1`), not just the IAST surface. Lazy import with a
    graceful fallback: if the transcoder is unavailable the field is left empty and
    build_l0 falls back to the IAST surface as the source segment (still valid, just
    not SLP1-normalized). Whole-verse transliteration, NOT the per-word form_key."""
    iast = (iast or '').strip()
    if not iast:
        return ''
    try:
        import build_src
        return build_src.iast_to_slp1(iast)
    except Exception:
        return ''


# --------------------------------------------------------------- subtitle parsers
_TS = re.compile(r'(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{1,3})')


def _ts_to_sec(m):
    """A VTT/SRT timestamp match -> float seconds. Hours optional; ',' or '.' ms."""
    h = int(m.group(1) or 0)
    return h * 3600 + int(m.group(2)) * 60 + int(m.group(3)) + int(m.group(4)) / 1000.0


def _parse_cue_block(block):
    """A subtitle cue block (lines) -> (t_start, t_end, text) or None. Shared by the
    VTT and SRT readers: both put `START --> END` on one line, text on the following
    lines; SRT prefixes an integer index line which we skip."""
    lines = [ln.rstrip() for ln in block.splitlines() if ln.strip()]
    if not lines:
        return None
    ts_line_i = None
    for i, ln in enumerate(lines):
        if '-->' in ln:
            ts_line_i = i
            break
    if ts_line_i is None:
        return None
    left, _, right = lines[ts_line_i].partition('-->')
    ms, me = _TS.search(left), _TS.search(right)
    if not (ms and me):
        return None
    text = ' '.join(lines[ts_line_i + 1:]).strip()
    if not text:
        return None
    return (_ts_to_sec(ms), _ts_to_sec(me), text)


def parse_subtitles(text):
    """Parse VTT or SRT text into a list of cues [{t_start, t_end, text}]. Cue
    blocks are separated by blank lines in both formats; a leading `WEBVTT` header
    and `NOTE`/`STYLE` blocks (VTT) are skipped by the per-block timestamp check."""
    # normalize newlines; strip a BOM if the file carried one
    text = text.lstrip('﻿').replace('\r\n', '\n').replace('\r', '\n')
    cues = []
    for block in re.split(r'\n\s*\n', text):
        cue = _parse_cue_block(block)
        if cue is not None:
            t0, t1, body = cue
            # strip VTT inline tags (<c>, <00:00:01.000>) that some ASR emits
            body = re.sub(r'<[^>]+>', '', body).strip()
            # keep EVERY non-empty cue -- length/guard filtering happens in
            # to_corpus_rows, never here: dropping a short cue at parse time would
            # desync parallel Sa/Ru tracks and fabricate wrong index pairings.
            if body:
                cues.append({'t_start': round(t0, 3), 't_end': round(t1, 3),
                             'text': body})
    return cues


def parse_cue_file(path):
    ext = os.path.splitext(path)[1].lower()
    with open(path, encoding='utf-8') as f:
        data = f.read()
    if ext in ('.vtt', '.srt'):
        return parse_subtitles(data)
    if ext in ('.json', '.jsonl'):
        # a pre-parsed cue list: [{t_start, t_end, text}] or JSONL of the same
        out = []
        data = data.strip()
        if data.startswith('['):
            rows = json.loads(data)
        else:
            rows = [json.loads(l) for l in data.splitlines() if l.strip()]
        for r in rows:
            if r.get('text'):
                out.append({'t_start': r.get('t_start'), 't_end': r.get('t_end'),
                            'text': str(r['text']).strip(),
                            'asr_conf': r.get('asr_conf')})
        return out
    sys.exit('unsupported cue file (want .vtt/.srt/.json/.jsonl): %s' % path)


# ------------------------------------------------------------------- pairing
def pair_cues(sa_cues, ru_cues):
    """Pair Sanskrit cues with their Russian rendering by cue index -- the common
    case for parallel subtitle tracks of the SAME recording (same segmentation).
    Returns [{i, t_start, t_end, sa, ru, asr_conf}]. A length mismatch is a hard
    error (mis-segmented tracks must be fixed upstream, never silently truncated --
    a silent zip() would fabricate wrong Sa<->Ru pairs, the F1 lesson)."""
    if len(sa_cues) != len(ru_cues):
        sys.exit('cue count mismatch: %d Sanskrit vs %d Russian cues. Parallel '
                 'subtitle tracks must share segmentation; align them upstream or '
                 'pass --pairs with explicit pairing.'
                 % (len(sa_cues), len(ru_cues)))
    pairs = []
    for i, (s, r) in enumerate(zip(sa_cues, ru_cues)):
        pairs.append({'i': i, 't_start': s.get('t_start'), 't_end': s.get('t_end'),
                      'sa': s.get('text', ''), 'ru': r.get('text', ''),
                      'asr_conf': s.get('asr_conf')})
    return pairs


def load_pairs(path):
    """Already-paired input: JSONL of {sa, ru, t_start, t_end[, asr_conf, passage]}."""
    pairs = []
    with open(path, encoding='utf-8') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            pairs.append({'i': i, 't_start': r.get('t_start'), 't_end': r.get('t_end'),
                          'sa': (r.get('sa') or '').strip(),
                          'ru': (r.get('ru') or '').strip(),
                          'asr_conf': r.get('asr_conf'),
                          'passage': r.get('passage')})
    return pairs


# ------------------------------------------------------------------- emit
def to_corpus_rows(pairs, work, media=None):
    """Turn paired cues into corpus_builder jsonl rows (build_l0.py input schema),
    tagged oral with time anchors. Two rows per kept pair (seg=sa, seg=ru), sharing
    one globally-unique `group`. Applies the never-invent guards: a Sanskrit surface
    present AND a Cyrillic-bearing Russian -- an untranslated/garbled cue is dropped
    (reported), never emitted as a fabricated pair."""
    rows = []
    kept = dropped = 0
    for p in pairs:
        sa = (p.get('sa') or '').strip()
        ru = (p.get('ru') or '').strip()
        passage = p.get('passage') or str(p['i'] + 1)
        if len(sa) < MIN_CUE_CHARS or not build_tmx.has_cyr(ru):
            dropped += 1
            continue
        group = '%s:%s' % (work, passage)
        anchors = {'modality': MODALITY_ORAL,
                   't_start': p.get('t_start'), 't_end': p.get('t_end')}
        if media:
            anchors['source_media'] = media
        if p.get('asr_conf') is not None:
            anchors['asr_conf'] = p['asr_conf']
        sa_row = {'group': group, 'seg': 'sa', 'passage': passage,
                  'text': sa, **anchors}
        slp1 = _to_slp1(sa)
        if slp1:
            sa_row['slp1'] = slp1
        rows.append(sa_row)
        rows.append({'group': group, 'seg': 'ru', 'passage': passage,
                     'text': ru, 'lang': 'ru', **anchors})
        kept += 1
    return rows, kept, dropped


def convert(sa_path, ru_path, pairs_path, work, media, out_path, sample=None):
    if pairs_path:
        pairs = load_pairs(pairs_path)
        src_note = 'pairs=%s' % os.path.basename(pairs_path)
    else:
        if not (sa_path and ru_path):
            sys.exit('convert needs either --pairs, or both --sa and --ru')
        sa_cues = parse_cue_file(sa_path)
        ru_cues = parse_cue_file(ru_path)
        pairs = pair_cues(sa_cues, ru_cues)
        src_note = 'sa=%s ru=%s' % (os.path.basename(sa_path), os.path.basename(ru_path))
    if sample is not None:
        pairs = pairs[:sample]
    rows, kept, dropped = to_corpus_rows(pairs, work, media)
    if not rows:
        sys.exit('convert: 0 valid oral pairs (all cues failed the never-invent '
                 'guards). Check that the Russian track carries Cyrillic. (%s)' % src_note)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as out:
        for r in rows:
            out.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('ingest_oral: %s -> %s' % (src_note, out_path))
    print('  %d oral verse-pairs kept, %d dropped (guard), %d jsonl rows, work=%s%s'
          % (kept, dropped, len(rows), work, (' media=%s' % media) if media else ''))
    print('  next: copy to SamudraManthanam/web/corpus_builder/jsonl/%s.jsonl, then '
          '`python build_l0.py build --work %s`' % (work, work))
    return 0


def inspect(path):
    cues = parse_cue_file(path)
    if not cues:
        sys.exit('inspect: 0 cues parsed from %s' % path)
    dur = (cues[-1].get('t_end') or 0) - (cues[0].get('t_start') or 0)
    ncyr = sum(1 for c in cues if build_tmx.has_cyr(c['text']))
    print('inspect: %s' % path)
    print('  %d cues, span %.1fs .. %.1fs (%.1fs), %d carry Cyrillic'
          % (len(cues), cues[0].get('t_start') or 0, cues[-1].get('t_end') or 0,
             dur, ncyr))
    for c in cues[:3]:
        print('  [%.2f-%.2f] %s' % (c.get('t_start') or 0, c.get('t_end') or 0,
                                    c['text'][:60]))
    return 0


# ------------------------------------------------------------------- selftest
SA_VTT = """WEBVTT

NOTE auto-generated, cleaned

1
00:00:01.000 --> 00:00:04.500
dharmakṣetre kurukṣetre samavetā yuyutsavaḥ

2
00:00:04.500 --> 00:00:08.000
māmakāḥ pāṇḍavāś caiva kim akurvata sañjaya

3
00:00:08.000 --> 00:00:10.000
<c>uh</c> ...
"""

RU_VTT = """WEBVTT

1
00:00:01.000 --> 00:00:04.500
На поле дхармы, на поле Куру, сошлись жаждущие битвы

2
00:00:04.500 --> 00:00:08.000
мои и сыновья Панду — что они делали, о Санджая?

3
00:00:08.000 --> 00:00:10.000
…
"""


def selftest():
    import tempfile
    # parser: hours-optional timestamps, inline-tag stripping, blank-line splitting
    sa_cues = parse_subtitles(SA_VTT)
    ru_cues = parse_subtitles(RU_VTT)
    assert len(sa_cues) == 3, 'expected 3 sa cues, got %d' % len(sa_cues)
    assert len(ru_cues) == 3, 'expected 3 ru cues, got %d' % len(ru_cues)
    assert sa_cues[0]['t_start'] == 1.0 and sa_cues[0]['t_end'] == 4.5, sa_cues[0]
    assert sa_cues[2]['text'] == 'uh ...', 'inline <c> tag not stripped: %r' % sa_cues[2]['text']

    pairs = pair_cues(sa_cues, ru_cues)
    assert len(pairs) == 3
    rows, kept, dropped = to_corpus_rows(pairs, 'gita-lecture', media='gita01.mp3')
    # cue 3: sa='uh ...' (>=2 chars) but ru='…' has no Cyrillic -> dropped by guard
    assert kept == 2, 'guard should keep 2 real pairs, kept %d' % kept
    assert dropped == 1, 'guard should drop the untranslated cue, dropped %d' % dropped
    assert len(rows) == 4, 'two rows per kept pair, got %d' % len(rows)

    sa_row = rows[0]
    assert sa_row['seg'] == 'sa' and sa_row['modality'] == 'oral'
    assert sa_row['t_start'] == 1.0 and sa_row['t_end'] == 4.5, sa_row
    assert sa_row['source_media'] == 'gita01.mp3'
    assert sa_row['group'] == 'gita-lecture:1', sa_row['group']
    ru_row = rows[1]
    assert ru_row['seg'] == 'ru' and ru_row['lang'] == 'ru'
    assert build_tmx.has_cyr(ru_row['text']), 'ru row must carry Cyrillic'
    assert ru_row['group'] == sa_row['group'], 'sa/ru share the group'

    # mismatch is a hard error, never a silent zip-truncation
    try:
        pair_cues(sa_cues, ru_cues[:2])
    except SystemExit:
        pass
    else:
        raise AssertionError('cue-count mismatch must be a hard error')

    # round-trip through a file: convert -> valid corpus jsonl
    d = tempfile.mkdtemp(prefix='oral_selftest_')
    sap = os.path.join(d, 'l.sa.vtt'); rup = os.path.join(d, 'l.ru.vtt')
    out = os.path.join(d, 'gita-lecture.jsonl')
    open(sap, 'w', encoding='utf-8').write(SA_VTT)
    open(rup, 'w', encoding='utf-8').write(RU_VTT)
    convert(sap, rup, None, 'gita-lecture', 'gita01.mp3', out)
    got = [json.loads(l) for l in open(out, encoding='utf-8') if l.strip()]
    assert len(got) == 4 and all(r['modality'] == 'oral' for r in got), got
    print('ingest_oral selftest OK -- VTT parse, index pairing, guards, anchors, mismatch-guard')
    return 0


def main():
    ap = argparse.ArgumentParser(description='Oral transcript -> corpus jsonl (H215 Slice 4)')
    sub = ap.add_subparsers(dest='cmd', required=True)

    c = sub.add_parser('convert', help='paired subtitle tracks -> corpus_builder jsonl')
    c.add_argument('--sa', help='Sanskrit transcript (.vtt/.srt/.json)')
    c.add_argument('--ru', help='Russian rendering (.vtt/.srt/.json), same segmentation')
    c.add_argument('--pairs', help='pre-aligned JSONL of {sa,ru,t_start,t_end}')
    c.add_argument('--work', required=True, help='work name (globally-unique group prefix)')
    c.add_argument('--media', default=None, help='source audio/video filename (provenance)')
    c.add_argument('--out', required=True, help='output <work>.jsonl')
    c.add_argument('--sample', type=int, default=None)

    i = sub.add_parser('inspect', help='parse a cue file and show stats')
    i.add_argument('path')

    sub.add_parser('selftest', help='fixture -> convert, assert')

    a = ap.parse_args()
    if a.cmd == 'convert':
        return convert(a.sa, a.ru, a.pairs, a.work, a.media, a.out, sample=a.sample)
    if a.cmd == 'inspect':
        return inspect(a.path)
    if a.cmd == 'selftest':
        return selftest()
    return 1


if __name__ == '__main__':
    sys.exit(main())
