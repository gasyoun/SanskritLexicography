# DECISIONS_PIPELINE_CAPABILITY_H335.md — pwg_ru evidence/government/genre schema rulings

_Created: 08-07-2026 · Last updated: 08-07-2026_

Records MG's rulings on the four `@DECIDE` forks parked in
[PIPELINE_CAPABILITY_AUDIT_2026-07-08.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_CAPABILITY_AUDIT_2026-07-08.md#forks-parked-for-mg-decide--with-recommendations)
(H335 W2/W3/W4), unblocking
[H337](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H337-Opus_RussianTranslation_pwg-ru-evidence-retrofit_08.07.26.md) ·
[H338](https://github.com/gasyoun/Uprava/blob/main/handoffs/H338-Sonnet_RussianTranslation_pwg-ru-government-backfill_08.07.26.md) ·
[H339](https://github.com/gasyoun/Uprava/blob/main/handoffs/H339-Sonnet_RussianTranslation_pwg-ru-sense-genres_08.07.26.md).
Eliciting session: Sonnet 5 (`claude-sonnet-5`), via `/decision-record`.
Entries are append-only — a later reversal is a new `D##` that cites and
supersedes the one it replaces, never an edit in place.

## D1 — Evidence schema shape (W2)

**Context.** `corpus_gate.build_card` assembles 7 evidence lanes
(INDEP/REF/SPECIALIST/SENSE/kosha-synonyms/botanical/corpus) per lemma, joined
on `form_key(slp1)`. None of the 11,261 store rows carry any evidence field
today. The fork was where this lives (in-store field vs a separate sidecar)
and how to record a lemma's absence from every source (per-sense "silent"
entries vs one lemma-level summary).

**Options considered.**
- In-store `evidence[]` field + one lemma-level `evidence_summary` entry for
  silence (recommended in the audit).
- A separate sidecar file, keyed by `key1`/subcard, joined at query time.
- In-store `evidence[]`, but with a `silent` row written per sense per
  missing source (7 lanes × 11,261 rows of negative entries).

**Ruling.** In-store field, with silence recorded once per lemma (not per
sense). Decider: MG. Dated 08-07-2026.

**Consequences.** `annotate_evidence.py` (H337) writes `evidence[]` directly
onto each store sense row, and a single `evidence_summary` entry per lemma
when a source is checked and finds nothing — never a `silent` row repeated
across every sense of that lemma. `annotation_report.py` reads the store
alone; no second file to join. Next action: build per the
[W2 spec](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_CAPABILITY_AUDIT_2026-07-08.md#spec--evidence-per-sense).

## D2 — Retrofit vs forward-only (W2/W3)

**Context.** Both the evidence join (W2) and the government extractor (W3)
are deterministic, offline, LLM-free joins against data already on disk. The
fork was whether to backfill the 11,261 already-translated rows now, or only
attach evidence/government to future translation windows.

**Options considered.**
- Retrofit all 11,261 rows now (recommended in the audit — pure offline
  compute, no re-translation, no Workflow spend).
- Forward-only: only new windows get evidence/government from now on.

**Ruling.** Retrofit all 11,261 rows now. Decider: MG. Dated 08-07-2026.

**Consequences.** H337's `annotate_evidence.py` and H338's
`annotate_government.py` both run as one-time backfills over the full store
before any new-window prompt-rule work lands, so every already-translated
sense becomes queryable (`annotation_report.py --by-source grin12 --relation
supports`, "verbs never governing gen.") without waiting on new production.

## D3 — Genre taxonomy (W4)

**Context.** Three genre vocabularies exist for the same underlying question
("what is this sense/lemma's textual genre?"): `ls_source_map.json`'s 25
curated, hierarchical, per-sense labels (citation-derived — "Kāvya — kathā");
DCS's genre buckets (frequency-weighted, corpus-attested, lemma-level, and
already crosswalked to Renou states I–V via
[`build_dcs_renou.GENRE_RENOU`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_dcs_renou.py#L40));
and DCS's own ~22 finer register codes underlying that bucket set. The audit
recommended keeping the two lanes separate (`genres` from citations,
`dcs_registers` from corpus frequency, never merged) because they answer
genuinely different questions. MG ruled instead for ONE merged taxonomy.

**Options considered.**
- Keep `ls_source_map`'s 25 labels canonical for per-sense `genres`; DCS stays
  in its own untranslated `dcs_registers` lane (audit's recommendation —
  rejected).
- Make DCS's genre buckets canonical instead (rejected — lemma-level, not
  per-sense, and carries the known silent join-key-loss bug at
  `build_dcs_freq_dims.py:133`).
- **Merge both into one taxonomy** (MG's ruling) — real design work with no
  existing code to reuse, so the merge shape is specified below rather than
  left to H339 to invent.

**Ruling.** Merge into a single taxonomy, designed here (not deferred to a
separate H339 design phase). Decider: MG. Dated 08-07-2026.

**Merge design.** A unified per-sense field carries BOTH the specific label
and its provenance, so the citation-derived and corpus-frequency-derived
signals stay distinguishable inside one field instead of silently conflated
(the exact risk the audit flagged):

```json
"genre": {
  "label": "Kāvya — kathā",        // the more specific label available
  "coarse": "kavya",                // one of: veda | epic | kavya | purana | sastra | kosha | buddhist | unknown
  "provenance": "ls_source_map"     // "ls_source_map" (per-sense citation) | "dcs_registers" (per-lemma corpus frequency)
}
```

**Precedence**: if the sense has a citation match in `ls_source_map`
(covers ~70% of `<ls>` occurrences), `label`/`coarse`/`provenance` come from
there — it is the more specific, per-sense signal. Only when a sense has NO
`ls_source_map` citation match does the lemma's `dcs_registers` corpus-vector
(if any) supply a fallback `coarse` bucket (`provenance: "dcs_registers"`,
`label` left null — the DCS lane doesn't have per-sense specificity to offer
as a `label`). A sense with neither gets `coarse: "unknown"`,
`provenance: null` — never silently defaulted to a bucket.

**Coarse-bucket crosswalk** (ls_source_map's 25 labels × DCS's buckets, both
sides collapsed onto one coarse vocabulary):

| coarse | ls_source_map labels | DCS bucket(s) (`GENRE_RENOU` keys) |
|---|---|---|
| `veda` | Veda — Saṃhitā, Veda — Brāhmaṇa, Veda — Sūtra, Veda — Vedāṅga | Vedic Saṃhitā, Brāhmaṇa, Upaniṣad |
| `epic` | Epic — Gītā, Epic — Itihāsa (MBh), Epic — Itihāsa (Rām), Epic — appendix (MBh) | Epic |
| `kavya` | Kāvya — Mahākāvya (Kālidāsa), Kāvya — drama (Kālidāsa), Kāvya — gnomic (mixed), Kāvya — historical, Kāvya — kathā, Kāvya — lyric, Kāvya — lyric (Jayadeva) | Kāvya, Nāṭya, Narrative Prose |
| `purana` | Purāṇa | Purāṇa |
| `sastra` | Śāstra — Dharma, Śāstra — Dharma (Manu), Śāstra — Jyotiṣa, Śāstra — Vyākaraṇa, Śāstra — poetics, Śāstra — Āyurveda | Arthaśāstra, Vyākaraṇa, Philosophy, Medical, Ritual |
| `kosha` | Kośa (lexicon), Kośa (modern compilation), Kośa (nighaṇṭu) | Kośa/Lexicon |
| `buddhist` | (none in ls_source_map's 45 works) | Buddhist |
| `unknown` | (siglum absent from ls_source_map AND lemma absent from DCS) | — |

Two labels have no direct DCS counterpart in `GENRE_RENOU` (`Śāstra —
Jyotiṣa`, `Śāstra — poetics`) — both fold into the `sastra` coarse bucket
regardless; this only affects the coarse rollup, never the specific `label`.
`Tantra/Āgama` (a DCS bucket) has no `ls_source_map` counterpart among the 45
curated works — it stays reachable only via the `dcs_registers` fallback
until a Tantra/Āgama work is added to `ls_source_map.json`.

**Consequences.** H339's `annotate_genres.py` builds directly against this
table — the crosswalk above is normative, not illustrative — plus the
existing precedent `dcs_registers` lane stays available unmodified as the
raw corpus-frequency signal for consumers that want it. `build_dcs_renou.
GENRE_RENOU` remains the single source of DCS-side bucket membership; do not
hand-duplicate it into the new crosswalk code.

## D4 — Government field shape (W3)

**Context.** The store's `government` schema slot exists but is a free
string, unpopulated in all 11,261 rows. `extract_government()` (the census
regex, already validated 30/30 on a seeded sample) deterministically produces
structured output (`cases[]`, `variation`, `connector`, `kind`). The planned
queries (all senses requiring `loc.`; senses allowing case variation; verbs
that never govern `gen.`) need to filter/aggregate on the case list.

**Options considered.**
- Structured object (`{cases:[...], variation, connector, kind}`) —
  recommended in the audit, matches the extractor's native output.
- Keep the free string, write a human-readable rendering into it.

**Ruling.** Structured object. Decider: MG. Dated 08-07-2026.

**Consequences.** H338's schema change tightens `$defs.sense.government`
from a free string to the structured shape; `annotate_government.py` writes
`extract_government(de)`'s output directly, no serialization-to-string step.
The W3(b)4 queries (loc.-requiring senses, variation senses, "verbs never
governing gen.") read `government.cases`/`government.variation` directly.

_Dr. Mārcis Gasūns_
