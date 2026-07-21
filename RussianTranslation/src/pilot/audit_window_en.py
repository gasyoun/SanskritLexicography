#!/usr/bin/env python
r"""audit_window_en.py — deterministic, report-only audit gate for the EN translation track.

The RU gate (`audit_window.py` + `audit_translation.py` + `prompt_rule_audit.py`) is wired
around `.merged.md`/`.raw.txt` files and Russian-specific semantic checks
(`NO-RUSSIAN`, Russian register), so the PWG->EN pilot ran with `--no-audit`. This is the
EN sibling: it works DIRECTLY on `wf_output.en.<root>.json` (per-sense `german` source +
`english` target) and keeps the language-agnostic gates while swapping the RU semantic
checks for EN ones.

Gates (per non-null card -> record -> sense, comparing `german` vs `english`):

  language-agnostic (the same invariants the RU gate enforces):
    LS-LOSS    every <ls>..</ls> citation must survive (english keeps >=90%, abs drop >=2)
    SAN-LOSS   every distinct {#..#} Sanskrit span must survive (>=85%, abs drop >=2)
    AB-LOSS    <ab>/<lex>/<lang> sigla must survive (abs drop >=2)   [sigla-kept]
    MISSING-EN english empty while german had gloss prose to translate [coverage]
    DUP        two senses in one record share identical english       [sense-duplicate]

  shared mechanical pre-gate (H405, stage2_pregate.py — the same gate wired into the
  RU audit_window.py; here it supplies only the invariants this auditor's own checks
  above don't, to avoid double-reporting):
    IS-LOSS         <is>..</is> italic-Sanskrit spans dropped (the AB regex omits <is>)
    STRANDED-ANCHOR a {Tn} placeholder left unrestored in the final text
    ANCHOR-LEAK/-MISMATCH  masked-pair anchor damage (defensive; restored EN rarely hits)

  markup-loss (pwg_ru/DharmaMitra crosswalk, FU1_PLAN.md; SOFT, never blocks --strict):
    MARKUP-LOSS {%..%} gloss-wrapper / <div> pairs dropped while the prose survives —
                the dominant EN residual per FABLE_JUDGE_S7 (~47% of rows); tracked here so
                it stops riding on judge samples, per that memo's planned gate.

  EN-specific semantic (what replaces the RU checks; SOFT QA signals):
    DE-RESIDUE untranslated German left in the english gloss prose (umlaut/eszett or an
               unambiguous German token: und, der, eig., überh., übertr., ...)
    RU-RESIDUE Cyrillic leaked into the english field (wrong-language bleed)
    CIRCULAR   the english gloss is just the headword repeated
    MW-DIVERGE none of the MW gloss's content words appear in the card's english
               (soft cross-check against Monier-Williams, the gold MG chose)

  H1152 guard 3 (H1070 finding #3, "nothing was really translated here"; SOFT, coverage
  accounting only -- not a fidelity defect, markup/meaning stay intact):
    XREF-ONLY     the german carries no gloss prose, only a cross-reference apparatus
                  ("Vgl. {#foo#} fgg.", "s. {#bar#}") -- a faithful english can only
                  reproduce the same apparatus, so counting it as translated prose inflates
                  coverage stats
    NWS-DE-LOCKED German prose from the NWS layer is trapped INSIDE a {#..#} span (a
                  masking miss that made real German look like opaque Sanskrit) -- it never
                  reached the translator, so it survives as German in `english` by
                  construction, not as a translation failure

Report-only by default (exit 0). `--strict` exits non-zero if any HARD gate
(LS/SAN/AB/IS/STRANDED-ANCHOR/MISSING-EN/DUP) fires, if any card came back null (missing EN), or if the
sense-dupe subgate crashed (a crash is NOT a clean pass); the soft semantic flags never
fail the gate. Failure reasons are printed and written to `--report`.

  python src/pilot/audit_window_en.py wf_output.en.pat.json
  python src/pilot/audit_window_en.py wf_output.en.*.json --strict
  python src/pilot/audit_window_en.py wf_output.en.pat.json --no-mw   # skip MW cross-check
"""
import argparse
import contextlib
import glob
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))          # .../src/pilot
SRC = os.path.dirname(HERE)                                # .../src
OUT = os.path.join(HERE, 'output')
INPUT_DIR = os.path.join(HERE, 'input')                    # portrait sidecars (H920 source_senses)
DEFAULT_MW_TM = os.path.join(SRC, 'mw_en_tm.json')

