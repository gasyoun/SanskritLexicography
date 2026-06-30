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

  EN-specific semantic (what replaces the RU checks; SOFT QA signals):
    DE-RESIDUE untranslated German left in the english gloss prose (umlaut/eszett or an
               unambiguous German token: und, der, eig., überh., übertr., ...)
    RU-RESIDUE Cyrillic leaked into the english field (wrong-language bleed)
    CIRCULAR   the english gloss is just the headword repeated
    MW-DIVERGE none of the MW gloss's content words appear in the card's english
               (soft cross-check against Monier-Williams, the gold MG chose)

Report-only by default (exit 0). `--strict` exits non-zero if any HARD gate
(LS/SAN/AB/MISSING-EN/DUP) fires; the soft semantic flags never fail the gate.

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
DEFAULT_MW_TM = os.path.join(SRC, 'mw_en_tm.json')

LS = re.compile(r'<ls\b')
SAN = re.compile(r'\{#.*?#\}', re.S)
AB = re.compile(r'<(?:ab|lex|lang)\b')
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
    r'|werden|wird|sein|eig|überh|übertr|näml|ungef|gleichs|urspr)\b', re.I)

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
    has_gloss = '{%' in g or bool(prose(g).strip())
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

    ep = prose(e)
    if CYR.search(ep):
        soft.append('RU-RESIDUE')
    de_hits = set(m.lower() for m in DE_WORDS.findall(ep))
    # Umlaut/eszett never occurs in IAST, but DOES occur in scholar names (Graßmann,
    # Böhtlingk) that legitimately survive. Genuine German residue (eig., überh., übertr.)
    # is lowercase, so only count an umlaut inside a non-capitalized token.
    for tok in re.findall(r'\S*[äöüÄÖÜß]\S*', ep):
        if not tok[:1].isupper():
            de_hits.add(tok.lower().strip('.,;:()'))
    if de_hits:
        soft.append('DE-RESIDUE(%s)' % ','.join(sorted(de_hits))[:40])
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
            # Within-card identical-gloss check (soft): skip structural headers and trivial
            # prose — preverb headers ("With ...") legitimately repeat. The canonical
            # cross-card tag dedup is delegated to audit_sense_dupes.py below.
            headerlike = any(hk in tag for hk in HEADERLIKE)
            if norm and not headerlike and len(words) >= 3:
                if norm in seen:
                    soft.append('SAME-GLOSS(=%s)' % seen[norm])
                else:
                    seen[norm] = tag
            for fl in hard + soft:
                flags.append((loc, fl))
        if do_mw and tm is not None:
            mw = mw_lookup(tm, h)
            if mw:
                mw_words = set(content_words(mw))
                if mw_words and not (mw_words & card_en_words):
                    flags.append(('%s/r%d' % (key, ri), 'MW-DIVERGE'))
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


HARD = ('MISSING-EN', 'LS-LOSS', 'SAN-LOSS', 'AB-LOSS', 'SENSE-DUPE')


def is_hard(flag):
    return any(flag.startswith(h) for h in HARD)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('wf_output', nargs='+',
                    help='one or more wf_output.en.<root>.json files (globs allowed)')
    ap.add_argument('--strict', action='store_true',
                    help='exit non-zero if any HARD gate (LS/SAN/AB/MISSING-EN/DUP) fires')
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
        if sd['returncode']:
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

    if args.report:
        rep = {'totals': totals, 'flag_counts': flag_counts,
               'hard_keys': sorted(hard_keys), 'files': per_file}
        with open(args.report, 'w', encoding='utf-8') as f:
            json.dump(rep, f, ensure_ascii=False, indent=1)
        print('report json  : %s' % args.report)

    sys.exit(1 if (args.strict and hard_total) else 0)


if __name__ == '__main__':
    main()
