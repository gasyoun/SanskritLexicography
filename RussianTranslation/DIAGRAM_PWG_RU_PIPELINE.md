# Diagram - how PWG translation works (PWG→RU pipeline)

_Created: 22-08-2026 · Last updated: 22-08-2026_

Rendered from the audited state in
[FULL_DH_STANDARDS_AUDIT_PWG_RU_22-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FULL_DH_STANDARDS_AUDIT_PWG_RU_22-08-2026.md)
(H3291). Numbers are the 22-08 snapshot.

```mermaid
flowchart TD
    %% ============ SOURCES ============
    subgraph SRC["1 · Sources (read-only)"]
        CSL["csl-orig v02/pwg<br/>(canonical digitised PWG,<br/>fenced — never committed)"]
        PWGXML["../pwgxml/pwg.xml<br/>(sibling checkout)"]
        LAYERS["dictionary layers<br/>PW · SCH · PWKVN · NWS<br/>(pwg-ru-data/layers)"]
        CORPUS["corpus-gate dicts + freq<br/>(corpus_lexicon 1.09M rows)"]
    end

    %% ============ PREPARE ============
    subgraph PREP["2 · Prepare (deterministic, no LLM)"]
        ASSEMBLE["compile_translatable.py<br/>→ assembled_cards.jsonl<br/>120,172 headword cards"]
        RAW["pwg-ru-data/raws/<br/>*.raw.txt · *.portrait.json<br/>*.rootmap.json per key"]
        PRIO["priority queue<br/>frequency × attestation strata<br/>(priority_5000_w2 manifests)"]
        ASSEMBLE --> RAW --> PRIO
    end

    %% ============ GATE BEFORE SPEND ============
    subgraph GATE0["3 · Live gate (before every paid window)"]
        HEALTH["health probe<br/>h963_c4_gate0_probe.py<br/>(wall ≤80s, route ≤45s)"]
        CANARY["canary gate<br/>dq_canary_puregloss card<br/>(3/3 senses, zero SAN-LOSS)<br/>→ GO receipt ≤6h old"]
        BOUNDED{"bounded_staged_run.py<br/>--execute"}
        RESERVATION["call-reservation ledger<br/>mandatory --max-calls<br/>--cost-ceiling"]
        HEALTH --> CANARY --> BOUNDED
        RESERVATION --> BOUNDED
    end

    %% ============ TRANSLATE ============
    subgraph TRANSLATE["4 · Translate (paid, one profile at a time)"]
        WORKER["headless_worker.py<br/>claude-cli-headless route<br/>(c1 / c4 / c5 profiles)<br/>sealed manifest+preflight sha"]
        TMREUSE["TM reuse first:<br/>exact → fragment fills<br/>(wave 2: drafted=0,<br/>158k deterministic)"]
        KILL["kill-tree containment<br/>HARD_TIMEOUT ceiling<br/>(safe-mode −55% wall)"]
        WORKER --> DRAFTS["wf_output drafts<br/>per-key cards"]
        TMREUSE --> WORKER
        KILL --> WORKER
    end

    %% ============ QUALITY ============
    subgraph QUALITY["5 · Deterministic gates (no judge)"]
        GATES["markup fidelity ({Tn})<br/>sense-loss · coverage · nws<br/>stage2-pregate · sense-dupes<br/>German-metalanguage flag"]
        AUDITW["audit_window.py<br/>→ classify_run.py<br/>→ requeue_from_audit.py"]
        PROMOTEQ{"promote or quarantine?"}
        GATES --> AUDITW --> PROMOTEQ
    end

    %% ============ STORE ============
    subgraph STORE["6 · Promote (locked, journaled)"]
        CLAIM["PromoteClaim (O_EXCL TTL)<br/>overlay-preserving merge<br/>(human rows protected)"]
        STOREJ["src/pwg_ru_translated.jsonl<br/>11,603 rows · sha 96afca3d<br/>atomic write + fsync backup<br/>promotion journal"]
        TMBUILD["card-TM rebuild +<br/>fragment-TM extend"]
        CLAIM --> STOREJ --> TMBUILD
    end

    %% ============ PUBLISH ============
    subgraph PUB["7 · Publish (DH surfaces)"]
        CANON["canonical.v1.jsonl<br/>2,392 publication records<br/>(green pack only)"]
        FMT["4 interchange formats<br/>JSONL · TMX 1.4b · TEI Lex-0 ·<br/>OntoLex-Lemon/vartrans/PROV-O<br/>loss ledger: 0 lost fields"]
        REL["GitHub release pwg-tm-canonical-v1.0.0<br/>== Zenodo DOI 10.5281/zenodo.21932901<br/>(byte-identical, CC BY 4.0)"]
        HUMAN["human gates (blocked):<br/>G5 review 5/11,163<br/>G6 gold 0/320 built-not-voted<br/>G7 double-review · G10 edition cut"]
        CANON --> FMT --> REL
        HUMAN -.->|"gate finish-lines B/C"| REL
    end

    %% ============ INDEPENDENT QA ============
    subgraph QA["8 · Independent quality instrument"]
        FREEZE["pwg_tm_quality.py freeze<br/>stratified n=400, seed-pinned"]
        JUDGE["blind packet → independent judge<br/>(≠ producer grok-4.6)<br/>fidelity ≥98% · equiv ≥95% · serious ≤1%"]
        VERDICT["verify → quality_report.json<br/>Wilson CIs"]
        FREEZE --> JUDGE --> VERDICT
    end

    %% ===== main flow =====
    CSL --> ASSEMBLE
    PWGXML --> ASSEMBLE
    LAYERS --> ASSEMBLE
    CORPUS --> ASSEMBLE
    PRIO --> BOUNDED
    BOUNDED -->|"GO receipt required"| WORKER
    WORKER --> DRAFTS --> GATES
    PROMOTEQ -->|"clean keys"| CLAIM
    PROMOTEQ -->|"defects → requeue"| PRIO
    PROMOTEQ -->|"quarantine"| QUAR["quarantine tiers<br/>(parked, never silent-drop)"]
    STOREJ -->|"promoted cards"| CANON
    TMBUILD --> TMREUSE
    CANON --> FREEZE
    VERDICT -.->|"wave-1 FAIL held:<br/>serious 2.5% > 1%"| REL
```

## Reading notes

| Edge | Meaning |
|---|---|
| Sources → assemble | Pure Python; the digitised German is never edited (csl-orig fence). |
| Live gate → bounded run | No spend without a fresh health PASS **and** a canary GO receipt consumed by code ([H2159](https://github.com/gasyoun/Uprava/blob/main/handoffs/) pin). |
| TM reuse inside translate | Fragments from already-promoted material fill new cards deterministically first; the model drafts only the residue. |
| Gates → requeue | A failed deterministic gate returns the key to the priority queue — nothing is silently dropped; defects go to named quarantine tiers. |
| Promote | The only writer of the store: lock + journal + fsynced backup; human-reviewed rows survive any re-promotion (H2146). |
| Canonical → publish | Only audit-clean "publication" records enter the citable pack; waves that failed the independent floor are withheld by name. |
| Independent QA | The R15 n=400 instrument that halted wave 1 and now guards wave 2's regeneration ([H3299](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3299-Fable_SanskritLexicography_pwgtm-wave2-regenerate-regate_22.08.26.md)). |

_Dr. Mārcis Gasūns_
