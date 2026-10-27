# Cornerstone Design Notes

## Status and intent

These are exploratory product and interaction notes, not finalized requirements or claims of clinical effectiveness. Ideas involving behavioral sensing, personalization, or language-model responses require validation, explicit user control, and alignment with the project's coursework-prototype boundaries before implementation.

## Current design artifact

![Initial basic Cornerstone wireframe](images/initial%20basic%20wireframe.png)

The initial wireframe explores a minimal landing view with entry points for a guided experience and chat, leading into a larger exercise or conversation view. It is an early sketch rather than an approved interface. It does not yet show the independently available support-information route, persistent history, clear exit controls, personalization controls, or failure states; those must be resolved before implementation.

## Phase 1 scope

The reviewed Phase 1 direction is defined in `docs/phase-1-contract.md`. It expands the earlier breathing-only concept into a small navigable framework with three immediately available paths:

1. A hold-to-breathe green circle on the home page, using the four-second inhale and six-second exhale pace.
2. A prominent 5-4-3-2-1 sensory-grounding page that requires no typing.
3. A standard persisted text-chat page using the server-configured OpenAI Responses API adapter, with focused fake providers limited to automated tests.

Six uninterrupted breathing cycles remain the planned 60-second completion point. Releasing earlier records an exit, stops the visual cue immediately, and prominently offers grounding. The browser measures active time; server timestamps and SQLite records support later evidence. Deterministic application code—not the model—owns exercise order, timing, exits, persistence, failures, and support access.

The complete route set also includes saved history, an account/CRUD framework using a fictional demo user, and independent static crisis-support information. The exact page behavior, provider boundary, failure states, and review decisions are in `docs/phase-1-contract.md`; endpoint payloads are in `docs/mvc-contracts.md`.

### Planned SQLite evidence

The minimum persisted records are:

- a conversation row linked to the user with creation/update time;
- user and assistant message rows linked to the conversation, with role, content, creation time, and delivery status such as `delivered`, `fallback`, or `failed`;
- an exercise-session row linked to the user, with skill name, `completed` or `exited` status, planned duration, start/end timestamps, measured active duration, and last cycle/phase or grounding step;
- enough request-status information to distinguish a successful model contribution from a deterministic fallback without storing credentials or hidden provider data.

The exact schema and Vue-to-FastAPI JSON contract must be documented before implementation. Persistence should be inspectable with SQLite queries while the application is stopped and restarted, demonstrating that both conversation and session history survive a process restart.

### Required verification evidence for this slice

Evidence must connect the browser experience to the saved database state:

- complete the six-cycle exercise in the browser and capture the completion state plus the observed duration;
- inspect SQLite to find the matching `completed` session and its conversation/messages;
- restart the app and show the same records through the history interface;
- use a mocked model failure, show the fallback in the browser, confirm the exercise and crisis-support route remain usable, and inspect the saved failure/fallback record;
- leave a second exercise before completion, show the resulting browser state, and inspect the matching `exited` session and partial measured duration;
- complete and leave the sensory-grounding sequence in separate fictional test runs, preserving step order and last-step state;
- open crisis-support information before, during, and after a failed request to demonstrate that the route is independent;
- record commands, screenshots or browser observations, relevant database queries/results, expected versus observed behavior, and anything not verified.

Routine automated checks should use mocked model outcomes. Any live-model check must be clearly labeled and kept separate from deterministic evidence. All scenarios and demonstrations remain fictional.

### Step 11 observed vertical slice

The built-in-browser walkthrough on 2026-10-22 completed sensory grounding, exited a second run at step two, saved a deterministic mock conversation, showed both exercise records and the conversation in History, and showed the same records after restarting FastAPI. A deliberate API outage exposed retry controls while the static `/support` route remained available. Read-only SQLite queries matched the browser state: one fictional user, one completed session, one exited session, one conversation, two delivered chat rows, and no foreign-key violations.

The walkthrough revised two implementation assumptions. First, compiling the Vue template had not established that the exercise and persistence conditionals composed correctly; browser observation found and corrected an outcome-card condition. Second, inherited theme colors were not sufficient for chat bubbles; a dark-mode screenshot found and corrected assistant-message contrast.

### Step 12 remaining deterministic evidence

The built-in browser completed the planned six-cycle paced-breathing sequence at exactly 60 seconds and exited a second run at 6.2 seconds. SQLite stored matching `completed` and `exited` records with phase/cycle last-step values. FastAPI was then run with intentionally incomplete provider configuration: the fictional user message and deterministic fallback were persisted, retry controls remained visible, and `/support` opened directly after the failure. No provider network call was made. The original adapter used for this failure demonstration was replaced by OpenAI in Step 13; the public failure contract is unchanged.

