# Publication decisions and licenses

- Publisher identity: vYronFORGE. (independent, not OpenAI).
- Repository target for owner review: `p9j9cnxt4y-wq/vYronFORGE-HotfixKit`.
- Original HotfixKit source uses MIT (retained). The new authored reference
  code is contributed under the same MIT license for this candidate.
- FORGEPRIME is a project/working name, not an asserted IETF, ISO or official
  OpenAI standard or registered trademark. Name/rights clearance remains
  a separate business decision; no FPP proprietary sources are republished.
- Apache-2.0 applies to *OpenAI's public Codex project*, not to the closed
  ChatGPT Desktop product; no OpenAI source was copied into this package.
- Public issue links cite upstream reports without asserting developer
  confirmation or common causality.
- Sensitive/new vulnerabilities: coordinated private disclosure first.
- Third-party binary patches, reverse-engineered vendor clients and private
  incident logs: NOT INCLUDED.

## Pre-publish checklist

1. Review each evidence level and remove accidental personal/host identifiers.
2. Reverify URL status and code citations. Do not publish duplicate issues.
3. Pass Python unit/integration tests on Linux and native Windows CI.
4. Recheck dated vulnerability-advisory snapshot separately: it is from
   2026-09-14, not a live guide for October.
5. Run source manifest, release safety scan, dependency/build checks.
6. Confirm the actual owner-linked repository and compare remote contents.
7. Request explicit owner approval for first push, tag, issue comments and
   release; do not treat FORGE_READY as that authorization.
8. Publish an RC/pre-release only after remote CI results, not a stable release.

GitHub issues should receive the smallest casepack and synthetic fixture
relevant to that one issue, not an entire multi-project forensic archive.
