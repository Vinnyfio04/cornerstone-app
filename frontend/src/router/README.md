# Frontend router

`index.js` owns the View's route-to-page mapping. The registered phase-one routes are
`/`, `/grounding`, `/chat`, `/history`, `/account`, and `/support`.

Route components are presentation placeholders at this stage. They must communicate
with backend controllers through the JSON contracts in `docs/mvc-contracts.md`; the
router does not import backend Python modules or access SQLite.
