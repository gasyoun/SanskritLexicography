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
const LIMIT = 30
const FALLBACK = ['arTa', 'agni', 'amfta', 'anna', 'aNga', 'akzara', 'anta', 'antarikza',
                  'ap', 'anya', 'apara', 'arjuna', 'anaGa', 'antar', 'api']
let CARDS
try {
  const __dir = dirname(fileURLToPath(import.meta.url))
  const manifest = JSON.parse(readFileSync(join(__dir, 'output', `scale_manifest.${SECTION}.json`), 'utf-8'))
  CARDS = manifest.map(e => e.key1).slice(OFFSET, OFFSET + LIMIT)
  console.error(`manifest ${SECTION}: ${manifest.length} keys; batch [${OFFSET}, ${OFFSET + LIMIT}) → ${CARDS.length} cards`)
} catch (e) {
  CARDS = FALLBACK
  console.error(`manifest read failed (${e.message}); using ${FALLBACK.length}-key fallback`)
}

const CONV = `pwg_ru CONVENTIONS (from Böhtlingk-Roth's own prefaces + project decisions — follow EXACTLY):
- REGISTER: scholarly-philological. Faithful to PWG's density and precision; this is a printed scholarly dictionary.
- Translate into Russian ONLY the German gloss prose.
- KEEP VERBATIM (never translate or transliterate): Sanskrit (IAST / Devanagari); the literary-source sigla (ṚV., MBH., M., AK., H., …); and the German grammatical abbreviations (m., f., n., Pl., Du., adj., …). They stay in PWG's Latin/German form.
- TWO-SOURCE PRINCIPLE (B&R's own): a sense backed by a TEXT citation (ṚV, MBH, M, …) is demonstrable usage = attested; a sense from a kośa/grammarian only (Amarakośa AK, Hemacandra H, Pāṇini P, Medinī Med.) is Indian-lexicographic — render it but mark source_type=lexicographic.
- VEDIC senses are 19th-c. European philology and may be superseded; render faithfully; if the German itself hedges, keep the hedge.`

const TR = `You are producing the Russian scholarly entry for one PWG headword (Petersburg Sanskrit Dictionary, Böhtlingk-Roth 1855-75).

${CONV}

INPUTS for headword KEY (read both):
  ${IN}\\KEYFILE.raw.txt        — the RAW German PWG record(s); the FULL sense text to translate (numbered 1)/2) senses, lettered a)/b) sub-senses; {%German%}, {#Sanskrit#}, <ls>sources</ls>, <ab>abbrev</ab>, <lex>grammar</lex>)
  ${IN}\\KEYFILE.portrait.json  — the parsed structure + EVIDENCE: per sense its equivalence_type, citations resolved to full source names + stratum, grammar/diasystem labels; and corpus_synonyms = the Russian ACTUALLY ATTESTED in the parallel corpus for this headword, by stratum (by_stratum) + a freq-ranked candidate set (candidates).

TASK: for EACH record (homonym) and EACH sense/sub-sense in the tree, write the Russian rendering.
- Use the corpus candidates as the PRIMARY evidence for word choice (they are attested, 84% precision; translation-weighted). Where SEVERAL near-synonyms fit, DISCRIMINATE them à la Apresjan: pick the one(s) right for THIS sense and state the differentia (semantic / combinatorial / stratum-connotational) briefly. Prefer renderings attested in the sense's CITED stratum (a ṚV-cited sense → the Vedic corpus renderings).
- Mark equivalence_type: a 1-2 word equivalent vs an explanatory gloss (толкование).
- Keep the German sense beside your Russian (side-by-side).

HARD RULES (the judge fails the card otherwise):
1. NO FABRICATION — never output a sense, sub-sense, or tag that is not an actual division in the raw German. Tags must match the raw exactly; do not invent, split, or merge senses (no added "epic"/"vedic" sub-sense the source lacks).
2. COMPLETE COVERAGE — render EVERY sense the raw card contains, in order: every numbered 1)/2), every lettered a)/b) sub-sense, AND any etymology / cross-reference / "personif." note (render the note too, with a short Russian gloss). Skip nothing.
3. SIGLA UNTOUCHED — never translate or transliterate ANY siglum or abbreviation, including COMMENTATOR sigla (Sāy., Schol., Sch., Comm.) and grammar abbrevs (m./f./Pl./Du.); they stay verbatim in PWG form. Let no German or English word leak into the Russian.
4. ALL RECORDS, INCLUDING NACHTRÄGE — a headword is often a MAIN record plus one or more ADDENDA/NACHTRÄGE records (each marked in the raw input). These do not repeat the word; they PATCH the main entry — "to sense 3 add citation X", "sense 10: read … instead of …", an etymology tail, a new astrological/numeric sense. Render EVERY record completely and EVERY addendum in full, including its tail (etymology, cross-reference, corrigendum). Addenda are first-class — never drop, summarise, or truncate them. Key each addendum sense to the main-entry sense number it patches.

Return ONLY the structured object.`

