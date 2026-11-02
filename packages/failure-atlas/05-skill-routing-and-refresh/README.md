# 05 — Implicit skill overtrigger and setup refresh failures

**Status / evidence class:** `PUBLIC_UPSTREAM + USER_REPORTED_TASK_TRACE`  
**Publication scope:** sanitized facts, not full logs or confidential diagnostics.  
**Historical first report:** 2026-10-24. **Case metadata last reviewed:** 2026-10-29. **Publication:** NOT PUBLISHED.

## Finding

Synthetic Alpha frontmatter excludes ROUTE_ALPHA_EXCLUDE; excluded task attempted body read, but setup refresh prevented successful load (#34712).

## Safety / interpretation

Separate metadata, model/tool-attempt, actual body load and internal host selection. Local oracle cannot prove host routing.

## Public sources (not vendor confirmation of root cause)

- [openai/codex#34712](https://github.com/openai/codex/issues/34712): Implicit skill routing ignores negative conditions

## Reproduction

Run `python -m unittest discover -s tests -p 'test_failure_atlas_05.py' -v` from the
repository root. Tests in this topic use synthetic fixtures or pure contracts.
They do **not** exercise a real vendor client, operating system failure,
server, owner gate, SSH session, filesystem deletion or memory exhaustion.

## Release gate

Independent host/runtime or Windows reproduction requires separate evidence.
Do not publish original raw traces or claim an upstream hotfix.
