# Reproducible regression test matrix

**Scope:** local synthetic code only. No SSH, QGA connection, root mutation, file-system-wide enumeration, or vendor binary patch.

## Test gates

| Contract | Negative control / failing pre-fix behavior | Fixed / accepted result | Automated location | Real-world coverage |
|---|---|---|---|---|
| Windows LF handling | Two LF delimiters are converted to CRLF; 32→34-byte phenomenon in original report; synthetic fixture rejects mutation | Binary stdin/stdout preserving original SHA-256 | `tests/test_execution_integrity.py` | Actual original Windows text-mode path **NOT_RUN** here |
| Windows composer path serialization | `Z:\AREA_01` vs `Z:\AREA\_01` must differ | Exact canonical bytes retained | `tests/test_model_payload_contract.py` and legacy `tests/test_path_integrity.py` | Actual proprietary composer **NOT_RUN** |
| Guest record delimiters | Literal backslash+t in actual stdout (`5C 74`) must be denied | ASCII horizontal tab `09` accepted for legacy format | `tests/test_execution_end_to_end.py`, `tests/test_guest_protocol.py` | Real guest V2 **NOT_RUN** |
| Python function entrypoint | Process exits 0 without invoking `main()` and emits empty stdout | Real local script invokes `main()`, emits completed records | `tests/fixtures/guest_missing_main.py`, `guest_valid.py` | Real remote result **NOT_RUN** |
| QGA-like JSON framing | Empty, invalid base64, nonzero exit, missing `exited`, wrong record count | All fields validated; strict base64; exact record schema | `tests/test_guest_protocol.py` | Synthetic QGA-shaped response only |
| Data classes/redaction | Unrecognized free-form fields or invalid path-like record values are denied | Only bounded code-shaped fields accepted | `tests/test_guest_protocol.py` | Not a replacement for a secret scanner |
| Model-vs-UI parity | Synthetic backslash insertion rejected | Canonical model input identical for selected path-like spans | `tools/codex_path_integrity_regression.py` | Can only become a true Codex integration test upstream |
| Exit code/timeout | Local nonzero process and subprocess timeout cause coded errors | Trusted child returns code 0 and valid result | `tests/test_execution_integrity.py` | No effect-capable test runner invoked |

## Independently repeat locally

From the repository root, with Python 3.10+:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python tools/verify_execution_contract.py
python tools/publication_scan.py
python tools/verify_release_manifest.py
```

The first two Python operations test real local child processes in the fixtures directory. Do **not** substitute third-party or production scripts into these fixtures.

## Recorded local candidate result (2026-10-19)

- Unit/negative tests: **69/69 PASS** (Python 3.13, Linux).
- Synthetic execution-chain smoke checks: **5/5 PASS**.
- Original 34 dated policy groups and 12 CERT-EU mapping checks: **local static PASS**, not fresh vendor-advisory validation.
- Source syntax and policy checks: **PASS**.
- Offline wheel construction and local wheel import: **PASS**.
- Windows CI, PowerShell AST, native desktop serializer, remote QGA, live certificate results: **NOT_RUN**.

The final hashes and filenames are in `evidence/SHA256SUMS.txt`; candidate environment summary is in `evidence/RELEASE_CANDIDATE_VERIFY_2026-10-19.json`.

## How to avoid false PASS

- A local process returning `0` is **not** accepted without a valid, nonempty protocol envelope.
- A QGA-style response with `exitcode=0` is **not** accepted unless the decoded guest output is schema-valid and complete.
- Mocking the parser with premanufactured valid strings is **not** a substitute for executing the actual shipped local guest fixture.
- A synthetic boundary proof is **not** automatically the same proof as the user's historical remote execution.
