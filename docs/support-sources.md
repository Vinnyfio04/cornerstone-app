# Support Content Sources

I selected the United States, specifically Pennsylvania, after confirming the intended jurisdiction. I replaced the placeholder View copy with static emergency and support information. I reviewed these sources on November 2, 2026:

- I used the connected helpline lookup to verify the U.S. Lifeline call, text, and online-chat destinations.
- I checked the [Pennsylvania Department of Human Services support page](https://www.pa.gov/agencies/dhs/resources/mental-health-substance-use-disorder/988) for Pennsylvania applicability.
- I checked [SAMHSA crisis guidance](https://www.samhsa.gov/find-support/in-crisis) for the distinction between crisis support and immediate danger or a medical emergency. Search returned the official guidance; the direct-page fetch returned a 403, so I do not claim that fetch succeeded.

I placed the content in `frontend/src/pages/CrisisSupportPage.vue` with no API request, account gate, classifier, or model dependency. I included source links, the review date, the coursework boundary, and a clear statement that Cornerstone cannot monitor anyone or contact a service on their behalf. I did not add claims about response times or promise confidentiality on Cornerstone's behalf.

I did not place a call, send a text, or start an external crisis chat during testing. I verified the contact destinations through the lookup and sources rather than contacting the services. I keep external phone/internet requirements separate from the availability of the local page. I did not modify the user-supplied text prompt, which still conservatively avoids inventing local contact details.
