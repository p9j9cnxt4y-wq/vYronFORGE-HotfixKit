# 06 — App consent, cursor, input desktop and screenshot capture

**Status / evidence class:** `PUBLIC_UPSTREAM + USER_REPORTED_RUN`  
**Publication scope:** sanitized facts, not full logs or confidential diagnostics.  
**Historical first report:** 2026-10-24. **Case metadata last reviewed:** 2026-10-29. **Publication:** NOT PUBLISHED.

## Finding

Computer Use discovery succeeded while approval timed out and GetCursorPos/input desktop access denied (#53300, #26358, #25178).

## Safety / interpretation

Never claim a GUI probe passed without approval, capture, visible input and process close; no UAC/ACL workarounds.

## Public sources (not vendor confirmation of root cause)

- [openai/codex#53300](https://github.com/openai/codex/issues/53300): Computer Use cursor denied and capture black
- [openai/codex#26358](https://github.com/openai/codex/issues/26358): Approval reviews time out
- [openai/codex#25178](https://github.com/openai/codex/issues/25178): Computer Use screenshot on Windows fails

## Reproduction

Run `python -m unittest discover -s tests -p 'test_failure_atlas_06.py' -v` from the
repository root. Tests in this topic use synthetic fixtures or pure contracts.
They do **not** exercise a real vendor client, operating system failure,
server, owner gate, SSH session, filesystem deletion or memory exhaustion.

## Release gate

Independent host/runtime or Windows reproduction requires separate evidence.
Do not publish original raw traces or claim an upstream hotfix.
