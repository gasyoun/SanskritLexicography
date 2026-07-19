import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

// TEMPLATE ONLY. Current production windows must be generated with
// `python src/pilot/gen_opt_harness.py <root>` and run via
// `src/pilot/run_pilot_wf.opt.js`; this committed file is the source template.

export const meta = {
  name: 'pwgru-pilot-a-section',
  description: 'corpus-first per-sense Russian translation + Apresjan discrimination + Sanskrit-microstructure rules (samasa/correlative/sastric) of a-section cards (coverage-first manifest); Sonnet bulk-judged, Opus adjudicates ONLY the rejects',
  phases: [
    { title: 'Translate', detail: 'Sonnet: per-sense Russian + near-synonym discrimination' },
    { title: 'Judge', detail: 'Sonnet: review register, sigla, discrimination, coverage — every card' },
    { title: 'Adjudicate', detail: 'Opus: re-judge ONLY the hard cases Sonnet flagged (ok=false or severity>=3)' },
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
3. SIGLA UNTOUCHED — never translate or transliterate ANY siglum or abbreviation, including COMMENTATOR sigla (Sāy., Schol., Sch., Comm.), grammar abbrevs (m./f./Pl./Du.), and German lexicographic/meta abbreviations inside <ab>…</ab> (Bed., Schol., s.v.) — keep the abbreviation token verbatim, NEVER expand it (e.g. <ab>Bed.</ab> stays «Bed.», not «значением»). <is>…</is> italic source text is a verbatim siglum, NEVER {%…%} gloss (do not render <is> inside {%…%}). They stay verbatim in PWG form; let no German or English word leak into the Russian. MARKUP DELIMITERS VERBATIM: in the german field reproduce the raw record's own delimiters EXACTLY — keep every {#…#} around Sanskrit and every <ls>…</ls>, <ab>…</ab>, <lex>…</lex>, <is>…</is> tag as-is; do NOT strip them to plain text, do NOT transliterate {#…#} to bare IAST, do NOT "clean"/"trim" the markup. Keep any Sanskrit you cite in the russian field wrapped in {#…#} too. The deterministic fidelity gate counts these tokens: a card that loses >10% of its <ls> or >15% of its {#…#} spans is REJECTED.
4. ALL RECORDS, INCLUDING NACHTRÄGE — a headword is often a MAIN record plus one or more ADDENDA/NACHTRÄGE records (each marked in the raw input). These do not repeat the word; they PATCH the main entry — "to sense 3 add citation X", "sense 10: read … instead of …", an etymology tail, a new astrological/numeric sense. Render EVERY record completely and EVERY addendum in full, including its tail (etymology, cross-reference, corrigendum). Addenda are first-class — never drop, summarise, or truncate them. Key each addendum sense to the main-entry sense number it patches. One addendum can itself carry SEVERAL numbered patch-items (1a, 2a, 3a, …) — render EVERY item; dropping any single patch fails coverage.
5. NWS LAYER — USE THE AUTHORITATIVE PRE-PARSED OWNER MAP. The input contains a section "=== LAYER: NWS — PRE-PARSED OWNER MAP (AUTHORITATIVE, N entries) ===" listing numbered entries  N. [NWS: OWNER] {#lemma#} [tag] gloss . Emit EXACTLY ONE NWS card row per numbered entry, IN THAT ORDER; copy each entry's [NWS: OWNER] token VERBATIM as that row's LAST citation; translate the gloss from its own language; keep {#lemma#}/IAST/sigla. Do NOT re-derive, swap, merge, drop, or re-order owners, and do NOT read owners off the raw fragment — the map is the single source of truth (this makes the F12 slide impossible). If no owner map is present, fall back to: ONE ENTRY PER SOURCE, OWNER-CITATION KEPT (the deterministic auditor nws_split.py checks this; it fails the card otherwise). The "=== LAYER: NWS ===" fragment packs many sub-dictionaries into one string in the shape  [LEMMA] TAG > gloss .. OWNER : page >  [LEMMA] TAG > gloss .. OWNER : page > …  — the diasystem TAG PRECEDES each gloss and the OWNER citation (Author year : page, e.g. "Graßmann 1873 (1996) : 70", "Geldner 1907 : 10", "MW : 47 (s.v. ap)") CLOSES it. Output ONE sense per such entry, in source order: NEVER merge two owners into one, never drop the owner, and never compress several "Wasser=water" attestations into a single row. Each NWS sense MUST (a) be tagged so it reads as NWS (prefix "[NWS:]" or tag "NWS"), and (b) keep its OWNER citation VERBATIM as the LAST citation of that sense (so the auditor can read the owner). CRITICAL reading direction (failure F12): the owner comes AFTER the gloss — do NOT slide it onto the next gloss; "X > Y : p" means Y:p owns X, not the following entry. Sub-lemmas the NWS lists (separate compound headwords, e.g. apaḥsaṃvarta, abdurga) are first-class entries too — render each as its own NWS row, never as a sense of the head.
6. TRANSLATE, DON'T ANNOTATE — render EXACTLY what the German states, no more. Within a sense, NEVER add an interpretive gloss, a parenthetical domain clarification, a scope qualifier, or a scholarly attribution («и другими», «и тому подобное», «(о небесных телах)») that the German does not itself contain. If the German credits a derivation to ONE authority (e.g. «wird von BENFEY … zurückgeführt»), name ONLY that authority — do NOT generalise «BENFEY» to «BENFEY и другими». When unsure, translate LESS, not more: an unsourced addition is a fidelity defect exactly like an omission.
7. GOVERNMENT MARKERS VERBATIM — when the German gloss carries a parenthesized case-government note (e.g. `(<ab>loc.</ab>)`, `(<ab>loc.</ab> und <ab>gen.</ab>)`) or a `mit dem <ab>case.</ab>` phrase, copy the case abbreviation into the sense's `government` field exactly as it appears in the source (one entry per marker found) — NEVER invent, guess, generalize, or add a case the German does not state. Leave `government` an empty array when the German carries no such marker. This is deterministic — do not paraphrase the case into the Kochergina idiom or any other rendering.
8. NO GERMAN PROSE IN CITATION SCAFFOLDING (H1302) — a German prose function word that JOINS citations or notes must be TRANSLATED into Russian, not kept: «Schol. zu X» → «Schol. к X», «bei X» → «у X», «X und Y» → «X и Y», «mit Ergänzung von Z» → «с восполнением Z», a section-header «Mit {#prefix#}» → «С {#prefix#}». Only the <ab>…</ab>/<ls>…</ls>/<is>…</is> siglum TOKEN itself stays verbatim (rule 3) — the connective prose around it becomes Russian. This applies INSIDE citations too, where German zu/bei/und/oder/nach/im/so/als commonly survive untranslated.

RENDERING GUIDANCE — Sanskrit microstructure (from the lexicography-manual harvest, see ../glossaries/de_ru_translation_aids.md; quality, judged softly — these refine wording, they do NOT add/drop senses):
- COMPOUNDS (samāsa) are right-headed: build the Russian off the vigraha, head = the SECOND member. tatpuruṣa asi-kalaha → «бой мечом» (head «бой»); NEVER a member-by-member calque off the first constituent. bahuvrīhi is exocentric (a possessor OUTSIDE the compound): hata-putra- → «та, у кого убиты сыновья / чьи сыновья убиты», not the literal sum. …-ādi / …-prabhṛti = an OPEN class = the hypernym of its members → «X и тому подобное / и прочее», never a closed list. Split an over-long stacked compound into several Russian clauses, not one calque (Apte/Gillon, Inglese-Geupel).
- CORRELATIVES (yad…tad): when the German keeps the correlative order, render a PREPOSED Russian correlative — кто…тот, что…то, какой…такой, чей…того, где…там, куда…туда, когда…тогда, как…так, сколько…столько, чем…тем. Doubled yo yaḥ → «кто бы ни / всякий, кто»; yāvat…tāvat → «пока…до тех пор»; yadi…tarhi → «если…то». Keep BOTH pairs; do not flip which clause is asserted (Mitrenina, Zaliznyak-Paducheva, Ruppel).
- ŚĀSTRIC FORMULAS — fixed dry Russian, do not re-translate per occurrence: iti arthaḥ → «то есть; таков смысл»; ity uktam → «сказано»; anena … vivakṣitam → «этим он хочет сказать»; X-bhāvaḥ / X-tvam → «состояние/свойство X». Their presence marks scholastic register → flat terminological Russian (Tubb).
- SYNONYM CARDINALITY: render a German synonym-string (Glanz, Schimmer, Pracht) as a Russian synonym-string of EQUAL cardinality — never collapse n near-synonyms to one word; pick by register, default to the neutral dominant (Apresjan, Baalbaki).
- PUNCTUATION carries sense-grouping: comma = interchangeable synonyms WITHIN one sense; semicolon = a boundary between non-interchangeable senses. Preserve PWG's comma/semicolon exactly in the Russian (Hartmann & James).
- MANNER/POSITION: where Russian grammatically forces a manner/position verb (идти/ползти/лететь; стоять/лежать/висеть) that the German leaves open, choose from the cited context; a wrong neutral default (e.g. «находиться», «лежать» for something that hangs) is grammatical-but-false (Apresjan).
- NON-CIRCULAR GLOSSES: a Russian gloss must be clearer than the Sanskrit/PWG headword. Avoid circular or cryptographic paraphrases, bare transliterated Sanskrit, or a rarer Russian term where a plain explanatory gloss is needed (Apresjan).

Return ONLY the structured object.`

const CARD = { ...FINAL_CARD_SCHEMA.$defs.card, $defs: FINAL_CARD_SCHEMA.$defs }
const JUDGE = { ...FINAL_CARD_SCHEMA.$defs.judge, $defs: FINAL_CARD_SCHEMA.$defs }

// root-split sub-card keys (man~~h0_00_pwg00, …) are ALREADY safe filename stems — use them
// verbatim; only true headword keys get re-encoded by safeName.
const fileOf = k => (k.includes('~~') ? k : safeName(k))

// QA-judge prompt, model-neutral (Sonnet judges every card; Opus re-judges only rejects).
const CHECKS = `Check: (1) Russian correctness vs the German; (2) scholarly-philological register; (3) sigla + grammar abbreviations kept VERBATIM (not translated/transliterated) — fail sigla_kept if any ṚV./MBH./m./f. was rendered into Russian; (4) per-sense near-synonym discrimination quality (real Apresjan differentiae, not a flat list); (5) non-circular glosses — reject cryptographic/circular definitions or bare transliterated Sanskrit as the Russian gloss; (6) corpus evidence actually used; (7) coverage — every PWG sense rendered; (8) Sanskrit-microstructure rendering (soft) — compounds right-headed (head = 2nd member, bahuvrīhi exocentric, -ādi = hypernym «и тому подобное»), correlatives preposed (кто…тот), śāstric formulas fixed-and-flat, synonym-string cardinality preserved, comma/semicolon sense-grouping kept; flag drift but do not fail an otherwise-correct card on (8) alone. severity 1=publishable … 5=broken; set ok=false when severity>=3.`

const judgePrompt = (card, k, role) => `${role}

${CONV}

You may re-read the source: ${IN}\\${fileOf(k)}.raw.txt and ${IN}\\${fileOf(k)}.portrait.json.

${CHECKS}

TRANSLATED CARD (JSON):
${JSON.stringify(card).slice(0, 12000)}`

// Escalation policy (research/JUDGE_POLICY.md, 2026-06-25; A/B-validated in JUDGE_AB.md,
// κ=1.0 over 474 cards). Sonnet judges EVERY card; Opus re-judges ONLY the hard cases Sonnet
// cannot clear — a reject: ok=false or severity>=3 — and its verdict is FINAL. Publishable
// cards (sev 1–2) keep Sonnet's verdict and spend no Opus tokens: that is the weekly-quota
// headroom (PILOT_COST.md §6/§7) that makes the bulk run feasible on one Max seat.
const isHard = j => !j || j.ok === false || (j.severity ?? 5) >= 3

phase('Translate')
const out = await pipeline(
  CARDS,
  // Stage 1 — translate (Sonnet)
  k => agent(TR.replace(/KEYFILE/g, fileOf(k)).replace(/KEY/g, k), { label: `tr:${k}`, phase: 'Translate', schema: CARD, model: 'sonnet' }),
  // Stage 2 — bulk judge (Sonnet), every card
  (card, k) => {
    if (!card) return { key: k, card: null, judge: null, judge_sonnet: null, escalated: false }
    return agent(judgePrompt(card, k, 'You are the QA judge for the pwg_ru bulk run. Review this translated card against the conventions and the source.'),
      { label: `judge:${k}`, phase: 'Judge', schema: JUDGE, model: 'sonnet' })
      .then(j => ({ key: k, card, judge: j, judge_sonnet: null, escalated: false }))
  },
  // Stage 3 — Opus adjudication, ONLY the hard cases Sonnet rejected. `judge` becomes the
  // final (Opus) verdict; Sonnet's original is preserved as `judge_sonnet`.
  (res, k) => {
    if (!res || !res.card || !res.judge || !isHard(res.judge)) return res
    return agent(judgePrompt(res.card, k,
      `You are the Opus adjudicator for the pwg_ru bulk run. The Sonnet judge flagged this card as a HARD case it could not clear (ok=${res.judge.ok}, severity=${res.judge.severity}; issues: ${JSON.stringify(res.judge.issues || []).slice(0, 1500)}). Re-judge it INDEPENDENTLY and authoritatively against the conventions and the source — confirm or OVERTURN Sonnet's verdict. Your verdict is final and decides whether the card is re-translated.`),
      { label: `opus-adj:${res.key}`, phase: 'Adjudicate', schema: JUDGE, model: 'opus' })
      .then(opus => ({ key: res.key, card: res.card, judge: opus, judge_sonnet: res.judge, escalated: true }))
  }
)

return { results: out.filter(Boolean) }
