# Cornerstone

Cornerstone is a coursework prototype exploring low-effort grounding skills for fictional testing scenarios. Phase 1 includes hold-to-breathe pacing, 5-4-3-2-1 sensory grounding, a daily check-in calendar, persisted OpenAI text chat, and an optional microphone-started `gpt-live-1` interaction backed by server-owned Responses delegation. The repository contains SQLite-backed model entities, database-controller CRUD, a validated FastAPI boundary, seven registered Vue routes, browser-timed skill interactions, and dedicated View request modules. Grounding, breathing, persistence, failure recovery, and the independent support route have browser/SQLite evidence; OpenAI text requests are fake-client verified, and Live audio has mocked backend/browser coverage only. No paid end-to-end provider call is claimed.

Repository: [https://github.com/Vinnyfio04/cornerstone-app](https://github.com/Vinnyfio04/cornerstone-app)

## Architecture

- `backend/models/` contains entity objects, relationships, and the model-owned local `data/` directory.
- `backend/controllers/` contains the SQLite database controller, FastAPI code, application services, and deterministic calculations. Route files remain thin and calculations remain framework-free.
- The complete `frontend/` directory is the View. It contains Vue source, components, CSS, assets, configuration, and build metadata; there is no additional nested MVC view directory.
- `docs/` will contain project documentation, including the documented JSON contract used for communication between Vue and FastAPI.

The dependency direction is view → controller → model. The frontend communicates with the controller only through the documented JSON API and never accesses SQLite directly.

The backend and frontend environments are project-owned. Python dependencies will be installed only in a virtual environment under `backend/`, and JavaScript dependencies will be installed locally under `frontend/`. Project dependencies must not be installed globally.

## Project documentation

- `docs/assignment_instructions.md` is the internal requirements-alignment source.
- `docs/design-pipeline.md` shows the current and planned project structure, request boundaries, and delivery checkpoints.
- `docs/design_notes.md` records exploratory product decisions, risks, and unresolved questions.
- `docs/phase-1-contract.md` defines the approved first-phase pages, interaction rules, model boundary, failure states, and acceptance evidence.
- `docs/mvc-contracts.md` defines model relationships and Model–View–Controller input/output rules.
- `docs/images/initial basic wireframe.png` is the current exploratory interface sketch.
- `docs/verification.md` records the latest repeatable scaffold checks and their limits.
- `prompts/` contains the small ordered library of major prompts used to establish and verify the scaffold.
- `handoffs/create-handoff.md` contains prompts for creating and resuming a temporary `handoffs/current.md` state record.

## Setup

Run these PowerShell commands from the project root to reproduce the backend environment on this computer:

```powershell
& 'C:\Users\Owner\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m venv 'backend\.venv'
& 'backend\.venv\Scripts\python.exe' -m pip install -r 'backend\requirements.txt'
```

The first command uses the verified CPython 3.12.14 interpreter. On another computer, replace that absolute path with a verified Python 3.10-or-newer executable. All backend dependencies are installed into `backend/.venv`; none are installed globally. The declared backend dependencies are `fastapi[standard]`, the official `openai` provider SDK, and `pytest`.

Install the frontend dependencies from the retained lockfile by running this PowerShell command from the project root:

```powershell
npm --prefix frontend ci
```

The frontend uses the project-local dependencies declared in `frontend/package.json` and locked in `frontend/package-lock.json`; Vue, Vue Router, and tooling are not installed globally.

## Phase 1 implementation status

- Step 1 complete: product, interaction, model, persistence, failure, and JSON contracts are documented.
- Step 2 complete: Vue Router and the original provider dependency were installed locally, and inert page/component/API/router scaffolds exist. The provider dependency was replaced by the OpenAI SDK in Step 13.
- Step 3 complete: the six documented Vue routes are registered and a Cornerstone application shell exposes primary navigation plus a separate support-information link.
- Step 4 complete: the home screen presents a green breathing-control preview, a prominent sensory-grounding entry, and a lower-emphasis chat entry in the documented order.
- Step 5 complete: the breathing control implements deterministic hold/release and keyboard start/stop behavior, four-second inhale and six-second exhale cues, a six-cycle completion point, measured active duration, early-exit state, and a post-stop grounding link.
- Step 6 complete: the grounding page implements the ordered 5-4-3-2-1 sequence, Back/Next/Finish controls, explicit early exit, measured duration, last-step result, restart, and home return.
- Step 7 complete: `Conversation` and `ExerciseSession` models, migration-safe schema initialization, chat-to-conversation relationships, exercise transition validation, CRUD, cascade behavior, and legacy-row preservation are implemented and tested.
- Step 8 complete: the FastAPI application factory, validated request schemas, stable JSON envelopes, user CRUD, exercise start/finish/exit, exercise history, and read-only conversation/message history endpoints are implemented and controller-tested.
- Step 9 complete: deterministic mock chat, the original configurable provider adapter, bounded context/output/timeout rules, persisted user/assistant/fallback records, and the chat-message endpoint are implemented and tested without a live provider call. Step 13 replaced that adapter with OpenAI.
- Step 10 complete: the View uses documented request modules to resolve one fictional demo user, save completed/exited exercises, send and recover mock chat, load saved activity, and update the demo display name. Transport and provider failures leave deterministic skills and navigation usable.
- Step 11 complete: a built-in-browser walkthrough completed sensory grounding, exited a second run, saved a deterministic mock conversation, reloaded history after an API restart, exposed retry controls during an API outage, and opened `/support` during that outage. Read-only SQLite rows matched the browser states. The walkthrough also found and fixed a grounding-outcome conditional bug and dark-mode chat contrast defect.
- Step 12 complete: the built-in browser completed all six paced-breathing cycles at 60 seconds, exited a second run early, and exercised incomplete provider configuration. The View showed a recoverable `model_unavailable` fallback, kept `/support` available, and SQLite matched the completed/exited sessions plus delivered/fallback chat rows. A misleading failure-mode label was found and corrected.
- Step 13 complete: the backend provider was migrated from Gemini to the OpenAI Responses API, current `.env` key/model names were mapped without exposing values, the OpenAI SDK replaced Google GenAI in the project virtual environment, and fake-client contract tests verify bounded requests without making a paid call.
- Step 14 complete: server-owned `GET /api/voice/config` and `POST /api/voice/sessions` create bounded `gpt-live-1` WebRTC sessions with Responses delegation through `VOICE_BACKEND_MODEL`, short Live instructions, separate backend instructions, disabled tools, sanitized failures, finite timeout, and no SDK retries. Mocked backend tests make no paid call.
- Step 15 complete at the mocked boundary: Chat contains an optional microphone-started WebRTC controller using `getUserMedia`, `RTCPeerConnection`, a remote audio element, and an `oai-events` data channel. Input/output transcript deltas fill transient user/assistant chat bubbles; interruption finishes the current assistant bubble and resumed assistant speech starts a new one. Mute changes only microphone-track enablement. End stops microphone tracks immediately, makes one bounded `session.close` attempt, waits briefly for `session.closed`, and then releases playback, timers, the channel, and the peer connection. Duplicate Start/End, transcript ordering, late events/SDP, duration expiry, navigation, page exit, unmount, and the independent support action have focused cleanup coverage while text chat remains usable.
- Step 18 complete: persisted text conversations can be started independently, are saved automatically with their ordered `chat_logs`, appear as named previews under History, and can be reopened in Chat to continue the same conversation. The existing relational schema remains unchanged: `conversations` owns user/timestamp metadata and `chat_logs` owns message content.
- Step 19 complete at the automated boundary: production text chat always uses the server-configured OpenAI Responses adapter. The runtime deterministic-response provider and `CHAT_PROVIDER=mock` selection were removed. Missing configuration now yields the existing recoverable `model_unavailable` path rather than a fabricated successful reply; focused test providers remain test-only. The server-managed prompt preserves the coursework, non-clinical, application-owned workflow boundaries, and requests use `store=False`.
- Step 20 complete at the automated boundary: persisted text chat now uses the supplied therapist-informed Cornerstone instruction verbatim from a dedicated controller-side prompt module. The instruction adds detailed response style, evidence, BPD-sensitive communication, rupture, application-capability, safety, professional, privacy, and cultural-humility boundaries while preserving fictional evaluation and application-owned exercise behavior. Fake-client tests confirm the prompt is passed as Responses `instructions`; voice retains its separate low-latency prompts.
- Step 21 complete: typed chat now adds an optimistic user bubble immediately on Send, labels it as sending while the provider request is pending, and replaces it in place with the persisted user/assistant records on success. Failure removes the transient bubble before reloading the saved fallback state, preventing duplicates or a permanently pending message.
- Step 22 complete at the automated boundary: local accounts can be registered, restored, signed into, edited, signed out, and deleted. Accounts store a unique username plus separate first and last names; passwords are salted and PBKDF2-hashed in the existing `login` table. The View stores only the active user identifier. Grounding, chat, voice, history, and saved activity require sign-in, while breathing and `/support` remain available signed out. This is prototype browser-session persistence, not server-issued API authorization.
- Final jurisdiction-specific support content, supplied reference-material integration, the fifteen-scenario evaluation, broad visual refinement, and a live paid voice/text OpenAI check remain incomplete. Live transcript bubbles are mock-verified but not yet confirmed against a real microphone/provider session.

## Verification

Run these PowerShell commands from the project root to verify the backend environment:

```powershell
& 'backend\.venv\Scripts\python.exe' -c "import pathlib, sys; import fastapi, pytest; assert pathlib.Path(sys.executable).resolve().is_relative_to(pathlib.Path('backend/.venv').resolve()); print(sys.executable); print(f'fastapi {fastapi.__version__}'); print(f'pytest {pytest.__version__}')"
& 'backend\.venv\Scripts\python.exe' -m pip check
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests -q --basetemp 'backend\.pytest_cache\tmp'
```

Run the frontend code-quality and production-build checks from the project root:

```powershell
npm --prefix frontend run lint
npm --prefix frontend run test:unit
npm --prefix frontend run build
```

## Local development

Start the FastAPI development server from the project root with:

```powershell
& 'backend\.venv\Scripts\python.exe' -m uvicorn backend.controllers.api.app:app --reload --host 127.0.0.1 --port 8000
```

Text chat always targets the OpenAI Responses adapter. With the ignored `.env`, start Uvicorn with `--env-file .env`; text chat requires `OPEN_AI_API_KEY` or `OPENAI_API_KEY` plus `OPENAI_CHAT_MODEL` (preferred) or `VOICE_BACKEND_MODEL` (compatibility fallback). Without complete text configuration, a sent message is saved with a fallback record and the API returns `model_unavailable`; it never substitutes a mock response. Voice requires the same key, `VOICE_BACKEND_MODEL`, and an optional bounded `VOICE_MAX_SESSION_SECONDS`. The spoken model is server-owned `gpt-live-1`; the delegated Responses model comes only from `VOICE_BACKEND_MODEL`. Do not commit the key. Configured text or voice use can incur paid API usage; no live paid call is claimed here.

Start the Vue development server from the project root with:

```powershell
npm --prefix frontend run dev
```

## TODO

- Continue the reviewed Phase 1 framework in `docs/phase-1-contract.md` one verified step at a time.
- Preserve the fictional evidence rows from Steps 11–12 until the user decides whether to retain or clear them for later demonstrations.
- Next, choose between a deliberately approved paid text/Live check, completing approved jurisdiction-specific support content, or building the fifteen-scenario evaluation matrix. Do not infer approval for paid calls or invent resource details.
- Keep server-issued authorization, final jurisdiction-specific support content, visual refinement, and use of the user's future reference material outside this completed integration step.

