-- PWG control-plane campaign database, migration 001 (H3714 Wave 1).
--
-- The database is the mutable system of record. Manifests, results, and
-- receipts stay on disk as immutable evidence addressed by SHA-256; this
-- schema stores identities, hashes, state, bindings, and relative paths only.
-- Secrets, credential-bearing prompts, and profile directories never enter it.

CREATE TABLE IF NOT EXISTS schema_version (
    version     INTEGER PRIMARY KEY,
    applied_at  TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id       TEXT PRIMARY KEY,
    scope             TEXT NOT NULL,
    language          TEXT NOT NULL,
    route             TEXT NOT NULL,
    max_calls         INTEGER NOT NULL CHECK (max_calls >= 0),
    cost_ceiling_usd  REAL NOT NULL CHECK (cost_ceiling_usd >= 0),
    promotable        INTEGER NOT NULL CHECK (promotable IN (0, 1)),
    created_by        TEXT NOT NULL,
    lifecycle_version TEXT NOT NULL,
    fence             TEXT NOT NULL,
    created_at        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id          TEXT PRIMARY KEY,
    campaign_id     TEXT NOT NULL REFERENCES campaigns(campaign_id),
    kind            TEXT NOT NULL CHECK (kind IN ('card', 'fragment')),
    source_identity TEXT NOT NULL,
    source_hash     TEXT NOT NULL,
    state           TEXT NOT NULL,
    parent_job_id   TEXT REFERENCES jobs(job_id),
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    CHECK (parent_job_id IS NULL OR parent_job_id <> job_id),
    UNIQUE (campaign_id, source_identity)
);
CREATE INDEX IF NOT EXISTS jobs_by_state ON jobs(campaign_id, state);

-- Append-only audit of every transactional move (architecture: state model).
CREATE TABLE IF NOT EXISTS job_transitions (
    transition_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id         TEXT NOT NULL REFERENCES jobs(job_id),
    from_state     TEXT NOT NULL,
    to_state       TEXT NOT NULL,
    reason         TEXT,
    evidence_sha   TEXT,
    at             TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS job_transitions_by_job ON job_transitions(job_id);

CREATE TABLE IF NOT EXISTS attempts (
    attempt_id      TEXT PRIMARY KEY,
    job_id          TEXT NOT NULL REFERENCES jobs(job_id),
    adapter         TEXT NOT NULL,
    route           TEXT NOT NULL,
    requested_model TEXT NOT NULL,
    ordinal         INTEGER NOT NULL CHECK (ordinal >= 1),
    outcome         TEXT,
    created_at      TEXT NOT NULL,
    UNIQUE (job_id, ordinal)
);

-- One row per billable provider request. Reserved before I/O; finalized once.
CREATE TABLE IF NOT EXISTS calls (
    call_id            TEXT PRIMARY KEY,
    attempt_id         TEXT NOT NULL REFERENCES attempts(attempt_id),
    route              TEXT NOT NULL,
    requested_model    TEXT NOT NULL,
    served_model       TEXT,
    reservation_id     TEXT NOT NULL UNIQUE,
    idempotency_key    TEXT NOT NULL UNIQUE,
    state              TEXT NOT NULL,
    input_tokens       INTEGER NOT NULL DEFAULT 0 CHECK (input_tokens >= 0),
    output_tokens      INTEGER NOT NULL DEFAULT 0 CHECK (output_tokens >= 0),
    observed_cost_usd  REAL NOT NULL DEFAULT 0 CHECK (observed_cost_usd >= 0),
    cost_evaluable     INTEGER NOT NULL DEFAULT 0 CHECK (cost_evaluable IN (0, 1)),
    request_sha256     TEXT,
    response_sha256    TEXT,
    failure_class      TEXT,
    reserved_at        TEXT NOT NULL,
    finalized_at       TEXT
);
CREATE INDEX IF NOT EXISTS calls_by_attempt ON calls(attempt_id);

-- A provider batch call may cover several jobs; call count is never inferred
-- from returned rows (retired architecture item 2).
CREATE TABLE IF NOT EXISTS call_jobs (
    call_id TEXT NOT NULL REFERENCES calls(call_id),
    job_id  TEXT NOT NULL REFERENCES jobs(job_id),
    PRIMARY KEY (call_id, job_id)
);

CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL REFERENCES campaigns(campaign_id),
    job_id      TEXT REFERENCES jobs(job_id),
    call_id     TEXT REFERENCES calls(call_id),
    kind        TEXT NOT NULL,
    path        TEXT NOT NULL,
    sha256      TEXT NOT NULL,
    media_type  TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    UNIQUE (campaign_id, kind, sha256)
);
CREATE INDEX IF NOT EXISTS artifacts_by_job ON artifacts(job_id);

CREATE TABLE IF NOT EXISTS verdicts (
    verdict_id             TEXT PRIMARY KEY,
    job_id                 TEXT NOT NULL REFERENCES jobs(job_id),
    verdict_class          TEXT NOT NULL,
    result_artifact_sha256 TEXT NOT NULL,
    validator_version      TEXT NOT NULL,
    reasons_json           TEXT NOT NULL,
    created_at             TEXT NOT NULL,
    UNIQUE (job_id, result_artifact_sha256, validator_version)
);

-- Explicit effects. Audit never writes here; ApplyService does (R2.4).
CREATE TABLE IF NOT EXISTS apply_intents (
    intent_id  TEXT PRIMARY KEY,
    verdict_id TEXT NOT NULL REFERENCES verdicts(verdict_id),
    job_id     TEXT NOT NULL REFERENCES jobs(job_id),
    intent     TEXT NOT NULL CHECK (
        intent IN ('requeue', 'quarantine', 'refill', 'promote')),
    payload_sha256 TEXT NOT NULL,
    applied_at TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (verdict_id, intent)
);

CREATE TABLE IF NOT EXISTS promotions (
    promotion_id  TEXT PRIMARY KEY,
    campaign_id   TEXT NOT NULL REFERENCES campaigns(campaign_id),
    phase         TEXT NOT NULL,
    store_path    TEXT NOT NULL,
    before_sha256 TEXT,
    after_sha256  TEXT,
    journal_path  TEXT,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);

-- Import identity = source path + content hash. A repeat is a no-op; a changed
-- payload for the same identity is a refusal (implementation step 6.2).
CREATE TABLE IF NOT EXISTS legacy_imports (
    import_id     TEXT PRIMARY KEY,
    source_kind   TEXT NOT NULL,
    source_path   TEXT NOT NULL,
    content_sha256 TEXT NOT NULL,
    campaign_id   TEXT REFERENCES campaigns(campaign_id),
    row_count     INTEGER NOT NULL DEFAULT 0 CHECK (row_count >= 0),
    imported_at   TEXT NOT NULL,
    UNIQUE (source_path)
);

-- Zero execution and zero promotion authority: comparison rows only (step 6.3).
CREATE TABLE IF NOT EXISTS shadow_observations (
    observation_id TEXT PRIMARY KEY,
    route          TEXT NOT NULL,
    legacy_key     TEXT NOT NULL,
    legacy_value   TEXT,
    pipeline_value TEXT,
    matched        INTEGER NOT NULL CHECK (matched IN (0, 1)),
    explanation    TEXT,
    observed_at    TEXT NOT NULL,
    UNIQUE (route, legacy_key)
);
