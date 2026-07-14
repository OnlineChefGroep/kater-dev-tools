# Kater control-plane wave: routing, contexts and operator state

Status: implementation started
Linear project: Kater Capability Fabric + Computer/Fleet
Milestone: M2 — Kater capability fabric

## Decision

Kater remains the capability and autonomous-engineering control plane. It may adopt proven gateway patterns from OmniRoute, but it does not become an inference-router clone.

The product boundary is explicit:

- gateway: protocol ingress, authentication, context resolution and capability discovery;
- routing core: provider/account pools, quotas, concurrency, health, cost and fallback;
- headless runtime: connector and embedded-service lifecycle;
- operator API: agents, jobs, interventions, evidence and audit;
- dashboard: a projection over the operator API, never the source of truth.

## First implementation slice

This branch introduces dependency-free domain contracts for:

- provider accounts and multi-window quotas;
- deterministic quota-aware account ranking;
- remote contexts with expiry and scopes;
- canonical agent states;
- embedded-service lifecycle states;
- typed intervention records.

The selector deliberately does not receive or return credentials. Credential resolution remains a separate policy-controlled step.

## Routing invariants

1. Disabled, exhausted or active-cooldown accounts are never selected.
2. Required scopes must be a subset of account scopes.
3. Concurrency and every quota window must admit the request.
4. Expired cooldowns and reset quota windows become eligible without mutating persisted state.
5. Ranking is deterministic; ties are broken by stable account ID.
6. Quota headroom dominates minor price or latency improvements to avoid burning the final usable account.
7. Every decision exposes reasons suitable for audit, telemetry and dashboard projection.

## Required follow-up slices

1. Persist provider/account pools, quota observations and usage ledger in SQLite.
2. Add policy-scoped remote context creation and short-lived token claims.
3. Integrate logical capability aliases and fallback into ProxyManager.
4. Add retry classification, cooldown feedback and session stickiness.
5. Expose routing decisions and quota state through REST, MCP and WebSocket.
6. Split embedded connector supervision from the central gateway process.
7. Add A2A task/status/artifact endpoints.
8. Connect agent state, resumability and intervention queue to repository/worktree/PR/Linear jobs.

## Non-goals for this slice

- no provider credentials in routing models;
- no dashboard-only state;
- no migration of Computer/Fleet ownership into Kater;
- no implicit policy grants from Brain or prompts;
- no compatibility break for existing prefixed MCP tools.
