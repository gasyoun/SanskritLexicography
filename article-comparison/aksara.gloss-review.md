# akṣara — review of the hand-authored RU sense-glosses (draft pass for sign-off)

**What this is.** An agent (Opus 4.8, 2026-06-26) editorial pass over the **55
hand-authored Russian sense-glosses** in [`aksara.pd-min.ru.md`](aksara.pd-min.ru.md),
checked against the English PD sense, the Sanskrit term, and Russian Indological
convention (Kochergina; Elizarenkova for Vedic terms). **No gloss was changed** —
this is a proposal list for a human editor (M.G.) to accept/reject. The skeleton
itself still says _«Перевод глосс — черновой, требует сверки»_; this closes that
loop with concrete, reviewable edits.

**How to sign off.** For each row put a decision in the `✓/✗` column (accept / reject
/ alter). Accepted edits then get applied to `aksara.pd-min.ru.md` col. 3 (and, where the
gloss feeds it, re-run `_build_skeletons_ru.py`). Severity: **H** = factual/category
error, **M** = norm/precision, **L** = optional polish, **FYI** = PD-source defect (no
RU action).

**Headline.** Of 55 glosses the draft is **excellent**, and the flagship finding is
rendered correctly: the syllable ↔ Imperishable/Brahman split (**слог** at 1Ai/F vs.
**Непреходящее, Высшее Существо** at 2A, capitalised, with **обитель Брахмана** at
2Ci) is exactly right. **Zero factual/category errors.** Findings are **2
norm/precision** fixes (sense 7 — the Cyrillic-macron glyph ⟨кӯ⟩ plus a Śrīvidyā
*kūṭa* sense-hint; sense 2Eiii — Mahat as a Sāṃkhya category-term, not a personal
name) and a handful of optional sense-hint add-glosses. One English-source OCR break
(`ex- perience`) was already silently corrected in the RU — noted FYI, no RU change.

---

## A. Substantive proposals

| ✓/✗ | Sense | English (PD) | Current RU | Proposed RU | Sev | Why |
|:--:|:--|:--|:--|:--|:--:|:--|
|  | **7** | three kūṭas beginning with Vāgbhava | три кӯты, начиная с Вагбхавы | три кута (слоговые блоки мантры: Вагбхава-, Камараджа-, Шакти-кута), начиная с Вагбхавы | **M** | Two issues. (a) *Glyph:* the current cell uses a **Cyrillic u-with-macron** (U+04EF) in ⟨кӯ⟩ — not a Kochergina norm and a likely typesetting artefact; carry long *ū* in italic Latin *kūṭa* or render plainly **кута**. (b) *Sense:* in SetuBa. 95. 24 these are the three **kūṭas of the Śrīvidyā/Tripurā Pañcadaśī mantra** (Vāgbhava-, Kāmarāja-, Śakti-kūṭa) — "blocks of syllables", not the ordinary "peak/heap" sense; a one-word hint disambiguates. Accept only if normalising the glyph **and** adding the Śrīvidyā hint. |
|  | **iii** (under 2E) | name of Mahat or Buddhi | имя Махата или Буддхи | (название) Махата (= Махан, Великое начало) или Буддхи | **M** | *Precision.* The Sanskrit (BrahmāṇḍP. iii. 3. 22, *…mahānakṣara eva ca*) names the Sāṃkhya tattva **mahat / mahān** — the cosmic Intellect, a category-term, not a personal name. "Махат" is right, but bare "имя" mislabels it as a proper name; cells 3A–I use "имя/название" for genuine names. A "(Великое начало)" hint marks the *mahat*-tattva. Minor — accept only if tightening the Sāṃkhya register. |

## B. Optional add-glosses (transliteration-only or thin cells that could carry a hint)

| ✓/✗ | Sense | English (PD) | Current RU | Proposed addition | Sev |
|:--:|:--|:--|:--|:--|:--:|
|  | **2B** | puruṣa | пуруша | пуруша (как Непреходящее, *akṣara = puruṣa*) | **L** (parallels 2A/2Cii, which spell out the Imperishable link; TattvSa. *…brahma akṣaraḥ*) |
|  | **iii** (under 2D) | ex-perience of individual soul | опыт индивидуальной души | опыт (блаженства) индивидуальной души | **L** (the fuller PD text reads *experience of the **bliss** of individual soul*, *aiśvaryākṣarayoḥ…*; the bliss nuance is dropped only in the PD-min skeleton) |
|  | **Eii** (under 2E) | illusion, Māyā | иллюзия, майя | иллюзия, майя (авидья, непроявленное *avyākṛta*) | **L** (Sanskrit equates *akṣara* with *avidyā / avyākṛta / māyā*: BrahmSūBh.(Śaṅ.) *akṣaram avyākṛtam…*) |
|  | **15** | a measure of time | мера времени | мера времени (= 1/5 каштхи) | **L** (the Apte value 1/5 Kāṣṭhā is carried in the PD/IAST source: *15 n. a measure of time = 1/5 Kāṣṭhā*) |

## C. FYI — English PD-source defects already corrected in the RU (no RU action)

These are OCR/line-break artifacts in the **English** PD column; the Russian gloss is
already correct. Flag upstream to the PD source if desired; the RU needs nothing.

| Sense | English (PD), as printed | RU (already correct) |
|:--|:--|:--|
| iii (under 2D) | ex**- **perience of individual soul (hyphen-break artifact) | опыт индивидуальной души |

---

## Coverage note

- **55/55 glosses reviewed.** ~53 accepted as-is (clean), **2 substantive proposals**
  (0 H, 2 M), **4 optional add-glosses** (all L), **1 FYI source-typo**.
- **Flagship split verified correct.** слог (1Ai, 1F) vs. Непреходящее/Высшее Существо
  (2A), обитель Брахмана (2Ci), Непреходящее как обитель Пурушоттамы/Вишну (2Cii),
  индивидуальная душа/джива (2Di), освобожденная душа (2Dii) — the
  syllable↔Imperishable/Brahman axis and its theological sub-senses are all rendered to
  Kochergina/Elizarenkova norm. No change proposed on the core split.
- Transliteration of theonyms and technical terms (Пурушоттама, Вишну, Шива, Ганеша,
  Вамана, Харанараяна, Брахма, Кашьяпа, Парвати, Кали, пуруша, пракрити, майя, авидья,
  мокша, джива) is consistent and standard — no changes there. The one glyph exception
  is sense 7 (⟨кӯ⟩, U+04EF), handled in §A.
- This artifact is the **agent-doable half** of the Track B gloss review; final
  scholarly **sign-off** on the two M-level proposals is the human step.
