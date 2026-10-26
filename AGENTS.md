# Cornerstone Agent Rules

## Project boundary and preparation

- Work only inside cornerstone.
- Read `AGENTS.md` and `README.md` before making changes.
- Ask targeted follow-up questions when missing information would materially change the work.

## Architecture

- Follow MVC with `backend/models/`, `backend/controllers/`, and the complete `frontend/` directory as the View.
- Keep model entities and the model-owned `data/` directory under `backend/models/`; models must not import controllers or frontend code.
- Keep the database controller, FastAPI code, calculations, and other business controllers under `backend/controllers/`.
- Controllers may call other controllers only through documented inputs, outputs, and error behavior.
- Keep all Vue screens, components, CSS, assets, and frontend runtime files inside `frontend/`; do not add a nested MVC `views/` directory.
- Keep UI and CSS in the View. The View must never access SQLite or import backend Python modules directly.
- Communicate between the View and controllers through the JSON contract documented in `docs/mvc-contracts.md`.
- Keep framework-free calculations separate from FastAPI route files even though both belong to the controller layer.

## Dependencies and permissions

- Do not install Python or JavaScript project dependencies globally.
- Do not add, remove, or upgrade dependencies without explaining why.
- Ask before any machine-level installation, destructive action, or scope expansion.
- Never use `sudo` automatically or bypass managed-computer policies.
- Stop only processes started for the current task.

## Reporting

- Report commands run, files changed, checks performed, and anything not verified.

