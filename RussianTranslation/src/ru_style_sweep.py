#!/usr/bin/env python
r"""ru_style_sweep.py -- H1305 mechanical RU style sweep: no-ё, terse editorial metalanguage.

Applies four ratified, deterministic rules (H178 DA-vote 19-07-2026, register rows
N7/N12/N4-terseness -- see RU_STYLE_MECHANICAL.md for the full ruling text + the
false-positive measurement that cleared R2/R3 for a BROAD (unrestricted) sweep):

  R1  no letter ё anywhere in RU output -- write е everywhere; the ONLY exception is the
      standalone word «всё»/«Всё» (kept to disambiguate from «все»/«Все»). A hyphenated
      compound like «всё-таки» is NOT the exception (it defaults to «все-таки», like
      every other ё-word) -- the whitelist regex explicitly excludes anything immediately
      followed/preceded by a letter or hyphen.
  R2  «вместо» -> «вм.» (editorial metalanguage: variant/replacement readings). Measured
      0/60 false positives on a random sample of the store's 291 occurrences (all are
      editorial "read X instead of Y" apparatus, none are narrative prose) -- applied
      UNRESTRICTED per the handoff's <2% threshold.
  R3  «в значении» -> «в знач.» (editorial metalanguage: sense specification). Measured
      0/24 false positives (100% of the store's occurrences hand-classified) -- applied
      unrestricted.
  R4  `ed. Bomb.` -> «Бомбейская ред.», but ONLY in free PROSE outside any <ls>...</ls>
      span. Measured split: 221 standalone <ls>ed. Bomb.</ls> + 61 embedded inside a
      longer citation (e.g. <ls>R. ed. Bomb. 3,69,4</ls>) = 282 in-<ls> occurrences that
      MUST stay verbatim Latin (src/pwg_sources.py.source_key()/resolve() key the citation
      off this exact Latin text against pwgbib.txt -- rewriting it to Cyrillic breaks
      source resolution), vs. 1 genuine free-prose occurrence outside any <ls> tag. Only
      that population is swept here; the in-<ls> population is a render-time display
      concern (counted + handed off in RU_STYLE_MECHANICAL.md, not fixed at the store
      level).

Reuse (not reinvented -- pattern mirrors the H1302 precedent):
  - store mode / backup / dry-run-by-default / atomic write: fix_german_connectives.py
    --store.
  - canonical store resolution: store_path.canonical_store (worktree-safe -- H805/w06).
  - --wf window-gate mode (FLAGGED_JSON, audit_window.py wiring): stage2_pregate.py --wf /
    audit_translation.py --wf (reads the SAME .merged.md rendered output audit_window
    already consumes for the other RU gates).

  python src/ru_style_sweep.py                 # dry-run store sweep (default), per-rule counts
  python src/ru_style_sweep.py --apply          # apply to the canonical store (backs up first)
  python src/ru_style_sweep.py --selftest       # fixture assertions
  python src/ru_style_sweep.py --wf wf.json     # window audit gate: FLAGGED_JSON (audit_window.py)
"""
import json
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))     # .../src
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from store_path import canonical_store  # noqa: E402

# ---------------------------------------------------------------------------
# R1 -- no-ё, with the «всё»/«Всё» standalone-token whitelist.
# ---------------------------------------------------------------------------
YO_CHAR = re.compile('[ёЁ]')
# Standalone «всё»/«Всё» ONLY: not immediately preceded/followed by a Cyrillic letter or a
# hyphen, so a hyphenated compound («всё-таки») or a longer word never qualifies -- those
# default to е like every other ё-word (the ruling's stated edge-case behavior).
WHITELIST_VSE = re.compile(r'(?<![а-яёА-ЯЁ\-])[Вв]сё(?![а-яёА-ЯЁ\-])')


