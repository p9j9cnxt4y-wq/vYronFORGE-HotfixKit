# 09 — Windows app lifecycle, mobile drift, compaction and writer leases

**Status / evidence class:** `SOURCE_REVIEWED + PUBLIC_UPSTREAM`  
**Publication scope:** sanitized facts, not full logs or confidential diagnostics.  
**Historical first report:** 2026-10-24. **Case metadata last reviewed:** 2026-10-29. **Publication:** NOT PUBLISHED.

## Finding

Desktop turn/start not acknowledged (#49518), iOS project drift (#36454), compaction failure (#43963), writer lock (#51429).

## Safety / interpretation

Distinct thread/turn/execution acknowledgements; session state must remain unknown unless actual receipts exist.

## Public sources (not vendor confirmation of root cause)

- [openai/codex#49518](https://github.com/openai/codex/issues/49518): Windows desktop startup and turn/start absent
- [openai/codex#36454](https://github.com/openai/codex/issues/36454): iOS and desktop project assignment drift
- [openai/codex#43963](https://github.com/openai/codex/issues/43963): Thread unusable after compaction context errors
- [openai/codex#51429](https://github.com/openai/codex/issues/51429): Remote iOS writer lock blocks desktop

## Reproduction

Run `python -m unittest discover -s tests -p 'test_failure_atlas_09.py' -v` from the
repository root. Tests in this topic use synthetic fixtures or pure contracts.
They do **not** exercise a real vendor client, operating system failure,
server, owner gate, SSH session, filesystem deletion or memory exhaustion.

## Release gate

Independent host/runtime or Windows reproduction requires separate evidence.
Do not publish original raw traces or claim an upstream hotfix.
