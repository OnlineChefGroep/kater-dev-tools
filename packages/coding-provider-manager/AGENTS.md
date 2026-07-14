# Coding Provider Manager agent contract

- Use `~/.local/bin/cpm agent manifest` for discovery.
- Prefer `cpm agent call` or JSONL through `cpm agent serve`; do not depend on a TTY.
- Never print or return provider keys, access tokens, OAuth refresh tokens, cookies or auth files.
- Add secrets only over stdin: `printf %s "$KEY" | cpm key add <provider> <alias>`.
- Use `keys.use`, `keys.next` or `keys.best` for API-key switching.
- Use `accounts.use` or `accounts.next` for delegated OAuth/account switching.
- Do not patch Codex, OpenCode, GitHub, Cursor or other client credential databases directly.
- Normal `cpm sync` must remain secret-free unless the caller explicitly requests `--secrets`.
- Use `ssh -T` for JSONL calls and `ssh -t` only for `cpm tui`.
