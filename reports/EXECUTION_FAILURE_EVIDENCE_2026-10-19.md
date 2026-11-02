# AI-assisted execution integrity — evidence review

**Publisher:** vYronFORGE.  
**Review date:** 2026-10-19  
**Scope:** public, sanitized engineering review; Windows-to-Python-to-SSH/QGA-style boundaries, Codex Desktop text serialization, local host reliability.  
**Status:** `RELEASE_CANDIDATE / LOCAL_SYNTHETIC_TESTS_VERIFIED / UPSTREAM_FIX_NOT_VERIFIED`.

## Finding classes and provenance

* `PUBLIC_UPSTREAM`: an independently retrievable, already-public issue; a report is not proof of a universally reproduced client defect.
* `SOURCE_REVIEWED`: directly inspected, sanitized uploaded JSON/XML or source code; the reported process actions were not necessarily independently rerun.
* `USER_REPORTED`: technical findings summarized by the local Codex operator; original script/remote packet capture not supplied with this release.
* `SYNTHETIC_REPRO`: a synthetic fixture actually executed by this release's local tests; demonstrates a failure *class*, not its vendor-specific occurrence.
* `HYPOTHESIS`: possible connection requiring additional evidence.

Do not collapse these classes into a blanket statement that OpenAI, Claude or any other proprietary model has the same defect.

## A. Character and execution boundary faults

| ID | Earliest grounded date | Observed / reported behavior | Evidence class | Test and mitigation | Responsibility boundary |
|---|---|---|---|---|---|
| E-01 | 2026-08-29 | Codex Desktop issue #41486: a literal Windows path containing `_` is rendered correctly in the sent bubble but reportedly reaches the model with an inserted backslash. | `PUBLIC_UPSTREAM` | `test_model_payload_contract.py`; strict byte preservation at composer/model-input boundary | Only OpenAI can fix its client serialization; this kit does **not** patch it |
| E-02 | 2026-10-18 | An old local Windows Python text sender changed a 32-byte fixture into 34 bytes (LF→CRLF); a binary sender retained 32 bytes. | `USER_REPORTED` + `SYNTHETIC_REPRO` | `test_execution_integrity.py` and `echo_bytes.py`; pass raw `bytes` through `subprocess.run(..., text=False, shell=False)` | User/agent-generated execution helper; not proven as an upstream Codex core defect |
| E-03 | 2026-10-19 | Guest code reportedly emitted literal `\\t` (`5C 74`) where the safe-record parser expected actual tab (`09`). | `USER_REPORTED` + `SYNTHETIC_REPRO` | `guest_literal_tab.py` old negative / `guest_real_tab.py` fixed; strict parser; structured JSON protocol alternative | Guest template/parser contract in user-generated controller |
| E-04 | 2026-10-19 | Guest Python reportedly defined `main()` but never invoked it. The process returned exit 0 without complete records. | `USER_REPORTED` + `SYNTHETIC_REPRO` | `guest_missing_main.py` negative / `guest_valid.py` positive; nonempty, schema-valid, count-matched, completed record required | User/agent-generated guest template, not an SSH or QGA transport bug |
| E-05 | 2026-10-19 | Local v2 guest controller: 11 new tests and 10 regressions reportedly PASS; actual read of VM110 with v2 not run when reported. | `USER_REPORTED` | Separate downstream live gate after local source/test hash review; *not* executed by this kit | No certification of AngelWings authorization or certificate automation |
| E-06 | 2026-10-19 | C0001 test-harness empty capture reportedly failed and was corrected before target reads. | `USER_REPORTED` | Empty stdout negative regression case; require an actual successful parsed result, never exit-code-only PASS | Test-harness implementation; not an OpenAI client defect |

### Reproduction summary (synthetic only)

```text
LF/CRLF negative       expected LF; mutated CRLF -> BOUNDARY_BYTE_MUTATION
Binary stdin positive  local Python child echoes original bytes -> SHA256 equal
Literal TAB negative   guest emits backslash+t -> BAD_LEGACY_FIELD_DELIMITER
Actual TAB positive    guest emits ASCII HT -> parser accepts
Missing main negative  child exits 0 with empty stdout -> EMPTY_OR_OVERSIZED_STDOUT
Valid guest positive   real local guest.py -> stdout -> simulated QGA base64 -> strict records
Model text negative    synthetic original path vs Markdown-escaped path -> mismatch
```

The positive guest test uses three **synthetic labels** (`VM110`, `VM100`, `VM170`). No virtual machine, SSH connection or external host is contacted. The tests never prove the earlier *real* remote environment's current state.

## B. Additional host/forensics findings — deliberately NOT collapsed into the escape bug

