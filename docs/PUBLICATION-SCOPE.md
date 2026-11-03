> Current status (2026-11-02): v0.4.1-rc1 is published at commit 081d99aee62a42e4e87b946291a24b8008b782f8. Version 0.4.1 is a separate, unpublished local candidate. Dated NOT_PUBLISHED/NOT_DONE entries describe their historical preparation time.

# Public release boundary

HotfixKit is intentionally published as a **defensive** repository.

## Included

- already-public vendor/CERT/government advisory identifiers and source URLs;
- minimum/fixed-version gates where the public source supports a deterministic comparison;
- fail-closed planning and redaction logic;
- audit/update helpers using supported local operating-system mechanisms;
- render-first containment tooling with an explicit mutation acknowledgement;
- benign synthetic tests and byte-integrity regression fixtures;
- reproducible build/test/checksum evidence.

## Excluded

The public tree must not contain:

- unpublished vulnerability details, exploit chains, weaponized payloads or bypass recipes;
- credentials, API keys, tokens, cookies, private keys or authentication material;
- real IP/MAC/SSID/host names, private URLs, postal codes or infrastructure model identifiers;
- raw operator conversations, session logs, screenshots or internal incident evidence;
- private server/VM topology, deployment addresses or environment-specific secrets;
- proprietary vendor binaries or unsupported binary/firmware modifications.

## Evidence semantics

A PASS applies only to the named local/static gate. It is **not** evidence that a third-party appliance was patched, that a production fleet is uncompromised, or that no later advisory exists.

Network, deployment, firmware and production-runtime effects are outside the public verification run unless a future release explicitly records a separately authorized effect and its evidence.