def apply_no_yo(text):
    """Replace every ё/Ё with е/Е, except inside a whitelisted standalone «всё»/«Всё»."""
    if not text or 'ё' not in text.lower():
        return text, 0
    protected = [(m.start(), m.end()) for m in WHITELIST_VSE.finditer(text)]

    def is_protected(pos):
        return any(s <= pos < e for s, e in protected)

    out = list(text)
    n = 0
    for m in YO_CHAR.finditer(text):
        pos = m.start()
        if is_protected(pos):
            continue
        out[pos] = 'Е' if m.group(0) == 'Ё' else 'е'
        n += 1
    return ''.join(out), n


# ---------------------------------------------------------------------------
# R2 -- «вместо» -> «вм.» (unrestricted; see docstring for the FP measurement).
# ---------------------------------------------------------------------------
VMESTO_CAP = re.compile(r'\bВместо\b')
VMESTO_LOW = re.compile(r'\bвместо\b')


def apply_terse_vmesto(text):
    if not text or 'место' not in text.lower():
        return text, 0
    text, c1 = VMESTO_CAP.subn('Вм.', text)
    text, c2 = VMESTO_LOW.subn('вм.', text)
    return text, c1 + c2


# ---------------------------------------------------------------------------
# R3 -- «в значении» -> «в знач.» (unrestricted; see docstring for the FP measurement).
# ---------------------------------------------------------------------------
VZNACH_CAP = re.compile(r'\bВ\s+значении\b')
VZNACH_LOW = re.compile(r'\bв\s+значении\b')


def apply_terse_vznach(text):
    if not text or 'значени' not in text.lower():
        return text, 0
    text, c1 = VZNACH_CAP.subn('В знач.', text)
    text, c2 = VZNACH_LOW.subn('в знач.', text)
    return text, c1 + c2


# ---------------------------------------------------------------------------
# R4 -- `ed. Bomb.` -> «Бомбейская ред.», PROSE ONLY (outside any <ls>...</ls> span).
# ---------------------------------------------------------------------------
LS_SPAN = re.compile(r'<ls\b[^>]*>.*?</ls>', re.S)
BOMB = re.compile(r'ed\.\s*Bomb\.')


def apply_bomb_prose_only(text):
    if not text or 'Bomb' not in text:
        return text, 0
    out, n, last = [], 0, 0
    for m in LS_SPAN.finditer(text):
        seg = text[last:m.start()]
        seg, c = BOMB.subn('Бомбейская ред.', seg)
        n += c
        out.append(seg)
        out.append(m.group(0))         # <ls>...</ls> span itself: untouched, verbatim
        last = m.end()
    tail = text[last:]
    tail, c = BOMB.subn('Бомбейская ред.', tail)
    n += c
    out.append(tail)
    return ''.join(out), n


# ---------------------------------------------------------------------------
# Combined sweep + read-only violation scan (the latter is what the audit_window.py
# `ru_style` gate and the store-mode "0 residual violations" check both reuse).
# ---------------------------------------------------------------------------
RULE_ORDER = (
    ('R4_bomb', apply_bomb_prose_only),
    ('R2_vmesto', apply_terse_vmesto),
    ('R3_vznach', apply_terse_vznach),
    ('R1_yo', apply_no_yo),
)


def sweep_text(text):
    """Apply R1-R4 in sequence; return (new_text, {rule_id: count})."""
    counts = {}
    for rule_id, fn in RULE_ORDER:
        text, c = fn(text)
        counts[rule_id] = c
    return text, counts


def scan_violations(text):
    """Read-only: which rule tags would fire on `text`? Used by the audit_window.py
    `ru_style` gate (FLAGGED_JSON on any hit) and by the store-mode auditor (0 residual
    violations after --apply). Never mutates the input."""
    if not text:
        return []
    _, counts = sweep_text(text)
    return [rule_id for rule_id, c in counts.items() if c]


# ---------------------------------------------------------------------------
# Store mode.
# ---------------------------------------------------------------------------
SRC = HERE
SAMPLES_PER_RULE = 6


