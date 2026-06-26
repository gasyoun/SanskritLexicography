import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

export const meta = {
  name: 'pwgru-pilot-a-section',
  description: 'corpus-first per-sense Russian translation + Apresjan discrimination of a-section cards (coverage-first manifest), Opus-judged',
  phases: [
    { title: 'Translate', detail: 'Sonnet: per-sense Russian + near-synonym discrimination' },
    { title: 'Judge', detail: 'Opus: review register, sigla, discrimination, coverage' },
  ],
}

const IN = 'C:\\\\Users\\\\user\\\\Documents\\\\GitHub\\\\SanskritLexicography\\\\RussianTranslation\\\\src\\\\pilot\\\\input'
const HERE = dirname(fileURLToPath(import.meta.url))
const FINAL_CARD_SCHEMA = JSON.parse(readFileSync(join(HERE, '..', '..', 'schemas', 'pwg_ru_final_card.schema.json'), 'utf-8'))
// Reversible Windows-safe filename stem — MUST match src/safe_filename.py.
// Keeps the legacy uppercase encoding for compatibility, and escapes forbidden
// filename chars such as "|" as ~hhhh.
const safeName = k => [...k].map(c => {
  if (c >= 'A' && c <= 'Z') return '_' + c.toLowerCase()
  if (/^[a-z0-9-]$/.test(c)) return c
  return '~' + c.charCodeAt(0).toString(16).padStart(4, '0')
}).join('')

// Manifest-driven batch: read scale_route.py's coverage-first ordering and take a
// slice. Edit SECTION/OFFSET/LIMIT to run successive batches (0–29, 30–59, …) over
// the full a-section's 12,155 inputs. Falls back to the original 15-key pilot list
// if the manifest can't be read (e.g. scale_route hasn't run, or no fs access).
const SECTION = 'a'
const OFFSET = 0
const LIMIT = 50
const FALLBACK = ['arTa', 'agni', 'amfta', 'anna', 'aNga', 'akzara', 'anta', 'antarikza',
                  'ap', 'anya', 'apara', 'arjuna', 'anaGa', 'antar', 'api']
let CARDS
try {
  const manifest = JSON.parse(readFileSync(join(HERE, 'output', `scale_manifest.${SECTION}.json`), 'utf-8'))
  CARDS = manifest.map(e => e.key1).slice(OFFSET, OFFSET + LIMIT)
  console.error(`manifest ${SECTION}: ${manifest.length} keys; batch [${OFFSET}, ${OFFSET + LIMIT}) → ${CARDS.length} cards`)
} catch (e) {
  CARDS = FALLBACK
  console.error(`manifest read failed (${e.message}); using ${FALLBACK.length}-key fallback`)
}

const CONV = `pwg_ru CONVENTIONS (from Böhtlingk-Roth's own prefaces + project decisions — follow EXACTLY):
- REGISTER: scholarly-philological. Faithful to PWG's density and precision; this is a printed scholarly dictionary.
- Translate into Russian the natural-language gloss prose. This is German in PWG/PW/SCH/PWKVN and most NWS sub-sources, but the NWS layer ALSO carries English (MW, Olivelle, Keller, Hoernle, BHSD, Sircar) and French (Renou, Padoux, Caland, Rivelex) glosses — translate each gloss FROM ITS OWN language, never relayed through German. A gloss given in two/three languages (e.g. "riz cuit; cooked rice; gekochter Reis") is ONE sense — render it once, not thrice (Guard 7).
- KEEP VERBATIM (never translate or transliterate): Sanskrit (IAST / Devanagari); the literary-source sigla (ṚV., MBH., M., AK., H., …); the German grammatical abbreviations (m., f., n., Pl., Du., adj., …); the German lexicographic/meta abbreviations inside <ab>…</ab> (Bed. = Bedeutung, Schol., s.v., u.s.w. — keep the token, NEVER expand it to its Russian meaning); and <is>…</is> italic source text (a source/siglum reference — keep verbatim, NEVER wrap as {%…%} German gloss). They stay in PWG's Latin/German form.
- TWO-SOURCE PRINCIPLE (B&R's own): a sense backed by a TEXT citation (ṚV, MBH, M, …) is demonstrable usage = attested; a sense from a kośa/grammarian only (Amarakośa AK, Hemacandra H, Pāṇini P, Medinī Med.) is Indian-lexicographic — render it but mark source_type=lexicographic.
- VEDIC senses are 19th-c. European philology and may be superseded; render faithfully; if the German itself hedges, keep the hedge.`

