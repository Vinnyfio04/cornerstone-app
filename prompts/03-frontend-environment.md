# 03 — Frontend Environment

Use this prompt to establish the minimal project-owned Vue toolchain without implementing a project interface.

```text
Read AGENTS.md and README.md. Work only inside Cornerstone. Inspect frontend/ before changing it and read the current official Vue Quick Start and create-vue workflow.

Verify the installed Node.js and npm versions and paths against Vue's current requirement. Ask before any machine-level installation. If the current official create-vue workflow materially changes the requested choices, explain the difference and stop for approval.

Initialize a minimal JavaScript Vue project directly inside the existing frontend/ directory. Do not create a nested frontend directory or install Vue tooling globally. Omit TypeScript, JSX, Router, Pinia, unit tests, end-to-end tests, formatting options, and experimental release options. Include ESLint and accept only companion tooling automatically required by the current official ESLint workflow; report that tooling explicitly.

Install only dependencies declared by the generated package.json and retain package-lock.json. Run lint and the production build. Update README.md with exact lockfile-based setup, lint, build, and development commands. Do not implement a project-specific interface, connect to FastAPI, or change backend files. Report all commands, generated paths, dependency evidence, warnings, and check results, then stop.
```

