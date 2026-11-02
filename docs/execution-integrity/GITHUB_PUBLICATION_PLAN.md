# GitHub publication/review plan — NOT EXECUTED

## Existing remote target

`https://github.com/p9j9cnxt4y-wq/vYronFORGE-HotfixKit` was verified as a **public but empty repository** at review time (2026-10-19). This local package does not authorize initializing, pushing, filing issues or creating releases.

Other prior public repository: `security-proving-fleet`. It is **out of scope**. Do not edit its historical submission or competition-linked materials.

## Proposed staged publication

1. Independently review this candidate for license attribution, sensitive paths, proprietary source and public-report accuracy.
2. Confirm the existing v0.2.2 policy snapshot still has correct version/coverage claims if republishing it. The policy snapshot is dated, **not current vulnerability guidance**.
3. Execute Linux and Windows CI. In particular the pre-existing PowerShell AST check was not validated on a Windows runner in the original v0.2.2 evidence.
4. Review `reports/EXECUTION_FAILURE_EVIDENCE_2026-10-19.md`, and recheck upstream issue states and changelog.
5. Owner explicitly authorizes first commit(s) to the existing empty repository with a proper `README`, `LICENSE`, CI and source tree.
6. Only after a published CI PASS and another owner decision, create an appropriately labeled `v0.3.0-rc1` **pre-release**, not a production/official OpenAI hotfix.
7. If warranted, post the narrowly scoped Codex path-regression comment from `CODEX-ISSUE-41486-COMMENT-DRAFT.md` under existing issue #41486. Do not open a duplicate issue solely for the same symptom.

## Possible release description

> vYronFORGE. HotfixKit v0.3.0-rc1 — Independent, non-vendor reference tests for character preservation and local guest-protocol output integrity in agent-written Python tooling. Includes negative controls for Windows LF/CRLF translation, literal tab escaping and an uninvoked Python `main()`. Does **not** patch OpenAI Codex/ChatGPT binaries, claim vendor certification, or contact remote systems.

## Required remaining checks

- Public/source tests on Linux: run locally and record exact version and counts.
- Windows CI: `PENDING`, never substitute a Linux test for native Windows verification.
- Actual Codex Desktop composer/model serialization: `NOT_RUN` by this project.
- Real SSH/Proxmox/QGA/AngelWings/mail certification: `NOT_RUN`; requires separate user authorization.
- Python/SSH script-capture reproducibility from historical real controller: `USER_REPORTED`, no source-identical live reproduction bundled here.