This run found that the provider-mode label incorrectly remained `mock` after a provider configuration failure. The View now reports `unavailable` in the error path, and a repeated browser check confirmed that label alongside the saved fallback. Live paid OpenAI behavior, final support-resource content, the fifteen-scenario evaluation, and systematic accessibility review remain outside this evidence.

### Step 13 OpenAI provider migration

The backend now uses the official OpenAI Python SDK and Responses API. It recognizes the existing ignored `.env` names `OPEN_AI_API_KEY` and `VOICE_BACKEND_MODEL`, plus `OPENAI_API_KEY` and `OPENAI_CHAT_MODEL` aliases. Step 19 removed the production deterministic-response provider and legacy `CHAT_PROVIDER` selection: runtime text chat always targets OpenAI, while incomplete configuration returns the existing recoverable unavailable result. Fake-client tests verify the multi-turn request shape, `store: false`, 256-token output limit, 15-second timeout, disabled retries, server-only key passage, and key prompt boundaries. No paid request was made and no secret value was printed or changed.

### Steps 14–15 Live voice increment

FastAPI now exposes public voice readiness and bounded WebRTC SDP exchange without returning credentials, models, prompts, provider URLs, tools, or policy. The Live layer uses server-owned `gpt-live-1`; Responses delegation requires the separate server-owned `VOICE_BACKEND_MODEL`. The short spoken prompt owns warm, brief delivery, one focused question at a time, backchannels, interruption, and `<|SpawnThinking|>` delegation. The separate backend prompt owns reviewed application scope, self-report versus interpretation, permission before suggesting an activity, honest missing-context handling, and the prohibitions against diagnosis, therapy/treatment claims, medical advice, monitoring claims, or invented record access. Tools are disabled.

The Chat View starts voice only after the microphone action. Its framework-free controller requests audio-only media, creates `oai-events` before the offer, waits for ICE gathering, exchanges SDP through FastAPI, and reports Active only after `session.started`. It exposes permission, connecting, active, muted, closing, closed, error, and autoplay-recovery states. Mute toggles only local microphone tracks; assistant playback, the provider session, and provider usage continue. End stops microphone tracks immediately, sends at most one `session.close` when the transport permits it, waits briefly for `session.closed`, and then releases audio, timers, the data channel, and the peer connection. A late SDP answer after End is used only to close the provider session and cannot restore active UI. Duration expiry, navigation, page exit, component unmount, and the independent support action use the same cleanup boundary. Each completed run starts the next voice conversation with new media and WebRTC resources. Denial and connection failure leave text chat usable. Audio and transient transcript events are not written to SQLite, and the static support route remains independent of model control.

Live transcript presentation reuses the standard chat chain without changing persistence. A framework-free View reducer accepts only bounded input/output transcript deltas with valid Live timeline intervals, preserves each fragment exactly, and keeps per-speaker bubbles independently updateable during overlap. User input marks a currently streaming assistant bubble as interrupted. Assistant output following user input creates a new assistant bubble, while timestamped late fragments can still update the earlier matching bubble. End and failure finalize visible bubbles; a later accepted Start clears them. Persisted typed messages and transient voice bubbles are merged only for display, and voice audio/text never enters the chat API or SQLite.

Mocked provider and browser tests cover these contracts without network or billing, including transcript accumulation, interruption, overlap, late ordering, stale-session rejection, and fresh-session reset. A real microphone permission flow, WebRTC negotiation, audio playback, Live event behavior, transcript accuracy, and paid Responses delegation remain unverified.

### Step 18 past conversation selection

Conversation persistence did not require a schema migration. `conversations` already stores the owning user plus creation/update timestamps, and its related `chat_logs` rows store ordered roles, content, delivery status, and timestamps. The missing behavior was View selection. History now derives a short label from the first user message and links a saved conversation back to Chat. Chat validates the query selection against the active demo user's summaries before requesting its messages, continues sending with that conversation ID, and exposes a separate New conversation action. The first message in a new conversation is persisted immediately through the existing endpoint; no independent Save endpoint or LLM history access was added. Starting a new text conversation ends an active voice session and clears only its transient captions.

### Step 20 reviewed text-chat instruction

Persisted text chat now imports its code-versioned developer instruction from `backend/controllers/services/chat_prompt.py`. The supplied prompt is retained verbatim and sent through the Responses API `instructions` field on every request. It adds explicit client-centered tone, self-report and inference boundaries, one-question/low-cognitive-load response shape, BPD-sensitive communication only when that context is supplied, rupture repair, application-capability limits, a bounded safety pathway, professional/privacy limits, and cultural humility. It continues to identify Cornerstone as a fictional coursework prototype, prohibits therapy/diagnosis/monitoring claims, forbids invented resources and application actions, and leaves exercise workflow to deterministic application code. The voice layer retains separate prompts because its delivery and delegation contract is independently bounded.

