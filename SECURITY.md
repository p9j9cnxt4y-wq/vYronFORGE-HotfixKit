# Security policy

HotfixKit is defensive tooling. Do not publish a new zero-day, credential, private endpoint, exploit chain, destructive payload, unpatched sandbox escape, or internal incident evidence in a public issue.

## Reporting

For a suspected third-party vulnerability, use the affected vendor/project's coordinated or private disclosure channel first. Public discussion should be limited to already-public advisories or benign, sanitized regression evidence.

For a HotfixKit defect, report the minimum reproducer necessary. Replace environment-specific identifiers with neutral synthetic values before posting.

## Public-tree guarantees

- Default operation is audit/plan/render-only.
- Management-plane containment requires both `--apply` and `--ack-network-impact`. Operating-system update helpers require their separate explicit apply option; audit remains the default.
- Proprietary vendor binaries are never modified by this project.
- Unknown patch state, unmatched inventory and empty inventory never become PASS.
- Evidence output is redacted before serialization where supported.
- `tools/publication_scan.py` rejects common secret/private-infrastructure/local-user-path patterns in the tracked release tree.
- Public evidence does not claim production patching, deployment or compromise eradication.
