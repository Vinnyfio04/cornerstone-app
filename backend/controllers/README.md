# Controllers

This directory connects the Vue view layer to the backend model through the documented JSON contract.

- `api/` owns FastAPI routes, request validation, and response serialization.
- `calculations/` owns framework-free deterministic calculations such as breathing phases, duration, and session transitions.
- `services/` coordinates model repositories, calculations, and bounded model-provider adapters.
- `database_controller.py` opens SQLite with foreign-key enforcement, migrates legacy chat rows into conversations without discarding them, and provides CRUD for `User`, `Login`, `Conversation`, `ChatLog`, and `ExerciseSession`.

FastAPI route files should remain thin. They validate HTTP input, call a service, and serialize its result; they do not directly query SQLite or implement timing calculations.