## Product direction

- Consider a mental-health skills application centered on processing and reflection.
- The user should be able to get what they need quickly, whether that is a breathing exercise, a way to explain a situation, or a conversation with a language model about what they are feeling.
- Keep the application simple, direct, and focused on its most important features.
- Prefer a smaller set of well-developed features that can respond intuitively to user choices over a broad, cluttered feature set.
- Avoid trying to address too many problems in one interface.

## Navigation and feature priority

- Determine what users are most likely to need from the application and keep the highest-priority actions within one or two clicks.
- Prioritize support for intensive moments. Emotional processing and reflection can appear later because the user may need to reach a steadier state before discussing what happened.
- Make urgent or frequently needed experiences immediately visible. If reaching a relevant exercise or conversation requires too many clicks, a stressed user may lose interest before finding it.
- Keep the interface uncluttered by limiting the number of competing paths and decisions.

## Low-effort reflection and visual input

- A questionnaire that presents many questions one at a time may demand too much time and effort, especially from someone who needs immediate support.
- Explore a more visual input method, such as a graph, to reduce the burden created by a long survey.
- Make the graph easy to access so the user can begin processing and representing their emotions quickly.
- One or two optional follow-up questions could support further reflection, but even that may cross into “too much work.” Test whether these questions add enough value to justify the added effort.

## Language-model communication

- The model's wording must be intentionally designed because small language choices can lead to substantially different user experiences and outcomes.
- Give the model clear requirements, specifications, boundaries, and examples so it can seek the desired information without inventing the interaction structure.
- Build a varied collection of desired conversation patterns. For each example, identify why the wording or structure works so the model can generalize the pattern rather than merely imitate a script.
- Relevant conversational datasets may be useful starting points for studying wording across thoughts, situations, and response styles. Dataset material must be reviewed for suitability, provenance, privacy, and alignment before use.

## Personalization and local data

- Consider storing local information about user responses and reactions so future responses can be tailored with less repeated effort.
- A simple example is remembering that a user reacted poorly to particular wording and avoiding that wording later.
- Store only information that has a clear purpose, and make the relationship between saved information and personalization understandable to the user.
- The application should clearly explain what is stored, where it is stored, and how it is used.
- Users need meaningful reassurance that their data remains private and is not used for model training, sale, or unrelated purposes. Any such assurance must match the system's actual data flow and provider policies.

## Adaptive interface and visual consistency

- Consider adapting small interface details based on the user's stated feelings and responses. Locally stored preferences or state may support this behavior.
- Be conservative about what changes. Major layout movement, changing navigation, or altering recognizable branding such as the logo could be disorienting or make the application harder to recognize.
- Preserve stable structure and predictable controls while limiting adaptation to details that have a clear user benefit.
- Give the user control over adaptation and a straightforward way to correct or disable it.

## Behavioral sensing: exploratory hypothesis and risks

- Eye movement was raised as a possible signal to explore because frequent darting might correlate with anxiety in some circumstances. This is an unvalidated design hypothesis, not an accurate anxiety test or a basis for diagnosis.
- Mouse speed is unlikely to be a reliable primary anxiety signal. Fast movement may indicate focus and can have many explanations unrelated to anxiety.
- Do not infer a user's mental state from either signal without appropriate evidence. The application must clearly communicate uncertainty and allow the user to correct any assumption.
- Eye tracking creates significant privacy and ethical concerns. It must never start without specific, informed, opt-in consent and a clear explanation of what is collected, processed, stored, and shared.
- A refusal to consent must not block access to the application's core experience.
- Before implementing any behavioral sensing, assess whether its demonstrated benefit justifies the privacy cost and whether a direct, lower-burden user input would work better.

## Questions to resolve

- Which jurisdiction-specific crisis-support resources and wording are approved for the static support page?
- When should active registration/login replace the fictional demo user used in Phase 1?
- What should the visual emotion-input graph represent, and how can it be usable without implying clinical measurement?
- Are optional follow-up questions valuable enough to justify their effort?
- Which personalization details should be saved locally, for how long, and with what review, correction, and deletion controls?
- Which model conversation patterns should be supported, and how will their wording be evaluated?
- Can useful adaptation be achieved through explicit user choices instead of behavioral inference?
- Should behavioral sensing be excluded from the initial scope because of validity, consent, privacy, and implementation risks?
