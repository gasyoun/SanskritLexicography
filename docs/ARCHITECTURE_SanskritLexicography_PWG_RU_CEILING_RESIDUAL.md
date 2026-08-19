# ARCHITECTURE — PWG→RU research-ceiling residual

_Created: 19-08-2026 · Last updated: 19-08-2026_

Index: [PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md).

## The shape all five units share

Every unit is an **additive layer over a closed historical corpus**. PWG stays
exactly what Böhtlingk and Roth left; nothing here writes back into it.

```
PWG entries (closed, historical)          ← never modified
   │
   ├─ pwg_sense_stratum.jsonl (Renou proxy, 23,461 senses)
   │      └─ R1: attestation window  ← ls citations × ls_source_map (45 works)
   │
   ├─ Cologne etymology extractors ─┐
   │                                 ├─ C4 two-lane layer (R2 builds the second lane)
   │  KEWA index (OCR, on disk) ────┘
   │
   ├─ R5: frozen gold sets ──▶ the yardstick every later number is measured on
   │
   └─ external witnesses (federated, never merged in)
          ├─ R3 DharmaMitra (Tib/Ch, post-1875)
          └─ R4 Heritage segmenter
```

## The label is the architecture

The single most consequential design constraint in this programme is not a data
structure — it is what each output is **allowed to claim**.

| Unit | The claim it may make | The claim that would be false |
|---|---|---|
| R1 | "this sense is attested in works dated X–Y **per Böhtlingk–Roth's citations**" | "this sense emerged in X" — the window describes a 19th-century citation habit, not the language |
| R2 | two lanes: *traditional* (Cologne dicts, what the 19th-c. tradition says) · *modern IE* (KEWA/EWA) | one merged "etymology" field — the ruling forbids it because the lanes have different epistemic status |
| R3 | derived measurements over DharmaMitra | a composed corpus, before the licence `@DECIDE` is ruled |
| R4 | agreement of two morphology witnesses against a hand-adjudicated set | either engine declared correct — this is a diff, never an overwrite |
| R5 | κ between MG and a **named, frozen** model annotator | inter-annotator agreement in the usual sense — annotator 2 is a model, and every downstream number inherits that |

C3, C5, C7 encode the same discipline in the source roadmap: DCS counts always
travel with the corpus size and genre skew; zero is `unattested-in-sample`, never
`rare`; citation residue is *measured and shrunk*, never quietly dropped. R1 in
particular must emit the C7 residue census rather than silently narrowing to
resolvable citations — a coverage number computed only over what resolved is the
same lie in numeric form.

## R5 — why the yardstick is built alone

Building a gold set and running an evaluation against it in the same pass bends
the yardstick: every judgment call in annotation gets made by someone who already
knows which way it helps the number. Hence the hard split — R5 publishes frozen,
versioned sets and stops; the WSD baseline, the COMET-QE calibration, and the BLI
evaluation are separate handoffs against sets they cannot re-cut.

The single-annotator constraint is real and the workaround is ruled, not
improvised: model-as-annotator-2, **frozen and documented** (model id, prompt,
decoding parameters, date). An undocumented annotator-2 makes κ unreproducible,
which makes it decorative.

## R2 — why the join is the hard part

KEWA lists dhātus as **finite forms**: `bhavati` heads what PWG keys as `bhū`. A
surface join therefore silently drops the entire verbal core while reporting
plausible coverage on nominals. The architecture is a `match_basis` column with
`finite-form→root` as a first-class class, and `ambiguous-multi` as a class rather
than a silent pick.

The failure mode to design against is the same as in kosha's verb crosswalk:
matching harder to raise the number. An unmatched KEWA heading is a **reportable
outcome**, not a defect to be engineered away.

## Cross-cutting invariants

| Invariant | Why |
|---|---|
| PWG is closed; bolt-ons federate, never extend | C8's ruling, and the corpus's whole value as a historical witness |
| Every derived asset registers in [PROJECT_INTERLINKS.md](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md) | so the next session consumes instead of rebuilding |
| Transcoding via the canonical transcoder only | [SHARED_CODE.md](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md) — one source per family; the broken `iast_to_devanagari` is why |
| External services: cache, throttle, identify | R3 and R4 both hit live academic services; the Heritage bot-wall is respected, never defeated |
| Every percentage carries its denominator | a coverage figure over only the resolvable subset is not a coverage figure |
| Rights uncertainty proceeds; confirmed prohibition stops | [standing policy](https://github.com/gasyoun/Uprava/blob/main/docs/STANDING_POLICY_RIGHTS_UNCERTAINTY_IS_NOT_A_STOP_2026.md) |

_Dr. Mārcis Gasūns_
