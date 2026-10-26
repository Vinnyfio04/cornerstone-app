# Cornerstone Current Handoff

Verified and updated on 2026-10-26 from `C:\Users\Owner\Desktop\School Work\5 Fall 2026\IST 402 - Vibe Coding\cornerstone-app`.

## Resume first

Read `AGENTS.md`, `README.md`, `docs/assignment_instructions.md`, `docs/phase-1-contract.md`, `docs/mvc-contracts.md`, `docs/design-pipeline.md`, `docs/design_notes.md`, `docs/verification.md`, and this handoff. Recheck the branch and working tree before editing. Preserve the pre-existing user modification to `report.md` unless the user explicitly asks to change it.

## Objective and current state

Cornerstone is a coursework prototype for low-effort grounding in fictional test scenarios. The current vertical slice demonstrates both chosen skills through the running interface, measured exercise duration and exit behavior, persisted text-chat conversations and sessions in SQLite, deterministic provider failure recovery, and an independent static support route. The latest increment adds optional spoken interaction to Chat, but its evidence is mocked rather than a paid browser/provider run.

The reviewed scope is:

- A home screen with hold-to-breathe pacing and a prominent 5-4-3-2-1 grounding entry.
- A separate sensory-grounding flow with completion, early exit, measured duration, and persistence.
- Persisted text chat with deterministic mock behavior, bounded OpenAI Responses configuration, fallback records, retry/reload controls, and process-restart history.
- Optional microphone-started OpenAI Live interaction on the Chat screen.
- A direct `/support` route that is View-owned and independent of model/API success. Its jurisdiction-specific resource content is still intentionally incomplete.
- Fictional local demo-user CRUD rather than active authentication.

## Latest implemented increment

Backend voice boundary:

- `GET /api/voice/config` returns only readiness status and the bounded duration.
- `POST /api/voice/sessions` accepts only a bounded SDP offer. The current app does not require a profile/owner ID for voice, so the endpoint does not accept one.
- `backend/controllers/services/voice_service.py` owns `gpt-live-1`, `VOICE_BACKEND_MODEL`, the provider URL through the SDK, prompts, policy, event allowlists, the 15-second timeout, disabled retries, and the no-tools setting.
- Provider creation uses `store: false` only as a session-retrieval setting; this is not a general provider-retention claim.
- Responses expose only a validated session ID, SDP answer, and duration. Missing configuration, invalid or oversized SDP, provider failures, timeouts, and malformed provider responses produce sanitized public errors.
- `LIVE_INSTRUCTIONS` is the short spoken prompt. `DELEGATED_BACKEND_INSTRUCTIONS` separately defines reviewed application scope, self-report versus interpretation, permission before suggesting an activity, honest missing-context handling, and the prohibitions against diagnosis, therapy/treatment claims, medical advice, implied human monitoring, or invented record access.
- The independent crisis-support route is outside model control. Audio and voice transcripts are not persisted.

Frontend voice boundary:

- `frontend/src/pages/ChatPage.vue` adds optional voice without replacing text chat.
- `frontend/src/voice/voiceSession.js` requests audio-only MediaDevices access, creates an `RTCPeerConnection`, remote audio element, and `oai-events` data channel, creates the data channel before the offer, waits for ICE gathering, exchanges SDP through FastAPI, and becomes active only after `session.started`.
- The View presents permission, connecting, active, muted, closing, closed, and error states. Blocked playback exposes **Enable assistant audio**. Permission denial or any connection/provider error leaves text chat usable.
- Stop, close, error, timeout, superseded starts, and component unmount release timers, tracks, handlers, data channel, peer connection, and remote audio state.

## Architecture and durable decisions

- MVC direction remains `frontend/` View → `backend/controllers/` → `backend/models/`.
- Models own entities, relationships, and `backend/models/data/`. Controllers own SQLite CRUD, FastAPI, provider orchestration, and business logic. The entire `frontend/` directory is the View.
- The View communicates only through `docs/mvc-contracts.md`; it never imports Python or accesses SQLite.
- Deterministic code owns exercise sequencing, timing, persistence, exits, errors, and support access. Model output is bounded and must not control the support route.
- Do not diagnose, represent the prototype as therapy/treatment, imply human monitoring, invent crisis resources, or claim access to unsupplied records.

