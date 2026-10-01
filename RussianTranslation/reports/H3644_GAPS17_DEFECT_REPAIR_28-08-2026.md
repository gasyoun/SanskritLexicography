# H3644 — GAPS §17 surface-form gates + `defect-repair` claim kind

_Created: 28-08-2026 · Last updated: 28-08-2026_

Grok 4.6 (`grok-4.6`). Handoff: [H3644 (Grok 4.6, 🟡2 medium) — pwg_ru GAPS §17 gates plus three hard-flagged rows](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3644-Grok_SanskritLexicography_pwg-ru-gaps17-defect-repair_28.08.26.md).

Zero paid Claude Max / API calls. Store not merged. `pwg-ru-data/tm/` not refreshed (hash did not move).

## 1. `pwg.tm.gate.v1` now fails GAPS §17

Two hard flags in [`src/pwg_tm_gates.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_gates.py):

- `GLOSS-DE-RESIDUE` — a `{%…%}` span whose inner text still has German letters, German function words, or Latin with no Cyrillic.
- `AB-MUTATED` — `<ab>…</ab>` tokens in the target are not positional-byte-identical to the source.

Canaries from the 27-08 sidecar ([`PWG_TM_W1_SERIOUS10_TAXONOMY_REPAIR_27-08-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_TM_W1_SERIOUS10_TAXONOMY_REPAIR_27-08-2026.md)):

| Headword | Predicate | Source | Target |
|---|---|---|---|
| `upakrama` | `GLOSS-DE-RESIDUE` | `{%Antritt, Anfang, Beginn%}` | identical German |
| `AtmasAt` | `GLOSS-DE-RESIDUE` | `{%an sich, zu sich, auf sich%}` | identical German (plus `{%thun%}` → `{%класть%}`) |
| `taruRa` | `AB-MUTATED` | `<ab>v. a.</ab>` | `<ab>т. е.</ab>` |

Prove:

```
python src/pwg_tm_gates.py --selftest
python src/pwg_tm_gates.py --scan release/pwg_tm_canonical/wave1_b_receipt/sample400.jsonl
```

`--selftest` PASS. `--scan` on the frozen H2684 n=400 sample:

```
rows=400 GLOSS-DE-RESIDUE=6 AB-MUTATED=81
gloss_keys: AtmasAt, aTa, sTA, upakrama, yad, yuj
```

`taruRa` is in the 81. Extra gloss hits are mixed fragments that left a German function-word span standing (`yad`: `{%wie%}` → `{%как%}` but `{%so%}` copied). Extra AB hits are dominated by `recurring_formula` expansions (`etad`: `<ab>demin.</ab>` → `<ab>уменьш.</ab>`), which the house copy-through convention now refuses at promotion time.

`audit_store_gates.py` prints a GAPS §17 surface census over store rows; that census does **not** change its SAN-LOSS exit code.

## 2. `coordinator.py claim --kind defect-repair`

Named kind. `--keys` + `--root` required. `prepare` stamps `--no-tm` on `gen_opt_harness2.py`. Do not improvise `gen_opt_harness2 --keys` without a lease.

```
python src/pilot/coordinator.py claim --help
```

`--kind {verb,nominal,rootmap,defect-repair}` with help text: `defect-repair: already-promoted root + --keys; prepare stamps --no-tm`.

Round-trip (temp `--data-root`, no live lease):

```
claim --kind defect-repair --lane pc --owner h3644-test --root dA --keys d_a~~h0_02_sec_2,d_a~~h0_05_anu
```

emits `kind=defect-repair`, `details.no_tm=true`, `reserved_keys` set.

## 3. `mA` / `pat` / `asvatantra` — parked, not `--no-tm`

They do **not** match the `dA` class that H3593 repaired.

| key1 | subcard | H3590 flag | severity | vs `dA` |
|---|---|---|---|---|
| `mA` | `m_a~~h0_zz_pw03` | SAN-LOSS 7/9 | **minor** | lost `√mI` variant on the root head |
| `pat` | `pat~~h0_zz_pw00` | SAN-LOSS 0/2 | **minor** | lost present stem `{#pa/tati#}` + epic-middle note |
| `asvatantra` | `asvatantra~~h0_zz_pw` | SAN-LOSS 1/3 | **minor** | lost fem. ending `(f. {#A#})` |

`dA` was **medium**: dropped the whole desiderative / preverb head-line plus citations (LS-LOSS 29/34 and SAN-LOSS 4/6). H3590's own fix path: requeue the two medium rows `--no-tm`; "the three minor rows are a G5 reviewer's call." H3654 confirmed the three SAN-LOSS rows still sit in the store after later promotions.

Fence: no paid Max window. `--no-tm` requeue is a paid headless window (H3593 spent 173 s / 1 call on `dA`). Parked.

Store backup: not taken — no merge.

## 4. Tests

`pytest tests/test_h3644_gaps17.py tests/test_pwg_tm_generate.py -q` → 25 passed.

_Dr. Mārcis Gasūns_
