# Plan: Kater dashboard rebuild (no slop)

Branch: `cursor/dashboard-rebuild-no-slop-fed0`

## Goal

Ship a **working** operator cockpit for the MCP gateway: live status, catalog
toggles, evals, deploy configs, settings — wired to the real API. No runtime
monkeypatch layer. Design quality should feel like a serious exchange/control
surface: sharp, dense, readable, not AI-slop SaaS.

## Diagnosis (current `main`)

1. **Broken JS** in `src/kater/web/dashboard.py`: `trackedTimeout` is missing
   (orphan body after `trackedRAF`). The live page only “works” because
   `review_fixes.py` string-patches the module at import time.
2. **API/UI drift**: dashboard JS calls paths/shapes that don’t match routes:
   - `/api/servers/{name}/set` → real: `/api/mcp/servers/{name}/{enable|disable}`
   - `/api/tunnel/toggle` → real: `/api/tunnel/{provider}/start|stop`
   - `/api/deploy/config` → real: `/api/deploy` + `/api/deploy/{format}`
   - `/api/command`, `/api/credentials/save` → do not exist
   - settings save uses wrong field names + `PUT` (route is `POST`)
   - status metrics read non-existent keys (`tools.total`, etc.)
3. **Half-applied redesign**: brutalist CSS + uppercase copy in source, then
   runtime sentence-case patches. Constellation canvas referenced but not driven.
4. **API review gaps** still live only in the patch layer:
   - events not newest-first
   - backends swallow errors instead of 503 + `backends` alias

## Approach

Fold the good review fixes into real source, then rewrite the dashboard as one
coherent module. Delete the patch shim.

### Phase A — API solidification (`routes.py` only)

- `_events`: filter → take last `limit` → reverse (newest first).
- `_backends`: return `{backends, servers, totals}`; on proxy failure log + **503**
  with empty lists; accept optional `proxy_factory` for tests.
- Re-export `_events` / `_backends` from `kater.api` so existing tests keep working.

### Phase B — Dashboard rewrite (`dashboard.py` only)

One composition: industrial control plane (not cream/serif, not purple glow).

| View | Behavior |
|------|----------|
| Dashboard | Metrics from `/api/status`, tunnels via `/api/tunnel` + start/stop, backend health, recent calls, live WS feed |
| Catalog | `/api/catalog` + profile filter; enable/disable via real MCP routes; detail drawer; credentials → `/api/mcp/servers/{name}/credentials` |
| Evals | `/api/evals` per-tool table |
| Deploy | `/api/deploy` tabs → `/api/deploy/{format}` + copy |
| Settings | `/api/settings` GET/POST with correct field names |

Keep: first-party OAuth (`kater-dashboard` → `/authorize`), WS ticket flow,
ARIA tabs, confirm dialogs, sentence-case operator copy, reduced-motion.

Drop: broken/orphan JS, fake `/api/command`, runtime patch dependency, unused
constellation animation unless it has a clear job (static topology map of
servers is fine).

### Phase C — Cleanup

- Delete `src/kater/web/review_fixes.py`.
- `web/__init__.py` → plain `from kater.web.dashboard import render_dashboard`.
- Update `tests/test_dashboard.py` + `tests/test_pr81_review_fixes.py` to assert
  the native implementation (no patch markers).
- Keep `test_api.test_dashboard_html` green (`constellation-canvas`, `cmd-input`,
  `KATER`).

### Phase D — Verify

```bash
uv run ruff check .
uv run pytest -v
# with kater serve:
curl -s localhost:9091/health
curl -s localhost:9091/ | head
curl -s localhost:9091/api/backends
curl -s localhost:9091/api/events
./scripts/smoke.sh
```

## File ownership (parallel-safe)

| Agent / unit | Files |
|--------------|-------|
| A — API | `src/kater/api/routes.py`, `src/kater/api/__init__.py` |
| B — Dashboard | `src/kater/web/dashboard.py` only |
| C — Cleanup/tests | `src/kater/web/__init__.py`, delete `review_fixes.py`, `tests/test_dashboard.py`, `tests/test_pr81_review_fixes.py` |
| Coordinator | ruff, pytest, smoke, commit/PR |

Do **not** edit the same file from two agents.

## Out of scope

- New MCP backends / profile catalog changes
- Auth/OAuth protocol changes
- Cloudflare/tunnel infra
- Dependabot / unrelated open PRs (#93 topbar CSS can land separately)

## Success criteria

- `kater serve` → dashboard loads without import-time string surgery
- All five views hydrate from real endpoints
- Enable/disable, tunnel start/stop, settings save, deploy copy work
- 426+ tests green; no `review_fixes` module left
