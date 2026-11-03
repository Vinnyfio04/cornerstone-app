# Cornerstone Design Pipeline

## Purpose

This document keeps project structure, request boundaries, and development checkpoints visible without duplicating the detailed internal requirements. Use it with `AGENTS.md`, `README.md`, and `docs/assignment_instructions.md` when planning or reviewing work.

Cornerstone currently has a verified backend environment, six SQLite-backed entities with database-controller CRUD, a validated FastAPI boundary for accounts, exercises, calendar check-ins, persisted text chat, history, and voice-session SDP exchange, plus server-configured OpenAI text and Live adapters. Production text chat has no synthetic-response mode: incomplete configuration follows the recoverable unavailable path, while automated tests inject focused provider doubles. The seven-route Vue View includes browser-timed skills, a multi-entry check-in calendar, and an optional microphone-started WebRTC controller on Chat. Browser/SQLite evidence covers the deterministic skills, historical mock-chat slices, restart persistence, request failure, and independent support route. Calendar persistence and exercise-ambience lifecycle have automated coverage. Text requests have fake-client coverage plus a bounded seven-reply live comparison within eight approved attempts; Live audio remains mock-verified only.

## Documentation order

1. `AGENTS.md` defines durable working and permission rules.
2. `docs/assignment_instructions.md` is the internal requirements-alignment source.
3. `docs/phase-1-contract.md` defines the reviewed implementation scope and interaction rules.
4. `docs/mvc-contracts.md` defines model relationships and JSON boundaries.
5. `docs/design_notes.md` records exploratory product decisions and unresolved questions.
6. This file records the intended architecture and delivery pipeline.
7. `README.md` records reproducible setup, verification, and development commands.
8. `docs/verification.md` records the latest verified checks and their limits.
9. `handoffs/current.md`, when intentionally generated, records temporary work-in-progress state.

## Project-file map

```text
cornerstone-app/
|
+-- AGENTS.md                         [current] durable agent rules
+-- README.md                         [current] setup and verification guide
+-- backend/
|   +-- requirements.txt              [current] FastAPI, OpenAI SDK, pytest
|   +-- .venv/                        [current, ignored] project Python environment
|   +-- models/                       [current] entity objects and relationships
|   |   +-- data/                     [current] ignored local SQLite data
|   |   `-- entities.py               [current] six Phase 1 model entities
|   +-- controllers/                  [current] database and business controllers
|   |   +-- database_controller.py    [current] migration-safe SQLite CRUD
|   |   +-- api/                      [current] validated FastAPI JSON boundary
|   |   +-- calculations/             [current scaffold] framework-free calculations
|   |   `-- services/                 [current] bounded text and Live provider orchestration
|   `-- tests/                        [current] deterministic backend checks
+-- frontend/
|   +-- package.json                  [current] Vue, Vue Router, and scripts
|   +-- package-lock.json             [current] locked JavaScript dependency graph
|   +-- src/                          [current] View source, components, CSS, and assets
|   |   +-- pages/                    [current] seven routed Phase 1 screens
|   |   +-- utils/                    [current] deterministic skill calculations
|   |   +-- api/                      [current] documented fetch request modules
|   |   +-- session/                  [current] account and exercise persistence
|   |   +-- voice/                    [current] framework-free WebRTC lifecycle controller
|   |   `-- router/                   [current] seven-route Vue Router mapping
|   +-- tests/                        [current] Node calculation/request unit tests
|   +-- public/                       [current] View static assets and CC0 ambience
|   +-- index.html                    [current] View HTML entry point
|   +-- vite.config.js                [current] View build configuration
|   +-- node_modules/                 [current, ignored] installed dependencies
|   `-- dist/                         [generated, ignored] production build output
+-- docs/
|   +-- assignment_instructions.md    [current] internal alignment source
|   +-- design-pipeline.md            [current] structure and flow overview
|   +-- design_notes.md               [current] exploratory product notes
|   +-- mvc-contracts.md              [current] MVC relationships and contracts
|   +-- phase-1-contract.md           [current] reviewed first-phase behavior
|   +-- verification.md               [current] scaffold verification record
|   `-- images/
|       +-- initial basic wireframe.png [current] exploratory interface sketch
|       `-- calendar wireframe.png      [current] calendar reference sketch
+-- prompts/                          [current] curated major project prompts
+-- handoffs/
|   +-- create-handoff.md             [current] handoff creation/resume prompts
|   `-- current.md                    [generated only when requested]
`-- .gitignore                        [current] generated and sensitive-file rules
```

The MVC dependency direction is `frontend/ (View) -> backend/controllers/ -> backend/models/`. Models own data, entities, and relationships. Controllers own the FastAPI boundary, database CRUD, application orchestration, and calculations that connect model results to documented JSON responses. The entire frontend is the View and owns screen-level presentation, components, and CSS. Routes should not contain calculations, View files should not perform persistence work, and model/provider details should remain behind controller contracts.

The initial wireframe shows a landing view with a breathing control plus guided-experience and chat entry points. Phase 1 now defines the home control as hold-to-breathe with an exercise-only wind-chime ambience and gives sensory grounding its own prominent route above chat. The calendar wireframe informed the implemented month grid and selected-day form; the current View extends it with month/year selectors, multiple events per day, custom emotion labels/colors, and past-date editing. History lists persisted text conversations and routes a selected conversation back into Chat, while New conversation creates a separate record on first send. The wireframes remain references rather than authoritative runtime specifications; `docs/phase-1-contract.md` and `docs/mvc-contracts.md` define current behavior.

## Request flow

```text
User action
    |
    v
