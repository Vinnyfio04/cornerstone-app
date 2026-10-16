# 02 — Backend Environment

Use this prompt to establish a reproducible, project-owned backend toolchain without implementing features.

```text
Read AGENTS.md and README.md. Work only inside Cornerstone and inspect backend/ for conflicts before changing anything.

Run a read-only Python preflight first. Report the operating system, every discoverable interpreter and path, whether Python 3.10 or newer is available, and whether a project-owned environment or dependency manifest already exists. Distinguish machine-level tools from project-owned dependencies.

If a compatible interpreter exists, create backend/.venv with it. Create backend/requirements.txt containing only fastapi[standard] and pytest, then install only those declared requirements into backend/.venv. Never install project packages globally and ask before any machine-level change.

Use backend/.venv/Scripts/python.exe for verification. Confirm its resolved path is inside backend/.venv, import FastAPI and pytest, run pip check, and update README.md with exact reproducible setup and verification commands. Do not add routes, domain functions, tests, databases, or frontend code. Report commands, changes, installed-version evidence, and anything not verified, then stop.
```

