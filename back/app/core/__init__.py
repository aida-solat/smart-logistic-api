"""Core infrastructure: config, database, auth, routing glue.

Phase 1 refactor: move `config.py`, `database.py`, `auth.py` from `app/` to
`app/core/` and update imports. Deferred to avoid breaking existing endpoints
during phase 0.
"""
