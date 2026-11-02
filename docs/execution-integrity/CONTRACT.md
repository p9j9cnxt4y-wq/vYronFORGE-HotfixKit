# Execution-boundary integrity contract (v1)

The contract addresses problems in **agent-written orchestration code**, independent of whether an agent came from Codex, ChatGPT, Claude, or another model. Support for a vendor's proprietary client is NOT implied.

## Invariants

1. Treat command/script bytes as bytes until the destination parser explicitly defines an encoding. Do not assume `text=True` preserves LF input across Windows process boundaries.
2. Execute a trusted script **from a file** using a concrete argument vector, with `shell=False`, `text=False`, bounded timeout and captured stdout/stderr. Do not assemble nested `-c "..."` shell strings from untrusted text.
3. If the contract requires *identical* bytes at a boundary, verify byte lengths and SHA-256 before interpreting the data. Normalizing, de-escaping or replacing characters without an explicit contract is not a valid repair.
4. Do not infer script execution from process launch or exit 0. Require a known protocol magic, a completion marker, declared record count, nonempty payload and exact schema.
5. Prefer a structured, versioned result (bounded UTF-8 JSON object) to free-form line protocols. If legacy tab fields are unavoidable, require byte `09`, not bytes `5C 74`, and reject CRLF where the declared format requires LF.
6. Wrap encoded guest output as base64 with strict decoding. Check QGA-style `exited`, `exitcode`, content fields, schema and allowed result codes before any interpretation.
7. Never print or publish raw stdout/stderr from a real host: opaque diagnostics can contain keys, paths and secrets. This library returns bytes only to the local caller. Sanitized errors use codes.
8. A synthetic local test is not a remote or vendor-client acceptance test. Separate signed/authorized effects from local unit verification.

## Minimal local usage

```python
from pathlib import Path
from vyronforge_hotfix.execution_integrity import run_local_python_file, verify_exact_bytes
from vyronforge_hotfix.guest_protocol import make_synthetic_qga_reply, parse_synthetic_qga_reply

result = run_local_python_file(Path("tests/fixtures/guest_valid.py"))
parsed = parse_synthetic_qga_reply(make_synthetic_qga_reply(result.stdout))
assert len(parsed) == 3
# The QGA-shaped wrapper is synthetic; no SSH, server or VM is contacted.
```

Standalone smoke verification:

```bash
python tools/verify_execution_contract.py
python -m unittest discover -s tests -v
```

## Deliberate limitations

- `run_local_python_file` is **not a sandbox**. Only run local trusted synthetic scripts. It can execute code; calling it on arbitrary user input is unsafe.
- `make_synthetic_qga_reply` is not a QGA client and cannot diagnose a real host.
- The JSON result schema is a new reference contract, **not** a claim that historic AngelWings guest output already uses it.
- This is not a source patch for `openai/codex` or the ChatGPT Desktop application. The composer/serializer has to be fixed and tested by its owner.
- Byte-exact checks are required only where the declared boundary promises byte preservation. UTF-8 versus terminal rendering issues require separate display testing.
- A product's build, runtime, certificate state and external authorization remain outside this reference library.
