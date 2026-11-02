# 10 — Archive safety, Vault source candidates and source authority

**Status / evidence class:** `USER_REPORTED_INVENTORY + SOURCE_REVIEWED`  
**Publication scope:** sanitized facts, not full logs or confidential diagnostics.  
**Historical first report:** 2026-10-24. **Case metadata last reviewed:** 2026-10-29. **Publication:** NOT PUBLISHED.

## Finding

1,749,996 archive members; 3,123 Vault path hits, zero direct Vault .csproj/.sln binding; metadata/contents not interchangeable.

## Safety / interpretation

Read-only indexing with explicit uncertainty, multi-label paths and status coverage; never delete synthetic fixture destinations.

## Public sources (not vendor confirmation of root cause)

- No public Codex issue is asserted for this local error class.

## Reproduction

Run `python -m unittest discover -s tests -p 'test_failure_atlas_10.py' -v` from the
repository root. Tests in this topic use synthetic fixtures or pure contracts.
They do **not** exercise a real vendor client, operating system failure,
server, owner gate, SSH session, filesystem deletion or memory exhaustion.

## Release gate

Independent host/runtime or Windows reproduction requires separate evidence.
Do not publish original raw traces or claim an upstream hotfix.
