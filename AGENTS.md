# Cornerstone Agent Rules

## Project boundary and preparation

- Work only inside cornerstone.
- Read `AGENTS.md` and `README.md` before making changes.
- Ask targeted follow-up questions when missing information would materially change the work.

## Architecture

- Keep framework-free Python domain logic separate from FastAPI routes.
- Keep frontend presentation separate from backend-request code.
- Communicate between Vue and FastAPI through a documented JSON contract.

## Dependencies and permissions

- Do not install Python or JavaScript project dependencies globally.
- Do not add, remove, or upgrade dependencies without explaining why.
- Ask before any machine-level installation, destructive action, or scope expansion.
- Never use `sudo` automatically or bypass managed-computer policies.
- Stop only processes started for the current task.

## Reporting

- Report commands run, files changed, checks performed, and anything not verified.

