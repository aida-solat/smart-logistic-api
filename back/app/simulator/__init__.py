"""Digital twin simulator (phase 3 — live).

Public API:
    - :func:`app.simulator.twin.run_simulation`
    - :func:`app.simulator.twin.monte_carlo`
    - :class:`app.simulator.twin.WarehouseConfig`
    - :data:`app.simulator.router.router` — FastAPI router mounted under /simulate
"""
from app.simulator.router import router  # noqa: F401