if HERE not in sys.path:
    sys.path.insert(0, HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)
from foreign_literal_guards import FRENCH_CONTEXT_WORDS, AMBIGUOUS_DE_FR_WORDS
import stage2_pregate   # H405: the shared mechanical pre-gate (RU + EN)
from sense_count import portrait_source_senses, output_sense_count, sense_shortfall  # H920

# Flag TYPES the pre-gate contributes to the EN path that this auditor's own
# per-sense checks above do NOT already produce. LS/SAN/AB/LEX/LANG loss stay owned
# by audit_sense (same thresholds), so pulling only these avoids double-reporting:
#   IS-LOSS         <is>…</is> italic-Sanskrit spans dropped (EN's AB regex omits <is>)
#   STRANDED-ANCHOR a {Tn} placeholder left unrestored in the final text
#   ANCHOR-LEAK/-MISMATCH  masked-pair anchor damage (defensive; restored EN rarely hits)
_PREGATE_NEW = {'IS-LOSS', 'STRANDED-ANCHOR', 'ANCHOR-LEAK', 'ANCHOR-MISMATCH'}

LS = re.compile(r'<ls\b')
SAN = re.compile(r'\{#.*?#\}', re.S)
AB = re.compile(r'<(?:ab|lex|lang)\b')
GLOSS = re.compile(r'\{%.*?%\}', re.S)
DIVTAG = re.compile(r'<div\b')
CYR = re.compile(r'[Ѐ-ӿ]')
LS_SPAN = re.compile(r'<ls[^>]*>.*?</ls>', re.S)
TAG = re.compile(r'<[^>]+>')
WORD = re.compile(r"[A-Za-z]{3,}")

LS_KEEP, SAN_KEEP = 0.90, 0.85

# High-precision German residue markers. Umlaut/eszett never occur in IAST, so they are a
# clean signal; the word list excludes tokens that collide with English ("die", "in", "so").
DE_UML = re.compile(r'[äöüÄÖÜß]')
DE_WORDS = re.compile(
    r'\b(und|oder|der|des|dem|den|eine|einen|einem|einer|sich|nicht|durch|gegen'
    r'|werden|wird|sein|eig|überh|übertr|näml|ungef|gleichs|urspr'
    # H1302 German-only survivors (no English homograph -- source:
    # foreign_literal_guards.GERMAN_PROSE_RESIDUE_EN_SAFE; LANG_PARITY german_prose_residue_h1302)
    r'|dessen|mit|ohne|von|für|bei|beim|nach|unter|statt|zum|zur|zu|ziehen'
    r'|häufiger|könnte|später|vielleicht|wohl)\b', re.I)

# English stop-words to drop before the MW content-word cross-check.
STOP = frozenset('the a an of to and or in on at for with from by as is be are was were that '
                 'this it its his her their etc also one who which what not no any some such '
                 'into out up down off over under more most very so'.split())

# Structural sense tags (preverb / secondary-conjugation headers) that legitimately carry
# trivial repeated prose ("With ..."); the same SKIP set the RU sense-dupe gate uses.
HEADERLIKE = ('header', 'gramm-forms', 'grammar', 'paradigm')


def prose(text):
    """Strip markup down to the translatable gloss prose (no Sanskrit, no citations, no tags)."""
    text = LS_SPAN.sub(' ', text)        # drop <ls>..</ls> citation contents
    text = SAN.sub(' ', text)            # drop {#..#} Sanskrit spans
    text = TAG.sub(' ', text)            # drop remaining tags
    text = text.replace('{%', ' ').replace('%}', ' ')   # gloss wrappers
    return text


def content_words(text):
    return [w.lower() for w in WORD.findall(prose(text)) if w.lower() not in STOP]


# H1152 guard 3 (H1070 finding #3, 12/170 rows in the FU1 gold sample): two DETERMINISTIC
# "nothing was really translated here" shapes that coverage stats currently count as
# ordinary translated prose. Both are SOFT (report-only, never --strict-blocking) -- the
# markup/meaning is intact either way, so this is a coverage-accounting fix, not a fidelity
# defect. The cross-reference vocabulary is now the single source shared with the RU harness
# (gen_opt_harness2.degenerate_passthrough_card) via the dependency-free xref_vocab module,
# so it can no longer drift as two independent copies (H1425 W2).
from xref_vocab import DEGENERATE_XREF_WORDS as _XREF_WORDS  # noqa: E402
_SPAN = re.compile(r'\{#(.*?)#\}', re.S)


