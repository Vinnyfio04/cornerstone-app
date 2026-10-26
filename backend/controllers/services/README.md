# Controller services

`chat_service.py` coordinates conversation ownership, ordered persistence, bounded context, provider output, and deterministic fallback records. `chat_provider.py` supplies deterministic mock mode plus a server-configured OpenAI Responses adapter. `voice_service.py` owns bounded `gpt-live-1` WebRTC session creation, separate Live and delegated Responses prompts, configuration readiness, event allowlists, response validation, timeout/error mapping, and the no-tools policy.

These services connect controller behavior to the frontend-facing API; Vue code does not import them directly. Text messages are persisted through `ChatService`; Live audio and transcripts are not persisted in the current voice increment.
