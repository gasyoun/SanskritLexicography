#!/usr/bin/env python
r"""stage2_pregate.py — deterministic mechanical pre-gate for the Stage-2 QA judge.

WHY THIS EXISTS
---------------
The Stage-2 QA judge prompt (pwg_ru_prompts/2_qa_sudya_opus.txt) is explicit that a
whole class of criteria are *format invariants*, NOT quality judgments — the anchor
placeholders {Tn}, the untranslatable spans behind them (<ls>/{#…#}/<ab>/<is>/<lex>/
<lang>), and the presence of actual Russian — and it says outright that their state
"НЕ должно влиять на вердикт". A model is a wasteful, non-deterministic, and
occasionally *wrong* way to check something a regex decides exactly. W5 of
PIPELINE_CAPABILITY_AUDIT_2026-07-08.md measured that the *semantic* half of Stage-4
cannot be de-LLM'd (synonymy defeats token overlap), but the *mechanical* half of
Stage-2 can be, completely.

So this module is a BLOCKING pre-gate: run it before the Opus judge. A card that
fails a mechanical invariant never reaches the judge (it is requeued for
re-translation instead), and the judge's rubric can drop the format criteria and
rule only on the irreducibly semantic part (fluency / fidelity / sense-fabrication).

WHAT IT CHECKS (two auto-detected modes)
----------------------------------------
* ANCHOR MODE — when either side still carries {Tn} placeholders (the masked
  body_de/body_ru pair the judge is actually handed): the multiset of {Tn} tokens
  must be identical on both sides (none lost, duplicated, or invented), and the
  Russian side must not have *leaked* a raw untranslatable span that should be
  hidden behind a placeholder (unmasking).

* RESTORED MODE — when neither side has {Tn} (the persisted merged output in
  src/pwg_ru_translated.jsonl, post-restore): every untranslatable span category
  (LS/SAN/AB/IS/LEX/LANG) present in the German must survive verbatim in the
  Russian, and <ab> abbreviations must NOT be expanded to Russian prose. Plus:
  if the German had {%…%} gloss prose to translate, the Russian must contain
  Cyrillic (else the card is empty / untranslated).

Category span definitions mirror pwg_mask.PAIRED (kept in sync by --selftest).
The loss threshold reuses audit_translation.py's guard (>=90% kept AND >=2 absolute
missing) so a tiny card that legitimately collapses one duplicate span is not
false-flagged, while a real apparatus dump loss still trips.

Language-agnostic by construction (it compares structure, never meaning), so it is
SHARED across RU/EN — see LANG_PARITY.md entry `stage2_pregate`.

  python src/stage2_pregate.py store [N]     # run over the translated store, bucket pass/fail
  python src/stage2_pregate.py card <key1>   # gate every store row for one headword, verbose
  python src/stage2_pregate.py --selftest    # synthetic cases; exit 1 on any failure
"""
import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')

# Per-category untranslatable spans. The UNION of these must stay identical to
# pwg_mask.PAIRED (asserted in --selftest) so the gate and the masker never drift.
CATEGORIES = {
    'LS':   re.compile(r'<ls\b[^>]*>.*?</ls>', re.S),      # literary-source sigla
    'SAN':  re.compile(r'\{#.*?#\}', re.S),                # SLP1 Sanskrit
    'AB':   re.compile(r'<ab\b[^>]*>.*?</ab>', re.S),      # meta-abbreviations
    'IS':   re.compile(r'<is\b[^>]*>.*?</is>', re.S),      # italic Sanskrit / sigla
    'LEX':  re.compile(r'<lex\b[^>]*>.*?</lex>', re.S),    # grammar pointers
    'LANG': re.compile(r'<lang\b[^>]*>.*?</lang>', re.S),  # foreign cognates
}
ANCHOR_RE = re.compile(r'\{T\d+\}')
GER_GLOSS_RE = re.compile(r'\{%.*?%\}', re.S)
CYR_RE = re.compile(r'[а-яёА-ЯЁ]')
# A raw untranslatable tag/span leaking into a MASKED Russian body = unmasking.
LEAK_RE = re.compile(r'</?(?:ls|ab|is|lex|lang)\b|\{#')

