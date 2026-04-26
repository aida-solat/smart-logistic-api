# Smart Logistics — Backend

FastAPI backend for the Causal Decision Copilot. See root `README.md` for the
full project vision.

**Live API:** https://smart-logistics-api-w0ik.onrender.com (`/health`, `/docs`)

## Quick Start

```bash
cp .env.example .env            # fill in secrets
docker-compose up --build        # app + postgres + redis + prometheus + grafana + mlflow
```

Services:

- API: http://localhost:8000 (docs at `/docs`)
- MLflow UI: http://localhost:5000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Local Dev (no Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Layout

```
app/
├── core/         # config, database, auth (phase 1 refactor target)
├── ml/           # baseline RandomForest (phase 1 migration)
├── causal/       # DoWhy / EconML effect estimation         [Phase 1]
├── optimizer/    # CVaR stochastic optimization             [Phase 2]
├── simulator/    # Digital twin / what-if                   [Phase 3]
├── explain/      # SHAP + causal path tracer                [Phase 2-4]
├── llm/          # Decision narrator & Q&A                  [Phase 4]
├── feedback/     # Override → counterfactual loop           [Phase 6]
├── ai.py         # (legacy, moves to ml/ in phase 1)
├── analytics.py  # pandas analytics
├── auth.py       # JWT + role/permission
├── config.py     # pydantic-settings
├── crud.py       # DB operations
├── database.py   # SQLAlchemy engine/session
├── main.py       # FastAPI app + routes
├── models.py     # SQLAlchemy ORM models
└── schemas.py    # Pydantic schemas
```

## Tests

```bash
pytest tests/ -v
```

## Bruno API Collection

See `bruno/` for HTTP request examples (open with Bruno app).