def xref_only(german):
    """A sense whose German carries no translatable gloss prose at all -- only a
    cross-reference apparatus ('Vgl. {#foo#} fgg.', 's. {#bar#}') -- so a faithful English
    rendering can only reproduce the same apparatus, never add real gloss content. A {%..%}
    gloss wrapper is the tell that real prose exists; its absence plus an all-cross-ref-word
    residue (after stripping <ls>/{#..#}/tags) means this row was never a translation target
    in the first place."""
    g = german or ''
    if GLOSS.search(g):                      # a {%..%} gloss wrapper -> real prose exists
        return False
    words = [w.lower().strip('.,;') for w in WORD.findall(prose(g))]
    return bool(words) and all(w in _XREF_WORDS for w in words)


def nws_de_locked(german):
    """German prose accidentally trapped INSIDE a {#..#} span (an NWS-layer masking miss):
    a {#..#} span is supposed to carry ONLY Sanskrit/IAST, so an umlaut/eszett or an
    unambiguous German function word inside one means that German text rode along as an
    opaque 'untranslatable' placeholder and NEVER REACHED THE TRANSLATOR -- it stays German
    in the final english field by construction, not by a translation failure."""
    for inner in _SPAN.findall(german or ''):
        if DE_UML.search(inner) or DE_WORDS.search(inner):
            return True
    return False


def find_results(o):
    if isinstance(o, dict):
        if isinstance(o.get('results'), list):
            return o['results']
        for v in o.values():
            r = find_results(v)
            if r is not None:
                return r
    if isinstance(o, list):
        for v in o:
            r = find_results(v)
            if r is not None:
                return r
    return None


def audit_sense(german, english):
    """Return (hard_flags, soft_flags) for one sense's german->english pair."""
    hard, soft = [], []
    g, e = german or '', english or ''
    # H1152 guard 3: flag the two "nothing was really translated here" shapes so a coverage
    # consumer can stop counting them as ordinary translated prose. SOFT — the card itself is
    # not defective (markup and meaning are intact either way).
    if xref_only(g):
        soft.append('XREF-ONLY')
    if nws_de_locked(g):
        soft.append('NWS-DE-LOCKED')
    # P7 (H1422): has_gloss used to fire on ANY non-empty prose residue, including a bare
    # cross-reference/abbreviation apparatus ('vgl. {#foo#} fgg.') that xref_only() already
    # recognizes as non-target (soft XREF-ONLY above) -- hard-failing MISSING-EN on a sense
    # that was never a translation target in the first place. Residual gap not attempted
    # here: xref_only's WORD regex requires 3+ letters, so a residue of ONLY 1-2 letter
    # tokens ('s.', 'u.') with no other prose still slips through as has_gloss=True.
    has_gloss = not xref_only(g) and ('{%' in g or bool(prose(g).strip()))
    if has_gloss and not e.strip():
        hard.append('MISSING-EN')
        return hard, soft

    sls, ols = len(LS.findall(g)), len(LS.findall(e))
    if sls > 0 and ols < sls * LS_KEEP and (sls - ols) >= 2:
        hard.append('LS-LOSS(%d/%d)' % (ols, sls))
    ssan, osan = len(set(SAN.findall(g))), len(set(SAN.findall(e)))
    if ssan > 0 and osan < ssan * SAN_KEEP and (ssan - osan) >= 2:
        hard.append('SAN-LOSS(%d/%d)' % (osan, ssan))
    sab, oab = len(AB.findall(g)), len(AB.findall(e))
    if sab > 0 and (sab - oab) >= 2:
        hard.append('AB-LOSS(%d/%d)' % (oab, sab))

    # P8 (H1422): the two marker classes were summed into one combined count before
    # comparing, so a dropped {%..%} gloss wrapper could be masked by an unrelated <div>
    # gained in the english (net count unchanged, e.g. source 2 gloss/0 div vs output
    # 0 gloss/2 div -- 2 == 2, no flag). Count and compare each class separately.
    sgl, ogl = len(GLOSS.findall(g)), len(GLOSS.findall(e))
    sdiv, odiv = len(DIVTAG.findall(g)), len(DIVTAG.findall(e))
    if (sgl > 0 and ogl < sgl) or (sdiv > 0 and odiv < sdiv):
        soft.append('MARKUP-LOSS(%d/%d)' % (ogl + odiv, sgl + sdiv))

    ep = prose(e)
    if CYR.search(ep):
        soft.append('RU-RESIDUE')
    de_hits = set(m.lower() for m in DE_WORDS.findall(ep))
    # "des" is both a German genitive/plural article ("des Todes") and a French
    # partitive/plural article ("des chevaux") -- the gen_fidelity_judge_en prompt
    # explicitly preserves French/Latin literals verbatim in the english field, so a
    # bare "des" hit with no other unambiguous German marker, alongside other French
    # vocabulary (FRENCH_WORDS), is a preserved French literal, not German residue.
    # Mirrors the RU "du"-vs-French collision fixed 2026-07-03 (prompt_rule_audit.py).
    if de_hits <= AMBIGUOUS_DE_FR_WORDS and FRENCH_CONTEXT_WORDS.search(ep):
        de_hits.clear()
    # Umlaut/eszett never occurs in IAST, but DOES occur in scholar names (Graßmann,
    # Böhtlingk) that legitimately survive. Genuine German residue (eig., überh., übertr.)
    # is lowercase, so only count an umlaut inside a non-capitalized token.
    for tok in re.findall(r'\S*[äöüÄÖÜß]\S*', ep):
        if not tok[:1].isupper():
            de_hits.add(tok.lower().strip('.,;:()'))
    if de_hits:
        soft.append('DE-RESIDUE(%s)' % ','.join(sorted(de_hits))[:40])

    # H405: fold in the mechanical invariants stage2_pregate.py owns that this
    # auditor doesn't — <is> preservation and stranded/leaked {Tn} anchors. Only the
    # NET-NEW flag types (see _PREGATE_NEW) are taken; LS/SAN/AB loss stay owned above.
    for fl in stage2_pregate.pregate(g, e)['flags']:
        if fl.split('(')[0] in _PREGATE_NEW:
            hard.append(fl)
    return hard, soft


