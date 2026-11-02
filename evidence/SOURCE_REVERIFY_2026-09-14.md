# Source re-verification — 2026-09-14

Release source status after a second independent re-check.

## Explicitly re-checked source windows

- CERT-EU Security Advisories 2026-001 through 2026-012: all twelve are explicitly mapped in `cert_eu_2026_advisory_coverage` and enforced by `tools/verify_source_coverage.py`.
- Canadian Centre for Cyber Security current alert list through 2026-09-10: MikroTik AL26-020, NetScaler AL26-019, Cisco ASA/FTD AL26-018 and SharePoint AL26-017 are represented in policy.
- CISA KEV/current September delta identified through 2026-09-11: Chrome, N-able N-central, Citrix NetScaler, MikroTik RouterOS, JFrog Artifactory, GitLab and ConnectWise ScreenConnect are represented in policy.
- ConnectWise ScreenConnect CVE-2026-84869: fixed in 26.6.5+, with temporary file-transfer-permission mitigation if immediate upgrade is impossible.
- Chrome 153 desktop: the release is represented with a platform-aware fail-closed gate; publication re-verification on 2026-09-15 tightened Windows to 153.0.8010.37+ to avoid a cross-source false-PASS.
- Linux CVE-2026-31431 (Copy Fail): CERT-EU interim mitigation plus current Ubuntu fixed-kernel evidence is represented without pretending one kernel version applies to every distribution.

## Boundaries

This remains a bounded static snapshot, not an exhaustive mirror of every CVE worldwide. The planner therefore treats unmatched assets and vendor-specific unknown patch states as WARN/REQUIRES_VENDOR_VERIFY, never PASS.

## Source URLs

- https://www.cert.europa.eu/publications/security-advisories/2026
- https://www.cyber.gc.ca/en/alerts-advisories
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- https://www.connectwise.com/company/trust/security-bulletins/2026-09-08-screenconnect-bulletin
- https://chromereleases.googleblog.com/2026/09/stable-channel-update-for-desktop_0808145027.html
- https://ubuntu.com/security/CVE-2026-31431