Vue view / presentation component
    |
    | calls a dedicated frontend request module
    | with a documented JSON payload
    v
Controller: FastAPI route / validation boundary
    |
    | passes validated data; owns HTTP concerns only
    v
Controller: framework-free calculation/application service
    |
    +--------------------+----------------------+
    |                    |                      |
    v                    v                      v
Model: SQLite     Controller: model     Controller: deterministic
repository       adapter/service       workflow and timing
[current]        [current]             [current]
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

The voice path is View → FastAPI session controller → OpenAI Live. The View supplies only a bounded SDP offer. FastAPI owns credentials, `gpt-live-1`, the Live prompt, the delegated `VOICE_BACKEND_MODEL` prompt, event allowlists, duration, timeout, and disabled tools/retries. The View creates `oai-events` before its offer, waits for ICE gathering, and reports Active only after `session.started`. A framework-free transcript reducer converts allowlisted input/output deltas into transient timestamped chat bubbles: interruption completes the current assistant bubble, both speakers can continue independently during overlap, and later assistant speech starts a new bubble. Mute changes only microphone-track enablement; it leaves assistant playback and the provider session running. End stops local tracks immediately, attempts one `session.close`, accepts a late SDP answer only to complete that close, and releases the remaining transport after `session.closed` or a short fallback. Navigation, page exit, unmount, duration expiry, and the independent support action also clean up voice. Audio and voice transcripts are intentionally not persisted; each accepted new Start clears the prior transient voice transcript.

## Delivery checkpoints

1. **Align:** Read the durable rules and internal requirements. Record assumptions and ask only questions that materially affect scope, safety, architecture, or verification.
2. **Design:** Define the user flow, JSON contract, state ownership, persistence boundaries, model limits, failure behavior, and verification evidence before implementation.
3. **Implement narrowly:** Keep framework-free domain rules, API routes, frontend presentation, request code, persistence, and model access separate.
4. **Verify deterministically:** Inject focused fake providers for routine checks without exposing a mock response mode in production. Confirm boundary behavior, persistence, interruptions, failures, and independent paths with repeatable evidence.
5. **Review and document:** Update the README and design notes when commands or decisions change. Record what was actually verified and what remains unresolved.
6. **Handoff deliberately:** Generate `handoffs/current.md` only when work must continue in another session, then verify its claims against the project before resuming.

## Remaining vertical-slice acceptance evidence

The November 2–3 submission pass completed the fifteen automated fictional scenarios, three behavior checks, approved repeated live text comparison, test-only mocked peer setup, and sourced U.S./Pennsylvania support content. Earlier checkpoint descriptions retain historical limits. Current remaining items are final timing/media evidence, an independent person's clean-checkout confirmation, physical-phone/accessibility review, and live voice verification. See `docs/evaluation.md`, `docs/support-sources.md`, and the latest verification entry.

Steps 11–12 established the chosen skills, chat success/failure, restart persistence, and independent support route across Vue, FastAPI, deterministic controller logic, and SQLite. Remaining evidence should extend rather than duplicate it:

- replace placeholder crisis-support copy only with approved jurisdiction-specific content;
- evaluate at least fifteen fictional scenarios and three explicit behavior checks;
- repeat a small approved selection with live OpenAI only after the key, model, paid-call limit, and reference material are available;
- perform a deliberately approved microphone/WebRTC walkthrough covering permission, playback, mute, close, failure recovery, and the absence of audio/transcript persistence;
- pair a final calendar browser walkthrough with read-only SQLite evidence for multiple same-day entries, editing, custom colors, and legacy-row preservation;
- browser observations are paired with database queries and repeatable automated checks, and the verification record states unfinished or untested behavior plainly.

The observed and remaining evidence is detailed in `docs/design_notes.md` and `docs/verification.md`. The JSON contract and exact schema are recorded in `docs/mvc-contracts.md`.
