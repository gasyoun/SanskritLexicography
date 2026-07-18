// AUTO-DERIVED v2 (batched + masked, canonical output) from run_pilot_wf.js - root=_nominal.
// Several masked cards per agent call; {Tn} restored to source markup in-JS so the
// returned result is a canonical wf_output.json. See TLONLY_PROTOTYPE.md.
export const meta = {
  name: 'pwgru-opt2-_nominal',
  description: 'batched+masked translation-only PWG->Russian; amortized per-call overhead + masked I/O, {Tn} restored in-JS to canonical cards',
  phases: [{ title: 'Translate', detail: 'Sonnet: N masked cards per call -> rich cards; {Tn} restored to markup' }],
}

const CONV_TR = "You are producing the Russian scholarly entry for one PWG headword (Petersburg Sanskrit Dictionary, B\u00f6htlingk-Roth 1855-75).\n\npwg_ru CONVENTIONS (from B\u00f6htlingk-Roth's own prefaces + project decisions \u2014 follow EXACTLY):\n- REGISTER: scholarly-philological. Faithful to PWG's density and precision; this is a printed scholarly dictionary.\n- Translate into Russian the natural-language gloss prose. This is German in PWG/PW/SCH/PWKVN and most NWS sub-sources, but the NWS layer ALSO carries English (MW, Olivelle, Keller, Hoernle, BHSD, Sircar) and French (Renou, Padoux, Caland, Rivelex) glosses \u2014 translate each gloss FROM ITS OWN language, never relayed through German. A gloss given in two/three languages (e.g. \"riz cuit; cooked rice; gekochter Reis\") is ONE sense \u2014 render it once, not thrice (Guard 7).\n- KEEP VERBATIM (never translate or transliterate): Sanskrit (IAST / Devanagari); the literary-source sigla (\u1e5aV., MBH., M., AK., H., \u2026); the German grammatical abbreviations (m., f., n., Pl., Du., adj., \u2026); the German lexicographic/meta abbreviations inside <ab>\u2026</ab> (Bed. = Bedeutung, Schol., s.v., u.s.w. \u2014 keep the token, NEVER expand it to its Russian meaning); and <is>\u2026</is> italic source text (a source/siglum reference \u2014 keep verbatim, NEVER wrap as {%\u2026%} German gloss). They stay in PWG's Latin/German form.\n- TWO-SOURCE PRINCIPLE (B&R's own): a sense backed by a TEXT citation (\u1e5aV, MBH, M, \u2026) is demonstrable usage = attested; a sense from a ko\u015ba/grammarian only (Amarako\u015ba AK, Hemacandra H, P\u0101\u1e47ini P, Medin\u012b Med.) is Indian-lexicographic \u2014 render it but mark source_type=lexicographic.\n- VEDIC senses are 19th-c. European philology and may be superseded; render faithfully; if the German itself hedges, keep the hedge.\n\nINPUTS for each headword are INLINED below per card (its masked German skeleton + portrait). Do NOT open files, do NOT call any tools, do NOT list directories, do NOT supply senses from memory \u2014 translate EXACTLY what is inlined, nothing else.\n\nTASK: for EACH record (homonym) and EACH sense/sub-sense in the tree, write the Russian rendering.\n- Use the corpus candidates as the PRIMARY evidence for word choice (they are attested, 84% precision; translation-weighted). Where SEVERAL near-synonyms fit, DISCRIMINATE them \u00e0 la Apresjan: pick the one(s) right for THIS sense and state the differentia (semantic / combinatorial / stratum-connotational) briefly. Prefer renderings attested in the sense's CITED stratum (a \u1e5aV-cited sense \u2192 the Vedic corpus renderings). EVIDENCE WEIGHT: if the portrait's corpus_synonyms carries evidence_scope='prefixed-form' or 'root', the candidates are direct evidence for THIS headword \u2014 use them as primary. If evidence_scope starts with 'root-fallback' (a split prefixed-verb sub-card whose own surface form is not in the corpus), the candidates are the BARE ROOT's \u2014 treat them as a weak hint only and let the German gloss of the prefixed verb govern; do not force a root-meaning synonym onto a prefix that has shifted the sense.\n- Mark equivalence_type: a 1-2 word equivalent vs an explanatory gloss (\u0442\u043e\u043b\u043a\u043e\u0432\u0430\u043d\u0438\u0435).\n- Keep the German sense beside your Russian (side-by-side).\n\nHARD RULES (the judge fails the card otherwise):\n1. NO FABRICATION \u2014 never output a sense, sub-sense, or tag that is not an actual division in the raw German. Tags must match the raw exactly; do not invent, split, or merge senses (no added \"epic\"/\"vedic\" sub-sense the source lacks).\n2. COMPLETE COVERAGE \u2014 render EVERY sense the raw card contains, in order: every numbered 1)/2), every lettered a)/b) sub-sense, AND any etymology / cross-reference / \"personif.\" note (render the note too, with a short Russian gloss). Skip nothing.\n3. SIGLA UNTOUCHED \u2014 never translate or transliterate ANY siglum or abbreviation, including COMMENTATOR sigla (S\u0101y., Schol., Sch., Comm.), grammar abbrevs (m./f./Pl./Du.), and German lexicographic/meta abbreviations inside <ab>\u2026</ab> (Bed., Schol., s.v.) \u2014 keep the abbreviation token verbatim, NEVER expand it (e.g. <ab>Bed.</ab> stays \u00abBed.\u00bb, not \u00ab\u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0435\u043c\u00bb). <is>\u2026</is> italic source text is a verbatim siglum, NEVER {%\u2026%} gloss (do not render <is> inside {%\u2026%}). They stay verbatim in PWG form; let no German or English word leak into the Russian. MARKUP DELIMITERS VERBATIM: in the german field reproduce the raw record's own delimiters EXACTLY \u2014 keep every {#\u2026#} around Sanskrit and every <ls>\u2026</ls>, <ab>\u2026</ab>, <lex>\u2026</lex>, <is>\u2026</is> tag as-is; do NOT strip them to plain text, do NOT transliterate {#\u2026#} to bare IAST, do NOT \"clean\"/\"trim\" the markup. Keep any Sanskrit you cite in the russian field wrapped in {#\u2026#} too. The deterministic fidelity gate counts these tokens: a card that loses >10% of its <ls> or >15% of its {#\u2026#} spans is REJECTED.\n4. ALL RECORDS, INCLUDING NACHTR\u00c4GE \u2014 a headword is often a MAIN record plus one or more ADDENDA/NACHTR\u00c4GE records (each marked in the raw input). These do not repeat the word; they PATCH the main entry \u2014 \"to sense 3 add citation X\", \"sense 10: read \u2026 instead of \u2026\", an etymology tail, a new astrological/numeric sense. Render EVERY record completely and EVERY addendum in full, including its tail (etymology, cross-reference, corrigendum). Addenda are first-class \u2014 never drop, summarise, or truncate them. Key each addendum sense to the main-entry sense number it patches. One addendum can itself carry SEVERAL numbered patch-items (1a, 2a, 3a, \u2026) \u2014 render EVERY item; dropping any single patch fails coverage.\n5. NWS LAYER \u2014 USE THE AUTHORITATIVE PRE-PARSED OWNER MAP. The input contains a section \"=== LAYER: NWS \u2014 PRE-PARSED OWNER MAP (AUTHORITATIVE, N entries) ===\" listing numbered entries  N. [NWS: OWNER] {#lemma#} [tag] gloss . Emit EXACTLY ONE NWS card row per numbered entry, IN THAT ORDER; copy each entry's [NWS: OWNER] token VERBATIM as that row's LAST citation; translate the gloss from its own language; keep {#lemma#}/IAST/sigla. Do NOT re-derive, swap, merge, drop, or re-order owners, and do NOT read owners off the raw fragment \u2014 the map is the single source of truth (this makes the F12 slide impossible). If no owner map is present, fall back to: ONE ENTRY PER SOURCE, OWNER-CITATION KEPT (the deterministic auditor nws_split.py checks this; it fails the card otherwise). The \"=== LAYER: NWS ===\" fragment packs many sub-dictionaries into one string in the shape  [LEMMA] TAG > gloss .. OWNER : page >  [LEMMA] TAG > gloss .. OWNER : page > \u2026  \u2014 the diasystem TAG PRECEDES each gloss and the OWNER citation (Author year : page, e.g. \"Gra\u00dfmann 1873 (1996) : 70\", \"Geldner 1907 : 10\", \"MW : 47 (s.v. ap)\") CLOSES it. Output ONE sense per such entry, in source order: NEVER merge two owners into one, never drop the owner, and never compress several \"Wasser=water\" attestations into a single row. Each NWS sense MUST (a) be tagged so it reads as NWS (prefix \"[NWS:]\" or tag \"NWS\"), and (b) keep its OWNER citation VERBATIM as the LAST citation of that sense (so the auditor can read the owner). CRITICAL reading direction (failure F12): the owner comes AFTER the gloss \u2014 do NOT slide it onto the next gloss; \"X > Y : p\" means Y:p owns X, not the following entry. Sub-lemmas the NWS lists (separate compound headwords, e.g. apa\u1e25sa\u1e43varta, abdurga) are first-class entries too \u2014 render each as its own NWS row, never as a sense of the head.\n6. TRANSLATE, DON'T ANNOTATE \u2014 render EXACTLY what the German states, no more. Within a sense, NEVER add an interpretive gloss, a parenthetical domain clarification, a scope qualifier, or a scholarly attribution (\u00ab\u0438 \u0434\u0440\u0443\u0433\u0438\u043c\u0438\u00bb, \u00ab\u0438 \u0442\u043e\u043c\u0443 \u043f\u043e\u0434\u043e\u0431\u043d\u043e\u0435\u00bb, \u00ab(\u043e \u043d\u0435\u0431\u0435\u0441\u043d\u044b\u0445 \u0442\u0435\u043b\u0430\u0445)\u00bb) that the German does not itself contain. If the German credits a derivation to ONE authority (e.g. \u00abwird von BENFEY \u2026 zur\u00fcckgef\u00fchrt\u00bb), name ONLY that authority \u2014 do NOT generalise \u00abBENFEY\u00bb to \u00abBENFEY \u0438 \u0434\u0440\u0443\u0433\u0438\u043c\u0438\u00bb. When unsure, translate LESS, not more: an unsourced addition is a fidelity defect exactly like an omission.\n7. GOVERNMENT MARKERS VERBATIM \u2014 when the German gloss carries a parenthesized case-government note (e.g. `(<ab>loc.</ab>)`, `(<ab>loc.</ab> und <ab>gen.</ab>)`) or a `mit dem <ab>case.</ab>` phrase, copy the case abbreviation into the sense's `government` field exactly as it appears in the source (one entry per marker found) \u2014 NEVER invent, guess, generalize, or add a case the German does not state. Leave `government` an empty array when the German carries no such marker. This is deterministic \u2014 do not paraphrase the case into the Kochergina idiom or any other rendering.\n\nRENDERING GUIDANCE \u2014 Sanskrit microstructure (from the lexicography-manual harvest, see ../glossaries/de_ru_translation_aids.md; quality, judged softly \u2014 these refine wording, they do NOT add/drop senses):\n- COMPOUNDS (sam\u0101sa) are right-headed: build the Russian off the vigraha, head = the SECOND member. tatpuru\u1e63a asi-kalaha \u2192 \u00ab\u0431\u043e\u0439 \u043c\u0435\u0447\u043e\u043c\u00bb (head \u00ab\u0431\u043e\u0439\u00bb); NEVER a member-by-member calque off the first constituent. bahuvr\u012bhi is exocentric (a possessor OUTSIDE the compound): hata-putra- \u2192 \u00ab\u0442\u0430, \u0443 \u043a\u043e\u0433\u043e \u0443\u0431\u0438\u0442\u044b \u0441\u044b\u043d\u043e\u0432\u044c\u044f / \u0447\u044c\u0438 \u0441\u044b\u043d\u043e\u0432\u044c\u044f \u0443\u0431\u0438\u0442\u044b\u00bb, not the literal sum. \u2026-\u0101di / \u2026-prabh\u1e5bti = an OPEN class = the hypernym of its members \u2192 \u00abX \u0438 \u0442\u043e\u043c\u0443 \u043f\u043e\u0434\u043e\u0431\u043d\u043e\u0435 / \u0438 \u043f\u0440\u043e\u0447\u0435\u0435\u00bb, never a closed list. Split an over-long stacked compound into several Russian clauses, not one calque (Apte/Gillon, Inglese-Geupel).\n- CORRELATIVES (yad\u2026tad): when the German keeps the correlative order, render a PREPOSED Russian correlative \u2014 \u043a\u0442\u043e\u2026\u0442\u043e\u0442, \u0447\u0442\u043e\u2026\u0442\u043e, \u043a\u0430\u043a\u043e\u0439\u2026\u0442\u0430\u043a\u043e\u0439, \u0447\u0435\u0439\u2026\u0442\u043e\u0433\u043e, \u0433\u0434\u0435\u2026\u0442\u0430\u043c, \u043a\u0443\u0434\u0430\u2026\u0442\u0443\u0434\u0430, \u043a\u043e\u0433\u0434\u0430\u2026\u0442\u043e\u0433\u0434\u0430, \u043a\u0430\u043a\u2026\u0442\u0430\u043a, \u0441\u043a\u043e\u043b\u044c\u043a\u043e\u2026\u0441\u0442\u043e\u043b\u044c\u043a\u043e, \u0447\u0435\u043c\u2026\u0442\u0435\u043c. Doubled yo ya\u1e25 \u2192 \u00ab\u043a\u0442\u043e \u0431\u044b \u043d\u0438 / \u0432\u0441\u044f\u043a\u0438\u0439, \u043a\u0442\u043e\u00bb; y\u0101vat\u2026t\u0101vat \u2192 \u00ab\u043f\u043e\u043a\u0430\u2026\u0434\u043e \u0442\u0435\u0445 \u043f\u043e\u0440\u00bb; yadi\u2026tarhi \u2192 \u00ab\u0435\u0441\u043b\u0438\u2026\u0442\u043e\u00bb. Keep BOTH pairs; do not flip which clause is asserted (Mitrenina, Zaliznyak-Paducheva, Ruppel).\n- \u015a\u0100STRIC FORMULAS \u2014 fixed dry Russian, do not re-translate per occurrence: iti artha\u1e25 \u2192 \u00ab\u0442\u043e \u0435\u0441\u0442\u044c; \u0442\u0430\u043a\u043e\u0432 \u0441\u043c\u044b\u0441\u043b\u00bb; ity uktam \u2192 \u00ab\u0441\u043a\u0430\u0437\u0430\u043d\u043e\u00bb; anena \u2026 vivak\u1e63itam \u2192 \u00ab\u044d\u0442\u0438\u043c \u043e\u043d \u0445\u043e\u0447\u0435\u0442 \u0441\u043a\u0430\u0437\u0430\u0442\u044c\u00bb; X-bh\u0101va\u1e25 / X-tvam \u2192 \u00ab\u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435/\u0441\u0432\u043e\u0439\u0441\u0442\u0432\u043e X\u00bb. Their presence marks scholastic register \u2192 flat terminological Russian (Tubb).\n- SYNONYM CARDINALITY: render a German synonym-string (Glanz, Schimmer, Pracht) as a Russian synonym-string of EQUAL cardinality \u2014 never collapse n near-synonyms to one word; pick by register, default to the neutral dominant (Apresjan, Baalbaki).\n- PUNCTUATION carries sense-grouping: comma = interchangeable synonyms WITHIN one sense; semicolon = a boundary between non-interchangeable senses. Preserve PWG's comma/semicolon exactly in the Russian (Hartmann & James).\n- MANNER/POSITION: where Russian grammatically forces a manner/position verb (\u0438\u0434\u0442\u0438/\u043f\u043e\u043b\u0437\u0442\u0438/\u043b\u0435\u0442\u0435\u0442\u044c; \u0441\u0442\u043e\u044f\u0442\u044c/\u043b\u0435\u0436\u0430\u0442\u044c/\u0432\u0438\u0441\u0435\u0442\u044c) that the German leaves open, choose from the cited context; a wrong neutral default (e.g. \u00ab\u043d\u0430\u0445\u043e\u0434\u0438\u0442\u044c\u0441\u044f\u00bb, \u00ab\u043b\u0435\u0436\u0430\u0442\u044c\u00bb for something that hangs) is grammatical-but-false (Apresjan).\n- NON-CIRCULAR GLOSSES: a Russian gloss must be clearer than the Sanskrit/PWG headword. Avoid circular or cryptographic paraphrases, bare transliterated Sanskrit, or a rarer Russian term where a plain explanatory gloss is needed (Apresjan).\n\nReturn ONLY the structured object."
const PREAMBLE = "=== MASKED + BATCHED REGIME (read first \u2014 overrides input-format details below) ===\nYou are given SEVERAL headwords at once, each in its own '=== CARD <key> ===' block.\nEach card's source German has been MASKED: every untranslatable span (Sanskrit {#..#},\nsource refs <ls>, abbreviations <ab>, italic <is>, grammar <lex>) is replaced by a {Tn}\nplaceholder token. You see ONLY the translatable German gloss prose + {Tn} tokens + the\nsense numbering. A Python post-step restores every {Tn} to its exact original markup.\n\nTherefore, wherever the rules below say \"keep {#..#}/<ls>/<ab> verbatim\" or \"reproduce\nthe markup delimiters EXACTLY\", that now means: **keep every {Tn} placeholder verbatim,\nunchanged and in its original order** \u2014 never invent, renumber, drop, expand, merge, or\nalter a {Tn}, and never type any Sanskrit, siglum, or markup yourself. In the `german`\nfield, reproduce the masked skeleton you were given for that sense EXACTLY (its German +\nits {Tn} tokens). In the `russian` field, put your translation, placing the relevant {Tn}\ntokens where the source cited a masked span. Translate EACH card; return one object per\nheadword in `cards`, with `key1` matching its '=== CARD <key> ===' header. Omit nothing.\n\n"
const GRAMMAR = ""
const GRAMMARS = {"nakzatra": "=== GRAMMAR (Whitney nominal) \u2014 the headword's declension class and \u00a7\u00a7; use to inform grammatical notes and flag irregular forms; NEVER let grammar override a corpus- or German-attested sense ===\nheadword nakzatra [n.]: a-stem, Whitney \u00a7\u00a7326\u2013334 (paradigm \u00a7330)\n  derivation ref: \u00a7\u00a71136\u20131245\n\n", "sarvatra": "=== GRAMMAR (Whitney nominal) \u2014 the headword's declension class and \u00a7\u00a7; use to inform grammatical notes and flag irregular forms; NEVER let grammar override a corpus- or German-attested sense ===\nheadword sarvatra [adj.]: a-stem, Whitney \u00a7\u00a7326\u2013334 (paradigm \u00a7330)\n  flags: tri_gender_adj\n  derivation ref: \u00a7\u00a71136\u20131245\n\n", "sakft": "=== GRAMMAR (Whitney nominal) \u2014 the headword's declension class and \u00a7\u00a7; use to inform grammatical notes and flag irregular forms; NEVER let grammar override a corpus- or German-attested sense ===\nheadword sakft [adv.]: indeclinable, Whitney \u00a7\u00a71096\u20131135 (paradigm \u2014)\n  compound members (MW k2): sakft \u2192 sa + kft\n  compound formation: \u00a7\u00a71246\u20131316\n  flags: compound:2_members\n  derivation ref: \u00a7\u00a71136\u20131245\n\n"}
const NWS_RULE = ""
const CARDS_SCHEMA = {"type": "object", "additionalProperties": false, "required": ["cards"], "properties": {"cards": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/card"}}}, "$defs": {"card": {"type": "object", "additionalProperties": false, "required": ["key1", "iast", "records", "notes"], "properties": {"key1": {"type": "string", "minLength": 1}, "iast": {"type": "string"}, "records": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/record"}}, "notes": {"type": "string"}}}, "record": {"type": "object", "additionalProperties": false, "required": ["h", "grammar", "senses"], "properties": {"h": {"type": "string"}, "grammar": {"type": "string", "description": "POS/gender as PWG, verbatim where applicable."}, "senses": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/sense"}}}}, "sense": {"type": "object", "additionalProperties": false, "required": ["tag", "german", "russian"], "properties": {"tag": {"type": "string", "minLength": 1}, "german": {"type": "string", "description": "The PWG German for this sense, with the source's {#\u2026#} Sanskrit delimiters and <ls>/<ab>/<lex>/<is> markup kept VERBATIM \u2014 not stripped to plain text, not transliterated to bare IAST."}, "russian": {"type": "string", "description": "The Russian rendering in scholarly register."}, "equivalence_type": {"enum": ["equivalent", "explanatory"]}, "source_type": {"enum": ["attested", "lexicographic", "mixed"]}, "stratum": {"type": "string", "description": "Stratum used, such as Vedic, Epic / early-Classical, Classical, Medieval, or empty."}, "differentia": {"type": "string", "description": "Apresjan near-synonym discrimination note, or empty when no discrimination was needed."}}}}}
const BATCHES = [["nakzatra"], ["sarvatra"], ["sakft"]]
const INPUTS = {"nakzatra": {"skeleton": "=== LAYER: PWG \u2014 MAIN ENTRY (B\u00f6htlingk-Roth, large) ===\n\n{T1}\u00a6 {T2}. {T3}\n{T140} 1\u3009 {%Gestirn%} {T4} (auch von der Sonne gebraucht) {T5}. {T6}. {T7} ({T8}) {T9} {T10}. {T11} {T12}. {T13} {T14}. {T15}. {T16}. {%Sterne%} {T17}. {T18}. {T19} {T20}. {T21} {T22}. {T23}. {T24}. {T25}. {T26}. {T27}. {T28}. {T29}. {T30}. {T31}. {T32}. {T33}. {T34} {T35}. {T36} {T37}. {T38}. {T39} {T40}. {T41}. Diese f\u00fcnf bilden bei den {T42} die Gruppe der {T43} {T44}. {T45} {T46}. {T47} {T48}. {T49}. {T50}. {T51}. {T52} {T53}. {T54}. {T55}. {T56} {T57}. Ein Mal {T58}: {T59} {T60}. {T61} {%aus einem Stern bestehend%} {T62}. {T63}. {T64}.\n{T141}\u2014 2\u3009 im {T65} {%die Mondstationen%}; in der \u00e4lteren Zeit (aber auch noch im {T66}) 27, sp\u00e4ter 28 an der Zahl. Dieselben werden in der Folge auch als {%Gemahlinnen des Mondes%}, als T\u00f6chter {T67}\u02bcs, augfefasst. {T68}. {T69}. {T70}. {T71}. {T72}. {T73}. {T74}. {T75}. {T76}. {T77}, {T78}. {T79} {T80} {T81} {T82}. {T83}. {T84}. {T85}. {T86} {T87}. Die Namen derselben {T88} {T89} {T90} {T91}, {T92}. {T93}, Die vedischen Nachrichten von den Nakshatra.\n{T142}\u2014 3\u3009 {%Perle%} {T94}_im_{T95} \u2014 Was die Etymologie betrifft, so l\u00e4sst sich gegen die von {T96}_in_{T97} vorgebrachte ({T98} + {T99}) einwenden, dass {%W\u00e4chter der Nacht%} nicht auf die Sonne passt, welche in den \u00e4ltesten Texten vorzugsweise {T100} genannt wird. Die Gleichsetzung von {T101} mit {T102} erregt gleichfalls Bedenken. Eher liesse sich noch an eine Zur\u00fcckf\u00fchrung auf {T103} ({T104} {T105}. {T106}.) denken, dann w\u00e4ren die Gestirne {%die am Himmel Heraufkommenden%}. Die spielende Zerlegung in {T107} + {T108} findet sich {T109}. {T110}. {T111}. {T112}.\n{T143}\u2014 {T113} {T114}.\n\n=== LAYER: PW \u2014 B\u00f6htlingk k\u00fcrzere Fassung (revision of PWG; may correct gender/sense) ===\n\n{T115}\u00a6 {T116}\n{T144}\u2014 1\u3009 {%Gestirn, Stern;%} {T117} {%die Sonne und die Sterne%} ({T118}) Einmal {T119} als Personification. Am Ende eines {T120} {T121} {T122}\n{T145}\u2014 2\u3009 {%Mondhaus,%} deren in der \u00e4lteren Zeit 27, sp\u00e4ter 28 angenommen werden. Personificirt als T\u00f6chter {T123}\u02bcs und Gattinnen des Mondes.\n{T146}\u2014 3\u3009 *{%Perle%} {T124}. {T125} {T126} 3\u3009.\n\n=== LAYER: PW \u2014 B\u00f6htlingk k\u00fcrzere Fassung (revision of PWG; may correct gender/sense) ===\n\n{T127}\u00a6 {T128} {T129} eines {T130} {T131}.{T147}\n\n=== LAYER: PW \u2014 B\u00f6htlingk k\u00fcrzere Fassung (revision of PWG; may correct gender/sense) ===\n\n{T132}\u00a6 III. 5.{T148}\n\n=== LAYER: SCH \u2014 Schmidt Nachtr\u00e4ge 1928 (pure addenda to PW; \u00b0=new vs pw, *=first attestation) ===\n\n{%Nak\u1e63atra%}\u00a6 m. N. pr. eines Ek\u0101da\u015b\u0101\u1e45gin, {T133} {part=,seq=16531,type=,n=2}\n\n=== LAYER: PWKVN \u2014 PWK variant supplement (keyed to PW sense numbers) ===\n\n{T134}\u00a6 {T135} {T136} eines {T137} {T138}.\n\n=== LAYER: PWKVN \u2014 PWK variant supplement (keyed to PW sense numbers) ===\n\n{T139}\u00a6 III. 5.", "portrait": "[\n {\n  \"schema_version\": \"pwg_ru.lexicographic_portrait.v1\",\n  \"key1\": \"nakzatra\",\n  \"key2\": \"na/kzatra\",\n  \"h\": \"\",\n  \"iast\": \"nak\u1e63atra\",\n  \"pos\": [\n   \"n.\"\n  ],\n  \"diasystem\": [\n   \"Classical\",\n   \"Epic / early-Classical\",\n   \"Vedic\"\n  ],\n  \"labels\": [\n   \"collective, collectively\",\n   \"compare\",\n   \"in general\",\n   \"masculine\",\n   \"see\",\n   \"special, particular\"\n  ],\n  \"senses\": [\n   {\n    \"n\": \"0\",\n    \"sub\": null,\n    \"equivalents_de\": [],\n    \"gloss_de\": \"\u00a6 U\u1e46\u0100DIS. 3,105 . n\",\n    \"equivalence_type\": \"explanatory\",\n    \"grammar\": [\n     \"n.\"\n    ],\n    \"ab_labels\": [],\n    \"diasystem\": [],\n    \"citations\": [\n     \"U\u1e46\u0100DIS\"\n    ],\n    \"citations_resolved\": {\n     \"U\u1e46\u0100DIS\": \"? [Cologne Addition]\"\n    },\n    \"strata\": {},\n    \"examples_sa\": [\n     \"na/kzatra\"\n    ]\n   },\n   {\n    \"n\": \"1\",\n    \"sub\": null,\n    \"equivalents_de\": [\n     \"Gestirn\"\n    ],\n    \"gloss_de\": \"1\u3009 Gestirn \u00fcberh. (auch von der Sonne gebraucht) AK. 1,1,2,22 . H. 107 . ( coll. ) \u1e5aV. 7,86,1 . 81,2 . 10,88,13 . 111,7 . 156,4 . Sterne 1,50,2 . 3,54,19 . 10,68,11 . 85,2 . AV. 6,128,1 . 3 . 7,13,1 .\",\n    \"equivalence_type\": \"equivalent\",\n    \"grammar\": [],\n    \"ab_labels\": [\n     \"collective, collectively\",\n     \"in general\",\n     \"masculine\"\n    ],\n    \"diasystem\": [\n     \"Classical\",\n     \"Epic / early-Classical\",\n     \"Vedic\"\n    ],\n    \"citations\": [\n     \"AIT. BR\",\n     \"AK\",\n     \"AV\",\n     \"H\",\n     \"HARIV\",\n     \"HI\u1e0c\",\n     \"K\u0100TY. \u015aR\",\n     \"L\u0100\u1e6cY\",\n     \"M\",\n     \"MBH\",\n     \"N\",\n     \"SU\u015aR\",\n     \"VS\",\n     \"\u0100\u015aV. G\u1e5aHY\",\n     \"\u015aAT. BR\",\n     \"\u1e5aV\"\n    ],\n    \"citations_resolved\": {\n     \"AIT. BR\": \"AITAREYABR\u0100HMA\u1e46A. Citirt nach den 8 Pa\u00f1cik\u0101 (einer \u00e4usseren Abtheilung, in welche die 40 nach sachlichen R\u00fccksichten gebildeten Adhy\u0101ya zerlegt sind) und den innerhalb der Pa\u00f1cik\u0101 durchlaufenden Kapitelzahlen. Hdschr. S\u0100YA\u1e46A'S Commentar dazu. Hdschr.\",\n     \"AK\": \"AMARAKO\u1e62A nach der Ausgabe von COLEBROOKE und LOISELEUR DESLONGCHAMPS (GILD. Bibl. 251. 253).\",\n     \"AV\": \"ATHARVAVEDASAM\u0303HIT\u0100, herausg. von R. ROTH und W. D. WHITNEY. Berlin bei F. D\u00dcMMLER. 1855. 8\u00ba. In den ersten Bogen des W\u00f6rter- buchs finden sich mehrere Citate, deren Zahlen mit der in der Aus- gabe angenommenen Z\u00e4hlung nicht ganz zusammentreffen. Man kann den Unterschied dadurch ausgleichen, dass man in den zusammen- gesetzten Liedern (Pary\u0101yas\u016bkta), welche in der Ausgabe als Ein- heiten gez\u00e4hlt sind, die Unterabtheilungen (Strophen) als besondere Lieder z\u00e4hlt.\",\n     \"H\": \"HEMACANDRA'S ABHIDH\u0100NACINT\u0100MA\u1e46I, ein systematisch angeordnetes synonymisches Lexicon. Herausgegeben, \u00fcbersetzt und mit Anmer- kungen begleitet von OTTO B\u00d6HTLINGK und CHARLES RIEU. St. Peters- burg 1847.\",\n     \"HARIV\": \"HARIVA\u1e42\u015aA im 4ten Bande des MBH. Aus diesem Werke haben wir die Nomina propria mit Benutzung des Index in der LANGLOIS'- schen Uebersetzung (GILD. Bibl. 122) aufgenommen.\",\n     \"HI\u1e0c\": \"HI\u1e0cIMBAVADHA in BOPP'S Ardschuna's Reise zu Indra's Himmel, nebst anderen Episoden des Maha-Bharata. Berlin 1824.\",\n     \"K\u0100TY. \u015aR\": \"K\u0100TY\u0100YANA'S \u015aRAUTAS\u016aTR\u0100\u1e46I. 26 Adhy\u0101ya. Hdschr.\",\n     \"L\u0100\u1e6cY\": \"L\u0100\u1e6cY\u0100YANA'S S\u016aTRA zum SV. Hdschr.\",\n     \"M\": \"MANU'S Gesetzbuch in der Ausg. von LOISELEUR DESLONGCHAMPS (GILD. Bibl. 289).\",\n     \"MBH\": \"MAH\u0100BH\u0100RATA, ed. Calc. (GILD. Bibl. 93). Von S. 521 des W\u00f6rter- buchs sind die drei ersten B\u00fccher, von S. 601 auch die f\u00fcnf letzten, von an auch das 13te Buch ausgebeutet worden.\",\n     \"N\": \"NALOP\u0100KHY\u0100NA in B\u00d6HTLINGK'S Chrestomathie (GILD. Bibl. 49). Die BOPP'sche Ausgabe (GILD. Bibl. 99) ist durch N. (BOPP) bezeichnet.\",\n     \"SU\u015aR\": \"SU\u015aRUTA, ed. Calc. (GILD. Bibl. 367); citirt nach Band, Seite und Zeile. Den Titel der HESSLER'schen Uebersetzung s. bei GILD. Bibl. 368.\",\n     \"VS\": \"V\u0100JASANEYISAM\u0303HIT\u0100. The V\u0100YASANEYI-SANHIT\u0100 in the M\u0100DHYANDINA -- and the K\u0100\u1e46VA-\u015a\u0100KH\u0100 with the commentary of MAH\u012aDHARA, edited by Dr. ALBRECHT WEBER. Berlin Ferd. D\u00fcmmler's Verlag\u1e63andlung. London Williams and Norgate. 1852. 4\u00ba.\",\n     \"\u0100\u015aV. G\u1e5aHY\": \"\u0100\u015aVAL\u0100YANA'S G\u1e5aHYAS\u016aTR\u0100\u1e46I in 4 Adhy\u0101ya. Hdschr.\",\n     \"\u015aAT. BR\": \"The \u015aATAPATHABR\u0100HMA\u1e46A in the M\u0101dhyandina-\u015a\u0101kh\u0101, with extracts made from the commentaries of S\u0100YA\u1e46A, HARISV\u0100MIN and DVIVEDAGANGA, edited by Dr. ALBRECHT WEBER. Berlin FERD. D\u00dcMM- LER'S Buchhandlung. London WILLIAMS and NORGATE. 1849.\",\n     \"\u1e5aV\": \"\u1e5aGVEDA. Es wird nach Ma\u1e47\u1e0dala, S\u016bkta und \u1e5ac citirt. ROSEN zu \u1e5aV. verweist auf die Anmerkungen in: Rigveda-Sanhita, liber primus, sanskrit\u00e8 et latin\u00e8; edidit FRIDERICUS ROSEN. London 1838.\"\n    },\n    \"strata\": {\n     \"Vedic\": \"\u1e5agveda\",\n     \"Epic / early-Classical\": \"Mah\u0101bh\u0101rata\"\n    },\n    \"examples_sa\": [\n     \"dvi\\\\tA nakza^traM\",\n     \"pa\\\\praTa^cca\\\\ BUma^\",\n     \"udu\\\\sriyA^H sfjeta\\\\ sUrya\\\\H sacA^~ u\\\\dyannakza^tramarci\\\\vat\",\n     \"nakza^traM pra\\\\tnamami^naccari\\\\zRu\"\n    ]\n   },\n   {\n    \"n\": \"2\",\n    \"sub\": null,\n    \"equivalents_de\": [\n     \"die Mondstationen\"\n    ],\n    \"gloss_de\": \"2\u3009 im Bes. die Mondstationen; in der \u00e4lteren Zeit (aber auch noch im HARIV. ) 27, sp\u00e4ter 28 an der Zahl. Dieselben werden in der Folge auch als Gemahlinnen des Mondes, als T\u00f6chter Dak\u1e63a \u02bcs, augfefasst\",\n    \"equivalence_type\": \"equivalent\",\n    \"grammar\": [],\n    \"ab_labels\": [\n     \"compare\",\n     \"see\",\n     \"special, particular\"\n    ],\n    \"diasystem\": [\n     \"Classical\",\n     \"Epic / early-Classical\",\n     \"Vedic\"\n    ],\n    \"citations\": [\n     \"AV\",\n     \"BH\u0100G. P\",\n     \"HARIV\",\n     \"Ind. St\",\n     \"K\u0100LAS\",\n     \"MBH\",\n     \"P\",\n     \"TBR\",\n     \"TS\",\n     \"VS\",\n     \"WARREN\",\n     \"WEBER\",\n     \"\u015aAT. BR\"\n    ],\n    \"citations_resolved\": {\n     \"AV\": \"ATHARVAVEDASAM\u0303HIT\u0100, herausg. von R. ROTH und W. D. WHITNEY. Berlin bei F. D\u00dcMMLER. 1855. 8\u00ba. In den ersten Bogen des W\u00f6rter- buchs finden sich mehrere Citate, deren Zahlen mit der in der Aus- gabe angenommenen Z\u00e4hlung nicht ganz zusammentreffen. Man kann den Unterschied dadurch ausgleichen, dass man in den zusammen- gesetzten Liedern (Pary\u0101yas\u016bkta), welche in der Ausgabe als Ein- heiten gez\u00e4hlt sind, die Unterabtheilungen (Strophen) als besondere Lieder z\u00e4hlt.\",\n     \"BH\u0100G. P\": \"BH\u0100GAVATAPUR\u0100\u1e46A, nach Anf\u00fchrungen im VP. und \u015aKDR. Von an sind die 9 von BURNOUF edirten Skandha (Gild. Bibl. 125) ausgebeutet worden.\",\n     \"HARIV\": \"HARIVA\u1e42\u015aA im 4ten Bande des MBH. Aus diesem Werke haben wir die Nomina propria mit Benutzung des Index in der LANGLOIS'- schen Uebersetzung (GILD. Bibl. 122) aufgenommen.\",\n     \"Ind. St\": \"WEBER'S Indische Studien.\",\n     \"K\u0100LAS\": \"K\u0100LASA\u1e42KALITA, citirt nach HAUGHTON'S W\u00f6rterbuch.\",\n     \"MBH\": \"MAH\u0100BH\u0100RATA, ed. Calc. (GILD. Bibl. 93). Von S. 521 des W\u00f6rter- buchs sind die drei ersten B\u00fccher, von S. 601 auch die f\u00fcnf letzten, von an auch das 13te Buch ausgebeutet worden.\",\n     \"P\": \"P\u0100\u1e46INI'S acht B\u00fccher grammatischer Regeln (GILD. Bibl. 244).\",\n     \"TBR\": \"TAITTIR\u012aYABR\u0100HMA\u1e46A.\",\n     \"TS\": \"TAITTIR\u012aYASAM\u0303HIT\u0100. 7 K\u0101\u1e47\u1e0da, eingetheilt in Pra\u015bna, Anuv\u0101ka und Ka\u1e47\u1e0dik\u0101. Die letzten bezeichnen nicht Satzabschnitte, sondern umfassen ye 50 W\u00f6rter. Hdschr.\",\n     \"VS\": \"V\u0100JASANEYISAM\u0303HIT\u0100. The V\u0100YASANEYI-SANHIT\u0100 in the M\u0100DHYANDINA -- and the K\u0100\u1e46VA-\u015a\u0100KH\u0100 with the commentary of MAH\u012aDHARA, edited by Dr. ALBRECHT WEBER. Berlin Ferd. D\u00fcmmler's Verlag\u1e63andlung. London Williams and Norgate. 1852. 4\u00ba.\",\n     \"WARREN\": \"? [Cologne Addition]\",\n     \"WEBER\": \"? [Cologne Addition]\",\n     \"\u015aAT. BR\": \"The \u015aATAPATHABR\u0100HMA\u1e46A in the M\u0101dhyandina-\u015a\u0101kh\u0101, with extracts made from the commentaries of S\u0100YA\u1e46A, HARISV\u0100MIN and DVIVEDAGANGA, edited by Dr. ALBRECHT WEBER. Berlin FERD. D\u00dcMM- LER'S Buchhandlung. London WILLIAMS and NORGATE. 1849.\"\n    },\n    \"strata\": {\n     \"Vedic\": \"Atharvaveda\",\n     \"Epic / early-Classical\": \"Mah\u0101bh\u0101rata\"\n    },\n    \"examples_sa\": [\n     \"SizwAH (kanyAH) somAya rAjYe 'Ta nakzatrAKyA dadO praBuH (dakzaH)\",\n     \"kfttikAdIni nakzatrARIndoH patnyastu\"\n    ]\n   },\n   {\n    \"n\": \"3\",\n    \"sub\": null,\n    \"equivalents_de\": [\n     \"Perle\"\n    ],\n    \"gloss_de\": \"3\u3009 Perle R\u0100JAN. _im_ \u015aKDR. \u2014 Was die Etymologie betrifft, so l\u00e4sst sich gegen die von AUFRECHT _in_ Z. f. vgl. Spr. 8,71 vorgebrachte ( + ) einwenden, dass W\u00e4chter der Nacht nicht auf die Sonne passt,\",\n    \"equivalence_type\": \"equivalent\",\n    \"grammar\": [],\n    \"ab_labels\": [\n     \"compare\"\n    ],\n    \"diasystem\": [\n     \"Vedic\"\n    ],\n    \"citations\": [\n     \"AUFRECHT\",\n     \"NIR\",\n     \"P\",\n     \"R\u0100JAN\",\n     \"TBR\",\n     \"Z. f. vgl. Spr\",\n     \"\u015aAT. BR\",\n     \"\u015aKDR\"\n    ],\n    \"citations_resolved\": {\n     \"AUFRECHT\": \"? [Cologne Addition]\",\n     \"NIR\": \"Y\u0100SKA'S NIRUKTA sammt den NIGHA\u1e46\u1e6cAVA'S herausgegeben und erkl\u00e4rt von RUDOLPH ROTH. G\u00f6ttingen 1852.\",\n     \"P\": \"P\u0100\u1e46INI'S acht B\u00fccher grammatischer Regeln (GILD. Bibl. 244).\",\n     \"R\u0100JAN\": \"R\u0100JANIRGHA\u1e46\u1e6cA, ein medicinisches W\u00f6rterbuch; nach An- f\u00fchrungen im \u015aKDR.\",\n     \"TBR\": \"TAITTIR\u012aYABR\u0100HMA\u1e46A.\",\n     \"Z. f. vgl. Spr\": \"Zeitschrift f\u00fcr vergleichende Sprachforschung auf dem Gebiete des Deutschen, Griechischen und Lateinischen herausgege- ben von Dr. THEODOR AUFRECHT und Dr. ADALBERT KUHN. Berlin.\",\n     \"\u015aAT. BR\": \"The \u015aATAPATHABR\u0100HMA\u1e46A in the M\u0101dhyandina-\u015a\u0101kh\u0101, with extracts made from the commentaries of S\u0100YA\u1e46A, HARISV\u0100MIN and DVIVEDAGANGA, edited by Dr. ALBRECHT WEBER. Berlin FERD. D\u00dcMM- LER'S Buchhandlung. London WILLIAMS and NORGATE. 1849.\",\n     \"\u015aKDR\": \"\u015aABDAKALPADRUMA (GILD. Bibl. 371).\"\n    },\n    \"strata\": {},\n    \"examples_sa\": [\n     \"nakza\",\n     \"tra\",\n     \"nakzatra\",\n     \"nakza\"\n    ]\n   }\n  ],\n  \"corpus_synonyms\": null\n }\n]", "ls": 79, "sk": 34, "senses": 7, "source_senses": 3, "nws": 0}, "sarvatra": {"skeleton": "=== LAYER: PWG \u2014 MAIN ENTRY (B\u00f6htlingk-Roth, large) ===\n\n{T1}\u00a6 (von {T2}) {T3} {T4}. {T5}.\n{T122} 1\u3009 {%\u00fcberall, stets, in allen F\u00e4llen, jederzeit%} {T6}. {T7}. {T8}. {T9}. {T10}. {T11}. {T12}. {T13}. {T14} {T15}. {T16}. {T17} {T18}. {T19} {T20}. {T21}. {T22}. {T23}. {T24}. {T25}. {T26}. {T27}. {T28}. {T29}. {T30}. {T31}. {T32}. {T33}. {T34}. {T35}, {T36} {T37}. {T38}. {T39}. {T40}. {T41}. {T42}. {T43} {T44}. {T45} {T46}. {T47} {T48}. {T49}. {T50}. {T51}. {T52}. {T53}. {T54}. {T55}. {T56}. {T57} {T58}. {T59}. {T60}. {T61} {T62}. {T63} {T64}. {T65}. {T66}. {T67}. {T68} {T69}. {T70} {%in keinem Falle%} {T71}.\n{T123}\u2014 2\u3009 = {T72} {T73} und {T74} {T75} {T76}. {T77} {T78} zu {T79}. {T80} {T81}. {T82} {T83}. {T84}. {T85} {T86} {T87}. {T88} {T89}. {T90} {T91}. {T92} {T93}. {T94} {T95}. {T96} {T97}. {T98}. {T99}. {T100} {T101}. {T102} ({T103} {T104}) {T105}. {T106}. {T107} {T108}. {T109} {%Holz f\u00fcr Nichts gut%} {T110}.\n{T124}\u2014 {T111} {T112}.\n\n=== LAYER: PW \u2014 B\u00f6htlingk k\u00fcrzere Fassung (revision of PWG; may correct gender/sense) ===\n\n{T113}\u00a6 {T114}\n{T125}\u2014 1\u3009 {%\u00fcberall, stets, in allen F\u00e4llen, jederzeit%}. Verst\u00e4rkt {T115} {T116} {T117} {T118} {T119}. Mit einer Negation {%in keinem Falle%}.\n{T126}\u2014 2\u3009 = {T120} mit einer Negation {%f\u00fcr Nichts%} {T121}", "portrait": "[\n {\n  \"schema_version\": \"pwg_ru.lexicographic_portrait.v1\",\n  \"key1\": \"sarvatra\",\n  \"key2\": \"sarva/tra\",\n  \"h\": \"\",\n  \"iast\": \"sarvatra\",\n  \"pos\": [\n   \"adj.\",\n   \"adv.\"\n  ],\n  \"diasystem\": [\n   \"Classical\",\n   \"Epic / early-Classical\",\n   \"Medieval\",\n   \"Vedic\"\n  ],\n  \"labels\": [\n   \"compare\",\n   \"noun\",\n   \"scholion\",\n   \"variant reading\"\n  ],\n  \"senses\": [\n   {\n    \"n\": \"0\",\n    \"sub\": null,\n    \"equivalents_de\": [],\n    \"gloss_de\": \"\u00a6 (von ) adv. P. 5,3,10 . VOP. 7,99\",\n    \"equivalence_type\": \"explanatory\",\n    \"grammar\": [\n     \"adv.\"\n    ],\n    \"ab_labels\": [],\n    \"diasystem\": [],\n    \"citations\": [\n     \"P\",\n     \"VOP\"\n    ],\n    \"citations_resolved\": {\n     \"P\": \"P\u0100\u1e46INI'S acht B\u00fccher grammatischer Regeln (GILD. Bibl. 244).\",\n     \"VOP\": \"VOPADEVA'S Grammatik, nach B\u00d6HTLINGK'S Ausgabe (GILD. Bibl. 249, {%a.%} S. 170).\"\n    },\n    \"strata\": {},\n    \"examples_sa\": [\n     \"sarva/tra\",\n     \"sarva\"\n    ]\n   },\n   {\n    \"n\": \"1\",\n    \"sub\": null,\n    \"equivalents_de\": [\n     \"\u00fcberall, stets, in allen F\u00e4llen, jederzeit\"\n    ],\n    \"gloss_de\": \"1\u3009 \u00fcberall, stets, in allen F\u00e4llen, jederzeit \u015aAT. BR. 2,4,3,9 . 4,4,1,18 . \u0100\u015aV. \u015aR. 9,2,5 . K\u0100TY. \u015aR. 3,2,6 . 5,8 . 4,10,5 . 9,6,10 . 11,1,7 . 4,4,18 . L\u0100\u1e6cY. 6,10,17 . 7,11,9 . 8,9,3 . KAU\u015a. 8 . 57 .\",\n    \"equivalence_type\": \"explanatory\",\n    \"grammar\": [],\n    \"ab_labels\": [\n     \"scholion\"\n    ],\n    \"diasystem\": [\n     \"Classical\",\n     \"Epic / early-Classical\",\n     \"Medieval\",\n     \"Vedic\"\n    ],\n    \"citations\": [\n     \"AV. PR\u0100T\",\n     \"BH\u0100G. P\",\n     \"DH\u016aRTAS\",\n     \"HARIV\",\n     \"HIT. Pr\",\n     \"KAP\",\n     \"KATH\u0100S\",\n     \"KAU\u015a\",\n     \"K\u0100TY. \u015aR\",\n     \"L\u0100\u1e6cY\",\n     \"M\",\n     \"P\",\n     \"R\",\n     \"SARVADAR\u015aANAS\",\n     \"Spr. (II)\",\n     \"TS. PR\u0100T\",\n     \"VAR\u0100H. B\u1e5aH. S\",\n     \"VIKR\",\n     \"VS. PR\u0100T\",\n     \"\u0100\u015aV. \u015aR\",\n     \"\u015aAT. BR\",\n     \"\u015a\u0100K\",\n     \"\u1e5aV. PR\u0100T\"\n    ],\n    \"citations_resolved\": {\n     \"AV. PR\u0100T\": \"PR\u0100TI\u015a\u0100KHYA zum ATHARVAVEDA. Citirt nach Adhy\u0101ya und S\u016btra. Hdschr. Siehe ROTH'S Einl. z. NIRUKTA, S. XLVII.\",\n     \"BH\u0100G. P\": \"BH\u0100GAVATAPUR\u0100\u1e46A, nach Anf\u00fchrungen im VP. und \u015aKDR. Von an sind die 9 von BURNOUF edirten Skandha (Gild. Bibl. 125) ausgebeutet worden.\",\n     \"DH\u016aRTAS\": \"DH\u016aRTASAM\u0100GAMA in LASSEN'S Anthologie (GILD. Bibl. 48).\",\n     \"HARIV\": \"HARIVA\u1e42\u015aA im 4ten Bande des MBH. Aus diesem Werke haben wir die Nomina propria mit Benutzung des Index in der LANGLOIS'- schen Uebersetzung (GILD. Bibl. 122) aufgenommen.\",\n     \"HIT. Pr\": \"Prooemium im HIT.\",\n     \"KAP\": \"KAPILA (The Aphorisms of the S\u00e1nkhya Philosophy, of Kapila; with illustrative extracts from the commentaries. I. Allahabad 1852. II--IV. ebend. 1834. Auch in der Bibl. ind.).\",\n     \"KATH\u0100S\": \"KATH\u0100SARITS\u0100GARA, ed. BROCKHAUS (GILD. Bibl. 237).\",\n     \"KAU\u015a\": \"KAU\u015aIKA'S S\u016aTRA zum ATHARVAVEDA. 14 Adhy\u0101ya. Die Ka\u1e47- \u1e0dik\u0101 sind durchgez\u00e4hlt. Hdschr.\",\n     \"K\u0100TY. \u015aR\": \"K\u0100TY\u0100YANA'S \u015aRAUTAS\u016aTR\u0100\u1e46I. 26 Adhy\u0101ya. Hdschr.\",\n     \"L\u0100\u1e6cY\": \"L\u0100\u1e6cY\u0100YANA'S S\u016aTRA zum SV. Hdschr.\",\n     \"M\": \"MANU'S Gesetzbuch in der Ausg. von LOISELEUR DESLONGCHAMPS (GILD. Bibl. 289).\",\n     \"P\": \"P\u0100\u1e46INI'S acht B\u00fccher grammatischer Regeln (GILD. Bibl. 244).\",\n     \"R\": \"R\u0100M\u0100YA\u1e46A. Ohne eine n\u00e4here Angabe ist bei den zwei ersten B\u00fcchern die Ausgabe von SCHLEGEL (GILD. Bibl. 84), bei den vier letzten die von GORRESIO (GILD. Bibl. 85) gemeint.\",\n     \"SARVADAR\u015aANAS\": \"? [Cologne Addition]\",\n     \"Spr. (II)\": \"Indische Spr\u00fcche. Sanskrit und Deutsch. Herausgegeben von Otto B\u00f6htlingk. Zweite vermehrte und verbesserte Auflage. 1870-1873 [Cologne Addition]\",\n     \"TS. PR\u0100T\": \"? [Cologne Addition]\",\n     \"VAR\u0100H. B\u1e5aH. S\": \"VAR\u0100HAMIHIRA'S B\u1e5aHATSAM\u0303HIT\u0100.\",\n     \"VIKR\": \"VIKRAMORVA\u015a\u012a, ed. BOLLENSEN (GILD. Bibl. 206). Eine einfache Zahl verweist auf einen \u015aloka, eine doppelte--auf Seite und Zeile.\",\n     \"VS. PR\u0100T\": \"PR\u0100TI\u015a\u0100KHYA zur V\u0100JASANEYISAM\u0303HIT\u0100, citirt nach Adhy\u0101ya und S\u016btra. Hdschr. S. ROTH in der Einl. z. NIR. S. XLVI.\",\n     \"\u0100\u015aV. \u015aR\": \"\u0100\u015aVAL\u0100YANA'S \u015aRAUTAS\u016aTR\u0100\u1e46I in 12 Adhy\u0101ya. Handschrift.\",\n     \"\u015aAT. BR\": \"The \u015aATAPATHABR\u0100HMA\u1e46A in the M\u0101dhyandina-\u015a\u0101kh\u0101, with extracts made from the commentaries of S\u0100YA\u1e46A, HARISV\u0100MIN and DVIVEDAGANGA, edited by Dr. ALBRECHT WEBER. Berlin FERD. D\u00dcMM- LER'S Buchhandlung. London WILLIAMS and NORGATE. 1849.\",\n     \"\u015a\u0100K\": \"\u015a\u0100KUNTALA, das Drama in der Ausgabe von B\u00d6HTLINGK (GILD. Bibl. 191). Eine einfache Zahl bezeichnet den \u015aloka, eine doppelte -- Seite und Zeile.\",\n     \"\u1e5aV. PR\u0100T\": \"PR\u0100TI\u015a\u0100KHYA zun \u1e5aGVEDA, citirt nach Pa\u1e6dala und Versen. Hdschr. S. ROTH in der Einl z. NIR. S. XLVII.\"\n    },\n    \"strata\": {\n     \"Epic / early-Classical\": \"R\u0101m\u0101ya\u1e47a\"\n    },\n    \"examples_sa\": [\n     \"svAhAkAraH sa\u02da\",\n     \"sa\u02da catvAri\",\n     \"devaSabdaM sa\u02da varjayeyuH\",\n     \"sarvatrEva\"\n    ]\n   },\n   {\n    \"n\": \"2\",\n    \"sub\": null,\n    \"equivalents_de\": [],\n    \"gloss_de\": \"2\u3009 = adj. und subst. M\u0100RK. P. 92,15 . Schol. zu \u015a\u0100K. 7,10 . HARIV. 15054 . MBH. 3,2471 . R. 1,52,5 . 10 PRAB. 30,4 . VIKR. 30,14 . Spr. (II) 6917 . 7476 . 7478 . R\u0100JA-TAR. 1,357 . BH\u0100G. P. 3,24,47 . 6\",\n    \"equivalence_type\": \"explanatory\",\n    \"grammar\": [\n     \"adj.\"\n    ],\n    \"ab_labels\": [\n     \"compare\",\n     \"noun\",\n     \"scholion\",\n     \"variant reading\"\n    ],\n    \"diasystem\": [\n     \"Classical\",\n     \"Epic / early-Classical\",\n     \"Medieval\"\n    ],\n    \"citations\": [\n     \"BH\u0100G. P\",\n     \"HARIV\",\n     \"MBH\",\n     \"M\u0100RK. P\",\n     \"PRAB\",\n     \"R\",\n     \"RAGH\",\n     \"R\u0100JA-TAR\",\n     \"Spr. (II)\",\n     \"VAR\u0100H. B\u1e5aH. S\",\n     \"VIKR\",\n     \"\u015a\u0100K\"\n    ],\n    \"citations_resolved\": {\n     \"BH\u0100G. P\": \"BH\u0100GAVATAPUR\u0100\u1e46A, nach Anf\u00fchrungen im VP. und \u015aKDR. Von an sind die 9 von BURNOUF edirten Skandha (Gild. Bibl. 125) ausgebeutet worden.\",\n     \"HARIV\": \"HARIVA\u1e42\u015aA im 4ten Bande des MBH. Aus diesem Werke haben wir die Nomina propria mit Benutzung des Index in der LANGLOIS'- schen Uebersetzung (GILD. Bibl. 122) aufgenommen.\",\n     \"MBH\": \"MAH\u0100BH\u0100RATA, ed. Calc. (GILD. Bibl. 93). Von S. 521 des W\u00f6rter- buchs sind die drei ersten B\u00fccher, von S. 601 auch die f\u00fcnf letzten, von an auch das 13te Buch ausgebeutet worden.\",\n     \"M\u0100RK. P\": \"M\u0100RK\u0100\u1e46\u1e0cEYAPUR\u0100\u1e46A in der Bibliotheca indica.\",\n     \"PRAB\": \"PRABODHACANDRODAYA, ed. BROCKHAUS (GILD. Bibl. 216).\",\n     \"R\": \"R\u0100M\u0100YA\u1e46A. Ohne eine n\u00e4here Angabe ist bei den zwei ersten B\u00fcchern die Ausgabe von SCHLEGEL (GILD. Bibl. 84), bei den vier letzten die von GORRESIO (GILD. Bibl. 85) gemeint.\",\n     \"RAGH\": \"RAGHUVA\u1e42\u015aA, ed. STENZLER (GILD. Bibl. 134).\",\n     \"R\u0100JA-TAR\": \"R\u0100JATARA\u1e44GI\u1e46\u012a, ed. TROYER (GILD. Bibl. 148) f\u00fcr die 6 ersten Taram\u0303ga's; f\u00fcr die folgenden die Calc. Ausg. (GILD. Bibl. 147).\",\n     \"Spr. (II)\": \"Indische Spr\u00fcche. Sanskrit und Deutsch. Herausgegeben von Otto B\u00f6htlingk. Zweite vermehrte und verbesserte Auflage. 1870-1873 [Cologne Addition]\",\n     \"VAR\u0100H. B\u1e5aH. S\": \"VAR\u0100HAMIHIRA'S B\u1e5aHATSAM\u0303HIT\u0100.\",\n     \"VIKR\": \"VIKRAMORVA\u015a\u012a, ed. BOLLENSEN (GILD. Bibl. 206). Eine einfache Zahl verweist auf einen \u015aloka, eine doppelte--auf Seite und Zeile.\",\n     \"\u015a\u0100K\": \"\u015a\u0100KUNTALA, das Drama in der Ausgabe von B\u00d6HTLINGK (GILD. Bibl. 191). Eine einfache Zahl bezeichnet den \u015aloka, eine doppelte -- Seite und Zeile.\"\n    },\n    \"strata\": {\n     \"Epic / early-Classical\": \"R\u0101m\u0101ya\u1e47a\",\n     \"Classical\": \"Raghuva\u1e43\u015ba\"\n    },\n    \"examples_sa\": [\n     \"sarvasmin\",\n     \"SAntikarmaRi\",\n     \"ASrame\",\n     \"kuSalaH\"\n    ]\n   }\n  ],\n  \"corpus_synonyms\": null\n }\n]", "ls": 78, "sk": 34, "senses": 4, "source_senses": 2, "nws": 0}, "sakft": {"skeleton": "=== LAYER: PWG \u2014 MAIN ENTRY (B\u00f6htlingk-Roth, large) ===\n\n{T1}\u00a6 ({T119}2.{T120} {T2} + {T3}) {T4} {T5}.\n{T121} 1\u3009 {%auf ein Mal, mit einem Male%}; = {T6} {T7}. {T8}. {T9} {T10}. {T11}. {T12} {T13}. {T14} {T15}. {T16}. {T17} {T18}. {T19}. {T20} {%mit einem Ruck abgetrennt%} {T21}. {T22}. {T23} {T24}. {T25} {T26}, {T27} {T28} {T29}. {T30}. so {T31} {%pl\u00f6tzlich%} {T32}.\n{T122}\u2014 2\u3009 {%einmal, semel%} {T33} {T34} {T35}. {T36} {T37}. {T38}. {T39}. {T40}. {T41}. {T42}. {T43}. [Page7-0508] {T44} {T45}. {T46}. {T47} {T48}. {T49} {T50}. {T51} {T52}. {T53}. {T54}. {T55}. {T56}. {T57}. {T58}. {T59}. {T60} {T61} {T62}. {T63}. {T64}. {T65}. {T66} {T67}. {T68} {T69}. {T70} {T71}. {T72} {T73}. {T74}. {T75}. {T76}. {T77}. {%einmal%} so {T78} {%irgend ein Mal%} {T79}. {T80} so {T81} {%einst, ehemals%} {T82}. {T83} {%nie%} {T84}.\n{T123}\u2014 3\u3009 {%ein f\u00fcr allemal, f\u00fcr immer%}: {T85} {T86}. {T87} {T88}. {T89}_in_{T90}. {T91}. {T92} {T93}. {T94}.\n{T124}\u2014 {T95} {T96} (auch {T97}. {T98}. {T99}. {T100}. {T101} nach der Lesart der {T102}).\n\n=== LAYER: PW \u2014 B\u00f6htlingk k\u00fcrzere Fassung (revision of PWG; may correct gender/sense) ===\n\n{T103}\u00a6\n{T125}\u2014 1\u3009 {T104} {%gleichzeitig th\u00e4tig%} {T105}. {T106} {T107}\n{T126}\u2014 2\u3009 {T108}\n{T127}\u2014 a\u3009 {%auf ein Mal, mit einem Male, mit einem Ruck, pl\u00f6tzlich%}. {T109} {T110} {T111} {T112}.\n{T128}\u2014 b\u3009 {%einmal, semel%}. {T113} {%einmal am Tage%}. Wiederholt {%immer nur einmal%}. {T114} (!) {T115}.\n{T129}\u2014 c\u3009 {%einmal,%} so {T116} {%irgend ein mal;%} mit der {T117} {%nie%}.\n{T130}\u2014 d\u3009 {%einst, ehemals%}.\n{T131}\u2014 e\u3009 {%ein f\u00fcr allemal, f\u00fcr immer%}.\n\n=== LAYER: SCH \u2014 Schmidt Nachtr\u00e4ge 1928 (pure addenda to PW; \u00b0=new vs pw, *=first attestation) ===\n\n\u00b0{%sak\u1e5bt%}\u00a6 {T118} wrong spelling of our author for {%\u015bak\u1e5bt%} (pun with {%asak\u1e5bt%}). {part=,seq=25923,type=\u02da,n=3}", "portrait": "[\n {\n  \"schema_version\": \"pwg_ru.lexicographic_portrait.v1\",\n  \"key1\": \"sakft\",\n  \"key2\": \"sakf/t\",\n  \"h\": \"\",\n  \"iast\": \"sak\u1e5bt\",\n  \"pos\": [\n   \"adv.\"\n  ],\n  \"diasystem\": [\n   \"Classical\",\n   \"Epic / early-Classical\",\n   \"Medieval\",\n   \"Vedic\"\n  ],\n  \"labels\": [\n   \"above all, especially\",\n   \"compare\",\n   \"scholion\"\n  ],\n  \"senses\": [\n   {\n    \"n\": \"0\",\n    \"sub\": null,\n    \"equivalents_de\": [],\n    \"gloss_de\": \"\u00a6 ( 2. + ) adv. P. 5,4,19\",\n    \"equivalence_type\": \"explanatory\",\n    \"grammar\": [\n     \"adv.\"\n    ],\n    \"ab_labels\": [],\n    \"diasystem\": [],\n    \"citations\": [\n     \"P\"\n    ],\n    \"citations_resolved\": {\n     \"P\": \"P\u0100\u1e46INI'S acht B\u00fccher grammatischer Regeln (GILD. Bibl. 244).\"\n    },\n    \"strata\": {},\n    \"examples_sa\": [\n     \"sakf/t\",\n     \"sa\",\n     \"kft\"\n    ]\n   },\n   {\n    \"n\": \"1\",\n    \"sub\": null,\n    \"equivalents_de\": [\n     \"auf ein Mal, mit einem Male\"\n    ],\n    \"gloss_de\": \"1\u3009 auf ein Mal, mit einem Male; = AK. 3,4,32 (, 4 . MED. avy. 33 . \u1e5aV. 8,1,14 . 2,16,8 . 10,33,3 . 1,105,18 . 6,66,1 . AIT. BR. 6,21 . TS. 3,4,2,2 . mit einem Ruck abgetrennt \u0100\u015aV. \u015aR. 2,6,4 . \u015aAT. BR.\",\n    \"equivalence_type\": \"explanatory\",\n    \"grammar\": [],\n    \"ab_labels\": [\n     \"above all, especially\",\n     \"scholion\"\n    ],\n    \"diasystem\": [\n     \"Epic / early-Classical\",\n     \"Vedic\"\n    ],\n    \"citations\": [\n     \"AIT. BR\",\n     \"AK\",\n     \"KAU\u015a\",\n     \"M\",\n     \"MBH\",\n     \"MED. avy\",\n     \"P\",\n     \"TS\",\n     \"\u0100\u015aV. \u015aR\",\n     \"\u015aAT. BR\",\n     \"\u015a\u0100\u1e44KH. \u015aR\",\n     \"\u1e5aV\"\n    ],\n    \"citations_resolved\": {\n     \"AIT. BR\": \"AITAREYABR\u0100HMA\u1e46A. Citirt nach den 8 Pa\u00f1cik\u0101 (einer \u00e4usseren Abtheilung, in welche die 40 nach sachlichen R\u00fccksichten gebildeten Adhy\u0101ya zerlegt sind) und den innerhalb der Pa\u00f1cik\u0101 durchlaufenden Kapitelzahlen. Hdschr. S\u0100YA\u1e46A'S Commentar dazu. Hdschr.\",\n     \"AK\": \"AMARAKO\u1e62A nach der Ausgabe von COLEBROOKE und LOISELEUR DESLONGCHAMPS (GILD. Bibl. 251. 253).\",\n     \"KAU\u015a\": \"KAU\u015aIKA'S S\u016aTRA zum ATHARVAVEDA. 14 Adhy\u0101ya. Die Ka\u1e47- \u1e0dik\u0101 sind durchgez\u00e4hlt. Hdschr.\",\n     \"M\": \"MANU'S Gesetzbuch in der Ausg. von LOISELEUR DESLONGCHAMPS (GILD. Bibl. 289).\",\n     \"MBH\": \"MAH\u0100BH\u0100RATA, ed. Calc. (GILD. Bibl. 93). Von S. 521 des W\u00f6rter- buchs sind die drei ersten B\u00fccher, von S. 601 auch die f\u00fcnf letzten, von an auch das 13te Buch ausgebeutet worden.\",\n     \"MED. avy\": \"MEDIN\u012aKO\u1e62A, ed. Calc. (GILD. Bibl. 258). Die W\u00f6rter sind zu- n\u00e4chst nach dem letzten Consonanten im Worte angeordnet: also (k), (kh), (g) u. s. w. Die Partikeln (avyaya) bilden einen besondern Abschnitt am Ende, den wir durch avy. bezeichnet haben.\",\n     \"P\": \"P\u0100\u1e46INI'S acht B\u00fccher grammatischer Regeln (GILD. Bibl. 244).\",\n     \"TS\": \"TAITTIR\u012aYASAM\u0303HIT\u0100. 7 K\u0101\u1e47\u1e0da, eingetheilt in Pra\u015bna, Anuv\u0101ka und Ka\u1e47\u1e0dik\u0101. Die letzten bezeichnen nicht Satzabschnitte, sondern umfassen ye 50 W\u00f6rter. Hdschr.\",\n     \"\u0100\u015aV. \u015aR\": \"\u0100\u015aVAL\u0100YANA'S \u015aRAUTAS\u016aTR\u0100\u1e46I in 12 Adhy\u0101ya. Handschrift.\",\n     \"\u015aAT. BR\": \"The \u015aATAPATHABR\u0100HMA\u1e46A in the M\u0101dhyandina-\u015a\u0101kh\u0101, with extracts made from the commentaries of S\u0100YA\u1e46A, HARISV\u0100MIN and DVIVEDAGANGA, edited by Dr. ALBRECHT WEBER. Berlin FERD. D\u00dcMM- LER'S Buchhandlung. London WILLIAMS and NORGATE. 1849.\",\n     \"\u015a\u0100\u1e44KH. \u015aR\": \"\u015a\u0100\u1e44KH\u0100YANA'S \u015aRAUTAS\u016aTR\u0100\u1e46I.\",\n     \"\u1e5aV\": \"\u1e5aGVEDA. Es wird nach Ma\u1e47\u1e0dala, S\u016bkta und \u1e5ac citirt. ROSEN zu \u1e5aV. verweist auf die Anmerkungen in: Rigveda-Sanhita, liber primus, sanskrit\u00e8 et latin\u00e8; edidit FRIDERICUS ROSEN. London 1838.\"\n    },\n    \"strata\": {\n     \"Vedic\": \"\u1e5agveda\",\n     \"Epic / early-Classical\": \"Mah\u0101bh\u0101rata\"\n    },\n    \"examples_sa\": [\n     \"saha\",\n     \"sa\\\\kftsu te\\\\ anu\\\\ stoma^M mudImahi\",\n     \"sa\\\\kftsu no^ mfLaya\",\n     \"a\\\\ru\\\\Ro mA^ sa\\\\kfdvfko^ dadarSa\"\n    ]\n   },\n   {\n    \"n\": \"2\",\n    \"sub\": null,\n    \"equivalents_de\": [\n     \"einmal, semel\"\n    ],\n    \"gloss_de\": \"2\u3009 einmal, semel AK. MED. \u1e5aV. 6,48,22 . 10,95,16 . TBR. 2,1,9,1 . AIT. BR. 1,26 . 2,24 . 7,17 . \u015aAT. BR. 1,2,3,11 . 2,4,3,9 . [Page7-0508] 4,5,3,1 . \u0100\u015aV. G\u1e5aHY. 1,3,3 . K\u0100TY. \u015aR. 1,7,9 . 8,46 . \u015aAT. BR\",\n    \"equivalence_type\": \"equivalent\",\n    \"grammar\": [],\n    \"ab_labels\": [\n     \"above all, especially\"\n    ],\n    \"diasystem\": [\n     \"Classical\",\n     \"Epic / early-Classical\",\n     \"Medieval\",\n     \"Vedic\"\n    ],\n    \"citations\": [\n     \"AIT. BR\",\n     \"AK\",\n     \"KATH\u0100S\",\n     \"K\u0100TY. \u015aR\",\n     \"M\",\n     \"MED\",\n     \"Spr. (II)\",\n     \"TBR\",\n     \"VAR\u0100H. B\u1e5aH. S\",\n     \"VIKR\",\n     \"Y\u0100J\u00d1\",\n     \"\u0100\u015aV. G\u1e5aHY\",\n     \"\u015aAT. BR\",\n     \"\u015a\u0100K\",\n     \"\u1e5aV\"\n    ],\n    \"citations_resolved\": {\n     \"AIT. BR\": \"AITAREYABR\u0100HMA\u1e46A. Citirt nach den 8 Pa\u00f1cik\u0101 (einer \u00e4usseren Abtheilung, in welche die 40 nach sachlichen R\u00fccksichten gebildeten Adhy\u0101ya zerlegt sind) und den innerhalb der Pa\u00f1cik\u0101 durchlaufenden Kapitelzahlen. Hdschr. S\u0100YA\u1e46A'S Commentar dazu. Hdschr.\",\n     \"AK\": \"AMARAKO\u1e62A nach der Ausgabe von COLEBROOKE und LOISELEUR DESLONGCHAMPS (GILD. Bibl. 251. 253).\",\n     \"KATH\u0100S\": \"KATH\u0100SARITS\u0100GARA, ed. BROCKHAUS (GILD. Bibl. 237).\",\n     \"K\u0100TY. \u015aR\": \"K\u0100TY\u0100YANA'S \u015aRAUTAS\u016aTR\u0100\u1e46I. 26 Adhy\u0101ya. Hdschr.\",\n     \"M\": \"MANU'S Gesetzbuch in der Ausg. von LOISELEUR DESLONGCHAMPS (GILD. Bibl. 289).\",\n     \"MED\": \"MEDIN\u012aKO\u1e62A, ed. Calc. (GILD. Bibl. 258). Die W\u00f6rter sind zu- n\u00e4chst nach dem letzten Consonanten im Worte angeordnet: also (k), (kh), (g) u. s. w. Die Partikeln (avyaya) bilden einen besondern Abschnitt am Ende, den wir durch avy. bezeichnet haben.\",\n     \"Spr. (II)\": \"Indische Spr\u00fcche. Sanskrit und Deutsch. Herausgegeben von Otto B\u00f6htlingk. Zweite vermehrte und verbesserte Auflage. 1870-1873 [Cologne Addition]\",\n     \"TBR\": \"TAITTIR\u012aYABR\u0100HMA\u1e46A.\",\n     \"VAR\u0100H. B\u1e5aH. S\": \"VAR\u0100HAMIHIRA'S B\u1e5aHATSAM\u0303HIT\u0100.\",\n     \"VIKR\": \"VIKRAMORVA\u015a\u012a, ed. BOLLENSEN (GILD. Bibl. 206). Eine einfache Zahl verweist auf einen \u015aloka, eine doppelte--auf Seite und Zeile.\",\n     \"Y\u0100J\u00d1\": \"Y\u0100J\u00d1AVALKYA'S Gesetzbuch. Sanskrit und Deutsch herausge- geben von Dr. ADOLPH FRIEDRICH STENZLER. Berlin und London 1849.\",\n     \"\u0100\u015aV. G\u1e5aHY\": \"\u0100\u015aVAL\u0100YANA'S G\u1e5aHYAS\u016aTR\u0100\u1e46I in 4 Adhy\u0101ya. Hdschr.\",\n     \"\u015aAT. BR\": \"The \u015aATAPATHABR\u0100HMA\u1e46A in the M\u0101dhyandina-\u015a\u0101kh\u0101, with extracts made from the commentaries of S\u0100YA\u1e46A, HARISV\u0100MIN and DVIVEDAGANGA, edited by Dr. ALBRECHT WEBER. Berlin FERD. D\u00dcMM- LER'S Buchhandlung. London WILLIAMS and NORGATE. 1849.\",\n     \"\u015a\u0100K\": \"\u015a\u0100KUNTALA, das Drama in der Ausgabe von B\u00d6HTLINGK (GILD. Bibl. 191). Eine einfache Zahl bezeichnet den \u015aloka, eine doppelte -- Seite und Zeile.\",\n     \"\u1e5aV\": \"\u1e5aGVEDA. Es wird nach Ma\u1e47\u1e0dala, S\u016bkta und \u1e5ac citirt. ROSEN zu \u1e5aV. verweist auf die Anmerkungen in: Rigveda-Sanhita, liber primus, sanskrit\u00e8 et latin\u00e8; edidit FRIDERICUS ROSEN. London 1838.\"\n    },\n    \"strata\": {\n     \"Vedic\": \"\u1e5agveda\",\n     \"Epic / early-Classical\": \"Manusm\u1e5bti\"\n    },\n    \"examples_sa\": [\n     \"sa\\\\kfdahna^H\",\n     \"sakfdindraM BUtAnyatyaricyanta\",\n     \"sakfnmantravacanam\",\n     \"sakfdgfhIta\"\n    ]\n   },\n   {\n    \"n\": \"3\",\n    \"sub\": null,\n    \"equivalents_de\": [\n     \"ein f\u00fcr allemal, f\u00fcr immer\"\n    ],\n    \"gloss_de\": \"3\u3009 ein f\u00fcr allemal, f\u00fcr immer: CH\u0100ND. UP. 3,11,3 . 8,4,2 . N\u1e5aS. T\u0100P. UP. _in_ Ind. St. 9,165 . VED\u0100NTAS. (Allah.) No. 124 . Spr. (II) 4569 . M\u0100RK. P. 109,67 . \u2014 Vgl. (auch MBH. 5,7160 . VAR\u0100H. B\u1e5aH. S.\",\n    \"equivalence_type\": \"explanatory\",\n    \"grammar\": [],\n    \"ab_labels\": [\n     \"compare\"\n    ],\n    \"diasystem\": [\n     \"Classical\",\n     \"Epic / early-Classical\"\n    ],\n    \"citations\": [\n     \"BH\u0100G. P\",\n     \"CH\u0100ND. UP\",\n     \"Ind. St\",\n     \"MBH\",\n     \"M\u0100RK. P\",\n     \"N\u1e5aS. T\u0100P. UP\",\n     \"Spr. (II)\",\n     \"VAR\u0100H. B\u1e5aH. S\",\n     \"VED\u0100NTAS. (Allah.) No\",\n     \"ed. Bomb\"\n    ],\n    \"citations_resolved\": {\n     \"BH\u0100G. P\": \"BH\u0100GAVATAPUR\u0100\u1e46A, nach Anf\u00fchrungen im VP. und \u015aKDR. Von an sind die 9 von BURNOUF edirten Skandha (Gild. Bibl. 125) ausgebeutet worden.\",\n     \"CH\u0100ND. UP\": \"CH\u0100NDOGYOPANI\u1e62AD, nach der Ausgabe von R\u00d6ER in der Bibliotheca indica.\",\n     \"Ind. St\": \"WEBER'S Indische Studien.\",\n     \"MBH\": \"MAH\u0100BH\u0100RATA, ed. Calc. (GILD. Bibl. 93). Von S. 521 des W\u00f6rter- buchs sind die drei ersten B\u00fccher, von S. 601 auch die f\u00fcnf letzten, von an auch das 13te Buch ausgebeutet worden.\",\n     \"M\u0100RK. P\": \"M\u0100RK\u0100\u1e46\u1e0cEYAPUR\u0100\u1e46A in der Bibliotheca indica.\",\n     \"N\u1e5aS. T\u0100P. UP\": \"N\u1e5aSI\u1e42HAT\u0100PAN\u012aYOPANI\u1e62AD ? [Cologne Addition]\",\n     \"Spr. (II)\": \"Indische Spr\u00fcche. Sanskrit und Deutsch. Herausgegeben von Otto B\u00f6htlingk. Zweite vermehrte und verbesserte Auflage. 1870-1873 [Cologne Addition]\",\n     \"VAR\u0100H. B\u1e5aH. S\": \"VAR\u0100HAMIHIRA'S B\u1e5aHATSAM\u0303HIT\u0100.\",\n     \"VED\u0100NTAS. (Allah.) No\": \"A Lecture on the Ved\u00e1nta, embracing the text of the Ved\u00e1nta-S\u00e1ra. Allahabad 1850.\",\n     \"ed. Bomb\": null\n    },\n    \"strata\": {\n     \"Epic / early-Classical\": \"Mah\u0101bh\u0101rata\"\n    },\n    \"examples_sa\": [\n     \"sakfddivA hEvAsmE Bavati\",\n     \"sakfdviBAta\",\n     \"BAnuH sakfdyuktaturaMga eva\",\n     \"a\u02da\"\n    ]\n   }\n  ],\n  \"corpus_synonyms\": null\n }\n]", "ls": 74, "sk": 32, "senses": 10, "source_senses": 3, "nws": 0}}
const PH = {"nakzatra": ["{#na/kzatra#}", "<ls>U\u1e46\u0100DIS. 3,105</ls>", "<lex>n.</lex>", "<ab>\u00fcberh.</ab>", "<ls>AK. 1,1,2,22</ls>", "<ls>H. 107</ls>", "{#dvi\\tA nakza^traM#}", "<ab>coll.</ab>", "{#pa\\praTa^cca\\ BUma^#}", "<ls>\u1e5aV. 7,86,1</ls>", "{#udu\\sriyA^H sfjeta\\ sUrya\\H sacA^~ u\\dyannakza^tramarci\\vat#}", "<ls n=\"\u1e5aV. 7,\">81,2</ls>", "{#nakza^traM pra\\tnamami^naccari\\zRu#}", "<ls n=\"\u1e5aV.\">10,88,13</ls>", "<ls n=\"\u1e5aV. 10,\">111,7</ls>", "<ls n=\"\u1e5aV. 10,\">156,4</ls>", "<ls n=\"\u1e5aV.\">1,50,2</ls>", "<ls n=\"\u1e5aV.\">3,54,19</ls>", "{#a\\Bi nakza^treBiH pi\\taro\\ dyAma^piMSan#}", "<ls n=\"\u1e5aV.\">10,68,11</ls>", "{#nakza^trARAme\\zAmu\\pasTe\\ soma\\ Ahi^taH#}", "<ls n=\"\u1e5aV. 10,\">85,2</ls>", "<ls>AV. 6,128,1</ls>", "<ls n=\"AV. 6,128,\">3</ls>", "<ls n=\"AV.\">7,13,1</ls>", "<ls n=\"AV.\">9,7,15</ls>", "<ls n=\"AV.\">15,6,2</ls>", "<ls>AIT. BR. 4,25</ls>", "<ls>VS. 14,19</ls>", "<ls n=\"VS.\">18,18</ls>", "<ls n=\"VS.\">22,28</ls>", "<ls>\u0100\u015aV. G\u1e5aHY. 4,4</ls>", "<ls>L\u0100\u1e6cY. 3,8,10</ls>", "{#nakzatrARi grahAstaTA#}", "<ls>M. 1,24</ls>", "{#vijYAya niSi panTAnaM nakzatragaRasUcitam#}", "<ls>HI\u1e0c. 1,3</ls>", "<ls>N. 5,6</ls>", "{#candrAdityO grahanakzatratArAH#}", "<ls>MBH. 13,7386</ls>", "<ls n=\"MBH.\">1,7677</ls>", "<is>Jaina</is>", "<is>Jyoti\u1e63ka</is>", "<ls>H. 92</ls>", "{#puRye tiTO muhUrte vA nakzatre vA guRAnvite#}", "<ls>M. 2,30</ls>", "{#nakzatrEryaSca jIvati#}", "<ls n=\"M.\">3,162</ls>", "<ls>SU\u015aR. 1,17,8</ls>", "<ls n=\"SU\u015aR. 1,\">114,4</ls>", "<ls n=\"SU\u015aR. 1,\">103,2</ls>", "{#dyOH sacandrArkanakzatrA#}", "<ls>MBH. 13,7070</ls>", "<ls n=\"MBH.\">3,12549</ls>", "<ls n=\"MBH. 3,\">16038</ls>", "{#\u02daSirasi#}", "<ls>HARIV. 12239</ls>", "<ab>masc.</ab>", "{#df\\|o nakza^tra u\\ta vi\\Svade^vo\\ BUmi\\mAtA\\ndyAM DA\\sinA\\yoH#}", "<ls>\u1e5aV. 6,67,6</ls>", "{#eka\u02da#}", "<ls>\u015aAT. BR. 13,8,1,3</ls>", "<ls>K\u0100TY. \u015aR. 21,3,3</ls>", "<ls>\u0100\u015aV. G\u1e5aHY. 4,5</ls>", "<ab>Bes.</ab>", "<ls>HARIV.</ls>", "<is>Dak\u1e63a</is>", "<ls>AV. 19,8,1</ls>", "<ls>VS. 18,40</ls>", "<ls>TS. 2,3,5,1</ls>", "<ls n=\"TS.\">3,4,7,1</ls>", "<ls>TBR. 1,5,1,1</ls>", "<ls n=\"TBR. 1,5,\">2,5</ls>", "<ls n=\"TBR.\">2,7,18,13</ls>", "<ls>\u015aAT. BR. 6,5,4,8</ls>", "<ls n=\"\u015aAT. BR.\">9,4,1,9</ls>", "<ls n=\"\u015aAT. BR.\">10,5,4,17</ls>", "<ls>P. 1,2,60</ls>", "<ls>MBH. 13,3256. fgg.</ls>", "<ls n=\"MBH. 13,\">4255. fgg.</ls>", "{#SizwAH (kanyAH) somAya rAjYe 'Ta nakzatrAKyA dadO praBuH (dakzaH)#}", "<ls>HARIV. 104</ls>", "<ls n=\"HARIV.\">1332</ls>", "<ls n=\"HARIV.\">11522</ls>", "<ls n=\"HARIV.\">11524</ls>", "{#kfttikAdIni nakzatrARIndoH patnyastu#}", "<ls>BH\u0100G. P. 6,6,23</ls>", "<ab>s.</ab>", "<ls>Ind. St. 1,89. fgg.</ls>", "<ab>Vgl.</ab>", "<ls>WARREN</ls>", "<ls>K\u0100LAS. 372</ls>", "<ls>WEBER</ls>", "<ls>R\u0100JAN.</ls>", "<ls>\u015aKDR.</ls>", "<ls>AUFRECHT</ls>", "<ls>Z. f. vgl. Spr. 8,71</ls>", "{#nakza#}", "{#tra#}", "{#nakzatra#}", "{#nakza#}", "{#nakta#}", "{#nakz#}", "<ab>vgl.</ab>", "<ls>NIR. 3,20</ls>", "<ls>TBR. 1,5,2,5</ls>", "{#na#}", "{#kzatra#}", "<ls>NIR. 3,20</ls>", "<ls>\u015aAT. BR. 2,1,2,18</ls>", "<ls n=\"\u015aAT. BR. 2,1,2,\">19</ls>", "<ls>P. 6,3,75</ls>", "<ab>Vgl.</ab>", "{#deva\u02da, yama\u02da#}", "{#na/kzatra#}", "<lex>n.</lex>", "<ab>Sg.</ab>", "<ab>coll.</ab>", "<lex>m.</lex>", "<ab>adj. Comp.</ab>", "<lex>f.</lex>", "{#A#}", "<is>Dak\u1e63a</is>", "<ls>R\u0100JAN. 13,154</ls>", "<ab>Vgl.</ab>", "{#nakzatramAlA#}", "{#nakzatra#}", "<lex>m.</lex>", "<ab>N. pr.</ab>", "<is>Ek\u0101da\u015b\u0101\u1e45gin</is>", "<ls>VARDHAM\u0100NAC. 1,48</ls>", "{#na/kzatra#}", "<ls>Vardham\u0101nac. 1,48.</ls>", "{#nakzatra#}", "<lex>m.</lex>", "<ab>N. pr.</ab>", "<is>Ek\u0101da\u015b\u0101\u1e45gin</is>", "<ls>VARDHAM\u0100NAC. 1,48</ls>", "{#na/kzatra#}", "<div n=\"1\">", "<div n=\"1\">", "<div n=\"1\">", "<div n=\"v\">", "<div n=\"1\">", "<div n=\"1\">", "<div n=\"1\">", "<info n=\"sup_5\"/>", "<info n=\"sup_7\"/>"], "sarvatra": ["{#sarva/tra#}", "{#sarva#}", "<lex>adv.</lex>", "<ls>P. 5,3,10</ls>", "<ls>VOP. 7,99</ls>", "<ls>\u015aAT. BR. 2,4,3,9</ls>", "<ls n=\"\u015aAT. BR.\">4,4,1,18</ls>", "<ls>\u0100\u015aV. \u015aR. 9,2,5</ls>", "<ls>K\u0100TY. \u015aR. 3,2,6</ls>", "<ls n=\"K\u0100TY. \u015aR. 3,\">5,8</ls>", "<ls n=\"K\u0100TY. \u015aR.\">4,10,5</ls>", "<ls n=\"K\u0100TY. \u015aR.\">9,6,10</ls>", "<ls n=\"K\u0100TY. \u015aR.\">11,1,7</ls>", "{#svAhAkAraH sa\u02da#}", "<ls n=\"K\u0100TY. \u015aR.\">4,4,18</ls>", "<ls>L\u0100\u1e6cY. 6,10,17</ls>", "{#sa\u02da catvAri#}", "<ls n=\"L\u0100\u1e6cY.\">7,11,9</ls>", "{#devaSabdaM sa\u02da varjayeyuH#}", "<ls n=\"L\u0100\u1e6cY.\">8,9,3</ls>", "<ls>KAU\u015a. 8</ls>", "<ls n=\"KAU\u015a.\">57</ls>", "<ls n=\"KAU\u015a.\">136</ls>", "<ls>VS. PR\u0100T. 2,15</ls>", "<ls n=\"VS. PR\u0100T.\">4,16</ls>", "<ls n=\"VS. PR\u0100T. 4,\">24</ls>", "<ls n=\"VS. PR\u0100T. 4,\">77</ls>", "<ls n=\"VS. PR\u0100T. 4,\">97</ls>", "<ls>AV. PR\u0100T. 3,60</ls>", "<ls>TS. PR\u0100T. 2,25</ls>", "<ls n=\"TS. PR\u0100T.\">12,11</ls>", "<ls n=\"TS. PR\u0100T.\">17,2</ls>", "<ls>P. 4,3,22</ls>", "<ls n=\"P.\">6,1,122</ls>", "<ls n=\"P.\">1,1,34</ls>", "<ab>Schol.</ab>", "<ls>M. 2,180</ls>", "<ls n=\"M.\">7,52</ls>", "<ls n=\"M.\">8,241</ls>", "<ls>R. 1,4,24</ls>", "<ls>\u015a\u0100K. 15</ls>", "<ls>VIKR. 39,14</ls>", "<ls>Spr. (II) 149. fg.</ls>", "<ls n=\"Spr. (II)\">2999</ls>", "<ls n=\"Spr. (II)\">6859. fg.</ls>", "<ls n=\"Spr. (II)\">6916</ls>", "<ls n=\"Spr. (II)\">6918. fg.</ls>", "<ls n=\"Spr. (II)\">7453</ls>", "<ls>VAR\u0100H. B\u1e5aH. S. 11,18</ls>", "<ls n=\"VAR\u0100H. B\u1e5aH. S.\">19,1</ls>", "<ls n=\"VAR\u0100H. B\u1e5aH. S.\">53,69</ls>", "<ls>KATH\u0100S. 24,104</ls>", "<ls>BH\u0100G. P. 7,7,55</ls>", "<ls>HIT. Pr. 2</ls>", "<ls n=\"HIT. Pr.\">10,14</ls>", "<ls>DH\u016aRTAS. 85,10</ls>", "{#sarvatrEva#}", "<ls>\u1e5aV. PR\u0100T. 2,27</ls>", "<ls n=\"\u1e5aV. PR\u0100T.\">4,14</ls>", "<ls>Spr. (II) 6262</ls>", "{#sarvatrApi#}", "<ls n=\"Spr. (II)\">6174</ls>", "{#sarvatra sarvadA#}", "<ls n=\"Spr. (II)\">2338</ls>", "<ls>HARIV. 15055</ls>", "<ls>KAP. 1,117</ls>", "<ls>BH\u0100G. P. 2,2,36</ls>", "{#sarvaTA sarvatra sarvadA#}", "<ls>SARVADAR\u015aANAS. 42,6</ls>", "{#na sa\u02da#}", "<ls>VAR\u0100H. B\u1e5aH. S. 2,16</ls>", "{#sarvasmin#}", "<lex>adj.</lex>", "<ab>subst.</ab>", "{#SAntikarmaRi#}", "<ls>M\u0100RK. P. 92,15</ls>", "{#ASrame#}", "<ab>Schol.</ab>", "<ls>\u015a\u0100K. 7,10</ls>", "{#kuSalaH#}", "<ls>HARIV. 15054</ls>", "{#kuSalam#}", "<ls>MBH. 3,2471</ls>", "<ls>R. 1,52,5</ls>", "<ls n=\"R. 1,52,\">10</ls>", "{#Badram#}", "<ls>PRAB. 30,4</ls>", "{#pramAdI#}", "<ls>VIKR. 30,14</ls>", "{#ramate prAjYaH#}", "<ls>Spr. (II) 6917</ls>", "{#parAjitaH#}", "<ls n=\"Spr. (II)\">7476</ls>", "{#yogyatvam#}", "<ls n=\"Spr. (II)\">7478</ls>", "{#samadfzwitvam#}", "<ls>R\u0100JA-TAR. 1,357</ls>", "<ls>BH\u0100G. P. 3,24,47</ls>", "<ls n=\"BH\u0100G. P.\">6,17,34</ls>", "{#padaM hi sarvatra guRErniDIyate#}", "<ls>RAGH. 3,62</ls>", "{#sarvatrAByAgato guruH#}", "<ab>v. l.</ab>", "{#sarvasyA\u02da#}", "<ls>Spr. (II) 2172</ls>", "<ls n=\"Spr. (II)\">4448</ls>", "{#dayAM kar#}", "<ls n=\"Spr. (II)\">4313</ls>", "{#sarvatra na SoBanaM dAru#}", "<ls>VAR\u0100H. B\u1e5aH. S. 79,37</ls>", "<ab>Vgl.</ab>", "{#sArvatrika#}", "{#sarva/tra#}", "<lex>Adv.</lex>", "{#sarvatrApi#}", "{#sarvatra#}", "{#sarvaTA#}", "{#sarvatra#}", "{#srvadA#}", "{#sarvasmin#}", "<ab>u. s. w.</ab>", "<div n=\"1\">", "<div n=\"1\">", "<div n=\"v\">", "<div n=\"1\">", "<div n=\"1\">"], "sakft": ["{#sakf/t#}", "{#sa#}", "{#kft#}", "<lex>adv.</lex>", "<ls>P. 5,4,19</ls>", "{#saha#}", "<ls>AK. 3,4,32 (28), 4</ls>", "<ls>MED. avy. 33</ls>", "{#sa\\kftsu te\\ anu\\ stoma^M mudImahi#}", "<ls>\u1e5aV. 8,1,14</ls>", "<ls n=\"\u1e5aV.\">2,16,8</ls>", "{#sa\\kftsu no^ mfLaya#}", "<ls n=\"\u1e5aV.\">10,33,3</ls>", "{#a\\ru\\Ro mA^ sa\\kfdvfko^ dadarSa#}", "<ls n=\"\u1e5aV.\">1,105,18</ls>", "<ls n=\"\u1e5aV.\">6,66,1</ls>", "{#na vE sakfdevAgre sarvaH saMBavati#}", "<ls>AIT. BR. 6,21</ls>", "<ls>TS. 3,4,2,2</ls>", "{#sakfdAcCinna/#}", "<ls>\u0100\u015aV. \u015aR. 2,6,4</ls>", "<ls>\u015aAT. BR. 2,4,2,17</ls>", "{#sakfllUna#}", "<ls>\u015a\u0100\u1e44KH. \u015aR. 4,4,6</ls>", "{#sakfllU#}", "<ls>P. 8,2,4</ls>", "<ab>Schol.</ab>", "{#sakfdAdIpana#}", "<ls>KAU\u015a. 80</ls>", "<ls>M. 8,151</ls>", "<ab>v. a.</ab>", "<ls>MBH. 1,4418</ls>", "<ls>AK.</ls>", "<ls>MED.</ls>", "<ls>\u1e5aV. 6,48,22</ls>", "{#sa\\kfdahna^H#}", "<ls n=\"\u1e5aV.\">10,95,16</ls>", "<ls>TBR. 2,1,9,1</ls>", "<ls>AIT. BR. 1,26</ls>", "<ls n=\"AIT. BR.\">2,24</ls>", "<ls n=\"AIT. BR.\">7,17</ls>", "<ls>\u015aAT. BR. 1,2,3,11</ls>", "<ls n=\"\u015aAT. BR.\">2,4,3,9</ls>", "{#sakfdindraM BUtAnyatyaricyanta#}", "<ls n=\"\u015aAT. BR.\">4,5,3,1</ls>", "<ls>\u0100\u015aV. G\u1e5aHY. 1,3,3</ls>", "{#sakfnmantravacanam#}", "<ls>K\u0100TY. \u015aR. 1,7,9</ls>", "{#sakfdgfhIta#}", "<ls n=\"K\u0100TY. \u015aR.\">8,46</ls>", "{#sakfdupamaTita/#}", "<ls>\u015aAT. BR. 2,6,1,6</ls>", "<ls>K\u0100TY. \u015aR. 24,3,34</ls>", "<ls>M. 6,20</ls>", "<ls n=\"M.\">11,92</ls>", "<ls n=\"M. 11,\">97</ls>", "<ls n=\"M. 11,\">100</ls>", "<ls n=\"M. 11,\">214</ls>", "<ls n=\"M. 11,\">250</ls>", "<ls>Spr. (II) 5253. fgg.</ls>", "<ls n=\"Spr. (II)\">6650. fgg.</ls>", "<ls n=\"Spr. (II)\">6656</ls>", "<ls>\u015a\u0100K. 27,2</ls>", "<ls>VIKR. 10</ls>", "<ls>VAR\u0100H. B\u1e5aH. S. 11,44</ls>", "{#sakfduktaM na gfhRAti#}", "<ls>Spr. (II) 6655</ls>", "{#sakfduktagfhItArTa#}", "<ls n=\"Spr. (II)\">6654</ls>", "{#sakfcCrutaDara#}", "<ls>KATH\u0100S. 2,61</ls>", "{#sakftsakft#}", "<ls>\u015aAT. BR. 1,8,2,5</ls>", "<ls>\u0100\u015aV. G\u1e5aHY. 4,7,14</ls>", "<ls>M. 5,139</ls>", "<ls n=\"M.\">9,70</ls>", "<ls>Y\u0100J\u00d1. 1,240</ls>", "<ab>v. a.</ab>", "<ls>Spr. (II) 1707</ls>", "{#sakftkftapraRayo 'yaM janaH#}", "<ab>v. a.</ab>", "<ls>\u015a\u0100K. 59,13</ls>", "{#mA \u2014 sakft#}", "<ls>Spr. (II) 2304</ls>", "{#sakfddivA hEvAsmE Bavati#}", "<ls>CH\u0100ND. UP. 3,11,3</ls>", "{#sakfdviBAta#}", "<ls n=\"CH\u0100ND. UP.\">8,4,2</ls>", "<ls>N\u1e5aS. T\u0100P. UP.</ls>", "<ls>Ind. St. 9,165</ls>", "<ls>VED\u0100NTAS. (Allah.) No. 124</ls>", "{#BAnuH sakfdyuktaturaMga eva#}", "<ls>Spr. (II) 4569</ls>", "<ls>M\u0100RK. P. 109,67</ls>", "<ab>Vgl.</ab>", "{#a\u02da#}", "<ls>MBH. 5,7160</ls>", "<ls>VAR\u0100H. B\u1e5aH. S. 28,4</ls>", "<ls n=\"VAR\u0100H. B\u1e5aH. S.\">30,3</ls>", "<ls n=\"VAR\u0100H. B\u1e5aH. S.\">68,74</ls>", "<ls>BH\u0100G. P. 1,5,36</ls>", "<ls>ed. Bomb.</ls>", "{#sakf/t#}", "<lex>Adj.</lex>", "<ls>AV. 11,1,10</ls>", "{#sayuj#}", "<ls>{{PAIPP.->AV.PAIPP.||20160118|Jim Funderburk.|https://github.com/sanskrit-lexicon/CORRECTIONS/issues/237|inferred}}</ls>", "<lex>Adv.</lex>", "<ab>Nom. abstr.</ab>", "{#sakfttva#}", "<lex>n.</lex>", "<ls>Comm. zu NY\u0100YAM. 9,3,13</ls>", "{#a/hnas#}", "{#sakfdA#}", "<ls>VET. (U.) 204,23</ls>", "<ab>v. a.</ab>", "<ab>Neg.</ab>", "<ls>P\u016br\u1e47abh. 56,12,</ls>", "<hom>", "</hom>", "<div n=\"1\">", "<div n=\"1\">", "<div n=\"1\">", "<div n=\"v\">", "<div n=\"1\">", "<div n=\"1\">", "<div n=\"2\">", "<div n=\"2\">", "<div n=\"2\">", "<div n=\"2\">", "<div n=\"2\">"]}
const FRAGS = {"nakzatra": [[{"skeleton": "=== LAYER: PWG \u2014 MAIN ENTRY (B\u00f6htlingk-Roth, large) ===\n\n{T1}\u00a6 {T2}. {T3}", "ls": 1, "sk": 1, "fsha": "1b2f436f5a470110e2e5a1c6ee61a636dd4c9055eb22e8c85b9f03ed81c76906", "si": 0}], [{"skeleton": "{T27} 1\u3009 {%Gestirn%} {T1} (auch von der Sonne gebraucht) {T2}. {T3}. {T4} ({T5}) {T6} {T7}. {T8} {T9}. {T10} {T11}. {T12}. {T13}. {%Sterne%} {T14}. {T15}. {T16} {T17}. {T18} {T19}. {T20}. {T21}. {T22}. {T23}. {T24}. {T25}. {T26}. ", "ls": 18, "sk": 6, "fsha": "b8be0efccc240d0a341f3bf6408983327aa5370951e7a1afc05c592f1cdb2373", "si": 0}], [{"skeleton": "{T1}. {T2}. {T3}. {T4}. {T5} {T6}. {T7} {T8}. {T9}. {T10} {T11}. {T12}. Diese f\u00fcnf bilden bei den {T13} die Gruppe der {T14} {T15}. {T16} {T17}. {T18} {T19}. {T20}. {T21}. {T22}. {T23} {T24}. {T25}. {T26}. {T27} ", "ls": 18, "sk": 7, "fsha": "11197caafc67379d8930f660735da9a2fa03e365db222f0d7757b645f20fd40a", "si": 0}], [{"skeleton": "{T1}. Ein Mal {T2}: {T3} {T4}. {T5} {%aus einem Stern bestehend%} {T6}. {T7}. {T8}.", "ls": 5, "sk": 2, "fsha": "a324abfbd8ad4fa3d2c411fc92b0e1b0528e7e162aaef1c873950c3037d9c492", "si": 0}], [{"skeleton": "{T23}\u2014 2\u3009 im {T1} {%die Mondstationen%}; in der \u00e4lteren Zeit (aber auch noch im {T2}) 27, sp\u00e4ter 28 an der Zahl. Dieselben werden in der Folge auch als {%Gemahlinnen des Mondes%}, als T\u00f6chter {T3}\u02bcs, augfefasst. {T4}. {T5}. {T6}. {T7}. {T8}. {T9}. {T10}. {T11}. {T12}. {T13}, {T14}. {T15} {T16} {T17} {T18}. {T19}. {T20}. {T21}. {T22} ", "ls": 18, "sk": 2, "fsha": "00bfe9824fc4e08424b2cbc5e3368fefadd7a4be84b71d03f575c921bc41607e", "si": 1}], [{"skeleton": "{T1}. Die Namen derselben {T2} {T3} {T4} {T5}, {T6}. {T7}, Die vedischen Nachrichten von den Nakshatra.", "ls": 5, "sk": 0, "fsha": "cc825719a113b4f54804afb1ef292387101b7c6333112914204809f3c8118714", "si": 1}], [{"skeleton": "{T24}\u2014 3\u3009 {%Perle%} {T1}_im_{T2} \u2014 Was die Etymologie betrifft, so l\u00e4sst sich gegen die von {T3}_in_{T4} vorgebrachte ({T5} + {T6}) einwenden, dass {%W\u00e4chter der Nacht%} nicht auf die Sonne passt, welche in den \u00e4ltesten Texten vorzugsweise {T7} genannt wird. Die Gleichsetzung von {T8} mit {T9} erregt gleichfalls Bedenken. Eher liesse sich noch an eine Zur\u00fcckf\u00fchrung auf {T10} ({T11} {T12}. {T13}.) denken, dann w\u00e4ren die Gestirne {%die am Himmel Heraufkommenden%}. Die spielende Zerlegung in {T14} + {T15} findet sich {T16}. {T17}. {T18}. {T19}.\n{T25}\u2014 {T20} {T21}.\n\n=== LAYER: PW \u2014 B\u00f6htlingk k\u00fcrzere Fassung (revision of PWG; may correct gender/sense) ===\n\n{T22}\u00a6 {T23}", "ls": 10, "sk": 10, "fsha": "1cffdfe8f04968861b3fb6b34f458fa09b22c429814d458aa11fbcc770e42383", "si": 2}, {"skeleton": "{T7}\u2014 1\u3009 {%Gestirn, Stern;%} {T1} {%die Sonne und die Sterne%} ({T2}) Einmal {T3} als Personification. Am Ende eines {T4} {T5} {T6}", "ls": 0, "sk": 1, "fsha": "c6a920325c35ecbaf568c214adf337301f7445484ed97c7f220d31d20d84a2a1", "si": 3}], [{"skeleton": "{T2}\u2014 2\u3009 {%Mondhaus,%} deren in der \u00e4lteren Zeit 27, sp\u00e4ter 28 angenommen werden. Personificirt als T\u00f6chter {T1}\u02bcs und Gattinnen des Mondes.", "ls": 0, "sk": 0, "fsha": "c66c128ad539c959a2ede7d1e2eb213eb8ae10cf30c33ebd2b75079880145328", "si": 4}, {"skeleton": "{T17}\u2014 3\u3009 *{%Perle%} {T1}. {T2} {T3} 3\u3009.\n\n=== LAYER: PW \u2014 B\u00f6htlingk k\u00fcrzere Fassung (revision of PWG; may correct gender/sense) ===\n\n{T4}\u00a6 {T5} {T6} eines {T7} {T8}.{T18}\n\n=== LAYER: PW \u2014 B\u00f6htlingk k\u00fcrzere Fassung (revision of PWG; may correct gender/sense) ===\n\n{T9}\u00a6 III. 5.{T19}\n\n=== LAYER: SCH \u2014 Schmidt Nachtr\u00e4ge 1928 (pure addenda to PW; \u00b0=new vs pw, *=first attestation) ===\n\n{%Nak\u1e63atra%}\u00a6 m. N. pr. eines Ek\u0101da\u015b\u0101\u1e45gin, {T10} {part=,seq=16531,type=,n=2}\n\n=== LAYER: PWKVN \u2014 PWK variant supplement (keyed to PW sense numbers) ===\n\n{T11}\u00a6 {T12} {T13} eines {T14} {T15}.\n\n=== LAYER: PWKVN \u2014 PWK variant supplement (keyed to PW sense numbers) ===\n\n{T16}\u00a6 III. 5.", "ls": 4, "sk": 5, "fsha": "508f5a94793a5f70e5ab90ec43b4e861d811fc7ef5f9bd34be791892b1f6fd11", "si": 5}]], "sarvatra": [[{"skeleton": "=== LAYER: PWG \u2014 MAIN ENTRY (B\u00f6htlingk-Roth, large) ===\n\n{T1}\u00a6 (von {T2}) {T3} {T4}. {T5}.", "ls": 2, "sk": 2, "fsha": "17da0f62ee1d4d948cf373ccd88d948f92a4a1a27c95a8697f6100d541f4d0f1", "si": 0}], [{"skeleton": "{T22} 1\u3009 {%\u00fcberall, stets, in allen F\u00e4llen, jederzeit%} {T1}. {T2}. {T3}. {T4}. {T5}. {T6}. {T7}. {T8}. {T9} {T10}. {T11}. {T12} {T13}. {T14} {T15}. {T16}. {T17}. {T18}. {T19}. {T20}. {T21}. ", "ls": 18, "sk": 3, "fsha": "83be11aa6f7d9af2a1590703ab316b7d5f8c3b827073acdff0c989f7e5f073ae", "si": 0}], [{"skeleton": "{T1}. {T2}. {T3}. {T4}. {T5}. {T6}. {T7}. {T8}. {T9}, {T10} {T11}. {T12}. {T13}. {T14}. {T15}. {T16}. {T17} {T18}. {T19} ", "ls": 18, "sk": 0, "fsha": "6ba07297d3f74267f2c788e53668ceeaae017e236a7b97871ce73a11919d099c", "si": 0}], [{"skeleton": "{T1}. {T2} {T3}. {T4}. {T5}. {T6}. {T7}. {T8}. {T9}. {T10}. {T11}. {T12} {T13}. {T14}. {T15}. {T16} {T17}. {T18} {T19}. {T20}. {T21}. ", "ls": 18, "sk": 3, "fsha": "2c5e948dd5468e36da315cabbe2b7a86cb0a42c6a3eddc224f8473f44742f104", "si": 0}], [{"skeleton": "{T1}. {T2} {T3}. {T4} {%in keinem Falle%} {T5}.", "ls": 3, "sk": 2, "fsha": "1cb901edbb1fc27787bf428c1f6c59cd320dc10967307208771f22e5f5fc66fc", "si": 0}], [{"skeleton": "{T39}\u2014 2\u3009 = {T1} {T2} und {T3} {T4} {T5}. {T6} {T7} zu {T8}. {T9} {T10}. {T11} {T12}. {T13}. {T14} {T15} {T16}. {T17} {T18}. {T19} {T20}. {T21} {T22}. {T23} {T24}. {T25} {T26}. {T27}. {T28}. {T29} {T30}. {T31} ({T32} {T33}) {T34}. {T35}. {T36} {T37}. {T38} {%Holz f\u00fcr Nichts gut%} ", "ls": 18, "sk": 16, "fsha": "3b169a682d14987b60c9724cecfaa234e260111e08a74b2782c64eef03900306", "si": 1}], [{"skeleton": "{T1}.\n{T6}\u2014 {T2} {T3}.\n\n=== LAYER: PW \u2014 B\u00f6htlingk k\u00fcrzere Fassung (revision of PWG; may correct gender/sense) ===\n\n{T4}\u00a6 {T5}", "ls": 1, "sk": 2, "fsha": "9ed1d28bca73d15918b24333facc7f2bb22dd13e85154b9d79c588aa092dd63b", "si": 1}, {"skeleton": "{T6}\u2014 1\u3009 {%\u00fcberall, stets, in allen F\u00e4llen, jederzeit%}. Verst\u00e4rkt {T1} {T2} {T3} {T4} {T5}. Mit einer Negation {%in keinem Falle%}.", "ls": 0, "sk": 5, "fsha": "6f0e5817cc0df64f642f0b81d1de2285bc399d113e34a1eb91637f869ac37582", "si": 2}, {"skeleton": "{T3}\u2014 2\u3009 = {T1} mit einer Negation {%f\u00fcr Nichts%} {T2}", "ls": 0, "sk": 1, "fsha": "63cbd26842dfcd4ab63e438539ec682ff6ed65ed189e39f3e390a4b06cfc9323", "si": 3}]], "sakft": [[{"skeleton": "=== LAYER: PWG \u2014 MAIN ENTRY (B\u00f6htlingk-Roth, large) ===\n\n{T1}\u00a6 ({T33}2.{T34} {T2} + {T3}) {T4} {T5}.\n{T35} 1\u3009 {%auf ein Mal, mit einem Male%}; = {T6} {T7}. {T8}. {T9} {T10}. {T11}. {T12} {T13}. {T14} {T15}. {T16}. {T17} {T18}. {T19}. {T20} {%mit einem Ruck abgetrennt%} {T21}. {T22}. {T23} {T24}. {T25} {T26}, {T27} {T28} {T29}. {T30}. so {T31} {%pl\u00f6tzlich%} {T32}.", "ls": 17, "sk": 12, "fsha": "10e6ee03d139667e828669d91dd62f1044888f5a290809fb29651505df059d84", "si": 0}], [{"skeleton": "{T24}\u2014 2\u3009 {%einmal, semel%} {T1} {T2} {T3}. {T4} {T5}. {T6}. {T7}. {T8}. {T9}. {T10}. {T11}. [Page7-0508] {T12} {T13}. {T14}. {T15} {T16}. {T17} {T18}. {T19} {T20}. {T21}. {T22}. {T23}. ", "ls": 18, "sk": 5, "fsha": "0e0b3ea9fe25a48ea160bc03d51beb9dce8c5d929d3c5f36327d58a665c7f7c3", "si": 1}], [{"skeleton": "{T1}. {T2}. {T3}. {T4}. {T5} {T6} {T7}. {T8}. {T9}. {T10}. {T11} {T12}. {T13} {T14}. {T15} {T16}. {T17} {T18}. {T19}. {T20}. {T21}. {T22}. {%einmal%} so {T23} {%irgend ein Mal%} ", "ls": 18, "sk": 4, "fsha": "7c7005ac914765c4f279e3a085a128cbeaa1009a1623f9ee4710949db1104af2", "si": 1}], [{"skeleton": "{T1}. {T2} so {T3} {%einst, ehemals%} {T4}. {T5} {%nie%} {T6}.", "ls": 3, "sk": 2, "fsha": "8be23aa567472ef3b67fbedd17017f1f2703af1d196fe6b3a057b5b0ddabb161", "si": 1}], [{"skeleton": "{T20}\u2014 3\u3009 {%ein f\u00fcr allemal, f\u00fcr immer%}: {T1} {T2}. {T3} {T4}. {T5}_in_{T6}. {T7}. {T8} {T9}. {T10}.\n{T21}\u2014 {T11} {T12} (auch {T13}. {T14}. {T15}. {T16}. {T17} nach der Lesart der {T18}).\n\n=== LAYER: PW \u2014 B\u00f6htlingk k\u00fcrzere Fassung (revision of PWG; may correct gender/sense) ===\n\n{T19}\u00a6", "ls": 13, "sk": 5, "fsha": "351f0f02403ffaac9fb50953be8bced25f622ecec63206aa6ee5934f5bcf25af", "si": 2}], [{"skeleton": "{T5}\u2014 1\u3009 {T1} {%gleichzeitig th\u00e4tig%} {T2}. {T3} {T4}", "ls": 2, "sk": 1, "fsha": "d9b0d33b8a57bebcc476e84f3058ecd427e063fb6acc912dba621e879acf98e2", "si": 3}, {"skeleton": "{T2}\u2014 2\u3009 {T1}", "ls": 0, "sk": 0, "fsha": "0bc39d5502502a2f4717317f3a29ba2f17fb930fdeb4ad168d17b97a2db24cde", "si": 4}, {"skeleton": "{T5}\u2014 a\u3009 {%auf ein Mal, mit einem Male, mit einem Ruck, pl\u00f6tzlich%}. {T1} {T2} {T3} {T4}.", "ls": 1, "sk": 1, "fsha": "ec44d2d44ddb0ec9647cf70319e6cc103394046e1d37bcf71ca9132ff32aa99f", "si": 5}, {"skeleton": "{T4}\u2014 b\u3009 {%einmal, semel%}. {T1} {%einmal am Tage%}. Wiederholt {%immer nur einmal%}. {T2} (!) {T3}.", "ls": 1, "sk": 2, "fsha": "935076f00712f7e749a691ca6defc864f032a4de0901134a2a65ac615fcd7718", "si": 6}, {"skeleton": "{T3}\u2014 c\u3009 {%einmal,%} so {T1} {%irgend ein mal;%} mit der {T2} {%nie%}.", "ls": 0, "sk": 0, "fsha": "5d06c009ebf0aa8004fde0f3ec3e8082f5a79dda081ecaf5b0167a848e0a990a", "si": 7}, {"skeleton": "{T1}\u2014 d\u3009 {%einst, ehemals%}.", "ls": 0, "sk": 0, "fsha": "4ac2a417359a9b469c4b1c79b120829e49cee897276512151974c74f036f1373", "si": 8}, {"skeleton": "{T2}\u2014 e\u3009 {%ein f\u00fcr allemal, f\u00fcr immer%}.\n\n=== LAYER: SCH \u2014 Schmidt Nachtr\u00e4ge 1928 (pure addenda to PW; \u00b0=new vs pw, *=first attestation) ===\n\n\u00b0{%sak\u1e5bt%}\u00a6 {T1} wrong spelling of our author for {%\u015bak\u1e5bt%} (pun with {%asak\u1e5bt%}). {part=,seq=25923,type=\u02da,n=3}", "ls": 1, "sk": 0, "fsha": "ea4b94f8f63b90fc33b1eb3f7672bd6d72971dcf9eedaa9096f7732f2e8fdda6", "si": 9}]]}
const PHF = {"nakzatra": [[["{#na/kzatra#}", "<ls>U\u1e46\u0100DIS. 3,105</ls>", "<lex>n.</lex>"]], [["<ab>\u00fcberh.</ab>", "<ls>AK. 1,1,2,22</ls>", "<ls>H. 107</ls>", "{#dvi\\tA nakza^traM#}", "<ab>coll.</ab>", "{#pa\\praTa^cca\\ BUma^#}", "<ls>\u1e5aV. 7,86,1</ls>", "{#udu\\sriyA^H sfjeta\\ sUrya\\H sacA^~ u\\dyannakza^tramarci\\vat#}", "<ls n=\"\u1e5aV. 7,\">81,2</ls>", "{#nakza^traM pra\\tnamami^naccari\\zRu#}", "<ls n=\"\u1e5aV.\">10,88,13</ls>", "<ls n=\"\u1e5aV. 10,\">111,7</ls>", "<ls n=\"\u1e5aV. 10,\">156,4</ls>", "<ls n=\"\u1e5aV.\">1,50,2</ls>", "<ls n=\"\u1e5aV.\">3,54,19</ls>", "{#a\\Bi nakza^treBiH pi\\taro\\ dyAma^piMSan#}", "<ls n=\"\u1e5aV.\">10,68,11</ls>", "{#nakza^trARAme\\zAmu\\pasTe\\ soma\\ Ahi^taH#}", "<ls n=\"\u1e5aV. 10,\">85,2</ls>", "<ls>AV. 6,128,1</ls>", "<ls n=\"AV. 6,128,\">3</ls>", "<ls n=\"AV.\">7,13,1</ls>", "<ls n=\"AV.\">9,7,15</ls>", "<ls n=\"AV.\">15,6,2</ls>", "<ls>AIT. BR. 4,25</ls>", "<ls>VS. 14,19</ls>", "<div n=\"1\">"]], [["<ls n=\"VS.\">18,18</ls>", "<ls n=\"VS.\">22,28</ls>", "<ls>\u0100\u015aV. G\u1e5aHY. 4,4</ls>", "<ls>L\u0100\u1e6cY. 3,8,10</ls>", "{#nakzatrARi grahAstaTA#}", "<ls>M. 1,24</ls>", "{#vijYAya niSi panTAnaM nakzatragaRasUcitam#}", "<ls>HI\u1e0c. 1,3</ls>", "<ls>N. 5,6</ls>", "{#candrAdityO grahanakzatratArAH#}", "<ls>MBH. 13,7386</ls>", "<ls n=\"MBH.\">1,7677</ls>", "<is>Jaina</is>", "<is>Jyoti\u1e63ka</is>", "<ls>H. 92</ls>", "{#puRye tiTO muhUrte vA nakzatre vA guRAnvite#}", "<ls>M. 2,30</ls>", "{#nakzatrEryaSca jIvati#}", "<ls n=\"M.\">3,162</ls>", "<ls>SU\u015aR. 1,17,8</ls>", "<ls n=\"SU\u015aR. 1,\">114,4</ls>", "<ls n=\"SU\u015aR. 1,\">103,2</ls>", "{#dyOH sacandrArkanakzatrA#}", "<ls>MBH. 13,7070</ls>", "<ls n=\"MBH.\">3,12549</ls>", "<ls n=\"MBH. 3,\">16038</ls>", "{#\u02daSirasi#}"]], [["<ls>HARIV. 12239</ls>", "<ab>masc.</ab>", "{#df\\|o nakza^tra u\\ta vi\\Svade^vo\\ BUmi\\mAtA\\ndyAM DA\\sinA\\yoH#}", "<ls>\u1e5aV. 6,67,6</ls>", "{#eka\u02da#}", "<ls>\u015aAT. BR. 13,8,1,3</ls>", "<ls>K\u0100TY. \u015aR. 21,3,3</ls>", "<ls>\u0100\u015aV. G\u1e5aHY. 4,5</ls>"]], [["<ab>Bes.</ab>", "<ls>HARIV.</ls>", "<is>Dak\u1e63a</is>", "<ls>AV. 19,8,1</ls>", "<ls>VS. 18,40</ls>", "<ls>TS. 2,3,5,1</ls>", "<ls n=\"TS.\">3,4,7,1</ls>", "<ls>TBR. 1,5,1,1</ls>", "<ls n=\"TBR. 1,5,\">2,5</ls>", "<ls n=\"TBR.\">2,7,18,13</ls>", "<ls>\u015aAT. BR. 6,5,4,8</ls>", "<ls n=\"\u015aAT. BR.\">9,4,1,9</ls>", "<ls n=\"\u015aAT. BR.\">10,5,4,17</ls>", "<ls>P. 1,2,60</ls>", "<ls>MBH. 13,3256. fgg.</ls>", "<ls n=\"MBH. 13,\">4255. fgg.</ls>", "{#SizwAH (kanyAH) somAya rAjYe 'Ta nakzatrAKyA dadO praBuH (dakzaH)#}", "<ls>HARIV. 104</ls>", "<ls n=\"HARIV.\">1332</ls>", "<ls n=\"HARIV.\">11522</ls>", "<ls n=\"HARIV.\">11524</ls>", "{#kfttikAdIni nakzatrARIndoH patnyastu#}", "<div n=\"1\">"]], [["<ls>BH\u0100G. P. 6,6,23</ls>", "<ab>s.</ab>", "<ls>Ind. St. 1,89. fgg.</ls>", "<ab>Vgl.</ab>", "<ls>WARREN</ls>", "<ls>K\u0100LAS. 372</ls>", "<ls>WEBER</ls>"]], [["<ls>R\u0100JAN.</ls>", "<ls>\u015aKDR.</ls>", "<ls>AUFRECHT</ls>", "<ls>Z. f. vgl. Spr. 8,71</ls>", "{#nakza#}", "{#tra#}", "{#nakzatra#}", "{#nakza#}", "{#nakta#}", "{#nakz#}", "<ab>vgl.</ab>", "<ls>NIR. 3,20</ls>", "<ls>TBR. 1,5,2,5</ls>", "{#na#}", "{#kzatra#}", "<ls>NIR. 3,20</ls>", "<ls>\u015aAT. BR. 2,1,2,18</ls>", "<ls n=\"\u015aAT. BR. 2,1,2,\">19</ls>", "<ls>P. 6,3,75</ls>", "<ab>Vgl.</ab>", "{#deva\u02da, yama\u02da#}", "{#na/kzatra#}", "<lex>n.</lex>", "<div n=\"1\">", "<div n=\"v\">"], ["<ab>Sg.</ab>", "<ab>coll.</ab>", "<lex>m.</lex>", "<ab>adj. Comp.</ab>", "<lex>f.</lex>", "{#A#}", "<div n=\"1\">"]], [["<is>Dak\u1e63a</is>", "<div n=\"1\">"], ["<ls>R\u0100JAN. 13,154</ls>", "<ab>Vgl.</ab>", "{#nakzatramAlA#}", "{#nakzatra#}", "<lex>m.</lex>", "<ab>N. pr.</ab>", "<is>Ek\u0101da\u015b\u0101\u1e45gin</is>", "<ls>VARDHAM\u0100NAC. 1,48</ls>", "{#na/kzatra#}", "<ls>Vardham\u0101nac. 1,48.</ls>", "{#nakzatra#}", "<lex>m.</lex>", "<ab>N. pr.</ab>", "<is>Ek\u0101da\u015b\u0101\u1e45gin</is>", "<ls>VARDHAM\u0100NAC. 1,48</ls>", "{#na/kzatra#}", "<div n=\"1\">", "<info n=\"sup_5\"/>", "<info n=\"sup_7\"/>"]]], "sarvatra": [[["{#sarva/tra#}", "{#sarva#}", "<lex>adv.</lex>", "<ls>P. 5,3,10</ls>", "<ls>VOP. 7,99</ls>"]], [["<ls>\u015aAT. BR. 2,4,3,9</ls>", "<ls n=\"\u015aAT. BR.\">4,4,1,18</ls>", "<ls>\u0100\u015aV. \u015aR. 9,2,5</ls>", "<ls>K\u0100TY. \u015aR. 3,2,6</ls>", "<ls n=\"K\u0100TY. \u015aR. 3,\">5,8</ls>", "<ls n=\"K\u0100TY. \u015aR.\">4,10,5</ls>", "<ls n=\"K\u0100TY. \u015aR.\">9,6,10</ls>", "<ls n=\"K\u0100TY. \u015aR.\">11,1,7</ls>", "{#svAhAkAraH sa\u02da#}", "<ls n=\"K\u0100TY. \u015aR.\">4,4,18</ls>", "<ls>L\u0100\u1e6cY. 6,10,17</ls>", "{#sa\u02da catvAri#}", "<ls n=\"L\u0100\u1e6cY.\">7,11,9</ls>", "{#devaSabdaM sa\u02da varjayeyuH#}", "<ls n=\"L\u0100\u1e6cY.\">8,9,3</ls>", "<ls>KAU\u015a. 8</ls>", "<ls n=\"KAU\u015a.\">57</ls>", "<ls n=\"KAU\u015a.\">136</ls>", "<ls>VS. PR\u0100T. 2,15</ls>", "<ls n=\"VS. PR\u0100T.\">4,16</ls>", "<ls n=\"VS. PR\u0100T. 4,\">24</ls>", "<div n=\"1\">"]], [["<ls n=\"VS. PR\u0100T. 4,\">77</ls>", "<ls n=\"VS. PR\u0100T. 4,\">97</ls>", "<ls>AV. PR\u0100T. 3,60</ls>", "<ls>TS. PR\u0100T. 2,25</ls>", "<ls n=\"TS. PR\u0100T.\">12,11</ls>", "<ls n=\"TS. PR\u0100T.\">17,2</ls>", "<ls>P. 4,3,22</ls>", "<ls n=\"P.\">6,1,122</ls>", "<ls n=\"P.\">1,1,34</ls>", "<ab>Schol.</ab>", "<ls>M. 2,180</ls>", "<ls n=\"M.\">7,52</ls>", "<ls n=\"M.\">8,241</ls>", "<ls>R. 1,4,24</ls>", "<ls>\u015a\u0100K. 15</ls>", "<ls>VIKR. 39,14</ls>", "<ls>Spr. (II) 149. fg.</ls>", "<ls n=\"Spr. (II)\">2999</ls>", "<ls n=\"Spr. (II)\">6859. fg.</ls>"]], [["<ls n=\"Spr. (II)\">6916</ls>", "<ls n=\"Spr. (II)\">6918. fg.</ls>", "<ls n=\"Spr. (II)\">7453</ls>", "<ls>VAR\u0100H. B\u1e5aH. S. 11,18</ls>", "<ls n=\"VAR\u0100H. B\u1e5aH. S.\">19,1</ls>", "<ls n=\"VAR\u0100H. B\u1e5aH. S.\">53,69</ls>", "<ls>KATH\u0100S. 24,104</ls>", "<ls>BH\u0100G. P. 7,7,55</ls>", "<ls>HIT. Pr. 2</ls>", "<ls n=\"HIT. Pr.\">10,14</ls>", "<ls>DH\u016aRTAS. 85,10</ls>", "{#sarvatrEva#}", "<ls>\u1e5aV. PR\u0100T. 2,27</ls>", "<ls n=\"\u1e5aV. PR\u0100T.\">4,14</ls>", "<ls>Spr. (II) 6262</ls>", "{#sarvatrApi#}", "<ls n=\"Spr. (II)\">6174</ls>", "{#sarvatra sarvadA#}", "<ls n=\"Spr. (II)\">2338</ls>", "<ls>HARIV. 15055</ls>", "<ls>KAP. 1,117</ls>"]], [["<ls>BH\u0100G. P. 2,2,36</ls>", "{#sarvaTA sarvatra sarvadA#}", "<ls>SARVADAR\u015aANAS. 42,6</ls>", "{#na sa\u02da#}", "<ls>VAR\u0100H. B\u1e5aH. S. 2,16</ls>"]], [["{#sarvasmin#}", "<lex>adj.</lex>", "<ab>subst.</ab>", "{#SAntikarmaRi#}", "<ls>M\u0100RK. P. 92,15</ls>", "{#ASrame#}", "<ab>Schol.</ab>", "<ls>\u015a\u0100K. 7,10</ls>", "{#kuSalaH#}", "<ls>HARIV. 15054</ls>", "{#kuSalam#}", "<ls>MBH. 3,2471</ls>", "<ls>R. 1,52,5</ls>", "<ls n=\"R. 1,52,\">10</ls>", "{#Badram#}", "<ls>PRAB. 30,4</ls>", "{#pramAdI#}", "<ls>VIKR. 30,14</ls>", "{#ramate prAjYaH#}", "<ls>Spr. (II) 6917</ls>", "{#parAjitaH#}", "<ls n=\"Spr. (II)\">7476</ls>", "{#yogyatvam#}", "<ls n=\"Spr. (II)\">7478</ls>", "{#samadfzwitvam#}", "<ls>R\u0100JA-TAR. 1,357</ls>", "<ls>BH\u0100G. P. 3,24,47</ls>", "<ls n=\"BH\u0100G. P.\">6,17,34</ls>", "{#padaM hi sarvatra guRErniDIyate#}", "<ls>RAGH. 3,62</ls>", "{#sarvatrAByAgato guruH#}", "<ab>v. l.</ab>", "{#sarvasyA\u02da#}", "<ls>Spr. (II) 2172</ls>", "<ls n=\"Spr. (II)\">4448</ls>", "{#dayAM kar#}", "<ls n=\"Spr. (II)\">4313</ls>", "{#sarvatra na SoBanaM dAru#}", "<div n=\"1\">"]], [["<ls>VAR\u0100H. B\u1e5aH. S. 79,37</ls>", "<ab>Vgl.</ab>", "{#sArvatrika#}", "{#sarva/tra#}", "<lex>Adv.</lex>", "<div n=\"v\">"], ["{#sarvatrApi#}", "{#sarvatra#}", "{#sarvaTA#}", "{#sarvatra#}", "{#srvadA#}", "<div n=\"1\">"], ["{#sarvasmin#}", "<ab>u. s. w.</ab>", "<div n=\"1\">"]]], "sakft": [[["{#sakf/t#}", "{#sa#}", "{#kft#}", "<lex>adv.</lex>", "<ls>P. 5,4,19</ls>", "{#saha#}", "<ls>AK. 3,4,32 (28), 4</ls>", "<ls>MED. avy. 33</ls>", "{#sa\\kftsu te\\ anu\\ stoma^M mudImahi#}", "<ls>\u1e5aV. 8,1,14</ls>", "<ls n=\"\u1e5aV.\">2,16,8</ls>", "{#sa\\kftsu no^ mfLaya#}", "<ls n=\"\u1e5aV.\">10,33,3</ls>", "{#a\\ru\\Ro mA^ sa\\kfdvfko^ dadarSa#}", "<ls n=\"\u1e5aV.\">1,105,18</ls>", "<ls n=\"\u1e5aV.\">6,66,1</ls>", "{#na vE sakfdevAgre sarvaH saMBavati#}", "<ls>AIT. BR. 6,21</ls>", "<ls>TS. 3,4,2,2</ls>", "{#sakfdAcCinna/#}", "<ls>\u0100\u015aV. \u015aR. 2,6,4</ls>", "<ls>\u015aAT. BR. 2,4,2,17</ls>", "{#sakfllUna#}", "<ls>\u015a\u0100\u1e44KH. \u015aR. 4,4,6</ls>", "{#sakfllU#}", "<ls>P. 8,2,4</ls>", "<ab>Schol.</ab>", "{#sakfdAdIpana#}", "<ls>KAU\u015a. 80</ls>", "<ls>M. 8,151</ls>", "<ab>v. a.</ab>", "<ls>MBH. 1,4418</ls>", "<hom>", "</hom>", "<div n=\"1\">"]], [["<ls>AK.</ls>", "<ls>MED.</ls>", "<ls>\u1e5aV. 6,48,22</ls>", "{#sa\\kfdahna^H#}", "<ls n=\"\u1e5aV.\">10,95,16</ls>", "<ls>TBR. 2,1,9,1</ls>", "<ls>AIT. BR. 1,26</ls>", "<ls n=\"AIT. BR.\">2,24</ls>", "<ls n=\"AIT. BR.\">7,17</ls>", "<ls>\u015aAT. BR. 1,2,3,11</ls>", "<ls n=\"\u015aAT. BR.\">2,4,3,9</ls>", "{#sakfdindraM BUtAnyatyaricyanta#}", "<ls n=\"\u015aAT. BR.\">4,5,3,1</ls>", "<ls>\u0100\u015aV. G\u1e5aHY. 1,3,3</ls>", "{#sakfnmantravacanam#}", "<ls>K\u0100TY. \u015aR. 1,7,9</ls>", "{#sakfdgfhIta#}", "<ls n=\"K\u0100TY. \u015aR.\">8,46</ls>", "{#sakfdupamaTita/#}", "<ls>\u015aAT. BR. 2,6,1,6</ls>", "<ls>K\u0100TY. \u015aR. 24,3,34</ls>", "<ls>M. 6,20</ls>", "<ls n=\"M.\">11,92</ls>", "<div n=\"1\">"]], [["<ls n=\"M. 11,\">97</ls>", "<ls n=\"M. 11,\">100</ls>", "<ls n=\"M. 11,\">214</ls>", "<ls n=\"M. 11,\">250</ls>", "<ls>Spr. (II) 5253. fgg.</ls>", "<ls n=\"Spr. (II)\">6650. fgg.</ls>", "<ls n=\"Spr. (II)\">6656</ls>", "<ls>\u015a\u0100K. 27,2</ls>", "<ls>VIKR. 10</ls>", "<ls>VAR\u0100H. B\u1e5aH. S. 11,44</ls>", "{#sakfduktaM na gfhRAti#}", "<ls>Spr. (II) 6655</ls>", "{#sakfduktagfhItArTa#}", "<ls n=\"Spr. (II)\">6654</ls>", "{#sakfcCrutaDara#}", "<ls>KATH\u0100S. 2,61</ls>", "{#sakftsakft#}", "<ls>\u015aAT. BR. 1,8,2,5</ls>", "<ls>\u0100\u015aV. G\u1e5aHY. 4,7,14</ls>", "<ls>M. 5,139</ls>", "<ls n=\"M.\">9,70</ls>", "<ls>Y\u0100J\u00d1. 1,240</ls>", "<ab>v. a.</ab>"]], [["<ls>Spr. (II) 1707</ls>", "{#sakftkftapraRayo 'yaM janaH#}", "<ab>v. a.</ab>", "<ls>\u015a\u0100K. 59,13</ls>", "{#mA \u2014 sakft#}", "<ls>Spr. (II) 2304</ls>"]], [["{#sakfddivA hEvAsmE Bavati#}", "<ls>CH\u0100ND. UP. 3,11,3</ls>", "{#sakfdviBAta#}", "<ls n=\"CH\u0100ND. UP.\">8,4,2</ls>", "<ls>N\u1e5aS. T\u0100P. UP.</ls>", "<ls>Ind. St. 9,165</ls>", "<ls>VED\u0100NTAS. (Allah.) No. 124</ls>", "{#BAnuH sakfdyuktaturaMga eva#}", "<ls>Spr. (II) 4569</ls>", "<ls>M\u0100RK. P. 109,67</ls>", "<ab>Vgl.</ab>", "{#a\u02da#}", "<ls>MBH. 5,7160</ls>", "<ls>VAR\u0100H. B\u1e5aH. S. 28,4</ls>", "<ls n=\"VAR\u0100H. B\u1e5aH. S.\">30,3</ls>", "<ls n=\"VAR\u0100H. B\u1e5aH. S.\">68,74</ls>", "<ls>BH\u0100G. P. 1,5,36</ls>", "<ls>ed. Bomb.</ls>", "{#sakf/t#}", "<div n=\"1\">", "<div n=\"v\">"]], [["<lex>Adj.</lex>", "<ls>AV. 11,1,10</ls>", "{#sayuj#}", "<ls>{{PAIPP.->AV.PAIPP.||20160118|Jim Funderburk.|https://github.com/sanskrit-lexicon/CORRECTIONS/issues/237|inferred}}</ls>", "<div n=\"1\">"], ["<lex>Adv.</lex>", "<div n=\"1\">"], ["<ab>Nom. abstr.</ab>", "{#sakfttva#}", "<lex>n.</lex>", "<ls>Comm. zu NY\u0100YAM. 9,3,13</ls>", "<div n=\"2\">"], ["{#a/hnas#}", "{#sakfdA#}", "<ls>VET. (U.) 204,23</ls>", "<div n=\"2\">"], ["<ab>v. a.</ab>", "<ab>Neg.</ab>", "<div n=\"2\">"], ["<div n=\"2\">"], ["<ls>P\u016br\u1e47abh. 56,12,</ls>", "<div n=\"2\">"]]]}
const BINARY_SPLIT = true
const PRESPLIT = []
// Wall-clock kill gate (H155 follow-up). See FAILURE_MODES_AND_KILL_GATE_2026-07-04.md.
const KILL = true
const KILL_FACTOR = 2.0
const KILL_BASE_MS = 20000
const KILL_SLOPE_MS = 45
const KILL_FLOOR_MS = 45000
const KILL_CEIL_MS = 180000
// H189 live budget kill-switch, split after H442/H462: whole-card translation/binary-split
// and fragment recovery spend independent pools. One runaway recovery cascade can no longer
// consume the capacity required to attempt the remaining primary batches; the recovery pool
// is the sum of the per-card heal ceilings, so those card-level guards are reachable.
const KILL_SWITCH = true
const MAX_AGENTS = 60
const MAX_TRANSLATE_AGENTS = 19
const MAX_HEAL_AGENTS = 41
// H255/H811 low-width staggered dispatch: cap the concurrent translateBatch/healOnly units so
// a degraded generation API isn't hit ~10-wide (the Workflow runtime cap) — a tiny card that
// takes ~54s ALONE is inflated past the 180s kill CEIL under contention. 0 = unbounded.
const MAX_WIDE = 0
const STAGGER_MS = 0
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
const TM_RESOLVED = {}
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
const META = {"schema_version": "pwg_ru.workflow_meta.v1", "generator": "gen_opt_harness2.batched-masked", "generated_at": "2026-07-18T08:52:51Z", "root": "_nominal", "safe_root": "~005fnominal", "lang": "ru", "gen_model": "claude-sonnet-5", "source_profile": null, "source_profiles": {"nakzatra": "pwg_with_supplements", "sarvatra": "pwg_with_supplements", "sakft": "pwg_with_supplements"}, "mode": "nominal_masked", "nominal": true, "nominal_keymap": {"nakzatra": "nakzatra", "sarvatra": "sarvatra", "sakft": "sakft"}, "grammar_layer": "nominal", "selected_keys": ["nakzatra", "sarvatra", "sakft"], "batches": [["nakzatra"], ["sarvatra"], ["sakft"]], "batch_count": 3, "rootmap_sha256": null, "input_hashes": {"nakzatra": {"raw_sha256": "bd26d813ca886314cb87bc51de9791c8e5e752cc7028f4a7508ac250423810ab", "portrait_sha256": "28dd965dd97433b0cca5f11bee1a12d1591d95c8a2b0e2c518e0a2316df262c8"}, "sarvatra": {"raw_sha256": "a06e83bcd891d75db23764ff85c0eafccce42a37826061c5b768d875b36cb351", "portrait_sha256": "813b74eebc4f2c801607ba030d7a8c3a0eaa4ad506c5e57a6b66a6713746a3ed"}, "sakft": {"raw_sha256": "987e730a1a690ba752dbef229c30031d1159a6a30311cd52663229bc8d36d899", "portrait_sha256": "c810c9741a1450b912cb984edf9453754e4a1c8fb555897dbbbafe4e75b9e31e"}}, "input_payload_keys": ["nakzatra", "sakft", "sarvatra"], "selfheal": true, "selfheal_group_budget": 12, "selfheal_cards": {"nakzatra": 8, "sarvatra": 7, "sakft": 6}, "binary_split": true, "output_budget": 90, "sense_presplit_budget": 20, "kill": true, "kill_gate": {"factor": 2.0, "base_ms": 20000, "slope_ms": 45, "floor_ms": 45000, "ceil_ms": 180000}, "kill_switch": true, "agent_budget_strategy": "split-pools-per-card-heal", "max_agents": 60, "max_translate_agents": 19, "max_heal_agents": 41, "translate_agent_expected": 3, "heal_budget_groups": 21, "heal_budget_cards": 3, "max_agents_factor": 3.0, "max_agents_headroom": 10, "max_wide": 0, "stagger_ms": 0, "per_card_heal_budget": true, "per_card_heal_factor": 1.5, "per_card_heal_headroom": 3, "kill_timeout_no_bisect": true, "presplit_group_cite_budget": 60, "presplit_group_sense_cap": 18, "presplit_keys": [], "tm": "translation_memory.ru.json", "tm_auto": true, "tm_available": false, "tm_cards": 0, "tm_hits": [], "frag_tm": null, "frag_tm_cards": [], "frag_tm_fragments": 0, "suggest_tm": null, "suggest_profile": "semantic", "suggest_tm_cards": [], "suggest_tm_top": {}, "degenerate_passthrough_keys": [], "agent_expected_after_tm": 3}

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
// mode (the shared GRAMMAR is injected once before CONV_TR) and in the --no-grammar arm.
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
    if (tok !== want) {
      TNMASK_MISMATCHES++
      TNMASK_DETAIL.push({ key: k, got: tok, want: want })
      if (TNMASK_HARD_REJECT) { noteFail(k, 'tnmask-reject: {Tn} multiset [' + tok + '] != [' + want + ']'); return null }
      log('{Tn} multiset mismatch (soft): ' + k + ' — kept, telemetry only')
    }
  }
  c = restoreCard(c, k)
  // Fidelity guard: restored <ls>/{#..#} counts MUST match the source — a mismatch
  // means misalignment / dropped {Tn}. Reject -> deterministic requeue, never emit garbled.
  const ls = countOf(c, /<ls\b/g), sk = countOf(c, /\{#/g)
  if (ls !== INPUTS[k].ls || sk !== INPUTS[k].sk) {
    noteFail(k, 'fidelity-reject: <ls> ' + ls + '/' + INPUTS[k].ls + ', {# ' + sk + '/' + INPUTS[k].sk)
    return null
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
    noteFail(k, 'translation-fidelity-reject: <ls> ' + lsT + '/' + INPUTS[k].ls + ', {# ' + skT + '/' + INPUTS[k].sk)
    return null
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
    const prompt = PREAMBLE + GRAMMAR + CONV_TR + blocks
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
  const stitched = { key1: k, records: stitchRecords(senses, owners) }
  if (fragProv.length) stitched.frag_prov = fragProv
  if (!missingFragments.length) {
    // fidelity check only meaningful on a COMPLETE heal — a partial result legitimately has
    // fewer citations than the source. Per-fragment token checks already gated each piece;
    // this whole-card count is the belt over those suspenders.
    if (countOf(stitched, /<ls\b/g) !== INPUTS[k].ls || countOf(stitched, /\{#/g) !== INPUTS[k].sk) {
      noteFail(k, 'stitched-fidelity-reject: complete heal, but restored <ls>/{# counts drift from source')
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
    const prompt = PREAMBLE + GRAMMAR + CONV_TR + nws + cur.map(cardBlock).join('')
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
                  null_keys: out.filter(r => !r.card).map(r => r.key),
                  partial_keys: out.filter(r => r.card && r.card.partial).map(r => r.key),
                  failures: _failures }
return { meta: META, summary, results: out }
