# Frontend router

`index.js` owns the View's route-to-page mapping. The seven registered phase-one
routes are `/`, `/grounding`, `/chat`, `/calendar`, `/history`, `/account`, and
`/support`.

Grounding, Chat, Calendar, and History carry `requiresAccount` metadata. The
application shell enforces that presentation-level gate with the current local
account state; it is not server-issued authorization. Route components communicate
with backend controllers through the JSON contracts in `docs/mvc-contracts.md`, and
the router does not import backend Python modules or access SQLite.