def mw_lookup(tm, h):
    if not tm or not h:
        return None
    key = SAN.sub('', h).strip()           # h is already SLP1; drop any {#..#} wrapper
    return tm.get(key)


def audit_card(result, tm, do_mw):
    """Audit one wf result row. Returns dict: key, flags (list of (loc, flag)), null bool."""
    key = result.get('key')
    card = result.get('card')
    if not card:
        return {'key': key, 'null': True, 'flags': []}
    flags = []
    for ri, rec in enumerate(card.get('records') or []):
        h = rec.get('h') or card.get('iast') or ''
        senses = rec.get('senses') or []
        seen = {}
        card_en_words = set()
        for si, s in enumerate(senses):
            tag = str(s.get('tag') or si)
            loc = '%s/r%d/s%s' % (key, ri, tag)
            hard, soft = audit_sense(s.get('german'), s.get('english'))
            ep = prose(s.get('english') or '')
            words = content_words(s.get('english') or '')
            card_en_words.update(words)
            norm = re.sub(r'\s+', ' ', ep).strip().lower()
            if norm and norm == h.lower():
                soft.append('CIRCULAR')
            # Within-card identical-gloss check: skip structural headers — preverb headers
            # ("With ...") legitimately repeat. The canonical cross-card tag dedup is
            # delegated to audit_sense_dupes.py below.
            # DUP (HARD): two senses share the exact same english, regardless of length —
            # a real duplicate is a real duplicate whether it's one word or ten.
            # SAME-GLOSS (soft): kept as a lower-confidence variant gated on >=3 content
            # words, for callers that only want the historical soft signal.
            # C2: the DUP key is the normalized RAW english, NOT prose() — prose() strips {#..#}
            # Sanskrit and <ls> citations, so two senses distinguished ONLY by their referent
            # ("N. of a serpent-demon {#vAsuki#}" vs "…{#takzaka#}") collapsed to one string and
            # the second was wrongly HARD-DUP'd, failing --strict on faithful output. The gate's
            # own contract ("the EXACT same english") requires KEEPING the referent; CIRCULAR
            # above keeps prose() `norm` (a gloss that is only the transliterated headword IS
            # circular even with its {#..#} stripped).
            dup_key = re.sub(r'\s+', ' ', (s.get('english') or '')).strip().lower()
            headerlike = any(hk in tag for hk in HEADERLIKE)
            if dup_key and not headerlike:
                if dup_key in seen:
                    hard.append('DUP(=%s)' % seen[dup_key])
                    if len(words) >= 3:
                        soft.append('SAME-GLOSS(=%s)' % seen[dup_key])
                else:
                    seen[dup_key] = tag
            for fl in hard + soft:
                flags.append((loc, fl))
        if do_mw and tm is not None:
            mw = mw_lookup(tm, h)
            if mw:
                mw_words = set(content_words(mw))
                if mw_words and not (mw_words & card_en_words):
                    flags.append(('%s/r%d' % (key, ri), 'MW-DIVERGE'))
    # H920 SAN-LOSS (whole-dropped-sense) guard — SHARED with the RU auditor's sense_loss
    # gate via sense_count.py. The per-sense SAN-LOSS flag above measures gloss token-loss
    # WITHIN a surviving sense; this catches a whole numbered sense dropped from a no_pwg /
    # supplement source (portrait source_senses vs output card sense count). A card whose
    # portrait predates the H920 stamp is silently skipped (never a false positive).
    expected = portrait_source_senses(INPUT_DIR, key)
    dropped = sense_shortfall(card, expected) if expected is not None else 0
    if dropped > 0:
        flags.append((key, 'MISSING-SENSE(out %d<src %d)' % (output_sense_count(card), expected)))
    return {'key': key, 'null': False, 'flags': flags}


