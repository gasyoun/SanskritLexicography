# Addenda-to-Addenda probe (PWG vol. 7 & PW Nachträge)

_Created: 06-07-2026 · Last updated: 06-07-2026_

**Deliverable 5 (NOW-track) of
[H180](https://github.com/gasyoun/Uprava/blob/main/handoffs/H180-Opus_RussianTranslation_pwg_ru_addenda_typology_glue_learner_05.07.26.md)**
(MG ruling 05-07-2026: "explore Addenda-to-Addenda now, defer the rest"). Question: does
the supplement-to-a-supplement material (PWG's *Nachträge* in vol. 7; PW's *Nachträge*)
already live in csl-orig, and how does it fold into
[`ADDENDA_TYPOLOGY.md`](ADDENDA_TYPOLOGY.md)?

## Finding — yes, it is already in csl-orig, and already in the merge

### 1. PWG *Nachträge* live in vol. 7 of csl-orig `pwg`

`pwg.txt` entries are stamped `<pc>V-PPPP` (volume-page). Volume 7 runs to `<pc>7-1822`
and holds **25,748 entries** — this is where PWG's *Nachträge und Berichtigungen*
(addenda & corrigenda, appended to the 7-volume großes PW, 1855–1875) sit. They are
**structurally ordinary `<L>` entries**, not flagged as addenda; isolating them requires
a page-range boundary within vol. 7 (the point where the main dictionary ends and the
Nachträge begin), which is a page-mapping task deferred to a second pass.

The German word *Nachtrag* also appears **341×** inside PWG definition prose (e.g.
`agniSeza` "Nachtrag zu … der Taitt. Saṃh."), but those are **semantic uses**, not
structural addenda — do not count them as A2A instances.

### 2. PW *Nachträge* live in vol. 7 of csl-orig `pw` (35,581 entries, to `<pc>7-390`).

### 3. The `pwkvn` layer IS the PW-Nachträge material, already merged and translated

The five-layer merge's **`pwkvn` layer** (= PW *Nachträge* vol. 7 + von Negelein) is
exactly this Addenda-to-Addenda content, already pulled onto the PWG skeleton. Evidence
— a real translated `pwkvn` sub-card:

```
Ap  subcard=_ap~~h0_zz_pwkvn  sense_tag=ava_caus
de: {#Ap#}¦ mit {#ava#} <ab>Caus.</ab> … {%erlangen [Page1-297-b] lassen%} <ls>NAIṢ. 8,89</ls>.
```

The embedded `[Page1-297-b]` is a **back-reference to PWG vol. 1 page 297** — i.e. the
Nachträge entry explicitly *relocates* onto a specific PWG page/sense. That is the
`relocate` operation of [`ADDENDA_TYPOLOGY.md`](ADDENDA_TYPOLOGY.md) §3.5 (`subtype=a2a`),
made concrete. There are **129 `pwkvn` sub-cards** in the current translated set.

## Fold-in rule

- A2A material = `op=relocate`, `direction=additive`, `subtype=a2a`, carried by the
  `pwkvn` layer.
- Its `insertion_point.target_sense` is recoverable from the `[PageV-PPP-x]` anchor
  embedded in the card body → resolve the anchor to the PWG homonym+sense it points at.
- No separate scrape needed — the material is already merged and translated; the only
  remaining work is anchor-resolution to populate `insertion_point`.

## Deferred backlog (catalogue only — no near-term work)

Per MG ruling, listed for the paper's "future data layers" section:

| layer | what it is | likely contribution |
|---|---|---|
| **Reviews of PWG** (Winternitz et al.) | contemporary scholarly reviews | entry-level corrections/critiques flagged by reviewers |
| **Böhtlingk–Roth letters** *Briefe zum Petersburger Wörterbuch 1852–1885* (Wiesbaden 2008) | editorial correspondence | rationale behind specific inclusion/abridgement decisions |
| **Kulikov 2010 review** (*Acta Orientalia Vilnensia*) | modern review | entry-level insight on the tradition's method |

## Next pass

1. Detect the vol.-7 page boundary where PWG's Nachträge begin (isolate them from the
   main vol. 7 body).
2. Resolve `[PageV-PPP-x]` anchors in `pwkvn` cards → PWG homonym/sense, populating
   `insertion_point` for the `a2a` instances.

_Dr. Mārcis Gasūns_
