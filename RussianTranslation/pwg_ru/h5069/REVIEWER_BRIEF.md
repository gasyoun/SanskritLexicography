# H5069 — independent reviewer brief (blind)

_Created: 20-09-2026 · Last updated: 20-09-2026_

You are an independent logic critic. You did not produce the material you are
about to judge and you have not seen anyone else's verdicts. Do not look for
them; do not read any file named `verdicts*`, `controls_key*` or
`*AUDIT*.md` in this directory. Judge from the primary evidence only.

## The material

`review_packet.jsonl` in this directory. One JSON object per line:

- `id` — opaque identifier.
- `source_string` — a span of the German source of the Petersburg Sanskrit
  Dictionary (Böhtlingk–Roth, PWG, 1855–1875). `{%…%}` wraps German prose
  glosses; `{#…#}` wraps Sanskrit that must survive untranslated; `<ls>`
  wraps a citation locus; `<ab>` wraps a lexicographic abbreviation.
- `target_string` — the Russian rendering of that same span.
- `gloss_pairs` — the `{%…%}` spans of each side, paired by index. A `null`
  on the Russian side means that side has fewer `{%…%}` spans; it does NOT by
  itself mean the meaning is missing — check `target_string` before concluding
  anything from a null.

## The single question

**Does the German source span license the meaning the Russian asserts?**

Not "is the Russian good Russian", not "is it fluent", not "is it the wording
I would choose". Only: is every assertion in the Russian covered by the
German, and does every qualification the German attaches survive?

## Verdict vocabulary — exactly one per item

- `faithful` — every Russian assertion is licensed; every German qualification
  survives.
- `addition` — the Russian asserts a meaning, referent, manner or specificity
  the German does not license.
- `omission` — the German attaches a qualification (hedge, restriction, domain
  label, grammatical scope) that the Russian silently drops, so the Russian
  reads more certain or more general than its source.
- `conflation` — two German spans or senses are merged into one Russian
  assertion, or a sense boundary moves.

## What this packet contains

The packet mixes published records with **at least one synthetic item carrying
a deliberately planted unsupported assertion**, and **at least one synthetic
item whose Russian was deliberately re-worded while staying fully licensed**.
Both are there to measure you. Convicting the re-worded one means you are
scoring surface divergence rather than source support; missing the planted one
means you cannot detect additions. You are not told which is which, or how
many of each.

## Required output

Write `reviewer_verdicts.json` in this directory:

```json
{
  "reviewer": "<who you are>",
  "model_version": "<your exact model id>",
  "verdicts": [
    {"id": "<id>", "verdict": "faithful|addition|omission|conflation",
     "confidence": "high|medium|low", "evidence": "<the German words and the
     Russian words that decide it, quoted>"}
  ],
  "challenged_control": "<name the item you believe is synthetic, say why, and
    say what would prove you wrong>",
  "limitations": "<what you could not check>"
}
```

Every one of the packet's items gets a row. Quote the deciding words — a
verdict with no quoted evidence is not usable.

_Гасунс_
