# Verification scope — 2026-09-14

This release is a **bounded, fail-closed high-signal snapshot**, not a claim to enumerate every vulnerability worldwide. It includes 34 policy groups selected because they are actively exploited, critical with a published remediation, or operationally critical to safe patching as of 2026-09-14.

Sources were cross-checked against vendor advisories/release notes, CERT-EU security advisories and threat intelligence, Canadian Centre for Cyber Security advisories, CISA KEV evidence where officially corroborated, and project security advisories for covered open-source dependencies.

A policy entry does not imply that a proprietary product can be generically binary-patched. For vendor-owned appliances/software, HotfixKit supplies fail-closed identification, containment guidance, version/fix gates where authoritative, and vendor-remediation requirements.

## Local verification boundary

- Python planner, policy schema, redaction, version gates, package build/install, wheel contents, Codex path-integrity corpus, Bash syntax, Node syntax/guard behavior, and nftables render-only containment are locally executable and verified.
- No real Check Point, SAP, Cisco, Palo Alto, Citrix, SonicWall, N-able, JFrog, Fortinet, Apple, Google, GitLab or other vendor target fleet was available for end-to-end production patch execution.
- PowerShell AST parsing requires a PowerShell runtime; the local container has none. The Windows GitHub Actions matrix contains the native PowerShell parser gate but it cannot execute until the repository runs in GitHub Actions (or another Windows/pwsh environment).
- Configuration/edition-specific vendor matrices remain `REQUIRES_VENDOR_VERIFY` when a generic comparison would be unsafe.
- Continuous monitoring is still required because the source set changes after the snapshot timestamp.

## CERT-EU 2026 advisory coverage gate

All CERT-EU Security Advisories 2026-001 through 2026-012 are now explicitly mapped to one or more policy groups. `tools/verify_source_coverage.py` makes this a release gate so a future package cannot silently claim CERT-EU coverage while omitting a published advisory.

Chrome desktop fixed builds are platform-aware and deliberately conservative: Linux 153.0.8010.36+; Windows/macOS 153.0.8010.37+ for this snapshot. Google publishes the Windows/Mac release pair as 153.0.8010.36/.37, while the Canadian Cyber Centre states versions prior to 153.0.8010.37 are affected by CVE-2026-87491; the planner therefore avoids a Windows .36 false-PASS.
