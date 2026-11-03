# Frontend request modules

These dedicated JSON request modules are the only frontend code that calls FastAPI. `client.js` validates the shared envelope and translates transport failures, while the resource modules implement the documented account, user, exercise-session, calendar check-in, text-chat, history, and voice-session requests. `accounts.js` sends credentials only to the account controller and never stores them. `checkIns.js` creates, lists, and updates user-owned dated check-ins through JSON. `voice.js` sends only a browser-created SDP offer and receives the public session answer; provider configuration remains server-owned.

Development requests use relative `/api` paths through Vite's localhost proxy. A deployment may set `VITE_API_BASE_URL`; no frontend module reads SQLite or imports backend Python code.
