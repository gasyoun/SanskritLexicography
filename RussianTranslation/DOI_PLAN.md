# DOI Plan

The immutable edition cut is prepared locally under `release/edition_vN/`.

Before DOI registration:

1. Validate the assembled export, interoperable exports, review status, gold labels, and release manifest.
2. Upload the exact `release/edition_vN/` directory to the archival repository.
3. Register the DOI against that immutable directory and update `CITATION.cff` with the DOI and final version.
4. Keep the generated `release_manifest.json` with SHA256 checksums as the audit record.