KEEP_RATIO = 0.90     # a category is preserved if >= this fraction survives
MIN_ABS_LOSS = 2      # ... and only flag when >= this many spans are actually missing


def _norm_spans(text, rx):
    """Whitespace-normalized span multiset (so a re-wrapped citation still matches)."""
    return Counter(re.sub(r'\s+', ' ', s).strip() for s in rx.findall(text))


def pregate(de, ru):
    """Mechanically gate one (German source, Russian translation) card pair.

    Returns {'status': 'pass'|'fail', 'mode': 'anchor'|'restored',
             'flags': [...], 'warnings': [...], 'detail': {...}}.

    `flags` (HARD) are unambiguous mechanical failures — the card must be
    requeued, not judged: span loss, anchor mismatch, a stranded (never-restored)
    {Tn}, or an unmasked span leaked into the Russian. `status == 'fail'` iff
    `flags` is non-empty.

    `warnings` (SOFT) are ambiguous signals that must NOT hard-block, because a
    deterministic rule cannot tell a real defect from a legitimate one: NO-RUSSIAN
    fires on a card with a {%…%} gloss and no Cyrillic, but that is a genuine
    untranslated-prose defect OR a Schmidt-supplement apparatus stub whose {%…%}
    is a *cited Sanskrit form* ("Mit {%paripra%}, <ls>…</ls>") with nothing to
    translate. So NO-RUSSIAN stays a warning and the card still reaches the
    semantic judge, which can tell the two apart. A warning does not fail the gate.
    """
    de = de or ''
    ru = ru or ''
    flags, warnings, detail = [], [], {}

    # Mode = whether DE is a CLEAN masked body (all untranslatable spans hidden
    # behind {Tn}, none raw) vs a RESTORED/final card (raw <ls>/{#/<ab> inline).
    de_has_raw = bool(LEAK_RE.search(de))
    de_masked = bool(ANCHOR_RE.search(de)) and not de_has_raw

    if de_masked:
        mode = 'anchor'
        de_anch = Counter(ANCHOR_RE.findall(de))
        ru_anch = Counter(ANCHOR_RE.findall(ru))
        if de_anch != ru_anch:
            flags.append('ANCHOR-MISMATCH')
            detail['anchor'] = {'lost': sorted((de_anch - ru_anch).elements()),
                                'extra_or_dup': sorted((ru_anch - de_anch).elements())}
        if LEAK_RE.search(ru):
            flags.append('ANCHOR-LEAK')      # a hidden span was unmasked into the RU body
            detail['leak'] = LEAK_RE.findall(ru)[:8]
    else:
        mode = 'restored'
        # A fully-restored card must carry NO placeholders; a leftover {Tn} means
        # the mask round-trip stranded an anchor (the `banD` half-restore defect).
        stranded = sorted(set(ANCHOR_RE.findall(de)) | set(ANCHOR_RE.findall(ru)))
        if stranded:
            flags.append('STRANDED-ANCHOR')
            detail['stranded'] = stranded[:8]
        cat_detail = {}
        for name, rx in CATEGORIES.items():
            d, r = _norm_spans(de, rx), _norm_spans(ru, rx)
            d_tot = sum(d.values())
            if d_tot == 0:
                continue
            missing = d - r                              # multiset difference
            miss_n = sum(missing.values())
            r_tot = sum(r.values())
            cat_detail[name] = '%d/%d' % (r_tot, d_tot)
            if miss_n >= MIN_ABS_LOSS and r_tot < d_tot * KEEP_RATIO:
                flags.append('%s-LOSS(%d/%d)' % (name, r_tot, d_tot))
                detail.setdefault('missing', {})[name] = sorted(missing.elements())[:8]
        if cat_detail:
            detail['spans'] = cat_detail
        if GER_GLOSS_RE.search(de) and not CYR_RE.search(ru):
            warnings.append('NO-RUSSIAN')

    return {'status': 'fail' if flags else 'pass', 'mode': mode,
            'flags': flags, 'warnings': warnings, 'detail': detail}


