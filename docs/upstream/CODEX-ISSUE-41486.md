# Codex Windows path-integrity regression — upstream #41486

This repository does **not** claim discovery of a new sandbox escape. It carries a benign regression invariant for an already-public Windows path-integrity issue in Codex Desktop:

- https://github.com/openai/codex/issues/41486

As re-checked on 2026-09-15, the upstream issue remains open. No private incident transcript, local filesystem inventory, account data or internal vYronFORGE infrastructure evidence is included here.

## Safe regression contribution

`tools/codex_path_integrity_regression.py` contains only synthetic path strings. It verifies byte-exact preservation using SHA-256 and exits non-zero on mutation.

Acceptance invariant:

```text
UTF8(canonical user text) == UTF8(model-visible input)
```

for literal/path-like segments. Presentation escaping must not silently change the canonical model payload.

## Upstream test shape

1. Send a synthetic corpus through the same composer/serialization pipeline used by Desktop.
2. Capture the model-input payload before transport.
3. Assert byte equality to the original UTF-8 text.
4. Cover backslashes, underscores, equals signs, non-ASCII text, code spans and pasted plain text.
5. Run the serializer test on Windows and independently of UI rendering.

Do not repost internal incident material. Any upstream contribution should be limited to materially new, reproducible and sanitized evidence.
