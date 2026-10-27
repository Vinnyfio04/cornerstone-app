# Controller services

`chat_service.py` coordinates conversation ownership, ordered persistence, bounded context, provider output, and deterministic fallback records. `chat_prompt.py` owns the reviewed, code-versioned developer instruction for persisted text chat. `chat_provider.py` supplies that instruction to the server-configured OpenAI Responses adapter; production chat has no synthetic-success provider. Focused provider doubles live only in tests. `voice_service.py` owns bounded `gpt-live-1` WebRTC session creation, separate Live and delegated Responses prompts, configuration readiness, event allowlists, response validation, timeout/error mapping, and the no-tools policy.

These services connect controller behavior to the frontend-facing API; Vue code does not import them directly. Text messages are persisted through `ChatService`; Live audio and transcripts are not persisted in the current voice increment.
