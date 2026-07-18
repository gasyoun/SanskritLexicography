# Reverse Dictionary of Sanskrit — changelog

_Created: 07-07-2026 · Last updated: 18-07-2026_

Tracks version/canonicity decisions and applied-corrections for the reverse-dictionary
dataset, per [`ACL_DH_COMPATIBILITY_ANALYSIS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/ACL_DH_COMPATIBILITY_ANALYSIS.md)
§4 steps 1–2 ([H270](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H270-Sonnet_SanskritLexicography_reverse-dict-publication-prep_07.07.26.md)).
The master `.txt` itself is gitignored (personal-materials-dump folder policy — see
[`README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/README.md)
"Commit scope"); this file is the tracked record of what was declared/verified/changed
against it.

## [Unreleased]

### Fixed — canonical dataset recovered from the fast-forward's untracked-backup — 18-07-2026

**The "data loss" of `266820-reverse-Gasuns.txt` (H733 audit, 11-07-2026) is resolved: the
file was never destroyed.** A Codex fast-forward session on 07-07-2026 09:32, updating the
main clone to an `origin/master` that newly tracked `ReverseDictionary/`, moved the entire
untracked personal-materials dump aside to
`C:\Users\user\Documents\GitHub\ReverseDictionary.untracked-backup.20260707T093250\`
(470 files, 1.7 GB) — announced in that session's own log but recorded in no repo doc, so
the 11-07 audit and every later pass (H1153 included) saw only the clean checkout and
declared the dataset unlocatable. Recovered and verified 18-07-2026 under
[H736](https://github.com/gasyoun/Uprava/blob/main/handoffs/H736-Fable_SanskritLexicography_reverse-dictionary-dataset-recovery_11.07.26.md):
4,135,335 bytes, 266,820 data lines (266,819 CRLF + 1 unterminated final), UTF-8 BOM
intact, SHA-256 `925e696f533d5a9607ea90fb71fae2d2e51d2cc3cb21f332c81cc43e150b9970` —
byte-size-identical to the 06-07-2026 listing in the conversion session's transcript.
Actions taken: canonical `.txt` restored to `ReverseDictionary/.doc.pdf/` (still
gitignored by design); full dump mirrored to
`D:\ReverseDictionary.untracked-backup.20260707T093250\` (robocopy, 470/470 files, hash
re-verified); README "Data location, integrity & backups" section added and the three dead
blob links repointed; [`DATA_REUSE_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/DATA_REUSE_MANUAL.md)
"not in a clone" claim corrected. The `.doc`/`.pdf` milestones (250,026 / 255,882) and
reference corpora (Stiehl 153,593; Kochergina 29,008) are all present in both backup
copies. Off-machine backup remains an open @DO (Yandex WebDAV creds,
[`Uprava/BACKUPS.md`](https://github.com/gasyoun/Uprava/blob/main/BACKUPS.md)); the
distribution-tier @DECIDE (rights ledger options i/ii/iii) is untouched by this recovery.
Recovered by Fable 5 (`claude-fable-5`).

### Added — rights ledger (W1-E) — 17-07-2026

**[`RIGHTS_LEDGER.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/RIGHTS_LEDGER.md)** — every source dictionary sorted into
exactly one of three buckets: **PD** (subtractable) · **in-copyright, marked** (`H`
Edgerton 12,552 + `P` Vettam Mani 1,919 = **14,471 = 5.4%**) · **in-copyright, UNMARKED —
cannot be isolated** (Stchoupak–Nitti–Renou, Turner, Mylius, Kochergina, Pujol — all five
carry declared codes but never appear as a marked source-code in the canonical file). The
**14,471 is stated as a LOWER BOUND**, not a total: because the five silent sources are
unidentifiable in the single-letter-per-line data, a "PD-only" subset **cannot be
certified** on available data. The ledger **builds** the rights position; it does not
**resolve** it — the residue is unresolvable by any agent effort (it needs funded
per-source headword lists + a human ruling). Also flags
[`.doc.pdf/Reverse-Kochergina.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/.doc.pdf/)
(in-copyright, on public `master`) as an **H734-class exposure** — flag only, removal is a
human call — and escalates the still-missing canonical `266820-reverse-Gasuns.txt` as
data loss, naming [H736](https://github.com/gasyoun/Uprava/blob/main/handoffs/H736-Fable_SanskritLexicography_reverse-dictionary-dataset-recovery_11.07.26.md)
as the recovery owner (consumed, not duplicated). No data published, no file moved or
deleted. Built by Opus 4.8 (`claude-opus-4-8[1m]`) under
[H1153](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1153-Opus_SanskritLexicography_revdict-rights-ledger-unresolvable-residue_17.07.26.md).

### Canonical version declared — 07-07-2026

**`.doc.pdf/266820-reverse-Gasuns.txt` is the canonical reverse-dictionary word list.**
Verified directly (not assumed): 266,820 data lines (`SOURCE_LETTER<TAB>IAST-word<CRLF>`,
the final line lacking a trailing CRLF — hence "266,819 lines" in earlier notes, which
counted CRLF-terminated lines only), UTF-8 with a leading BOM (`EF BB BF`), all lines
already NFC-normalized (checked with Python `unicodedata.normalize`), zero exact
duplicate lines, and zero duplicate *words* even when the source-letter column is
ignored — every one of the 266,820 headwords is textually unique.

The following earlier-stage drafts are **superseded** and kept only as historical
snapshots (per-README, already documented as such — this entry makes the declaration
formal and dated):

| Draft | Headword count | Form | Status |
|---|---|---|---|
| `.doc.pdf/reverse-250026-dev.doc` / `.txt` / `.pdf` | 250,026 | Devanagari script, space-delimited (not the `SOURCE<TAB>word` TSV schema) | Superseded |
| `.doc.pdf/reverse-255882.doc` | 255,882 | Not converted (26 MB `.doc`, no plain-text sibling) | Superseded |
| `.doc.pdf/reverse-250026-IAST.pdf` / `reverse-250026-IAST_031213_b3.doc` | 250,026 | IAST transliteration, PDF/Word only | Superseded |
| `.doc.pdf/266820-reverse-Gasuns.txt` | **266,820** | IAST, `SOURCE<TAB>word` TSV | **Canonical** |

**Why the count grew — investigated, not fully determinable cheaply.** The compiler's
own preface (`Обратный словарь санскрита.mdx`) frames the three counts as "different
stages of the compilation," not different editions. A cheap, direct diff of the drafts
against the canonical list was attempted and found **not feasible without a
non-trivial conversion step**:

- The 250,026-word draft's only plain-text form (`reverse-250026-dev.txt`) is in
  **Devanagari script**, space-delimited, not the canonical file's IAST/TSV schema —
  comparing headword sets across the two would require a Devanagari→IAST
  transliteration pass first (a real conversion project, not a cheap check).
- The 255,882-word draft has **no plain-text form at all** — only a 26 MB `.doc`,
  already excluded from this session's doc→mdx conversion pass (see README "What was
  converted this session") as disproportionate to convert.
- The IAST-script variant of the 250,026 draft exists only as PDF/`.doc`, not `.txt`.

**Honest conclusion:** the exact source of growth (new source dictionaries added
between drafts vs. error corrections vs. both) is **not established here** — recorded
as "growth unexplained" rather than guessed, per this task's own instruction. A future
session could resolve this cheaply only after a Devanagari-to-IAST transliteration
pass over `reverse-250026-dev.txt` (out of scope for this pass).

### Outstanding errata — investigated, found already resolved — 07-07-2026

[`Опечатки которые не успели.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%9E%D0%BF%D0%B5%D1%87%D0%B0%D1%82%D0%BA%D0%B8%20%D0%BA%D0%BE%D1%82%D0%BE%D1%80%D1%8B%D0%B5%20%D0%BD%D0%B5%20%D1%83%D1%81%D0%BF%D0%B5%D0%BB%D0%B8.mdx)
is a pdftotext extraction of the source PDF and lost all Cyrillic/Devanagari text and
diacritics (the PDF's embedded fonts have no usable ToUnicode mapping for those glyphs)
— the `.mdx` alone is not reliable enough to drive an automated find/replace against a
266,820-line canonical dataset. The source PDF was instead **rendered to page images**
(`PyMuPDF`/`fitz`, since `pdftoppm` is not installed locally) and read visually — the
table is a clean "стр. (page) / было (was) / заменить на (replace with)" errata table
titled *"Опечатки, которые не успели исправить к лету 2018"* ("Typos we didn't get to
by summer 2018"), i.e. corrections outstanding against a **2018 print-layout draft** of
the full glossed dictionary (page numbers, Russian glosses, grammatical tags, and
front-alphabetized section headers like `ca`/`da`/`pa` — a different, richer artifact
than this folder's bare `SOURCE<TAB>word` reverse-index list).

Of the ~30 rows, most are not applicable to the reverse-index list at all (Russian gloss
wording fixes, added glosses/meanings, Devanagari ligature-only touch-ups with the IAST
spelling unchanged, entry-order swaps, section-header formatting) — the reverse index
carries no glosses, meanings, grammatical tags, or Devanagari. The rows that *do* name a
plain IAST word change were checked directly against the canonical 266,820-line list:

| Page | Was (2018 draft) | Corrected to | In canonical list? |
|---|---|---|---|
| 197 | `sprh` | `sparh` | `sparh` present; `spṛh` (the correctly-formed root, not the draft's truncated `sprh`) is also present as a separate, valid headword — not a duplicate to resolve |
| 314 | `baviṣyati` | `bhaviṣyati` | Wrong form absent; corrected form absent too (this is a conjugated example form in a grammar note, not a headword in this list) |
| 317 | `glāpayati` | `glapayati` | Neither present (conjugated causative-paradigm example, not a headword here) |
| 323 | `mimāṃsat` | `mimāṃsati` | Neither present (conjugated desiderative-paradigm example, not a headword here) |
| 326 | `śiks` | `śikṣ` | Neither present (root-paradigm example, not a headword here) |
| 341 | `kṛṣivala` | `kṛṣīvala` | Wrong form **absent**, corrected form **present** |
| 350 | *(word missing)* | `dviṣ` | Present |
| 355 | *(word missing)* | `parivart` | **Absent** (see note below) |
| 357 | *(word missing)* | `pūjā` | Present |
| 359 | `baliyaṃs` | `balīyaṃs` | Wrong form **absent**, corrected form **present** |
| 364 | `mūrtirmant` | `mūrtimant` | Wrong form **absent**, corrected form **present** |
| 366 | *(word missing)* | `yuyutsu` | Present |
| 372 | *(word missing)* | `vṛddha` | Present (also `vṛddhā`, tagged `M`=MW, present separately — a legitimate distinct headword, not a duplicate) |

**Finding: no correction needed.** For every checkable word-level row, the erroneous
2018-draft form is either absent from the canonical list or the already-correct form is
what's present — i.e. **the canonical 266,820-entry list already reflects this errata
sheet**, compiled/updated after summer 2018 from corrected source material. The one
exception, `parivart` (p355, "add this word after `parimitāhāra`"), is genuinely absent
from the canonical list — but that row is an *addition* (a new headword the compiler
meant to insert into the glossed 2018 dictionary), not a substitution of a wrong
existing headword, and adding a never-before-listed headword to a *reverse index*
(rather than to the full glossed dictionary this errata sheet corrects) is an editorial
call outside this pass's remit — flagged here rather than silently added.

**No changes were applied to the master file this pass** — the investigation confirmed
the current canonical list needs none, which is itself the documented, honest outcome
this step called for.

---

_Dr. Mārcis Gasūns_
