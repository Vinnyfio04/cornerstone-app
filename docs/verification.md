# Cornerstone Scaffold Verification

Last verified: 2026-10-26

## Scope

This record verifies the project-owned backend environment, MVC model/database-controller behavior, the FastAPI route and schema boundary, deterministic mock chat, the configuration contract of the OpenAI adapter, View request mappings and failure handling, installed frontend dependency tree, registered Vue route source, production build, browser-observed vertical-slice evidence, and Git baseline. Paid OpenAI output has not been invoked or verified.

## Git baseline

- Repository: [https://github.com/Vinnyfio04/cornerstone-app](https://github.com/Vinnyfio04/cornerstone-app)
- Working branch: `codex/first-rough-implementation`
- Current committed version: `e7baca0f0a001550a1a1709cdf6ca684cef3afa3` (`Created initial framework of the project.`)
- At verification time, local `HEAD` and the local `origin/main` tracking reference matched.
- `report.md` had a pre-existing uncommitted modification and was intentionally excluded from this documentation update.

## Backend environment

Commands:

```powershell
& 'backend\.venv\Scripts\python.exe' --version
& 'backend\.venv\Scripts\python.exe' -B -c "import pathlib, sys; import fastapi, pytest; assert pathlib.Path(sys.executable).resolve().is_relative_to(pathlib.Path('backend/.venv').resolve()); print('executable=' + sys.executable); print('fastapi=' + fastapi.__version__); print('pytest=' + pytest.__version__)"
& 'backend\.venv\Scripts\python.exe' -m pip check
```

Observed results:

- Python 3.12.14 ran from `backend/.venv`.
- FastAPI 0.143.1 and pytest 9.1.1 imported successfully.
- `pip check` reported no broken requirements.
- All commands exited successfully.

## MVC database controller

Commands:

```powershell
New-Item -ItemType Directory -Force -Path 'backend\.pytest_cache'
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests -q --basetemp 'backend\.pytest_cache\tmp'
& 'backend\.venv\Scripts\python.exe' -B -c 'from backend.controllers import DatabaseController; db=DatabaseController(); db.initialize_schema(); print(db.check_references())'
```

Observed results:

- The first pytest attempt could not create its default Windows temporary directory under the managed sandbox. A second attempt also failed because the explicitly selected base directory's parent did not exist. After creating the ignored `backend/.pytest_cache/` parent, the same tests completed with `2 passed`.
- CRUD was exercised for `User`, `Login`, and `ChatLog` using temporary SQLite files.
- Tests confirmed the one-to-one user/login relationship, ordered user/chat-log relationship, foreign-key rejection for a missing user, and cascade deletion.
- The local `backend/models/data/cornerstone.db` was initialized with `users`, `login`, and `chat_logs`; `PRAGMA foreign_key_check` returned no violations.
- These checks validate the model/database-controller contract only. They do not validate authentication, HTTP endpoints, the Vue interface, exercise sessions, or personalization behavior.

## Frontend environment

Commands:

```powershell
node --version
npm --version
npm --prefix frontend ls --depth=0
& 'frontend\node_modules\.bin\oxlint.cmd' 'frontend'
& 'frontend\node_modules\.bin\eslint.cmd' 'frontend' '--no-cache'
npm --prefix frontend run build
```

Observed results:

- Node v25.7.0 and npm 11.10.1 were available; the Node version satisfies the range declared in `frontend/package.json`.
- The installed top-level dependency tree completed successfully.
- Oxc and ESLint returned success. ESLint emitted the existing warning that `eslint-plugin-oxlint` could not find `.oxlintrc.json`; no lint errors were reported.
- Vite 8.3.4 completed a production build with 24 modules transformed.
- Generated `frontend/dist/` output remains ignored and is not verification of any application-specific behavior.

The direct non-fixing lint commands were used so verification would not rewrite source files. The documented `npm --prefix frontend run lint` script uses `--fix` and `--cache`.

On 2026-10-21, the non-fixing Oxc and ESLint checks passed again with the same `.oxlintrc.json` warning. A standard Vite build transformed all 24 modules but failed while copying `frontend/public/favicon.ico` because the existing `frontend/dist/favicon.ico` was locked (`EBUSY`) during overlapping verification. The build was repeated to the ignored isolated output directory `backend/.pytest_cache/frontend-dist` and completed successfully with the same 24 modules. This establishes that the source still builds, but it does not establish why the existing generated favicon was temporarily locked.

## Phase 1 Step 2 scaffold and dependencies

Commands:

```powershell
npm --prefix frontend install vue-router@4
& 'backend\.venv\Scripts\python.exe' -m pip install google-genai
& 'backend\.venv\Scripts\python.exe' -m pip check
npm --prefix frontend ls vue-router --depth=0
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests -q --basetemp 'backend\.pytest_cache\tmp'
& 'frontend\node_modules\.bin\oxlint.cmd' 'frontend'
& 'frontend\node_modules\.bin\eslint.cmd' 'frontend' '--no-cache'
npm --prefix frontend run build -- --outDir ../backend/.pytest_cache/frontend-step2-dist
```

Observed results:

- `vue-router` 4.6.4 was added to `frontend/package.json` and the npm lockfile.
- `google-genai` 2.32.0 imported from `backend/.venv`; it was added to `backend/requirements.txt`.
- Installing Google GenAI replaced the environment's `websockets` 17.2 with its compatible 16.1.1 requirement. `pip check` reported no broken requirements afterward.
- This is a historical Step 2 record. Step 13 replaced this provider dependency and adapter with OpenAI.
- npm reported `EBADENGINE` warnings because Node 25.7.0 is outside the even-numbered ranges declared by several existing transitive packages. Installation still completed with zero reported vulnerabilities.
- Database-controller tests completed with `2 passed`.
- Non-fixing Oxc and ESLint completed successfully; ESLint repeated the existing missing `.oxlintrc.json` warning.
- Vite built successfully to the ignored isolated Step 2 output directory with 24 transformed modules.
- Six inert page files plus placeholder component, request-module, and router boundaries were created. They are not registered or imported by the generated application yet, so this step does not verify page navigation or application behavior.

## Phase 1 Step 3 application shell and routes

Commands:

```powershell
npm --prefix frontend run lint
npm --prefix frontend run build
& 'backend\.venv\Scripts\python.exe' -m pytest --basetemp 'backend/.pytest-step3-run'
npm --prefix frontend run dev -- --host 0.0.0.0 --port 41731
```

Observed results:

- Vue Router is registered in `frontend/src/main.js`, and `frontend/src/router/index.js` maps `/`, `/grounding`, `/chat`, `/history`, `/account`, and `/support` to their six placeholder pages.
- The generated Vue demonstration shell was replaced with a Cornerstone shell containing primary navigation, routed content, a persistent direct link to `/support`, and a prototype disclaimer.
- Frontend lint completed successfully, and Vite 8.3.4 built 36 transformed modules successfully.
- The first backend test attempt failed before test execution because pytest could not create its managed Windows default temporary directory. Repeating the unchanged tests with a project-local `--basetemp` completed with `2 passed`.
- Vite reported that the development server started on port 41731. The managed command sandbox could not open a socket to that server, so local HTTP route probes were not treated as evidence.
- Browser verification was attempted with the in-app browser. Its `localhost:5173` resolved to an unrelated Nittany Leasing application, and both the Windows LAN address and host bridge failed to reach this Vite process. Consequently, no visual navigation pass is claimed for Step 3.
- This step verifies route registration and compilation only. Every routed page remains an inert placeholder, and no feature behavior or backend request is implied.

## Phase 1 Step 4 home-screen framework

Commands:

```powershell
npm --prefix frontend run lint
npm --prefix frontend run build
& 'backend\.venv\Scripts\python.exe' -m pytest --basetemp 'backend/.pytest_cache/tmp-step4'
rg -n --glob '*.js' "Hold with thumb|Start 5-4-3-2-1 grounding|Start a chat|Crisis support information" frontend/dist
rg -n --glob '*.css' "breathing-circle|action-link-primary|support-link" frontend/dist
```

Observed results:

- The home source now presents the required controls in order: green breathing-control preview, prominent 5-4-3-2-1 grounding entry, and lower-emphasis chat entry.
- Grounding and chat entries are Vue Router links to `/grounding` and `/chat`. The support-information link remains in the application shell on every route.
- The breathing circle is deliberately disabled and labeled as a preview so this framework step does not imply that hold/release timing works.
- Frontend lint completed successfully. Vite 8.3.4 built 42 transformed modules, and the compiled bundle contained the expected labels and component styles.
- The unchanged backend database tests completed with `2 passed` using an ignored project-local pytest temporary directory.
- A visual browser pass remains unavailable because the managed in-app browser cannot reach the Windows-hosted Vite process, as recorded in Step 3. No visual, responsive-layout, focus-order, or click-navigation claim is made for Step 4.
- No API request, SQLite write, provider call, breathing timer, grounding progression, or chat interaction was added or tested in this step.

## Phase 1 Step 5 deterministic breathing interaction

Commands:

```powershell
npm --prefix frontend run test:unit
npm --prefix frontend run lint
npm --prefix frontend run build
& 'backend\.venv\Scripts\python.exe' -m pytest --basetemp 'backend/.pytest_cache/tmp-step5'
```

Observed results:

- `frontend/src/utils/breathingTimeline.js` owns the framework-free timing constants and snapshot calculation: four-second inhale, six-second exhale, ten-second cycles, six cycles, and a 60-second completion boundary.
- Three Node unit tests passed. They cover the inhale/exhale boundaries, cycle transition, six-cycle completion, elapsed-time clamping, invalid/negative time normalization, and measured-duration formatting.
- `BreathingCircle.vue` now measures active time with `performance.now()`, renders phase/cycle/progress state, and stops on pointer release, pointer cancellation, focus loss, page visibility loss, or component unmount during route navigation.
- Pointer/touch hold and keyboard hold are supported on the circle. A separate keyboard start/stop control provides equivalent toggle behavior.
- Early stop produces a local `exited` state and measured duration; reaching 60 seconds produces a local `completed` state. Both reveal a prominent link to `/grounding`.
- `prefers-reduced-motion` removes circle scaling while retaining text cues and timing. A separate live region announces phase/cycle changes without announcing the frame-by-frame duration.
- Frontend lint completed successfully, Vite 8.3.4 built 43 transformed modules, and the unchanged backend database tests completed with `2 passed`.
- The available in-app browser still cannot reach the Windows-hosted Vite process. The timing utility is unit-tested, but pointer capture, keyboard interaction, visibility interruption, route interruption, animation, focus order, and the full 60-second experience are not claimed as browser-observed evidence.
- No API request or SQLite write occurs. Exercise-session persistence and history remain intentionally deferred.

## Phase 1 Step 6 deterministic sensory grounding

Commands:

```powershell
npm --prefix frontend run test:unit
npm --prefix frontend run lint
npm --prefix frontend run build
& 'backend\.venv\Scripts\python.exe' -m pytest --basetemp 'backend/.pytest_cache/tmp-step6'
```

Observed results:

- `frontend/src/utils/groundingSequence.js` defines the immutable five-step order: five things seen, four felt, three heard, two smelled, and one tasted.
- Four grounding utility tests passed. They verify the exact sense/count order, valid step lookup, completed and exited results, visible last-step identifiers, duration rounding/formatting, and rejection of illegal status or step values.
- Together with the existing breathing tests, the frontend unit command completed with `7 passed`.
- The grounding page begins monotonic timing when mounted, provides Back, Next, Finish, and Leave exercise controls, and produces a local result with `completed` or `exited`, measured duration, and last visible step.
- The first Back control is disabled, Finish appears only on the fifth prompt, no typed response is required, and completion/exit offers restart or home return. The application-shell support link remains present throughout.
- Navigating away stops the local timer through component cleanup and constructs an exited result before the component is discarded. Because persistence is intentionally absent, that route-exit result is not yet recoverable after navigation.
- Frontend lint completed successfully, Vite 8.3.4 built 47 transformed modules, and the unchanged backend database tests completed with `2 passed`.
- The available in-app browser still cannot reach the Windows-hosted Vite process. Prompt rendering, control focus/order, click navigation, measured duration in the rendered page, completion, and early exit are not claimed as browser-observed evidence.
- No API request or SQLite write occurs. Grounding and breathing persistence remain deferred to the model/controller step.

## Phase 1 Step 7 conversation and exercise persistence models

Commands:

```powershell
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests -q --basetemp 'backend/.pytest_cache/tmp-step7-final'
& 'backend\.venv\Scripts\python.exe' -m pip check
& 'backend\.venv\Scripts\python.exe' -c 'from backend.controllers import DatabaseController; DatabaseController().initialize_schema()'
```

The project database was then opened read-only with Python's `sqlite3` module to list non-system tables, columns, row counts, and `PRAGMA foreign_key_check` results.

Observed results:

- Five backend tests passed. They cover CRUD across all entities, conversation ownership, ordered conversation messages, conversation/message cascade behavior, exercise creation/completion/exit validation, terminal-state idempotence/conflicts, user cascade deletion, and foreign-key enforcement.
- A populated legacy-schema test starts with two `chat_logs` rows that lack `conversation_id`. Initialization creates one preserved conversation, retains both chat IDs, content values, ordering, timestamps, and delivery states, adds a non-null conversation reference, removes the temporary legacy table, and remains idempotent on a second initialization.
- Legacy chat migration runs inside a SQLite savepoint. An error rolls back the table replacement rather than leaving a partially migrated chat table.
- `pip check` reported no broken requirements. No dependency was added or changed in this step.
- The ignored project database contained zero rows before migration. After initialization it contained `users`, `login`, `conversations`, `chat_logs`, and `exercise_sessions`; `chat_logs` had the new `conversation_id` column, and `PRAGMA foreign_key_check` returned no violations.
- The project database remained empty after schema initialization; no fictional user or exercise data was seeded.
- The seven frontend utility tests, frontend lint, and the 47-module Vite production build also passed unchanged.
- FastAPI endpoints and View-to-controller requests do not exist yet, so this verifies persistence only through the Python database-controller contract and direct SQLite inspection—not through the running interface.

## Phase 1 Step 8 FastAPI boundary and non-chat endpoints

Commands:

```powershell
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests -q --basetemp 'backend/.pytest_cache/tmp-step8'
& 'backend\.venv\Scripts\python.exe' -m pip check
npm --prefix frontend run test:unit
npm --prefix frontend run lint
npm --prefix frontend run build
```

The project database was also reopened in SQLite URI read-only mode to list tables, row counts, and `PRAGMA foreign_key_check` results.

Observed results:

- Eleven backend tests passed: the five database-controller tests plus six API-boundary tests.
- The API tests verify OpenAPI registration for health, user CRUD, exercise start/update/history, and conversation/message history. They explicitly verify that the chat-message route is still absent.
- Pydantic request models reject blank names, undocumented fields, invalid skills/statuses, and negative durations. Routes serialize the documented `data`/`error` envelope and map missing records or illegal terminal exercise transitions to stable `not_found` and `conflict` responses.
- User CRUD, measured exercise duration, completed/exited state, newest-first exercise/conversation history, increasing message order, and omission of internal message ownership fields are controller-tested against temporary SQLite files.
- Reopening a second application/controller instance against the same temporary SQLite path preserved the fictional user and a completed grounding session with `42231` milliseconds and `taste_1` as the last step.
- FastAPI initializes the schema through its application lifespan. A local development entry point is available at `backend.controllers.api.app:app`.
- `pip check` reported no broken requirements; no dependency was added or changed in this step.
- Read-only inspection confirmed the project database still contains the five expected tables, zero rows in each table, and no foreign-key violations. Step 8 tests used temporary SQLite files and did not seed the project database.
- All seven frontend utility tests passed, frontend lint exited successfully, and Vite built 47 modules.
- The managed Windows command environment blocks localhost socket access and its Python event loop cannot be used for an ASGI request. Tests therefore exercise registered FastAPI route functions, Pydantic schemas, error responses, OpenAPI metadata, database controllers, and persistence in process; they do not claim a live HTTP request, browser observation, or Vue-to-FastAPI integration.
- No chat provider, chat-message POST route, live provider call, Vue request, active login behavior, or browser persistence was added in this step.

## Phase 1 Step 9 bounded chat service and provider adapters

Commands:

```powershell
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests -q --basetemp 'backend/.pytest_cache/tmp-step9'
& 'backend\.venv\Scripts\python.exe' -m pip check
npm --prefix frontend run test:unit
npm --prefix frontend run lint
npm --prefix frontend run build
```

After the suite, Python's `sqlite3` module opened the generated unavailable-provider database and the ignored project database in URI read-only mode.

Observed results:

- Twenty-two backend tests passed. New checks cover the registered chat-message route, deterministic mock success, new and existing conversations, user/assistant persistence, input boundaries, injected unavailable and timeout outcomes, stable `model_unavailable`/`model_timeout` mapping, and persisted fallback records.
- Service tests verify that retained context is capped at 12 messages and 8,000 characters, provider output is capped at 4,000 stored characters, and a conversation belonging to another user cannot be reused.
- Request validation caps user messages at 2,000 characters. The original provider adapter configured a 15-second SDK timeout and a 256-token output limit.
- A fake provider client verified model selection, role mapping, server-only API-key passage, request configuration, and response extraction without opening a network connection. Missing key/model configuration failed deterministically before any network call.
- This Step 9 provider contract was superseded by the OpenAI adapter in Step 13. Deterministic mock mode and the public failure envelope remain unchanged.
- Provider errors and diagnostics are translated to stable public messages; keys, model diagnostics, internal prompts, paths, and tracebacks are not serialized by the endpoint.
- Direct SQLite inspection found the unavailable-provider test conversation in order as `('user', 'delivered')`, then `('assistant', 'fallback')`, with no foreign-key violations. The project database remained unchanged with zero rows in all five tables and no foreign-key violations.
- No therapy-conversation reference material was generated. The small system instruction only defines prototype boundaries and prohibits diagnostic, monitoring, emergency-service, and invented-contact claims.
- No dependency was added or upgraded in Step 9.
- At the end of Step 9, the View still made no API request, so that step alone did not demonstrate chat success/failure or SQLite chat persistence.

## Phase 1 Step 10 View-to-API integration

Commands:

```powershell
npm --prefix frontend run test:unit
npm --prefix frontend run lint
npm --prefix frontend run build
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests -q --basetemp 'backend\.pytest_cache\tmp-step10'
& 'backend\.venv\Scripts\python.exe' -c "import sqlite3; p='file:backend/models/data/cornerstone.db?mode=ro'; c=sqlite3.connect(p, uri=True); names=['users','login','conversations','chat_logs','exercise_sessions']; print({n:c.execute('SELECT COUNT(*) FROM '+n).fetchone()[0] for n in names}); print('foreign_key_violations', c.execute('PRAGMA foreign_key_check').fetchall()); c.close()"
```

Uvicorn and Vite were also started on `127.0.0.1:8000` and `127.0.0.1:5173` for one browser attempt, then both task-started processes were stopped.

Observed results:

- Eighteen frontend unit tests passed. They cover the deterministic skill calculations plus shared-envelope parsing, public error mapping, transport failure behavior, exact user/exercise/chat request payloads, demo-user creation/recovery/stale-ID replacement, and completed/unsaved exercise persistence.
- The View now resolves a fictional demo user through user CRUD, stores only its integer identifier in local storage, and exposes a retryable server-connection state without claiming authentication.
- Breathing and grounding create active exercise sessions and send completed or exited results with browser-measured duration and last visible step. Failed saves are labeled unsaved or error while the local exercise remains usable.
- Chat loads the newest saved conversation, sends new or continued messages through the bounded chat endpoint, displays mock/provider mode and saved fallback state, reloads server history after a failed request, and retains the failed draft for retry.
- History retrieves newest-first exercise sessions and all conversation messages. Account updates the fictional public display name. No View file imports Python or accesses SQLite.
- Vite's local proxy sends `/api` to `127.0.0.1:8000`, while `VITE_API_BASE_URL` remains available for another deployment arrangement.
- Frontend lint passed. Vite 8.3.4 built 58 transformed modules successfully. All 22 backend tests passed unchanged. No dependency was added or upgraded.
- The in-app browser attempted `http://127.0.0.1:5173/` and returned `net::ERR_CONNECTION_TIMED_OUT`. Therefore no click, timed-skill, route-exit, provider-failure, reload-persistence, responsive-layout, focus-order, or accessibility behavior is claimed as browser-observed evidence.
- Read-only SQLite inspection after the unreachable browser attempt found zero rows in `users`, `login`, `conversations`, `chat_logs`, and `exercise_sessions`, with no foreign-key violations. This correctly confirms that the failed browser connection did not create evidence data; it does not prove View-to-SQLite persistence.
- Final crisis-support content is still deferred. The direct `/support` route and persistent link remain independent of the request modules, but their rendered availability has not been browser-observed.

## Phase 1 Step 11 built-in-browser and SQLite vertical slice

Commands and tools:

```powershell
npm --prefix frontend run dev -- --host 0.0.0.0 --port 5173
& 'backend\.venv\Scripts\python.exe' -u -m uvicorn backend.controllers.api.app:app --host 0.0.0.0 --port 8000
npm --prefix frontend run test:unit
npm --prefix frontend run lint
npm --prefix frontend run build
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests -q --basetemp 'backend\.pytest_cache\tmp-step11'
```

The ChatGPT built-in browser operated the running Vue View. Python's `sqlite3` module then opened `cornerstone.db` in URI read-only mode and queried the resulting fictional records plus `PRAGMA foreign_key_check`.

Observed results:

- The built-in browser reached Vue and FastAPI when both servers ran with approved local-host access outside the managed command sandbox. Uvicorn logs recorded the browser's user, exercise, chat, and history requests with successful HTTP statuses.
- One complete 5-4-3-2-1 run visibly advanced through all five ordered prompts and ended as `COMPLETED`, showing `30.1 seconds` and “Notice one thing you can taste.” SQLite session `1` matched it with `30090` measured milliseconds and `last_step = 'taste_1'`.
- A second run advanced to “Notice four things you can feel,” then used **Leave exercise**. The View showed `EXITED`, `6.4 seconds`, and that last visible prompt. SQLite session `2` matched it with `6384` milliseconds and `last_step = 'feel_4'`.
- The fictional mock-chat input produced the deterministic Cornerstone response in `mock` mode. History displayed the completed and exited sessions plus the ordered user/assistant conversation. SQLite contained one fictional user, one conversation, and two delivered chat rows with matching content and order.
- FastAPI was stopped while Vue remained running. Opening Chat showed a public unreadable-response error; submitting a fictional follow-up exposed **Retry message** and **Reload saved messages** without disabling navigation. The failed transport attempt created no additional chat row.
- During that outage, the persistent **Crisis support information** link opened `/support` without an API call. This verifies route independence, not final resource content; the page still states that resource details require approval.
- After restarting FastAPI, History reloaded the same two exercise sessions and conversation, demonstrating process-restart persistence through the running interface. Read-only SQLite inspection found no foreign-key violations.
- The walkthrough exposed a real grounding-template defect: the outcome card's `v-else` was attached to persistence status instead of exercise status, so an outcome appeared during an active run and disappeared after a successful save. It was revised to render only when `exerciseStatus !== 'active'`; the same browser then showed the correct completed and exited outcomes.
- A dark-mode screenshot exposed low-contrast assistant text on a light chat bubble. `ChatMessage.vue` now assigns an explicit dark foreground to assistant messages, and the corrected browser screenshot showed readable text.
- After the two fixes, the browser console contained no warnings or errors. Eighteen frontend tests, frontend lint, the 58-module production build, and all 22 backend tests passed. No dependency was added or upgraded.
- The fictional evidence rows remain in the ignored project database for review. They are not seed data and are not committed.

## Phase 1 Step 12 paced breathing and model-failure evidence

The existing Vue and default mock FastAPI servers remained running for the breathing checks. FastAPI was then restarted temporarily with the original provider selected and its credential/model variables absent, producing a deterministic configuration failure before any provider network call. After verification, FastAPI was restored to default mock mode. Step 13 subsequently replaced that provider adapter with OpenAI without changing the public failure contract.

Observed results:

- The browser started paced breathing with the keyboard-equivalent toggle. A midpoint observation showed cycle 4 at `33.5 seconds`; the deterministic sequence then reached `Sequence complete`, six cycles, and `60.0 seconds` without user intervention.
- SQLite exercise session `8` matched the completion with `skill = 'paced_breathing'`, `status = 'completed'`, `planned_duration_ms = 60000`, `measured_active_duration_ms = 60000`, and `last_step = 'exhale_cycle_6'`.
- A second browser run was stopped early. The View showed `Breathing stopped at 6.2 seconds` and a saved-state confirmation. SQLite session `9` matched it as `exited`, `6250` measured milliseconds, and `last_step = 'exhale_cycle_1'`.
- In intentionally incomplete provider mode, the browser submitted a fictional scenario and received the public `model_unavailable` message plus a visible **Saved fallback** assistant response. **Retry message**, **Reload saved messages**, navigation, breathing, grounding, history, and the persistent support link remained available.
- The browser opened `/support` immediately after the model failure, establishing that this direct View route does not depend on successful model output. The placeholder content is still not approved final crisis-resource content.
- Read-only SQLite inspection found each failed-provider user message saved as `delivered`, followed by an assistant row with `delivery_status = 'fallback'`. `PRAGMA foreign_key_check` returned no violations.
- The first failure run exposed a labeling defect: the page retained `Provider mode: mock` after a provider failure because mode was updated only on success. `ChatPage.vue` now changes the visible mode to `unavailable` in the error path. A repeated incomplete-provider browser run displayed `PROVIDER MODE: UNAVAILABLE` with the fallback and retry controls.
- No live provider call was attempted, no key was read or displayed, and no reference conversations were invented.
- After the label fix, eighteen frontend tests, frontend lint, the 58-module production build, and all 22 backend tests passed. The browser console contained no warnings or errors.
- FastAPI and Vue were returned to the normal default-mock development configuration and left running at the user's request.

## Phase 1 Step 13 OpenAI provider migration

Commands:

```powershell
& 'backend\.venv\Scripts\python.exe' -m pip install -r backend\requirements.txt
& 'backend\.venv\Scripts\python.exe' -m pip uninstall -y google-genai
& 'backend\.venv\Scripts\python.exe' -m pip check
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests -q --basetemp=backend\.pytest-tmp-openai
npm --prefix frontend run test:unit
npm --prefix frontend run lint
npm --prefix frontend run build
```

Observed results:

- The official `openai` 3.36.1 SDK replaced `google-genai` in `backend/.venv` and `backend/requirements.txt`; `pip check` reported no broken requirements.
- The adapter uses `client.responses.create`, passes the controller-owned system instruction, preserves ordered user/assistant turns, requests at most 256 output tokens, uses a 15-second client timeout, and disables SDK retries.
- OpenAI SDK timeout, connection, and status failures map to the existing controller-owned `model_timeout` or `model_unavailable` behavior. Raw exceptions and credentials remain outside the View contract.
- Configuration recognizes the current ignored `.env` names `OPEN_AI_API_KEY` and `VOICE_BACKEND_MODEL`, plus `OPENAI_API_KEY` and `OPENAI_CHAT_MODEL`. With no explicit `CHAT_PROVIDER`, a present key selects OpenAI and no key selects deterministic mock mode.
- The `.env` file itself was neither edited nor printed. Only variable names were inspected.
- Fake-client tests verify the OpenAI request contract without network access or billing. The backend suite completed with `24 passed`; the initial run's setup errors were caused solely by the managed Windows temp directory, and the same tests passed with a workspace-local `--basetemp`.
- The unchanged View passed all `18` unit tests and lint; Vite built `58` modules successfully.
- No paid OpenAI request was made, so model availability, account billing, response quality, and live error behavior remain unverified.

## Not yet verified

- A deliberately approved live OpenAI contribution using the configured paid account and suitable reference material
- Final approved jurisdiction-specific crisis-support resource content
- Component-level Vue tests, systematic accessibility checks, or a saved walkthrough recording

These items remain evidence or implementation work and must not be inferred from successful unit, controller, lint, or build checks.

## Phase 1 Steps 14–15 Live voice boundary and handoff audit

The next increment added a server-owned OpenAI Live boundary and a microphone-started WebRTC controller to the existing Chat screen. Verification remained entirely mocked: no paid provider request was made and no browser microphone was opened.

Backend behavior now verified by the automated suite:

- `GET /api/voice/config` returns only `configured` or `unconfigured` status plus the bounded session duration. It never returns a credential, model name, provider URL, prompt, tools, or policy.
- `POST /api/voice/sessions` accepts only `sdp_offer`. The current application does not require an owner/profile identifier to begin voice, so one is not accepted or invented for this increment.
- SDP is required to be nonblank, begin with `v=0`, contain an audio media section, contain no NUL byte, and remain at or below 65,536 UTF-8 bytes. Undocumented request fields are rejected.
- The provider request is server-owned: Live uses `gpt-live-1`; Responses delegation uses `VOICE_BACKEND_MODEL`; `store: false`, no tools, `tool_choice: none`, a 15-second timeout, no automatic retry, and explicit client/server data-channel event allowlists are applied.
- Provider exceptions and malformed responses map to sanitized public timeout/unavailable errors. Successful responses expose only the validated session ID, SDP answer, and duration.
- `store: false` is documented only as the Live session-retrieval setting used by this request, not as a general guarantee about provider retention.
- The spoken and delegated prompt layers remain separate and server-side in `backend/controllers/services/voice_service.py` as `LIVE_INSTRUCTIONS` and `DELEGATED_BACKEND_INSTRUCTIONS`. The static `/support` route remains outside model control.

Frontend behavior now verified with mocked MediaDevices, RTCPeerConnection, audio, data-channel, and API implementations:

- Voice begins only after the person chooses **Start voice**. The controller requests `getUserMedia({ audio: true, video: false })`, creates the `oai-events` data channel before the offer, sets the local offer, waits for ICE gathering, posts the SDP to FastAPI, and applies the answer.
- The interface reports permission, connecting, active, muted, closing, closed, and error states. It reports active only after receiving `session.started`.
- Permission denial, missing microphone, connection failure, and provider failure preserve the independent text-chat controls. Blocked autoplay exposes **Enable assistant audio**, which retries `audio.play()` from a user gesture.
- Stop, provider close, timeout, error, component unmount, and superseded-start paths clear timers and handlers, close the data channel/peer connection, stop local tracks, pause the remote audio element, and clear its stream.
- Audio and voice transcripts are not written to SQLite in this increment.

Current audit commands run on 2026-10-26:

```powershell
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests -q --basetemp 'backend\.pytest_cache\handoff-2026-10-26'
Set-Location frontend
node --test tests\*.test.js
npx oxlint .
npx eslint . --no-cache
npm run build
& '..\backend\.venv\Scripts\python.exe' -m pip check
```

Observed results:

- The backend suite completed with `40 passed in 5.12s`.
- The frontend suite completed with `23` tests passed and `0` failed, including the mocked voice lifecycle checks.
- Non-fixing Oxc and ESLint checks exited successfully without output.
- Vite 8.3.4 built `60` modules successfully in `1.45s`.
- `pip check` reported no broken requirements.
- Read-only inspection of `backend/models/data/cornerstone.db` found `2` users, `0` login rows, `1` conversation, `6` chat rows, and `9` exercise sessions. Exercise outcomes were paced breathing: `2` completed and `4` exited; sensory grounding: `2` completed and `1` exited. Chat rows were `3` delivered user messages, `1` delivered assistant message, and `2` fallback assistant messages. `PRAGMA foreign_key_check` returned no violations.
- A names-and-presence-only inspection found the ignored environment currently has nonempty `OPEN_AI_API_KEY`, `VOICE_BACKEND_MODEL`, and `VOICE_MAX_SESSION_SECONDS` entries; the aliases `OPENAI_API_KEY`, `OPENAI_CHAT_MODEL`, and explicit `CHAT_PROVIDER` were absent. No value was printed or changed. Loading this environment can therefore select paid OpenAI text and voice paths; a future live request needs explicit approval.
- Earlier development-process identifiers were no longer available when checked. The audit does not claim that FastAPI or Vite is currently running.

Still unverified after Steps 14–15:

- Real microphone permission and denial in the built-in browser
- Real WebRTC negotiation, remote audio playback, interruption, mute/unmute, close, duration expiry, Live event behavior, and autoplay recovery
- A paid `gpt-live-1` session or delegated Responses contribution, including provider availability, account billing, response quality, and provider-side retention behavior
- SQLite inspection after a real voice session to reconfirm that no audio or transcripts were saved
- Component-level Vue tests, systematic accessibility checks, the fifteen-scenario evaluation, final jurisdiction-specific support content, and a saved walkthrough recording

## Phase 1 Step 16 voice lifecycle controls and cleanup

The View voice controller now distinguishes microphone muting from session termination. Mute and Unmute change only the enabled state of microphone audio tracks; they do not pause assistant audio, close the Live session, or end provider usage. End stops microphone tracks immediately, sends no more than one `session.close`, waits briefly for `session.closed`, and then closes playback, timers, the data channel, and the peer connection. If SDP arrives after End while the bounded close wait is active, the answer is applied only to send `session.close`; it does not restore active state or a duration timer.

Focused mocks cover duplicate Start, repeated End, late SDP, duration expiry, component unmount, route navigation, page exit, the independent crisis-support action, and a fresh set of media/WebRTC resources for the next conversation. The support link announces cleanup before navigation, while route-leave and unmount cleanup remain independently idempotent. Audio and transcript persistence were not added.

Commands run on 2026-10-26:

```powershell
Set-Location frontend
node --test tests\voiceSession.test.js
node --test tests\*.test.js
npx oxlint .
npx eslint . --no-cache
npm run build
```

Observed results:

- The focused voice file completed with `13` passing tests and `0` failures.
- The full frontend suite completed with `32` passing tests and `0` failures.
- Non-fixing Oxc and ESLint checks exited successfully without output.
- Vite 8.3.4 built `61` modules successfully.
- No provider request, microphone permission, remote audio, billing behavior, or database write was exercised. These are mocked lifecycle results only.

## Phase 1 Step 17 transient Live transcript bubbles

The Chat View now displays allowlisted GPT-Live input/output transcript deltas in the same visual message chain as persisted text chat without changing the persistence contract. Assistant and user fragments grow their respective bubbles as timestamped deltas arrive. User speech marks the current assistant bubble interrupted, and later assistant speech starts a new bubble. Per-speaker timeline handling keeps overlapping speech independently updateable and routes late fragments to the earlier matching bubble. A bounded same-speaker gap creates a new display bubble because GPT-Live transcript deltas do not include item identifiers or a completed-turn event.

The transcript reducer is framework-free and accepts only nonempty strings of at most 8,000 characters with finite nonnegative `start_ms`/`end_ms` values in order. It preserves accepted fragments exactly. The WebRTC controller generation-guards all incoming events, ignores transcript data after End, finalizes visible bubbles on End/close/error, and clears the transient transcript only for an accepted new Start. Duplicate Start retains the active transcript, while a stale data-channel callback cannot update a later session. Voice messages remain in View memory, are not sent through the chat API, and are not stored in SQLite.

Commands run on 2026-10-27:

```powershell
Set-Location frontend
node --test tests/liveTranscript.test.js tests/voiceSession.test.js
npm run test:unit
npx oxlint .
npx eslint . --no-cache
npm run build
Set-Location ..
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests\test_voice_api.py -q --basetemp 'backend\.pytest_cache\voice-transcript-tmp'
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests -q --basetemp 'backend\.pytest_cache\live-transcript-all'
& 'backend\.venv\Scripts\python.exe' -m pip check
git diff --check
```

Observed results:

- The focused transcript/lifecycle run completed with `24` passing tests and `0` failures.
- The focused backend voice contract completed with `16` passing tests and `0` failures; it now explicitly pins the five allowed server event types, including both transcript deltas.
- The full frontend suite completed with `44` passing tests and `0` failures.
- The full backend suite completed with `40` passing tests and `0` failures.
- Non-fixing Oxc and ESLint checks exited successfully without output.
- Vite 8.3.4 built `62` modules successfully.
- `pip check` reported no broken requirements, and `git diff --check` reported no whitespace errors.
- No provider request, microphone access, audio playback, paid usage, application-database write, or browser transcript rendering was exercised. The transcript and lifecycle results are focused mocks plus a production compile, not live-provider evidence.

Still unverified after Step 17:

- Real microphone and WebRTC behavior, including the provider's actual transcript timing and accuracy
- Visual interruption/overlap behavior in a browser receiving real Live events
- Remote playback, autoplay recovery, Mute/Unmute, End, and microphone release against a paid session
- Read-only SQLite inspection after that deliberately approved live session

## Phase 1 Step 18 past conversation save/load

The existing persistence model was retained. A `conversations` row stores `id`, `user_id`, `created_at`, and `updated_at`; actual ordered message roles/content/delivery states remain in related `chat_logs` rows. Typed messages already save immediately through `POST /api/chat/messages`, which creates a conversation when `conversation_id` is null and continues one when an owned identifier is supplied.

The View now exposes that persistence as a past-conversation workflow. History derives a bounded label from the first user message, shows message count/update time, and links to Chat with the selected identifier. Chat accepts only positive integer query identifiers found in the active demo user's conversation list, loads that conversation's messages, and continues it on subsequent sends. New conversation clears the current selection, ends and clears transient voice UI if necessary, and lets the existing endpoint create a new persistent record on first send. No LLM access to past conversations, schema migration, dependency change, or separate Save endpoint was added.

Commands run on 2026-10-27:

```powershell
Set-Location frontend
npm run test:unit
npx oxlint .
npx eslint . --no-cache
npm run build
Set-Location ..
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests -q --basetemp 'backend\.pytest_cache\past-conversations'
```

Observed results:

- The frontend suite completed with `49` passing tests and `0` failures, including query parsing, explicit saved selection, unavailable selection, newest-default behavior, fresh-conversation selection, and transient-caption clearing.
- Non-fixing Oxc and ESLint checks exited successfully without output.
- Vite 8.3.4 built `63` modules successfully.
- The backend suite completed with `40` passing tests and `0` failures, including the existing persisted new/continued conversation and history contracts.
- No dependency, schema, provider, microphone, or paid-call change was made.
- Browser clicking and a new read-only SQLite inspection were not performed in this automated pass; the persistence controller/API behavior is covered by existing backend tests, while the new routing helpers are unit-tested and the Vue integration production-builds successfully.

## Phase 1 Step 19 OpenAI-only text-chat runtime

Production text chat no longer contains or selects a deterministic success response. `build_chat_provider` always creates the OpenAI Responses adapter, including when credentials are absent. Incomplete configuration therefore preserves the user message and fallback record and returns the existing recoverable `model_unavailable` response; it cannot silently appear successful. The obsolete `CHAT_PROVIDER=mock` setting has no runtime effect. Repeatable tests continue to inject small provider doubles directly through the application/service boundary.

The server-owned text instruction was aligned with the documented coursework boundary: fictional scenarios, calm and concise language, self-reported facts only, no diagnosis/therapy/monitoring claims, one follow-up question at most, no invented crisis resources, and application ownership of exercise workflow. The adapter passes bounded multi-turn `user`/`assistant` input to the configured model, requests at most 256 output tokens, uses a 15-second timeout with retries disabled, and sets `store: false`. The View now describes the OpenAI connection instead of presenting mock mode as normal behavior.

Commands run on 2026-10-27:

```powershell
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests\test_chat_service.py backend\tests\test_api.py -q --basetemp 'backend\.pytest_cache\openai-chat-focused-final'
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests -q --basetemp 'backend\.pytest_cache\openai-chat-all-final'
& 'backend\.venv\Scripts\python.exe' -m pip check
Set-Location frontend
npm run test:unit
npx oxlint .
npx eslint . --no-cache
npm run build
```

Observed results:

- The focused text-chat controller/API run completed with `21` passing tests and `0` failures.
- The full backend suite completed with `42` passing tests and `0` failures.
- The full frontend suite completed with `49` passing tests and `0` failures.
- Non-fixing Oxc and ESLint checks exited successfully without output.
- Vite 8.3.4 built `63` modules successfully.
- `pip check` reported no broken requirements.
- No OpenAI network request, paid usage, browser send, or response-quality evaluation was performed. The API request evidence comes from a fake SDK client, not a live model.

Still unverified after Step 19:

- One deliberately approved live text request using the configured key/model, including provider availability, billing, latency, response quality, and provider-side handling beyond the request's `store: false` setting
- The fifteen-scenario language-quality and safety evaluation required before claiming that the prompt behavior is suitable
- Integration of `backend/models/data/intents.json`; its provenance and suitability still require review, so it is not sent to the model
- Browser confirmation after restarting the currently running FastAPI process with the intended `.env`

## Phase 1 Step 20 supplied text-chat instruction

The user-supplied Cornerstone instruction is stored verbatim in `backend/controllers/services/chat_prompt.py` and imported by the OpenAI text adapter. It remains controller-owned and never enters the View or an API response. Each Responses request supplies it through the top-level `instructions` field while bounded user/assistant history remains separate `input`. The existing 256-token output bound, `store: false`, timeout, retry, persistence, and sanitized-failure contracts are unchanged. Live voice continues to use its separately reviewed delivery/delegation prompts.

Commands run on 2026-10-27:

```powershell
& 'backend\.venv\Scripts\python.exe' -c "from pathlib import Path; from backend.controllers.services.chat_prompt import SYSTEM_INSTRUCTION; source=Path(r'C:\Users\Owner\.codex\attachments\5761bf1c-2d5b-4cad-9ddf-06c726d10f50\Pasted text.txt').read_text(encoding='utf-8'); print('EXACT_MATCH', SYSTEM_INSTRUCTION == source); print('PROMPT_CHARS', len(SYSTEM_INSTRUCTION))"
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests\test_chat_service.py -q --basetemp 'backend\.pytest_cache\chat-prompt-focused'
& 'backend\.venv\Scripts\python.exe' -m pytest backend\tests -q --basetemp 'backend\.pytest_cache\chat-prompt-all'
& 'backend\.venv\Scripts\python.exe' -m pip check
git diff --check
```

Observed results:

- The source comparison reported `EXACT_MATCH True` for all `13,872` prompt characters.
- The focused text-provider suite completed with `11` passing tests and `0` failures.
- The full backend suite completed with `42` passing tests and `0` failures.
- `pip check` reported no broken requirements, and `git diff --check` reported no whitespace errors.
- No OpenAI response request, paid usage, frontend behavior, voice behavior, or prompt-quality evaluation was exercised.

Still unverified after Step 20:

- Live model adherence to the supplied instruction and the required fifteen-scenario language/safety evaluation
- Whether the 256-token output bound is sufficient for every safety-pathway response
- Integration of `backend/models/data/intents.json`, which remains excluded pending provenance and suitability review

## Phase 1 Step 21 optimistic typed-message display

Chat now appends a transient user message to the rendered message list before awaiting `POST /api/chat/messages`. The transient record has a collision-resistant local identifier, a server-compatible timestamp, and `delivery_status: pending`, which is presented as `Sending…` and exposed as busy to assistive technology. A successful response replaces that exact pending entry in place with the persisted user and assistant records. A failed request removes the pending entry before the existing recovery load, so saved fallback records remain authoritative and a second transport failure cannot leave a stale sending indicator.

Commands run on 2026-10-27:

```powershell
Set-Location frontend
node --test tests\optimisticChat.test.js
npm run test:unit
npx oxlint .
npx eslint . --no-cache
npm run build
```

Observed results:

- The focused optimistic-message suite completed with `4` passing tests and `0` failures, covering immediate creation, success reconciliation without duplication, an already-removed pending record, and failure removal.
- The full frontend suite completed with `53` passing tests and `0` failures.
- Non-fixing Oxc and ESLint checks exited successfully without output.
- Vite 8.3.4 built `64` modules successfully, and the running development server accepted HMR updates for Chat and the message component.
- No provider request, database write, or paid usage was initiated by these checks.

Still unverified after Step 21:

- A manual browser send observed under deliberately throttled provider/network latency
- Visual and screen-reader confirmation of the brief `Sending…` state before a fast response arrives
