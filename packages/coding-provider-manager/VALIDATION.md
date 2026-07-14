# Coding Provider Manager v0.4.0 validation

Generated: 2026-07-14

## Build and tests

- TypeScript strict check passed.
- 14 Vitest files passed; 28 tests passed.
- ESM production build passed.
- npm audit reported 0 known vulnerabilities.
- Clean global-prefix installation passed.
- `cpm --version` returned `0.4.0`.
- Agent single-call and JSONL server smoke tests passed.
- OpenTUI snapshot and real pseudo-terminal startup/interrupt tests passed 3/3.

## Catalog

- 9 provider profiles.
- 49 coding surfaces.
- 3 multi-account drivers.

## Security

- AES-256-GCM vault retained.
- Master key and encrypted vault use mode `0600` on Unix.
- Key listings, agent responses and normal sync bundles are secret-free.
- Account metadata recursively redacts token/key/secret/auth/password/cookie fields.
- OAuth token files are not patched by CPM.

## Known boundary

Initial OAuth enrollment still belongs to the official or specialized client. Once accounts exist, CPM can switch accounts without logout/login through the registered driver.
