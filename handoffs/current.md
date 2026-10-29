# Cornerstone Current Handoff

Verified and updated on 2026-10-27 from `C:\Users\Owner\Desktop\School Work\5 Fall 2026\IST 402 - Vibe Coding\cornerstone-app`.

## Resume first

Read `AGENTS.md`, `README.md`, `docs/design-pipeline.md`, `docs/design_notes.md`, `docs/verification.md`, `docs/phase-1-contract.md`, `docs/mvc-contracts.md`, and this handoff. Recheck Git status and the latest user request before editing. Treat this file as a navigation aid rather than authority.

Do not discard or overwrite `report.md`. It is the user's only pre-existing working-tree change and the user explicitly prohibited changing it while creating this handoff.

## Current objective and authorized scope

Cornerstone is a local coursework prototype for fictional testing of low-effort grounding skills. The current application connects the Vue View, FastAPI controllers, OpenAI provider boundaries, and SQLite persistence.

The most recent user work focused on preparing `report.md` and identifying the browser/SQLite screenshots needed for submission. This handoff task was limited to documentation. No application code, dependency, provider setting, Git history, or database row was changed.

## Implemented project state

- The six Vue routes are Home, Grounding, Chat, History, Account, and `/support`.
- Home contains a browser-timed 4-second inhale/6-second exhale exercise. Six cycles complete at 60 seconds; an early release is saved as exited.
- Grounding contains the ordered 5-4-3-2-1 sequence with Back, Next, Finish, Leave, measured duration, completion/exit results, and persistence.
- SQLite stores fictional users, conversations, ordered chat logs, and exercise sessions. History lists saved exercises and can reopen a selected conversation in Chat.
- Chat immediately displays a pending typed user bubble, reconciles it with persisted rows on success, and removes it before fallback recovery on failure.
- Production text chat is OpenAI-only. There is no runtime deterministic-success or `CHAT_PROVIDER=mock` mode. Missing configuration saves the user/fallback rows and returns the recoverable `model_unavailable` path. Tests inject focused provider doubles.
- The user-supplied text instruction is stored in `backend/controllers/services/chat_prompt.py` and is sent through the Responses API `instructions` field. It remains server-owned.
- Optional voice uses a server-owned `gpt-live-1` WebRTC boundary with Responses delegation through `VOICE_BACKEND_MODEL`. Transient input/output transcript bubbles, interruption, overlap, mute, End, timeout, navigation, page exit, and cleanup have mocked coverage.
- Voice audio and transcript bubbles are intentionally not sent through the text-chat API or stored in SQLite.
- The persistent `/support` route is View-owned and independent of API/model success. Its jurisdiction-specific resource content is still placeholder text.
- Account uses a fictional local demo user with an editable display name. Registration, login, and authentication are not active.

## Durable decisions

- MVC direction remains `frontend/` View → `backend/controllers/` → `backend/models/`.
- Deterministic application code owns exercise order, timing, completion, exit, persistence, errors, and support access.
- The model may contribute bounded conversation only. It must not control exercise workflow or access to support information.
- Do not diagnose, claim therapy/treatment, imply human monitoring, invent crisis resources, or claim access to information not supplied to the application.
- Do not make a live provider call without explicit user approval. The ignored environment is configured well enough that starting Uvicorn with `--env-file .env` can incur paid text or voice usage.

## Current configuration

A names-and-presence-only check of the ignored `.env` on 2026-10-27 found nonempty `OPEN_AI_API_KEY`, `VOICE_BACKEND_MODEL`, and `VOICE_MAX_SESSION_SECONDS`. `OPENAI_API_KEY`, `OPENAI_CHAT_MODEL`, and `CHAT_PROVIDER` were absent. No value was printed or changed.

Because production text chat is OpenAI-only, a credential-free run demonstrates the recoverable unavailable/fallback path rather than a successful mock reply. Historical mock-chat browser evidence remains valid only as earlier application/persistence evidence and must not be presented as a current live-model result.

## Git state

