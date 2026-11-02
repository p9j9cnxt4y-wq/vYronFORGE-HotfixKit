# Changelog

## 0.4.1-rc1 — 2026-10-29 (LOCAL CORRECTED CANDIDATE, NOT PUBLISHED)

- Correct vendor identity matching to exact normalized declared names or explicit aliases (fix false PASS for shortened vendor names).
- Redact free-text Authorization Bearer/Basic and additional structured credential fields; extend publication scanning.
- Replace wheel verifier with ZIP path/duplication/RECORD-hash/source-byte validation and negative tests.
- Separate historical 0.3/0.4 evidence from current release acceptance; add 20+ independent release checks.
- No OpenAI binary patch, production execution, remote Windows CI, FPP host attestation or publication claimed.

## 0.4.0-rc1 — 2026-10-24 (LOCAL CANDIDATE, NOT PUBLISHED)

- Add 11 independent error-/theme-specific evidence and regression packages.
- Add local fail-closed contract oracles for path, resource, skill, approval,
  evidence, remote-metadata and publication decisions; no real destructive actions.
- Bind current public upstream Codex reports without conflating unrelated defects.
- Keep the 0.3 execution-integrity suite intact and runnable; no OpenAI binary patch.
- Explicitly label FORGEPRIME FPP 0.1.0 as an externally reported local closure,
  not bundled or product-activated; FPP readiness never authorizes execution.
- Native Windows GitHub CI, owner release gate and true host reproduction are pending.


## 0.3.0-rc1 — 2026-10-19 (LOCAL CANDIDATE, not published)

- Preserve the 2026-09-15 validated v0.2.2 snapshot as the starting point.
- Add a general-purpose, local-only byte integrity and guest output contract to mitigate agent-generated Python orchestration errors.
- Add real local child subprocess and strict JSON/QGA-shaped synthetic output tests with explicit fail-before/pass-after negative controls.
- Document public Codex issue #41486 separately from user-reported Python helper mistakes and unrelated reliability issues.
- Add a publication/review plan; do **not** claim an upstream or production binary patch.


## 0.2.2 — 2026-09-15

Public-release hardening of the recovered 2026-09-14 HotfixKit candidate.

- Added explicit public/private scope boundary and publication scanner.
- Removed redundant upstream incident-link material and retained only sanitized regression documentation.
- Tightened the Chrome Windows fixed-build gate to `153.0.8010.37+` after cross-source re-verification; Linux remains `153.0.8010.36+`, macOS `153.0.8010.37+`.
- Re-ran local unit, policy, source-coverage, redaction/publication, vm2, path-integrity, syntax, containment and wheel/install gates.
- Preserved `WARN_POWERSHELL_CI_PENDING` because native PowerShell AST parsing is configured in Windows CI but unavailable in the local verification runtime.

## 0.2.1 — 2026-09-14

Recovered verified package baseline with 34 bounded policy groups, fail-closed planning, supported local update helpers, containment rendering, redaction, regression harnesses and release evidence.
