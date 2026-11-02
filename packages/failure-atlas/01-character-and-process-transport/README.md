# 01 — Byte integrity, escaping, subprocess and guest entrypoints

**Status / evidence class:** `PUBLIC_UPSTREAM + USER_REPORTED + SYNTHETIC_REPRO`  
**Publication scope:** sanitized facts, not full logs or confidential diagnostics.  
**Historical first report:** 2026-10-24. **Case metadata last reviewed:** 2026-10-29. **Publication:** NOT PUBLISHED.

## Finding

Windows composer escaping (#41486, #46037); text-mode LF/CRLF; literal tab; Python main() not invoked.

## Safety / interpretation

Preserve byte-identical input/output and require structured completion; never infer a vendor binary fix from synthetic tests.

## Public sources (not vendor confirmation of root cause)

- [openai/codex#41486](https://github.com/openai/codex/issues/41486): Codex desktop path text mutated before model delivery
- [openai/codex#46037](https://github.com/openai/codex/issues/46037): Windows Copy as path escapes underscores

## Reproduction

Run `python -m unittest discover -s tests -p 'test_failure_atlas_01.py' -v` from the
repository root. Tests in this topic use synthetic fixtures or pure contracts.
They do **not** exercise a real vendor client, operating system failure,
server, owner gate, SSH session, filesystem deletion or memory exhaustion.

## Release gate

Independent host/runtime or Windows reproduction requires separate evidence.
Do not publish original raw traces or claim an upstream hotfix.