- Remote: `https://github.com/Vinnyfio04/cornerstone-app.git`
- Branch: `main`
- Upstream: `origin/main`
- `HEAD`: `5921804d3a92fe3be2f4f9cbbe96005eec2ecfe7`
- Commit: `Update project report`
- Before the handoff documentation edits, the only working-tree change was `M report.md`.
- This handoff task additionally modifies `docs/verification.md` and `handoffs/current.md`.
- No commit, push, branch change, reset, checkout, or destructive Git action was performed.

## Verification completed on 2026-10-27

Commands:

```powershell
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests -q --basetemp 'backend\.pytest_cache\handoff-2026-10-27'
Set-Location frontend
npm run test:unit
npx oxlint .
npx eslint . --no-cache
npm run build
& '..\backend\.venv\Scripts\python.exe' -m pip check
```

Results:

- Backend: `42` tests passed.
- Frontend: `53` tests passed.
- Oxc and ESLint exited successfully without output.
- Vite 8.3.4 built `64` modules successfully.
- `pip check` reported no broken requirements.
- No browser, provider, microphone, or paid call was exercised.

Read-only SQLite inspection found:

- `users`: 2
- `login`: 0
- `conversations`: 6
- `chat_logs`: 20
- `exercise_sessions`: 34
- Paced breathing: 2 completed, 23 exited
- Sensory grounding: 2 completed, 7 exited
- Chat: 10 delivered user rows, 6 delivered assistant rows, 4 fallback assistant rows
- `PRAGMA foreign_key_check`: no violations

These are ignored local fictional evidence rows, not committed seed data.

## Known report discrepancy

The working copy of `report.md` was intentionally not changed during this handoff. It currently contains facts that no longer match the merged application:

- It says text chat uses a deterministic mock provider by default. Current production text chat is OpenAI-only.
- It lists 40 backend tests, 49 frontend tests, and a 63-module build. The current verified results are 42 backend tests, 53 frontend tests, and a 64-module build.
- Its screenshot links still need the user's final evidence URLs.

Only correct these items when the user explicitly authorizes another report edit.

## Files changed for this handoff

- `handoffs/current.md`: replaced stale branch, feature, configuration, verification, database, risk, and next-step information.
- `docs/verification.md`: appended the 2026-10-27 handoff audit and current check results.
- `report.md`: not touched during this handoff.

## Unfinished or unverified

Implemented but not live-verified:

- A real OpenAI text response using the configured account, including latency, response quality, billing, and adherence to the supplied instruction.
- Real microphone permission, WebRTC negotiation, remote audio, transcript timing/accuracy, interruption, mute/unmute, End, duration expiry, and autoplay recovery.
- Read-only SQLite inspection immediately after a live voice session to reconfirm that voice audio/transcripts are not stored.

Planned or incomplete:

- Approved jurisdiction-specific support resources.
- The fifteen-scenario fictional evaluation and three cross-case behavior checks.
- Final screenshots, demonstration recording, and process recording.
- Systematic accessibility review and final visual refinement.
- Active authentication if it remains in scope.
- Reviewed integration of `backend/models/data/intents.json`; it remains excluded from model input pending provenance and suitability review.

## Exact recommended next step

Resume submission evidence work without changing application behavior:

1. Recheck `report.md` and ask for authorization before correcting its known runtime/test-count discrepancies.
2. Start fresh local servers only for the evidence being captured. Do not assume an old localhost tab means either server is running.
3. Capture browser and matching read-only SQLite evidence for exercise completion/duration, exercise exit, conversation persistence, request failure/recovery, and independent `/support` access.
4. Keep historical mock evidence labeled as historical. Do not use it as proof of a current model contribution.
5. Ask for explicit approval before any live OpenAI text or voice request. If approval is not given, document the live-provider limitation honestly and continue with non-paid evidence.
6. Add the final commit hash, screenshot URLs, and recording URLs only after those artifacts exist.

Do not invent final support resources, expose environment values, broaden into authentication, or modify `report.md` without a new user request.
