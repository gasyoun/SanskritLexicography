# siD sense-duplicate investigation — verdict: faithful, not over-production

**Date:** 2026-06-30 · **Trigger:** Slice D `siD` failed the `sense_dupes` gate (the lone
gate FAIL in Slice C+D). MG decision: *investigate the source before whitelist-vs-retranslate.*

## The flag

`audit_sense_dupes` reported four cross-part duplicates within homonym `h1` (PWG `2. siD`,
split into 4 citation-budget parts `si_d~~h1_00_pwg00..03`):

| tag | rendered by |
|---|---|
| `3` | pwg00 + pwg02 |
| `4` | pwg00 + pwg02 |
| `ppp-siddha-2` | pwg02 + pwg03 |
| `ppp-siddha-3` | pwg02 + pwg03 |

## Ground truth (raw source + rendered cards)

PWG `2. siD` re-uses sense numbers across **distinct structural levels** that the gate's flat
`(homonym, tag)` namespace cannot separate:

- **`3`** — pwg00 = the **verb** sense 3 (*giltig sein*, "to be valid"); pwg02 = sense 3 of the
  **derived feminine noun** (*`3) f. siddhā`*, an adjective/noun branch). Different lemma.
- **`4`** — pwg00 = the **verb** sense 4 (*zu Theil werden*); pwg02 = sense 4 of the **neuter
  noun** (*`4) n.` Zaubermacht*, "magic power"). Different lemma.
- **`ppp-siddha-2/3`** — pwg03 = the **base participle** `siddha` senses 2/3 (*zu Theil geworden*
  / *zurechtgemacht*); pwg02 = the **prefixed** participles `prasiddha` / `saṃsiddha` senses 2/3
  (*in Ordnung gekommen* / *bekannt*). Different participle stems, same number, same flat tag.

The rendered Russian/German for each pair is **distinct and faithful to the printed source** —
the model did not render the same sense twice. The collision is purely a **tag-namespace**
artifact: PWG genuinely repeats `3`, `4`, and the participle numbering across the verb, its
derived nouns, and its prefixed participles, and the `gen_opt_harness2` output tags them in one
flat space per homonym.

## Verdict

**Faithful, not over-production.** Re-translation would not help — the numbers genuinely repeat
in print, and a re-run would re-collide. The `batch_of` mechanism does not apply (these are
*different* senses sharing a number, not a citation-split of *one* sense).

## Resolution

A precise, committed exemption in
[`src/pilot/rootmap_overrides.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/rootmap_overrides.json) `_dupe_exempt`:

```json
"_dupe_exempt": { "si_d": { "h1": ["3", "4", "ppp-siddha-2", "ppp-siddha-3"] } }
```

`audit_sense_dupes.is_dupe_exempt()` skips exactly these four `(h1, tag)` collisions for `si_d`
(and only when all emitting sub-cards share that root — a cross-root collision is never exempt).
The `sense_dupes` gate now PASSes for siD. Covered by `window_selftest`
`test_sense_dupe_cross_level_exempt`.

## Root-cause note (future work, not blocking)

The deeper fix is structural-level namespacing in the gate (separate verb / derived-noun /
prefix-participle numbering spaces), parallel to the existing secondary-conjugation namespacing
(`section_of()`), but that needs reliable level markers in the rendered tags or the source
markup (`<lex>f.</lex>`, `<lex>n.</lex>`, prefix `{#pra#}` headers). Until then, `_dupe_exempt`
is the honest, auditable escape hatch for verified cases.
