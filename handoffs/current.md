# Cornerstone Current Handoff

## November 3 submission update

The user subsequently authorized report completion and up to eight paid text attempts. `report.md` is now intentionally edited. Seven `gpt-5.6-sol` replies completed and one attempt failed to connect; the eight-attempt record in `docs/live-model-results.json` is exhausted and must not be reset or rerun for more paid calls without authorization. The user confirmed Codex-only development AI use, reuse of setup prompts but no other coursework code, and U.S./Pennsylvania support scope. The support View now has sourced static content. `AI-USE.md`, `docs/evidence-log.md`, `docs/evaluation.md`, and `docs/support-sources.md` record the added evidence. The test-only peer fixture uses its own ignored database and disables live voice. Earlier instructions below excluding `report.md` are historical and superseded by the latest user request. See the latest `docs/verification.md` entry for installation results and remaining limits.

Verified and updated on 2026-11-02 from `C:\Users\Owner\Desktop\School Work\5 Fall 2026\IST 402 - Vibe Coding\cornerstone-app`.

## Resume first

Read `AGENTS.md`, `README.md`, `docs/design-pipeline.md`, `docs/design_notes.md`, `docs/verification.md`, `docs/phase-1-contract.md`, `docs/mvc-contracts.md`, and this handoff. Recheck Git status and the latest user request before editing. Treat this file as a navigation aid rather than authority.

The user explicitly excluded `report.md` from the 2026-11-02 documentation refresh. Do not change it as part of that work.

## Current project state

- The Vue View has seven routes: Home, Grounding, Chat, Check-in, History, Account, and Support.
- Home has a deterministic 4-second inhale/6-second exhale exercise. The natural-speed `gentle-wind-chimes.mp3` ambience starts and loops only while the activity is active, then stops and rewinds on release, completion, interruption, navigation, or unmount.
- Check-in presents the calendar above the entry panel. Users can add multiple entries to today or a past date, edit an existing entry, select a standard feeling or enter a custom feeling and color, and see up to three colored markers on a saved date. Future dates are read-only. Month and year selectors support direct navigation.
- SQLite has six model entities: `User`, `Login`, `Conversation`, `ChatLog`, `ExerciseSession`, and `CheckIn`. The check-in migration preserves legacy rows while removing the old one-entry-per-day restriction.
- FastAPI owns user, exercise, conversation/chat, voice-session, and check-in JSON boundaries. The Vue View does not access SQLite or import backend Python.
- Account state remains a local fictional prototype rather than server-token authentication.
- Typed chat persistence, optimistic display, saved-conversation reopening, OpenAI-only production text chat, optional Live voice, and the independent Support route remain as documented in the phase contract and MVC contracts.

## Current verification baseline

At the start of the documentation refresh, Git was on `main` at `f1f4b64` (`Enhance calendar check-ins and exercise ambience`) and matched the local `origin/main` tracking reference.

- Backend: `47` tests passed; one non-failing pytest cache warning was emitted because the managed environment denied root cache access.
- Frontend: `64` tests passed.
- Frontend lint: passed.
- Production build: passed with Vite 8.3.4 and `69` transformed modules.
- The running development server returned HTTP `200`, `audio/mpeg`, and `1,721,029` bytes for the committed ambience file.
- No paid provider request, microphone access, database write, dependency change, or application-source change was made by the documentation audit.

## Remaining work and limitations

- Capture final browser and matching read-only SQLite evidence for the calendar create/edit/multiple-entry workflow if submission evidence requires it.
- Complete a systematic accessibility and physical-phone responsive review.
- Replace placeholder jurisdiction-specific support content only after approved resources are supplied.
- Perform the fifteen-scenario fictional language/safety evaluation before making a model-quality claim.
- Live OpenAI text and voice behavior, billing, latency, microphone handling, and remote playback still require explicit approval and a deliberately controlled test.
- `backend/models/data/intents.json` remains excluded from model input pending provenance and suitability review.
- Active server-backed authentication is not implemented and should not be implied by the local account gate.

## Recommended next step

Review the documentation diff, confirm `report.md` has no changes, and commit/push the documentation only if requested. For final evidence, start fresh local servers and pair calendar browser screenshots with read-only SQLite inspection rather than relying on historical screenshots.

---

# Archived handoff — 2026-10-27

The remainder of this file is the prior handoff snapshot. Its six-route, five-entity, authentication, test-count, Git-hash, and next-step statements are historical and are superseded by the current section above.

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
