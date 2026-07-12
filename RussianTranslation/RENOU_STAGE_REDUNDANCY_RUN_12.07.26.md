## Series A — assembled_cards chain (full check, every row)

- rows (all four stages zipped in lockstep): **120173** — equal lengths
- assembled_cards.jsonl ⊂ assembled_cards.renou.jsonl: adds ['renou_dcs', 'renou_dcs_oldest', 'renou_dcs_texts', 'renou_enriched', 'renou_provenance']; key1 sequence mismatches **0**; modified-field violations **0**
- assembled_cards.renou.jsonl ⊂ assembled_cards.renou.bhs.jsonl: adds ['renou_bhs']; key1 sequence mismatches **0**; modified-field violations **15383** (fields: {'renou_provenance': 9649, 'renou_enriched': 5734}; examples [('a', 'renou_provenance'), ('aMSa', 'renou_provenance'), ('aMSu', 'renou_provenance')])
- assembled_cards.renou.bhs.jsonl ⊂ assembled_cards.renou.bhs.wl.jsonl: adds ['renou_wl']; key1 sequence mismatches **0**; modified-field violations **23** (fields: {'renou_provenance': 23}; examples [('akzoBya', 'renou_provenance'), ('amitABa', 'renou_provenance'), ('DarmaDAtuvAgISvara', 'renou_provenance')])

## Series B — per-dict old underscore chain vs canonical `{code}.renou.jsonl`

### AP
- old chain `ap_renou.jsonl -> ap_renou.bhs.jsonl -> ap_renou.bhs.wl.jsonl`: 90654 rows zipped
  - step ap_renou.jsonl ⊂ ap_renou.bhs.jsonl: adds ['renou_bhs']; key mismatches 0; modified-field violations 6014 (fields: {'renou_provenance': 3650, 'renou_enriched': 2364}; e.g. [('a', 'renou_provenance'), ('a', 'renou_provenance'), ('akaca', 'renou_enriched')])
  - step ap_renou.bhs.jsonl ⊂ ap_renou.bhs.wl.jsonl: adds ['renou_wl']; key mismatches 0; modified-field violations 5 (fields: {'renou_provenance': 5}; e.g. [('akzoBya', 'renou_provenance'), ('amitABa', 'renou_provenance'), ('vajrAkAra', 'renou_provenance')])
- old-final `ap_renou.bhs.wl.jsonl` (90654 rows, 88701 distinct key1) vs canonical `ap.renou.jsonl` (90654 rows, 88701 distinct key1): key1 only-in-old 0 rows / only-in-canonical 0 rows
- sampled signal agreement on common key1 (1-in-25, n=3626): 3459 agree / 167 disagree (fields: {'renou_ls': 41, 'renou_enriched': 136, 'renou_dcs': 130})

### AP90
- old chain: only `ap90_renou.jsonl` (34882 rows)
- old-final `ap90_renou.jsonl` (34882 rows, 34277 distinct key1) vs canonical `ap90.renou.jsonl` (34882 rows, 34277 distinct key1): key1 only-in-old 0 rows / only-in-canonical 0 rows
- sampled signal agreement on common key1 (1-in-25, n=1396): 1285 agree / 111 disagree (fields: {'renou_enriched': 99, 'renou_dcs': 52, 'renou_ls': 7})

### BEN
- old chain: only `ben_renou.jsonl` (17310 rows)
- old-final `ben_renou.jsonl` (17310 rows, 17036 distinct key1) vs canonical `ben.renou.jsonl` (17310 rows, 17036 distinct key1): key1 only-in-old 0 rows / only-in-canonical 0 rows
- sampled signal agreement on common key1 (1-in-25, n=693): 609 agree / 84 disagree (fields: {'renou_enriched': 73, 'renou_dcs': 41, 'renou_ls': 7})

### BHS
- old chain: only `bhs_renou.jsonl` (17839 rows)
- old-final `bhs_renou.jsonl` (17839 rows, 17777 distinct key1) vs canonical `bhs.renou.jsonl` (17839 rows, 17777 distinct key1): key1 only-in-old 0 rows / only-in-canonical 0 rows
- sampled signal agreement on common key1 (1-in-25, n=714): 692 agree / 22 disagree (fields: {'renou_enriched': 22, 'renou_dcs': 21, 'renou_ls': 1})

### MW
- old chain `mw_renou.jsonl -> mw_renou.bhs.jsonl -> mw_renou.bhs.wl.jsonl`: 286560 rows zipped
  - step mw_renou.jsonl ⊂ mw_renou.bhs.jsonl: adds ['renou_bhs']; key mismatches 0; modified-field violations 49188 (fields: {'renou_provenance': 33949, 'renou_enriched': 15239}; e.g. [('a', 'renou_provenance'), ('a', 'renou_provenance'), ('akAra', 'renou_provenance')])
  - step mw_renou.bhs.jsonl ⊂ mw_renou.bhs.wl.jsonl: adds ['renou_wl']; key mismatches 0; modified-field violations 50 (fields: {'renou_provenance': 50}; e.g. [('akzoBya', 'renou_provenance'), ('akzoBya', 'renou_provenance'), ('akzoByA', 'renou_provenance')])
- old-final `mw_renou.bhs.wl.jsonl` (286560 rows, 194084 distinct key1) vs canonical `mw.renou.jsonl` (286560 rows, 194084 distinct key1): key1 only-in-old 0 rows / only-in-canonical 0 rows
- sampled signal agreement on common key1 (1-in-25, n=11396): 8416 agree / 2980 disagree (fields: {'renou_ls': 2596, 'renou_dcs': 545, 'renou_enriched': 1171})

### PW
- old chain: only `pw_renou.jsonl` (170556 rows)
- old-final `pw_renou.jsonl` (170556 rows, 151349 distinct key1) vs canonical `pw.renou.jsonl` (170556 rows, 151349 distinct key1): key1 only-in-old 0 rows / only-in-canonical 0 rows
- sampled signal agreement on common key1 (1-in-25, n=6799): 6012 agree / 787 disagree (fields: {'renou_enriched': 653, 'renou_dcs': 296, 'renou_ls': 237})

### SCH
- old chain: only `sch_renou.jsonl` (29125 rows)
- old-final `sch_renou.jsonl` (29125 rows, 28455 distinct key1) vs canonical `sch.renou.jsonl` (29125 rows, 28455 distinct key1): key1 only-in-old 0 rows / only-in-canonical 0 rows
- sampled signal agreement on common key1 (1-in-25, n=1165): 1040 agree / 125 disagree (fields: {'renou_enriched': 120, 'renou_ls': 8, 'renou_dcs': 48})

### PWG
- old underscore chain: **absent** (canonical `pwg.renou.jsonl` only — already clean)

