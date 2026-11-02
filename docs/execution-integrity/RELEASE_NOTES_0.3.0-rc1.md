# vYronFORGE. HotfixKit v0.3.0-rc1 (candidate)

**Release class:** `LOCAL_PUBLICATION_CANDIDATE_ONLY` — not published, not approved by OpenAI, not an official patch.

This release keeps the v0.2.2 defensive/security policy snapshot (dated 2026-09-14) intact and adds a **Python standard-library-only reference guard** for AI-generated execution code.

Highlights:
- Binary, non-shell stdin/stdout subprocess wrapper for trusted local Python files.
- SHA-256 and length receipts for declared byte-preserving boundaries without outputting raw data.
- Versioned JSON guest result envelope with strict nonempty/completed/count validation.
- QGA-shaped **synthetic** base64 transport simulator and strict parser; no live QGA client.
- Legacy tab-format negative test for literal backslash+t versus real HT.
- Actual local child-process entrypoint negative test (process exits zero without records).
- Synthetic Codex Windows path-mutation fixture for existing issue #41486.
- Evidence ledger splitting upstream reports, direct source observations, local synthetic tests and unverified hypotheses.

The previous security policy catalog is frozen rather than freshly revalidated. Consult actual vendor advisories before taking patch decisions. Windows-only CI remains a separate verification gate.
