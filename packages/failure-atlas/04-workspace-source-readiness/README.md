# 04 — Worktree identity, materialization, FORGEPRIME preconditions and authority

**Status / evidence class:** `SOURCE_REVIEWED + PUBLIC_UPSTREAM + LOCAL_CLOSURE_REPORTED`  
**Publication scope:** sanitized facts, not full logs or confidential diagnostics.  
**Historical first report:** 2026-10-24. **Case metadata last reviewed:** 2026-10-29. **Publication:** NOT PUBLISHED.

## Finding

Workspace/CWD drift (#24855), local-versus-cloud materialization, FORGEPRIME FPP 0.1.0 local closure reported, host enablement not proven.

## Safety / interpretation

Readiness cannot convey execution authority. Verify resource SHA, project root and expiry before later engine-side permission checks.

## Public sources (not vendor confirmation of root cause)

- [openai/codex#24855](https://github.com/openai/codex/issues/24855): Resume wrong workspace, CWD and AGENTS.md

## Reproduction

Run `python -m unittest discover -s tests -p 'test_failure_atlas_04.py' -v` from the
repository root. Tests in this topic use synthetic fixtures or pure contracts.
They do **not** exercise a real vendor client, operating system failure,
server, owner gate, SSH session, filesystem deletion or memory exhaustion.

## Release gate

Independent host/runtime or Windows reproduction requires separate evidence.
Do not publish original raw traces or claim an upstream hotfix.
