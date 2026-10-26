# Local model data

Local SQLite database files live here. `cornerstone.db` was moved here from the former root-level `data/` directory and now belongs to the model layer.

Database files and their WAL/SHM companions are ignored so fictional test records, credentials, or local state are not committed. Schema creation and repeatable seed data should be implemented in code rather than relying on a checked-in runtime database.
