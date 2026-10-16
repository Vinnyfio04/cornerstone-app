# 04 — Complete Scaffold Verification

Use this prompt for the final non-mutating audit before repository initialization.

```text
Read AGENTS.md, README.md, and relevant project documentation. Work only inside Cornerstone.

Verify without changing source files, dependency declarations, lockfiles, or installed dependencies. Confirm the required root structure; README architecture and reproducible commands; AGENTS boundary, separation, permission, and reporting rules; the backend interpreter location; the exact backend requirements; FastAPI and pytest imports; Python dependency consistency; Node.js and npm paths and versions; the current official Vue Node requirement; Vue and ESLint declarations; lockfile presence and installed-tree consistency; frontend lint; production build; ignore coverage; and preservation of manifests and lockfiles.

Inspect non-generated backend and frontend files to confirm that no project-specific route, domain function, backend test, API integration, or interface has been implemented beyond an allowed framework starter. Distinguish generated development-tool behavior from an application API connection.

Classify every result as passed, failed, partial, or not applicable. Report advisory engine warnings and other partial readiness without treating successful checks as failures. Use hashes or equivalent evidence to show that verification did not alter protected project files. Report every verification command and stop.
```