const TR = `You are producing the Russian scholarly entry for one PWG headword (Petersburg Sanskrit Dictionary, Böhtlingk-Roth 1855-75).

${CONV}

INPUTS for headword KEY (read both):
  ${IN}\\KEYFILE.raw.txt        — the RAW German PWG record(s); the FULL sense text to translate (numbered 1)/2) senses, lettered a)/b) sub-senses; {%German%}, {#Sanskrit#}, <ls>sources</ls>, <ab>abbrev</ab>, <lex>grammar</lex>)
  ${IN}\\KEYFILE.portrait.json  — the parsed structure + EVIDENCE: per sense its equivalence_type, citations resolved to full source names + stratum, grammar/diasystem labels; and corpus_synonyms = the Russian ACTUALLY ATTESTED in the parallel corpus for this headword, by stratum (by_stratum) + a freq-ranked candidate set (candidates).

TASK: for EACH record (homonym) and EACH sense/sub-sense in the tree, write the Russian rendering.
- Use the corpus candidates as the PRIMARY evidence for word choice (they are attested, 84% precision; translation-weighted). Where SEVERAL near-synonyms fit, DISCRIMINATE them à la Apresjan: pick the one(s) right for THIS sense and state the differentia (semantic / combinatorial / stratum-connotational) briefly. Prefer renderings attested in the sense's CITED stratum (a ṚV-cited sense → the Vedic corpus renderings). EVIDENCE WEIGHT: if the portrait's corpus_synonyms carries evidence_scope='prefixed-form' or 'root', the candidates are direct evidence for THIS headword — use them as primary. If evidence_scope starts with 'root-fallback' (a split prefixed-verb sub-card whose own surface form is not in the corpus), the candidates are the BARE ROOT's — treat them as a weak hint only and let the German gloss of the prefixed verb govern; do not force a root-meaning synonym onto a prefix that has shifted the sense.
- Mark equivalence_type: a 1-2 word equivalent vs an explanatory gloss (толкование).
- Keep the German sense beside your Russian (side-by-side).

HARD RULES (the judge fails the card otherwise):
1. NO FABRICATION — never output a sense, sub-sense, or tag that is not an actual division in the raw German. Tags must match the raw exactly; do not invent, split, or merge senses (no added "epic"/"vedic" sub-sense the source lacks).
2. COMPLETE COVERAGE — render EVERY sense the raw card contains, in order: every numbered 1)/2), every lettered a)/b) sub-sense, AND any etymology / cross-reference / "personif." note (render the note too, with a short Russian gloss). Skip nothing.
3. SIGLA UNTOUCHED — never translate or transliterate ANY siglum or abbreviation, including COMMENTATOR sigla (Sāy., Schol., Sch., Comm.), grammar abbrevs (m./f./Pl./Du.), and German lexicographic/meta abbreviations inside <ab>…</ab> (Bed., Schol., s.v.) — keep the abbreviation token verbatim, NEVER expand it (e.g. <ab>Bed.</ab> stays «Bed.», not «значением»). <is>…</is> italic source text is a verbatim siglum, NEVER {%…%} gloss (do not render <is> inside {%…%}). They stay verbatim in PWG form; let no German or English word leak into the Russian.
4. ALL RECORDS, INCLUDING NACHTRÄGE — a headword is often a MAIN record plus one or more ADDENDA/NACHTRÄGE records (each marked in the raw input). These do not repeat the word; they PATCH the main entry — "to sense 3 add citation X", "sense 10: read … instead of …", an etymology tail, a new astrological/numeric sense. Render EVERY record completely and EVERY addendum in full, including its tail (etymology, cross-reference, corrigendum). Addenda are first-class — never drop, summarise, or truncate them. Key each addendum sense to the main-entry sense number it patches. One addendum can itself carry SEVERAL numbered patch-items (1a, 2a, 3a, …) — render EVERY item; dropping any single patch fails coverage.
5. NWS LAYER — USE THE AUTHORITATIVE PRE-PARSED OWNER MAP. The input contains a section "=== LAYER: NWS — PRE-PARSED OWNER MAP (AUTHORITATIVE, N entries) ===" listing numbered entries  N. [NWS: OWNER] {#lemma#} [tag] gloss . Emit EXACTLY ONE NWS card row per numbered entry, IN THAT ORDER; copy each entry's [NWS: OWNER] token VERBATIM as that row's LAST citation; translate the gloss from its own language; keep {#lemma#}/IAST/sigla. Do NOT re-derive, swap, merge, drop, or re-order owners, and do NOT read owners off the raw fragment — the map is the single source of truth (this makes the F12 slide impossible). If no owner map is present, fall back to: ONE ENTRY PER SOURCE, OWNER-CITATION KEPT (the deterministic auditor nws_split.py checks this; it fails the card otherwise). The "=== LAYER: NWS ===" fragment packs many sub-dictionaries into one string in the shape  [LEMMA] TAG > gloss .. OWNER : page >  [LEMMA] TAG > gloss .. OWNER : page > …  — the diasystem TAG PRECEDES each gloss and the OWNER citation (Author year : page, e.g. "Graßmann 1873 (1996) : 70", "Geldner 1907 : 10", "MW : 47 (s.v. ap)") CLOSES it. Output ONE sense per such entry, in source order: NEVER merge two owners into one, never drop the owner, and never compress several "Wasser=water" attestations into a single row. Each NWS sense MUST (a) be tagged so it reads as NWS (prefix "[NWS:]" or tag "NWS"), and (b) keep its OWNER citation VERBATIM as the LAST citation of that sense (so the auditor can read the owner). CRITICAL reading direction (failure F12): the owner comes AFTER the gloss — do NOT slide it onto the next gloss; "X > Y : p" means Y:p owns X, not the following entry. Sub-lemmas the NWS lists (separate compound headwords, e.g. apaḥsaṃvarta, abdurga) are first-class entries too — render each as its own NWS row, never as a sense of the head.

Return ONLY the structured object.`