def _iter_store(store):
    with open(store, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def run_store(apply_=False):
    default_local = os.path.join(SRC, 'pwg_ru_translated.jsonl')
    store = canonical_store(default_local)
    print('resolved store  : %s' % store)
    if not os.path.exists(store):
        sys.exit('STORE ABSENT: %s' % store)
    rows = list(_iter_store(store))
    totals = {rid: 0 for rid, _ in RULE_ORDER}
    samples = {rid: [] for rid, _ in RULE_ORDER}
    touched_rows = 0
    for r in rows:
        ru = r.get('ru') or ''
        if not ru:
            continue
        new, counts = sweep_text(ru)
        row_total = sum(counts.values())
        if row_total:
            touched_rows += 1
            key = '%s|%s|%s' % (r.get('key1'), r.get('subcard'), r.get('sense_tag'))
            for rid, c in counts.items():
                totals[rid] += c
                if c and len(samples[rid]) < SAMPLES_PER_RULE:
                    samples[rid].append((key, ru, new))
            if apply_:
                r['ru'] = new
    grand_total = sum(totals.values())
    print('mode            : %s' % ('APPLY' if apply_ else 'DRY RUN'))
    print('rows            : %d' % len(rows))
    print('rows touched    : %d' % touched_rows)
    print('substitutions   :')
    for rid, _ in RULE_ORDER:
        print('  %-12s %d' % (rid, totals[rid]))
    print('  %-12s %d' % ('TOTAL', grand_total))
    print()
    for rid, _ in RULE_ORDER:
        if samples[rid]:
            print('--- %s samples (%d shown) ---' % (rid, len(samples[rid])))
            for key, before, after in samples[rid]:
                print('  [%s]' % key)
                print('    before: ...%s...' % before[:160].replace('\n', ' '))
                print('    after : ...%s...' % after[:160].replace('\n', ' '))
    if apply_ and grand_total:
        bak = store + '.h1305.bak'
        if not os.path.exists(bak):
            shutil.copyfile(store, bak)
            print('\nbackup          : %s' % bak)
        tmp = store + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        os.replace(tmp, store)
        print('wrote           : %s' % store)
    elif not apply_:
        print('\n(dry run -- pass --apply to write)')
    return grand_total


# ---------------------------------------------------------------------------
# --wf window-gate mode (audit_window.py wiring): reads the SAME .merged.md rendered
# output the other RU gates (audit_translation.py --wf, stage2_pregate.py --wf) consume.
# ---------------------------------------------------------------------------
def cmd_wf(wf_path):
    pilot = os.path.join(SRC, 'pilot')
    if pilot not in sys.path:
        sys.path.insert(0, pilot)
    import audit_translation as at  # noqa: E402 -- stems_from_wf / IN / OUT shared with the other RU gates

    stems = at.stems_from_wf(wf_path)
    flagged = []
    rows = []
    for stem in stems:
        outp = os.path.join(at.OUT, stem + '.merged.md')
        if not os.path.exists(outp):
            rows.append((stem, 'skip', ['NO-OUTPUT']))
            continue
        text = open(outp, encoding='utf-8').read()
        viols = scan_violations(text)
        if viols:
            flagged.append(stem)
            rows.append((stem, 'FAIL', viols))
        else:
            rows.append((stem, 'ok', []))
    print('=== ru_style mechanical gate (%d units) ===' % len(stems))
    print('%-28s %-5s %s' % ('unit', 'st', 'flags'))
    for stem, st, marks in rows:
        if st != 'ok':
            print('%-28s %-5s %s' % (stem[:28], st, ' '.join(marks)))
    print('\n%s: %d/%d clean, %d hard-flagged'
          % ('PASS' if not flagged else 'FAIL', len(stems) - len(flagged), len(stems), len(flagged)))
    print('FLAGGED_JSON: %s' % json.dumps(flagged))
    return 0 if not flagged else 1


# ---------------------------------------------------------------------------
# Selftest.
# ---------------------------------------------------------------------------
def selftest():
    # R1: yo -> e, «отвоёвывать» -> «отвоевывать»
    t, n = apply_no_yo('отвоёвывать')
    assert t == 'отвоевывать' and n == 1, (t, n)
    # R1: standalone «всё» is preserved
    t, n = apply_no_yo('всё хорошо')
    assert t == 'всё хорошо' and n == 0, (t, n)
    t, n = apply_no_yo('Всё пропало')
    assert t == 'Всё пропало' and n == 0, (t, n)
    # R1 edge case: hyphenated «всё-таки» is NOT whitelisted -> defaults to е
    t, n = apply_no_yo('всё-таки пришёл')
    assert t == 'все-таки пришел' and n == 2, (t, n)
    # R1: a word containing yo elsewhere in the same string is still fixed even when
    # «всё» sits right next to it (whitelist span is exact, does not leak).
    t, n = apply_no_yo('она всё ещё ждёт')
    assert t == 'она всё еще ждет' and n == 2, (t, n)

    # R2: metalanguage «вместо» -> «вм.», case preserved
    t, n = apply_terse_vmesto('ошибочно вместо {#nyaveSayat#}')
    assert t == 'ошибочно вм. {#nyaveSayat#}' and n == 1, (t, n)
    t, n = apply_terse_vmesto('Вместо простого acc.')
    assert t == 'Вм. простого acc.' and n == 1, (t, n)

    # R3: «в значении» -> «в знач.»
    t, n = apply_terse_vznach('С samudA в значении samudAnaya')
    assert t == 'С samudA в знач. samudAnaya' and n == 1, (t, n)

    # R4: standalone <ls>ed. Bomb.</ls> is NEVER touched (source-resolution safety)
    t, n = apply_bomb_prose_only('(так <ls>ed. Bomb.</ls>)')
    assert t == '(так <ls>ed. Bomb.</ls>)' and n == 0, (t, n)
    # R4: embedded citation form is NEVER touched either
    t, n = apply_bomb_prose_only('<ls>R. ed. Bomb. 3,69,4</ls>')
    assert t == '<ls>R. ed. Bomb. 3,69,4</ls>' and n == 0, (t, n)
    # R4: genuine free prose OUTSIDE any <ls> IS translated
    t, n = apply_bomb_prose_only('<ls>Mālatīm.</ls> (ed. Bomb.) 304,1.')
    assert t == '<ls>Mālatīm.</ls> (Бомбейская ред.) 304,1.' and n == 1, (t, n)

    # combined sweep_text applies all four independently, in one pass
    combined, counts = sweep_text(
        'ошибочно вместо {#X#}, как читает <ls>ed. Bomb.</ls>. В значении «всё пропало»')
    assert combined == (
        'ошибочно вм. {#X#}, как читает <ls>ed. Bomb.</ls>. В знач. «всё пропало»'), combined
    assert counts['R2_vmesto'] == 1 and counts['R3_vznach'] == 1 and counts['R4_bomb'] == 0, counts

    # scan_violations mirrors sweep_text exactly (read-only, same detectors)
    assert scan_violations('обычный русский текст без нарушений') == []
    assert 'R1_yo' in scan_violations('пришёл поздно')
    assert 'R2_vmesto' in scan_violations('читать вместо этого')
    assert 'R4_bomb' not in scan_violations('<ls>ed. Bomb.</ls>')  # in-<ls> is not a violation

    # idempotence: re-running the sweep on already-swept text changes nothing
    twice, counts2 = sweep_text(combined)
    assert twice == combined and sum(counts2.values()) == 0, (twice, counts2)

    print('ru_style_sweep selftest: PASS')
    return True


def main():
    argv = sys.argv[1:]
    if '--selftest' in argv:
        selftest()
        return
    if '--wf' in argv:
        i = argv.index('--wf')
        if i + 1 >= len(argv):
            sys.exit('usage: python src/ru_style_sweep.py --wf <wf_output.json>')
        sys.exit(cmd_wf(argv[i + 1]))
    apply_ = '--apply' in argv
    run_store(apply_=apply_)


if __name__ == '__main__':
    main()