const CARD = {
  type: 'object', additionalProperties: false,
  properties: {
    key1: { type: 'string' }, iast: { type: 'string' },
    records: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          h: { type: 'string' },
          grammar: { type: 'string', description: 'POS/gender as PWG (m./f./n./…), verbatim' },
          senses: {
            type: 'array',
            items: {
              type: 'object', additionalProperties: false,
              properties: {
                tag: { type: 'string' },
                german: { type: 'string', description: 'the PWG German for this sense (trimmed, sigla kept)' },
                russian: { type: 'string', description: 'the Russian rendering (scholarly; sigla/abbrevs kept)' },
                equivalence_type: { enum: ['equivalent', 'explanatory'] },
                source_type: { enum: ['attested', 'lexicographic', 'mixed'] },
                stratum: { type: 'string', description: 'stratum used (Vedic/Epic/Classical/Medieval or empty)' },
                differentia: { type: 'string', description: 'Apresjan note when discriminating near-synonyms, else empty' },
              },
              required: ['tag', 'german', 'russian', 'equivalence_type', 'source_type', 'stratum', 'differentia'],
            },
          },
        },
        required: ['h', 'grammar', 'senses'],
      },
    },
    notes: { type: 'string' },
  },
  required: ['key1', 'iast', 'records', 'notes'],
}

const JUDGE = {
  type: 'object', additionalProperties: false,
  properties: {
    key1: { type: 'string' },
    ok: { type: 'boolean' },
    severity: { type: 'integer', description: '1 best … 5 worst' },
    register_ok: { type: 'boolean' },
    sigla_kept: { type: 'boolean', description: 'sources + grammar abbrevs left verbatim, NOT translated' },
    coverage_ok: { type: 'boolean', description: 'every PWG sense rendered' },
    corpus_used: { type: 'boolean' },
    discrimination_quality: { enum: ['strong', 'adequate', 'weak', 'missing'] },
    issues: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: { severity: { type: 'integer' }, detail: { type: 'string' } },
        required: ['severity', 'detail'],
      },
    },
    note: { type: 'string' },
  },
  required: ['key1', 'ok', 'severity', 'register_ok', 'sigla_kept', 'coverage_ok', 'corpus_used', 'discrimination_quality', 'issues', 'note'],
}

phase('Translate')
const out = await pipeline(
  CARDS,
  k => agent(TR.replace(/KEYFILE/g, safeName(k)).replace(/KEY/g, k), { label: `tr:${k}`, phase: 'Translate', schema: CARD, model: 'sonnet' }),
  (card, k) => {
    if (!card) return { key: k, card: null, judge: null }
    return agent(`You are the Opus QA judge for the pwg_ru pilot. Review this translated card against the conventions and the source.

${CONV}

You may re-read the source: ${IN}\\${safeName(k)}.raw.txt and ${IN}\\${safeName(k)}.portrait.json.

Check: (1) Russian correctness vs the German; (2) scholarly-philological register; (3) sigla + grammar abbreviations kept VERBATIM (not translated/transliterated) — fail sigla_kept if any ṚV./MBH./m./f. was rendered into Russian; (4) per-sense near-synonym discrimination quality (real Apresjan differentiae, not a flat list); (5) corpus evidence actually used; (6) coverage — every PWG sense rendered. severity 1=publishable … 5=broken.

TRANSLATED CARD (JSON):
${JSON.stringify(card).slice(0, 12000)}`,
      { label: `judge:${k}`, phase: 'Judge', schema: JUDGE, model: 'opus' })
      .then(j => ({ key: k, card, judge: j }))
  }
)

return { results: out.filter(Boolean) }
