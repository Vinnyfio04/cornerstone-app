# View pages

These files are the seven routed Phase 1 screens inside the MVC View. Home and Grounding own deterministic browser interactions. Calendar, Chat, History, and Account call dedicated modules under `src/api/`; Calendar supports multiple editable check-ins on present or past dates and keeps future dates read-only. Chat also presents the optional microphone-started controller from `src/voice/` while leaving text chat independent. The Support screen is deliberately View-owned and independent of API or model availability, with sourced U.S./Pennsylvania contact information. The bounded live text comparison is recorded in `docs/live-model-results.json`; live voice and systematic accessibility review remain unverified.

The full `frontend/` directory remains the View; `pages/` is only an organizational folder for screen-level Vue components, not a separate MVC layer.
