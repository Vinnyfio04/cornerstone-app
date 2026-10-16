# Cornerstone Design Notes

## Status and intent

These are exploratory product and interaction notes, not finalized requirements or claims of clinical effectiveness. Ideas involving behavioral sensing, personalization, or language-model responses require validation, explicit user control, and alignment with the project's coursework-prototype boundaries before implementation.

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

- Which small set of features best supports the initial experience?
- What should the visual emotion-input graph represent, and how can it be usable without implying clinical measurement?
- Are optional follow-up questions valuable enough to justify their effort?
- Which personalization details should be saved locally, for how long, and with what review, correction, and deletion controls?
- Which model conversation patterns should be supported, and how will their wording be evaluated?
- Can useful adaptation be achieved through explicit user choices instead of behavioral inference?
- Should behavioral sensing be excluded from the initial scope because of validity, consent, privacy, and implementation risks?
