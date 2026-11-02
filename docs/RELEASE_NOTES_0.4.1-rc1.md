# HotfixKit v0.4.1-rc1 — release candidate

This release is prepared locally and has not been pushed or released by
HOTFIXKIT-PUBLISH-013. Remote Windows/Linux CI and actual FORGEPRIME/FPP host
readiness are separate pending gates.

## Included scope

- Dependency-free defensive inventory planner with fail-closed unknown states.
- Exact vendor matching, structured/free-text credential redaction and strict
  wheel RECORD/source-byte validation from the supplied 0.4.1-rc1 candidate.
- Failure Atlas: 11 topic packages, 62 findings, synthetic regression contracts.
- Dated policy snapshot: 2026-09-14; not a current vulnerability feed.
- Corrected release-content validation in a normal Git checkout: local .git
  metadata is allowed, but any .git entry in the release manifest is rejected.
  Three new regression tests cover normal and malicious manifest cases.
- Explicit UTF-8 and disabled bytecode generation in Windows/Linux CI.

The original 180-test evidence dated 2026-10-29 remains historical. Current
test counts, native-host results and archive digests belong to the external
HOTFIXKIT-PUBLISH-013 verification record. This document does not claim remote
CI, a production patch, a vendor root cause, or full platform acceptance.

## Installation and checks

Use the checked wheel in an isolated Python environment (Python >=3.10).
Offline installation needs no runtime dependencies:

    python -m pip install --no-index --no-deps vyronforge_hotfixkit-0.4.1rc1-py3-none-any.whl
    vyf-hotfix plan --inventory examples/inventory.example.json

For source tests, install the package or set PYTHONPATH=src, then run
python -m unittest discover -s tests -v. Verify the complete release source
manifest with tools/verify_release_manifest.py. Distribution archives must be
created exclusively from that verified manifest plus the manifest itself,
never by recursively archiving a checkout.

## Publication boundary

An Atlas readiness precondition is not a genuine FORGEPRIME/FPP gate.
Publication requires the real adapter and current candidate-bound receipt,
then separate owner approval before first push, and another approval before
tag/release. No server, deployment, credentials or live remediation are used
by the release verification.

Copyright (c) 2026 vYronFORGE. MIT license; see LICENSE.
