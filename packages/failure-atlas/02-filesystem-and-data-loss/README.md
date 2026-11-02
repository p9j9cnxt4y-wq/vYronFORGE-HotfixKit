# 02 — Destructive file operations and volume boundaries

**Status / evidence class:** `PUBLIC_UPSTREAM + HISTORICAL_USER_REPORTED`  
**Publication scope:** sanitized facts, not full logs or confidential diagnostics.  
**Historical first report:** 2026-10-24. **Case metadata last reviewed:** 2026-10-29. **Publication:** NOT PUBLISHED.

## Finding

April E: data-loss account; earlier Proxmox service disruption; comparable public workspace deletion (#43343, #55161).

## Safety / interpretation

Reject ambiguous paths, traversal, reparse crossings and all delete operations in this reference kit; do not reenact losses.

## Public sources (not vendor confirmation of root cause)

- [openai/codex#43343](https://github.com/openai/codex/issues/43343): Destructive cleanup escaped Windows workspace
- [openai/codex#55161](https://github.com/openai/codex/issues/55161): Data loss from empty-path expansion with venv --clear

## Reproduction

Run `python -m unittest discover -s tests -p 'test_failure_atlas_02.py' -v` from the
repository root. Tests in this topic use synthetic fixtures or pure contracts.
They do **not** exercise a real vendor client, operating system failure,
server, owner gate, SSH session, filesystem deletion or memory exhaustion.

## Release gate

Independent host/runtime or Windows reproduction requires separate evidence.
Do not publish original raw traces or claim an upstream hotfix.
