# Cornerstone frontend

This directory is the complete MVC View for Cornerstone. It is a Vue 3 and
Vite application with seven routes: Home, Grounding, Chat, Check-in Calendar,
History, Account, and independent Crisis Support. The View communicates with
FastAPI only through the request modules in `src/api/`; it never imports
backend Python or accesses SQLite directly.

The Home page owns the browser-timed 4-second inhale/6-second exhale exercise.
A CC0 wind-and-chime ambience starts with the exercise and stops when the
exercise stops. Grounding owns the deterministic 5-4-3-2-1 flow. Calendar
supports multiple check-ins per present or past date, editable saved entries,
preset and custom feelings/colors, and up to three date markers. Chat supports
persisted text conversations and optional transient Live voice sessions.

## Setup

From the repository root, install the locked project-local dependencies:

```powershell
npm --prefix frontend ci
```

No frontend dependency should be installed globally.

## Development and verification

Run the development server from the repository root:

```powershell
npm --prefix frontend run dev
```

Vite serves the View at `http://127.0.0.1:5173` by default and proxies relative
`/api` requests to the local FastAPI server. A deployment may set
`VITE_API_BASE_URL`.

Run the repeatable frontend checks with:

```powershell
npm --prefix frontend run test:unit
npm --prefix frontend run lint
npm --prefix frontend run build
```

See `../README.md` for complete project setup and `../docs/mvc-contracts.md` for
the View-to-controller JSON contract.
