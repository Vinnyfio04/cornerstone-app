# View pages

These files are routed Phase 1 screens inside the MVC View. Home and grounding own deterministic browser interactions; chat, history, and account call dedicated modules under `src/api/`. Chat also presents the optional microphone-started controller from `src/voice/` while leaving text chat independent. The support screen is deliberately View-owned and independent of API or model availability. Final support copy, live-audio verification, and visual refinement remain later work.

The full `frontend/` directory remains the View; `pages/` is only an organizational folder for screen-level Vue components, not a separate MVC layer.
