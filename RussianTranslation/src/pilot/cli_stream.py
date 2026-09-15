#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cli_stream.py — reading the Claude CLI's token-streaming stdout (H4528).

`claude -p --output-format stream-json --verbose --include-partial-messages` writes one JSON
object per line (NDJSON) WHILE the call runs, ending with a `type: result` line whose object
is byte-for-byte the envelope `--output-format json` prints alone (same key set, same
`structured_output`; measured against CLI 2.1.251, see pwg_ru/h4528/). Three things about
that stream matter to the headless worker, and each is a helper here:

1. LIVENESS. Only CONTENT lines mean the model is producing the answer: `stream_event`
   (token/tool-input deltas), `assistant` / `user` (completed turn messages) and the final
   `result`. `system` lines do NOT — and one of them is the reason this filter exists: while
   the CLI retries a refused request internally it prints `system/api_retry` lines
   (`error_status: 429`, `error: rate_limit`) every few seconds. Counted as progress, that
   chatter would keep a quota-locked spawn looking alive until the 600 000 ms backstop — the
   exact hang FINDINGS §270 describes. Same principle as H2878's "stderr is not progress".
2. CLASSIFICATION TEXT. A killed call's stdout now contains the model's own partial output,
   and a PWG card legitimately contains strings like `429` (a page or verse number) that
   `RATE_RE` would read as an account-level refusal. Classification must see the CLI's own
   lines (system + result) and never the content deltas.
3. THE ENVELOPE. Downstream parsing keeps receiving exactly one envelope object: the `result`
   line. A buffered `json` stdout passes through unchanged.

No model call, no I/O. Pure functions over bytes/str.
"""
import json

#: Line types that carry the model's answer (or its completion). Everything else — today only
#: `system` (`init`, `status`, `api_retry`, ...) — is CLI bookkeeping and not liveness.
CONTENT_LINE_TYPES = frozenset({'stream_event', 'assistant', 'user', 'result'})

#: Line types whose text classification may read. The content types minus `result`'s payload
#: are excluded; `result` stays because on a non-zero exit it is the CLI's own error envelope,
#: exactly what the buffered `json` lane handed `classify_process` before this module existed.
CLASSIFIABLE_LINE_TYPES = frozenset({'system', 'result'})


def _as_text(data):
    if data is None:
        return ''
    if isinstance(data, bytes):
        return data.decode('utf-8', 'replace')
    return data


def _line_type(line):
    """The `type` of one NDJSON line, or None when the line is not a JSON object."""
    line = line.strip()
    if not line.startswith('{'):
        return None
    try:
        obj = json.loads(line)
    except ValueError:
        return None
    if not isinstance(obj, dict):
        return None
    value = obj.get('type')
    return value if isinstance(value, str) else None


def is_progress_line(line):
    """True when one complete stdout line is evidence the model is producing its answer.

    Unparseable / non-JSON lines count as progress. That is the conservative direction for a
    kill decision: output this module does not understand is still output, and the cost of
    misreading it as silence would be killing a call that was working.
    """
    kind = _line_type(_as_text(line))
    if kind is None:
        return bool(_as_text(line).strip())
    return kind in CONTENT_LINE_TYPES


def is_ndjson_stream(stdout):
    """True when stdout is a multi-line NDJSON stream rather than one buffered envelope."""
    text = _as_text(stdout).strip()
    if not text.startswith('{'):
        return False
    try:
        json.loads(text)
        return False                      # one complete document: the buffered `json` shape
    except ValueError:
        return '\n' in text


def result_envelope_text(stdout):
    """The envelope text downstream parsing should see.

    Buffered `json` stdout is returned unchanged. For a stream, the LAST `type: result` line;
    when a stream has none (killed, or the CLI died before finishing) the original text is
    returned so the caller's own parser fails loudly exactly as it would on garbage.
    """
    text = _as_text(stdout)
    if not is_ndjson_stream(text):
        return text
    for line in reversed(text.splitlines()):
        if _line_type(line) == 'result':
            return line.strip()
    return text


def classification_text(stdout):
    """The part of stdout an error classifier may read: CLI lines only, never content deltas.

    Buffered `json` stdout is returned unchanged (it IS the CLI's envelope). For a stream,
    only `system` / `result` lines and non-JSON lines survive.
    """
    text = _as_text(stdout)
    if not is_ndjson_stream(text):
        return text
    kept = []
    for line in text.splitlines():
        kind = _line_type(line)
        if kind is None or kind in CLASSIFIABLE_LINE_TYPES:
            kept.append(line)
    return '\n'.join(kept)


def api_retry_statuses(stdout):
    """HTTP statuses of the CLI's internal retries, in order (`system/api_retry` lines).

    Bounded forensic scalar list — the provider's status codes, never its text. Empty for a
    buffered stdout or a stream with no retries.
    """
    text = _as_text(stdout)
    if not is_ndjson_stream(text):
        return []
    statuses = []
    for line in text.splitlines():
        if '"api_retry"' not in line:
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if obj.get('type') == 'system' and obj.get('subtype') == 'api_retry':
            status = obj.get('error_status')
            statuses.append(status if isinstance(status, int) else None)
    return statuses


def selftest():
    init = '{"type":"system","subtype":"init","session_id":"s"}'
    retry = '{"type":"system","subtype":"api_retry","attempt":1,"error_status":429,"error":"rate_limit"}'
    delta = ('{"type":"stream_event","event":{"type":"content_block_delta","delta":'
             '{"type":"input_json_delta","partial_json":"Rv. 1, 429"}}}')
    result = '{"type":"result","subtype":"success","is_error":false,"structured_output":{"cards":[]}}'
    stream = '\n'.join([init, retry, delta, result]) + '\n'
    assert not is_progress_line(init) and not is_progress_line(retry.encode())
    assert is_progress_line(delta) and is_progress_line(result) and is_progress_line('garbage')
    assert not is_progress_line('   ')
    assert is_ndjson_stream(stream) and not is_ndjson_stream(result)
    assert json.loads(result_envelope_text(stream))['subtype'] == 'success'
    assert result_envelope_text(result) == result
    cls = classification_text(stream)
    assert 'api_retry' in cls and 'partial_json' not in cls and '"result"' in cls, cls
    assert api_retry_statuses(stream) == [429] and api_retry_statuses(result) == []
    assert result_envelope_text(init + '\n' + delta + '\n') == init + '\n' + delta + '\n'
    print('cli_stream selftest: PASS')
    return 0


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(selftest())
