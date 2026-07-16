# H1080 PWG→Russian store repair — 17 July 2026

The canonical store was repaired atomically without any model or production-generation call.
The source store was hash-locked before mutation, copied to a hash-addressed backup, and replaced
only after the repair utility proved the expected key/subcard multiset delta.

| Check | Result |
|---|---:|
| Store before | 11,605 rows · `cc1d544ed92d201ca8cbecde0b5e9a8191994dfd1baf20841da82f1f9ae7c805` |
| Placeholder rows repaired | 668 of 670 |
| Null `h` rows repaired | 468 |
| Quarantined | 2 `banD` rows |
| Store after | 11,603 rows · `f15caf7d1f65db0269498c50ecdcd6bf098572a543c12a055ae08c374377b2f9` |
| Residual raw `{Tn}` / null `h` | 0 / 0 |
| Second application | no-op (`already_clean`) |
| RU card TM | 2,476 valid cards · `121d56fc9b6acb52c6bed81587953104a86b5ef83a607bbe8e2bd16d1db7b4ab` |

The 668 recoverable rows were restored only from content-addressed raw inputs or historical
generated-harness placeholder maps bound to the recorded raw-input hash. The two remaining rows
contain indices outside their own maps (`{T196}` with 195 entries and `{T235}` with 234 entries),
so retaining their text would fabricate evidence. Their uncommitted quarantine payload is sealed
by SHA-256 `dad87e89009bf0f3b292d41d6f67bcd225623b0cae184c567ee725d1b4472490`;
the tracked JSON report records each original row hash without publishing the payload.

The backup remains uncommitted and byte-identical to the pre-repair store. The RU card translation
memory was rebuilt exactly once from the clean store and validated. The publication and fragment
TMs were not rebuilt because H1080 changed the canonical card store, not those independent sources.

No fresh c4 health probe, quarantined-key retranslation, promotion, or paid window was run. Those
remain gated on completion of the manifest-v2 and launch-control hardening stage.
