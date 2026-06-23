# NWS erratum email — draft for the Halle/Marburg team

**Purpose.** A single source-data defect surfaced by the full NWS
attribution audit (see [NWS_AUDIT_REPORT.md](NWS_AUDIT_REPORT.md), errata
table). The audit ran a deterministic owner-attribution parser over the whole
*Nachtragswörterbuch des Sanskrit* (all 167,990 entries / the complete SLP1
range; 61,072 attribution-bearing entries) and found exactly **one** defect in
the NWS source itself — every other unrecovered owner is a parser known
limitation, not bad data. This is therefore a complete, consolidated erratum,
not a running list.

**Recipient.** The NWS project team — Indology: Hanneder & Demoto-Hahn
(Marburg), Slaje, Einicke, Siegfried & Wilke (Halle); via the project site
<https://nws.uzi.uni-halle.de/>. Send by hand (one targeted note, no automated
posting).

**The defect in one line.** In the entry `vṛtrakhādá`, the literature reference
reads `NṚV 2B : 79 (s. (2. khād )` but should read `NṚV 2B : 79 (s.v. 2. khād )`
— `s.` is missing its `v.`, and there is one superfluous opening parenthesis
(the parenthetical is unbalanced). Confirmed against the two sibling entries
that carry the identical reference in well-formed shape:
`amitrakhādá → NṚV 2B : 79 (s.v. 2. khād )` and
`vikhādá → NṚV 2B : 79 (s.v. 2 khād )`.

---

## Betreff: Korrekturhinweis NWS — fehlerhafter Quellverweis bei *vṛtrakhādá*

Sehr geehrtes NWS-Team,

im Rahmen einer russischen Übersetzung des Petersburger Wörterbuchs haben wir
einen deterministischen Parser entwickelt, der zu jedem NWS-Eintrag den
zugehörigen Quellverweis (Autor/Werk : Seite) automatisch wiederherstellt, und
ihn zur Qualitätssicherung über das **gesamte** Nachtragswörterbuch laufen
lassen (alle 167.990 Einträge; 61.072 davon mit Quellenangabe).

Dabei ist genau **ein** Fehler im NWS-Quelltext selbst aufgefallen, den wir
Ihnen hiermit gesammelt melden möchten:

- **Lemma:** `vṛtrakhādá`
- **Wie gedruckt:** `NṚV 2B : 79 (s. (2. khād )`
- **Vermutlich gemeint:** `NṚV 2B : 79 (s.v. 2. khād )`

Es handelt sich offenbar um einen Digitalisierungsfehler: `s.` ohne `v.` sowie
eine überzählige öffnende Klammer, sodass die Klammer nicht geschlossen wird.

Beleg: Die beiden Schwestereinträge mit demselben Quellverweis `NṚV 2B : 79`
tragen den Querverweis in korrekter Form —
`amitrakhādá → NṚV 2B : 79 (s.v. 2. khād )` und
`vikhādá → NṚV 2B : 79 (s.v. 2 khād )`.

Für Rückfragen oder weitere Details (Fundstelle, Audit-Methodik) stehen wir
gerne zur Verfügung. Vielen Dank für Ihre wertvolle Arbeit am
Nachtragswörterbuch.

Mit freundlichen Grüßen
