# Selected Development Evidence

## Scope

I selected a small set of prompts, changes, checks, and decisions rather than including a full chat export. I used fictional scenarios and excluded credentials, private environment values, personal account data, and research-participant information. Earlier observations below come from the saved verification record; I do not present them as new browser runs.

## Bounded scaffold

I asked for a local Vue, FastAPI, and SQLite project with project-owned dependencies and MVC boundaries. I retained the [initial scaffold prompt](../prompts/01-bounded-scaffold.md), [backend prompt](../prompts/02-backend-environment.md), and [frontend prompt](../prompts/03-frontend-environment.md).

I separated model entities and data, controller/API behavior, and the complete frontend View. I used environment, dependency, lint, and build checks to establish the scaffold. I kept model workflow control out of the View-to-database boundary.

## Revised approach: build success and visible behavior

I initially relied on successful build and utility checks for the grounding interface. During the October 22 browser walkthrough, I found that the outcome-card conditional did not display the intended result. I also found poor assistant-message contrast in dark mode.

I used the visible result and matching SQLite records to separate a presentation failure from a persistence failure. I corrected the condition and message colors, then repeated the browser check. I decided to retain browser/database comparisons alongside automated tests. The observations are recorded under Step 11 in [verification](verification.md) and [design notes](design_notes.md).

## Revised approach: provider failure

I tested incomplete provider configuration after completing and leaving breathing in the browser. I observed a recoverable fallback and matching saved records, but the provider label still said `mock`. I corrected the label to `unavailable` and checked it again.

I later removed synthetic successful responses from production text chat. I kept injected provider doubles in tests so routine checks stayed repeatable and free of paid requests. I verified missing configuration, timeout, bounded context, and saved fallback behavior in [API tests](../backend/tests/test_api.py) and [chat tests](../backend/tests/test_chat_service.py).

## History and personalization

I added conversation selection so saved chats could be continued rather than only displayed. I kept the existing conversation/message relationship and added View selection instead of an extra save operation. I checked requested, unavailable, and new-conversation selections in [conversation tests](../frontend/tests/conversationSelection.test.js).

I added explicit local account state and editable check-ins instead of inferring feelings from behavior. I used backend migration and API checks to retain legacy rows and multiple entries per day. I checked calendar helpers, request mapping, and account restoration with frontend tests. I kept this as user-controlled continuity, without automatic distress detection or recommendations.

## November 2 report revision

I asked Codex to preserve my wording, use first person, keep the writing minimal, and describe only implemented features. I compared the old report with the current routes, account/calendar code, provider boundary, and saved verification history.

I corrected stale demo-account, mock-provider, route-count, and test-count claims. I documented fifteen existing fictional automated scenarios and three behavior checks, while separating mocked results from unperformed live comparisons. I replaced the copied system prompt with a source link and a short explanation.

## November 2 follow-up

I asked Codex to complete the remaining material other than screenshots and video. I added this evidence log, an AI-use disclosure, portable setup guidance, and a test-only peer fixture. I kept production chat unchanged.

My first peer-fixture check expected a boolean `configured` field from the voice endpoint and failed with `KeyError`. I checked the actual JSON contract, corrected the test to expect `status: unconfigured`, and reran it successfully. I used controller checks to confirm mocked success, timeout, unavailable replies, restart persistence, and disabled voice even when provider environment names were present.

I recorded final commands and the isolated installation result in [verification](verification.md). I kept the final submission hash, independent-person check, and any unavailable live evidence explicitly unresolved rather than inventing results.
