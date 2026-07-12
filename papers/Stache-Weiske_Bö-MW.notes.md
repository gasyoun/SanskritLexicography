# Reading notes — Stache-Weiske (2015) on the Böhtlingk–Monier-Williams plagiarism dispute

_Created: 12-07-2026 · Last updated: 12-07-2026_

Companion notes to [`Stache-Weiske_Bö-MW.pdf`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/Stache-Weiske_Bö-MW.pdf).

> Agnes Stache-Weiske. 2015. „Man muß zuweilen Insekten mit Kanonen schießen." Max Müllers Rolle
> im Streit zwischen Böhtlingk und Monier-Williams. In: *„In ihrer rechten Hand hielt sie ein
> silbernes Messer mit Glöckchen…" — Studies in Indian Culture and Literature* (Festschrift Heidrun
> Brückner), eds. A. A. Esposito, H. Oberlin, B. A. Viveka Rai & K. J. Steiner, 323–336. Wiesbaden:
> Harrassowitz. ISBN 978-3-447-10548-4.

## Why this paper matters to us

It is the **primary-source documentation of the founding accusation of Sanskrit computational
lexicography-forensics**: Otto Böhtlingk's 1883 charge that Monier-Williams's *Sanskrit-English
Dictionary* (MW) is an unselbständige "Ausbeutung" (exploitation) of the Petersburg dictionaries
(PW/pw). Reconstructed from the newly-surfaced Böhtlingk↔Max-Müller correspondence (22 Müller letters
in the Leipzig Streitberg Nachlass + Böhtlingk's replies in the Oxford Bodleian), it hands us the
**exact terms** of the charge — which is precisely what our A10 forensic suite (csl-atlas) measures on
the digitised editions. The paper turns A10 from "an interesting quantitative exercise" into "the
computational adjudication of a named, dated, 140-year-old scholarly accusation." That framing is the
enrichment.

## The dispute in one paragraph

MW appeared 1872; Böhtlingk largely **ignored** it for eleven years ("keine Citate … dann brauche ich
es nicht"). In 1881 Max Müller — a Clarendon Press curator with a long personal animus against MW,
dating to his 1860 defeat for the Boden Chair — reopened it when MW sought a 2nd edition, feeding
Böhtlingk the plagiarism framing and the English legal theory that reprinting another's misprints is
"piracy." Böhtlingk went public in the 1883 preface to *pw* vol. 4, citing **35 passages**. The
Clarendon Press first declined, then (with a £900 India-Council subsidy) published MW² anyway. Müller's
verdict on the whole affair — the title quote — was that shooting Böhtlingk's cannon at the MW "insect"
was an unpleasant business. Zgusta (1988) later judged it a failure of *acknowledgement*, not theft.

## The charge, itemised — and what each clause maps onto

Müller's letter of 11 June 1881 (Stache-Weiske p. 328) states it most precisely: MW reproduces PW's
**omissions**, its **errors**, and its **sense-order** —
> „Was in Ihrem Werk ausgelaßen u[nd] versehen ist, ist bei ihm ausgelaßen und versehen u[nd] die
> Reihenfolge der Bedeutungen einfach abgeschrieben."

Böhtlingk to the Clarendon Press, 28 Nov 1881 (p. 330): MW carries "Versehen mannigfacher Art,
Druckfehler und falsche Citate, die wiederholt werden." Böhtlingk's own evidential bar (25 March 1882,
p. 332): a **single** demonstrable copied case suffices. Müller's legal test (30 June 1881): under
English law "Wiederabdruck von Druckfehlern" = piracy — i.e. the **common-error principle**, exactly
the Lachmann criterion our A10 uses.

| Historical clause (1881–83) | Our computational test | Status now |
|---|---|---|
| Shared **omissions** — "was ausgelaßen ist, ist ausgelaßen" | A10 §3.5 / **F9** shared-omission (this session) | **Measured.** MW's omissions track PWG's ≈8× more than independent Apte (gap-sensitivity 12.3× vs 1.5×) → inventory descent confirmed; **but** MW independently fills 54.6% of PWG's gaps → *not* a carbon copy. Descent, not blindness. |
| Shared **errors** — misprints | A10 §4.1 F4b (Ahlborn), §4.3 F4a print errors | **Null.** MW carries ≈0% of PWG's misspellings; 0 shared print errors. |
| Shared **false citations** | A10 §6 F7 (Harivaṃśa vulgate) | **Measured null** on tested corpora (1/587 via DCS; 0 shared errors vs Kinjawadekar vulgate). A recorded negative, not a closed avenue — a Nilakantha-vulgate MBH text would reopen it. |
| Copied **sense-order** — "Reihenfolge der Bedeutungen" | A10 §3.4 F5 (citation-order 0.811) — **proxy only** | **Partially tested.** F5 measures *citation* order, not *meaning* order. The literal Müller claim (order of senses) is **untested** — see actionable #1. |
| Shared apparatus (which words / which texts) | A10 §3.1–3.3 (containment, F1 citation Jaccard, F2 homonym) | **Strongly positive** — the paper's core. |

Net verdict (ours, matching Zgusta's historical one): **MW is heir to Böhtlingk's scholarship —
inventory, citation apparatus, entry order — and author of its own English prose and typesetting.**
Böhtlingk's "shared errors" charge does **not** hold on the digitised evidence; his "shared apparatus /
inventory" charge holds overwhelmingly. The dispute was, in modern terms, about un-credited *derived*
work, not fabricated errors.

## What this session did (H796)

- **Ran the shared-omission test (F9)** — the one clause of the charge A10 had never tested. Result and
  method: [`csl-atlas/.../SHARED_OMISSION_TEST.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/SHARED_OMISSION_TEST.md),
  script [`f9_shared_omission.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f9_shared_omission.py).
- **Integrated the documentary history into A10** (not a new paper, per instruction): §1 grounding (the
  35 Stellen, the correspondence, Müller's legal test, Zgusta's verdict), §3.5 result, F9 in the method
  table, abstract + references (Stache-Weiske 2015, Zgusta 1988). [csl-atlas PR #263](https://github.com/sanskrit-lexicon/csl-atlas/pull/263).
- **Logged the non-independence caveat** as [FINDINGS §82](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md): PWG/PW/MW collapse to ≈one European
  witness; do not count their agreement as independent corroboration.

## Actionable items — "pure statement then, verifiable now"

1. **Sense-order test (Müller's literal item, still untested).** F5 measured *citation* order; the
   charge was *"die Reihenfolge der Bedeutungen"* — the order of glosses/senses within an entry. A
   cross-lingual sense-sequence alignment (MW English senses ↔ PWG German senses, per shared headword)
   would close the last open clause. Harder than F5 (needs sense segmentation + DE↔EN sense matching),
   but the data (parsed MW + PWG entries) is in hand. **This is the one remaining "asserted but not
   measured" clause.**
2. **Locate Böhtlingk's actual 35 Stellen** (1883 *pw* vol. 4 preface, pp. II–III) and resolve each on
   the digitised editions — a small, high-value gold set for *directly* re-adjudicating the specific
   cases Böhtlingk chose, rather than corpus-wide aggregates. The preface text is a scan; OCR + manual
   extraction of ~35 items is cheap.
3. **Widen the shared-omission anchor** (F9 used SKD ∩ VCP = 6,941; SKD ∪ VCP or + Amarakośa/Apte-cross
   would test robustness) — an enhancement, not a gate.

## Bibliographic leads surfaced by the paper (for our lit library)

- Zgusta, L. 1988. "Copying in lexicography: Monier-Williams … (Dvaikośyam)." *Lexicographica* 4,
  145–164. — the scholarly analysis of exactly our question; **should be acquired** for M01/A10.
- Zgusta, L. 1986. "Eine Kontroverse zwischen der deutschen und englischen Sanskrit-Lexikographie."
- Stache-Weiske, A. 2007. *Otto Böhtlingk an Rudolf Roth. Briefe zum Petersburger Wörterbuch 1852–1885.*
  Wiesbaden: Harrassowitz. — the full Böhtlingk–Roth correspondence; the source behind most of the paper.
- Stache-Weiske, A. 2012. "…Verhältnis von Otto Böhtlingk und Max Müller." In *200 Jahre Indienforschung*.

_Dr. Mārcis Gasūns_
