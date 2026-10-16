# Cornerstone

Cornerstone is a new web application project. Its product requirements and feature scope have not yet been defined; this repository currently contains only the bounded initial scaffold and project guidance.

## Architecture

- `backend/` will contain Python backend code. Framework-free domain logic will remain separate from the FastAPI API layer.
- `frontend/` will contain the Vue user interface. Presentation code will remain separate from code that sends requests to the backend.
- `docs/` will contain project documentation, including the documented JSON contract used for communication between Vue and FastAPI.

The backend and frontend environments are project-owned. Python dependencies will be installed only in a virtual environment under `backend/`, and JavaScript dependencies will be installed locally under `frontend/`. Project dependencies must not be installed globally.

## Project documentation

- `docs/assignment_instructions.md` is the internal requirements-alignment source.
- `docs/design-pipeline.md` shows the current and planned project structure, request boundaries, and delivery checkpoints.
- `prompts/` contains the small ordered library of major prompts used to establish and verify the scaffold.
- `handoffs/create-handoff.md` contains prompts for creating and resuming a temporary `handoffs/current.md` state record.

## Setup

Run these PowerShell commands from the project root to reproduce the backend environment on this computer:

```powershell
& 'C:\Users\Owner\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m venv 'backend\.venv'
& 'backend\.venv\Scripts\python.exe' -m pip install -r 'backend\requirements.txt'
```

The first command uses the verified CPython 3.12.14 interpreter. On another computer, replace that absolute path with a verified Python 3.10-or-newer executable. All backend dependencies are installed into `backend/.venv`; none are installed globally. The declared backend dependencies are limited to `fastapi[standard]` and `pytest`.

Install the frontend dependencies from the retained lockfile by running this PowerShell command from the project root:

```powershell
npm --prefix frontend ci
```

The frontend uses the project-local dependencies declared in `frontend/package.json` and locked in `frontend/package-lock.json`; Vue and its tooling are not installed globally.

## Verification

Run these PowerShell commands from the project root to verify the backend environment:

```powershell
& 'backend\.venv\Scripts\python.exe' -c "import pathlib, sys; import fastapi, pytest; assert pathlib.Path(sys.executable).resolve().is_relative_to(pathlib.Path('backend/.venv').resolve()); print(sys.executable); print(f'fastapi {fastapi.__version__}'); print(f'pytest {pytest.__version__}')"
& 'backend\.venv\Scripts\python.exe' -m pip check
```

Run the frontend code-quality and production-build checks from the project root:

```powershell
npm --prefix frontend run lint
npm --prefix frontend run build
```

## Local development

No backend development command is available until a FastAPI application entry point is implemented. Start the Vue development server from the project root with:

```powershell
npm --prefix frontend run dev
```

## TODO

- Define Cornerstone's product purpose and feature requirements.
- Establish and document the Vue-to-FastAPI JSON contract when API requirements are known.
- Record a backend development command after a FastAPI application entry point is implemented.

