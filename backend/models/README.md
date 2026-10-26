# Models

This directory owns Cornerstone's data and persistence-facing domain representation.

- `data/` holds local SQLite runtime files. Database files are ignored by Git.
- `entities.py` defines framework-free `User`, `Login`, `Conversation`, `ChatLog`, and `ExerciseSession` records.
- `backend/controllers/database_controller.py` owns migration-safe SQLite schema initialization and CRUD for these models.

The model must not import FastAPI, Vue code, or controller modules. It exposes plain Python objects to controllers.
