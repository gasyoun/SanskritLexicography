# G6 MQM gold starter — decisions applied (H1796)

_Created: 28-07-2026 · Last updated: 28-07-2026_

Audit record per the [`/decisions-apply`](https://github.com/gasyoun/claude-config/blob/main/commands/decisions-apply.md)
runbook for sheet `g6-mqm-gold-starter-2026-07-25`, bound to
[`review/locks/g6-mqm-gold-starter-2026-07-25.lock.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/locks/g6-mqm-gold-starter-2026-07-25.lock.json)
(20 cards drawn by
[`src/build_g6_mqm_gold_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_g6_mqm_gold_sheet.py)
from the 320-row scaffold
[`gold/gold_set.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/gold_set.jsonl)).
Voted by MG 28-07-2026; applied the same day by Opus 5 1M (`claude-opus-5[1m]`),
reviewer id `MG`. Binding verified before anything was written —
`content_hash sha256:e69ca4782356…` equals the lock's, 20 export ids ≡ 20 lock ids,
no drift.

The raw export
(`review/g6-mqm-gold-starter-2026-07-25_decisions.json`) and the adjudicated
sibling (`review/g6-mqm-gold-starter-2026-07-25-adjudicated_decisions.json`) are
personal voting artifacts and stay gitignored; the committed artifacts are the
lock, this record, and the label files below.

## Verdict counts

| stage | approve | reject | defer | total |
|---|---:|---:|---:|---:|
| MG's raw export | 14 | 6 | 0 | 20 |
| after adjudication (28-07-2026) | 16 | 3 | 1 | 20 |

Route: `validate_decisions.py` → `apply_decisions.py --gate G6 --reviewer MG` →
[`gold/decisions_g6-mqm-gold-starter-2026-07-25.csv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/decisions_g6-mqm-gold-starter-2026-07-25.csv)
→ `gold_ingest.py` →
[`gold/decisions_g6-mqm-gold-starter-2026-07-25.labels.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/decisions_g6-mqm-gold-starter-2026-07-25.labels.jsonl).
The explicit out path keeps the 320-row hard gate with the full set, per
`apply_decisions.py`'s G6 contract.

## Why an adjudication round was needed at all

The G6 vote contract is: `reject` ⇒ the **correct label must be the first word of
the note**. Five of the six rejects were free prose, so
`apply_decisions.py` aborted the whole file (it is deliberately all-or-nothing —
partial application is worse than none):

| id | sa → ru | LLM label | note began with | outcome |
|---|---|---|---|---|
| 2 | kṛtāñjali → «сложив руки» | correct | `partial,` | ✅ convertible as cast |
| 105 | kāpālike → «череп» | wrong-sense | `kāpālika` | ❌ ruled below |
| 118 | aruṇāmśub → «Аруна» | partial | `aruṇāmśub` | ❌ ruled below |
| 122 | na → «словно» | correct | `na` | ❌ ruled below |
| 201 | dhvanisparśa → «звуки и прикосновения» | correct | `звуки` | ❌ ruled below |
| 221 | prāyaṇa → «смерти» | lemma-variant | `Почему` | ❌ ruled below |

MG ruled each of the five in chat on 28-07-2026. No label was inferred by the
agent; each row below is MG's own call.

| id | ruling | recorded as |
|---|---|---|
| 105 | «kāpālika и есть череп» — the LLM's `wrong-sense` is wrong | reject → human label `correct` |
| 118 | no typology label can be given without more context | **defer** → `needs_adjudication=true`, `llm_label` `partial` retained |
| 122 | LLM label stands | approve (see the objection below) |
| 201 | LLM label stands | approve |
| 221 | «Почему lemma-variant, а не correct» — the LLM's `lemma-variant` is wrong | reject → human label `correct` |

### id 122 — the reject that the card itself caused

`na` → «словно» (work `08_rigveda`, translation) was rejected with «na это всегда
нет, никогда не словно». In Rigvedic usage `na` is a regular **particle of
comparison** («словно, как») alongside the negation — Grassmann s.v. `na` 2,
Macdonell §180 (`śyeno na` «словно сокол»). Once that was surfaced, MG left the
LLM's `correct` in force, and stated the operative rule:

> «не было оговорено, что это Ригведа, а тем более приведено все то, что тобой
> сейчас написано. Это все надо давать ДО, а не ПОСЛЕ»

That is a requirement on the **card**, not on the reviewer, and it is what
[FINDINGS §499](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
records. Four further cards carry the same complaint in their notes —
id 3 («не говоришь от какого корня и что корень означает согласно Whitney … не
приводишь контексты, а у нас их десятки, если не сотни»), id 6 («Недостаточно
данных для однозначного ответа»), id 92 («не видя контекста, а он у тебя есть,
но отсутствует у меня — допустим»), id 1 («почему мы работаем не с основами, а
формами падежей?»).

## What the labels say

| measure | value |
|---|---|
| rows ingested | 20 |
| LLM label confirmed by MG | 16 |
| LLM label overturned | 3 (ids 2, 105, 221) |
| left for adjudication | 1 (id 118) |
| **LLM label accuracy, resolved rows** | **16/19 = 84.2 %, Wilson 95 % [62.4 %, 94.5 %]** |
| same counting id 118 as a miss | 16/20 = 80.0 %, Wilson 95 % [58.4 %, 91.9 %] |

Label distribution, LLM as shown vs MG as recorded:

| label | LLM | human |
|---|---:|---:|
| correct | 12 | 13 |
| lemma-variant | 4 | 3 |
| proper-name | 2 | 2 |
| partial | 1 | 2 |
| wrong-sense | 1 | 0 |
| hallucinated | 0 | 0 |

> **This is a starter packet, not a precision figure of record.** n=19 gives a
> ±16-point interval, `hallucinated` was never exercised, and `wrong-sense` was
> exercised once and overturned. Nothing downstream should quote 84.2 % as the
> pwg_ru label accuracy; the number that will carry that weight is the n=400
> store cut (H1665, gate G6b).

## Follow-ups opened in the same pass

1. **Evidence panel before the vote** ([H1801](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1801-Opus_SanskritLexicography_g6-gold-card-evidence-panel_28.07.26.md))
   — the G6 card must carry the dictionary sense, the root, and corpus contexts,
   since the project already holds all three. Blocks the n=400 sheet.
2. **Reject-label picker in the emitter** ([H1802](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1802-Sonnet_csl-pyutil_review-sheet-reject-label-picker_28.07.26.md))
   — `csl_pyutil.render_review_sheet`
   must offer the six typology labels as a required control on reject instead of
   relying on a note-prefix convention. 5/6 non-compliance at n=6 would be ~250
   unusable rejects at n=400.
3. **[H1665](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1665-Fable_SanskritLexicography_pwg-store-gold-cut-execute-r1-r5_26.07.26.md)
   gated on both** — its hard gate 1 (R5, "g6 starter applied") is now satisfied,
   but generating 400 cards on the current card design would reproduce this
   failure at 20× the cost.

## Leftovers

- The sheet HTML `review/g6_mqm_starter_sheet.html` was removed after application
  per the `/decisions-apply` Phase-4 rule (a voted sheet next to live ones invites
  re-voting); it is reproducible from the generator, and the lock is committed.
- `g5-live-queue-batch1v3-2026-07-26` remains unvoted — it was sequenced *after*
  G6 and is the next open sheet (H1655).

_Dr. Mārcis Gasūns_
