# Cornerstone MVC Contracts

## Scope and source

No CSV files are present in the repository. The initial model is therefore derived from the requested `users`, `login`, and `chat_logs` tables plus the `conversations` and `exercise_sessions` records required for chat grouping, measured exercise duration, completion, and early exit. Any future CSV import must be analyzed and mapped explicitly before changing these fields or relationships.

## MVC ownership

- **Model — `backend/models/`:** entity objects, relationships, and the model-owned `data/` directory. Models contain no HTTP or UI behavior.
- **View — `frontend/`:** Vue source, screens, components, CSS, assets, frontend request adapters, and build/runtime configuration. The View never reads SQLite directly.
- **Controller — `backend/controllers/`:** database access and CRUD, FastAPI routes, deterministic calculations, application services, and adapters that translate model results into the View's JSON contract.

Dependencies move in one direction: View → Controller → Model. A Model does not call a Controller or View. A Controller does not import Vue code. The View knows controller JSON shapes, not Python model classes or database rows.

## Model relationships

### `users`

`users.id` is the primary identifier used by the other tables.

- `id`: integer primary key
- `display_name`: required display label
- `preferences_json`: JSON object reserved for explicit, user-correctable preferences
- `created_at`, `updated_at`: SQLite timestamps

### `login`

Each user may have at most one login record. `login.user_id` is unique and references `users.id` with cascade deletion. `username` is unique and case-insensitive. `password_hash` accepts an already-hashed credential only; plaintext passwords must never cross the database-controller contract or be stored.

### `conversations`

A user may have many conversations. Each conversation stores its user reference, creation time, and update time. Deleting a user cascades to that user's conversations. Deleting a conversation cascades to its chat-log rows.

### `chat_logs`

A user may have many chat-log rows grouped by conversation. `chat_logs.user_id` references `users.id`, and `chat_logs.conversation_id` references `conversations.id`; both use cascade deletion. Increasing `id` values preserve insertion order within a conversation. Roles are limited to `user`, `assistant`, and `system`; delivery states are `delivered`, `fallback`, and `failed`.

### `exercise_sessions`

A user may have many exercise sessions. Each row contains:

- `skill`: `paced_breathing` or `sensory_grounding`;
- `status`: `active`, `completed`, or `exited`;
- `planned_duration_ms`: the planned active duration when applicable;
- `measured_active_duration_ms`: active browser-measured duration;
- `started_at`, `ended_at`: server timestamps;
- `last_step`: the last breathing phase/cycle or grounding step shown.

Deleting a user cascades to the user's exercise sessions. Controllers validate legal state transitions; the View cannot mark an unknown session complete.

The history exists to support visible history and future, explicit personalization. No automatic mental-state inference or personalization behavior is implemented by this schema.

## Model–Controller contract

`DatabaseController` accepts a filesystem path, creates the approved schema, and opens each transaction with `PRAGMA foreign_keys = ON`.

- `create_*` returns the created frozen dataclass.
- `get_*` returns the matching dataclass or `None`.
- `list_*` returns dataclasses ordered by primary key.
- `update_*` returns the updated dataclass or `None` when the identifier does not exist.
- `delete_*` returns `True` when one row was deleted and `False` otherwise.
- `check_references()` returns foreign-key violations; an empty list means SQLite found none.
- SQLite constraint failures propagate as `sqlite3.IntegrityError` for a service or API controller to map to a stable external error.

Controllers must return model dataclasses or documented controller result objects, never live SQLite connections, cursors, or `sqlite3.Row` objects.

## Controller–Controller contract

Business controllers may call the database controller or another controller through public methods only. Calls use typed Python inputs and return model dataclasses or documented result objects. Controllers must not reach into another controller's connection, private helper, or provider implementation. Exceptions must be caught and translated at the controller boundary responsible for the next layer.

## View–Controller JSON contract

