# BUGHUNT — SanskritLexicography — 19.10.2026

_Created: 19-10-2026 · /bughunt interactive day hunt · executor DeepSeek Flash (`deepseek-flash`) · read-only hunt: no data byte and no source file was changed by this pass_

Measured on `origin/master` **[47ff6a72](https://github.com/gasyoun/SanskritLexicography/commit/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83)** (the tree was in sync with `origin/master`; the hunt ran in an isolated worktree, never the shared main tree). Elapsed: ~35 min of hunt, `write_now()` reproduction included.

This is the **first** `BUGHUNT-FINDINGS` report for this repo (no prior report at the root), and it is the day-mode twin of the 19-10-2026 03:00 night run, which failed operationally — `agent exit=0 but report missing on origin` → rc=3, cursor not advanced — not because the repo was clean.

## Verdict first

**Two real defects: one latent data-integrity trap in the headword-snapshot writer (HIGH), one hole in the UTF-8 gate's text-vs-binary sniff (MEDIUM).**

The trap is the interesting one because every surface in the repo is green: the 222-test offline suite passes, the H6518 writer selftest passes 10/10, and the BOM audit of 17-10-2026 certified the BOM state. They pass *and* contradict each other, because no test ever runs the documented regeneration against the **real** `then-2014/` inputs — the selftest uses a 4-line synthetic fixture that asserts the opposite of what the suite's own pin asserts about the committed file. The first legitimate `python headword_diff.py now` therefore injects `EF BB BF` into a 194,084-line list, silently drops the headword `a` from every BOM-less reader, and turns `tests/test_headword_snapshots.py` red with a message that names neither the cause nor the ruling.

## What verified green (baseline, so a later session does not re-derive it)

| Check | Result |
|---|---|
| `python3 tests/run_offline_suite.py` | **222 passed**, 13.99 s, network disabled, external roots → nonexistent |
| `python3 HeadwordLists/headword_diff_selftest.py` | `SELFTEST GREEN — all H6518 write-contract behaviors verified` (5 tests) |
| `python3 scripts/check_prose_number_drift.py --check` | exit 0, no stale prose number |
| `python3 scripts/eol_census.py --ref origin/master` | `OK — 0 CR bytes across every text-attributed path` (5,343 of 5,400 paths, read as blobs) |
| `python3 tools/epistemic_integrity_check.py --structural-only` | OK — 302 distinct headings, Index parity holds, no duplicate §-numbers |
| `ruff check --select E9,F63,F7,F82,F811` | 0 hits — no undefined names, no broken f-strings |
| `python3 tools/utf8_gate.py` | OK — 5,354 text files decode as UTF-8, 46 binary skipped |

---

## §1 — HIGH · The snapshot writer injects a BOM into `now-2026/MW-unique-key1-…`, drops the headword `a` from BOM-less readers, and reds its own suite pin

**Where.** [HeadwordLists/headword_diff.py:252](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/HeadwordLists/headword_diff.py#L252) — the write-contract line shipped in H6518 ([PR #2416](https://github.com/gasyoun/SanskritLexicography/pull/2416)):

```python
out = os.path.join(NOW2026, out_name)
enc = "utf-8-sig" if _has_bom(then_path) else "utf-8"   # ← the then-2014 sibling, not `out`
with open(out, "w", encoding=enc, newline="\n") as fh:
```

The encoding of the file being **overwritten** is decided by a **different file** — its 2014 ancestor. That is the ratified contract ([BOM audit §4](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/docs/ENCODING_BOM_AUDIT_HEADWORDLISTS_17-10-2026.md), *"the output byte-begins with the then-2014 sibling's BOM where that sibling has one"*), and it is exercised by [headword_diff_selftest.py:157-172](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/HeadwordLists/headword_diff_selftest.py#L157-L172) — `test_bom_preservation` asserts the output **does** carry `EF BB BF`.

**The contradicting fact.** The one pair where the contract bites is committed in the opposite state:

| artifact | bytes | says |
|---|---|---|
| [`then-2014/MW-unique-key1-193978.txt`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/HeadwordLists/then-2014/MW-unique-key1-193978.txt) | `efbbbf…` | BOM **present** (ruled *keep*, MG 17-10-2026) |
| [`now-2026/MW-unique-key1-194084.txt`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/HeadwordLists/now-2026/MW-unique-key1-194084.txt) | `610a61…` | BOM **absent** — written by `ec578b37`, before the contract existed |
| [`tests/test_headword_snapshots.py:150`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/tests/test_headword_snapshots.py#L150) | — | `assert not raw.startswith(b"\xef\xbb\xbf"), "no BOM"` — for **every** `now-2026/` list, MW key1 included |

So the committed data, the shipped contract and the suite pin are three different answers to the same question, and the suite is green only because the contract has never been applied to real data: `now-2026/` was regenerated in June, the contract landed on 18-10-2026.

**Live reproduction (real input, sandboxed output).** `then-2014/` seeded with the **committed** MW key1 file, `now-2026/` seeded with the **committed** MW key1 file, `CSL_ORIG_V02` pointed at a 3-entry fake `mw/mw.txt`, then `headword_diff.write_now()`:

```
committed now-2026 first 3 bytes: 610a61 (len 2050081)
Wrote 1 now-2026/ snapshots:  now-2026/MW-unique-key1-194084.txt [BOM]
after regen first 3 bytes:       efbbbf (len 15)
BOM added? True
first line decoded as plain utf-8: b'\\ufeffa'
repo test pin 'not raw.startswith(BOM)' would now: FAIL
```

The consequence is not cosmetic. The list's first headword is `a`, the commonest Sanskrit headword there is:

```
committed bytes:                      b'a\nafRin\naMS\n'
first headword (plain utf-8):         'a'
after contract regen (plain utf-8):   '\ufeffa'
membership "a" in the list's lines -> False
```

Any consumer that opens these lists with `encoding="utf-8"` (not `utf-8-sig`) silently loses `a`. In-repo readers happen to be BOM-tolerant by luck, not by rule: [tests/conftest.py:207-209](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/tests/conftest.py#L207-L209) and `build_union16.py` read `utf-8-sig`; the sibling crosswalk documents the assumption as *"BOM state read as-is, none present"* ([bhs_dcs_mw_key2_crosswalk.py:18](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/HeadwordLists/bhs_dcs_mw_key2_crosswalk.py#L18)).

**Why no gate caught it.** The nightly/CI surfaces are structurally blind to this:

* `tests/test_headword_snapshots.py` asserts on the **committed** bytes; it never runs the generator.
* `headword_diff_selftest.py` runs the generator on a fixture whose BOM state was chosen to satisfy the contract, not to match `then-2014/`.
* The BOM audit (§3, §4) censused `HeadwordLists/` for BOM **presence** and ruled on the 2014 file; it did not compare a 2014 file's BOM against the BOM of the `now-2026/` file the contract derives from it. Its census therefore reads *6 BOM files*, while the contract's own consequence would make it 7.
* `tools/utf8_gate.py` accepts a UTF-8 BOM by design, so CI stays green even after the injection.

**Fix (needs a one-line ruling first, because the two sides are both "documented").** Minimal, ruling-neutral: consult the file being written, and fall back to the 2014 sibling only when the output is new —

```python
enc = "utf-8-sig" if os.path.exists(out) and _has_bom(out) else "utf-8"
```

That makes `/now-2026/` stable under regeneration (no BOM today ⇒ no BOM tomorrow) and keeps the 2014 file untouched — consistent with the MG ruling *keep* of 17-10-2026, which was about **`then-2014/`**, not about spreading the byte forward. If instead the propagated BOM is the intended end-state, the same PR must (a) commit the BOM'd `now-2026/MW-unique-key1`, (b) flip `test_headword_snapshots.py:150` to a per-file expectation, (c) re-pin the BOM census to 7 and say why. Either way **one** of the three surfaces must move; leaving them as they are guarantees the next regeneration surprises whoever runs it.

## §2 — MEDIUM · The UTF-8 gate treats a BOM-less UTF-16 file as *binary* whenever its text is not Latin — so the gate's own defence does not cover the class it was built for

**Where.** [tools/utf8_gate.py:74-77](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/tools/utf8_gate.py#L74-L77) and [`:47-64`](https://github.com/gasyoun/SanskritLexicography/blob/47ff6a72959b4f2c4aebc5ccf0c0fec44465da83/tools/utf8_gate.py#L47-L64):

```python
if b"\x00" in head:
    if _looks_like_utf16_ascii(head):
        return "error", "UTF-16 without BOM — text must be UTF-8", 0
    return "binary", "NUL byte in the first 8 KiB", 0
```

`_looks_like_utf16_ascii` requires one interleaved plane to be **>80 % NUL** and the other **>90 % printable ASCII**. That holds for UTF-16-encoded *Latin* text only. UTF-16-encoded Russian or Devanagari puts its high byte in a non-zero range (`0x04xx` for Cyrillic), so neither plane is NUL-heavy, the file is classified `binary`, and `run()` counts it in `counts["binary"]` — skipped, never decoded, never failed.

This matters because the gate's stated purpose is content-based detection *"so an unusually named text file cannot slip past the gate"* (docstring L10-12), and the incident that created it was exactly a **Windows PowerShell console capture of Russian text** (docstring L3-6). Windows PowerShell 5.1 redirects to UTF-16LE by default — the most likely way such a capture arrives is the one shape the sniff misses.

**Live reproduction** (identical input bytes, three encodings):

```
cyr utf16 no BOM -> ('binary', 'NUL byte in the first 8 KiB', 0)     ← skipped, gate green
deva utf16 noBOM -> ('binary', 'NUL byte in the first 8 KiB', 0)     ← skipped, gate green
cyr utf16 BOM    -> ('error',  'UTF-16/UTF-32 BOM — text must be UTF-8', 0)   ← caught
```

**Not live today** — and that is the honest limit of this finding: all **46** binary-skipped tracked files were checked by hand and every one is a genuine binary (`.xlsx`, `.gz`, `.db`, `.pdf`, `.jpg`, `.png`), so the gate is not currently letting a bad file through. It is a hole, not a breach.

**Fix.** Decide UTF-16-ness structurally rather than by ASCII density: a NUL in *either* plane with a repeated byte stride of 2 (or 4) over the head, plus a printable ratio computed after decoding the probed plane as UTF-16LE/BE, catches non-Latin text without matching compressed data. Cheaper complement: probe the first 512 bytes at stride 2 and 4 and require one consistent decode; keep the existing binary controls in `--selftest` and add two — `ru_utf16le` and `deva_utf16le` must come back `error`, not `binary`.

---

## Checked and dismissed (recorded so the next hunt does not re-chase them)

| Candidate | Verdict |
|---|---|
| `tools/epistemic_integrity_check.py` (full mode) is **red on master**: `findings_dashboard/data.json` 301 vs 302 FINDINGS headings; §649 missing from both dashboards | **Not a defect — documented cadence.** CI and the pre-commit hook run `--structural-only`; the parity half runs only inside the monthly `findings-dashboard` workflow *after* the builders, and the platform probes run from the residential machine. §649 landed 19-10-2026, the next refresh is the 3rd. Worth knowing: the public `findings/` site is one finding behind until then. |
| 46 tracked files skipped by `utf8_gate` | All genuine binaries (largest: `HeadwordLists/sanhw1.xlsx` 41 MB, `crosswalk_candidates.jsonl.gz` 22 MB, a `.db` fixture, PDFs/JPEGs). No encoding violation hiding there. |
| `ruff` 240 findings | Style residue only: 191 unused imports / 45 `F841` dead assignments (`total_target`, `pads`, `specs`, `screening`) with no behavioural effect on any output. No `E722` (bare `except`), no `B006/B008` (mutable defaults), no `F821` anywhere in 964 files. |
| `check_prose_number_drift.py --check` | Clean; the RU-thousands-separator widening (H5509) and the basename glob fix (H5421) are both in the shipped code and correct. |
| `eol_census.py` at `origin/master` | 0 CR bytes. The blob-based redesign (H2301) is what makes that number trustworthy. |
| `conftest.py` network guard | Patches `socket.socket.connect`, `connect_ex`, `create_connection`, `urlopen`, `urlretrieve` — covers `requests`/`urllib3`/`http.client` by construction. Residual (not demonstrated, not claimed): a test calling `subprocess` could still reach the net. |

## Reusable residue (method, not repo-specific)

**A test that pins the state a generator has never produced is not a regression test — it is a tripwire for the first honest run.** Three green surfaces disagreed here because each was written against a different moment in time: the data (June), the contract (18-10), the pin (08-09). The cheap general check: for every "regenerable" artifact, one test should run the generator against the **real** inputs in a sandbox and byte-compare, not against a fixture that was authored alongside the generator. That is the difference between `headword_diff_selftest.py` (which passes and would bless the injection) and `test_headword_snapshots.py` (which would fail and cannot explain why).

— end of report —
