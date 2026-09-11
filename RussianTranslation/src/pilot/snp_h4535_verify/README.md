# H4535 verifier artifacts — SNP keyed-vs-csl-orig parity (data class)

Independent verification pass for [H4535](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H4535-OxAlpha_SanskritLexicography_snp-keyed-upgrade-cslorig_11.09.26.md),
run 11-09-2026 by a headless OxAlpha/GLM window (`zai-coding-plan/glm-5.3-flash`) — a different
model than the executor, pairing per MG ruling 11-09-2026 (mirror clause).

- `scan_yadisk.py <snp.txt>` — parse the 453 `<H1>` entries (L / pc / key2 / body), tag balance.
- `scan_cslorig.py <snp.txt>` — parse the 453 meta-line entries (L / pc / k1 / k2), structure census.
- `join.py` — join both record sets by L (consumes the two JSONs; 0 pc/headword mismatches expected).
- `folddiff.py` — markup-strip + NFKD fold diff (450/453; diffs L2, L176, L440 — all csl-orig-favouring).
- `containment.py` — difflib containment over all 453 pairs (zero yadisk readings missing from csl-orig).

Sources: yadisk `1974-SNP/snp.txt` re-fetched via
`rclone copy yadisk:Sanskrityatina/05_Sanskrit-Lexicon/1974-SNP`; csl-orig `v02/snp/snp.txt`
read from `origin/main`. **Result: PASS** — 450/453 after folding, three diffs (L2 typo fix,
L176 Greek ὀνυξ restoration, L440 relocated end-matter), zero lost readings.
`VERIFIER_SECTION.md` is the verdict verbatim, as appended to the handoff.
Parity doc: [YADISK_SNP_KEYED_VS_CSLORIG_PARITY_11-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/main/YADISK_SNP_KEYED_VS_CSLORIG_PARITY_11-09-2026.md).
