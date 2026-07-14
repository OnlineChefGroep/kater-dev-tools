# Coding Provider Manager v0.4.0

`cpm` is an interactive and agent-native control plane for provider keys, OAuth account pools, model catalogs, coding tools, MCP resources, usage and SSH synchronization.

This bootstrap import contains the validated installable npm package plus SSH/operator documentation. A standalone `OnlineChefGroep/coding-provider-manager` repository is still the correct final home; the current GitHub connector cannot create repositories, so this package is staged under `kater-dev-tools` for immediate use.

## Install on an SSH agent host

After merge:

```bash
ssh sofie 'curl -fsSL https://raw.githubusercontent.com/OnlineChefGroep/kater-dev-tools/main/packages/coding-provider-manager/scripts/install-agent.sh | bash'
```

Before merge, install directly from the PR branch:

```bash
ssh sofie 'curl -fsSL https://raw.githubusercontent.com/OnlineChefGroep/kater-dev-tools/feat/coding-provider-manager-v0.4.0/packages/coding-provider-manager/scripts/install-agent.sh | CPM_REF=feat/coding-provider-manager-v0.4.0 bash'
```

The binary is installed without root access at `~/.local/bin/cpm`.

## Give a key to the remote host

The key travels over stdin and does not appear in the SSH command line:

```bash
printf '%s' "$OPENROUTER_API_KEY" | \
  ssh -T sofie '~/.local/bin/cpm key add openrouter primary'
```

## Agent calls over SSH

```bash
printf '%s\n' '{"id":1,"method":"system.status","params":{}}' | \
  ssh -T sofie '~/.local/bin/cpm agent serve'
```

Or use the included helper:

```bash
./scripts/cpm-ssh-agent.sh sofie keys.next '{"provider":"openrouter"}'
```

## Interactive terminal

```bash
ssh -t sofie '~/.local/bin/cpm tui'
```

Headless agents should use `cpm agent call` or `cpm agent serve`; the TUI is never required for automation.

## Account and key switching

```bash
cpm key next openrouter
cpm key best openrouter
cpm accounts next codex-multi-auth
cpm accounts next opencode-codex-multi-auth
cpm accounts next github
```

Once accounts exist in the delegated manager, these commands switch without logout/login.

## Validation

See `VALIDATION.md` and `SHA256SUMS`. The package passed 28 tests, strict TypeScript checking, production build, clean global installation, JSONL agent smoke tests and PTY TUI startup checks.