const CARD = { ...FINAL_CARD_SCHEMA.$defs.card, $defs: FINAL_CARD_SCHEMA.$defs }
const JUDGE = { ...FINAL_CARD_SCHEMA.$defs.judge, $defs: FINAL_CARD_SCHEMA.$defs }

// root-split sub-card keys (man~~h0_00_pwg00, …) are ALREADY safe filename stems — use them
// verbatim; only true headword keys get re-encoded by safeName.
const fileOf = k => (k.includes('~~') ? k : safeName(k))

phase('Translate')
const out = await pipeline(
  CARDS,
  k => agent(TR.replace(/KEYFILE/g, fileOf(k)).replace(/KEY/g, k), { label: `tr:${k}`, phase: 'Translate', schema: CARD, model: 'sonnet' }),
  (card, k) => {
    if (!card) return { key: k, card: null, judge: null }
    return agent(`You are the Opus QA judge for the pwg_ru pilot. Review this translated card against the conventions and the source.

${CONV}

You may re-read the source: ${IN}\\${fileOf(k)}.raw.txt and ${IN}\\${fileOf(k)}.portrait.json.

Check: (1) Russian correctness vs the German; (2) scholarly-philological register; (3) sigla + grammar abbreviations kept VERBATIM (not translated/transliterated) — fail sigla_kept if any ṚV./MBH./m./f. was rendered into Russian; (4) per-sense near-synonym discrimination quality (real Apresjan differentiae, not a flat list); (5) corpus evidence actually used; (6) coverage — every PWG sense rendered. severity 1=publishable … 5=broken.

TRANSLATED CARD (JSON):
${JSON.stringify(card).slice(0, 12000)}`,
      { label: `judge:${k}`, phase: 'Judge', schema: JUDGE, model: 'opus' })
      .then(j => ({ key: k, card, judge: j }))
  }
)

return { results: out.filter(Boolean) }
