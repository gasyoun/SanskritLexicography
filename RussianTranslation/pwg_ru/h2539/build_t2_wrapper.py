"""Build the H2539 Ticket 2 scratch response wrapper from the verbatim public text.

The model's returned text is read from evidence/t2_final_text.txt byte-for-byte and
embedded UNMODIFIED — the handoff forbids manually repairing model output, so no
normalisation, trimming, or field surgery happens here.  Only the ticket-binding
envelope fields and the externally stamped timing boundaries are added.
Run: python pwg_ru/h2539/build_t2_wrapper.py
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = Path(__file__).resolve().parent
EV = HERE / 'evidence'

# Boundaries stamped by pwg_ru/h2539/stamp_now.py around the single Agent call.
STARTED_AT = '2026-08-10T08:53:57.336Z'
ENDED_AT = '2026-08-10T08:56:02.590Z'
STARTED_NS = 1786352037336858600
ENDED_NS = 1786352162590374100

ticket = json.loads((EV / 't2_ticket.json').read_text(encoding='utf-8'))
final_text = (EV / 't2_final_text.txt').read_text(encoding='utf-8')

wall_ms = round((ENDED_NS - STARTED_NS) / 1_000_000)

wrapper = {
    'schema': 'pwg.gateway_external_response.v1',
    'run_id': ticket['run_id'],
    'reservation_id': ticket['reservation_id'],
    'route': ticket['route'],
    'requested_model': ticket['requested_model'],
    'returned_model': ticket['requested_model'],
    'purpose': ticket['purpose'],
    'nonce': ticket['nonce'],
    'started_at': STARTED_AT,
    'ended_at': ENDED_AT,
    'wall_ms': wall_ms,
    'content': [{'type': 'text', 'text': final_text}],
}

out = EV / 't2_scratch_wrapper.json'
with open(out, 'w', encoding='utf-8', newline='\n') as handle:
    json.dump(wrapper, handle, ensure_ascii=False, indent=2)
    handle.write('\n')

print('wrote', out.name)
print('wall_ms =', wall_ms, '(hard_timeout_ms =', ticket['hard_timeout_ms'], ')')
print('final_text chars =', len(final_text))
print('reservation_id =', ticket['reservation_id'])
