#!/usr/bin/env python
"""renou_portrait.py — turn the Renou signals into editor-facing output.

Two editorial uses of the tags:

1. `portrait(entry)` — a compact, human-readable Renou label for a headword, for
   display in the dictionary entry: the era span, the first attestation, and a
   confidence note from `renou_provenance` (a V supported only by `bhs` is flagged
   register-only; an all-era span is flagged low-information — see below). Runs on a
   canonical `{code}.renou.jsonl`.

   Low-information flag: a tag spanning every Renou state (`ca`, `idam`, `akāra` =
   I–V) is corpus-accurate but says nothing diachronic — era-neutral high-frequency
   words attested everywhere. The inter-signal audit (renou_audit.py) showed this is
   the residual the min-support fix correctly does NOT prune, because it is not an
   error — it is a *display* concern. `portrait` sets `renou_low_info: True` so a UI
   can de-emphasise / collapse the badge instead of showing a meaningless five-era span.

2. `order_senses_oldest_first(card)` — reorder a structured card's senses so the
   earliest-attested meaning comes first (uses the per-sense `renou_oldest` +
   `renou_oldest_sense` that annotate_renou writes). Ready for the structured
   per-sense store; a no-op on cards without senses.

  python renou_portrait.py label mw.renou.jsonl [--out OUT]   # add renou_label to each entry
  python renou_portrait.py demo mw.renou.jsonl agni buddha akṣobhya
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import renou
NAME = {'I': 'ведийское', 'II': 'паниниевское', 'III': 'эпическое',
        'IV': 'классическое', 'V': 'буддийско-джайнское'}
EN = {'I': 'Vedic', 'II': 'Pāṇinian', 'III': 'Epic', 'IV': 'Classical', 'V': 'Buddhist/Jaina'}
_ORDER = {s: i for i, s in enumerate(renou.STATES)}
# a span covering this many states is era-neutral → low-information for display
# (default = all five; tighten to 4 to also flag near-universal words).
LOW_INFO_MIN_STATES = len(renou.STATES)
# Register (subsection) display names. The bhāṣya/épig registers are the editorially
# interesting ones; an entry in very many registers is register-uninformative.
NAME_REG = {
    'rgveda': 'ригведа', 'atharva': 'атхарваведа', 'yajus': 'яджус',
    'brahmana': 'брахманы', 'upanisad': 'упанишады', 'sutra': 'сутры',
    'vyakarana': 'грамматика', 'epig': 'эпиграфика',
    'epic': 'эпос', 'purana': 'пураны', 'tantra': 'тантры', 'smrti': 'смрити',
    'karika': 'карики', 'bhasya': 'комментарий', 'katha': 'повеств. проза',
    'natya': 'драма', 'kavya': 'кавья',
    'bauddha': 'буддийское', 'jaina': 'джайнское', 'hors_inde': 'вне Индии',
}
REG_LOW_INFO_MIN = 10  # carrying ≥half the lattice = register-uninformative


def portrait(e):
    """-> {renou_label, renou_first, renou_note, renou_low_info} or None when untagged."""
    states = e.get('renou_enriched') or []
    if not states:
        return None
    prov = e.get('renou_provenance') or {}
    first = e.get('renou_dcs_oldest') or e.get('renou_ls_oldest') or ''
    notes = []
    # weak-V flag: V attested only via the BHS register membership (no ls/dcs/wl)
    if 'V' in states and set(prov.get('V', [])) <= {'bhs'}:
        notes.append('V: только регистр (BHS)')
    # low-information flag: an all-era span discriminates nothing (era-neutral word)
    low_info = len(states) >= LOW_INFO_MIN_STATES
    if low_info:
        notes.append('малоинформативно: во всех эпохах')
    label = ' · '.join(NAME[s] for s in states)
    # register sub-label (orthogonal axis). A bhāṣya tag is the editorially salient one.
    regs = e.get('renou_register') or []
    reg_low_info = len(regs) >= REG_LOW_INFO_MIN
    if regs and not reg_low_info and 'bhasya' in regs:
        notes.append('регистр: комментарий (бхашья)')
    out = {
        'renou_label': label,
        'renou_first': NAME.get(first, ''),
        'renou_note': '; '.join(notes),
        'renou_low_info': low_info,
    }
    if regs:
        out['renou_register_label'] = ' · '.join(NAME_REG.get(r, r) for r in regs)
        out['renou_register_low_info'] = reg_low_info
    return out


def order_senses_oldest_first(card):
    """Reorder records' senses by earliest attestation. Senses with a dated
    `renou_oldest` lead (by state order = rough chronology), undated keep order.
    Mutates and returns the card; safe on cards lacking senses."""
    for rec in card.get('records', []):
        senses = rec.get('senses')
        if not senses:
            continue
        rec['senses'] = sorted(
            senses,
            key=lambda s: (_ORDER.get(s.get('renou_oldest', ''), 99),
                           senses.index(s)))
    return card


def cmd_label(path, out):
    n = labelled = 0
    sink = open(out + '.tmp', 'w', encoding='utf-8', newline='')
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        o = json.loads(line)
        p = portrait(o)
        if p:
            o.update(p); labelled += 1
        sink.write(json.dumps(o, ensure_ascii=False) + '\n')
        n += 1
    sink.close()
    os.replace(out + '.tmp', out)
    print('%d entries · %d labelled → %s' % (n, labelled, os.path.basename(out)))


def cmd_demo(path, words):
    want = set(words)
    for line in open(path, encoding='utf-8'):
        o = json.loads(line)
        if o.get('iast') in want:
            p = portrait(o)
            print('%-14s %s%s' % (o['iast'], o.get('renou_enriched'),
                  '  [малоинформативно]' if p and p.get('renou_low_info') else ''))
            print('   label: %s' % (p['renou_label'] if p else '—'))
            print('   первое свидетельство: %s%s' % (p['renou_first'] or '—',
                  ('  · ' + p['renou_note']) if p and p['renou_note'] else '') if p else '—')
            print('   provenance: %s' % o.get('renou_provenance'))
            if p and p.get('renou_register_label'):
                print('   регистр: %s%s' % (p['renou_register_label'],
                      '  [малоинформативно]' if p.get('renou_register_low_info') else ''))
                print('   register provenance: %s' % o.get('renou_register_provenance'))
            want.discard(o['iast'])
            if not want:
                break


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__); return
    cmd, path = args[0], args[1]
    rest = args[2:]
    if cmd == 'label':
        out = path
        if '--out' in rest:
            out = rest[rest.index('--out') + 1]
        cmd_label(path, out)
    elif cmd == 'demo':
        cmd_demo(path, rest)
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