| ID | Date / period | Finding | Evidence class | Boundary / follow-up |
|---|---|---|---|---|
| H-01 | 2026-09-18 to 2026-10-16 | Windows Reliability Monitor recorded 27 failed and 3 successful update events for the Codex package. Multiple update events do not prove 27 separate software failures or explain a root cause. | `SOURCE_REVIEWED` XML exports | Need Windows AppX deployment diagnostics for cause; **not** fixed by this library |
| H-02 | 2026-09-28 | Seven Reliability Monitor critical events for a local CoWorker verification executable; other WER entries overlap with RAC records. | `SOURCE_REVIEWED` | Need corresponding original run receipts; unrelated to Codex without a causal proof |
| H-03 | 2026-10-14 | One `ChatGPT.exe` critical crash record at 21:07:58; paired WER event likely same incident. | `SOURCE_REVIEWED` | Missing faulting-module / exception-code proof; not equated with character mutation |
| H-04 | 2026-10-18 | Screenshot showed ChatGPT error and nonresponsive window; manual restart reportedly restored normal appearance. | `USER_REPORTED` screenshot/feedback | Separate desktop reliability issue; crash cause unproven |
| H-05 | 2026-10-18 | Codex chat displayed `1. Jan., 1:00` despite October system time. | `USER_REPORTED` screenshot | Unix epoch or null-timestamp fallback is **hypothesis**; persisted timestamp not verified |
| H-06 | 2026-10-15..19 | Work/Chat/Codex plugin or skill availability differed across hosts in user screenshots. | `USER_REPORTED` | Host/workspace availability vs registry identity and actual load must be tested separately |
| H-07 | 2026-10-16 | Full project metadata run: 368,626 dirs; 1,373,407 files; 2,947 permission denials; 161 unfollowed reparse points. Opaque IDs impeded product attribution. | `SOURCE_REVIEWED` JSON and scanner source | Forensics governance/instrumentation issue; not a byte-escaping root cause |
| H-08 | 2026-10-19 | Two `dotnet build --no-restore` runs exited 1 with `MSB5021`; zero C# errors were reported but the first cancellation trigger is missing. | `SOURCE_REVIEWED` `BUILD_AND_TEST_RESULTS.json` | Build cancellation unknown; this kit cannot repair MSBuild or claim full AngelWings product parity |
| H-09 | Aug–Oct 2026 | Multiple resumed development tasks showed contradictory project roots, Source-Authority and historical PASS/current status. | `SOURCE_REVIEWED` summaries plus `USER_REPORTED` | Require canonical root/receipt reconciliation; do not infer authorship or source identity from names |

**Reliability Monitor provenance:** Two XML exports generated on 2026-10-16 expose identical event and graph payloads at different export times. They are not independent corroborating scans. The logs are not bundled in this public release: they may contain internal executable names and environment details.

## C. Confidence and causal limits

- Public issue #41486 is a **reported Codex Desktop client-side message mutation**. Our local path checks are synthetic and cannot exercise OpenAI's actual composer or model gateway.
- The CRLF transport error and the guest template errors are **different mechanisms in locally generated scripts**. They may be produced by an AI assistant, but authorship, original root cause and prevalence across vendors are not proven.
- `LF->CRLF` does not always cause a shell failure; it violates an exact-byte contract where LF was required.
- Guest exit code `0` is not sufficient: the full declared output schema, record count, and completion state must be checked.
- No private Codex logs, credentials, internal file trees, real target responses, raw system identifiers or copyrighted vendor binaries are distributed.

## D. Source and release map

1. `https://github.com/openai/codex/issues/41486` — already-public Codex Desktop path mutation bug, open when checked for this report.
2. `https://github.com/openai/codex/issues/46037` — related reported Windows path paste/escaping behavior; distinct reproduction needed.
3. Local user-supplied Codex technical summaries (2026-10-18–19), treated as user-reported evidence.
4. Local user-supplied Windows Reliability Monitor XML exports (generated 2026-10-16), inspected for event counts without redistributing original logs.
5. Local user-supplied `BUILD_AND_TEST_RESULTS.json`, `SOURCE_AND_COMPONENT_BINDING.json`, and `FINAL_STATE.json` from `CSHARP_NEUVERIFIKATION_20261019T191524Z`.
6. HotfixKit v0.2.2 source archive, SHA-256 `282c3d5e81574b1f366a1679d3c7b384c7942f8584a97c1f4ef42d4964c2e399`.

**Public-disclosure rule:** if a newly discovered issue exposes unpublished security-sensitive behavior, report it privately to the vendor. This package intentionally contains only non-destructive, publicly safe examples.
