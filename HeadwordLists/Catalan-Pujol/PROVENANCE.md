# Provenance note

The files in this folder were first committed in
[`56564a0`](https://github.com/gasyoun/SanskritLexicography/commit/56564a05895f02015c088d8c26d26ef90cbeb596),
whose message — *"feat(article-comparison): sort comparison-table rows
chronologically by edition year"* — describes an **unrelated** change. The
Catalan-Pujol files were swept into that commit by a parallel `git add` running
mid-session; they have nothing to do with the article-comparison work.

The commit message could not be corrected: rewording it requires a force-push,
which `master`'s branch protection rejects. This note records the true
provenance instead.

## What this folder is

The headword spine of the *Diccionari Sànscrit–Català* (Òscar Pujol,
Enciclopèdia Catalana, 2005 — the first Sanskrit→Catalan dictionary) and its
coverage analysis against the Cologne Digital Sanskrit Lexicon (CDSL)
wordlists. The source list is mirrored from the `sanskrit-lexicon/CORRECTIONS`
repo. See [`Sanskrit-Catalan-Wordlist-vs-Cologne.md`](Sanskrit-Catalan-Wordlist-vs-Cologne.md)
for the full report.

| Commit | Date | What it added |
|---|---|---|
| [`56564a0`](https://github.com/gasyoun/SanskritLexicography/commit/56564a05895f02015c088d8c26d26ef90cbeb596) | 2026-06-26 | Source list, report, per-category uncovered-word lists, scripts (message mislabeled — see above) |
| [`75b917d`](https://github.com/gasyoun/SanskritLexicography/commit/75b917d1cc1f954d59eb301a33f41074ec210259) | 2026-06-26 | Made the three analysis scripts repo-portable |
