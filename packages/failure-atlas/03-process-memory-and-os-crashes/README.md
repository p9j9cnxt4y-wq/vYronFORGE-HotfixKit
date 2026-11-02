# 03 — Process storms, virtual memory, Windows disk pressure and kernel crashes

**Status / evidence class:** `PUBLIC_UPSTREAM + USER_REPORTED + HISTORICAL_RECORD_SUMMARY`  
**Publication scope:** sanitized facts, not full logs or confidential diagnostics.  
**Historical first report:** 2026-10-24. **Case metadata last reviewed:** 2026-10-29. **Publication:** NOT PUBLISHED.

## Finding

Git-process accumulation, 98% RAM report (#48666), commit memory exhaustion (#38765); C: full and reported BSOD double fault remain distinct.

## Safety / interpretation

Require bounded process/memory/time budgets; all local tests use pure budget arithmetic, no resource stress.

## Public sources (not vendor confirmation of root cause)

- [openai/codex#48666](https://github.com/openai/codex/issues/48666): Git process accumulation and high physical RAM
- [openai/codex#38765](https://github.com/openai/codex/issues/38765): Commit memory exhaustion and crashes

## Reproduction

Run `python -m unittest discover -s tests -p 'test_failure_atlas_03.py' -v` from the
repository root. Tests in this topic use synthetic fixtures or pure contracts.
They do **not** exercise a real vendor client, operating system failure,
server, owner gate, SSH session, filesystem deletion or memory exhaustion.

## Release gate

Independent host/runtime or Windows reproduction requires separate evidence.
Do not publish original raw traces or claim an upstream hotfix.
