# 11 — GitHub packaging, IP scope, redaction and publication gates

**Status / evidence class:** `PUBLIC_REPO_METADATA + DOCUMENTED_CONSTRAINT`  
**Publication scope:** sanitized facts, not full logs or confidential diagnostics.  
**Historical first report:** 2026-10-24. **Case metadata last reviewed:** 2026-10-29. **Publication:** NOT PUBLISHED.

## Finding

HotfixKit earlier GitHub repo empty, v0.3 local source candidate; upstream issue reuse; FORGEPRIME working name rights review.

## Safety / interpretation

No automatic push. Explicit owner review, offline test, native Windows CI, licensing and secret scan before GitHub release.

## Public sources (not vendor confirmation of root cause)

- No public Codex issue is asserted for this local error class.

## Reproduction

Run `python -m unittest discover -s tests -p 'test_failure_atlas_11.py' -v` from the
repository root. Tests in this topic use synthetic fixtures or pure contracts.
They do **not** exercise a real vendor client, operating system failure,
server, owner gate, SSH session, filesystem deletion or memory exhaustion.

## Release gate

Independent host/runtime or Windows reproduction requires separate evidence.
Do not publish original raw traces or claim an upstream hotfix.
