# vYronFORGE. Failure Atlas 0.1.0-rc1

**Companion introduced with HotfixKit 0.4.0-rc1 (2026-10-24), corrected in 0.4.1-rc1 (2026-10-29). Local reference candidate, not published.**

## Scope

The full finding-level register has **62 review entries** under `ALL_FINDINGS_20261029.md` and machine-readable `FINDINGS_REGISTER_20261029.json`. Eleven packages under `packages/failure-atlas/` provide independent findings,
provenance limits, existing Codex issue links, and self-contained synthetic
regression contracts. They do not assert that unrelated incidents were caused
by the same vendor component. A reported data-loss event is not a confirmed
OpenAI implementation flaw without its actual execution evidence.

This is a *failure-class collection*, not an exhaustive inventory of all
possible ChatGPT/Codex defects. It is not a destructive cleanup or exploit kit.

## Test

```
python -m unittest discover -s tests -v
python tools/verify_failure_atlas.py
python tools/publication_scan.py
python tools/verify_release_manifest.py
```

The inherited 0.3.0-rc1 test suite remains present. The new module offers
reference-oracle behavior without changing the existing remediation planner.

## Evidence levels

- `PUBLIC_UPSTREAM`: public issue text, not developer root-cause certification.
- `SOURCE_REVIEWED`: locally read JSON, README or selected source; no live replay claim.
- `USER_REPORTED`: prior owner or Codex report with missing raw event trace.
- `SYNTHETIC_REPRO`: local synthetic negative/positive pair.
- `HISTORICAL_RECORD_SUMMARY`: time-bound prior review, original dumps absent.
- `LOCAL_CLOSURE_REPORTED`: owner-reported tests; no current host integration proof.

## Mandatory invariants

- FORGE_READY is *not* EXECUTION_AUTHORIZED.
- READY, process started, exit zero, successful application and productive PASS
  are distinct facts.
- No inferred root, mounted volume, source authority or current release from a
  name-only path inventory.
- No automatic delete, overwrite, deployment, server access or installation.
- Public issue state was re-checked 2026-10-29 (see `UPSTREAM_STATUS_20261029.json`), but open issues do not prove current client defects.
- No privileged sandbox, UAC, ACL or system protection bypass.
- No process-spawn stress testing on a real host.
- All public artifacts have redacted, synthetic paths only.

## FORGEPRIME reference

FPP 0.1.0 with a local CoWorker readiness adapter was reported as
`PASS_LOCAL_HOST_CLOSURE` on 2026-10-21 (13/13 adapter tests, 28/28 executed
FPP tests, 1 optional skip), but the FPP source package and real productive
host adapter are **not included here or independently revalidated**. The
`readiness_precondition` helper is explicitly a synthetic precondition oracle,
**not** an implementation of the normative FPP schema, signature verifier,
replay store, or a replacement for RGES permission checks. A productive
Codex/CoWorker pre-run FPP check MUST invoke the *real* current FPP adapter
with live source binding, expiry and digest verification, and fail closed.

## Windows and release limits

Current tests run locally under Python without Windows app binaries. Native
Windows desktop and GitHub Actions CI have not run for this new candidate.
True Host skill-selection, Computer Use, app approvals, actual remote
services, privileged deletion containment, replay persistence, and client
model-message serialization remain out of scope of synthetic tests.

Original v0.3 candidate: SHA256
`48f6acfad37b885789c9f5fd5d00885237eb17cb92a111bac805c7d006e1129b`.
It is retained separately in the top-level upload bundle.