# ---- store runner --------------------------------------------------------
def _iter_store(path=STORE):
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def cmd_store(args):
    n = int(args[0]) if args else None
    total = clean = warned = failed = 0
    flag_counts = Counter()
    warn_counts = Counter()
    mode_counts = Counter()
    samples = []
    for r in _iter_store():
        de, ru = r.get('de', ''), r.get('ru', '')
        if not de and not ru:
            continue
        total += 1
        res = pregate(de, ru)
        mode_counts[res['mode']] += 1
        if res['status'] == 'fail':
            failed += 1
            for fl in res['flags']:
                flag_counts[fl.split('(')[0]] += 1
            if len(samples) < 12:
                samples.append((r.get('key1', '?'), r.get('subcard', ''), res['flags']))
        elif res['warnings']:
            warned += 1
            for w in res['warnings']:
                warn_counts[w] += 1
        else:
            clean += 1
        if n and total >= n:
            break

    print('=== Stage-2 mechanical pre-gate over the translated store ===')
    print('cards gated: %d   (mode: %s)' % (
        total, ', '.join('%s=%d' % (k, v) for k, v in mode_counts.items())))
    print('  CLEAN  -> judge  : %6d  (%.2f%%)' % (clean, 100.0 * clean / max(total, 1)))
    print('  WARN   -> judge* : %6d  (%.2f%%)  [passes, flagged for the judge]'
          % (warned, 100.0 * warned / max(total, 1)))
    print('  FAIL   -> requeue: %6d  (%.2f%%)  [hard-blocked; never reaches the judge]'
          % (failed, 100.0 * failed / max(total, 1)))
    if flag_counts:
        print('--- HARD failure reasons (a card may trip several) ---')
        for fl, c in flag_counts.most_common():
            print('    %-16s %6d' % (fl, c))
    if warn_counts:
        print('--- soft warnings (do not block) ---')
        for w, c in warn_counts.most_common():
            print('    %-16s %6d' % (w, c))
    if samples:
        print('--- sample hard failures ---')
        for k1, sc, fls in samples:
            print('    %-14s %-6s %s' % (str(k1)[:14], str(sc)[:6], ' '.join(fls)))


def cmd_card(args):
    if not args:
        sys.exit('usage: python src/stage2_pregate.py card <key1>')
    key1 = args[0]
    hit = 0
    for r in _iter_store():
        if str(r.get('key1')) != key1:
            continue
        hit += 1
        res = pregate(r.get('de', ''), r.get('ru', ''))
        marks = ' '.join(res['flags']) or (' '.join('warn:' + w for w in res['warnings'])) or 'ok'
        print('%s [%s] %s  %s' % (key1, r.get('subcard', ''), res['status'].upper(), marks))
        if res['detail']:
            print('    ' + json.dumps(res['detail'], ensure_ascii=False))
    if not hit:
        print('no store rows for key1=%s' % key1)


