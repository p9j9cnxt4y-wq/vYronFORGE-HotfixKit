# Public release re-verification — 2026-09-15

Release candidate: `vYronFORGE. HotfixKit 0.2.2`

## Recovery basis

The candidate was reconstructed from the previously generated 2026-09-14 HotfixKit package, then re-run and sanitized for public GitHub publication. The security policy snapshot remains dated 2026-09-14; this file records the later publication verification.

## Publication hardening

- Public scope boundary documented.
- Internal incident detail and redundant upstream incident-link document removed.
- Source-tree publication scanner added to CI.
- Literal test identifiers replaced with generated synthetic values.
- Chrome gate corrected conservatively: Linux `153.0.8010.36+`; Windows/macOS `153.0.8010.37+` for this bounded snapshot.
- No private infrastructure, credentials, private URLs or raw operator logs are intended in the public tree.

## Local verification

The final values below are generated/confirmed by the release run and mirrored in `VERIFY.txt`:

- unit/negative tests: `PASS`
- policy schema and 34-group load: `PASS`
- CERT-EU 2026-001..012 mapping gate: `PASS`
- bundled policy byte identity: `PASS`
- Codex benign path-integrity harness: `PASS`
- vm2 dependency/configuration guard behavior: `PASS`
- Bash/Node/Python syntax/compile gates: `PASS`
- nftables render-only and no-ack denial gates: `PASS`
- wheel build/content/install/CLI smoke: `PASS`
- publication scan: `PASS`
- checksum manifest: `PASS`

## Unverified locally

PowerShell AST parsing is not claimed locally when `pwsh` is unavailable in the verification runtime. The GitHub Actions matrix contains a Windows `pwsh` parser gate. Until that workflow runs successfully on GitHub, the release status remains `WARN_POWERSHELL_CI_PENDING` rather than an unconditional full-platform PASS.

## Effect boundary

No production network, firmware, vendor appliance, deployment, current-switch or remote-runtime mutation is part of this verification. This is source/package verification only.