The health, user CRUD, exercise-session, exercise-history, chat-message, conversation-history, message-history, and voice-session FastAPI endpoints are implemented. Every endpoint uses JSON and the following stable envelope:

```json
{
  "data": {},
  "error": null
}
```

Failures use:

```json
{
  "data": null,
  "error": {
    "code": "stable_machine_code",
    "message": "Short user-facing explanation"
  }
}
```

The View may send only fields documented for a specific endpoint and must treat unknown response fields as optional. Controllers validate inputs, map database constraints to stable error codes, and serialize timestamps as strings. Credentials, password hashes, internal prompts, provider secrets, SQLite paths, and tracebacks must never appear in View responses.

The Phase 1 endpoint-specific request and response fields are defined below. The frontend must not depend on an endpoint until that endpoint is implemented and verified.

## Phase 1 endpoint contracts

All endpoints are rooted at `/api`. Successful responses use the shared `data`/`error` envelope. Fields not listed here must not be required from the View.

### Health

`GET /api/health`

```json
{
  "data": {
    "status": "ok",
    "chat_mode": "mock",
    "model_ready": false
  },
  "error": null
}
```

The response may report readiness but must not expose keys, prompts, paths, or provider diagnostics.

### User CRUD

`POST /api/users`

```json
{
  "display_name": "Fictional Demo User",
  "preferences": {}
}
```

`GET /api/users/{user_id}` has no body.

`PATCH /api/users/{user_id}` accepts either or both fields:

```json
{
  "display_name": "Updated Fictional User",
  "preferences": {
    "preferred_skill": "paced_breathing"
  }
}
```

`DELETE /api/users/{user_id}` returns:

```json
{
  "data": {
    "deleted": true
  },
  "error": null
}
```

Public user responses contain `id`, `display_name`, `preferences`, `created_at`, and `updated_at`. Login credentials and password hashes are never included. Active registration/login is outside Phase 1.

### Start an exercise session

`POST /api/exercise-sessions`

```json
{
  "user_id": 1,
  "skill": "paced_breathing",
  "planned_duration_ms": 60000
}
```

Grounding may use `planned_duration_ms: null` when treated as self-paced.

Response data contains `id`, `user_id`, `skill`, `status: "active"`, `planned_duration_ms`, `measured_active_duration_ms: 0`, `started_at`, `ended_at: null`, and `last_step`.

### Finish or exit an exercise session

`PATCH /api/exercise-sessions/{session_id}`

```json
{
  "status": "exited",
  "measured_active_duration_ms": 18420,
  "last_step": "inhale_cycle_2"
}
```

The only Phase 1 terminal statuses are `completed` and `exited`. The controller validates non-negative duration and the transition from `active`. Repeating the same terminal update may return the existing result; changing one terminal state into another is a conflict.

### Exercise history

`GET /api/users/{user_id}/exercise-sessions`

Response data contains a `sessions` array ordered newest first. It does not calculate or claim clinical progress.

### Send a chat message

`POST /api/chat/messages`

```json
{
  "user_id": 1,
  "conversation_id": null,
  "content": "Fictional scenario text"
}
```

When `conversation_id` is null, the controller creates a conversation. The response contains the conversation identifier plus public user and assistant message objects:

```json
{
  "data": {
    "conversation_id": 7,
    "user_message": {
      "id": 21,
      "role": "user",
      "content": "Fictional scenario text",
      "delivery_status": "delivered",
      "created_at": "timestamp"
    },
    "assistant_message": {
      "id": 22,
      "role": "assistant",
      "content": "Bounded response",
      "delivery_status": "delivered",
      "created_at": "timestamp"
    },
    "chat_mode": "mock"
  },
  "error": null
}
```

On provider failure, the user message remains saved and an assistant failure or fallback record is saved. The response uses `model_unavailable` or `model_timeout`; it may include a deterministic public fallback message but never raw provider output or a traceback.

