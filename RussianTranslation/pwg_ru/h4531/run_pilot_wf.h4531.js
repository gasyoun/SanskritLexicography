// AUTO-DERIVED v2 (batched + masked, canonical output) from run_pilot_wf.js - root=d_a.
// Several masked cards per agent call; {Tn} restored to source markup in-JS so the
// returned result is a canonical wf_output.json. See TLONLY_PROTOTYPE.md.
export const meta = {
  name: 'pwgru-opt2-d_a',
  description: 'batched+masked translation-only PWG->Russian; amortized per-call overhead + masked I/O, {Tn} restored in-JS to canonical cards',
  phases: [{ title: 'Translate', detail: 'Sonnet: N masked cards per call -> rich cards; {Tn} restored to markup' }],
}

const CONV_TR = "You are producing the Russian scholarly entry for one PWG headword (Petersburg Sanskrit Dictionary, B\u00f6htlingk-Roth 1855-75).\n\npwg_ru CONVENTIONS (from B\u00f6htlingk-Roth's own prefaces + project decisions \u2014 follow EXACTLY):\n- REGISTER: scholarly-philological. Faithful to PWG's density and precision; this is a printed scholarly dictionary.\n- Translate into Russian the natural-language gloss prose. This is German in PWG/PW/SCH/PWKVN and most NWS sub-sources, but the NWS layer ALSO carries English (MW, Olivelle, Keller, Hoernle, BHSD, Sircar) and French (Renou, Padoux, Caland, Rivelex) glosses \u2014 translate each gloss FROM ITS OWN language, never relayed through German. A gloss given in two/three languages (e.g. \"riz cuit; cooked rice; gekochter Reis\") is ONE sense \u2014 render it once, not thrice (Guard 7).\n- KEEP VERBATIM (never translate or transliterate): Sanskrit (IAST / Devanagari); the literary-source sigla (\u1e5aV., MBH., M., AK., H., \u2026); the German grammatical abbreviations (m., f., n., Pl., Du., adj., \u2026); the German lexicographic/meta abbreviations inside <ab>\u2026</ab> (Bed. = Bedeutung, Schol., s.v., u.s.w. \u2014 keep the token, NEVER expand it to its Russian meaning); and <is>\u2026</is> italic source text (a source/siglum reference \u2014 keep verbatim, NEVER wrap as {%\u2026%} German gloss). They stay in PWG's Latin/German form.\n- TWO-SOURCE PRINCIPLE (B&R's own): a sense backed by a TEXT citation (\u1e5aV, MBH, M, \u2026) is demonstrable usage = attested; a sense from a ko\u015ba/grammarian only (Amarako\u015ba AK, Hemacandra H, P\u0101\u1e47ini P, Medin\u012b Med.) is Indian-lexicographic \u2014 render it but mark source_type=lexicographic.\n- VEDIC senses are 19th-c. European philology and may be superseded; render faithfully; if the German itself hedges, keep the hedge.\n\nINPUTS for each headword are INLINED below per card (its masked German skeleton + portrait). Do NOT open files, do NOT call any tools, do NOT list directories, do NOT supply senses from memory \u2014 translate EXACTLY what is inlined, nothing else.\n\nTASK: for EACH record (homonym) and EACH sense/sub-sense in the tree, write the Russian rendering.\n- Use the corpus candidates as the PRIMARY evidence for word choice (they are attested, 84% precision; translation-weighted). Where SEVERAL near-synonyms fit, DISCRIMINATE them \u00e0 la Apresjan: pick the one(s) right for THIS sense and state the differentia (semantic / combinatorial / stratum-connotational) briefly. Prefer renderings attested in the sense's CITED stratum (a \u1e5aV-cited sense \u2192 the Vedic corpus renderings). EVIDENCE WEIGHT: if the portrait's corpus_synonyms carries evidence_scope='prefixed-form' or 'root', the candidates are direct evidence for THIS headword \u2014 use them as primary. If evidence_scope starts with 'root-fallback' (a split prefixed-verb sub-card whose own surface form is not in the corpus), the candidates are the BARE ROOT's \u2014 treat them as a weak hint only and let the German gloss of the prefixed verb govern; do not force a root-meaning synonym onto a prefix that has shifted the sense.\n- Mark equivalence_type: a 1-2 word equivalent vs an explanatory gloss (\u0442\u043e\u043b\u043a\u043e\u0432\u0430\u043d\u0438\u0435).\n- Keep the German sense beside your Russian (side-by-side).\n\nHARD RULES (the judge fails the card otherwise):\n1. NO FABRICATION \u2014 never output a sense, sub-sense, or tag that is not an actual division in the raw German. Tags must match the raw exactly; do not invent, split, or merge senses (no added \"epic\"/\"vedic\" sub-sense the source lacks).\n2. COMPLETE COVERAGE \u2014 render EVERY sense the raw card contains, in order: every numbered 1)/2), every lettered a)/b) sub-sense, AND any etymology / cross-reference / \"personif.\" note (render the note too, with a short Russian gloss). Skip nothing.\n3. SIGLA UNTOUCHED \u2014 never translate or transliterate ANY siglum or abbreviation, including COMMENTATOR sigla (S\u0101y., Schol., Sch., Comm.), grammar abbrevs (m./f./Pl./Du.), and German lexicographic/meta abbreviations inside <ab>\u2026</ab> (Bed., Schol., s.v.) \u2014 keep the abbreviation token verbatim, NEVER expand it (e.g. <ab>Bed.</ab> stays \u00abBed.\u00bb, not \u00ab\u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0435\u043c\u00bb). <is>\u2026</is> italic source text is a verbatim siglum, NEVER {%\u2026%} gloss (do not render <is> inside {%\u2026%}). They stay verbatim in PWG form; let no German or English word leak into the Russian. MARKUP DELIMITERS VERBATIM: in the german field reproduce the raw record's own delimiters EXACTLY \u2014 keep every {#\u2026#} around Sanskrit and every <ls>\u2026</ls>, <ab>\u2026</ab>, <lex>\u2026</lex>, <is>\u2026</is> tag as-is; do NOT strip them to plain text, do NOT transliterate {#\u2026#} to bare IAST, do NOT \"clean\"/\"trim\" the markup. Keep any Sanskrit you cite in the russian field wrapped in {#\u2026#} too. The deterministic fidelity gate counts these tokens: a card that loses >10% of its <ls> or >15% of its {#\u2026#} spans is REJECTED.\n4. ALL RECORDS, INCLUDING NACHTR\u00c4GE \u2014 a headword is often a MAIN record plus one or more ADDENDA/NACHTR\u00c4GE records (each marked in the raw input). These do not repeat the word; they PATCH the main entry \u2014 \"to sense 3 add citation X\", \"sense 10: read \u2026 instead of \u2026\", an etymology tail, a new astrological/numeric sense. Render EVERY record completely and EVERY addendum in full, including its tail (etymology, cross-reference, corrigendum). Addenda are first-class \u2014 never drop, summarise, or truncate them. Key each addendum sense to the main-entry sense number it patches. One addendum can itself carry SEVERAL numbered patch-items (1a, 2a, 3a, \u2026) \u2014 render EVERY item; dropping any single patch fails coverage.\n5. NWS LAYER \u2014 USE THE AUTHORITATIVE PRE-PARSED OWNER MAP. The input contains a section \"=== LAYER: NWS \u2014 PRE-PARSED OWNER MAP (AUTHORITATIVE, N entries) ===\" listing numbered entries  N. [NWS: OWNER] {#lemma#} [tag] gloss . Emit EXACTLY ONE NWS card row per numbered entry, IN THAT ORDER; copy each entry's [NWS: OWNER] token VERBATIM as that row's LAST citation; translate the gloss from its own language; keep {#lemma#}/IAST/sigla. Do NOT re-derive, swap, merge, drop, or re-order owners, and do NOT read owners off the raw fragment \u2014 the map is the single source of truth (this makes the F12 slide impossible). If no owner map is present, fall back to: ONE ENTRY PER SOURCE, OWNER-CITATION KEPT (the deterministic auditor nws_split.py checks this; it fails the card otherwise). The \"=== LAYER: NWS ===\" fragment packs many sub-dictionaries into one string in the shape  [LEMMA] TAG > gloss .. OWNER : page >  [LEMMA] TAG > gloss .. OWNER : page > \u2026  \u2014 the diasystem TAG PRECEDES each gloss and the OWNER citation (Author year : page, e.g. \"Gra\u00dfmann 1873 (1996) : 70\", \"Geldner 1907 : 10\", \"MW : 47 (s.v. ap)\") CLOSES it. Output ONE sense per such entry, in source order: NEVER merge two owners into one, never drop the owner, and never compress several \"Wasser=water\" attestations into a single row. Each NWS sense MUST (a) be tagged so it reads as NWS (prefix \"[NWS:]\" or tag \"NWS\"), and (b) keep its OWNER citation VERBATIM as the LAST citation of that sense (so the auditor can read the owner). CRITICAL reading direction (failure F12): the owner comes AFTER the gloss \u2014 do NOT slide it onto the next gloss; \"X > Y : p\" means Y:p owns X, not the following entry. Sub-lemmas the NWS lists (separate compound headwords, e.g. apa\u1e25sa\u1e43varta, abdurga) are first-class entries too \u2014 render each as its own NWS row, never as a sense of the head.\n6. TRANSLATE, DON'T ANNOTATE \u2014 render EXACTLY what the German states, no more. Within a sense, NEVER add an interpretive gloss, a parenthetical domain clarification, a scope qualifier, or a scholarly attribution (\u00ab\u0438 \u0434\u0440\u0443\u0433\u0438\u043c\u0438\u00bb, \u00ab\u0438 \u0442\u043e\u043c\u0443 \u043f\u043e\u0434\u043e\u0431\u043d\u043e\u0435\u00bb, \u00ab(\u043e \u043d\u0435\u0431\u0435\u0441\u043d\u044b\u0445 \u0442\u0435\u043b\u0430\u0445)\u00bb) that the German does not itself contain. If the German credits a derivation to ONE authority (e.g. \u00abwird von BENFEY \u2026 zur\u00fcckgef\u00fchrt\u00bb), name ONLY that authority \u2014 do NOT generalise \u00abBENFEY\u00bb to \u00abBENFEY \u0438 \u0434\u0440\u0443\u0433\u0438\u043c\u0438\u00bb. When unsure, translate LESS, not more: an unsourced addition is a fidelity defect exactly like an omission.\n7. GOVERNMENT MARKERS VERBATIM \u2014 when the German gloss carries a parenthesized case-government note (e.g. `(<ab>loc.</ab>)`, `(<ab>loc.</ab> und <ab>gen.</ab>)`) or a `mit dem <ab>case.</ab>` phrase, copy the case abbreviation into the sense's `government` field exactly as it appears in the source (one entry per marker found) \u2014 NEVER invent, guess, generalize, or add a case the German does not state. Leave `government` an empty array when the German carries no such marker. This is deterministic \u2014 do not paraphrase the case into the Kochergina idiom or any other rendering.\n8. NO GERMAN PROSE IN CITATION SCAFFOLDING (H1302) \u2014 a German prose function word that JOINS citations or notes must be TRANSLATED into Russian, not kept: \u00abSchol. zu X\u00bb \u2192 \u00abSchol. \u043a X\u00bb, \u00abbei X\u00bb \u2192 \u00ab\u0443 X\u00bb, \u00abX und Y\u00bb \u2192 \u00abX \u0438 Y\u00bb, \u00abmit Erg\u00e4nzung von Z\u00bb \u2192 \u00ab\u0441 \u0432\u043e\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435\u043c Z\u00bb, a section-header \u00abMit {#prefix#}\u00bb \u2192 \u00ab\u0421 {#prefix#}\u00bb. Only the <ab>\u2026</ab>/<ls>\u2026</ls>/<is>\u2026</is> siglum TOKEN itself stays verbatim (rule 3) \u2014 the connective prose around it becomes Russian. This applies INSIDE citations too, where German zu/bei/und/oder/nach/im/so/als commonly survive untranslated.\n9. RUSSIAN STYLE MECHANICS (H1305) \u2014 NO LETTER \u0401 anywhere in the russian field: write \u0435 everywhere (\u00ab\u043e\u0442\u0432\u043e\u0451\u0432\u044b\u0432\u0430\u0442\u044c\u00bb \u2192 \u00ab\u043e\u0442\u0432\u043e\u0435\u0432\u044b\u0432\u0430\u0442\u044c\u00bb); the ONLY exception is the standalone word \u00ab\u0432\u0441\u0451\u00bb (used to disambiguate from \u00ab\u0432\u0441\u0435\u00bb \u2014 never in a compound like \u00ab\u0432\u0441\u0451-\u0442\u0430\u043a\u0438\u00bb, which stays \u00ab\u0432\u0441\u0435-\u0442\u0430\u043a\u0438\u00bb like every other \u0451-word). In editorial/apparatus metalanguage write the TERSE forms \u00ab\u0432\u043c.\u00bb instead of \u00ab\u0432\u043c\u0435\u0441\u0442\u043e\u00bb and \u00ab\u0432 \u0437\u043d\u0430\u0447.\u00bb instead of \u00ab\u0432 \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0438\u00bb (this is about editorial commentary \u2014 variant readings, sense specification \u2014 not about narrative gloss prose, which stays natural Russian). `ed. Bomb.` stays the verbatim Latin siglum wherever it sits inside `<ls>\u2026</ls>` (rule 3, sigla untouched) \u2014 NEVER translate it there (it feeds src/pwg_sources.py's citation resolver); only a free-prose `ed. Bomb.` OUTSIDE any `<ls>\u2026</ls>` tag becomes \u00ab\u0411\u043e\u043c\u0431\u0435\u0439\u0441\u043a\u0430\u044f \u0440\u0435\u0434.\u00bb.\n\nRENDERING GUIDANCE \u2014 Sanskrit microstructure (from the lexicography-manual harvest, see ../glossaries/de_ru_translation_aids.md; quality, judged softly \u2014 these refine wording, they do NOT add/drop senses):\n- COMPOUNDS (sam\u0101sa) are right-headed: build the Russian off the vigraha, head = the SECOND member. tatpuru\u1e63a asi-kalaha \u2192 \u00ab\u0431\u043e\u0439 \u043c\u0435\u0447\u043e\u043c\u00bb (head \u00ab\u0431\u043e\u0439\u00bb); NEVER a member-by-member calque off the first constituent. bahuvr\u012bhi is exocentric (a possessor OUTSIDE the compound): hata-putra- \u2192 \u00ab\u0442\u0430, \u0443 \u043a\u043e\u0433\u043e \u0443\u0431\u0438\u0442\u044b \u0441\u044b\u043d\u043e\u0432\u044c\u044f / \u0447\u044c\u0438 \u0441\u044b\u043d\u043e\u0432\u044c\u044f \u0443\u0431\u0438\u0442\u044b\u00bb, not the literal sum. \u2026-\u0101di / \u2026-prabh\u1e5bti = an OPEN class = the hypernym of its members \u2192 \u00abX \u0438 \u0442\u043e\u043c\u0443 \u043f\u043e\u0434\u043e\u0431\u043d\u043e\u0435 / \u0438 \u043f\u0440\u043e\u0447\u0435\u0435\u00bb, never a closed list. Split an over-long stacked compound into several Russian clauses, not one calque (Apte/Gillon, Inglese-Geupel).\n- CORRELATIVES (yad\u2026tad): when the German keeps the correlative order, render a PREPOSED Russian correlative \u2014 \u043a\u0442\u043e\u2026\u0442\u043e\u0442, \u0447\u0442\u043e\u2026\u0442\u043e, \u043a\u0430\u043a\u043e\u0439\u2026\u0442\u0430\u043a\u043e\u0439, \u0447\u0435\u0439\u2026\u0442\u043e\u0433\u043e, \u0433\u0434\u0435\u2026\u0442\u0430\u043c, \u043a\u0443\u0434\u0430\u2026\u0442\u0443\u0434\u0430, \u043a\u043e\u0433\u0434\u0430\u2026\u0442\u043e\u0433\u0434\u0430, \u043a\u0430\u043a\u2026\u0442\u0430\u043a, \u0441\u043a\u043e\u043b\u044c\u043a\u043e\u2026\u0441\u0442\u043e\u043b\u044c\u043a\u043e, \u0447\u0435\u043c\u2026\u0442\u0435\u043c. Doubled yo ya\u1e25 \u2192 \u00ab\u043a\u0442\u043e \u0431\u044b \u043d\u0438 / \u0432\u0441\u044f\u043a\u0438\u0439, \u043a\u0442\u043e\u00bb; y\u0101vat\u2026t\u0101vat \u2192 \u00ab\u043f\u043e\u043a\u0430\u2026\u0434\u043e \u0442\u0435\u0445 \u043f\u043e\u0440\u00bb; yadi\u2026tarhi \u2192 \u00ab\u0435\u0441\u043b\u0438\u2026\u0442\u043e\u00bb. Keep BOTH pairs; do not flip which clause is asserted (Mitrenina, Zaliznyak-Paducheva, Ruppel).\n- \u015a\u0100STRIC FORMULAS \u2014 fixed dry Russian, do not re-translate per occurrence: iti artha\u1e25 \u2192 \u00ab\u0442\u043e \u0435\u0441\u0442\u044c; \u0442\u0430\u043a\u043e\u0432 \u0441\u043c\u044b\u0441\u043b\u00bb; ity uktam \u2192 \u00ab\u0441\u043a\u0430\u0437\u0430\u043d\u043e\u00bb; anena \u2026 vivak\u1e63itam \u2192 \u00ab\u044d\u0442\u0438\u043c \u043e\u043d \u0445\u043e\u0447\u0435\u0442 \u0441\u043a\u0430\u0437\u0430\u0442\u044c\u00bb; X-bh\u0101va\u1e25 / X-tvam \u2192 \u00ab\u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435/\u0441\u0432\u043e\u0439\u0441\u0442\u0432\u043e X\u00bb. Their presence marks scholastic register \u2192 flat terminological Russian (Tubb).\n- SYNONYM CARDINALITY: render a German synonym-string (Glanz, Schimmer, Pracht) as a Russian synonym-string of EQUAL cardinality \u2014 never collapse n near-synonyms to one word; pick by register, default to the neutral dominant (Apresjan, Baalbaki).\n- PUNCTUATION carries sense-grouping: comma = interchangeable synonyms WITHIN one sense; semicolon = a boundary between non-interchangeable senses. Preserve PWG's comma/semicolon exactly in the Russian (Hartmann & James).\n- MANNER/POSITION: where Russian grammatically forces a manner/position verb (\u0438\u0434\u0442\u0438/\u043f\u043e\u043b\u0437\u0442\u0438/\u043b\u0435\u0442\u0435\u0442\u044c; \u0441\u0442\u043e\u044f\u0442\u044c/\u043b\u0435\u0436\u0430\u0442\u044c/\u0432\u0438\u0441\u0435\u0442\u044c) that the German leaves open, choose from the cited context; a wrong neutral default (e.g. \u00ab\u043d\u0430\u0445\u043e\u0434\u0438\u0442\u044c\u0441\u044f\u00bb, \u00ab\u043b\u0435\u0436\u0430\u0442\u044c\u00bb for something that hangs) is grammatical-but-false (Apresjan).\n- NON-CIRCULAR GLOSSES: a Russian gloss must be clearer than the Sanskrit/PWG headword. Avoid circular or cryptographic paraphrases, bare transliterated Sanskrit, or a rarer Russian term where a plain explanatory gloss is needed (Apresjan).\n\nReturn ONLY the structured object."
const PREAMBLE = "=== TASK SHAPE (read first) ===\nThis is a self-contained, read-only text-transformation task, complete in a single turn.\nEverything it needs is inline below: there is no repository to explore, no file to open or\nwrite, no command to run, and nothing outside this message is consulted or modified. The\ndeliverable is exactly the structured result described by the response schema \u2014 returning\nthat result IS the completion of this task. Nothing here is a proposal awaiting approval, so\nno planning step, clarifying question, or approval round applies to it.\n\n=== MASKED + BATCHED REGIME (read first \u2014 overrides input-format details below) ===\nYou are given SEVERAL headwords at once, each in its own '=== CARD <key> ===' block.\nEach card's source German has been MASKED: every untranslatable span (Sanskrit {#..#},\nsource refs <ls>, abbreviations <ab>, italic <is>, grammar <lex>) is replaced by a {Tn}\nplaceholder token. You see ONLY the translatable German gloss prose + {Tn} tokens + the\nsense numbering. A Python post-step restores every {Tn} to its exact original markup.\n\nTherefore, wherever the rules below say \"keep {#..#}/<ls>/<ab> verbatim\" or \"reproduce\nthe markup delimiters EXACTLY\", that now means: **keep every {Tn} placeholder verbatim,\nunchanged and in its original order** \u2014 never invent, renumber, drop, expand, merge, or\nalter a {Tn}, and never type any Sanskrit, siglum, or markup yourself. In the `german`\nfield, reproduce the masked skeleton you were given for that sense EXACTLY (its German +\nits {Tn} tokens). In the `russian` field, put your translation, placing the relevant {Tn}\ntokens where the source cited a masked span. Translate EACH card; return one object per\nheadword in `cards`, with `key1` matching its '=== CARD <key> ===' header. Omit nothing.\n\n=== GLOSS WRAPPERS {%\u2026%} \u2014 PRESERVE THE WRAPPER ===\nA German span wrapped as {%\u2026%} in the source is a lexicographic gloss marker (the GAPS \u00a717\nGLOSS-DE-RESIDUE convention). The wrapper is markup, not decoration: EVERY {%\u2026%} span in a\ncard's source MUST reappear in your translation as {%\u2026%} around its translated gloss in the\n`russian` field. Never drop the wrapper, never replace it with \u00ab\u2026\u00bb quotes, never leave the\nGerman word untranslated inside it.\nWorked example \u2014 DE `a\u3009 {%ein%} <is>Arhant</is> <ls>H. 25</ls>.` becomes\nRU `\u0430) {%\u043d\u0435\u043a\u0438\u0439%} <is>Arhant</is> <ls>H. 25</ls>.`. As masked input the same sense reads\n`a\u3009 {%ein%} {T1} {T2}.` and your translation must read `\u0430) {%\u043d\u0435\u043a\u0438\u0439%} {T1} {T2}.` \u2014 the\n{Tn} tokens verbatim, the {%\u2026%} wrapper kept around the translated gloss.\nThis rule applies ONLY to {%\u2026%} spans you can SEE in your masked source. A {Tn} masked span\nstays {Tn} VERBATIM in both fields \u2014 never translate it, never wrap it in {%\u2026%} or any other\nmarkup, never reconstruct its content; the deterministic post-step restores the original\nspan exactly.\n\n"
const GRAMMAR = ""
const GRAMMARS = {"d_a~~h12_00_pwg00": "", "d_a~~h5_00_pwg00": "", "d_a~~h7_00_pwg00": "", "d_a~~h9_05_samup_a": "", "d_a~~h0_06_a_bi": "", "d_a~~h8_00_pwg00": "", "d_a~~h0_03_sec_3": "", "d_a~~h2_09_pari_ri": "", "d_a~~h0_27_pari_ri": "", "d_a~~h0_33_atipra": "", "d_a~~h0_21_apavy_a": "", "d_a~~h2_01_api": "", "d_a~~h0_07_ava": "", "d_a~~h11_00_pwg00": "", "d_a~~h2_06_vyava": "", "d_a~~h0_29_nis": "", "d_a~~h9_06_vy_a": "", "d_a~~h2_03_a_byava": "", "d_a~~h0_09_anv_a": "", "d_a~~h0_13_ud_a": "", "d_a~~h0_15_a_byup_a": "", "d_a~~h2_05_paryava": "", "d_a~~h0_12_sama_by_a": "", "d_a~~h2_11_nis": ""}
// B02 (H1339): per-key display IAST (from the portrait sidecars, ONE Python helper) so the
// heal-stitched card can be schema-complete at construction (iast/notes are CARD_REQUIRED).
const IASTS = {"d_a~~h12_00_pwg00": "d\u0101", "d_a~~h5_00_pwg00": "d\u0101", "d_a~~h7_00_pwg00": "d\u0101", "d_a~~h9_05_samup_a": "d\u0101", "d_a~~h0_06_a_bi": "abhid\u0101", "d_a~~h0_03_sec_3": "d\u0101", "d_a~~h2_09_pari_ri": "d\u0101", "d_a~~h0_27_pari_ri": "d\u0101", "d_a~~h0_33_atipra": "d\u0101", "d_a~~h0_21_apavy_a": "d\u0101", "d_a~~h2_01_api": "d\u0101", "d_a~~h0_07_ava": "d\u0101", "d_a~~h11_00_pwg00": "d\u0101", "d_a~~h2_06_vyava": "d\u0101", "d_a~~h0_29_nis": "d\u0101", "d_a~~h9_06_vy_a": "d\u0101", "d_a~~h2_03_a_byava": "d\u0101", "d_a~~h0_09_anv_a": "d\u0101", "d_a~~h0_13_ud_a": "d\u0101", "d_a~~h0_15_a_byup_a": "d\u0101", "d_a~~h2_05_paryava": "d\u0101", "d_a~~h0_12_sama_by_a": "d\u0101", "d_a~~h2_11_nis": "d\u0101"}
const NWS_RULE = ""
const CARDS_SCHEMA = {"type": "object", "additionalProperties": false, "required": ["cards"], "properties": {"cards": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/card"}}}, "$defs": {"card": {"type": "object", "additionalProperties": false, "required": ["key1", "iast", "records", "notes"], "properties": {"key1": {"type": "string", "minLength": 1}, "iast": {"type": "string"}, "records": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/record"}}, "notes": {"type": "string"}}}, "record": {"type": "object", "additionalProperties": false, "required": ["h", "grammar", "senses"], "properties": {"h": {"type": "string"}, "grammar": {"type": "string", "description": "POS/gender as PWG, verbatim where applicable."}, "senses": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/sense"}}}}, "sense": {"type": "object", "additionalProperties": false, "required": ["tag", "german", "russian"], "properties": {"tag": {"type": "string", "minLength": 1}, "german": {"type": "string", "description": "The PWG German for this sense, with the source's {#\u2026#} Sanskrit delimiters and <ls>/<ab>/<lex>/<is> markup kept VERBATIM \u2014 not stripped to plain text, not transliterated to bare IAST."}, "russian": {"type": "string", "description": "The Russian rendering in scholarly register."}, "equivalence_type": {"enum": ["equivalent", "explanatory"]}, "source_type": {"enum": ["attested", "lexicographic", "mixed"]}, "stratum": {"type": "string", "description": "Stratum used, such as Vedic, Epic / early-Classical, Classical, Medieval, or empty."}, "differentia": {"type": "string", "description": "Apresjan near-synonym discrimination note, or empty when no discrimination was needed."}}}}}
const BATCHES = [["d_a~~h12_00_pwg00"], ["d_a~~h5_00_pwg00"], ["d_a~~h7_00_pwg00"], ["d_a~~h9_05_samup_a"], ["d_a~~h0_06_a_bi"], ["d_a~~h0_03_sec_3"], ["d_a~~h2_09_pari_ri"], ["d_a~~h0_27_pari_ri"], ["d_a~~h0_33_atipra"], ["d_a~~h0_21_apavy_a"], ["d_a~~h2_01_api"], ["d_a~~h0_07_ava"], ["d_a~~h11_00_pwg00"], ["d_a~~h2_06_vyava"], ["d_a~~h0_29_nis"], ["d_a~~h9_06_vy_a"], ["d_a~~h2_03_a_byava"], ["d_a~~h0_09_anv_a"], ["d_a~~h0_13_ud_a"], ["d_a~~h0_15_a_byup_a"], ["d_a~~h2_05_paryava"], ["d_a~~h0_12_sama_by_a"], ["d_a~~h2_11_nis"]]
const INPUTS = {"d_a~~h12_00_pwg00": {"skeleton": "=== LAYER: PWG-ROOT HEAD homonym 13 \u2014 root=dA (simple verb + senses; same root_key) ===\n\n{T5}7.{T6} {T1}\u00a6 mit {T2} {T3} 7 lies {T4}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 0, "sk": 3, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h5_00_pwg00": {"skeleton": "=== LAYER: PWG-ROOT HEAD homonym 6 \u2014 root=dA (simple verb + senses; same root_key) ===\n\n{T5}6.{T6} {T1}\u00a6 (von {T7}5.{T8} {T2}) {T3} {%Schutz%} {T4}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 2, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h7_00_pwg00": {"skeleton": "=== LAYER: PWG-ROOT HEAD homonym 8 \u2014 root=dA (simple verb + senses; same root_key) ===\n\n{T5}8.{T6} {T1}\u00a6 (von {T7}7.{T8} {T2}) {T3} {%das Reinigen%} {T4}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 2, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h9_05_samup_a": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 10 \u2014 root=dA upasarga=samupA (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T3}\u2014 {T1} 1\u3009 {%to take%} {T2}", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root-fallback (prefixed form samupA+dA not in corpus \u2014 hint only, defer to the German gloss)\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 1, "senses": 1, "source_senses": 1, "nws": 0}, "d_a~~h0_06_a_bi": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 1 \u2014 root=dA upasarga=aBi (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T4}\u2014 {T1} {%geben%}: {T2} {T3}.", "portrait": "[{\"key1\": \"aBidA\", \"iast\": \"abhid\u0101\", \"evidence_scope\": \"prefixed-form\", \"corpus_synonyms\": {\"n\": 1, \"by_stratum\": {\"Classical\": [\"\u043d\u0430 \u0441\u0430\u043c\u043e\u043c \u0434\u0435\u043b\u0435\"]}, \"candidates\": [\"\u043d\u0430 \u0441\u0430\u043c\u043e\u043c \u0434\u0435\u043b\u0435\"]}}]", "ls": 1, "sk": 2, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h0_03_sec_3": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 1 \u2014 root=dA SECONDARY intens (caus./desid./intens. of the simple verb) ===\n\n{T6}\u2014 {T1} {T2} {T3}, {T4} {T5}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 2, "sk": 1, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h2_09_pari_ri": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 3 \u2014 root=dA upasarga=pariRi (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T5}\u2014 {T1}, {T2} {T3}, {T4}", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root-fallback (prefixed form pariRi+dA not in corpus \u2014 hint only, defer to the German gloss)\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 2, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h0_27_pari_ri": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 1 \u2014 root=dA upasarga=pariRi (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T5}\u2014 {T1}, {T2} {T3}, {T4}", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root-fallback (prefixed form pariRi+dA not in corpus \u2014 hint only, defer to the German gloss)\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 2, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h0_33_atipra": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 1 \u2014 root=dA upasarga=atipra (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T4}\u2014 {T1} {%hin\u00fcbergeben%}: {T2} {T3}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root-fallback (prefixed form atipra+dA not in corpus \u2014 hint only, defer to the German gloss)\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 2, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h0_21_apavy_a": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 1 \u2014 root=dA upasarga=apavyA (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T4}\u2014 {T1} {%\u00f6ffnen%}: {T2} {T3}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root-fallback (prefixed form apavyA+dA not in corpus \u2014 hint only, defer to the German gloss)\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 2, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h2_01_api": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 3 \u2014 root=dA upasarga=api (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T4}\u2014 {T1} {%abschneiden%}: {T2} {T3}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root-fallback (prefixed form api+dA not in corpus \u2014 hint only, defer to the German gloss)\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 2, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h0_07_ava": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 1 \u2014 root=dA upasarga=ava (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T6}\u2014 {T1}, {T2} {T3} {T4} zu {T5}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root-fallback (prefixed form ava+dA not in corpus \u2014 hint only, defer to the German gloss)\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 2, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h11_00_pwg00": {"skeleton": "=== LAYER: PWG-ROOT HEAD homonym 12 \u2014 root=dA (simple verb + senses; same root_key) ===\n\n{T8}4.{T9} {T1}\u00a6 mit {T2} {T3} {T4}.\n{T10}\u2014 {T5} {%l\u00f6sen%}: {T6} {T7}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 5, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h2_06_vyava": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 3 \u2014 root=dA upasarga=vyava (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T5}\u2014 {T1} {%vertheilen%}: {T2} {T3}. {T4}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root-fallback (prefixed form vyava+dA not in corpus \u2014 hint only, defer to the German gloss)\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 2, "sk": 2, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h0_29_nis": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 1 \u2014 root=dA upasarga=nis (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T7}\u2014 {T1}, {T2} {T3} {T4}, {T5} {T6}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root-fallback (prefixed form nis+dA not in corpus \u2014 hint only, defer to the German gloss)\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 2, "sk": 2, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h9_06_vy_a": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 10 \u2014 root=dA upasarga=vyA (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T7}\u2014 {T1}, {T2} und {T3} {T4} ohne {T5} {T6}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root-fallback (prefixed form vyA+dA not in corpus \u2014 hint only, defer to the German gloss)\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 4, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h2_03_a_byava": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 3 \u2014 root=dA upasarga=aByava (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T4}\u2014 {T1} {%dazu hin abtheilen%} {T2}. \u2014 Hierher geh\u00f6rt {T3}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root-fallback (prefixed form aByava+dA not in corpus \u2014 hint only, defer to the German gloss)\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 2, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h0_09_anv_a": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 1 \u2014 root=dA upasarga=anvA (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T5}\u2014 {T1} {T2} {%wieder an sich nehmen%}: {T3} {T4}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root-fallback (prefixed form anvA+dA not in corpus \u2014 hint only, defer to the German gloss)\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 2, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h0_13_ud_a": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 1 \u2014 root=dA upasarga=udA (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T6}\u2014 {T1} {%erheben%}: {T2} {T3}.\n{T7}\u2014 {T4} {T5}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root-fallback (prefixed form udA+dA not in corpus \u2014 hint only, defer to the German gloss)\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 3, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h0_15_a_byup_a": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 1 \u2014 root=dA upasarga=aByupA (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T4}\u2014 {T1} {%auflesen%}: {T2} {T3}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root-fallback (prefixed form aByupA+dA not in corpus \u2014 hint only, defer to the German gloss)\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 2, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h2_05_paryava": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 3 \u2014 root=dA upasarga=paryava (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T4}\u2014 {T1} {%ringsum St\u00fccke abtrennen%}: {T2} {T3}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root-fallback (prefixed form paryava+dA not in corpus \u2014 hint only, defer to the German gloss)\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 2, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h0_12_sama_by_a": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 1 \u2014 root=dA upasarga=samaByA (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T5}\u2014 {T1} {T2} {%zusammenfassen%}: {T3} {T4}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root-fallback (prefixed form samaByA+dA not in corpus \u2014 hint only, defer to the German gloss)\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 2, "senses": 0, "source_senses": 0, "nws": 0}, "d_a~~h2_11_nis": {"skeleton": "=== LAYER: PWG-ROOT SUBCARD homonym 3 \u2014 root=dA upasarga=nis (prefixed verb nested in the dA root article; root_key links it back) ===\n\n{T8}\u2014 {T1}, {T2} {T3} {T4}, {T5}\n{T9}\u2014 {T6} {T7}.", "portrait": "[{\"key1\": \"dA\", \"iast\": \"d\u0101\", \"evidence_scope\": \"root-fallback (prefixed form nis+dA not in corpus \u2014 hint only, defer to the German gloss)\", \"corpus_synonyms\": {\"n\": 194, \"by_stratum\": {\"Vedic\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0435\u0442 [\u044d\u0442\u0443 \u0436\u0438\u0437\u043d\u044c] \u0436\u0438\u0432\u043e\u043c\u0443\"], \"Epic / early-Classical\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0442\u044c\"], \"Classical\": [\"\u043f\u0440\u0435\u043f\u043e\u0434\u043d\u0435\u0441\u0442\u0438\", \"\u0432\u044b\u0434\u0430\u043d\u0430 \u0437\u0430\u043c\u0443\u0436\"], \"Medieval\": [\"\u0434\u0430\u0432\u0430\u0442\u044c\"]}, \"candidates\": [\"\u0434\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u043e\u0432\u0430\u0442\u044c\", \"\u043e\u0442\u0434\u0430\u0432\u0430\u0442\u044c\", \"\u043f\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0432\u044b\u0434\u0430\u0442\u044c\", \"\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u043e\u0434\u0430\u0440\u0438\u0442\u044c\", \"\u0434\u0435\u0440\u0436\u0430\u0442\u044c\", \"\u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c\", \"\u0434\u0430\u044f\u0442\u0435\u043b\u044c\"]}}]", "ls": 1, "sk": 3, "senses": 0, "source_senses": 0, "nws": 0}}
const PH = {"d_a~~h12_00_pwg00": ["{#dA#}", "{#ava#}", "<ab>Z.</ab>", "{#trIRyavadAtAni vi\u02da#}", "<hom>", "</hom>"], "d_a~~h5_00_pwg00": ["{#dA#}", "{#dA#}", "<lex>f.</lex>", "<ls>MED. d. 1</ls>", "<hom>", "</hom>", "<hom>", "</hom>"], "d_a~~h7_00_pwg00": ["{#dA#}", "{#dA#}", "<lex>f.</lex>", "<ls>MED. d. 1</ls>", "<hom>", "</hom>", "<hom>", "</hom>"], "d_a~~h9_05_samup_a": ["{#samupA#}", "<ls>BENFEY.</ls>", "<div n=\"p\">"], "d_a~~h0_06_a_bi": ["{#aBi#}", "{#aByadAt#}", "<ls>MBH. 3,13309</ls>", "<div n=\"p\">"], "d_a~~h0_03_sec_3": ["<ab>intens.</ab>", "{#dedIyate#}", "<ls>P. 6,4,66</ls>", "<ab>Sch.</ab>", "<ls>VOP. 20,4</ls>", "<div n=\"p\">"], "d_a~~h2_09_pari_ri": ["{#pariRi#}", "{#\u02dadyati#}", "<ls>P. 8,4,17</ls>", "<ab>Sch.</ab>", "<div n=\"p\">"], "d_a~~h0_27_pari_ri": ["{#pariRi#}", "{#\u02dadadAti#}", "<ls>P. 8,4,17</ls>", "<ab>Sch.</ab>", "<div n=\"p\">"], "d_a~~h0_33_atipra": ["{#atipra#}", "{#\u02dadAya#}", "<ls>L\u0100\u1e6cY. 5,9,5</ls>", "<div n=\"p\">"], "d_a~~h0_21_apavy_a": ["{#apavyA#}", "{#apavyAdAyOzWO#}", "<ls>\u015aAT. BR. 11,4,2,10</ls>", "<div n=\"p\">"], "d_a~~h2_01_api": ["{#api#}", "{#Bi\\nadmi^ mu\\zkAvapi^ dyAmi\\ Sepa^H#}", "<ls>AV. 4,37,7</ls>", "<div n=\"p\">"], "d_a~~h0_07_ava": ["{#ava#}", "<ab>partic.</ab>", "{#avadatta#}", "<is n=\"K\u0101rik\u0101\">K\u0101r.</is>", "<ls>P. 7,4,47</ls>", "<div n=\"p\">"], "d_a~~h11_00_pwg00": ["{#dA#}", "{#ni#}", "<ab>vgl.</ab>", "{#nidAtar, nidAna#}", "{#vi#}", "{#vyadyat, vi dyata^H#}", "<ls>TBR. 3,10,9,1</ls>", "<hom>", "</hom>", "<div n=\"p\">"], "d_a~~h2_06_vyava": ["{#vyava#}", "{#vyavadAyASnanti#}", "<ls>KAU\u015a. 66</ls>", "<ls n=\"KAU\u015a.\">68</ls>", "<div n=\"p\">"], "d_a~~h0_29_nis": ["{#nis#}", "<ab>partic.</ab>", "{#nirdatta#}", "<ls>P. 7,4,47</ls>", "<ab>Sch.</ab>", "<ls>VOP. 26,126</ls>", "<div n=\"p\">"], "d_a~~h9_06_vy_a": ["{#vyA#}", "{#\u02dadehi#}", "<ab>med.</ab>", "{#vyAdatta#}", "{#muKam#}", "<ls>BH\u0100G. P. 10,8,36</ls>", "<div n=\"p\">"], "d_a~~h2_03_a_byava": ["{#aByava#}", "<ls>\u015aAT. BR. 2,5,2,40</ls>", "{#aByavadAnya#}", "<div n=\"p\">"], "d_a~~h0_09_anv_a": ["{#anvA#}", "<ab>med.</ab>", "{#anvA 'ahaM tAM dAsye#}", "<ls>\u015aAT. BR. 2,1,2,16</ls>", "<div n=\"p\">"], "d_a~~h0_13_ud_a": ["{#udA#}", "{#u\\dA\\dAya^ pfTi\\vIm#}", "<ls>VS. 1,28</ls>", "<ab>Vgl.</ab>", "{#udAtta#}", "<div n=\"p\">", "<div n=\"v\">"], "d_a~~h0_15_a_byup_a": ["{#aByupA#}", "{#PalAni pAtayAmAsa \u2014 aByupAdAya visrabDo BakzayAmAsa#}", "<ls>MBH. 12,672</ls>", "<div n=\"p\">"], "d_a~~h2_05_paryava": ["{#paryava#}", "{#(puroqASam) sa\\ma\\ntaM pa\\ryava^dyati#}", "<ls>TS. 2,3,7,4</ls>", "<div n=\"p\">"], "d_a~~h0_12_sama_by_a": ["{#samaByA#}", "<ab>med.</ab>", "{#etAstejomAtrAH samaByAdadAnaH#}", "<ls>\u015aAT. BR. 14,7,2,1</ls>", "<div n=\"p\">"], "d_a~~h2_11_nis": ["{#nis#}", "<ab>partic.</ab>", "{#nirdita#}", "<ls>P. 7,4,40</ls>", "<ab>Sch.</ab>", "<ab>Vgl.</ab>", "{#nirdAtar#}", "<div n=\"p\">", "<div n=\"v\">"]}
const FRAGS = {}
const PHF = {}
const BINARY_SPLIT = true
const PRESPLIT = []
// Wall-clock kill gate (H155 follow-up). See FAILURE_MODES_AND_KILL_GATE_2026-07-04.md.
const KILL = true
const KILL_FACTOR = 2.0
const KILL_BASE_MS = 20000
const KILL_SLOPE_MS = 45
const KILL_FLOOR_MS = 45000
const KILL_CEIL_MS = 600000
// H189 live budget kill-switch, split after H442/H462: whole-card translation/binary-split
// and fragment recovery spend independent pools. One runaway recovery cascade can no longer
// consume the capacity required to attempt the remaining primary batches; the recovery pool
// is the sum of the per-card heal ceilings, so those card-level guards are reachable.
const KILL_SWITCH = true
const MAX_AGENTS = 79
const MAX_TRANSLATE_AGENTS = 79
const MAX_HEAL_AGENTS = 0
// H255/H811 low-width staggered dispatch: cap the concurrent translateBatch/healOnly units so
// a degraded generation API isn't hit ~10-wide (the Workflow runtime cap) — a tiny card that
// takes ~54s ALONE is inflated past the 180s kill CEIL under contention. 0 = unbounded.
const MAX_WIDE = 3
const STAGGER_MS = 2000
// H442 per-card heal budget: a per-card ceiling on heal agent() calls, threaded through
// healGroup's bisection recursion. Unlike MAX_AGENTS (a shared window pool), this stops ONE
// dense card from spending the whole window budget: once a card's own heal spend crosses
// ceil(nGroups * PER_CARD_HEAL_FACTOR) + PER_CARD_HEAL_HEADROOM, healGroup stops retrying/
// bisecting and returns the resolved fragments as a PARTIAL card (rest -> missing_fragments,
// targeted-requeue-able). A dense card thus fails fast + cheap, leaving budget for cards that
// can heal cleanly (H437: 3-4 dense cards were exhausting 61/61 agents, starving ~9 others).
const PER_CARD_HEAL_BUDGET = true
const PER_CARD_HEAL_FACTOR = 1.5
const PER_CARD_HEAL_HEADROOM = 3
// H442: a KILL-TIMEOUT must not drive healGroup's bisection. A soft/malformed failure
// still bisects (a bigger group is genuinely harder; halves may parse), but a killed group
// routes unresolved fragments straight to the cheap transient requeue instead of halving
// toward tiny fragments that hit the same 45s floor.
const KILL_TIMEOUT_NO_BISECT = true
// --tm: cards pre-resolved from the content-addressed translation memory (source-SHA hit).
// Emitted verbatim as canonical rows with tm:true and NO agent() call — their markup is
// already restored (they come from the promoted store), so they bypass restore/accept.
const TM_RESOLVED = {"d_a~~h8_00_pwg00": {"iast": "d\u0101", "key1": "d_a~~h8_00_pwg00", "notes": "", "records": [{"grammar": "", "h": "9", "senses": [{"differentia": "Nachtrag, \u043e\u0442\u0441\u044b\u043b\u0430\u044e\u0449\u0438\u0439 \u043a \u043e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u0441\u0442\u0430\u0442\u044c\u0435 7. d\u0101; \u0443\u043a\u0430\u0437\u044b\u0432\u0430\u0435\u0442 \u0434\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0435 \u0443\u043f\u043e\u0442\u0440\u0435\u0431\u043b\u0435\u043d\u0438\u0435.", "equivalence_type": "explanatory", "german": "<hom>1.</hom> {#dA#}\u00a6 [<ab>vgl.</ab> [Page3-0565]] <ab>Z.</ab> 7. {#datte#} auch <ls>PA\u00d1CAT. I,356.</ls><info n=\"rev\"/>", "russian": "<hom>1.</hom> {#dA#}\u00a6 [<ab>vgl.</ab> [Page3-0565]] <ab>Z.</ab> 7. {#datte#} \u0442\u0430\u043a\u0436\u0435 <ls>PA\u00d1CAT. I,356.</ls><info n=\"rev\"/>", "source_type": "attested", "stratum": "", "tag": "1"}]}]}}
// Conservative no-LLM lane for tiny cross-reference/supplement stubs that contain no
// translatable German gloss. These are accounted rows, not skipped keys.
const DEGENERATE_RESOLVED = {}
// --tm fragment reuse: FRAG_TM[k] mirrors FRAGS[k]'s group shape; each slot is either a
// cached fragment's ALREADY-RESTORED senses (served with NO agent() call inside selfHeal)
// or null (translate it). A fully-cached card heals at zero cost; a partial giant card
// re-runs only its still-missing fragments. Empty ({}) unless --tm found a fragment sidecar.
const FRAG_TM = {}
// Suggestion TM is advisory only: it may seed wording/evidence in the prompt, but it NEVER
// pre-resolves a card and therefore never changes tm_hits, batches, or agent accounting.
const SUGGEST_TM = {}
const META = {"schema_version": "pwg_ru.workflow_meta.v1", "generator": "gen_opt_harness2.batched-masked", "generated_at": "2026-09-11T02:58:27Z", "root": "d_a", "safe_root": "d~005fa", "lang": "ru", "gen_model": "claude-sonnet-5", "source_profile": null, "source_profiles": {"d_a~~h12_00_pwg00": "pwg_only", "d_a~~h5_00_pwg00": "pwg_only", "d_a~~h7_00_pwg00": "pwg_only", "d_a~~h9_05_samup_a": "pwg_only", "d_a~~h0_06_a_bi": "pwg_only", "d_a~~h8_00_pwg00": "pwg_only", "d_a~~h0_03_sec_3": "pwg_only", "d_a~~h2_09_pari_ri": "pwg_only", "d_a~~h0_27_pari_ri": "pwg_only", "d_a~~h0_33_atipra": "pwg_only", "d_a~~h0_21_apavy_a": "pwg_only", "d_a~~h2_01_api": "pwg_only", "d_a~~h0_07_ava": "pwg_only", "d_a~~h11_00_pwg00": "pwg_only", "d_a~~h2_06_vyava": "pwg_only", "d_a~~h0_29_nis": "pwg_only", "d_a~~h9_06_vy_a": "pwg_only", "d_a~~h2_03_a_byava": "pwg_only", "d_a~~h0_09_anv_a": "pwg_only", "d_a~~h0_13_ud_a": "pwg_only", "d_a~~h0_15_a_byup_a": "pwg_only", "d_a~~h2_05_paryava": "pwg_only", "d_a~~h0_12_sama_by_a": "pwg_only", "d_a~~h2_11_nis": "pwg_only"}, "mode": "nominal_masked", "nominal": true, "nominal_keymap": {"d_a~~h12_00_pwg00": "dA", "d_a~~h5_00_pwg00": "dA", "d_a~~h7_00_pwg00": "dA", "d_a~~h9_05_samup_a": "dA", "d_a~~h0_06_a_bi": "aBidA", "d_a~~h8_00_pwg00": "dA", "d_a~~h0_03_sec_3": "dA", "d_a~~h2_09_pari_ri": "dA", "d_a~~h0_27_pari_ri": "dA", "d_a~~h0_33_atipra": "dA", "d_a~~h0_21_apavy_a": "dA", "d_a~~h2_01_api": "dA", "d_a~~h0_07_ava": "dA", "d_a~~h11_00_pwg00": "dA", "d_a~~h2_06_vyava": "dA", "d_a~~h0_29_nis": "dA", "d_a~~h9_06_vy_a": "dA", "d_a~~h2_03_a_byava": "dA", "d_a~~h0_09_anv_a": "dA", "d_a~~h0_13_ud_a": "dA", "d_a~~h0_15_a_byup_a": "dA", "d_a~~h2_05_paryava": "dA", "d_a~~h0_12_sama_by_a": "dA", "d_a~~h2_11_nis": "dA"}, "grammar_layer": "nominal", "selected_keys": ["d_a~~h12_00_pwg00", "d_a~~h5_00_pwg00", "d_a~~h7_00_pwg00", "d_a~~h9_05_samup_a", "d_a~~h0_06_a_bi", "d_a~~h8_00_pwg00", "d_a~~h0_03_sec_3", "d_a~~h2_09_pari_ri", "d_a~~h0_27_pari_ri", "d_a~~h0_33_atipra", "d_a~~h0_21_apavy_a", "d_a~~h2_01_api", "d_a~~h0_07_ava", "d_a~~h11_00_pwg00", "d_a~~h2_06_vyava", "d_a~~h0_29_nis", "d_a~~h9_06_vy_a", "d_a~~h2_03_a_byava", "d_a~~h0_09_anv_a", "d_a~~h0_13_ud_a", "d_a~~h0_15_a_byup_a", "d_a~~h2_05_paryava", "d_a~~h0_12_sama_by_a", "d_a~~h2_11_nis"], "batches": [["d_a~~h12_00_pwg00"], ["d_a~~h5_00_pwg00"], ["d_a~~h7_00_pwg00"], ["d_a~~h9_05_samup_a"], ["d_a~~h0_06_a_bi"], ["d_a~~h0_03_sec_3"], ["d_a~~h2_09_pari_ri"], ["d_a~~h0_27_pari_ri"], ["d_a~~h0_33_atipra"], ["d_a~~h0_21_apavy_a"], ["d_a~~h2_01_api"], ["d_a~~h0_07_ava"], ["d_a~~h11_00_pwg00"], ["d_a~~h2_06_vyava"], ["d_a~~h0_29_nis"], ["d_a~~h9_06_vy_a"], ["d_a~~h2_03_a_byava"], ["d_a~~h0_09_anv_a"], ["d_a~~h0_13_ud_a"], ["d_a~~h0_15_a_byup_a"], ["d_a~~h2_05_paryava"], ["d_a~~h0_12_sama_by_a"], ["d_a~~h2_11_nis"]], "batch_count": 23, "rootmap_sha256": null, "input_hashes": {"d_a~~h12_00_pwg00": {"raw_sha256": "1499a08eaaab64266cfee10b52a8516c6d6b1e327c57bb3c6184ef497bb3efb6", "portrait_sha256": "8850687e29db8811b3de0d62fd95106d0baeec6de0bd6d13d4dd87c4117724e8"}, "d_a~~h5_00_pwg00": {"raw_sha256": "8d23972f0b3670cfe700c3e68cd8a4ab88cd7ab0746964564ce1fe52bfd25fdf", "portrait_sha256": "8850687e29db8811b3de0d62fd95106d0baeec6de0bd6d13d4dd87c4117724e8"}, "d_a~~h7_00_pwg00": {"raw_sha256": "263eadf110ffeb20c09fecdd0d5f1f4e22f3bde9dcef9ee266c80438b5dfb864", "portrait_sha256": "8850687e29db8811b3de0d62fd95106d0baeec6de0bd6d13d4dd87c4117724e8"}, "d_a~~h9_05_samup_a": {"raw_sha256": "22cbd9cb07f1e0e0c8464b50803f1fb96be354e8eb2399bf978c20c2355fd721", "portrait_sha256": "f1699e40df24cf26d9e6d85207f3b8c9762439015688aa8210878eb1452404a7"}, "d_a~~h0_06_a_bi": {"raw_sha256": "a7bdb811ef01404376758a5229a14459a19fea3f465c20d0164ffa912501d1d5", "portrait_sha256": "64a28cb5a263f8d6a832a4392fe6e1090c9379843551c34f1cb3bcb00610a9cd"}, "d_a~~h8_00_pwg00": {"raw_sha256": "a23ef4ce46b0174560bf5dca808b86ea3f711b762a42dd6d154282820990bba3", "portrait_sha256": "8850687e29db8811b3de0d62fd95106d0baeec6de0bd6d13d4dd87c4117724e8"}, "d_a~~h0_03_sec_3": {"raw_sha256": "a1d377dca52081867e15e772a00b1a5f74f72e659f5fefa66d914317eb53faf4", "portrait_sha256": "8850687e29db8811b3de0d62fd95106d0baeec6de0bd6d13d4dd87c4117724e8"}, "d_a~~h2_09_pari_ri": {"raw_sha256": "56bc9b680b93adb0042394c4cb02cf2d8b8bbe51cc4624308d7b4afec8ab8577", "portrait_sha256": "b75ba600e5feffec41c0d8726752f041d2ebe5939840bc53b09142f434bb197d"}, "d_a~~h0_27_pari_ri": {"raw_sha256": "d4e3d07f5ea53cd36a6028fb971520c20aece92c77211f64e7b0f9618d7b02eb", "portrait_sha256": "b75ba600e5feffec41c0d8726752f041d2ebe5939840bc53b09142f434bb197d"}, "d_a~~h0_33_atipra": {"raw_sha256": "2575d5fa85a7ba0835f3c6a49ffbac827230505791d6b6df5d01b8aed5c6ceb5", "portrait_sha256": "964970636dfa590aa6b5247be0f201a7710101188fd26c98182b6fd5f74eaf3d"}, "d_a~~h0_21_apavy_a": {"raw_sha256": "b03640442581c0b38e4f89012de8907a2d6ecf57477b1955970dc332234e7f49", "portrait_sha256": "bba9250a62427c8d76d7ae71076587cf5fad177956c64e4e70c1a816c3cf0d75"}, "d_a~~h2_01_api": {"raw_sha256": "29da1567c1c96ca14e9f3bc974adb44f26cd9e61ed540f9d72a6ed7bfb8f33eb", "portrait_sha256": "7e1d041299a2fe0cb9999a02b6cf3de6f61a6f697b0949fa3b47e50d2a598589"}, "d_a~~h0_07_ava": {"raw_sha256": "a98a3d7494b1697fcea75d5ec0ae311b506903e52bb5da9e36b5faba3841f010", "portrait_sha256": "172d41ea3085fde01447e3b68e0dbea250ef15cba6e4b8f4336eb19778193096"}, "d_a~~h11_00_pwg00": {"raw_sha256": "223b5b422658e9d7b7f284e8d0ace599c9becee8589334a69cccb95f6b94d840", "portrait_sha256": "8850687e29db8811b3de0d62fd95106d0baeec6de0bd6d13d4dd87c4117724e8"}, "d_a~~h2_06_vyava": {"raw_sha256": "2e807571d000c184e10af66291a888731b8c539564f68f5681654d2df704e45f", "portrait_sha256": "0e90094900694ef8c6bb92a4e828d2f2d28935bb326e912f2588bb6833c8c915"}, "d_a~~h0_29_nis": {"raw_sha256": "2cc1e822c11809e7aa7bb0be52058f98adbd76a54a017dfe6f592ef2e07b1e42", "portrait_sha256": "dead41d5c28a4482d18be74e42e894a747a9a3fa5a21c96f7ca06f238dbddb97"}, "d_a~~h9_06_vy_a": {"raw_sha256": "e8dff76e38f4df7ddce460d9f292a009ce4e5cd1bef3a7ca5fbd8285dabb0a1c", "portrait_sha256": "c43a2a20d72e379faa47444d5824ea203ae075289f585b1ddc10b77b54860894"}, "d_a~~h2_03_a_byava": {"raw_sha256": "44e08f60549756b586eb894d450445a0dcc76f276d4b12b5f43c3303723b3055", "portrait_sha256": "d971d784f2edfaefbfa03990213d811b3d6b709bb94ff67d5b0c589fe20257b7"}, "d_a~~h0_09_anv_a": {"raw_sha256": "89629d0074368d51780231498689f99e534fb4b1844bd7f549277b8bf19149e5", "portrait_sha256": "5676510c1742c62e514c99cf6da1cad6b0d219c4a59d812e7e0dd9d3fd07e904"}, "d_a~~h0_13_ud_a": {"raw_sha256": "7e08bb12110d0fd2a4f874747ceb8c9ea2646b4896bcad410bba092247509e1b", "portrait_sha256": "f05b6a7e854df756d428564b7b9746d011ac13a1e13e031de49b41bab079d861"}, "d_a~~h0_15_a_byup_a": {"raw_sha256": "d53465451758f457da7b5264d9d940271596590b58caee28f363bb3ff73082d9", "portrait_sha256": "0b0875c5533b218bd48f8fd1fcf75a7f3cf0b175b9c06f9d088f2624661b6777"}, "d_a~~h2_05_paryava": {"raw_sha256": "00366a87faf06bad3f8418f76e4a1dc72098e438657baa8de7e9b6db00cf4869", "portrait_sha256": "321054ee05869c3f944f347a300ebfdb8a3df762240350a4096f6b1869430ede"}, "d_a~~h0_12_sama_by_a": {"raw_sha256": "ff4acbd191df6066a7c14c4af50ccd14d405faf143677a35ab814d867a18d2d8", "portrait_sha256": "64ebb6e4f3f9ca856bfb2d39b4e6d87507e64d47253d612f40f88624b66e64d4"}, "d_a~~h2_11_nis": {"raw_sha256": "a487f2408b8eee64f8bf597f68e17fca85a0094c739b271ab5a22fc30b15c693", "portrait_sha256": "dead41d5c28a4482d18be74e42e894a747a9a3fa5a21c96f7ca06f238dbddb97"}}, "input_payload_keys": ["d_a~~h0_03_sec_3", "d_a~~h0_06_a_bi", "d_a~~h0_07_ava", "d_a~~h0_09_anv_a", "d_a~~h0_12_sama_by_a", "d_a~~h0_13_ud_a", "d_a~~h0_15_a_byup_a", "d_a~~h0_21_apavy_a", "d_a~~h0_27_pari_ri", "d_a~~h0_29_nis", "d_a~~h0_33_atipra", "d_a~~h11_00_pwg00", "d_a~~h12_00_pwg00", "d_a~~h2_01_api", "d_a~~h2_03_a_byava", "d_a~~h2_05_paryava", "d_a~~h2_06_vyava", "d_a~~h2_09_pari_ri", "d_a~~h2_11_nis", "d_a~~h5_00_pwg00", "d_a~~h7_00_pwg00", "d_a~~h9_05_samup_a", "d_a~~h9_06_vy_a"], "selfheal": true, "selfheal_group_budget": 12, "selfheal_cards": {}, "binary_split": true, "output_budget": 1, "sense_presplit_budget": 20, "kill": true, "kill_gate": {"factor": 2.0, "base_ms": 20000, "slope_ms": 45, "floor_ms": 45000, "ceil_ms": 600000}, "kill_switch": true, "agent_budget_strategy": "split-pools-per-card-heal", "max_agents": 79, "max_translate_agents": 79, "max_heal_agents": 0, "translate_agent_expected": 23, "heal_budget_groups": 0, "heal_budget_cards": 0, "max_agents_factor": 3.0, "max_agents_headroom": 10, "max_wide": 3, "stagger_ms": 2000, "per_card_heal_budget": true, "per_card_heal_factor": 1.5, "per_card_heal_headroom": 3, "kill_timeout_no_bisect": true, "presplit_group_cite_budget": 60, "presplit_group_sense_cap": 18, "presplit_group_call_weight": 12000, "presplit_keys": [], "tm": "translation_memory.ru.json", "tm_auto": true, "tm_available": true, "tm_cards": 1, "tm_hits": ["d_a~~h8_00_pwg00"], "frag_tm": null, "frag_tm_cards": [], "frag_tm_fragments": 0, "suggest_tm": null, "suggest_profile": "semantic", "suggest_tm_cards": [], "suggest_tm_top": {}, "degenerate_passthrough_keys": [], "agent_expected_after_tm": 23}

const restore = (t, ph) => (t || '').replace(/\{T(\d+)\}/g, (m, n) => (ph[+n - 1] !== undefined ? ph[+n - 1] : m))
const countOf = (card, re) => { let n = 0; for (const rec of (card.records || [])) for (const s of (rec.senses || [])) n += ((s.german || '').match(re) || []).length; return n }
// H1152 guard 2: countOf() above ONLY ever reads the `german` SOURCE-echo field — it was
// built to verify the model copied the masked German verbatim, never to verify the
// TRANSLATION. countOfField lets accept() run the identical count over the actual
// target-language field (`english`/`russian`) too, so a {Tn} that survives in `german`
// but is silently dropped from the translation (H1070 r102: {#uc#} in a <F> footnote
// survived `german` 33/33 but vanished from `english`, 32/33 -- invisible to countOf()
// because it never looks at the translation field at all) is no longer invisible.
const countOfField = (card, field, re) => { let n = 0; for (const rec of (card.records || [])) for (const s of (rec.senses || [])) n += ((s[field] || '').match(re) || []).length; return n }
// Failure ledger: key -> last-known reason a card/fragment is unresolved. Every path that
// nulls a card MUST leave a reason here — a bare null is indistinguishable downstream
// between a hard agent() throw, a fidelity reject, and the model omitting the card,
// which is exactly the ambiguity that made a week of failures undiagnosable. Surfaced
// per-row (results[].error) and in summary.failures.
const FAIL = {}
const noteFail = (k, why) => { FAIL[k] = String(why).slice(0, 300) }
// --- wall-clock kill gate ---------------------------------------------------------
// Budget each schema-bearing agent() call a wall-clock allowance scaled to its output
// volume (skelBytes = summed masked-skeleton length of its cards/fragments — the model's
// output is ~2x this, and it's a natural composite of every failure driver); a call that
// runs past KILL_FACTOR x its expected time is abandoned so the caller can fall to the
// bounded fragment lane instead of waiting out the full StructuredOutput retry cap.
// setTimeout is a RELATIVE timer (Date.now() is banned in the runtime); AbortController
// is unavailable, so an abandoned call keeps running in the background until it dies on
// its own cap — we stop BLOCKING on it, which is the whole point.
class KillTimeout extends Error {}
const isKill = e => (e instanceof KillTimeout) || (e && /kill-timeout/.test(String(e && e.message)))
const killBudgetMs = skelBytes => Math.min(KILL_CEIL_MS, Math.max(KILL_FLOOR_MS, KILL_FACTOR * (KILL_BASE_MS + KILL_SLOPE_MS * skelBytes)))
const skelBytesOfKeys = keys => keys.reduce((n, k) => n + (INPUTS[k] ? INPUTS[k].skeleton.length : 0), 0)
// H220: a SINGLE card with no selfheal fallback (single-fragment supplement / nominal card
// that does not split) has NO smaller lane for the kill gate to route to — abandoning it on
// the byte-scaled budget is pure loss. Such a card still returns a VALID card, only slower
// than a tiny skeleton's budget predicts: the fixed per-call StructuredOutput latency
// (~55-105 s) dominates, independent of skeleton size. The no-PWG w1 run killed 6/6 nulls
// this way (kill-timeout 53-104 s, all would have passed accept). Give a no-fallback single
// the CEIL budget so it is only abandoned on a true >CEIL hang.
// H255/H823 extension: give ANY single-card batch the CEIL, not just no-fallback ones. The
// original rule kept a SPLITTABLE single on the aggressive byte-scaled gate because "a kill
// routes to fragment heal" — but the heal groups run on the SAME byte-scaled budgets, so on a
// slow API BOTH the whole-card attempt AND the heal lane kill on the ~55-105 s fixed latency,
// and the card is a permanent null anyway (the H255 presplit-cohort loss). A lone card has no
// batch-mates to starve, so it should get the full CEIL on its ONE whole-card attempt (it
// either lands within the fixed latency or genuinely hangs) instead of being abandoned into a
// heal lane that is no better budgeted. Multi-card BATCHES keep the byte-scaled gate (there a
// kill legitimately routes to binary-split, and one slow card must not hold up its mates).
// SHARED (keys on FRAGS, no RU/EN branching).
const hasFallback = k => Array.isArray(FRAGS[k]) && FRAGS[k].length > 0
const killBudgetForCur = cur => (cur.length === 1) ? KILL_CEIL_MS : killBudgetMs(skelBytesOfKeys(cur))
// Split-pool budget state. Labels beginning `heal:` are recovery; every other call is primary
// translation (including resolveGroup binary splits). BudgetExceeded is deliberately NOT an
// isKill(): a kill routes to recovery, whereas a pool stop must issue zero more calls in that
// lane. AGENTS_SPENT remains the backwards-compatible total telemetry counter.
class BudgetExceeded extends Error {}
let AGENTS_SPENT = 0
let BUDGET_TRIPPED = false
let TRANSLATE_AGENTS_SPENT = 0
let HEAL_AGENTS_SPENT = 0
let TRANSLATE_BUDGET_TRIPPED = false
let HEAL_BUDGET_TRIPPED = false
// H462 telemetry: COUNTERS ONLY, no behavioural change. The two decisive numbers of every
// launch post-mortem — the kill-timeout count and the 'Connection closed mid-response'
// count — previously existed only as console.log strings and were hand-counted from
// transcripts into LAUNCH_FUCKUPS.md ('58 of 61 kill-timeouts', '3 conn-errors'). Returned
// in `summary` so the orchestrator and classify_run.py read them mechanically instead.
// CONN_ERRORS counts THROWN transport errors; agent() can also RETURN NULL on a terminal
// API error after retries — those stay visible as agent-returned-null in summary.failures,
// so a zero here is 'no thrown transport error', not 'network provably healthy'.
let KILL_TIMEOUTS = 0
let CONN_ERRORS = 0
let HEAL_CALLS = 0
let KILL_BISECT_BLOCKED = 0
// H960 SAN-LOSS shortfall telemetry: TELEMETRY ONLY, no behavioural change (SOFT rollout).
// accept() records — but does NOT reject on — a card whose emitted top-level sense count
// falls short of the source's deterministic (cross-reference-hardened) source_senses. This
// is the whole-dropped-sense signal the <ls>/{# fidelity guard is blind to (H920's deferred
// deepest fix). It is soft-first so live traffic can measure the true drop-vs-false-flag
// balance before the reject+requeue is armed; flipping SANLOSS_HARD_REJECT=true (owner-gated,
// after the live measurement) turns each shortfall into the same deterministic requeue as an
// ls/sk fidelity-reject. Counter + per-card details ride in `summary` for classify_run.py.
const SANLOSS_HARD_REJECT = false
let SANLOSS_SHORTFALLS = 0
const SANLOSS_DETAIL = []
// H960 grammar-{Tn} multiset telemetry: TELEMETRY ONLY, no behavioural change (SOFT rollout).
// The main-path accept() <ls>/{# count check is blind to a dropped GRAMMAR <lex> {Tn} (or any
// masked span carrying neither an <ls> nor a {#) — the exact gap the heal path's acceptFrag
// already guards with a full {Tn}-multiset compare. accept() records — but does NOT reject on —
// a card whose emitted {Tn} multiset differs from its source skeleton's. Soft-first so live
// traffic can measure the drop-vs-self-expansion mix (a model that writes literal <ls>..</ls>
// instead of {Tn} also trips this) before the reject is armed; flipping TNMASK_HARD_REJECT=true
// (owner-gated) turns each mismatch into the same deterministic requeue as an ls/sk reject.
const TNMASK_HARD_REJECT = false
let TNMASK_MISMATCHES = 0
const TNMASK_DETAIL = []
// H858 Part B german-anchor telemetry: how many cards were SAVED from an ls/sk fidelity-reject
// by re-injecting a dropped source span, and which spans. Unlike the two soft gates above this
// is not a rollout switch — the repair only ever runs on a card that was already being thrown
// away, and only lands when it verifies exactly source-faithful, so there is nothing to arm.
let GERMAN_ANCHOR_REPAIRS = 0
const GERMAN_ANCHOR_DETAIL = []
// H3665: `german_anchor_repairs: 0` reads the same whether nothing needed repairing or the
// repair was never reached. The batch lane keeps the same two extra counters as the headless
// twin (headless_worker.normalize_batch), so a summary from either route is read the same way.
let GERMAN_ANCHOR_INVOCATIONS = 0
const GERMAN_ANCHOR_NOT_REACHED = []
// H3675: the target-side repair's own telemetry, same shape as the german one.
let TARGET_ANCHOR_REPAIRS = 0
let TARGET_ANCHOR_INVOCATIONS = 0
const TARGET_ANCHOR_DETAIL = []
const isConn = e => !!(e && !(e instanceof KillTimeout) && /connection closed|connection error|econnreset|econnrefused|socket hang up|fetch failed|network error/i.test(String(e && e.message)))
async function agentKill(prompt, opts, skelBytes, budgetMsOverride) {
  const healLane = !!(opts && opts.label && /^heal:/.test(String(opts.label)))
  const lane = healLane ? 'heal' : 'translate'
  const spent = healLane ? HEAL_AGENTS_SPENT : TRANSLATE_AGENTS_SPENT
  const ceiling = healLane ? MAX_HEAL_AGENTS : MAX_TRANSLATE_AGENTS
  if (KILL_SWITCH && ceiling != null && spent >= ceiling) {
    BUDGET_TRIPPED = true
    if (healLane) HEAL_BUDGET_TRIPPED = true
    else TRANSLATE_BUDGET_TRIPPED = true
    throw new BudgetExceeded('budget-kill-switch[' + lane + ']: hit ' + ceiling + ' agent() calls; lane remainder requeued')
  }
  AGENTS_SPENT++
  if (healLane) HEAL_AGENTS_SPENT++
  else TRANSLATE_AGENTS_SPENT++
  // heal-lane spend: every healGroup label starts 'heal:' (bisection halves inherit the
  // prefix), so this counts real heal agent() calls against the whole window — the
  // per-card view stays on selfHeal's cardBudget.spent.
  if (healLane) HEAL_CALLS++
  if (!KILL) return agent(prompt, opts)   // kill gate off = counters best-effort (never in production)
  const ms = (budgetMsOverride != null) ? budgetMsOverride : killBudgetMs(skelBytes)
  let timer
  const guard = new Promise((_, rej) => { timer = setTimeout(() => rej(new KillTimeout('kill-timeout ' + Math.round(ms / 1000) + 's @ skelBytes=' + skelBytes)), ms) })
  try { return await Promise.race([agent(prompt, opts), guard]) }
  catch (e) { if (isKill(e)) KILL_TIMEOUTS++; else if (isConn(e)) CONN_ERRORS++; throw e }
  finally { clearTimeout(timer) }
}
// Masked-token multiset of a text: the {Tn} placeholders it carries, order-insensitive.
// Two texts with equal token multisets restore to identical citation/markup content.
const tokensOf = t => ((t || '').match(/\{T\d+\}/g) || []).sort().join(' ')
// C-17: which fields' {Tn} must MATCH the source skeleton for the fragment-fidelity guard is NOT
// re-typed here -- it is injected from card_fields.js_token_fidelity_spec(), the SAME constant the
// Python `card_token_multiset` collects from, so the two twins cannot drift (the C-17 defect was
// the Python lane omitting `grammar` while this JS lane hard-coded rec.grammar + s.german).
const TOKEN_FIDELITY_SPEC = {"record": ["grammar"], "sense": ["german"]}

// H858 Part B: source-anchored repair of {Tn} spans the model dropped from its `german`
// echo. Python twin: src/german_anchor.py (authored there and interpolated here — never
// re-typed per lane). Repair-then-verify: accept() calls this ONLY for a card that already
// failed the german-side fidelity count, and re-runs that count afterwards, so a card that
// passes today is byte-untouched. Refuses unless the echo is a strict order-preserving
// subsequence of the source (no foreign token, no duplicate, no reordering) — under that
// precondition the only possible defect is a drop, which the source fixes deterministically.
const GA_TOKEN_RE = /\{T\d+\}/g
const gaTokens = t => ((t || '').match(GA_TOKEN_RE) || [])
const gaSenses = card => { const out = []; for (const rec of (card.records || [])) for (const s of (rec.senses || [])) if (s && typeof s === 'object') out.push(s); return out }
const gaSpans = skeleton => { const out = []; let m; const re = new RegExp(GA_TOKEN_RE.source, 'g'); while ((m = re.exec(skeleton || '')) !== null) out.push([m[0], m.index, m.index + m[0].length]); return out }
const gaPlan = (card, skeleton) => {
  const spans = gaSpans(skeleton)
  const want = spans.map(s => s[0])
  if (new Set(want).size !== want.length) return { ok: false, reason: 'source-token-repeat' }
  const senses = gaSenses(card)
  if (!senses.length) return { ok: false, reason: 'no-senses' }
  const order = new Map(want.map((t, i) => [t, i]))
  const seen = new Set()
  let last = -1
  for (const s of senses) for (const t of gaTokens(s.german)) {
    if (!order.has(t)) return { ok: false, reason: 'foreign-token', token: t }
    if (seen.has(t)) return { ok: false, reason: 'duplicate-token', token: t }
    if (order.get(t) <= last) return { ok: false, reason: 'reordered-token', token: t }
    seen.add(t); last = order.get(t)
  }
  const missing = want.filter(t => !seen.has(t))
  if (!missing.length) return { ok: false, reason: 'nothing-missing' }
  const after = new Map(), before = new Map(), head = []
  const push = (map, key, t) => { if (!map.has(key)) map.set(key, []); map.get(key).push(t) }
  for (let i = 0; i < spans.length; i++) {
    const [token, start, end] = spans[i]
    if (seen.has(token)) continue
    let prev = null, nxt = null
    for (let j = i - 1; j >= 0; j--) if (seen.has(spans[j][0])) { prev = spans[j]; break }
    for (let j = i + 1; j < spans.length; j++) if (seen.has(spans[j][0])) { nxt = spans[j]; break }
    if (prev === null) head.push(token)                          // nothing survives before it
    else if (nxt === null) push(after, prev[0], token)
    else if ((start - prev[2]) <= (nxt[1] - end)) push(after, prev[0], token)
    else push(before, nxt[0], token)
  }
  return { ok: true, after: after, before: before, head: head, missing: missing }
}
const gaReanchor = (card, skeleton) => {
  const p = gaPlan(card, skeleton)
  if (!p.ok) return p
  const senses = gaSenses(card)
  const expand = m => (p.before.get(m) || []).map(t => t + ' ').join('') + m
                      + (p.after.get(m) || []).map(t => ' ' + t).join('')
  for (const s of senses) {
    if (typeof s.german !== 'string' || !s.german.match(GA_TOKEN_RE)) continue
    s.german = s.german.replace(GA_TOKEN_RE, expand)
  }
  if (p.head.length) {
    const first = senses[0]
    const text = typeof first.german === 'string' ? first.german : ''
    first.german = p.head.join(' ') + (text ? ' ' + text : '')
  }
  return p
}
const gaStamp = p => ({ reinjected: p.missing.map(t => t.replace(/[{}]/g, '')), head: p.head.map(t => t.replace(/[{}]/g, '')) })


// Target-side twin of the german-anchor repair: re-injects {Tn} spans the model dropped from
// the TRANSLATION field while echoing `german` faithfully (FINDINGS 605/608; the live shape is
// hasita~~h0_zz_pw, german 2/2 target 1/2). Python twin: src/target_anchor.py (authored there
// and interpolated here — never re-typed per lane). Repair-then-verify: accept() calls this
// ONLY for a card that already failed the TARGET-field fidelity count, and re-runs that count
// afterwards. The anchor is the SAME sense's german, which still carries every token in order —
// so this restores a token to a position its own parallel names, it does not parse prose.
const TA_TOKEN_RE = /\{T\d+\}/g
const taTokens = t => ((t || '').match(TA_TOKEN_RE) || [])
const taSenses = card => { const out = []; for (const rec of (card.records || [])) for (const s of (rec.senses || [])) if (s && typeof s === 'object') out.push(s); return out }
const taSpans = text => { const out = []; let m; const re = new RegExp(TA_TOKEN_RE.source, 'g'); while ((m = re.exec(text || '')) !== null) out.push([m[0], m.index, m.index + m[0].length]); return out }
const taPlan = (card, field) => {
  const senses = taSenses(card)
  if (!senses.length) return { ok: false, reason: 'no-senses' }
  const plans = [], missingAll = []
  for (let i = 0; i < senses.length; i++) {
    const s = senses[i]
    const spans = taSpans(s.german)
    const want = spans.map(x => x[0])
    if (new Set(want).size !== want.length) return { ok: false, reason: 'anchor-token-repeat', sense: i }
    const order = new Map(want.map((t, n) => [t, n]))
    const seen = new Set()
    let last = -1
    for (const t of taTokens(s[field])) {
      if (!order.has(t)) return { ok: false, reason: 'foreign-token', sense: i, token: t }
      if (seen.has(t)) return { ok: false, reason: 'duplicate-token', sense: i, token: t }
      if (order.get(t) <= last) return { ok: false, reason: 'reordered-token', sense: i, token: t }
      seen.add(t); last = order.get(t)
    }
    const missing = want.filter(t => !seen.has(t))
    if (!missing.length) continue
    const after = new Map(), before = new Map(), head = [], tail = []
    const push = (map, key, t) => { if (!map.has(key)) map.set(key, []); map.get(key).push(t) }
    for (let n = 0; n < spans.length; n++) {
      const [token, start, end] = spans[n]
      if (seen.has(token)) continue
      let prev = null, nxt = null
      for (let j = n - 1; j >= 0; j--) if (seen.has(spans[j][0])) { prev = spans[j]; break }
      for (let j = n + 1; j < spans.length; j++) if (seen.has(spans[j][0])) { nxt = spans[j]; break }
      // Sense start AND sense end are the virtual anchors when nothing survives on that
      // side — see the Python twin's comment. Without them a leading-but-not-first span jumps
      // in front of its own prose and a trailing span lands behind it.
      const left = start - (prev === null ? 0 : prev[2])
      const right = nxt === null ? (s.german || '').length - end : nxt[1] - end
      if (left <= right) { if (prev === null) head.push(token); else push(after, prev[0], token) }
      else { if (nxt === null) tail.push(token); else push(before, nxt[0], token) }
    }
    plans.push({ index: i, after: after, before: before, head: head, tail: tail })
    for (const t of missing) missingAll.push(t)
  }
  if (!missingAll.length) return { ok: false, reason: 'nothing-missing' }
  return { ok: true, senses: plans, missing: missingAll }
}
const taReanchor = (card, field) => {
  const p = taPlan(card, field)
  if (!p.ok) return p
  const senses = taSenses(card)
  for (const entry of p.senses) {
    const s = senses[entry.index]
    const expand = m => (entry.before.get(m) || []).map(t => t + ' ').join('') + m
                        + (entry.after.get(m) || []).map(t => ' ' + t).join('')
    if (typeof s[field] === 'string' && s[field].match(TA_TOKEN_RE)) {
      s[field] = s[field].replace(TA_TOKEN_RE, expand)
    }
    if (entry.head.length) {
      const text = typeof s[field] === 'string' ? s[field] : ''
      s[field] = entry.head.join(' ') + (text ? ' ' + text : '')
    }
    if (entry.tail.length) {
      const text = typeof s[field] === 'string' ? s[field] : ''
      s[field] = (text ? text + ' ' : '') + entry.tail.join(' ')
    }
  }
  return p
}
// ONE LINE, like gaStamp: the JS test harness extracts it with a single-line matcher.
const taStamp = p => ({ reinjected: p.missing.map(t => t.replace(/[{}]/g, '')), head: p.senses.reduce((a, e) => a.concat(e.head), []).map(t => t.replace(/[{}]/g, '')) })

const cardTokens = card => { let a = []; for (const rec of (card.records || [])) { for (const f of TOKEN_FIDELITY_SPEC.record) a = a.concat((rec[f] || '').match(/\{T\d+\}/g) || []); for (const s of (rec.senses || [])) for (const f of TOKEN_FIDELITY_SPEC.sense) a = a.concat((s[f] || '').match(/\{T\d+\}/g) || []) } return a.sort().join(' ') }
// Index a returned cards[] by its self-declared key1 (the prompt requires key1 to echo the
// '=== CARD <key> ===' header). Used to match responses by KEY first, position second —
// positional-only matching silently misassigns every card after an omitted/reordered one.
const byKey1 = cards => { const m = {}; for (const c of cards) if (c && c.key1 !== undefined && !(c.key1 in m)) m[c.key1] = c; return m }
const exactCard = (cards, km, expected, fallbackIndex) => {
  if (km[expected] !== undefined) return km[expected]
  const c = cards[fallbackIndex]
  return (c && c.key1 === expected) ? c : null
}
// C-01: which fields carry {Tn} and must be unmasked is NOT re-typed here -- it is injected
// from card_fields.js_restore_spec(field), the same constant the Python lane restores from
// and promote_final_cards refuses on. Hand-maintaining this list on each lane is exactly how
// card.iast / rec.h / s.tag / s.differentia came to be promoted with their placeholders intact.
const RESTORE_SPEC = {"card": ["iast"], "record": ["h", "grammar"], "sense": ["tag", "german", "differentia", "russian"]}
// H1152 guard 2: the per-sense target-language field name ('english'/'russian'), so accept()
// can run countOfField over the actual translation, not just the `german` source echo.
const TARGET_FIELD = 'russian'
// C-02: rebuild records[] from healed senses, preserving each sense's [h, grammar] owner.
// The stitch used to emit `records: [{ senses }]` — no h, no grammar — which violates
// schemas/pwg_ru_final_card.schema.json (record.required = {h, grammar, senses}) and made the
// promote path write h: null. It also collapsed real homonyms (79 sub-cards carry more than
// one distinct h). Consecutive senses sharing an owner stay in one record; a change of owner
// opens the next, so document order — and the whole-card fidelity counts — are unchanged.
// The Python twin is headless_worker.stitch_records; keep them behaviourally identical.
function stitchRecords(senses, owners) {
  const out = []
  for (let i = 0; i < senses.length; i++) {
    const [h, grammar] = owners[i] || [null, null]
    const last = out[out.length - 1]
    if (!last || last.h !== h || last.grammar !== grammar) out.push({ h, grammar, senses: [senses[i]] })
    else last.senses.push(senses[i])
  }
  return out
}
function restoreCard(card, k) {
  const ph = PH[k] || []
  for (const f of RESTORE_SPEC.card) if (typeof card[f] === 'string') card[f] = restore(card[f], ph)
  for (const rec of (card.records || [])) {
    for (const f of RESTORE_SPEC.record) if (typeof rec[f] === 'string') rec[f] = restore(rec[f], ph)
    for (const s of (rec.senses || [])) {
      for (const f of RESTORE_SPEC.sense) if (typeof s[f] === 'string') s[f] = restore(s[f], ph)
    }
  }
  return card
}
// Per-card grammar (nominal mode): each headword carries its own block. Empty in root
// mode (the shared GRAMMAR is injected once after CONV_TR, H2191) and in the --no-grammar arm.
const suggestionBlock = k => {
  const rows = SUGGEST_TM[k] || []
  if (!rows.length) return ''
  const scoreBits = r => [
    'de=' + (r.score_de_fragment ?? 'n/a'),
    'sa=' + (r.score_sa_headword ?? 'n/a'),
    'tag=' + (r.score_semantic_tag ?? 'n/a'),
    'combined=' + (r.score_combined ?? r.score ?? 'n/a')
  ].join(' ')
  return '\n--- advisory translation-memory suggestions (SUGGEST ONLY: may seed weak evidence; do not copy unsupported senses; mark provenance if used) ---\n' +
    rows.map(r => '[' + (r.source_kind || 'suggestion') + ' ' + scoreBits(r) + ' ' + (r.provenance_note || '') + '] ' + (r.text || '')).join('\n')
}
const cardBlock = k => (GRAMMARS[k] || '') + '\n\n=== CARD ' + k + ' ===\n--- masked German (translatable only; {Tn}=masked span) ---\n' + INPUTS[k].skeleton + suggestionBlock(k) + '\n--- portrait (evidence) ---\n' + INPUTS[k].portrait

const accept = (c, k) => {
  if (!c) return null
  // H960 grammar-{Tn} multiset guard (soft). BEFORE restore (the {Tn} placeholders are gone
  // after restoreCard): a dropped grammar <lex> {Tn} carries neither an <ls> nor a {#, so the
  // count check below is blind to it — but the {Tn} multiset is not. This is the heal path's
  // acceptFrag check (which has run in production without incident) brought to the main path.
  // SOFT by default: record telemetry, do NOT reject; arming is TNMASK_HARD_REJECT (owner-gated).
  {
    const tok = cardTokens(c), want = tokensOf(INPUTS[k].skeleton)
    // H1226: persist the pre-restore {Tn} pairing this check compares — candidate `got` vs
    // masked-skeleton `want` — so a SOFT (un-rejected) expansion becomes MEASURABLE offline
    // from the promoted row. The store keeps only post-restore text, dropping the very pairing
    // TNMASK needs (H1150 returned DO_NOT_ARM, denominator 1, for exactly this reason). Set
    // UNCONDITIONALLY: clean cards (got===want) are the measurement denominator. Braces stripped
    // ('{T1} {T2}' -> 'T1 T2') so this provenance never reads as a raw {Tn} residue in the store
    // (equality is preserved — same bijection on both sides). Survives restoreCard (RESTORE_SPEC
    // lists only the text fields, never `tnmask`). Only accept() carries it: the heal path's
    // acceptFrag hard-rejects fragment {Tn} mismatches, so no un-rejected expansion reaches a
    // healed card (see pwg_ru/h1226 design note).
    c.tnmask = { got: tok.replace(/[{}]/g, ''), want: want.replace(/[{}]/g, '') }
    if (tok !== want) {
      TNMASK_MISMATCHES++
      TNMASK_DETAIL.push({ key: k, got: tok, want: want })
      if (TNMASK_HARD_REJECT) { noteFail(k, 'tnmask-reject: {Tn} multiset [' + tok + '] != [' + want + ']'); return null }
      log('{Tn} multiset mismatch (soft): ' + k + ' — kept, telemetry only')
    }
  }
  // H858 Part B: snapshot the PRE-restore card. The anchored repair below works on {Tn}
  // tokens, which restoreCard consumes — after it a dropped span is indistinguishable from
  // prose and can no longer be anchored. Python twin: headless_worker.normalize_batch.
  const masked = JSON.parse(JSON.stringify(c))
  let germanStamp = null
  c = restoreCard(c, k)
  // Fidelity guard: restored <ls>/{#..#} counts MUST match the source — a mismatch
  // means misalignment / dropped {Tn}. Reject -> deterministic requeue, never emit garbled.
  let ls = countOf(c, /<ls\b/g), sk = countOf(c, /\{#/g)
  if (ls !== INPUTS[k].ls || sk !== INPUTS[k].sk) {
    // H858 Part B: the model dropped a masked span from its `german` echo — the dominant
    // retry-RESISTANT null class (6 of 7 residual nulls in no_pwg_w10, H1283): a requeue
    // reproduces it, because the drop is a property of the echo, not of transport. Re-inject
    // the dropped spans from the source skeleton and re-run THIS SAME count as the verifier.
    // Accepted only when the repair makes the card exactly source-faithful; anything else
    // falls through to the identical reject as before. A card that passed the count above
    // never enters this branch, so clean cards are byte-untouched.
    GERMAN_ANCHOR_INVOCATIONS++
    const rep = gaReanchor(masked, INPUTS[k].skeleton || '')
    const cand = rep.ok ? restoreCard(JSON.parse(JSON.stringify(masked)), k) : null
    const cls = cand ? countOf(cand, /<ls\b/g) : -1, csk = cand ? countOf(cand, /\{#/g) : -1
    if (cand && cls === INPUTS[k].ls && csk === INPUTS[k].sk) {
      // `masked` was snapshotted AFTER the tnmask block above, so the repaired card already
      // carries the same H1226 pre-restore pairing — the stamp keeps describing what the model
      // actually emitted, never the repaired text.
      c = cand
      germanStamp = gaStamp(rep)          // H3675: survives the target repair's re-restore
      c.german_anchor = germanStamp
      GERMAN_ANCHOR_REPAIRS++
      GERMAN_ANCHOR_DETAIL.push({ key: k, reinjected: c.german_anchor.reinjected })
      log('german-anchor repair: ' + k + ' re-injected ' + c.german_anchor.reinjected.join(',') + ' from source')
      ls = cls; sk = csk
    } else {
      noteFail(k, 'fidelity-reject: <ls> ' + ls + '/' + INPUTS[k].ls + ', {# ' + sk + '/' + INPUTS[k].sk +
        '; german-anchor ' + (rep.ok ? 'verify-failed' : (rep.reason || 'refused')))
      return null
    }
  }
  // H1152 guard 2: the check above counts <ls>/{#..#} ONLY in the `german` source-echo
  // field (countOf's hard-coded `s.german` read) -- it proves the model faithfully copied
  // the masked German back out, never that the TRANSLATION preserved the same spans. A
  // {Tn} can be dropped from the translation field alone with zero effect on the check
  // above (this is the H960/H911 `dropped_sanskrit_span` gap, already known and detected
  // as a LOW/report-only RU-side signal in prompt_rule_audit.markup_sigla_risks, but never
  // wired as a HARD, blocking check on the generation path for either language). Root
  // cause, confirmed against the live H1070 r102 row (vac~~h0_00_pwg00, {#uc#} inside a
  // <F> footnote): `german` carried 33/33 expected {#..#} spans (this check passed clean)
  // while `english` carried only 32/33 -- the drop happened ONLY in the field this guard
  // never inspects. Run the identical count over the actual target-language field so a
  // translation-only drop can no longer hide behind a clean source echo.
  const lsT = countOfField(c, TARGET_FIELD, /<ls\b/g), skT = countOfField(c, TARGET_FIELD, /\{#/g)
  if (lsT !== INPUTS[k].ls || skT !== INPUTS[k].sk) {
    // H3665: the german-only guard above passed, so the german repair branch was never
    // entered -- this card is invisible to `german_anchor_repairs` in BOTH directions.
    GERMAN_ANCHOR_NOT_REACHED.push(k)
    // H3675: repair-then-verify on the TARGET side. The german echo is faithful, so THIS
    // sense's german still carries every {Tn} in order and is a sound anchor; re-inject the
    // dropped ones and re-run this same count as the verifier. Refused cards fall through to
    // the identical reject as before. MG ruled `reanchor` over an explicit requeue 29-08-2026.
    TARGET_ANCHOR_INVOCATIONS++
    const trep = taReanchor(masked, TARGET_FIELD)
    const tcand = trep.ok ? restoreCard(JSON.parse(JSON.stringify(masked)), k) : null
    const tls = tcand ? countOf(tcand, /<ls\b/g) : -1, tsk = tcand ? countOf(tcand, /\{#/g) : -1
    const tlsT = tcand ? countOfField(tcand, TARGET_FIELD, /<ls\b/g) : -1
    const tskT = tcand ? countOfField(tcand, TARGET_FIELD, /\{#/g) : -1
    if (!(tcand && tls === INPUTS[k].ls && tsk === INPUTS[k].sk
          && tlsT === INPUTS[k].ls && tskT === INPUTS[k].sk)) {
      noteFail(k, 'translation-fidelity-reject: <ls> ' + lsT + '/' + INPUTS[k].ls + ', {# ' + skT + '/' + INPUTS[k].sk +
        '; target-anchor ' + (trep.ok ? 'verify-failed' : (trep.reason || 'refused')))
      return null
    }
    c = tcand
    // The re-restore produced a fresh object, so a german repair already applied to this card
    // must be re-stamped or its provenance is silently lost.
    if (germanStamp) c.german_anchor = germanStamp
    c.target_anchor = taStamp(trep)
    TARGET_ANCHOR_REPAIRS++
    TARGET_ANCHOR_DETAIL.push({ key: k, reinjected: c.target_anchor.reinjected })
    log('target-anchor repair: ' + k + ' re-injected ' + c.target_anchor.reinjected.join(',') + ' into ' + TARGET_FIELD)
  }
  // H960 SAN-LOSS shortfall guard (H920's deferred deepest fix). The ls/sk fidelity check
  // above is blind to a whole dropped sense that carries neither a citation nor a {#..#} span
  // (darvI 2/3). Compare the emitted top-level sense count to the source's deterministic,
  // cross-reference-hardened source_senses (stamped Python-side). exp<1 (unnumbered supplement)
  // is skipped, and only a shortfall (emitted < exp) is flagged — a faithful split that yields
  // MORE senses never trips it. SOFT by default: record telemetry, do NOT reject; arming the
  // reject is SANLOSS_HARD_REJECT (owner-gated, after live measurement of the false-flag rate).
  const exp = INPUTS[k].source_senses
  if (exp > 0) {
    const emitted = (c.records || []).reduce((n, rec) => n + ((rec.senses || []).length), 0)
    if (emitted < exp) {
      SANLOSS_SHORTFALLS++
      SANLOSS_DETAIL.push({ key: k, expected: exp, emitted: emitted, dropped: exp - emitted })
      if (SANLOSS_HARD_REJECT) {
        noteFail(k, 'sanloss-reject: senses ' + emitted + '/' + exp)
        return null
      }
      log('SAN-LOSS shortfall (soft): ' + k + ' senses ' + emitted + '/' + exp + ' — kept, telemetry only')
    }
  }
  return c
}

// Resolve one heal GROUP (indices into `grp`), trying the whole group up to 3 attempts;
// if it still has >1 unresolved fragment, bisect and resolve each half independently with
// its own fresh 3-attempt budget — this is the safety net a grouped call needs: a live run
// on brU showed a 2-fragment group (ud) fail all 3 attempts and lose BOTH fragments, where
// the pre-grouping one-fragment-per-call design would only have risked one. Bisection falls
// back toward that safer granularity only when a group actually struggles, so the happy path
// (group succeeds) keeps the full cost saving. Returns a {idx: card} map, or null if any
// fragment never resolved even as a singleton.
async function healGroup(k, idxs, grp, label, budget) {
  const resolved = {}
  const fkey = fi => k + '_f' + fi
  // H442 per-card heal budget: `budget` is a shared mutable {spent,max} owned by the CARD
  // (selfHeal creates one and passes the same object into every group + every bisection
  // recursion). Once the card's own heal spend crosses budget.max, stop starting new calls
  // and return the resolved fragments as partial — the card's remaining fragments requeue,
  // but it never keeps consuming the shared window MAX_AGENTS pool. budget==null (or
  // --no-per-card-heal-budget) restores the old unbounded behavior.
  const budgetExhausted = () => budget && budget.max != null && budget.spent >= budget.max
  // Accept a returned fragment only if its masked-token multiset matches the fragment's
  // skeleton — the heal path previously accepted fragments UNCHECKED (the main path's
  // accept() fidelity guard had no heal-side sibling), so a misaligned/mangled fragment
  // could be stitched into a partial card with no gate downstream reading it.
  const acceptFrag = (c, fi) => {
    if (!c) return false
    if (cardTokens(c) !== tokensOf(grp[fi].skeleton)) {
      noteFail(fkey(fi), 'fragment-fidelity-reject: {Tn} multiset mismatch')
      return false
    }
    resolved[fi] = c
    return true
  }
  let pending = idxs.slice()
  let killedOut = false   // H442: did this group's attempt loop end on a kill-timeout?
  for (let att = 0; att < 3 && pending.length; att++) {
    if (budgetExhausted()) {
      pending.forEach(fi => noteFail(fkey(fi), 'per-card-heal-budget: card ' + k + ' hit ' + budget.max + ' heal calls — partial, requeue remaining'))
      break   // fail fast to partial; the card stops consuming the shared window budget
    }
    if (budget) budget.spent++   // account this call against the card's own ceiling
    const blocks = pending.map(i => '\n\n=== CARD ' + fkey(i) + ' (fragment ' + (i + 1) + '/' + grp.length + ') ===\n--- masked German (translatable only; {Tn}=masked span) ---\n' + grp[i].skeleton).join('')
    // B01 (H1339): fragment/heal calls serve exactly ONE card k, so inject that card's own
    // evidence -- per-card grammar (the ONLY grammar in nominal windows, where the shared
    // GRAMMAR constant is empty) and the portrait (Sanskrit citation evidence), exactly as
    // the whole-card batch lane's cardBlock does. Presplit giants -- the densest,
    // highest-value cards -- were translated with ZERO evidence before this.
    // H2191: stable-left order, the JS twin of headless_worker.fragment_prompt --
    // PREAMBLE + CONV_TR (run-invariant) before the window's GRAMMAR and this card's own.
    const prompt = PREAMBLE + CONV_TR + GRAMMAR + (GRAMMARS[k] || '') + blocks
      + '\n--- portrait (evidence) ---\n' + (INPUTS[k] ? INPUTS[k].portrait : '')
    const gskel = pending.reduce((n, fi) => n + (grp[fi].skeleton ? grp[fi].skeleton.length : 0), 0)
    let res
    try {
      res = await agentKill(prompt, { label: label + '[' + pending.length + ']' + (att ? '(r' + att + ')' : ''), phase: 'Translate', schema: CARDS_SCHEMA, model: 'claude-sonnet-5', tools: [] }, gskel)
    } catch (e) {
      if (!isKill(e)) throw e   // real hard failure — propagate (caught by selfHeal's per-group try)
      killedOut = true
      if (KILL_TIMEOUT_NO_BISECT) KILL_BISECT_BLOCKED++   // H462: telemetry only
      pending.forEach(fi => noteFail(fkey(fi), e.message))
      log(label + ': kill-timeout-no-bisect: ' + e.message + ' — abandoned, requeueing ' + pending.length + ' fragment(s)')
      break   // stop retrying this group; kill-timeout fragments requeue instead of bisecting
    }
    if (res && Array.isArray(res.cards)) {
      const km = byKey1(res.cards)
      // Fragments may arrive reordered, but a positional fallback is safe only when the
      // fallback card still echoes the exact fragment key and passes the token multiset guard.
      pending.forEach((fi, idx) => {
        const fk = fkey(fi)
        const cand = exactCard(res.cards, km, fk, idx)
        if (!cand) { noteFail(fk, 'missing-or-mismatched-fragment-key'); return }
        acceptFrag(cand, fi)
      })
    } else {
      pending.forEach(fi => noteFail(fkey(fi), res ? 'malformed-response (no cards[])' : 'agent-returned-null'))
    }
    pending = pending.filter(fi => !resolved[fi])
  }
  // H442 kill-timeout no-bisect: a group that ended on a kill-timeout is treated as
  // transiently slow, not too big. Leave unresolved fragments as `missing` for requeue.
  const killBisectBlocked = killedOut && KILL_TIMEOUT_NO_BISECT
  if (killBisectBlocked && pending.length > 1) {
    log(label + ': kill-timeout-no-bisect: not bisecting ' + pending.length + ' fragment(s), routing to transient requeue')
  }
  if (pending.length > 1 && !budgetExhausted() && !killBisectBlocked) {
    const mid = Math.ceil(pending.length / 2)
    // Guard each half independently: an unguarded Promise.all rejects wholesale when one
    // half hard-throws, discarding the OTHER half's already-resolved fragments — the same
    // one-late-failure-wipes-earlier-work class fixed at the selfHeal and translateBatch
    // levels (PR #38/#40), recurring inside the bisection itself.
    // H442: the same `budget` object flows into both halves, so the card's ceiling bounds the
    // TOTAL bisection cascade (both halves share one counter), not each half independently.
    const [a, b] = await Promise.all([
      healGroup(k, pending.slice(0, mid), grp, label + '/A', budget).catch(e => { pending.slice(0, mid).forEach(fi => noteFail(fkey(fi), 'heal-hard-failure: ' + (e && e.message || e))); return null }),
      healGroup(k, pending.slice(mid), grp, label + '/B', budget).catch(e => { pending.slice(mid).forEach(fi => noteFail(fkey(fi), 'heal-hard-failure: ' + (e && e.message || e))); return null }),
    ])
    if (a) Object.assign(resolved, a.resolved)
    if (b) Object.assign(resolved, b.resolved)
    pending = pending.filter(fi => !resolved[fi])
  }
  // Partial credit WITHIN the group too: return what resolved plus the exact missing
  // fragment indices — the old contract (null unless ALL fragments resolved) discarded a
  // group's resolved siblings over one stubborn fragment, the same all-or-nothing shape
  // PR #40 removed one level up.
  return { resolved, missing: pending }
}

// --selfheal fallback: a card the batch could not translate is split (deterministically,
// precomputed in FRAGS) into fragments, GROUPED into budget-sized batches (fragment-grouping
// tier), then each group is translated in ONE agent() call (several fragments per call, same
// multi-card-per-prompt pattern as translateBatch) and the fragments' senses are stitched into
// one card. Groups that never resolve (even solo, after healGroup's own bisection) are SKIPPED,
// not fatal to the whole card — a giant flat headword with no rootmap (e.g. large nominal
// stems like kAla/ka/SrI) can need 40+ groups, where requiring every one to succeed drives
// joint success probability toward zero even at a high per-group success rate. A partial
// result (missing_groups > 0) is still returned so downstream sense-coverage gates
// (audit_coverage.py / ru_coverage.py) can measure and flag exactly what's missing — the same
// philosophy the pipeline already uses for partial per-root RU coverage, just applied within
// one oversized card. Only returns null if NOTHING resolved at all. A partial card carries
// partial:true + missing_fragments (exact 'gN:fM' ids) + missing_groups/total_groups so a
// follow-up can requeue JUST the failed pieces instead of re-running the whole card.
async function selfHeal(k) {
  // H220 observability: a no-fallback selfHeal is the LAST resort after an upstream failure
  // (kill-timeout / missing-or-mismatched-key / fidelity-reject). Don't clobber that specific
  // reason with the generic 'no-selfheal-fallback' — the overwrite hid a kill-gate mass-kill
  // behind a misleading message for a whole session. Only set it when nothing failed yet.
  const groups = FRAGS[k]; if (!groups || !groups.length) { if (!FAIL[k]) noteFail(k, 'no-selfheal-fallback (card did not split or a fragment mask was lossy)'); return null }
  // H442 per-card heal budget: one shared {spent,max} for THIS card, threaded into every group's
  // healGroup and its bisection recursion. max scales off the card's own group count (happy path
  // is ~1 call/group), so a dense card that keeps bisecting fails fast to partial at its ceiling
  // instead of draining the shared window MAX_AGENTS pool and starving the other cards. Disabled
  // (max:null) restores the old unbounded per-card heal.
  const cardBudget = PER_CARD_HEAL_BUDGET
    ? { spent: 0, max: Math.ceil(groups.length * PER_CARD_HEAL_FACTOR) + PER_CARD_HEAL_HEADROOM }
    : { spent: 0, max: null }
  const ftm = FRAG_TM[k] || []            // --tm: per-group cached-senses-or-null, mirrors FRAGS[k]
  const senses = []
  const owners = []             // C-02: parallel to `senses` — the [h, grammar] each came from
  const missingFragments = []   // 'g<gi+1>:f<fi>' identifiers — persisted on the card so a
                                // targeted requeue of JUST the failed fragments is possible
                                // from wf_output alone (the inline path previously recorded
                                // only a count, making a follow-up a full re-run)
  const fragProv = []           // {fsha, senses} per FRESHLY-resolved fragment — harvested by
                                // translation_memory.py build-frags into the fragment TM so the
                                // next run reuses it (ground truth captured at the moment of success)
  // siTag: canonical tag per source sense_ord (FRAGS[k][gi][i].si), fixed to whatever tag the
  // FIRST fragment of that sense_ord reports. Citation-batch continuations of the same oversized
  // sense carry no sense-boundary marker of their own, so the model tags them independently and
  // fabricates fresh incrementing numbers (1,2,3...) that then collide with a sibling rootmap
  // part's REAL different senses in audit_sense_dupes.py's cross-part check. Forcing every
  // fragment sharing a sense_ord onto the same tag is the fix (see PIPELINE_HISTORY.md).
  const siTag = {}
  const applyTag = (si, s) => {
    if (si === undefined || si === null) return
    if (siTag[si] === undefined) siTag[si] = s.tag
    else s.tag = siTag[si]
  }
  for (let gi = 0; gi < groups.length; gi++) {
    const grp = groups[gi]
    const gph = (PHF[k] || [])[gi] || []
    const gtm = ftm[gi] || []
    // Fragments already in the TM are served directly (no agent() call); heal only the rest.
    // A fully-cached group issues zero calls; a partial giant card re-runs only what's missing.
    const uncached = []
    for (let i = 0; i < grp.length; i++) { if (!gtm[i]) uncached.push(i) }
    // A hard agent() failure inside healGroup (thrown, not returned — see translateBatch's
    // comment) must be caught HERE, per group: uncaught, it unwinds out of this whole loop and
    // discards every earlier group's already-accumulated senses along with it (observed live —
    // 45 agent calls ran, several groups plausibly succeeded, yet the card still came back with
    // ZERO senses because one later group's hard failure wiped the local `senses` array before
    // selfHeal could return anything).
    let r = { resolved: {}, missing: [] }
    if (uncached.length) {
      try { r = await healGroup(k, uncached, grp, 'heal:' + k + '#g' + (gi + 1), cardBudget) }
      catch (e) { r = { resolved: {}, missing: uncached }; noteFail(k, 'heal-group-hard-failure g' + (gi + 1) + ': ' + (e && e.message || e)) }
    }
    for (const fi of (r.missing || [])) missingFragments.push('g' + (gi + 1) + ':f' + fi)
    for (let i = 0; i < grp.length; i++) {
      if (gtm[i]) {
        // cached senses are ALREADY restored to source markup (validated at their harvest run);
        // slot them in at their document position — do NOT re-restore (no {Tn} remain). Tag
        // normalization still applies: an older cache entry harvested before this fix may carry
        // a fabricated tag.
        // R6: a served frag-TM slot is v2 -- it carries the PER-SENSE owner harvested at the fresh
        // resolve. v1 (ownerless) rows are a serve-time cache MISS (the gview build drops them), so
        // a served slot restores each sense's real (h, grammar) instead of a null owner.
        {
          const cs = (gtm[i] && gtm[i].senses) || []
          const co = (gtm[i] && gtm[i].owners) || []
          for (let j = 0; j < cs.length; j++) {
            applyTag(grp[i].si, cs[j]); senses.push(cs[j])
            const o = co[j] || [null, null]
            owners.push([o[0] == null ? null : o[0], o[1] == null ? null : o[1]])
          }
        }
        continue
      }
      const card = r.resolved[i]
      if (!card) continue   // an uncached fragment that never resolved — already in missingFragments
      const ph = gph[i] || []
      const fsenses = []
      const fowners = []
      for (const rec of (card.records || [])) {
        for (const f of RESTORE_SPEC.record) if (typeof rec[f] === 'string') rec[f] = restore(rec[f], ph)
        for (const s of (rec.senses || [])) {
          for (const f of RESTORE_SPEC.sense) if (typeof s[f] === 'string') s[f] = restore(s[f], ph)
          applyTag(grp[i].si, s)
          // C-02: keep the OWNING record's (h, grammar) alongside the sense. This loop used to
          // flatten records->senses and drop `rec`, so the stitch below had nothing left to
          // emit and every promoted row read h: null (403 of the 468 came from this lane).
          senses.push(s); owners.push([rec.h, rec.grammar]); fsenses.push(s); fowners.push([rec.h, rec.grammar])
        }
      }
      // R6: emit the PER-SENSE owner into frag_prov so a warm-cache stitch restores ownership.
      if (grp[i].fsha && fsenses.length) fragProv.push({ fsha: grp[i].fsha, senses: fsenses, owners: fowners })
    }
  }
  if (!senses.length) { if (!FAIL[k]) noteFail(k, 'selfheal-nothing-resolved'); return null }
  // B02 (H1339): iast/notes are CARD_REQUIRED -- a stitched card missing them was refused
  // by the save gate / final-schema audit gate, losing the whole healed window.
  const stitched = { key1: k, iast: IASTS[k] || k, notes: '', records: stitchRecords(senses, owners) }
  if (fragProv.length) stitched.frag_prov = fragProv
  if (!missingFragments.length) {
    // fidelity check only meaningful on a COMPLETE heal — a partial result legitimately has
    // fewer citations than the source. Per-fragment token checks already gated each piece;
    // this whole-card count is the belt over those suspenders.
    if (countOf(stitched, /<ls\b/g) !== INPUTS[k].ls || countOf(stitched, /\{#/g) !== INPUTS[k].sk) {
      noteFail(k, 'stitched-fidelity-reject: complete heal, but restored <ls>/{# counts drift from source')
      return null
    }
    // H1152 parity (C1): the counts above run over `german` only (countOf hard-codes s.german),
    // proving the SOURCE echo is faithful — NOT that the translation preserved its spans. The
    // batch accept() lane closed this with a target-field count (translation-fidelity-reject);
    // the heal/presplit lane never did, so a {#..#}/<ls> span kept in `german` but dropped from
    // russian/english (the live H1070 r102 pattern: german 33/33, english 32/33) was stitched and
    // promoted with a Sanskrit/citation span silently missing from the translation column. The
    // presplit lane routes exactly the citation/sense-dense giants most prone to this drop.
    if (countOfField(stitched, TARGET_FIELD, /<ls\b/g) !== INPUTS[k].ls || countOfField(stitched, TARGET_FIELD, /\{#/g) !== INPUTS[k].sk) {
      noteFail(k, 'stitched-translation-fidelity-reject: complete heal, but target-field <ls>/{# counts drift from source')
      return null
    }
  } else {
    stitched.partial = true
    stitched.missing_fragments = missingFragments
    stitched.missing_groups = new Set(missingFragments.map(x => x.split(':')[0])).size
    stitched.total_groups = groups.length
    log('heal:' + k + ' partial — ' + missingFragments.length + ' fragment(s) missing (' + missingFragments.join(', ') + ')')
  }
  return stitched
}

phase('Translate')
// Try a group of cards up to 2 full-group attempts, retrying ONLY the cards still
// unresolved (positional within the shrinking pending set) — one missing/garbled card
// must not re-bill the rest. Returns { resolved, pending } (pending = still-unresolved).
// With BINARY_SPLIT off this is the whole retry story (unchanged from before); with it on,
// a group of >1 cards that still fails after 2 attempts is bisected and each half gets its
// own fresh 2-attempt budget — isolates a single poison card instead of re-billing the
// group around it identically on every retry.
async function resolveGroup(pending, label) {
  const resolved = {}
  let cur = pending.slice()
  for (let attempt = 0; attempt < 2 && cur.length; attempt++) {
    // lean mode: NWS_RULE is non-empty and injected only when the batch has an NWS card
    // (full mode: NWS_RULE is '' and the NWS rule already lives inside CONV_TR).
    const nws = (NWS_RULE && cur.some(k => INPUTS[k].nws)) ? ('\n\n' + NWS_RULE + '\n') : ''
    // H2191: stable-left order, the JS twin of headless_worker.build_prompt --
    // PREAMBLE + CONV_TR (identical on every call) before the window-scoped GRAMMAR,
    // then [nws], then the volatile card blocks (per-card grammar stays in cardBlock).
    const prompt = PREAMBLE + CONV_TR + GRAMMAR + nws + cur.map(cardBlock).join('')
    let res
    try {
      res = await agentKill(prompt, { label: label + '[' + cur.length + ']' + (attempt ? '(retry)' : ''), phase: 'Translate', schema: CARDS_SCHEMA, model: 'claude-sonnet-5', tools: [] }, skelBytesOfKeys(cur), killBudgetForCur(cur))
    } catch (e) {
      if (!isKill(e)) throw e   // real hard failure — propagate as before (translateBatch -> selfheal)
      // Kill: stop RE-billing this whole call — a stall re-times-out identically. Mark the
      // still-pending cards and break so BINARY_SPLIT can isolate the slow one (smaller halves
      // get proportionally smaller budgets), bottoming out to selfHeal per card.
      cur.forEach(k => noteFail(k, e.message))
      log(label + ': ' + e.message + ' — abandoned, routing ' + cur.length + ' card(s) to split/heal')
      break
    }
    if (res && Array.isArray(res.cards)) {
      // Match responses by their echoed key1 ONLY. Positional fallback can silently put
      // content under the wrong headword when a model omits/reorders cards, especially for
      // zero-marker cross-reference stubs where count-based fidelity guards are blind.
      const km = byKey1(res.cards)
      // H220 nominal key-echo tolerance: a masked nominal / no-PWG card carries the CLEAN SLP1
      // headword in its portrait ('key1': "CAyA"), which pulls the model into echoing that
      // instead of the mangled sub-card stem in the '=== CARD <stem> ===' header
      // (_c_ay_a~~h0_zz_pw) — confirmed for leading/interior-underscore stems (_c_ay_a->CAyA,
      // g_ayatr_i->gAyatrI). Recover ONLY when the returned key1 equals nominal_keymap[stem]
      // AND that SLP1 maps to EXACTLY ONE pending stem in this batch (unambiguous) — then
      // re-key the card to the stem. Never positional; NULL for root (PWG) windows
      // (META.nominal false), so test_generated_harness_strict_key_matching stays honest.
      const NKM = (META.nominal && META.nominal_keymap) ? META.nominal_keymap : null
      cur.forEach((k, i) => {
        let cand = km[k]
        if ((cand === undefined || cand === null) && NKM && NKM[k] && NKM[k] !== k) {
          const slp1 = NKM[k]
          const rivals = cur.filter(x => NKM[x] === slp1)
          if (rivals.length === 1) {
            // The model may echo the CLEAN SLP1 headword alone (slp1), OR the SLP1 with the
            // sub-card suffix kept — 'avyAhata~~h0_zz_pw' for the stem 'avy_ahata~~h0_zz_pw'
            // (H255 avy_ahata: SLP1 headword, but the ~~<layer> suffix carried over). Both are
            // unambiguous re-keys to the stem; still gated on META.nominal + rivals===1.
            const sfx = k.includes('~~') ? k.slice(k.indexOf('~~')) : ''
            const hit = (km[slp1] !== undefined && km[slp1] !== null) ? km[slp1]
                      : (sfx && km[slp1 + sfx] !== undefined && km[slp1 + sfx] !== null) ? km[slp1 + sfx]
                      : null
            if (hit) { cand = hit; cand.key1 = k }
          }
        }
        if (cand === undefined || cand === null) { noteFail(k, 'missing-or-mismatched-key'); return }
        const c = accept(cand, k)
        if (c) resolved[k] = c
      })
    } else {
      cur.forEach(k => noteFail(k, res ? 'malformed-response (no cards[])' : 'agent-returned-null'))
    }
    cur = cur.filter(k => !resolved[k])
  }
  if (BINARY_SPLIT && cur.length > 1) {
    const mid = Math.ceil(cur.length / 2)
    // Each half guarded independently — an unguarded Promise.all rejects wholesale on one
    // half's hard throw and discards the other half's resolved cards (see healGroup).
    const empty = h => ({ resolved: {}, pending: h })
    const [a, b] = await Promise.all([
      resolveGroup(cur.slice(0, mid), label + '/A').catch(e => { cur.slice(0, mid).forEach(k => noteFail(k, 'batch-hard-failure: ' + (e && e.message || e))); return empty(cur.slice(0, mid)) }),
      resolveGroup(cur.slice(mid), label + '/B').catch(e => { cur.slice(mid).forEach(k => noteFail(k, 'batch-hard-failure: ' + (e && e.message || e))); return empty(cur.slice(mid)) }),
    ])
    Object.assign(resolved, a.resolved, b.resolved)
    cur = cur.filter(k => !resolved[k])
  }
  return { resolved, pending: cur }
}
async function translateBatch(batch, bi) {
  // A hard agent() failure (e.g. StructuredOutput retry cap exceeded, not just a malformed
  // response our own retry/heal loops already catch) throws instead of returning. Guard
  // resolveGroup AND selfHeal INDEPENDENTLY — a caller that wraps both in one try/catch
  // (as an earlier version of this fix did) swallows a whole-batch failure before --selfheal
  // ever runs, which defeats the fallback for exactly the cards that need it most (observed
  // live: a huge single-card nominal batch hard-failed the main attempt and the heal path,
  // with its precomputed fragment groups, never even got a chance to run). Both paths degrade
  // to "unresolved" on a hard failure — requeue-able, not fatal, and selfHeal still gets tried.
  const resolved = {}, healed = {}
  try {
    let pending = batch.slice()
    try {
      const r = await resolveGroup(batch, 'b' + bi)
      Object.assign(resolved, r.resolved); pending = r.pending
    } catch (e) {
      // fall through to --selfheal below with the full batch still pending
      log('b' + bi + ': whole-batch hard failure (' + (e && e.message || e) + ') — falling through to selfheal')
      batch.forEach(k => noteFail(k, 'batch-hard-failure: ' + (e && e.message || e)))
    }
    // self-healing tier: split-translate-stitch the cards the batch gave up on (no-op unless
    // --selfheal populated FRAGS). Runs only for the few still-failing cards.
    for (const k of pending) {
      let c = null
      try { c = await selfHeal(k) } catch (e) { c = null; noteFail(k, 'selfheal-hard-failure: ' + (e && e.message || e)) }
      if (c) { resolved[k] = c; healed[k] = 1 }
    }
  } catch (e) {
    // ABSOLUTE BACKSTOP — nothing above should throw, but if it does, the batch must
    // still return one row per input key. An uncaught throw here makes parallel() yield
    // null for the whole batch slot, and every key in it VANISHES from the results
    // (save_and_audit.py then drops the null slot on save — the exact silent-loss mode
    // this harness exists to prevent). Cards resolved before the throw are kept.
    batch.forEach(k => { if (!resolved[k] && !FAIL[k]) noteFail(k, 'batch-crash: ' + (e && e.message || e)) })
    log('b' + bi + ': unexpected batch crash (' + (e && e.message || e) + ') — returning accounted rows')
  }
  return batch.map(k => {
    const row = { key: k, card: resolved[k] || null, judge: null, judge_sonnet: null, escalated: !!healed[k] }
    if (!row.card && FAIL[k]) row.error = FAIL[k]
    return row
  })
}
// Pre-split lane (MG 2026-07-02): cards routed at GENERATION time straight to the fragment
// path — their whole-card attempt is a known loss (citation load alone exceeds the whole
// per-batch output budget; the 125-<ls> pwg00 heads failed the retry cap even solo), so
// skipping it converts up-to-5 paid retries into zero. Same selfHeal machinery, same
// partial-credit + missing_fragments contract; presplit:true marks the row's provenance.
async function healOnly(k) {
  let c = null
  try { c = await selfHeal(k) } catch (e) { c = null; noteFail(k, 'selfheal-hard-failure: ' + (e && e.message || e)) }
  const row = { key: k, card: c || null, judge: null, judge_sonnet: null, escalated: !!c, presplit: true }
  if (!row.card && FAIL[k]) row.error = FAIL[k]
  return [row]
}
// H255/H811 low-width staggered dispatch. Runs `thunks` with at most `width` in flight,
// spacing the first `width` starts by `staggerMs` so a degraded generation API isn't hit by
// a thundering herd. On a degraded API a tiny card that completes in ~54s ALONE is inflated
// past the 180s kill CEIL at ~10-wide (the Workflow runtime cap); at <=3-wide it keeps its
// isolated latency. width<=0 or >=len falls back to the runtime parallel(); a thrown thunk
// resolves to null (parallel() parity), and results stay index-aligned with `thunks`.
async function boundedParallel(thunks, width, staggerMs) {
  if (!width || width >= thunks.length) return parallel(thunks)
  const results = new Array(thunks.length).fill(null)
  let next = 0
  const worker = async () => {
    for (let idx = next++; idx < thunks.length; idx = next++) {
      try { results[idx] = await thunks[idx]() } catch (e) { results[idx] = null }
    }
  }
  const workers = []
  for (let w = 0; w < width; w++) {
    if (staggerMs && w > 0) await new Promise(r => setTimeout(r, staggerMs))
    workers.push(worker())
  }
  await Promise.all(workers)
  return results
}
// A Workflow session cannot prove which CLAUDE_CONFIG_DIR it billed or participate in
// the host-wide active-call lock. A profile-bound v2 artifact is therefore executable
// only through headless_worker.py; abort here before the first paid agent() call.
if (META.execution_manifest_schema === 'pwg.headless_execution_manifest.v2') {
  throw new Error('manifest-v2 production is CLI/headless-only; run the execution manifest')
}
// UNITS pairs each parallel slot with the exact keys it owes rows for, so the accounting
// backfill below stays index-correct with the presplit lane appended after the batches.
const UNITS = BATCHES.map((b, i) => ({ keys: b, run: () => translateBatch(b, i) }))
  .concat(PRESPLIT.map(k => ({ keys: [k], run: () => healOnly(k) })))
const grouped = await boundedParallel(UNITS.map(u => u.run), MAX_WIDE, STAGGER_MS)
// TOTAL ACCOUNTING INVARIANT: every selected key appears in `results` exactly once, no
// matter what failed above. parallel() resolves a thrown thunk to null — flat() would
// carry that null into results (crashing the summary below and silently dropping the
// batch's keys at save time). Synthesize accounted null rows for any such unit, then
// backfill any key that STILL isn't present (belt over suspenders).
const out = []
const seen = new Set()
// TM lane first: pre-resolved cards cost nothing and are already accounted for, so seed
// them before backfilling the translated units. tm:true marks provenance for the summary.
for (const k in TM_RESOLVED) { if (!seen.has(k)) { out.push({ key: k, card: TM_RESOLVED[k], judge: null, judge_sonnet: null, escalated: false, tm: true }); seen.add(k) } }
for (const k in DEGENERATE_RESOLVED) { if (!seen.has(k)) { out.push({ key: k, card: DEGENERATE_RESOLVED[k], judge: null, judge_sonnet: null, escalated: false, degenerate_passthrough: true }); seen.add(k) } }
grouped.forEach((rows, i) => {
  if (Array.isArray(rows)) {
    for (const r of rows) if (r && r.key && !seen.has(r.key)) { out.push(r); seen.add(r.key) }
  } else {
    log('u' + i + ': unit thunk resolved null — synthesizing accounted rows for its ' + UNITS[i].keys.length + ' key(s)')
    for (const k of UNITS[i].keys) if (!seen.has(k)) { out.push({ key: k, card: null, judge: null, judge_sonnet: null, escalated: false, error: FAIL[k] || 'batch-thunk-null' }); seen.add(k) }
  }
})
for (const k of META.selected_keys) if (!seen.has(k)) { out.push({ key: k, card: null, judge: null, judge_sonnet: null, escalated: false, error: FAIL[k] || 'unaccounted-key (should be impossible — report this)' }); seen.add(k) }
// Compact summary first so the orchestrator can read counts (ok/null/healed + the exact
// null keys to requeue) WITHOUT parsing the full results blob. results are still carried
// for save_and_audit/promote (the workflow runtime can't write files -> must be returned).
// `failures` maps every null key to its last-known reason; `partial_keys` lists healed
// cards that carry partial:true (usable but incomplete — see missing_fragments on the card).
const _ok = out.filter(r => r.card).length
const _failures = {}
for (const r of out) if (!r.card) _failures[r.key] = r.error || FAIL[r.key] || 'unknown'
const summary = { root: META.root, lang: META.lang, cards: out.length, ok: _ok,
                  null: out.length - _ok, healed: out.filter(r => r.escalated).length,
                  presplit: PRESPLIT.length, tm: out.filter(r => r.tm).length,
                  degenerate_passthrough: out.filter(r => r.degenerate_passthrough).length,
                  frag_tm_fragments: META.frag_tm_fragments || 0,
                  // Total counters stay backwards-compatible; lane counters make starvation
                  // and the binding pool directly observable.
                  agents_spent: AGENTS_SPENT, max_agents: (KILL_SWITCH ? MAX_AGENTS : null),
                  budget_kill_switch_tripped: BUDGET_TRIPPED,
                  translate_agents_spent: TRANSLATE_AGENTS_SPENT,
                  max_translate_agents: (KILL_SWITCH ? MAX_TRANSLATE_AGENTS : null),
                  translate_budget_tripped: TRANSLATE_BUDGET_TRIPPED,
                  heal_agents_spent: HEAL_AGENTS_SPENT,
                  max_heal_agents: (KILL_SWITCH ? MAX_HEAL_AGENTS : null),
                  heal_budget_tripped: HEAL_BUDGET_TRIPPED,
                  // H462: returned telemetry (previously log-only, hand-counted from
                  // transcripts). kill_bisect_blocked counts heal groups whose kill-timeout
                  // was routed to requeue instead of bisection (KILL_TIMEOUT_NO_BISECT).
                  kill_timeouts: KILL_TIMEOUTS, conn_errors: CONN_ERRORS,
                  heal_calls: HEAL_CALLS, kill_bisect_blocked: KILL_BISECT_BLOCKED,
                  // H960 SAN-LOSS shortfall telemetry (SOFT — no reject unless
                  // SANLOSS_HARD_REJECT). sanloss_shortfalls counts kept-but-short cards;
                  // sanloss_detail lists {key,expected,emitted,dropped} for the audit join.
                  sanloss_shortfalls: SANLOSS_SHORTFALLS, sanloss_hard_reject: SANLOSS_HARD_REJECT,
                  sanloss_detail: SANLOSS_DETAIL,
                  // H960 grammar-{Tn} multiset telemetry (SOFT — no reject unless TNMASK_HARD_REJECT).
                  tnmask_mismatches: TNMASK_MISMATCHES, tnmask_hard_reject: TNMASK_HARD_REJECT,
                  tnmask_detail: TNMASK_DETAIL,
                  german_anchor_repairs: GERMAN_ANCHOR_REPAIRS,
                  german_anchor_detail: GERMAN_ANCHOR_DETAIL,
                  // H3665: repairs 0 + invocations 0 + not_reached [k] == the repair never ran
                  // on a card that died a fidelity death (the `hasita` no_pwg_w09 shape).
                  german_anchor_invocations: GERMAN_ANCHOR_INVOCATIONS,
                  german_anchor_not_reached: GERMAN_ANCHOR_NOT_REACHED,
                  // H3675: the target-side twin's telemetry.
                  target_anchor_repairs: TARGET_ANCHOR_REPAIRS,
                  target_anchor_invocations: TARGET_ANCHOR_INVOCATIONS,
                  target_anchor_detail: TARGET_ANCHOR_DETAIL,
                  null_keys: out.filter(r => !r.card).map(r => r.key),
                  partial_keys: out.filter(r => r.card && r.card.partial).map(r => r.key),
                  failures: _failures }
return { meta: META, summary, results: out }
