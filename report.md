# Milestone Report

## Repository

[https://github.com/Vinnyfio04/cornerstone-app](https://github.com/Vinnyfio04/cornerstone-app)

Submitted commit: [Add the final submitted commit after saving and committing the finished work. The application baseline I checked was `f1f4b641d9928a11a4927497387e992e6f88e866`.]

## Scope

For this version, I focused on making the main parts of the application work together. I included 4–6 paced breathing, 5-4-3-2-1 sensory grounding, chat, saved history, local accounts, a check-in calendar, and a separate crisis-support route.

I developed Cornerstone as a coursework prototype for fictional situations. I do not present it as therapy, a diagnosis tool, an emergency service, or a replacement for professional care.

## Working Experience

I kept the main experience in the Vue interface. I placed breathing on the home page, followed by sensory grounding and chat. I also included pages for Check-in, History, Account, and crisis-support information.

I used a four-second inhale and six-second exhale for six breathing cycles. I kept sensory grounding in the order of five things to see, four to feel, three to hear, two to smell, and one to taste. I kept the exercise order, timing, saved state, exit controls, and support access in application code so these parts do not depend on a model response.

I added local registration, sign-in, account editing, sign-out, and deletion. I kept breathing and support available without signing in. I require sign-in in the interface for grounding, chat, voice, history, and check-ins. I store hashed passwords, but I have not implemented server-issued authorization, so I do not consider the local account gate secure API authentication.

## Changes from Part 3.1

I kept the original goal of a simple experience with low reading and typing effort. I chose breathing and sensory grounding because I could present the steps directly without asking for written answers. I kept stopping and changing direction under the user's control.

I expanded the earlier breathing-focused idea to include a separate grounding page. I also moved beyond the fictional demo account by adding local accounts and a calendar. I let a person choose feelings, use a custom label and color, and edit more than one check-in on a date rather than having the application guess how they feel. I gained more personal history, but signing in and entering check-ins adds effort.

I changed conversation history from something to review into something that can be reopened and continued. I removed the production mock-response option so a missing model configuration produces an honest unavailable state. I still use injected fake responses in tests.

I found during browser testing that a successful build did not guarantee a correct screen. I corrected a grounding-result condition and chat contrast after reviewing the visible results. I also corrected a misleading provider label after a failed request. I kept these observations in my [design notes](docs/design_notes.md) and [verification record](docs/verification.md).

I compared these decisions with the initial design notes retained in Git. I chose explicit check-ins and stable controls instead of the proposed emotion graph, automatic interface adaptation, or behavioral sensing. I kept personalization limited to information a person chooses to save. I reused setup prompts from earlier coursework, but no other application code.

## Model Contribution

I use the OpenAI Responses API for production text chat. I keep the prompt and provider configuration on the backend and limit the conversation context, response size, and request timeout. I use the model for conversation, while application code controls exercises and persistence. I do not give the model automatic access to calendar entries or all saved history.

I keep the text instruction in [chat_prompt.py](backend/controllers/services/chat_prompt.py). I ask for brief, supportive replies without diagnosis, treatment, monitoring claims, or invented application actions. I have verified that the instruction is sent with a fake client, but I have not established how consistently a live model follows it.

I also included an optional microphone button and voice-session controller. I checked interruption, mute, ending, transcript handling, and cleanup with mocks. I do not save voice audio or its temporary transcript to text-chat history. I have not verified a real microphone and paid provider session.

## Conversation and Session Persistence

I store conversations, ordered messages, exercise sessions, accounts, and check-ins in SQLite. I show completed and exited exercises in History with their measured duration and last step. I keep past conversations in a dropdown beside New conversation in Chat, where saved messages can be reviewed and reopened.

I use saved history for continuity rather than automatic recommendations. I let a person continue a selected conversation, update account details, and review or edit calendar entries. I keep only a bounded part of the selected conversation in the model context, so saved history does not mean unlimited model memory.

I allow multiple check-ins for today or a past date, preset or custom feelings and colors, and editing saved entries. I show up to three date markers while keeping all entries in the selected-day panel. I keep future dates read-only in the interface.

## Exercise Duration

I measure active exercise time in the browser. I start grounding timing when the first prompt appears and stop it when the exercise is finished or left. I start breathing timing when the control is activated and stop it on release or after six cycles.

I planned breathing for 60 seconds. In the earlier browser walkthrough, I recorded completion at 60 seconds and an early exit at 6.2 seconds, with matching SQLite records. I keep wind-chime ambience active only during breathing.

I keep grounding self-paced and do not force completion. I use an intended evaluation pace of about ten seconds per prompt, plus up to five seconds for advancing controls, or about 55 seconds total. I do not treat that estimate as an observed typical-user duration. I exclude account setup and navigation from active timing. [Add the measured grounding duration and separate entry/setup times when collecting the final demonstration evidence.]

## Leaving an Exercise and Request Failure

I let a person leave either exercise without finishing. I save an exited result and the measured duration when persistence is available. I keep breathing usable if the backend is unavailable, although I cannot save its result. I cannot promise access to signed-in pages if restoring the account fails.

I provide Retry message and Reload saved messages controls for chat failures. I save the user message and a fallback result when a provider request fails. I remove the temporary sending bubble before recovering saved messages so it does not remain pending or appear twice.

## Independent Crisis-Support Route

I placed crisis-support information at `/support` and kept its link in the application header. I made this route independent of the model, a classifier, FastAPI, and SQLite. I do not use an application distress detector to decide whether it is available.

I ask the model to respond carefully to fictional crisis-related input, but I do not treat the prompt as a guarantee. I added U.S./Pennsylvania support information using the helpline lookup and official Pennsylvania and SAMHSA sources. I kept the contact links static and separate from the model. I do not claim that Cornerstone can monitor anyone or contact a service for them.

## Fictional Scenario Evaluation

I reran the saved automated tests on November 1, 2026. I used fictional data, temporary test databases, fake providers, and mocked browser objects. I recorded the following results at the tested function or controller boundary; I did not run these as fifteen new browser walkthroughs or live-model conversations.

1. I registered a fictional account and signed in with the correct password. I expected the same account and a hashed stored password. I observed both in `backend/tests/test_api.py`.
2. I tried an incorrect password. I expected an invalid-credentials result. I observed a 401 result in `backend/tests/test_api.py`.
3. I restored a remembered fictional account. I expected the saved identifier to recover that account without storing credentials in the browser. I observed this in `frontend/tests/demoUser.test.js`.
4. I simulated six uninterrupted breathing cycles. I expected four-second inhales, six-second exhales, and completion at 60 seconds. I observed those timing results in `frontend/tests/breathingTimeline.test.js`.
5. I simulated leaving grounding at the hearing step. I expected an exited result with the last visible step and measured duration. I observed both in `frontend/tests/groundingSequence.test.js`.
6. I simulated completing grounding at the taste step. I expected a completed result with the final step. I observed that result in `frontend/tests/groundingSequence.test.js`.
7. I created and edited a fictional calendar check-in. I expected the updated feeling, color, and description on the original date. I observed those values in `backend/tests/test_api.py`.
8. I added a second check-in on the same date. I expected both entries to remain saved. I observed both in `backend/tests/test_api.py`.
9. I selected a future date in the calendar helper. I expected creation to be disallowed. I observed that result in `frontend/tests/calendar.test.js`; I did not treat it as a server-wide restriction.
10. I sent a fictional message through an injected successful provider. I expected ordered user and assistant records. I observed both saved as delivered in `backend/tests/test_api.py`.
11. I selected a saved conversation. I expected the requested conversation rather than a new one. I observed that selection in `frontend/tests/conversationSelection.test.js`.
12. I sent a fictional message with incomplete model configuration. I expected an unavailable result rather than a fake successful answer. I observed a 503 result and saved user/fallback records in `backend/tests/test_api.py`.
13. I injected a model timeout. I expected a timeout result while preserving the message and fallback. I observed a 504 result and both records in `backend/tests/test_api.py`.
14. I simulated a failed pending text message. I expected its temporary bubble to be removed before saved-state recovery. I observed its removal in `frontend/tests/optimisticChat.test.js`.
15. I denied microphone permission in the mocked browser. I expected a recoverable voice error without calling the API. I observed both in `frontend/tests/voiceSession.test.js`.

I used these cases to check ordinary activity, interruptions, and failures. I have not used their fake replies as evidence of supportive language or model safety.

## Behavior Checks

1. I require support access to remain independent across loading, request failure, and voice activity. I found the link outside the account-gated page content, earlier browser evidence of support opening during an API outage, and a passing mocked voice-cleanup check for the support action. [Capture the same failure-to-support path in the final current-version recording.]
2. I require exercise order and timing to stay independent of model replies. I observed passing breathing-timeline and grounding-sequence tests, including completed and exited results.
3. I require failed provider requests to preserve the fictional message and mark the fallback separately. I observed this for missing configuration, provider unavailability, and timeout in the backend tests.

## Live-Model Comparison and Peer Testing

I completed an approved live text comparison with `gpt-5.6-sol`, using the same text instruction and request limits as the application. I capped the session at eight attempts and disabled automatic retries. I recorded seven completed replies and one connection failure. I saved the fictional inputs, outputs, returned model identifier, and timings in [the live results](docs/live-model-results.json).

- I expected brief acknowledgment for assignment stress. I received one completed reply offering a manageable choice; the other attempt failed before connecting, so I do not claim a repeated pair for this case.
- I expected a refusal of an exercise to be respected. In both replies, I observed acknowledgment and no repeated exercise pressure. I saw different wording and a question in one reply.
- I expected a misunderstood emotion to be corrected. In both replies, I observed acknowledgment of the mistake and one follow-up question, with slightly different wording.
- I expected a fictional immediate-danger case to produce a brief safety response without invented contacts or claims of intervention. In both replies, I observed directions toward external help and the independent support page. I also noticed direct second-person wording despite the fictional-character framing.

I used this small sample to examine variation, not establish reliable safety or clinical effectiveness. I did not run these calls through the browser or write them into the normal application database.

I use mocked responses for routine checks and the test-only [peer server](backend/tests/peer_server.py) for browser peer testing. I keep its database separate and disable live voice. I documented the commands and failure inputs in [the evaluation procedure](docs/evaluation.md). I returned to mocked checks after the eight-attempt cap. For any live peer session, I require the host to track attempts, set a limit of no more than fifty model calls, and return to mocks at that limit. I have not claimed a completed classmate session.

## Surprising Finding and Limitation

I was surprised that the application could build successfully while the grounding result still displayed incorrectly. I used the browser result to find the conditional problem and corrected it. I learned to compare visible results with saved records instead of relying only on a successful build.

I have not tested repeated live responses to ambiguous fictional crisis-related language. I cannot claim consistent interpretation or response quality from mocked tests. I also have not completed a physical-phone accessibility review or live voice verification.

## Generated Code

I use `reconcilePendingMessage` in [optimisticChat.js](frontend/src/utils/optimisticChat.js) to replace a temporary sending bubble with the saved user and assistant messages. I find the temporary message by its identifier and replace it in the same position. If it is already gone, I append the saved pair. I remove a failed pending message before loading saved history.

I checked replacement, duplicate prevention during replacement, and failed-bubble removal in [optimisticChat.test.js](frontend/tests/optimisticChat.test.js).

I also used Codex to generate the test-only peer fixture. In `create_peer_app`, I inject a fixed text provider and empty voice settings into the existing application factory. I reuse the normal routes and persistence while preventing the fixture from making live model requests. I use exact test inputs to trigger timeout and unavailable results. I checked these outcomes and restart persistence at the controller boundary in [test_peer_server.py](backend/tests/test_peer_server.py). [Explain this generated fixture or the pending-message function in the process recording.]

## Verification and Clean Checkout

I completed the following checks in the existing local environment:

- I passed 48 backend tests and 64 frontend tests, including the new peer-fixture controller check.
- I passed non-fixing Oxc and ESLint checks.
- I completed the Vite production build with 71 modules transformed.
- I ran `pip check` and found no broken Python requirements.

I ran these commands from the project root, except ESLint, which I ran inside `frontend`:

```powershell
& 'backend/.venv/Scripts/python.exe' -m pytest backend/tests -q -p no:cacheprovider --basetemp backend/.pytest_cache/report-review
npm --prefix frontend run test:unit
npm --prefix frontend exec -- oxlint .
# Inside frontend:
& './node_modules/.bin/eslint.cmd' . --no-cache
# Back at the project root:
npm --prefix frontend run build
& 'backend/.venv/Scripts/python.exe' -m pip check
```

I corrected the outdated mock-mode guidance in `.env.example` and expanded the README with prerequisites, the browser address, credential-free behavior, and mocked peer-testing instructions. I used a clean source copy with no copied virtual environment, Node dependencies, local database, or private environment file to check installation separately from the working environment. I passed 48 backend tests and 64 frontend tests in that isolated copy, completed its build, and found no broken Python requirements. I recorded the commands, versions, installation results, and warnings in [verification](docs/verification.md).

I made only the approved text calls and no new microphone checks. I relied on the earlier recorded browser/SQLite evidence for the complete exercise and failure flows, current automated checks for repeatability, and the isolated setup check for installation evidence.

## Demonstration and Process Evidence

[Add an accessible finished-application recording link. Show a fictional account, exercise completion and early exit, saved history after restart, a reopened conversation, calendar creation/editing, request failure, and independent support access. Clearly distinguish mocked replies from any live model contribution.]

[Add readable browser and matching SQLite screenshots for exercise duration/exit, persisted history, calendar edits, and fallback records. Remove credentials and personal information.]

## Unfinished Work

I  have not completed a systematic physical-phone accessibility review or a live voice check, so I keep those limitations explicit.

I disclosed Codex use, available model identifiers, and reused setup prompts in [AI-USE.md](AI-USE.md). I connected selected prompts, changes, failures, checks, and decisions in a [redacted evidence log](docs/evidence-log.md).

## Design and Verification Documents

- [Initial wireframe](docs/images/initial%20basic%20wireframe.png)
- [Calendar wireframe](docs/images/calendar%20wireframe.png)
- [README](README.md)
- [Phase 1 contract](docs/phase-1-contract.md)
- [MVC contracts](docs/mvc-contracts.md)
- [Design notes](docs/design_notes.md)
- [Verification record](docs/verification.md)
- [Selected scaffold prompts](prompts/)
- [AI-use disclosure](AI-USE.md)
- [Curated evidence log](docs/evidence-log.md)
- [Evaluation and peer-testing procedure](docs/evaluation.md)
- [Saved live-model results](docs/live-model-results.json)
