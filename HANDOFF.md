# HANDOFF — documentation development

Orientation for the next agent (Opus 4.8) continuing **documentation** work in
this repo. Read this together with [CLAUDE.md](CLAUDE.md) (repo conventions),
[.ai_state.md](.ai_state.md) (session journal), and the org-level
[../CLAUDE.md](../CLAUDE.md) (ecosystem, issue taxonomy, `.ai_state.md`
protocol). Released state as of writing: **v1.0.1** (2026-06-14).

## What this repo is (so you document the right thing)

A **data/research workspace**, not a software project — no source code, no build
or tests. CI and pre-commit are lint-only (markdown / YAML / EOF / trailing
whitespace). "Documentation development" here means: directory indexes, naming
conventions, provenance of data files, and keeping cross-references honest.

## Conventions you must follow

- **Clickable links everywhere.** Every path/URL is a Markdown link. Do not put
  repository file paths in bare backticks when a human is expected to click
  them. In chat use working-dir-relative links; in GitHub issue/PR/release
  bodies use full `blob`/`tree` URLs (relative links don't resolve there).
- **Language matches the material.** Russian-content directories get Russian
  indexes (see [Syntax-Lectures/README.md](Syntax-Lectures/README.md),
  [RussianTranslation/mw_ru_prompts/README.md](RussianTranslation/mw_ru_prompts/README.md));
  the root README and CLAUDE.md are English.
- **External refs are plain text, not links.** Files that live in *other* repos
  (the mw_ru working repo; sibling csl-atlas/standards/VisualDCS) must NOT be
  linked — a dead link fails CI link-check. Demote to plain text with a
  "(не входит в этот репозиторий)" / "external repo" note. See
  [mw_ru.md](RussianTranslation/mw_ru.md) section 7 for the pattern.
- **BOM is inconsistent** across `HeadwordLists/` exports — check `head -c 3 file`
  before transforming; preserve the file's existing BOM state. Do not assume the
  org "no BOM" rule.
- **Commits:** `ai-wip:` prefix, one logical change each. **Never** commit binary
  or large data unless asked. Keep markdown lint-clean (no trailing whitespace,
  newline at EOF).
- **Releases:** promote changelog `[Unreleased]` → `[X.Y.Z] - DATE`, annotated
  tag `vX.Y.Z`, then `gh release create` with the version's changelog section as
  notes. `1.0.0` is intentionally untagged; first real tag is `v1.0.1`.

## Verification recipes (run before committing docs)

Resolve every relative Markdown link against its own file's directory:

```sh
git ls-files '*.md' | while read f; do d=$(dirname "$f");
  grep -oE "\]\(([^)]+)\)" "$f" | sed -E 's/.*\]\((.*)\)/\1/' \
  | grep -vE "^https?:|^#|^mailto:" | while read t; do p=${t%%#*};
    [ -e "$d/$p" ] || echo "BROKEN $f -> $t"; done; done
```

Find file references in prose that don't exist in the repo (external/gap check):

```sh
git ls-files '*.md' | xargs grep -ohoE "[A-Za-z0-9_][A-Za-z0-9_./-]*\.(md|py|json|html|txt|xml)" \
  | sort -u  # then classify: external repo / intentional-absence / URL fragment
```

## Open documentation gaps

All five gaps from the original 2026-06-14 documentation pass are now closed:

1. **HeadwordLists index** — done: [HeadwordLists/README.md](HeadwordLists/README.md)
   (naming scheme, key1/key2, variant patterns, BOM caveat, 16-code dictionary
   table). Released in v1.0.2.
2. **Reference-file provenance** — done: [REFERENCES.md](REFERENCES.md) (source,
   date, producer, size per asset). Released in v1.0.2.
3. **Top-level docs map** — done: the "Documentation map" section in
   [README.md](README.md). Released in v1.0.2.
4. **CONTRIBUTING expansion** — done: [CONTRIBUTING.md](CONTRIBUTING.md) now
   spells out the data-change provenance expectation and doc conventions.
   Released in v1.0.2.
5. **kosha import** — **decided: keep external** (user, 2026-06-14).
   `docs/dict/kosha_ai_translation.md` (dev counterpart to `mw_ru.md`) lives in
   the separate mw_ru working repo and is not present on disk here, so it cannot
   be imported without fabrication. It stays external and is documented in
   [RussianTranslation/mw_ru.md](RussianTranslation/mw_ru.md) §7. If the file is
   ever supplied, place it and convert the §7 plain-text reference into a link.

No documentation gaps are currently open. New work should start from a
user-confirmed need, following the loop below.

## How to work

Pull one gap, **confirm scope with the user**, implement, run the link sweep,
`ai-wip:` commit, push, then log it in [.ai_state.md](.ai_state.md) (move to
✅ Completed) and add a changelog `[Unreleased]` entry. The user drives commit
and release timing — do not tag releases unprompted.
