# Phase 1 Product and Interaction Contract

## Status

This document defines the first implementation phase for review before application code or dependencies change. It supersedes the earlier one-path concept that treated breathing as a separate fixed-start exercise and limited the model to a one-turn acknowledgement.

Cornerstone remains a local coursework prototype evaluated only with fictional scenarios. The interface may prioritize urgent access to grounding skills, but it must not call itself an emergency service, therapy, diagnosis, clinical monitoring, or clinically validated support.

## Phase objective

Build a functional framework connecting the Vue View, FastAPI controllers, and SQLite models. Phase 1 emphasizes navigable pages, deterministic skill structure, persistence boundaries, a mockable chat-provider interface, and clear failure states. Visual refinement and supplied conversation-reference material come later.

## Page routes

| Route | Purpose | Phase 1 behavior |
| --- | --- | --- |
| `/` | Home | Hold-to-breathe control, prominent grounding entry, chat entry, persistent support link |
| `/grounding` | 5-4-3-2-1 grounding | Deterministic five-step sequence with no required typing |
| `/chat` | Conversation | Standard text chat using mock mode without credentials and OpenAI when configured |
| `/history` | Saved activity | Lists persisted chat messages and exercise sessions for the active fictional user |
| `/account` | Account framework | Profile CRUD shell; authentication remains inactive unless explicitly approved |
| `/support` | Crisis-support information | Static View content that works without FastAPI, SQLite, OpenAI, or classification |

The complete `frontend/` directory is the MVC View. Screen files may live under `frontend/src/pages/`; no nested MVC `views/` directory will be introduced.

## Home interaction

The first screen places actions in this order:

1. A concise coursework-prototype notice and persistent **Crisis support information** link.
2. A large green breathing circle labeled **Hold with thumb**.
3. A large, visually prominent **5-4-3-2-1 grounding** button.
4. A lower-emphasis **Start a chat** button.

The interface must remain understandable without relying on color alone.

## Hold-to-breathe contract

- Pointer, touch, or stylus press starts a repeating four-second inhale and six-second exhale cue.
- Releasing, pointer cancellation, route navigation, or loss of page visibility stops the cue immediately.
- A keyboard-accessible start/stop control provides equivalent behavior for users who cannot hold a pointer.
- Six uninterrupted cycles equal the planned 60-second completion point.
- A release before 60 seconds is stored as `exited`; reaching 60 seconds is stored as `completed`.
- Reaching 60 seconds does not trap the user or force navigation. The interface marks the planned sequence complete and permits release.
- The browser measures active time with a monotonic clock. The controller also records server start/end timestamps. Paused or released time is not active exercise time.
- After every release, regardless of duration, the home page prominently offers the grounding route.
- The model never controls breathing phases, timing, completion, or exit state.

## 5-4-3-2-1 grounding contract

The sequence remains deterministic and ordered:

1. Five things the user can see.
2. Four things the user can feel.
3. Three things the user can hear.
4. Two things the user can smell.
5. One thing the user can taste.

Phase 1 requires no typed response. The user advances with clear Next and Back controls and can leave at any time. Completion stores `completed`; leaving stores `exited` and the last visible step. Measured duration begins with the first sensory instruction and ends on finish or exit. Crisis-support information remains available throughout.

## Chat contract

The chat page provides a message list, text input, send action, loading state, retryable failure state, history access, an optional microphone-started voice session, and the persistent support link. Voice permission denial or connection failure never disables text chat.

- The credential-free development provider is deterministic `mock` mode.
- OpenAI mode is enabled when the server has `OPEN_AI_API_KEY` or `OPENAI_API_KEY` plus a configured model identifier.
- `OPENAI_CHAT_MODEL` is the preferred model setting; the existing `VOICE_BACKEND_MODEL` is accepted as a compatibility fallback. No model identifier is hard-coded into View code.
- Provider credentials, prompts, tracebacks, password hashes, and filesystem paths never reach the View.
- A user message is saved before the provider call. Successful, fallback, and failed assistant outcomes are saved distinctly.
- A failed or timed-out request returns a deterministic explanation and leaves navigation, breathing, grounding, history, and support information usable.
- Phase 1 limits message length, retained context, and output length through controller-owned constants.

