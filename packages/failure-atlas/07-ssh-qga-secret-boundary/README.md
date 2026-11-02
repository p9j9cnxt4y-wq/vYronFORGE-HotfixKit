# 07 — Remote transport contracts, structured systemd discovery and secret-safe results

**Status / evidence class:** `USER_REPORTED_RUN + SYNTHETIC_REPRO`  
**Publication scope:** sanitized facts, not full logs or confidential diagnostics.  
**Historical first report:** 2026-10-24. **Case metadata last reviewed:** 2026-10-29. **Publication:** NOT PUBLISHED.

## Finding

Generated SSH/QGA controller CRLF, tab and missing entrypoint; later SYSTEMD_UNIT_LIST -> SECRET_BOUNDARY_STOP; actual VM status unproven.

## Safety / interpretation

Strict allowlisted structured metadata, per-run HMAC correlation, explicit coverage, no SSH/VM access or secrets.

## Public sources (not vendor confirmation of root cause)

- No public Codex issue is asserted for this local error class.

## Reproduction

Run `python -m unittest discover -s tests -p 'test_failure_atlas_07.py' -v` from the
repository root. Tests in this topic use synthetic fixtures or pure contracts.
They do **not** exercise a real vendor client, operating system failure,
server, owner gate, SSH session, filesystem deletion or memory exhaustion.

## Release gate

Independent host/runtime or Windows reproduction requires separate evidence.
Do not publish original raw traces or claim an upstream hotfix.
