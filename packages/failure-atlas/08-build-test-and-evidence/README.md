# 08 — Build cancellation, test completeness, fail-closed status and evidence checks

**Status / evidence class:** `SOURCE_REVIEWED + USER_REPORTED`  
**Publication scope:** sanitized facts, not full logs or confidential diagnostics.  
**Historical first report:** 2026-10-24. **Case metadata last reviewed:** 2026-10-29. **Publication:** NOT PUBLISHED.

## Finding

OwnerBridge no-restore MSB5021 cancellation; partial scanner permission errors; incorrect WARN-as-zero and first-keyword classification risks.

## Safety / interpretation

Insufficient root-cause telemetry stays UNKNOWN; warnings and incomplete scans cannot return PASS.

## Public sources (not vendor confirmation of root cause)

- No public Codex issue is asserted for this local error class.

## Reproduction

Run `python -m unittest discover -s tests -p 'test_failure_atlas_08.py' -v` from the
repository root. Tests in this topic use synthetic fixtures or pure contracts.
They do **not** exercise a real vendor client, operating system failure,
server, owner gate, SSH session, filesystem deletion or memory exhaustion.

## Release gate

Independent host/runtime or Windows reproduction requires separate evidence.
Do not publish original raw traces or claim an upstream hotfix.
