# NWS section-audit — handoff runbook

Paste the block below into each new chat, changing only the section letter on
the first line. Run one letter first; then spin up the rest as separate streams
(one chat per letter). Input generation is independent per letter, so parallel
runs are safe — the only shared files are `CHANGELOG.md` and
`NWS_AUDIT_REPORT.md`.

**Done so far:** a (original dev pilot), b, c, d, e, f, g, h, i, j, k, l.
**Remaining:** m, n, and the rest of the SLP1 key universe (incl. long-vowel /
capital SLP1 sections such as `A`, `I`, `U`, … if present in the manifest).
Note `f` = SLP1 ṛ; pick the SLP1 letter, not the IAST one.

---

Audit the **m-section** of the NWS attribution parser. (Change "m" to your
assigned letter.)

Repo: C:\Users\user\Documents\GitHub\SanskritLexicography  (work in RussianTranslation/src)
Branch: master. Pull first.

ONE command does everything (builds the manifest if missing, generates merged
inputs resumably, runs the deterministic split-preview audit):

    cd RussianTranslation/src
    python nws_audit_section.py m

Read the SUMMARY line. Interpret:
- **bleeds**: expect 0, occasionally a few (`Hillebrandt 1885 : IV` on `gam`,
  `kar`, …). A roman-cite bleed leaves the owner correct but contaminates the
  injected owner map; the `nws_owner_map` debleed cleans freshly-generated maps.
  Verify "owner-map residual contamination: 0". Bleeds are NOT a code bug.
- **real no-owner** bucketed by class. Meister `(2.1)`, Böhtlingk `*NNN`, roman
  page, and page-less x-ref are KNOWN LIMITATIONS — expected, NOT bugs, need NO
  code change. Each was tried in nws_split and reverted (admitting the token
  destabilises segment/owner alignment). Do not "fix" them.
- **OTHER**: any line printed as "?? OTHER" is unclassified — inspect the raw
  fragment. The function takes the fragment TEXT, not the key:
      python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); import nws_split; f=nws_split.nws_fragment('<KEY>'); print(repr(f)); print(nws_split.split(f))"
  Decide: (a) a KNOWN class mislabelled → treat as benign; (b) a **source-data
  typo** in NWS (e.g. an unbalanced paren — compare against sibling entries with
  the same owner; if the siblings parse, it's bad input, NOT a parser gap → add
  a row to the errata, no code change); or (c) a genuinely NEW gap class — the
  ONLY thing that warrants discussion before any coding.
- **cross-check** must read "OK". "MISMATCH" → stop and report.

Then record the result in BOTH living files:

1. **RussianTranslation/CHANGELOG.md** — append ONE bullet to the "### Audited"
   list under "## 2026-06-23", mirroring the a–l bullets (keys → NWS-bearing,
   entries, bleeds, no-owner = benign + real with class, real-loss %, owner-map
   cross-check).
2. **RussianTranslation/NWS_AUDIT_REPORT.md** — add ONE row to the cumulative
   roll-up table, then re-total the Σ row (keys, NWS-bearing, entries, bleeds,
   benign, real, and real % = real ÷ entries). Update the real-loss taxonomy
   counts. If a source-data typo was found, add a row to the "NWS source-data
   errata" table.

Lint both: no trailing whitespace, newline at EOF, valid markdown. Commit + push:

    git add RussianTranslation/CHANGELOG.md RussianTranslation/NWS_AUDIT_REPORT.md
    git commit -m "docs(changelog): <letter>-section audit result"
    (end the commit body with: Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>)
    git push   # if push fails with a schannel/TLS error, just retry — it's transient

PARALLEL-STREAM HYGIENE (several letters at once):
- Input generation is independent per letter (distinct keys/files), so parallel
  generation is safe.
- The shared files are CHANGELOG.md and NWS_AUDIT_REPORT.md. If your push is
  rejected (another stream pushed first), run `git pull --rebase` then push
  again. The changelog bullet rebases cleanly; for the report, re-check that the
  Σ totals still include every row after the rebase (two streams both editing
  the Σ line can conflict — if so, re-sum from the table).
- Do NOT commit anything under pilot/input, pilot/output, or pilot/nws — it's
  gitignored corpus data. Only the two docs (and code, if a TRUE new bug is
  found and confirmed) get committed.