## Git and working-tree state

- Remote: `https://github.com/Vinnyfio04/cornerstone-app.git`
- Branch: `codex/first-rough-implementation`
- Upstream: none recorded
- `HEAD`: `e7baca0f0a001550a1a1709cdf6ca684cef3afa3`
- Commit: `Created initial framework of the project.`
- The working tree contains the Phase 1 implementation and documentation as uncommitted modifications/untracked files relative to that initial commit. Do not discard or broadly overwrite it.
- Modified tracked files include `.gitignore`, `AGENTS.md`, `README.md`, `backend/requirements.txt`, design docs, frontend package/runtime files, this handoff, and `report.md`.
- Untracked implementation files include the current backend models/controllers/tests, MVC and verification docs, and frontend API/components/pages/router/session/utils/voice/tests.
- `report.md` is known pre-existing user work and must be preserved.

## Current configuration and paid-call warning

A names-and-presence-only inspection of the ignored `.env` found nonempty `OPEN_AI_API_KEY`, `VOICE_BACKEND_MODEL`, and `VOICE_MAX_SESSION_SECONDS`. `OPENAI_API_KEY`, `OPENAI_CHAT_MODEL`, and explicit `CHAT_PROVIDER` were absent. No secret value was printed or changed.

Starting Uvicorn with `--env-file .env` can therefore select billable OpenAI behavior for text and voice. Do not make a live provider call without explicit user approval. For a credential-free text demonstration, force `CHAT_PROVIDER=mock` in the task-started server process without editing the ignored environment.

## Verification completed on 2026-10-26

- Backend: `40 passed in 5.12s` using a workspace-local pytest base temporary directory.
- Frontend: `23` tests passed, `0` failed, including mocked voice/browser lifecycle tests.
- Non-fixing Oxc and ESLint checks exited successfully without output.
- Vite 8.3.4 built `60` modules in `1.45s`.
- `pip check` reported no broken requirements.
- No paid provider call was made.

Read-only SQLite inspection of `backend/models/data/cornerstone.db` found:

- `users`: 2; `login`: 0; `conversations`: 1; `chat_logs`: 6; `exercise_sessions`: 9.
- Paced breathing: 2 completed, 4 exited. Sensory grounding: 2 completed, 1 exited.
- Chat: 3 delivered user messages, 1 delivered assistant message, 2 fallback assistant messages.
- `PRAGMA foreign_key_check`: no violations.

Earlier browser/SQLite evidence demonstrates a completed sensory-grounding exercise, an exited grounding exercise, a complete 60-second breathing sequence, an early breathing exit, deterministic mock chat, fallback rows after model failure, history after API restart, and `/support` availability during an API outage. Exact observations are in `docs/verification.md`.

The development processes used for earlier walkthroughs are no longer available. Start fresh servers before further browser work; do not assume FastAPI or Vite is running because the in-app browser still shows a localhost URL.

## Unfinished and unverified

- Real browser microphone permission/denial, WebRTC negotiation, remote audio, interruption, mute/unmute, closing, duration expiry, autoplay recovery, and Live data-channel behavior.
- Any paid `gpt-live-1` or delegated Responses request, model quality, provider availability, billing, or provider-side retention behavior.
- Post-live-session SQLite inspection confirming that no audio or transcripts were stored.
- The fifteen-scenario evaluation matrix, component-level Vue tests, systematic accessibility review, and saved walkthrough recording.
- Final approved jurisdiction-specific crisis-support resources.
- Active authentication and supplied therapy-conversation reference material.
- Broad visual refinement and an updated wireframe covering history, exits, failures, and support.

## Exact next step

Ask the user whether they explicitly approve one short paid end-to-end Live-audio check. If approved, start FastAPI with the ignored environment and start Vite, open `/chat`, have the user grant microphone permission, run one brief fictional interaction, verify all visible voice states plus mute/close/autoplay recovery where possible, then inspect SQLite read-only to confirm that no audio or voice transcript rows were added. Keep the session within the configured duration and report that `store: false` is not a general retention guarantee.

If the user does not approve paid use, keep provider/browser behavior mocked and proceed with the fifteen-scenario evaluation matrix or the remaining accessibility/support-content work they choose. Do not infer paid approval, invent final support resources, or broaden into active authentication or absent reference-material ingestion.