def load_sense_dupes():
    """Import the language-agnostic RU sense-dupe gate once (it keys on tags, not gloss
    language). In-process call avoids a Python-interpreter spawn per file — the per-spawn
    startup was the audit's dominant cost at scale."""
    if SRC not in sys.path:
        sys.path.insert(0, SRC)
    try:
        import audit_sense_dupes
        return audit_sense_dupes
    except Exception as e:                       # pragma: no cover - import guard
        print('(audit_sense_dupes import failed: %s)' % e, file=sys.stderr)
        return None


def run_sense_dupes(mod, path):
    """Call audit_sense_dupes.main() in-process for `path`, capturing its GATE line + rc."""
    if mod is None:
        return {'returncode': None, 'summary': '(audit_sense_dupes unavailable)'}
    saved_argv = sys.argv
    buf = io.StringIO()
    try:
        sys.argv = ['audit_sense_dupes', path]
        with contextlib.redirect_stdout(buf):
            rc = mod.main()
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else 1
    except Exception as e:                       # pragma: no cover - defensive
        return {'returncode': None, 'summary': '(sense-dupe error: %s)' % e}
    finally:
        sys.argv = saved_argv
    out = buf.getvalue()
    line = next((l for l in out.splitlines() if 'GATE' in l), out.strip())
    return {'returncode': rc, 'summary': line.strip()}


HARD = ('MISSING-EN', 'MISSING-SENSE', 'LS-LOSS', 'SAN-LOSS', 'AB-LOSS', 'IS-LOSS',
        'STRANDED-ANCHOR', 'ANCHOR-LEAK', 'ANCHOR-MISMATCH', 'SENSE-DUPE', 'DUP')


