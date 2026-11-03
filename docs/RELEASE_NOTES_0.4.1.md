# HotfixKit 0.4.1 — Stable candidate

Status: LOCAL_CANDIDATE_NOT_PUBLISHED. Base: published v0.4.1-rc1, commit
081d99aee62a42e4e87b946291a24b8008b782f8. No new Git commit or remote CI is claimed.

## Changes

- Reject ambiguous/prerelease versions; match branch component boundaries and retain unassessed duplicate/missing inventory IDs.
- Require explicit Gitea edition and ScreenConnect client identity.
- Use the 2026-11-02 manufacturer review by default; keep the September snapshot byte-identical. Correct MikroTik, SonicWall and MLflow baselines; include GitLab backports and the reviewed Chrome stable baseline.
- Require vendor verification for eight groups without complete current manufacturer evidence.
- Windows audit uses local cached metadata by default, rejects incomplete searches and makes online scanning explicit. Citrix health reports insufficient evidence rather than silently ignoring log failures.
- Security updates are selected by language-independent Microsoft classification or all defined security severity levels; localized titles no longer control inclusion. Missing service evidence and a stopped Citrix BrokerAgent cannot yield a healthy result.
- Linux audit returns package-manager failures and no longer fails after a successful dnf/yum/zypper audit merely because Apply was not selected.

## Realness and limits

Local verification binds source bytes, regression tests, installed package behavior,
CLI, source/wheel scans and reproducible builds in the separate owner report.
A real Windows offline-cache smoke passed with zero cached security updates;
this does not establish current patch compliance. Citrix was not installed, so VDA
functional acceptance is NOT_RUN/NOT_APPLICABLE. Windows Git Bash mocks verify
shell error propagation only. Isolated native Linux testing is NOT_RUN: no usable
general-purpose guest or running container daemon was available. No service was
started and no distro/image was installed. These limitations remain open before
any claim of production or cross-platform acceptance.

New remote CI, target-environment patch acceptance, online update scans and actual
production application are NOT_RUN. The RC's four passing CI jobs do not transfer
to modified source. FPP readiness is time-bound and must be freshly obtained for
the exact future controlled action; FORGE_READY is not execution authorization.

## Owner gates

Review exact candidate diff, file map, source-tree identity, source/wheel SHA-256,
test results and limitations. A separate explicit gate is required for the first
Stable source commit/push and subsequent CI readback. Tag v0.4.1 and release/upload
require another explicit approval after exact-commit CI verification. No deploy
or productive patching is included. Assets must be rebound if any source changes.
