# OSS / Private Split — Phase 2 Audit

**Date:** 2026-07-02  
**Scope:** `kater-dev-tools` working tree at split branch `feat/oss-private-split`

## Summary

| Classification | Count | Action |
|----------------|-------|--------|
| generic-example | 15+ | Keep in OSS |
| org-specific-config | 28 | Move to `utrecht-katermcp` or genericize in OSS |
| credential-shaped (P0) | 1 (local only) | Purge locally; not in git index |

## Hit table

| File | Line(s) | Match (redacted) | Classification | Action |
|------|---------|------------------|----------------|--------|
| `scripts/ensure-online.sh` | 11–12 | `https://kater.chefgroep.online/...` | org-specific-config | Move to `utrecht-katermcp/deploy/` |
| `scripts/systemd/kater.service` | 8, 14–15 | `%h/kater-dev-tools`, `kater.chefgroep.online` | org-specific-config | Move to `utrecht-katermcp/deploy/systemd/`; OSS ships `kater.service.example` |
| `docs/PLAN-v1.0.md` | 182, 272, 276 | `kater.chefgroep.online` | org-specific-config | Move to private `docs/` or redact |
| `docs/HANDOFF-2026-06-13.md` | multiple | `/home/sofie/...`, chefgroep VPS | org-specific-config | Remove from OSS; move to private |
| `docs/HANDOFF-2026-06-25.md` | multiple | internal paths | org-specific-config | Remove from OSS; move to private |
| `docs/adapters/utrecht.md` | 9, 17 | Tailscale IP, `OnlineChefGroep/utrecht-fleet` | org-specific-config | Move to `utrecht-katermcp/docs/` |
| `src/kater/profiles.py` | 370–381, 517 | `utrecht` ToolSource, `PRIVATE_PROFILES` | org-specific-config | Remove utrecht source; keep generic `KATER_EXTENSIONS_MODULE` hook |
| `src/kater/adapters/utrecht.py` | all | Utrecht adapter | org-specific-config | Move to `utrecht-katermcp/src/utrecht_kater/` |
| `src/kater/registry.py` | 40–120 | `utrecht_*` native tools | org-specific-config | Move with adapter; load via extensions |
| `src/kater/chains.py` | 39–48 | `utrecht_status` chain | org-specific-config | Move with adapter |
| `tests/test_utrecht_adapter.py` | all | Utrecht tests | org-specific-config | Move to private repo |
| `tests/test_registry.py` | 17–35 | utrecht assertions | org-specific-config | Update to `demo_private` fixture |
| `tests/test_chains.py` | 12, 35–40 | utrecht chain | org-specific-config | Update to fixture |
| `tests/test_profiles.py` | 27 | `utrecht` in profiles | org-specific-config | Update to fixture |
| `tests/test_api.py` | 277–280 | `utrecht` visibility | org-specific-config | Update to fixture |
| `tests/test_cli.py` | 85–88 | utrecht chains CLI | org-specific-config | Update to fixture |
| `tests/test_hardening.py` | 484 | `utrecht` not in public | org-specific-config | Update to `demo_private` |
| `.kater/oauth.json` | 8–35 | `tok_…`, `code_…`, production redirect | credential-shaped (local) | **Purge file locally; rotate tokens** — not tracked |
| `README.md` | 3, 134 | `OnlineChefGroep`, `utrecht` catalog row | generic-example | Keep attribution; remove utrecht row |
| `pyproject.toml` | 8, 27–30 | `OnlineChefGroep` URLs | generic-example | Keep |
| `docker-compose.yml` | 19 | `kater.example.com` | generic-example | Keep |
| `scripts/deploy-cloudflare.sh` | 4 | `kater.example.com` | generic-example | Keep |
| `.env.example` | 70–71 | `UTRECHT_*` placeholders | generic-example | Remove utrecht section from OSS |

## Grep commands (working tree)

```bash
grep -rniE "chefgroep\.(nl|online)" .     # 8 hits in 4 tracked files + gitignored oauth.json
grep -rniE "onlinechefgroep" . --include="*.py" ...  # 0 in code/config (README/LICENSE only)
grep -rniE "(postgres|redis|upstash)://[^\"'\s]+@" .  # 0
find . -name ".env" -not -name ".env.example"           # 0
```

## Move map → `utrecht-katermcp`

| OSS path | Private path |
|----------|--------------|
| `scripts/ensure-online.sh` | `deploy/ensure-online.sh` |
| `scripts/systemd/kater.service` | `deploy/systemd/kater.service` |
| `src/kater/adapters/utrecht.py` | `src/utrecht_kater/adapter.py` |
| utrecht registry/chains/profile defs | `src/utrecht_kater/extensions.py` |
| `docs/adapters/utrecht.md` | `docs/adapters/utrecht.md` |
| `docs/HANDOFF-*.md`, `docs/PLAN-v1.0.md` | `docs/internal/` |
| — | `profiles/ops.yaml`, `profiles/utrecht.yaml` (deployment env manifests) |
| — | `.env.example` (names only, OCG production) |
| — | `docs/DEPLOYMENT.md` |

## OSS replacements

| Removed | Replaced with |
|---------|---------------|
| Hardcoded `chefgroep.online` | `kater.example.com` or `$KATER_DOMAIN` in examples |
| `utrecht` profile in core | `KATER_EXTENSIONS_MODULE=utrecht_kater.extensions` (private) |
| `PRIVATE_PROFILES = {"utrecht"}` | Empty in OSS; defined in extension module |
