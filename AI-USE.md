# AI Use

## Development tools

I used OpenAI Codex to inspect the repository, revise documentation, write and review code, and run local checks. In the November 2, 2026 report session, I used a GPT-6-based Codex agent. I do not have an exact model snapshot or desktop app version recorded for that session.

I used PowerShell, Git, Python/pytest, Node's test runner, Oxc, ESLint, and Vite to check the work. These are development and verification tools, not additional conversational models.

I supplied the text-chat instruction retained in `backend/controllers/services/chat_prompt.py`. I used Codex assistance for the bounded scaffold, MVC organization, integration, tests, and documentation as recorded in the saved prompts and verification notes. I reviewed the resulting behavior through tests and the documented browser/database checks. I do not treat generated code or a passing build as proof that every interaction works.

## Application models

I use the OpenAI Python SDK, locally verified as version `3.36.1`, for the application's provider boundary. Text chat uses the server's `OPENAI_CHAT_MODEL`, with `VOICE_BACKEND_MODEL` as a compatibility fallback. I do not publish credentials or assume a particular text model when its identifier is not in the submitted evidence.

I configured the implemented voice boundary with `gpt-live-1` and a separately configured delegated Responses model. I have only mocked verification of voice, so I do not claim a successful live voice session.

I used injected fake providers and mocked browser objects for routine checks. I label these as mocks; they do not establish live language quality, clinical effectiveness, or a successful provider connection. I keep any approved live-model results separate in the evaluation record.

## Earlier work and limits

I reused setup prompts from earlier coursework at the start of this project. I followed the familiar Vue, FastAPI, and SQLite approach and retained Vue starter files. I did not reuse other coursework application code. Codex was the only AI development tool I used.

I completed the approved live text comparison with `gpt-5.6-sol`: seven completed replies within an eight-attempt cap, including one connection failure. I used the application's text instruction, 256-token output limit, disabled retries, and `store=False`. I saved the fictional inputs and outputs in [the live record](docs/live-model-results.json).

## Evidence

- [Curated evidence log](docs/evidence-log.md)
- [Saved major scaffold prompts](prompts/)
- [Design decisions](docs/design_notes.md)
- [Verification history](docs/verification.md)
- [Evaluation and peer-testing procedure](docs/evaluation.md)

I keep credentials, local account records, personal information, and private third-party content out of the submitted evidence.
