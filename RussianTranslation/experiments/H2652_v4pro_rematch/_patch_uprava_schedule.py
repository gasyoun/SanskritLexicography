#!/usr/bin/env python
"""Land the after-16-Aug off-peak-only schedule on Uprava origin/main (plumbing)."""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

UPRAVA = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..', '..', 'Uprava'))
if not os.path.isdir(os.path.join(UPRAVA, 'tools')):
    UPRAVA = r'C:\Users\user\Documents\GitHub\Uprava'
sys.path.insert(0, os.path.join(UPRAVA, 'tools'))
import handoff_claims  # noqa: E402

NEEDLE = """Peak windows after the switch: **01:00–04:00 and 06:00–10:00 UTC** (Beijing 09:00–12:00 and 14:00–18:00). All other hours = off-peak.
"""
INSERT = """Peak windows after the switch: **01:00–04:00 and 06:00–10:00 UTC** (Beijing 09:00–12:00 and 14:00–18:00; Europe/CEST in August: **03:00–06:00 and 08:00–12:00**). All other hours = off-peak.

**Standing PWG schedule (human, 13-08-2026):** until 16-08-2026 16:00 UTC burn the flat card. After the switch, **never pay peak**. Off-peak only, or defer the job. Off-peak is half of the *new* peak and still above today's flat rates. Enforced in [`deepseek_arm.refuse_if_peak`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/deepseek_arm.py) (escape `ALLOW_DEEPSEEK_PEAK=1` only).
"""


def xform(text):
    if INSERT.strip() in text:
        return text
    if NEEDLE not in text:
        raise ValueError('peak-windows sentence not found')
    text = text.replace(NEEDLE, INSERT, 1)
    text = text.replace(
        '_Created: 13-08-2026 · Last updated: 13-08-2026_',
        '_Created: 13-08-2026 · Last updated: 13-08-2026_',
        1,
    )
    return text


def xform_findings(text):
    mark = 'Peak windows are 01:00–04:00 and 06:00–10:00 UTC.'
    repl = (
        'Peak windows are 01:00–04:00 and 06:00–10:00 UTC '
        '(Europe/CEST in August: 03:00–06:00 and 08:00–12:00). '
        'Standing PWG rule from 13-08-2026: after the switch, run off-peak or defer — never pay peak.'
    )
    if repl in text:
        return text
    if mark not in text:
        raise ValueError('FINDINGS §375 peak-windows sentence not found')
    return text.replace(mark, repl, 1)


ok = handoff_claims.commit_texts_to_origin(
    UPRAVA,
    {
        'docs/DEEPSEEK_V4_PRO_0813_ORG_LANE_MAP_2026-08.md': xform,
        'FINDINGS.md': xform_findings,
    },
    'docs: PWG DeepSeek after 16-08 is off-peak only (never pay peak)',
)
print('landed' if ok else 'NOT_LANDED', ok)
