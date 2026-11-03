# vYronFORGE. HotfixKit

**First introduced in 0.4.0-rc1: Failure Atlas**, a topic-separated collection of
redacted failure-class evidence, synthetic negative controls and portable
non-executing contract oracles. See `docs/failure-atlas/ALL_FINDINGS_20261029.md` and `docs/failure-atlas/README.md` and
`packages/failure-atlas/`. This is **not** an OpenAI binary patch, a vendor
certification, a production-ready agent executor or a claim that every reported
incident shares one root cause.


**Version 0.4.1 — local Stable candidate, not published.**

The public prerelease [v0.4.1-rc1](https://github.com/p9j9cnxt4y-wq/vYronFORGE-HotfixKit/releases/tag/v0.4.1-rc1) was published and independently verified on 2026-11-02 at commit `081d99aee62a42e4e87b946291a24b8008b782f8`. Its four CI jobs passed. Those results apply to that RC commit, not to this changed candidate. Stable source push, tag and release require separate owner gates.

HotfixKit is a bounded emergency remediation planner and verification pack. It does **not** claim to replace vendor patches, patch proprietary firmware, discover every vulnerability, or prove that a production environment is clean.

The public RC repository contains only defensive policy metadata, audit/update helpers, fail-closed gates, benign synthetic regression tests, and reproducible verification evidence. Internal incident data, exploit chains, credentials, private endpoints, infrastructure identifiers and raw operator logs are intentionally excluded.

## Historical corrected candidate (2026-10-29)

- Read the complete [62-finding register](docs/failure-atlas/ALL_FINDINGS_20261029.md) and [local verification report](docs/failure-atlas/FINAL_RELEASE_REVIEW_20261029.md).
- **180 local automated tests**, repeated in **20 passing rounds** (3,600 test executions); **35 independent content checks**, repeated in 20 rounds.
- Fixed in this independent reference implementation: exact vendor identity matching, improved Bearer credential redaction, strict wheel/RECORD/source-byte checks, and historical/current metadata separation.
- Public vendor bugs and Windows/production execution are **not claimed fixed**. Native GitHub CI and real FORGEPRIME host readiness remain `NOT_RUN`; no GitHub push/release is claimed.

## Current local preparation

HOTFIXKIT-HARDENING-018 prepares version 0.4.1 from the published RC without
changing the original checkout. New regression coverage addresses unknown versions,
branch boundaries, duplicate inventory IDs, edition/component identity, Windows
partial audit results and Linux package-manager failures.
See [Stable candidate notes](docs/RELEASE_NOTES_0.4.1.md) and
[manufacturer review](docs/POLICY_REVIEW_20261102.md). Exact candidate source hashes,
tests and artifacts are bound in the separate owner-gate evidence. No candidate CI,
deployment or Stable publication is claimed by the historical results below.

## Scope

The default snapshot is **2026-11-02**: 34 selected groups, 26 with a bounded
manufacturer claim reviewed and 8 explicitly UNKNOWN. UNKNOWN groups cannot
produce PASS_FIXED. The **2026-09-14 historical snapshot is preserved unchanged**
and can be selected explicitly with `--policy`; its older thresholds are not current
compliance evidence. Neither snapshot is a complete or live vulnerability feed.

Representative coverage includes:

- Microsoft Windows and SharePoint 2026 active-exploitation advisories
- MikroTik RouterOS / MikroTrick
- Check Point VPN critical advisories
- SAP September critical advisories
- Adobe Commerce/Magento and Acrobat/Reader
- Cisco Nexus, IOS XR and ASA/FTD
- VMware Workstation/Fusion
- PAN-OS
- Citrix NetScaler and VDA operational regression detection
- N-able N-central, JFrog Artifactory, SonicWall SMA1000
- Gitea, MLflow, GitLab, ConnectWise ScreenConnect
- Google Chrome reviewed desktop baseline with explicit platform identity
- selected Apple, Fortinet and Ivanti advisories
- Linux CVE-2026-31431 mitigation guidance
- vm2 dependency/configuration hard gate with outer-isolation requirement
- a benign Codex Windows path-integrity regression harness for upstream issue #41486

This is a **dated policy snapshot**, not a live vulnerability feed. Unknown or unmatched assets never become a clean PASS.

## Operating model

```text
READ inventory/policy
  -> PLAN fail-closed
  -> RUN supported local hotfix or render containment
  -> VERIFY resulting state
  -> WRITE redacted evidence
  -> STOP before external/network mutation unless the operator explicitly applies it
```

## Quick start

```bash
python -m pip install -e .
vyf-hotfix plan --inventory examples/inventory.example.json --out evidence/report.json
python -m unittest discover -s tests -v
python tools/verify_policy.py
python tools/verify_source_coverage.py
python tools/publication_scan.py
python tools/verify_release_manifest.py
```

### Windows security updates

Audit cached metadata only (no online search; zero cached updates is not current compliance):

```powershell
.\scripts\windows\patch-security-updates.ps1 -Mode Audit
```

An explicitly authorized online audit may use `-Mode Audit -OnlineScan`.
Partial search results fail with exit code 2.

Apply currently applicable Microsoft security updates (separate operator authorization and administrator required):

```powershell
.\scripts\windows\patch-security-updates.ps1 -Mode Apply
```

### Linux security updates

```bash
./scripts/linux/patch-security-updates.sh --audit
sudo ./scripts/linux/patch-security-updates.sh --apply
```

Linux audit can contact configured repositories; obtain network authorization before running it. The local hardening run did not start a Linux guest or contact repositories.

On apt systems without `unattended-upgrade`, the script intentionally refuses a broad automatic upgrade.

### Citrix VDA health gate

Read-only detection for the published September regression signatures:

```powershell
.\scripts\windows\citrix_vda_health.ps1 -LookbackHours 6
```

Exit code `2` marks the VDA unhealthy; code `3` means insufficient evidence. Missing BrokerAgent returns NOT_APPLICABLE. Event-log access failures never become healthy results. OS-specific out-of-band fixes are listed in CTX697101; absence of signatures does not prove compliance. The script does not uninstall Microsoft security updates.

### vm2 hard gate

`scripts/node/vm2_guard.mjs` requires vm2 `>= 3.12.2`, rejects dangerous NodeVM configurations, and requires an outer process/container/VM isolation signal before NodeVM use. It is defense in depth; a same-process JavaScript sandbox is not treated as an absolute host boundary.

### Management-plane containment

Render rules only:

```bash
python scripts/containment/nft_mgmt_lockdown.py --management-cidr 192.0.2.0/24 --ports 22,443
```

No rules are applied unless both `--apply` and `--ack-network-impact` are supplied.

## Codex path-integrity regression

The repository does **not** publish internal incident logs or claim a new sandbox escape. `tools/codex_path_integrity_regression.py` is a harmless local byte-integrity corpus associated with the already-public upstream Codex issue #41486. See `docs/upstream/CODEX-ISSUE-41486.md`.

## New: independent execution-integrity reference (0.3.0-rc1)

This **local-only** reference suite covers common character/escaping failures in agent-generated Python orchestration: CRLF mutation at a binary boundary, literal `\\t` instead of byte `09` for tab records, and a Python entrypoint that exits zero without invoking `main()`.

The reference code uses actual local Python child scripts, wraps their output in a synthetic QGA-shaped base64 envelope, and runs a strict production-style parser. It does **not** contact SSH or QGA, and does **not** patch proprietary Codex/ChatGPT software.

```bash
python tools/verify_execution_contract.py
python -m unittest discover -s tests -v
```

Full classification and limitations:
- `reports/EXECUTION_FAILURE_EVIDENCE_2026-10-19.md`
- `docs/execution-integrity/CONTRACT.md`
- `docs/execution-integrity/RELEASE_NOTES_0.3.0-rc1.md`
- `docs/execution-integrity/GITHUB_PUBLICATION_PLAN.md`
- `docs/upstream/CODEX-ISSUE-41486-COMMENT-DRAFT.md` (not posted)
- `reports/REGRESSION_TEST_MATRIX.md`

## Safety boundary

- No exploit or proof-of-concept payloads.
- No credential harvesting or persistence logic.
- No proprietary binary/firmware patching.
- Default operations are audit/plan/render-only.
- Unknown patch state, empty inventory and unmatched inventory are never PASS.
- Network/system mutation requires explicit operator action.
- Publication scanning rejects common secret, private-infrastructure and local-user-path material.
- Production patching/deployment is **not** claimed by the included evidence.

## Verification

The reproducible local/CI gates are documented in:

- `evidence/CANDIDATE_VERIFY_20261029.json` (historical supplied candidate)
- `evidence/QA_20_ROUNDS_20261029.json` (historical 20 review rounds and logs)
- `evidence/RELEASE_CONTENT_GATE_20261029.json` (historical 35 content checks)
- `evidence/RELEASE_CANDIDATE_VERIFY_2026-10-19.json` (historical v0.3.0-rc1 evidence)
- `evidence/SHA256SUMS.txt` (current source manifest)
- `evidence/VERIFY.txt` and `evidence/PUBLIC_RELEASE_REVERIFY_2026-09-15.md` (**historical v0.2.2**, not current candidate acceptance)

The PowerShell parser check has passed locally on Windows during HOTFIXKIT-PUBLISH-013. The Windows/Linux GitHub Actions matrix is **configured** but remains `NOT_RUN` for this candidate until an authorized push and exact-commit readback. Local syntax checks and unit tests do not establish full Windows/Linux remediation acceptance.

## Sources and disclosure

Authoritative source URLs are embedded per policy group in `policies/critical-2026-09-14.json`. See `SECURITY.md` and `docs/PUBLICATION-SCOPE.md` before filing security-related issues.

## License

MIT.

## Inventory identity and result limits

Gitea requires `edition: "community"` or `edition: "enterprise"`; numeric versions from the two lines are not interchangeable. ScreenConnect requires `component: "client"` and the deployed client version. A server record cannot prove agent remediation. Unsupported/prerelease versions fail closed. `PASS_FIXED` means only the named policy comparison passed, never full security or support status.