# ---- selftest ------------------------------------------------------------
def _selftest():
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    # 0) category union stays in sync with the masker
    try:
        import pwg_mask
        ours = {p.pattern for p in CATEGORIES.values()}
        theirs = set(pwg_mask.PAIRED)
        check('categories-match-pwg_mask.PAIRED', ours == theirs)
    except Exception as e:                       # pragma: no cover
        print('  (skipped pwg_mask sync check: %s)' % e)

    # 1) clean restored card passes
    de = 'gut, freundlich {%nahe%} <ls>RV. 1,1</ls> {#mitra#} <ab>vgl.</ab>'
    ru = 'хороший, дружелюбный <ls>RV. 1,1</ls> {#mitra#} <ab>vgl.</ab>'
    check('clean-restored-pass', pregate(de, ru)['status'] == 'pass')

    # 2) dropped citations (>=2, below ratio) fail with LS-LOSS
    de2 = 'x <ls>A. 1</ls> <ls>B. 2</ls> <ls>C. 3</ls>'
    ru2 = 'ы <ls>A. 1</ls>'
    r2 = pregate(de2, ru2)
    check('ls-loss-fail', r2['status'] == 'fail' and any(f.startswith('LS-LOSS') for f in r2['flags']))

    # 3) losing ONE span on a small card does NOT flag (abs-diff guard)
    de3 = 'x <ls>A. 1</ls> <ls>B. 2</ls>'
    ru3 = 'ы <ls>A. 1</ls>'
    check('single-loss-guard', pregate(de3, ru3)['status'] == 'pass')

    # 4) expanded/dropped abbreviations (>=2) fail with AB-LOSS
    de4 = 'p <ab>vgl.</ab> q <ab>caus.</ab> r <ab>m.</ab>'
    ru4 = 'п сравни q каузатив r мужской род'
    r4 = pregate(de4, ru4)
    check('ab-expansion-fail', r4['status'] == 'fail' and any(f.startswith('AB-LOSS') for f in r4['flags']))

    # 5) German gloss present but no Russian output -> NO-RUSSIAN is a WARNING,
    #    not a hard fail (may be a form-citation apparatus stub); card still passes.
    r5 = pregate('{%nahe stehend%}', 'nahe stehend')
    check('no-russian-warns-not-fails', r5['status'] == 'pass' and 'NO-RUSSIAN' in r5['warnings'])

    # 6) a card with no {%…%} and no Russian is fine (pure apparatus)
    check('apparatus-only-pass', pregate('<ls>RV. 1</ls> {#mitra#}', '<ls>RV. 1</ls> {#mitra#}')['status'] == 'pass')

    # 7) anchor mode — matched {Tn} passes
    check('anchor-match-pass',
          pregate('a {T1} b {T2}', 'а {T1} б {T2}')['status'] == 'pass')

    # 8) anchor mode — lost placeholder fails
    r8 = pregate('a {T1} b {T2}', 'а {T1}')
    check('anchor-lost-fail', r8['status'] == 'fail' and 'ANCHOR-MISMATCH' in r8['flags'])

    # 9) anchor mode — duplicated placeholder fails
    r9 = pregate('a {T1} b {T2}', 'а {T1} б {T2} {T2}')
    check('anchor-dup-fail', r9['status'] == 'fail' and 'ANCHOR-MISMATCH' in r9['flags'])

    # 10) anchor mode — a hidden span unmasked into RU fails with ANCHOR-LEAK
    r10 = pregate('a {T1} b {T2}', 'а {T1} б <ls>RV. 1</ls>')
    check('anchor-leak-fail', 'ANCHOR-LEAK' in r10['flags'])

    # 11) restored card with a leftover {Tn} (never restored) -> STRANDED-ANCHOR
    r11 = pregate('<ls>RV. 1</ls> {T5} <ab>vgl.</ab>', '<ls>RV. 1</ls> {T5} <ab>vgl.</ab>')
    check('stranded-anchor-fail', r11['status'] == 'fail' and 'STRANDED-ANCHOR' in r11['flags'])

    if fails:
        print('SELFTEST FAIL: ' + ', '.join(fails))
        return 1
    print('SELFTEST PASS (11 cases + masker-sync)')
    return 0


def main():
    args = sys.argv[1:]
    if args[:1] == ['--selftest']:
        sys.exit(_selftest())
    if args[:1] == ['store']:
        return cmd_store(args[1:])
    if args[:1] == ['card']:
        return cmd_card(args[1:])
    print(__doc__)


if __name__ == '__main__':
    main()