The supplied therapy-conversation material will be used only after the user provides it and its provenance and suitability are reviewed. It will be treated as curated reference context or examples, not as a claim that OpenAI models were trained or fine-tuned by this project. No reference conversations will be generated to fill the missing source material.

## Account and history decision

Phase 1 uses one clearly labeled fictional local demo user so the skill and chat flows can be exercised without pretending that authentication is complete. Existing `users`, `login`, and `chat_logs` CRUD remains available at the model/controller boundary. The account page is a CRUD framework, not a security claim.

Working registration/login is deferred until password hashing, session handling, and authentication tests are deliberately scoped. Plaintext passwords must never be persisted or returned.

The history page shows only the active fictional user's saved chat messages and exercise sessions, including completion/exit status, measured duration, and model delivery status. It must not imply that another person is monitoring the history.

## Persistence additions

The existing three tables remain. Phase 1 adds:

- `conversations`: groups ordered `chat_logs` for one user;
- `exercise_sessions`: stores skill, status, planned duration, server timestamps, measured active duration, and last step/phase.

`chat_logs` gains a conversation reference. Migrations must preserve existing rows and must not overwrite a database file supplied later by the user. The exact fields and relationships are defined in `docs/mvc-contracts.md`.

## Independent support route

The `/support` page is compiled into the Vue View and opens without calling the backend. A persistent link appears on every route, including loading and error states. No keyword detector, model response, or classifier is required to reveal it.

Jurisdiction-specific resource names and contact details remain unresolved and must be supplied or approved before the support page is considered complete. Until then, the framework may contain clearly labeled placeholder copy, but verification must not claim final crisis-resource content.

## Project dependencies

- `vue-router` provides distinct, recoverable frontend page routes.
- `openai`, OpenAI's official Python SDK, sits behind a controller adapter and uses the Responses API.

Both were installed only into the existing project-owned environments and recorded in their manifests/lockfile. Their installation does not enable routing or OpenAI calls by itself. npm emitted engine warnings because Node 25.7.0 falls outside several transitive packages' even-numbered support ranges; verification therefore records the current build result without claiming Node 25 is a preferred long-term runtime.

## Required failure states

Phase 1 must visibly handle:

- missing OpenAI API key or model;
- OpenAI timeout or provider error;
- backend unavailable;
- invalid API input;
- database conflict or missing record;
- release, cancellation, route change, or visibility loss during breathing;
- leaving grounding before completion.

Failures must use the documented JSON error envelope when the backend is involved. The static support route must remain available.

## Phase 1 completion evidence

Phase 1 is ready for review when evidence shows:

- all routes open through the running View;
- the breathing control starts on press and stops on release;
- a full 60-second sequence and an early release produce distinct persisted states;
- grounding preserves its five ordered steps and records completion or exit;
- mock chat succeeds and injected chat failure remains recoverable;
- OpenAI mode is wired but clearly reported as unverified until a paid call is deliberately approved and suitable reference material is supplied;
- conversation and exercise history survive restart;
- support information opens independently before, during, and after backend/model failure;
- automated checks, browser observations, and SQLite queries agree;
- unfinished authentication, final support content, reference material, and visual refinement are reported honestly.

## Review decisions before Step 2

The following decisions are adopted for this contract unless changed during review:

1. Releasing before 60 seconds means `exited`; reaching six cycles means `completed`.
2. Phase 1 uses a fictional demo user and defers active login.
3. `conversations` and `exercise_sessions` are added to meet persistence and evidence needs.
4. Credential-free runs default to mock mode; a configured OpenAI key selects the OpenAI adapter and its server-side model setting.
5. Final jurisdiction-specific crisis-resource content remains blocked on user approval.