The chat service accepts at most 2,000 characters per user message, retains at most 12 recent messages and 8,000 context characters, requests at most 256 output tokens, stores at most 4,000 assistant-response characters, and configures a 15-second provider timeout with SDK retries disabled. Mock mode is deterministic. OpenAI mode accepts server-side `OPEN_AI_API_KEY` or `OPENAI_API_KEY` and resolves the model from `OPENAI_CHAT_MODEL` or the existing `VOICE_BACKEND_MODEL`; none of these values is returned to the View. When no provider is explicit, a present key selects OpenAI and no key selects mock. The current system instruction is a small behavioral boundary, not supplied therapy-conversation material. No missing reference conversations are generated.

### Conversation history

`GET /api/users/{user_id}/conversations` returns conversation summaries ordered newest first.

`GET /api/conversations/{conversation_id}/messages` returns public message objects ordered by increasing identifier.

### Voice configuration and session exchange

`GET /api/voice/config` returns only public readiness and the server-owned duration:

```json
{
  "data": {
    "status": "configured",
    "duration_seconds": 300
  },
  "error": null
}
```

`POST /api/voice/sessions` accepts only a bounded WebRTC SDP offer:

```json
{
  "sdp_offer": "v=0..."
}
```

Its successful response contains only the validated Live session identifier, WebRTC SDP answer, and duration:

```json
{
  "data": {
    "session_id": "live_123",
    "sdp_answer": "v=0...",
    "duration_seconds": 300
  },
  "error": null
}
```

The View creates an `oai-events` data channel before its offer, waits for ICE gathering, and reports `active` only after `session.started`. Mute changes only local audio-track enablement; it does not stop assistant playback or the provider session. End stops microphone tracks immediately, sends at most one `session.close` when possible, waits briefly for `session.closed`, and then closes audio, timers, the data channel, and the peer connection. Late SDP answers after End may be applied only to send the close event and must not reactivate stale UI. Duplicate Start and repeated End are ignored. Duration expiry, route navigation, page exit, component unmount, and the independent support action clean up the current session, and a later Start uses fresh media and peer resources. The API key, models, prompts, provider URL, tools, and policy remain server-owned. The View must reject or ignore no server configuration because its request schema permits only `sdp_offer`. Voice audio and transient transcript events are not written to SQLite in this increment. The static `/support` route remains View-owned and independent of voice state or model behavior.

### Stable Phase 1 error codes

- `validation_error` — invalid or missing View input;
- `not_found` — unknown user, conversation, message, or exercise session;
- `conflict` — uniqueness or illegal state-transition conflict;
- `model_unavailable` — model mode is not configured or provider call failed;
- `model_timeout` — provider deadline elapsed;
- `database_error` — persistence failed without exposing internal details.
- `voice_unavailable` — voice configuration, provider exchange, or provider response is unavailable;
- `voice_timeout` — the Live session-creation deadline elapsed.

HTTP status codes and JSON error codes must be mapped in the API controller and covered by tests. The `/support` route is View-owned static content and has no backend contract.

## View request implementation

`frontend/src/api/client.js` is the only general HTTP adapter. It validates the shared `data`/`error` envelope, converts controller errors to `ApiError`, and maps failed transport or non-JSON responses to stable View-safe errors. `users.js`, `sessions.js`, `chat.js`, and `voice.js` map screen actions to the endpoint-specific fields above. During local Vite development, `/api` is proxied to `http://127.0.0.1:8000`; a deployment may instead provide `VITE_API_BASE_URL`.

The View stores only the fictional demo user's integer identifier in browser local storage. It resolves the complete public user through `GET /api/users/{id}`, replaces a stale identifier through `POST /api/users`, and never stores credentials. Exercise persistence converts the View's camel-case result object into the controller's snake-case payload. Chat and history consume only public serialized messages and sessions. If a request fails, the deterministic skill remains available and the View presents retry or unsaved state rather than reading SQLite directly.
