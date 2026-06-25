#!/usr/bin/env python
"""judge_disagreements.py — the production semantic gate: mine Opus-vs-Sonnet judge
disagreements into a human-adjudication queue, shown with FULL entry context.

Rationale (decided 2026-06-25): a synthetic "subtle semantic defect" has a contestable
ground truth — часть vs доля for a one-word gloss is undecidable in isolation, and decidable
cases are the rude ones both models already catch. So the semantic-power question is settled
on REAL data: run both judges on every card, and have the human adjudicate ONLY the cards
where they disagree, each shown with the complete German + Russian entry and both verdicts.
The disagreement set IS the test; the human is the ground truth.

A disagreement = the two judges differ on accept/reject (one BAD, one OK) OR their severities
differ by >= --sev-gap (a borderline crossing worth a look).

  python judge_disagreements.py opus.jsonl sonnet.jsonl                 # summary + queue
  python judge_disagreements.py opus.jsonl sonnet.jsonl --cards pairs.jsonl --out adjudicate.md
  python judge_disagreements.py opus.jsonl sonnet.jsonl --sev-gap 3

Verdict file = JSONL of {key1|tag, ok, severity, note?}. --cards = JSONL of {key1|tag,
body_de, body_ru} for the full-context queue (optional; without it the queue shows verdicts
+ notes only).
"""
import argparse, json, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BAD_SEV = 3


def load(path):
    txt = open(path, encoding='utf-8').read().strip()
    rows = json.loads(txt) if txt.startswith('[') else [json.loads(l) for l in txt.splitlines() if l.strip()]
    return {(r.get('tag') or r.get('key1')): r for r in rows}


def is_bad(v):
    return (not v.get('ok', True)) or int(v.get('severity', 0)) >= BAD_SEV


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('opus'); ap.add_argument('sonnet')
    ap.add_argument('--cards', help='JSONL with body_de/body_ru per id, for the full-context queue')
    ap.add_argument('--sev-gap', type=int, default=2, help='severity gap that also counts as a disagreement')
    ap.add_argument('--out', help='write the adjudication queue to this markdown file')
    a = ap.parse_args()

    O, S = load(a.opus), load(a.sonnet)
    cards = load(a.cards) if a.cards else {}
    ids = sorted(set(O) & set(S))
    disagree = []
    for i in ids:
        o, s = O[i], S[i]
        verdict_diff = is_bad(o) != is_bad(s)
        sev_diff = abs(int(o.get('severity', 0)) - int(s.get('severity', 0))) >= a.sev_gap
        if verdict_diff or sev_diff:
            disagree.append((i, o, s, verdict_diff))

    n = len(ids)
    hard = [d for d in disagree if d[3]]          # accept/reject conflicts (the ones that matter)
    print('scored both: %d | DISAGREEMENTS: %d (%.1f%%)  — of which accept/reject conflicts: %d (%.1f%%)'
          % (n, len(disagree), 100 * len(disagree) / max(n, 1), len(hard), 100 * len(hard) / max(n, 1)))
    for i, o, s, vd in disagree:
        tag = 'CONFLICT' if vd else 'sev-gap '
        print('  [%s] %-26s opus(ok=%s sev=%s)  sonnet(ok=%s sev=%s)'
              % (tag, i, o.get('ok'), o.get('severity'), s.get('ok'), s.get('severity')))

    if a.out:
        L = ['# Judge adjudication queue — Opus vs Sonnet disagreements', '',
             'You are the ground truth. For each card decide the last column: `opus` / `sonnet` /'
             ' `both-ok` / `both-wrong`, with a one-line reason. Only the cards where the two judges'
             ' disagreed are here (%d of %d).' % (len(disagree), n), '']
        for i, o, s, vd in disagree:
            L += ['## `%s`  %s' % (i, '— ACCEPT/REJECT CONFLICT' if vd else '— severity gap'),
                  '- **Opus:** ok=%s sev=%s — %s' % (o.get('ok'), o.get('severity'), o.get('note', '')),
                  '- **Sonnet:** ok=%s sev=%s — %s' % (s.get('ok'), s.get('severity'), s.get('note', '')),
                  '- **Your call:** ____ (opus / sonnet / both-ok / both-wrong) — reason: ']
            c = cards.get(i)
            if c:
                L += ['', '<details><summary>full entry</summary>', '', '**body_de**', '```', c.get('body_de', ''), '```',
                      '**body_ru**', '```', c.get('body_ru', ''), '```', '</details>']
            L.append('')
        open(a.out, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
        print('queue -> %s' % a.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