def is_hard(flag):
    return any(flag.startswith(h) for h in HARD)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('wf_output', nargs='+',
                    help='one or more wf_output.en.<root>.json files (globs allowed)')
    ap.add_argument('--strict', action='store_true',
                    help='exit non-zero on any HARD gate (LS/SAN/AB/IS/STRANDED-ANCHOR/MISSING-EN/DUP), '
                         'any null card, or a crashed sense-dupe subgate')
    ap.add_argument('--mw-tm', default=DEFAULT_MW_TM,
                    help='MW translation-memory JSON for the soft cross-check (default: src/mw_en_tm.json)')
    ap.add_argument('--no-mw', action='store_true', help='skip the MW divergence cross-check')
    ap.add_argument('--report', help='write the machine-readable JSON report to this path')
    args = ap.parse_args()

    paths = []
    for p in args.wf_output:
        paths.extend(sorted(glob.glob(p)) or [p])

    tm = None
    do_mw = not args.no_mw
    if do_mw:
        if os.path.exists(args.mw_tm):
            tm = json.load(open(args.mw_tm, encoding='utf-8'))
        else:
            print('(MW TM %s not found — skipping MW cross-check)' % os.path.relpath(args.mw_tm, SRC),
                  file=sys.stderr)
            do_mw = False

    sense_dupes_mod = load_sense_dupes()
    totals = {'files': 0, 'cards': 0, 'null': 0, 'senses': 0}
    flag_counts = {}
    per_file = []
    hard_keys = set()
    null_keys = []            # keys that came back with no card (missing EN translation)
    crashed_files = []        # files where the sense-dupe subgate could not run -> NOT clean
    for path in paths:
        if not os.path.exists(path):
            print('(skip: %s not found)' % path, file=sys.stderr)
            continue
        data = json.load(open(path, encoding='utf-8'))
        results = find_results(data) or []
        totals['files'] += 1
        file_flags = []
        for res in results:
            row = audit_card(res, tm, do_mw)
            if row['null']:
                totals['null'] += 1
                null_keys.append(row.get('key') or '?')
                continue
            totals['cards'] += 1
            for loc, fl in row['flags']:
                base = fl.split('(')[0]
                flag_counts[base] = flag_counts.get(base, 0) + 1
                file_flags.append({'loc': loc, 'flag': fl})
                if is_hard(fl):
                    hard_keys.add(row['key'])
            totals['senses'] += sum(len(r.get('senses') or [])
                                    for r in (res.get('card') or {}).get('records') or [])
        # Canonical cross-card sense-dupe gate — language-agnostic (keys on tags, not gloss
        # language), so the existing RU tool runs unchanged on the EN wf_output. Called
        # in-process (see run_sense_dupes) to avoid a subprocess spawn per file.
        sd = run_sense_dupes(sense_dupes_mod, path)
        if sd['returncode'] is None:
            # A crash / unavailable subgate is NOT a clean pass — record it so --strict fails
            # instead of a green light on an un-run gate (FL2: "crash != clean").
            crashed_files.append(os.path.basename(path))
        elif sd['returncode']:
            flag_counts['SENSE-DUPE'] = flag_counts.get('SENSE-DUPE', 0) + 1

        per_file.append({'file': os.path.basename(path), 'flags': file_flags, 'sense_dupe': sd})
        print('\n=== %s ===' % os.path.basename(path))
        if not file_flags:
            print('  clean (per-sense)')
        for ff in file_flags:
            print('  %-28s %s' % (ff['loc'], ff['flag']))
        print('  sense-dupe gate: %s' % sd['summary'])

    print('\n=== EN AUDIT SUMMARY ===')
    print('files        : %d' % totals['files'])
    print('cards (nn)   : %d   null: %d   senses: %d' % (totals['cards'], totals['null'], totals['senses']))
    if flag_counts:
        for base in sorted(flag_counts):
            tag = 'HARD' if is_hard(base) else 'soft'
            print('  %-12s %4d  [%s]' % (base, flag_counts[base], tag))
    else:
        print('  no flags')
    hard_total = sum(v for k, v in flag_counts.items() if is_hard(k))
    print('hard flags   : %d  (cards: %d)' % (hard_total, len(hard_keys)))
    if null_keys:
        print('null cards   : %d (missing EN — %s%s)' % (
            len(null_keys), ', '.join(null_keys[:8]), ', ...' if len(null_keys) > 8 else ''))
    if crashed_files:
        print('crashed gates: sense-dupe could not run on %s' % ', '.join(crashed_files))

    # --strict must fail on a HARD gate, a null card (missing translation), OR a crashed
    # subgate — each is a reason the window is not verified clean. Report the reasons.
    strict_reasons = []
    if hard_total:
        strict_reasons.append('%d hard flag(s)' % hard_total)
    if null_keys:
        strict_reasons.append('%d null card(s)' % len(null_keys))
    if crashed_files:
        strict_reasons.append('%d crashed sense-dupe gate(s)' % len(crashed_files))

    if args.report:
        os.makedirs(os.path.dirname(os.path.abspath(args.report)), exist_ok=True)
        rep = {'totals': totals, 'flag_counts': flag_counts,
               'hard_keys': sorted(hard_keys), 'null_keys': null_keys,
               'crashed_files': crashed_files, 'strict_reasons': strict_reasons,
               'files': per_file}
        with open(args.report, 'w', encoding='utf-8') as f:
            json.dump(rep, f, ensure_ascii=False, indent=1)
        print('report json  : %s' % args.report)

    if args.strict and strict_reasons:
        print('STRICT FAIL   : %s' % '; '.join(strict_reasons))
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
