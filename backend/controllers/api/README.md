# Controller API

- `app.py` provides the FastAPI application factory and local application object.
- `routes.py` implements the health, user, exercise-session, chat-message, read-only history, voice-configuration, and voice-session routes.
- `schemas.py` rejects undocumented request fields and validates the documented inputs.
- `responses.py` owns the stable `data`/`error` envelope and public entity serialization.

Database-backed routes call controllers through their public contracts, the chat-message route calls `ChatService`, and voice routes call `VoiceService`. Credentials, models, prompts, password hashes, SQLite paths, provider diagnostics, and tracebacks are never serialized to the View.
