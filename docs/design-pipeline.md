# Cornerstone Design Pipeline

## Purpose

This document keeps project structure, request boundaries, and development checkpoints visible without duplicating the detailed internal requirements. Use it with `AGENTS.md`, `README.md`, and `docs/assignment_instructions.md` when planning or reviewing work.

Cornerstone currently has a verified backend environment and an unmodified Vue starter. The application-specific modules shown below are design targets, not implemented features.

## Documentation order

1. `AGENTS.md` defines durable working and permission rules.
2. `docs/assignment_instructions.md` is the internal requirements-alignment source.
3. This file records the intended architecture and delivery pipeline.
4. `README.md` records reproducible setup, verification, and development commands.
5. `handoffs/current.md`, when intentionally generated, records temporary work-in-progress state.

## Project-file map

```text
cornerstone-app/
|
+-- AGENTS.md                         [current] durable agent rules
+-- README.md                         [current] setup and verification guide
+-- backend/
|   +-- requirements.txt              [current] declared Python dependencies
|   +-- .venv/                        [current, ignored] project Python environment
|   +-- api/                          [planned] FastAPI routes and JSON boundary
|   +-- domain/                       [planned] framework-free application rules
|   +-- persistence/                  [planned] SQLite repositories and schema access
|   +-- services/                     [planned] model and application orchestration
|   `-- tests/                        [planned] deterministic backend checks
+-- frontend/
|   +-- package.json                  [current] Vue and tooling declarations
|   +-- package-lock.json             [current] locked JavaScript dependency graph
|   +-- src/                          [current] generated Vue starter
|   |   +-- components/               [planned use] presentation components
|   |   +-- api/                      [planned] backend-request code
|   |   +-- views/                    [planned] application-level screens
|   |   `-- state/                    [planned] client session state
|   +-- node_modules/                 [current, ignored] installed dependencies
|   `-- dist/                         [generated, ignored] production build output
+-- docs/
|   +-- assignment_instructions.md    [current] internal alignment source
|   `-- design-pipeline.md             [current] structure and flow overview
+-- prompts/                          [current] curated major project prompts
+-- handoffs/
|   +-- create-handoff.md             [current] handoff creation/resume prompts
|   `-- current.md                    [generated only when requested]
`-- .gitignore                        [current] generated and sensitive-file rules
```

The planned directory names may be refined before feature implementation. The separation boundaries are durable: routes should not contain domain rules, presentation components should not perform backend requests directly, and persistence or model-provider details should remain behind adapters.

## Request flow

```text
User action
    |
    v
Vue presentation component
    |
    | calls a dedicated frontend request module
    | with a documented JSON payload
    v
FastAPI route / validation boundary
    |
    | passes validated data; owns HTTP concerns only
    v
Framework-free domain/application service
    |
    +--------------------+----------------------+
    |                    |                      |
    v                    v                      v
SQLite repository   Model adapter        Deterministic workflow
[planned]           [planned]            state and timing [planned]
    |                    |                      |
    +--------------------+----------------------+
                         |
                         v
              Documented result object
                         |
                         v
                 FastAPI JSON response
                         |
                         v
              Frontend request module
                         |
                         v
                Vue presentation update

Independent support-information path
User -----------------> always-available UI route/content
                         (must not depend on model success)
```

The model may contribute bounded language output, but deterministic application code must control workflow steps, timing, saved state, exits, failures, and independently available support information.

## Delivery checkpoints

1. **Align:** Read the durable rules and internal requirements. Record assumptions and ask only questions that materially affect scope, safety, architecture, or verification.
2. **Design:** Define the user flow, JSON contract, state ownership, persistence boundaries, model limits, failure behavior, and verification evidence before implementation.
3. **Implement narrowly:** Keep framework-free domain rules, API routes, frontend presentation, request code, persistence, and model access separate.
4. **Verify deterministically:** Prefer mocked model behavior for routine checks. Confirm boundary behavior, persistence, interruptions, failures, and independent paths with repeatable evidence.
5. **Review and document:** Update the README and design notes when commands or decisions change. Record what was actually verified and what remains unresolved.
6. **Handoff deliberately:** Generate `handoffs/current.md` only when work must continue in another session, then verify its claims against the project before resuming.

