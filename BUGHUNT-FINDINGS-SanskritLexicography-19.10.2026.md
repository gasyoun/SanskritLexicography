# BUGHUNT — SanskritLexicography — 19.10.2026

_Created: 19-10-2026 · /bughunt interactive day hunt · executor DeepSeek Flash (`deepseek-flash`) · read-only hunt: no data byte and no source file was changed by this pass_

Measured on `origin/master` **[47ff6a72](https://github.com/gasyoun/SanskritLexicography/commit/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83)** in an isolated worktree (never the shared main tree). Elapsed: ~65 min, including two independent scoped audit passes run in parallel with the main one and every reported finding re-run by hand.

This is the **first** `BUGHUNT-FINDINGS` report for this repo, and it is the day-mode twin of the 19-10-2026 03:00 night run, which failed operationally — `agent exit=0 but report missing on origin` → rc=3, cursor not advanced — not because the repo was clean.

## Verdict first

**Fourteen defects: six HIGH, seven MEDIUM, one MEDIUM-LOW.** Eight of them sit in the enforcement layer the repo trusts to stop bad input (§1–§8), and every one of those fails **open** — it reports green/OK/exit 0 while a real violation exists. Six sit in the measurement layer whose numbers humans then quote (§9–§14): a CLI flag documented as "measure the pre-filter baseline" that the canary silently ignores, a published canary table no current invocation reproduces, a control count understated by one siglum, and an acceptance gate that passes a report whose headline number was edited to `99999`.

The enforcement pattern is worth naming because it is not random: **each gate is correct about the artifact it was written for and wrong about the artifact it is pointed at** — staged blob vs working tree (§2), diff header vs content line (§3), tag that resolves vs tag that does not (§4), checkout attributes vs ref attributes (§8), scanned prefix vs full push (§6). The measurement pattern is the same shape one level up: **the number is computed over a population that the invocation does not record.**

**Evidence tiers, stated per finding.** §1–§8 were found in this hunt and re-run by hand here — every reproduction below is the command and output this session observed. §9–§14 come from an independent scoped audit pass run in parallel over the census/measurement scripts; I re-ran **none** of their numbers, and I confirmed §10 and §11 at code level only (the signature and the guard body, both quoted). They are reported with that tier so nobody mistakes them for the same grade of evidence.

## What verified green (baseline, so a later session does not re-derive it)

| Check | Result |
|---|---|
| `python3 tests/run_offline_suite.py` | **222 passed**, 13.99 s, network disabled, external roots → nonexistent |
| `python3 HeadwordLists/headword_diff_selftest.py` | `SELFTEST GREEN` (5 tests, 20 assertions) |
| `python3 scripts/check_prose_number_drift.py --check` | exit 0, no stale prose number |
| `python3 scripts/eol_census.py --ref origin/master` | `OK — 0 CR bytes across every text-attributed path` (5,343 of 5,400 paths) |
| `python3 tools/epistemic_integrity_check.py --structural-only` | OK — 302 distinct headings, Index parity holds, no duplicate §-numbers |
| `ruff check --select E9,F63,F7,F82,F811` | 0 hits in 964 files — no undefined names, no broken f-strings |
| `python3 tools/utf8_gate.py` | OK — 5,354 text files decode as UTF-8, 46 binary skipped |

---

## §1 — HIGH · The snapshot writer injects a BOM into `now-2026/MW-unique-key1-…`, drops the headword `a` from BOM-less readers, and reds its own suite pin

**Where.** [HeadwordLists/headword_diff.py:252](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/HeadwordLists/headword_diff.py#L252) — the write-contract line shipped in H6518 ([PR #2416](https://github.com/gasyoun/SanskritLexicography/pull/2416)):

```python
out = os.path.join(NOW2026, out_name)
enc = "utf-8-sig" if _has_bom(then_path) else "utf-8"   # ← the then-2014 sibling, not `out`
with open(out, "w", encoding=enc, newline="\n") as fh:
```

The encoding of the file being **overwritten** is decided by a **different file** — its 2014 ancestor. That is the ratified contract ([BOM audit §4](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/docs/ENCODING_BOM_AUDIT_HEADWORDLISTS_17-10-2026.md)), and it is exercised by [headword_diff_selftest.py:157-172](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/HeadwordLists/headword_diff_selftest.py#L157-L172) — `test_bom_preservation` asserts the output **does** carry `EF BB BF`.

**The contradicting fact.** The one pair where the contract bites is committed in the opposite state:

| artifact | bytes | says |
|---|---|---|
| [`then-2014/MW-unique-key1-193978.txt`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/HeadwordLists/then-2014/MW-unique-key1-193978.txt) | `efbbbf…` | BOM **present** (ruled *keep*, MG 17-10-2026) |
| [`now-2026/MW-unique-key1-194084.txt`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/HeadwordLists/now-2026/MW-unique-key1-194084.txt) | `610a61…` | BOM **absent** — written by `ec578b37`, before the contract existed |
| [`tests/test_headword_snapshots.py:150`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/tests/test_headword_snapshots.py#L150) | — | `assert not raw.startswith(b"\xef\xbb\xbf"), "no BOM"` — for **every** `now-2026/` list, MW key1 included |

Committed data, shipped contract and suite pin are three different answers to the same question, and the suite is green only because the contract (18-10-2026) post-dates the data (June 2026).

**Live reproduction (real input, sandboxed output).** `then-2014/` seeded with the **committed** MW key1 file, `now-2026/` seeded with the **committed** MW key1 file, `CSL_ORIG_V02` pointed at a 3-entry fake `mw/mw.txt`, then `headword_diff.write_now()`:

```
committed now-2026 first 3 bytes: 610a61 (len 2050081)
Wrote 1 now-2026/ snapshots:  now-2026/MW-unique-key1-194084.txt [BOM]
after regen first 3 bytes:       efbbbf
first line decoded as plain utf-8: b'\\ufeffa'
repo test pin 'not raw.startswith(BOM)' would now: FAIL
```

The consequence is not cosmetic — the list's first headword is `a`, the commonest Sanskrit headword there is:

```
committed bytes:                      b'a\nafRin\naMS\n'
first headword (plain utf-8):         'a'
after contract regen (plain utf-8):   '\ufeffa'
membership "a" in the list's lines -> False
```

Any consumer opening these lists with `encoding="utf-8"` (not `utf-8-sig`) silently loses `a`. In-repo readers are BOM-tolerant by luck, not by rule: [tests/conftest.py:207-209](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/tests/conftest.py#L207-L209) and `build_union16.py` read `utf-8-sig`; the sibling crosswalk documents the assumption as *"BOM state read as-is, none present"* ([bhs_dcs_mw_key2_crosswalk.py:18](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/HeadwordLists/bhs_dcs_mw_key2_crosswalk.py#L18)).

**Why no gate caught it.** `test_headword_snapshots.py` asserts on the **committed** bytes and never runs the generator; the H6518 selftest runs the generator on a fixture authored alongside it; the BOM audit censused BOM **presence** in `HeadwordLists/` and never compared a 2014 file's BOM with the `now-2026/` file derived from it (its census reads *6 BOM files*; the contract's own consequence makes it 7). `tools/utf8_gate.py` accepts a UTF-8 BOM by design, so CI stays green after the injection.

**Fix (needs a one-line ruling first, because both sides are documented).** Minimal, ruling-neutral: consult the file being written, falling back to the 2014 sibling only when the output is new —

```python
enc = "utf-8-sig" if os.path.exists(out) and _has_bom(out) else "utf-8"
```

That makes `now-2026/` stable under regeneration and keeps `then-2014/` untouched, consistent with the MG *keep* ruling of 17-10-2026, which was about the 2014 file. If instead the propagated BOM is the intended end-state, the same PR must commit the BOM'd file, flip `test_headword_snapshots.py:150` to a per-file expectation, and re-pin the BOM census to 7. Either way **one** surface must move.

## §2 — HIGH · `utf8_gate.py --staged` validates the working tree, not the index — the pre-commit gate cannot see the bytes it is committing

**Where.** [tools/utf8_gate.py:110-122](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/tools/utf8_gate.py#L110-L122) lists staged paths with `git diff --cached`, then hands `Path` objects to `check_file()`, which does `path.open("rb")` — the **worktree** file. Both callers use staged mode: [`.githooks/pre-commit:92-93`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/.githooks/pre-commit#L92-L93) and [`.pre-commit-config.yaml:19-23`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/.pre-commit-config.yaml#L19-L23).

**Reproduction** — invalid bytes staged, file then edited to valid (the ordinary "fix the file after `git add`, forget to re-add" path):

```
index blob : 6f6b20ff206261640a        ← invalid UTF-8 (0xff)
worktree   : 6e6f772076616c696420...    ← valid
$ python3 tools/utf8_gate.py --staged
utf8-gate: OK — 1 text files decode as UTF-8 (0 binary skipped, 1 tracked)   rc=0
```

The commit then lands the invalid blob. The mirror case is a **false refusal**: a valid index with an invalid unstaged edit blocks a commit that would have been clean. `--selftest` never exercises `--staged`, which is why both directions stay invisible.

**Fix.** In staged mode decode the staged object (`git show :<path>` or `git cat-file blob :<path>`), and add one positive + one negative `--staged` control to the selftest.

## §3 — HIGH · The stale-base guard misnumbers every removed line after a content line beginning with `--`, so it blames the wrong line and misses a fresh revert

**Where.** [scripts/pre_push_stale_base_check.py:565-566](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/scripts/pre_push_stale_base_check.py#L565-L566) (and the same pattern at `:585` for added lines, `:1542` for `changelog_tag_drift`):

```python
if line.startswith("---") or line.startswith("+++"):
    continue                       # ← skips the CONTENT line too, without advancing old_line
if line.startswith("-"):
    numbers.append(old_line); old_line += 1
```

A removed markdown rule or YAML fence renders as `----`, a removed `--flag` as `---flag`; both match the header test and are dropped **without** advancing the counter. Every later removed line in that file's diff is then off by one, and `blame_map` inspects the wrong line.

**Reproduction** (scratch repo; remote tip `intro/---/old line/tail`, push deletes `---` and `old line`):

```
removed_line_numbers("HEAD~1","HEAD","doc.md") -> [2]
expected (lines at the remote tip this push removes) -> [2, 3]
```

Line 2 is the rule, whose blame is old; line 3 is the line that actually vanished. The guard's own control (same shape without the `---` line) blocks correctly, so the `---` is the discriminator. This is not an exotic input: **249 tracked `.md` files in this repo contain a `---` line** (`FINDINGS.md` alone has 33).

**Fix.** Skip only the header run before the first `@@` hunk; treat every `-`/`+` line after it as content.

## §4 — HIGH · `envelope_check.py` CHK-5 passes when the tag does not exist *and* no commit is recorded (`None == None`)

**Where.** [scripts/envelope_check.py:285-286](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/scripts/envelope_check.py#L285-L286):

```python
tag_commit = git(REPO, "rev-parse", "{}^{{commit}}".format(cr.get("tag", "")))
record("CHK-5-code-revision", tag_commit == cr.get("commit"), ...)
```

`git()` returns `None` on any failure (`:76-80`). CHK-1 only requires `code_revision` to be a non-empty dict, so an envelope may carry a tag and **no** `commit` — and then `None == None` is `True`.

**Reproduction** (a real committed envelope, `data/manifest/envelopes/v1.144.164.envelope.json`, with `code_revision` set to `{"tag": "v-does-not-exist"}`):

```
[pass] CHK-5-code-revision — v-does-not-exist -> None
```

The detail string is the smoking gun: the check prints `-> None` and passes. The control with `commit: "0"*40` gives `[FAIL] … (tag resolves to None)`.

**Fix.** Fail when `tag_commit is None` or `cr.get("commit")` is falsy, before comparing.

## §5 — MEDIUM · The UTF-8 gate calls a BOM-less UTF-16 file *binary* whenever its text is not Latin

**Where.** [tools/utf8_gate.py:74-77](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/tools/utf8_gate.py#L74-L77) with [`:47-64`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/tools/utf8_gate.py#L47-L64). `_looks_like_utf16_ascii` requires one interleaved plane to be **>80 % NUL** and the other **>90 % printable ASCII** — true for UTF-16-encoded Latin only. UTF-16 Cyrillic (`0x04xx`) and Devanagari (`0x09xx`) have no NUL-heavy plane, so the file is classified `binary`, counted in `counts["binary"]`, and skipped.

```
cyr utf16 no BOM -> ('binary', 'NUL byte in the first 8 KiB', 0)     ← skipped, gate green
deva utf16 noBOM -> ('binary', 'NUL byte in the first 8 KiB', 0)     ← skipped, gate green
cyr utf16 BOM    -> ('error',  'UTF-16/UTF-32 BOM — text must be UTF-8', 0)   ← caught
```

This is exactly the class the gate was built for: its docstring cites a **CP1251 PowerShell console capture**, and Windows PowerShell 5.1 redirects to UTF-16LE by default. **Not live today** — all 46 binary-skipped tracked files were hand-checked and are genuine binaries (`.xlsx`, `.gz`, `.db`, `.pdf`, `.jpg`, `.png`), so this is a hole, not a breach.

**Fix.** Decide UTF-16 structurally (NUL in either plane at a consistent stride of 2 or 4, then decode-probe the plane) rather than by ASCII density, and add `ru_utf16le` / `deva_utf16le` negatives to `--selftest`.

## §6 — MEDIUM · A truncated stale-base scan can print **nothing at all** and allow the push

**Where.** [scripts/pre_push_stale_base_check.py:1650](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/scripts/pre_push_stale_base_check.py#L1650) sets `truncated = len(paths) > max_paths`, but the "only the first N changed paths were scanned" NOTE is printed only inside `if n_mod or warned:` ([`:1821-1824`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/scripts/pre_push_stale_base_check.py#L1821-L1824)). The hook calls the checker without `--json`, so a push touching more than `max_paths` files whose scanned prefix is clean produces **zero bytes of output and exit 0** — the docstring's promise (*"the script says so rather than silently sampling"*) does not hold precisely in the silent case.

**Fix.** Print the NOTE whenever `truncated`, and carry it in the JSON `result`, independent of whether anything was found.

## §7 — MEDIUM · `changelog_dupe_evidence_gate.py --repo ./dir` declares a dirty changelog "nothing to check"

**Where.** [scripts/changelog_dupe_evidence_gate.py:89-90](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/scripts/changelog_dupe_evidence_gate.py#L89-L90). Root detection compares `os.path.dirname(os.path.join(args.repo, name))` with `os.path.normpath(args.repo)`; `dirname` keeps the `./` segment, so `--repo ./dup` yields `root=None`, the gate takes the pre-registered *legitimate-empty* branch (`no_changelog_in_repo`), writes a `pass/declared_empty` sidecar and exits 0 — and `gate_evidence.py --require changelog_duplicate_bullets` accepts it.

```
$ ... --repo /tmp/dup   → FAIL (worked) — 1 hit                rc=1
$ ... --repo ./dup      → no changelog found in ./dup — nothing to check   rc=0
```

(Systematic-run-of-3: identical directory, identical content, verdict by path spelling.) CI calls the gate without `--repo`, so this is a trap for any other caller, not a live CI hole.

**Fix.** Compare `normpath(dirname(...))` with `normpath(abspath(args.repo))`, and enter the empty branch only when `find_changelogs()` returned nothing.

## §8 — MEDIUM · `eol_census.py` takes text attributes from the checkout, so a ref that adds `.gitattributes` is censused `OK` while carrying CRs

**Where.** [scripts/eol_census.py:79-103](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/scripts/eol_census.py#L79-L103) resolves attributes with `git check-attr`, which reads the **checkout's** `.gitattributes`, and [`:222-229`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/scripts/eol_census.py#L222-L229) intersects CR candidates with those attribute-derived text paths. A ref that adds `* text=auto eol=lf` at the same time as a CR-carrying blob is therefore censused against the *old* attribute set: `0 text-attributed of 3 paths … OK — 0 CR bytes`, exit 0, while the same ref with its own `.gitattributes` present reports `VIOLATION — 1 path(s) … 3 CR`.

This contradicts the module's central claim (*"never consults the working tree or the index, and it is therefore valid run from any clone, any worktree, or CI"*) and it fails in the one direction that matters — a new file class silently dropping out of the denominator. The `0 text-attributed` state is itself a loud signal the code treats as success.

**Fix.** Read the attribute set from the ref (e.g. `git show <ref>:.gitattributes` into a temp attributes file for `check-attr --source`), and refuse/non-zero when zero paths are text-attributed.

---

# Part B — measurement layer (§9–§14)

_Source: an independent scoped audit pass over `HeadwordLists/works_catalogue/` and `data/`, run in parallel with §1–§8 and not re-run by the author of this part. Evidence quoted is that pass's observed output; where I confirmed the mechanism at code level myself, the line is marked **confirmed here**. Its scratch runs live in `/tmp/audit`; no repo file was written._

## §9 — HIGH · The NCC census population silently depends on an optional workbook, and no artifact records which one produced a number

**Where.** [`census_ncc_mss.py:187-205`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/HeadwordLists/works_catalogue/census_ncc_mss.py#L187-L205) (`build_lexicon`; the workbook branch adds the `Details` keys only when `--vdcs-details` is passed), consumed at `:738`.

The catalogue-siglum lexicon grows from 925 to 1,227 sigla when the workbook is supplied; because a near *next* catalogue match ends the previous catalogue's segment, the **unit count** changes too. Nothing in the TSV, the JSON or the run metadata records which lexicon was used — so two runs of the same command can publish different populations under the same column names.

**Observed.** `--pilot 500`: **1,319** distinct units without the workbook vs **1,477** with it (1,837 / 1,996 with `--no-edition-filter`). `--canary`: Mahābhārata **1,839 vs 2,355**, Rāmāyaṇa 688 vs 819, Bhāgavata 4,005 vs 5,419. The published pilot total is **2,080** (`NCC_MSS_CENSUS_PILOT_CANARY_2026-10-18.md`, `ncc_mss_census_pilot_500.tsv`), while the repo also ships `…_post_filter.tsv` = 1,290 and `ncc_mss_filter_delta_2026-10-18.json` = 1,809 / 1,290. **No invocation of the documented command reproduces 2,080**, and the docstring's claim that *"a run without the workbook behaves identically"* (`:34-36`) is false.

**Fix.** Persist the lexicon mode and sigla count in every artifact; make `--pilot`/`--canary` require the workbook or refuse, instead of measuring a different population silently.

## §10 — HIGH · `--no-edition-filter` is ignored for `--canary` — a documented baseline switch that changes nothing

**Where.** [`census_ncc_mss.py:486`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/HeadwordLists/works_catalogue/census_ncc_mss.py#L486) — **confirmed here**: `def run_canary(rows, cat_re, out_path, vdcs_path=None)` has no `filter_editions` parameter, `:506` hardcodes the default, and `:769-771` calls `run_canary(rows, cat_re, p, args.vdcs_details)`. The flag reaches only `run_pilot` (`:751-752`).

**Observed by the independent pass.** `--canary --no-edition-filter --vdcs-details WB` produces a **byte-identical** TSV to the filtered run (`diff` → identical): a human asking for the pre-filter baseline gets the filtered numbers, with no error and no warning. Meanwhile the published table (`NCC_MSS_CENSUS_PILOT_CANARY_2026-10-18.md:91,92,94`; `ncc_mss_canary_20.tsv`) prints **2,519 / 1,006 / 6,699** (deltas +2,498 / −1,756 / +4,451), current code gives **2,355 / 819 / 5,419** (+2,334 / −1,943 / +3,171), 1,839/688/4,005 without the workbook, and 2,406/863/5,829 even pre-filter+workbook. **No invocation yields the published figures** — and the sibling report `NCC_MSS_UNIT_SEMANTICS_2026-10-19.md` already quotes the *other* set (2,355/819/5,419) for the same works.

Context that keeps this honest: the H7078 changelog entry already records the mechanism as a known limitation for the *next* run (*"`run_canary()` does not parameterise `filter_editions`, so a fresh `--canary` returns smaller figures (Mahābhārata 2,585 → 2,457 with the workbook); the committed numbers were carried"*). What is **not** recorded anywhere is that the flag is silently accepted and ignored — that is a CLI defect, not a caveat.

**Fix.** Thread `filter_editions` through `run_canary` and `main`, then regenerate `ncc_mss_canary_20.tsv` and the report table from one run.

## §11 — MEDIUM · The composition joins `fold(title)` against an index keyed by a different normalisation

**Where.** [`pd_acc_ncc_composition.py:59-65`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/HeadwordLists/works_catalogue/pd_acc_ncc_composition.py#L59-L65) (`fold`), `:79` (`by_key[rec["match_key"]]`), `:85,87`, `:257,263`.

`fold()` deletes every non-`A-Za-z` character; `parse_ncc.match_key` keeps `)`, `,`, `?` and trailing digits, and removes `_`. **4,852 of 152,526** NCC records have `match_key != fold(iast)`, so the exact route can never reach them.

**Observed.** ncc_id `22_9_a_118`, iast `'Yājñavalkyasmṛti)_'` → `match_key` `yajnavalkyasmrti)`, `fold` `yajnavalkyasmrti`; the control siglum `YājñaSm.` (340 occurrences) is counted as a miss. The published control *"NCC exact folded headword 127 / 164, 93,934"* is really **128 / 164, 94,274** (same answer via `fold(iast)` or `fold(match_key)`); the headline exact-NCC layer moves 978 works / 96,835 → 97,150 occurrences (+315, 4 sigla).

**Fix.** Build both indexes (`acc_by_key`, `ncc_by_key`) with `fold(...)`, or fold `match_key` before insertion.

## §12 — MEDIUM · The acceptance gate passes a report whose headline count was falsified

**Where.** [`check_pd_acc_ncc_composition.py:98-101`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/HeadwordLists/works_catalogue/check_pd_acc_ncc_composition.py#L98-L101) — **confirmed here**: guard (e) is `if sum(Counter(r["provenance"]).values()) != len(comp)` — an arithmetic tautology — and guard (d) (`:142-168`) only asserts that each table row's **last cell** carries the literal interim flag. Nothing binds a number printed in the report `.md` to the TSVs it summarises.

**Observed.** With the five inputs copied to a scratch dir and one cell edited — `| composition rows … | 8930 |` → `| 99999 |` — the checker printed `PASS all H6994 composition guards` and exited 0.

**Fix.** Recompute every report table number inside the checker and assert equality (or emit the report and the TSVs from one shared dict).

## §13 — MEDIUM · The canary's "VisualDCS mss" cell can print a hardcoded constant that was never read

**Where.** [`census_ncc_mss.py:567-570`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/HeadwordLists/works_catalogue/census_ncc_mss.py#L567-L570) (`try: out[label] = int(float(...))` / `except ValueError: pass`) with `:510` (`v = vdcs.get(label, fallback)`, constants at `:94-115`); the positional cell parse at `:548-557` ignores `c@r`, which the sibling `ncc_mss_unit_semantics.py:86-93` already fixed.

An unreadable `mss` cell — or a sparse row, which shifts every later column — drops the label **silently**, and `run_canary` then substitutes the hard-coded 21 / 2,762 / 17 / 2,248, labels the cell *"VisualDCS mss"*, and computes a `DIFF` delta from it. Workbook-absent, cell-unreadable and row-misaligned are indistinguishable in the artifact.

**Observed.** An xlsx whose Rāmāyaṇa `mss` cell reads `2,762 mss` → `read_vdcs_canary()` = `{}` → canary row `('Rāmāyaṇa', 1, 3, 3, 2762, -2759, 'DIFF')`.

**Fix.** Raise when a requested label's `mss` is missing or non-numeric; key cells by `c@r`.

## §14 — MEDIUM-LOW · The sampling-frame allocator cannot allocate feasible distributions

**Where.** [`data/definition_typology_pool_sampler.py:119`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/data/definition_typology_pool_sampler.py#L119) (`fixed` = classes below the floor), `:144-153` (overflow), `:154-158` (validation).

(i) A class with `0 < total < min_quota` is placed in `fixed` (docstring: *"take everything it has"*) and then always rejected by `if 0 < class_totals[c] and q < min_quota: raise` — the documented path is dead. (ii) The overflow step dumps the entire overflow on one donor without re-checking that donor's cap.

**Observed.** `allocate_quotas({'synonym':5,'equivalent':100,'encyclopedic':100,'residual':100}, 300)` → `ValueError: floor violated for synonym: 5 < 10`; with `'synonym':10` → `ValueError: quota 102 exceeds class size 100`, although `10/97/97/96` is a valid allocation. Any dictionary carrying a 1–9-entry class aborts the whole seven-dict draw, so the published `300 × 7 = 2,100` frame is only producible on distributions that dodge both paths.

**Fix.** Exempt `fixed` classes from the floor check; spread overflow across all under-cap donors (water-filling) and re-validate.

**Not reported from that pass, recorded as a negative:** the `extract_units` edition filter was probed over the published 500-entry sample (451 `journal_or_series` / 57 `year_like` / 19 `page_ref_prefix` drops) and every sampled drop was a genuine year, printed-book reference or page range — the filter is not a defect. Its real-data composition run also reproduced the committed report exactly (8,930 rows; 8,190 both / 657 direct / 83 composed; ledger 50 = 36 PASS + 14 REJECT; control 122/164, 106,408 occurrences), so §11–§12 are not staleness.

---

## Checked and dismissed (recorded so the next hunt does not re-chase them)

| Candidate | Verdict |
|---|---|
| `tools/epistemic_integrity_check.py` (full mode) **red on master**: dashboards 301 vs 302 FINDINGS headings; §649 missing | **Not a defect — documented cadence.** CI and pre-commit run `--structural-only`; the parity half runs only inside the monthly `findings-dashboard` workflow *after* the builders, and the platform probes run from the residential machine. §649 landed 19-10-2026, the next refresh is the 3rd. Consequence worth knowing: the public `findings/` site is one finding behind until then. |
| 46 tracked files skipped by `utf8_gate` | All genuine binaries (largest: `HeadwordLists/sanhw1.xlsx` 41 MB, `crosswalk_candidates.jsonl.gz` 22 MB, a `.db` fixture, PDFs/JPEGs). No encoding violation hiding there. |
| `ruff` 240 findings | Style residue: 191 unused imports, 45 dead `F841` assignments (`total_target`, `pads`, `specs`, `screening`) with no effect on any output. No `E722` bare `except`, no `B006/B008` mutable defaults, **no `F821`** in 964 files. |
| `check_prose_number_drift.py --check` | Clean; the RU-thousands-separator widening (H5509) and basename-glob fix (H5421) are in the shipped code and correct. |
| `eol_census.py --ref origin/master` | 0 CR bytes at the tip (5,343 text-attributed of 5,400). §8 is about a ref whose attributes differ from the checkout's, not about the current verdict. |
| `conftest.py` network guard | Patches `socket.socket.connect`, `connect_ex`, `create_connection`, `urlopen`, `urlretrieve` — covers `requests`/`urllib3`/`http.client` by construction. Residual, not claimed: a test shelling out could still reach the net. |
| `gate_evidence.py` vacuity logic, `pyfloor.py` floor comparison, `git_ops.py` seam, documented non-fast-forward skip | Read, reproduced nothing — no defect to report. |

## Reusable residue (method, not repo-specific)

1. **A test that pins the state a generator has never produced is a tripwire for the first honest run, not a regression test.** Three green surfaces disagreed here (§1) because each was written against a different moment: the data (June), the contract (18-10), the pin (08-09). The cheap general check: for every "regenerable" artifact, one test should run the generator against the **real** inputs in a sandbox and byte-compare.
2. **Enumerate a gate's failure modes by asking which artifact it opens, not which rule it states.** Seven failures here collapse into one question — *is the thing being read the thing that will be committed / scanned / resolved / censused?* A gate whose `--staged` / `--ref` / `--repo` mode reads a neighbouring artifact (worktree, checkout, spelling of a path) will fail open and its selftest will not notice, because the selftest builds the neighbour and the target to agree.


## Operational note — the guard refused this hunt's own re-write, and was right to

Landing this report hit `STALE_BASE_GUARD_REFUSAL` on the branch that carried its **first draft**: the second commit replaced the draft with the finished text, which the guard read as *"deletes 26 line(s) that landed on origin/… within the last 3 day(s)"* — lines this same session had written ten minutes earlier. That is the H3880 false-positive shape, and it was **not** overridden: the escape hatch is a human's, and "I know those lines are mine" is exactly what the 29-07 and 04-08 authors believed. The sanctioned path was taken instead — the final text landed as **one forward-only commit on a fresh branch off `origin/master`**.

Worth noting, because this report contains two findings against that same guard (§3, §6): the guard's own refusal message was accurate about *what* changed and wrong about *whose* work it was, which is the same "reads the right rule about the wrong artifact" pattern as §1–§8. Its banner already offers the correct remedy (*rebuild on a fresh worktree and re-apply*), so no change is proposed here — only the datum, for whoever tunes the 3-day window.


## Fix ledger — 19-10-2026 (same day, after the report merged)

MG: *«fix»*. Ten of the fourteen findings are closed in this pass; every closure carries the command that proves the refusal fires, and the four open ones are open for a stated reason, not for lack of time.

| § | sev | status | change | proof observed |
|---|---|---|---|---|
| §1 | HIGH | **fixed** | [`headword_diff.py:252`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/headword_diff.py#L252) consults the file being written; selftest re-pinned (output's own BOM preserved, a brand-new output never inherits the 2014 sibling's); `test_bom_never_inherited_from_then_2014` added | reran the original trap with the committed 2014 file: before `efbbbf` + `\ufeffa`, after `610a61` + `a` |
| §2 | HIGH | **fixed** | [`utf8_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/tools/utf8_gate.py): `--staged` decodes `git cat-file blob :<path>`; selftest gained both staged directions | invalid index + valid worktree → `rc=1` naming the file; valid index + invalid worktree → `rc=0` |
| §3 | HIGH | **fixed** | three parsers in [`pre_push_stale_base_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/scripts/pre_push_stale_base_check.py) now skip only the pre-hunk header run | `removed_line_numbers()` → `[2, 3]` (was `[2]`); `added_line_texts()` keeps a `+++`-initial line |
| §4 | HIGH | **fixed** | CHK-5 extracted to `code_revision_verdict()`: dead tag or missing commit now FAIL, with the reason named | `[FAIL] CHK-5 — v-does-not-exist -> None (tag does not resolve…)`; control `[pass] 1.144.6 -> 3f0be6a3ecd3` |
| §5 | MED | **fixed** | structural UTF-16 probe (decode the head; ≥95 % printable) + a 2 % control-density rule | all four non-Latin UTF-16 controls refuse, including the no-NUL Devanagari case; **0 classification changes across 5,402 tracked files** |
| §6 | MED | **fixed** | truncation NOTE printed whenever `truncated`, outside the found/warned branch | code-verified; the silent `--max-paths` path now always speaks |
| §7 | MED | **fixed** | `--repo` normalised to absolute on both sides; a found changelog can never take the empty branch | `--repo ./dup` → `rc=1`, same as the absolute path (was `rc=0` "nothing to check") |
| §8 | MED | **fixed** | attributes resolved with `check-attr --source=<ref>`; a zero-text-denominator census now refuses (`rc=2`) instead of printing OK | CR blob + ref-only `.gitattributes`: `rc=0` → `rc=1`; at `origin/master` the denominator moved 5,343 → 5,345 |
| §9 | HIGH | **partial** | the mode is now named: `lexicon_mode`/`catalogue_sigla`/input sha in a `<output>.meta.json` sidecar, a loud stderr WARNING without the workbook, and the false "behaves identically" docstring corrected | canary run writes `"lexicon_mode": "witness-prefix-only"` + `catalogue_sigla: 925` |
| §10 | HIGH | **fixed** | `filter_editions` threaded through `run_canary`/`main` | canary now differs: Mahābhārata 1,839 vs 1,888, Rāmāyaṇa 688 vs 737 (was byte-identical) |
| §11 | MED | **open** | — | changing the join key moves a published count (978 works / 96,835 → 97,150 occurrences); that needs a regeneration + a human read, not a silent PR |
| §12 | MED | **open** | — | binding every report number to its TSV is only meaningful *after* §11 settles the numbers; the checker's tautology is harmless until then and is documented here |
| §13 | MED | **fixed** | under a supplied workbook an unreadable/absent `mss` cell now refuses instead of substituting the hardcoded constant; the constants survive only for the documented workbook-absent run | `ValueError: … has no readable mss value for 'Rāmāyaṇa' — refusing to substitute` |
| §14 | MED-LOW | **fixed** | the floor exempts classes we take whole; overflow is water-filled across all under-cap donors | `{'synonym':5,…}, 300` → 5/98/99/98 (was `ValueError`); `{'a':3,'b':4,'c':500}, 200` → 3/4/193 |

Repo gates after the pass: **232-test offline suite green** (was 222 — the 10 new pins are one per fixed gate, each holding both the refusal and its legitimate mirror), `utf8_gate --selftest` 16/16, H6518 selftest green, prose-number drift clean, epistemic `--structural-only` OK, `eol_census --ref origin/master` still `0 CR bytes`.

**What the fixes did NOT touch:** no data byte, no published table, no store row. §1 writes nothing today (it only makes the *next* regeneration safe); §10–§13 change what a *future* run produces, and the committed artifacts are unchanged until someone regenerates them deliberately.

— end of report —
