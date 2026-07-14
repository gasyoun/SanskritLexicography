# pwg_ru upstream-change watcher

_Created: 06-07-2026 · Last updated: 06-07-2026_

The pwg_ru source is a **5-layer all-in-one** assembled over **live** upstreams, so a
headword can change *after* we translate it. This watcher answers the three questions
M.G. asked (05-07-2026):

1. **Do we log when each layer was added?** → yes, now:
   [`src/pilot/layer_versions.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/layer_versions.py)
   appends an immutable snapshot of every layer's upstream version to
   [`src/pilot/layer_version_log.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/layer_version_log.jsonl).
2. **Can we watch Cologne monthly (PWG/PW/SCH/PWKVN)?** → yes, cheap:
   [`src/pilot/watch_upstream.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/watch_upstream.py) `cologne`.
3. **Can we watch NWS monthly?** → yes, heavier: `watch_upstream.py nws` (re-fetches only
   the promoted headwords from Halle — polite, resume-safe).

The watcher **only flags** — it never re-translates. Re-runs of the flagged headwords go
through the normal drain discipline
([H179](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H179-Opus_RussianTranslation_pwg_ru_nominal_core_queue_reorder_05.07.26.md) /
[H151](https://github.com/gasyoun/Uprava/blob/main/handoffs/README.md)): branch + PR,
`--no-tm`, ≤3-wide, `--gen-model-version claude-sonnet-5`.

## What each tool does

### `layer_versions.py` — "which upstream version is each layer at?"

```sh
cd RussianTranslation/src/pilot
python layer_versions.py snapshot    # append today's upstream state to the log
python layer_versions.py show        # print the latest snapshot
python layer_versions.py show --all  # every logged snapshot, compact
```

Per csl-orig layer it records the repo HEAD, the **last commit that touched
`v02/<code>/<code>.txt`** (sha + date + subject) and record/headword counts; for NWS it
records the scraped-card count, the net-new (`has_nws_extra`) count and a hash of the
cached key list. This is the *temporal* companion to the watcher: the log says *when*
`pw` last moved under us; the watcher says *what* changed.

### `watch_upstream.py cologne` — monthly git diff (cheap, run first)

```sh
python watch_upstream.py cologne --baseline   # ONE-TIME: seed the per-layer last-seen commit, no diff
python watch_upstream.py cologne              # thereafter: diff last-seen..HEAD per layer
```

For each of PWG/PW/SCH/PWKVN it diffs the committed file between the last-seen commit and
the current csl-orig HEAD (`git show <sha>:v02/<code>/<code>.txt`), parses the changed
`<L>..<LEND>` records into **changed / added / removed headwords** (reusing the
`dict_merge` / `pwg_mask` / `corpus_gate.form_key` parse), and cross-references the
promoted store rows of that layer. csl-orig is **read-only** here — only `git log` / `git
show`.

### `watch_upstream.py nws` — monthly Halle re-fetch (heavier)

```sh
python watch_upstream.py nws                  # read-only diff: re-fetch promoted headwords, don't touch cache
python watch_upstream.py nws --update-cache   # also refresh the gitignored NWS cache when changed
python watch_upstream.py nws --delay 5        # politeness delay between fetches (default 3s)
```

Re-fetches **only the promoted headwords** (~48, not the 168k-card cache), compares the
`nws` / `sch` / `has_nws_extra` fragments to the cached JSON, and flags changes. If Halle
is unreachable it writes a skip note and exits cleanly (log it to
[`Uprava/SERVER_OUTAGES.md`](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md)
and retry) — the Cologne diff is unaffected.

## Outputs (under `src/pilot/upstream_changes/`)

| File | What |
|---|---|
| `_state.json` | per-layer last-seen commit + last NWS run — the incremental anchor |
| `<YYYY-MM>.md` | human report: per-layer changed-headword counts + the stale worklist |
| `<YYYY-MM>.stale.json` | machine worklist consumed by the drain handoffs |

Each stale entry carries the headword's stamped `provenance.input_raw_sha256` (the H170
primitive): the drain regenerates that headword's raw input, re-hashes it, and re-runs the
mismatch. The watcher never mutates the store.

## Scheduling

### Local (primary — csl-orig lives on this machine)

Windows Task Scheduler, monthly, Cologne diff (the NWS re-fetch is run manually or at a
lower cadence because it hits a small academic server):

```powershell
schtasks /Create /TN "pwg_ru-upstream-cologne" /SC MONTHLY /D 1 /ST 07:00 ^
  /TR "cmd /c cd /d C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src\pilot && python watch_upstream.py cologne && python layer_versions.py snapshot"
```

### GitHub Actions (alternative)

[`.github/workflows/upstream-watch.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/upstream-watch.yml)
runs the Cologne diff monthly: it checks out `sanskrit-lexicon/csl-orig` alongside this
repo, points the watcher at it via the `PWG_RU_CSL_ORIG` env var, and opens/updates a
**"monthly upstream drift"** issue with the report. NWS is left to the local run (live
Halle fetch from CI is impolite and flaky).

## Guardrails

- **Never auto-re-translates** — flag + report only.
- Reuses the H170 `input_raw_sha256` / `pipeline_version.py stale` primitive — does not
  reinvent change-detection.
- csl-orig is read-only (git `log` / `show` only; never a commit or push to it).
- The NWS cache (`src/pilot/nws/`) is gitignored; `--update-cache` refreshes it locally but
  nothing there is committed.

_Dr. Mārcis Gasūns_
