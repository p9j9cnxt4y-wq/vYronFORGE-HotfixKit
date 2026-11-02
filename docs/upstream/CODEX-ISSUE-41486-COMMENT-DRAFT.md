# Suggested comment for upstream issue #41486 — DRAFT, not posted

We maintain a small, synthetic regression harness for the Windows path-integrity issue described here:
https://github.com/openai/codex/issues/41486

**Test property:** the literal UTF-8 characters entered by a user for a path-like text span must match the corresponding canonical characters delivered to the model, even when rich-text or Markdown rendering adds presentation escaping.

**Regression example:** input `Z:\AREA_01` must not become `Z:\AREA\_01` in model-visible text.

Suggested upstream test:
- Enter the fixture as plain text, inline code and pasted text in the actual Codex Desktop composer.
- Capture a trusted, internal pre-model canonical payload, not only the rendered chat bubble.
- Assert byte equality of the path-like span at composer, serializer and model-input boundaries.
- Include underscores, backslashes, spaces, non-ASCII text, quote characters and Windows long paths.
- Fail the test if a literal backslash is inserted or a literal underscore is escaped in the *model payload*.

We can provide a local byte-comparison test utility; it **does not independently reproduce** your proprietary Desktop serialization path and cannot provide a tested binary patch for it.

Separately, our agent-generated Python/SSH/QGA-style helper code showed local LF/CRLF, field-delimiter and uninvoked-entrypoint defects. Those are **not evidence of the same upstream Codex Desktop issue**, so we are tracking them as distinct execution-protocol contract tests rather than treating them as duplicates of #41486.

---

Publication check: do not paste real account identifiers, hostnames, machine paths, session logs or credentials into an upstream comment. Owner review required before posting.
