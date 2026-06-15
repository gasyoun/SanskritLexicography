# pwg_ru pilot — end-to-end run (2026-06-15)

A 6-card pilot that runs the **full De→Ru pipeline** on real PWG entries with
**no external key and no Claude API** — only the Max subscription via Claude
Code. It proves that stages P0 (mask) → P2 (harvest) → P3 (translate) → P4
(judge) → restore produce publishable Russian dictionary cards.

## Method

6 headwords from the `a-` section (one record each), via the committed,
API-free tooling:

1. **P0 mask** — [src/pwg_mask.py](src/pwg_mask.py) turns each PWG record into a
   masked German skeleton (`{Tn}` placeholders for Sanskrit/refs/abbrev).
2. **P2 harvest** — [src/corpus_gate.py](src/corpus_gate.py) attaches the
   attested Russian senses (5 dicts + KOW reference + corpus).
3. **P3 translate** — **Claude Code workflow, Sonnet 4.6 on Max** translates the
   masked German (keep `{Tn}` verbatim; translate `{%…%}` German glosses keeping
   the wrapper).
4. **P4 judge** — **Opus 4.8 on Max** judges each (placeholders intact? German
   `{%…%}` translated? no German left? terminology sound?).
5. **Restore** — `{Tn}` placeholders deterministically reinserted; round-trip
   verified per card.

## Result

| Headword (IAST) | German gloss | → Russian | Judge |
|---|---|---|---|
| aṃśaka | Theil; Erbe; Verwandter | часть; наследник; родственник | sev 1 ✓ |
| aṃśala | Schulter; stark, kräftig | плечо; сильный, крепкий | sev 1 ✓ |
| aṃśasavarṇa | das Reduciren von Brüchen auf einen gemeinschaftlichen Nenner | приведение дробей к общему знаменателю | sev 1 ✓ |
| aṃśāvataraṇa | die Herabkunft der Theile | нисхождение частей | sev 1 ✓ |
| aṃśupaṭṭa | eine besondere Art Zeug | особый вид ткани | sev 2 ✓ |
| aṃśumatī | der Wasserstrom in den Lüften | поток воды в небесах | sev 1 ✓ |

**6/6 publishable** (five severity-1, one severity-2), **6/6 with placeholders
intact**, and every Sanskrit `{#…#}`, source ref `<ls>`, abbreviation `<ab>`,
`<lex>` and `<div>` restored byte-exact.

## What the pilot confirmed

- **The masker holds in production.** German `{%…%}` glosses translate with the
  wrapper kept (`{%Theil%}`→`{%часть%}`); the rest of the entry is untouched.
- **Latin handled without a rule.** On `aṃśumatī` the masker had kept the Latin
  binomial `{%Hedysarum gangeticum%}` inline (it is not German); Sonnet left it
  untranslated on its own and Opus confirmed it — the German/Latin edge resolves
  even when the deterministic masker defaults to German.
- **Harvest corroborates translation.** The fresh Russian agrees with the
  attested reuse senses (e.g. `aṃśala` плечо = Schulter; `aṃśasavarṇa` matches
  the KOW math idiom) — evidence the additive-senses model is coherent.
- **Safety works.** The masker's one lossy record (the giant `a` entry) is
  flagged by the per-card round-trip assertion, not silently mistranslated.

## What this does and does not need

- **Needs nothing external.** P0/P2/P3/P4 all run now: deterministic Python for
  mask/harvest/restore; Claude Code workflows on Max for translate/judge.
- **Still gated on a key:** P1, the DeepSeek corpus word-alignment lexicon — the
  reuse *multiplier* that raises coverage beyond the dictionaries. The core
  dictionary pipeline does not depend on it.
- **Scale-up:** the same translate/judge workflow, looped/scheduled over batches
  ("Sonnet nonstop"), is the production run. See
  [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md).
