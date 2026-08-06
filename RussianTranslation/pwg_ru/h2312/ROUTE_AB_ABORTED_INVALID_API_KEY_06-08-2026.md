# Rank-2 route A/B — aborted: the metered key is present but invalid (06-08-2026)

_Created: 06-08-2026 · Last updated: 06-08-2026_

**Handoff.** [H2312](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2312-Opus_RussianTranslation_pwg-rank2-route-ab-metered-arm_06.08.26.md)
(**Opus 5**) — rank-2 route A/B: run the metered Messages-API arm against CLI-headless.
Executed by Opus 5 1M (`claude-opus-5[1m]`); paid calls on Sonnet 5 (`claude-sonnet-5`).

**Authorisation.** A human granted the metered spend on 06-08-2026 ("May spend, how many
make sense it is ok"), closing the metered half of the subscription-vs-metered `@DECIDE`.
Planned shape: 8 paid calls, `--keys 2 --repeats 2` over both arms, ~$3–4.

---

## 1. Result: the A/B did not run, and the reason is a bad credential

**All four API-arm calls returned HTTP 401 `invalid x-api-key`.**

| arm | key | n | outcome |
|---|---|--:|---|
| api | nakzatra | 1, 2 | **http_401** `authentication_error` |
| api | sarvatra | 1, 2 | **http_401** `authentication_error` |

`{'type': 'error', 'error': {'type': 'authentication_error', 'message': 'invalid x-api-key'}}`

A 401 bills nothing, so **the API arm cost $0**. No route comparison exists: an arm that
never authenticated cannot be compared to one that ran.

## 2. What the CLI arm did spend

The run was killed during the CLI `sarvatra` legs, so 6 of 8 envelopes landed (4 API 401s
+ 2 CLI). **Real spend: $1.6843** — all of it CLI.

| run | turns | wall_ms | api_ms | create | read | out | envelope $ |
|---|--:|--:|--:|--:|--:|--:|--:|
| `cli_nakzatra_1` | **3** | 471 083 | 404 431 | 108 122 | 69 637 | 42 288 | 1.3040 |
| `cli_nakzatra_2` | **2** | 165 393 | 106 767 | 34 455 | 35 184 | 10 873 | 0.3804 |

Two observations, both consistent with [H2250](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2250/CLI_CACHE_AMORTISATION_REMEASURE_06-08-2026.md)
and neither strong enough to stand alone at n=2:

- **The identical prompt again took a different number of turns** (3 vs 2), and cost moved
  with it (**3.4×**, $1.30 → $0.38). This is the same non-comparability H2250 documented:
  a card envelope sums usage over a variable agentic loop.
- **Call #2 did not fully amortise** — `create` 34 455 against `read` 35 184, not the
  `create = 0` the trivial phase showed. Do **not** read this as contradicting the
  rewritten truth #1: with the turn count differing, the second call is not the same unit
  of work as the first, which is precisely why the trivial arm (`--max-turns 1`) is the one
  that carries that verdict.

## 3. Root cause: `--check` proved presence, not authentication

Before spending, `--check` printed:

```
auth          : ANTHROPIC_API_KEY read from C:\Users\user\.secrets\anthropic.env
```

That line means **a non-empty value was found** — and `api_client()`'s own docstring said
so, in as many words: *"Presence-only auth report"*. It was nonetheless read (in this
session's own reporting to the operator) as *the credential is resolved, nothing technical
is in the way*. It was not: the key is present and **invalid** — expired, revoked, or from
a different account.

**This is the same defect shape the org has now hit three times**: a check that passes for
a reason unrelated to the property under test
([Uprava FINDINGS §320](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md), and
[§324](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)'s gate that priced a
different call than the lane it gated). Here it cost a paid run and a false "ready" report
to a human who was being asked to authorise spend on that basis.

## 4. Fix shipped in this pass

`--check` now **authenticates** instead of merely reporting presence:

```
auth          : ANTHROPIC_API_KEY read from C:\Users\user\.secrets\anthropic.env
auth verified : NO -- HTTP 401, the key is present but INVALID (expired, revoked, or from
                a different account). The API arm cannot run.
```

`verify_auth()` calls `client.models.list(limit=1)` — an authenticated `GET /v1/models`
that bills **no tokens**, so the verification is free and runs on every `--check`. It never
raises and never echoes the credential. `api_client()` deliberately stays presence-only and
now carries a note saying why: `--run` needs a client object even when the credential is
bad, so a 401 is *recorded as a measured `failure_class`* rather than crashing the harness
before it writes an envelope — which is exactly why the four 401 envelopes above exist as
evidence.

The harness docstring's superseded premise (*"a one-shot subprocess cannot amortise its own
system prompt … a 20x spread"*) was also corrected in the same pass: that is v1.127.0
behaviour, overturned by H2250, and it was the stated reason for this A/B's existence.

## 5. What is actually blocked, and on whom

**A valid metered API key.** Nothing else — the prompt split is byte-identical on both
cards, both arms are wired, the spend ruling is granted, and the CLI arm demonstrably runs.

The spend authorisation is **not** consumed: $1.68 of a ~$3–4 budget went to the CLI arm,
and the API arm never billed. Once a working key is in
`C:\Users\user\.secrets\anthropic.env` (or `ANTHROPIC_API_KEY` in the environment), the
same command completes the A/B:

```
python src/pilot/h2158_route_ab.py --check          # must now print `auth verified : yes`
python src/pilot/h2158_route_ab.py --run --keys 2 --repeats 2 --timeout 900 \
    --out ../RussianTranslation/pwg_ru/h2312/raw
```

**Do not re-run `--run` until `--check` prints `auth verified : yes`** — that is the whole
point of the fix above.

---

_Dr. Mārcis Gasūns_
