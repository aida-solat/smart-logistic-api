# Smart Logistics — Causal Decision Copilot

[![CI](https://github.com/aida-solat/smart-logistic-api/actions/workflows/ci.yml/badge.svg)](https://github.com/aida-solat/smart-logistic-api/actions/workflows/ci.yml)

**Live demo:** [logistic.deciwa.com](https://logistic.deciwa.com) ·
**API:** [smart-logistics-api-w0ik.onrender.com](https://smart-logistics-api-w0ik.onrender.com/health)

A prescriptive, causal, risk-aware decision engine for logistics operations.

Most logistics AI answers the wrong question. It tells you _how late a
shipment will be_. What an operations manager actually needs is a
recommendation: _what should I do right now, and what happens if I don't?_
That's what this project tries to answer.

## What it does

A single pipeline that:

1. Learns causal effects of logistics decisions from historical data using
   do-calculus (DoWhy backdoor adjustment) — not just correlations.
2. Adjusts the downstream optimizer's penalty by the causal delay shift
   `Δ·ATE` via `penalty' = base · exp(−β · Δ·ATE)`.
3. Optimizes under tail risk with a Rockafellar–Uryasev CVaR LP over
   bootstrapped Olist demand scenarios (inventory), and an OR-Tools CVRP
   scored by Monte-Carlo CVaR of makespan (routing).
4. Validates every decision offline in a SimPy digital twin (A/B backtest,
   per-KPI uplift, Pareto flag).
5. Closes the loop: post-deployment realized costs are logged and β is
   refit via OLS.

## Why it's different

- Causal ATE modulates the CVaR penalty of a Rockafellar–Uryasev LP for
  joint route/inventory decisions.
- Penalty sensitivity β is refit from the ratio of realized to baseline
  cost across deployed decisions.
- Decisions are certified Pareto-improving in a SimPy twin before they
  reach production.
- VRP routes are re-scored with Monte-Carlo CVaR of makespan under
  travel-time noise, not just deterministic distance.

## Layout

```
smart logistic api/
├── back/                     FastAPI backend
│   ├── app/
│   │   ├── core/             routing, config, database, auth
│   │   ├── ml/               baseline RandomForest models
│   │   ├── causal/           causal graph + DoWhy/EconML effect estimation
│   │   ├── optimizer/        CVaR stochastic optimization (OR-Tools / CVXPY)
│   │   ├── simulator/        SimPy digital twin + what-if simulation
│   │   ├── explain/          SHAP + causal path tracer + decision ledger
│   │   ├── llm/              decision narrator and Q&A agent
│   │   └── feedback/         operator override loop
│   ├── experiments/          MLflow runs, notebooks
│   ├── data/                 datasets (gitignored)
│   ├── tests/                pytest suite
│   └── bruno/                Bruno API test collection
└── front/                    Next.js + Radix UI decision cockpit
```

## Tech stack

- Backend: FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Redis
- Causal ML: DoWhy, EconML, scikit-learn, statsmodels
- Optimization: OR-Tools, CVXPY, PuLP
- Simulation: SimPy
- Explainability: SHAP, custom causal path tracer
- Tracking: MLflow
- Monitoring: Prometheus, Grafana
- Frontend: Next.js, Radix UI, TailwindCSS, react-map-gl, visx
- Deployment: Docker Compose

## Roadmap

| Phase | Goal                                             |
| ----- | ------------------------------------------------ |
| 0     | Cleanup and scaffolding                          |
| 1     | Causal MVP on Olist (DoWhy ATE + counterfactual) |
| 2     | CVaR stochastic inventory optimizer              |
| 3     | SimPy digital twin + A/B validation              |
| 4     | Risk-aware VRP (OR-Tools + Monte-Carlo CVaR)     |
| 5     | Causal-informed CVaR end-to-end pipeline         |
| 6     | Next.js + Radix decision cockpit UI              |
| 7     | Adaptive β calibration from deployment feedback  |
| 8     | LLM narrator + Q&A over decisions                |
| 9     | Active learning / override-feedback retraining   |

Phases 0–9 are shipped. Next up: Kafka streaming ingestion and multi-echelon
inventory.

## Services (docker compose)

| Service    | URL                   | Purpose                         | Where        |
| ---------- | --------------------- | ------------------------------- | ------------ |
| FastAPI    | http://localhost:8000 | Backend API, OpenAPI at `/docs` | local + prod |
| Next.js    | http://localhost:3200 | Decision cockpit UI             | local + prod |
| PostgreSQL | —                     | Persistent storage              | local + prod |
| Redis      | —                     | Cache / queues                  | local + prod |
| MLflow     | http://localhost:5500 | Experiment audit trail          | local only   |
| Grafana    | http://localhost:3100 | KPI dashboards                  | local only   |
| Prometheus | http://localhost:9090 | Metrics scraping                | local only   |

The monitoring stack (MLflow, Grafana, Prometheus) runs locally via
`docker compose up` — it requires persistent volumes that don't fit a
free-tier hosting plan. Production deploys ship API + UI + DB + Redis only.

## Key endpoints

```
# Feedback
POST /feedback/override                 log an operator override
GET  /feedback/overrides?limit=50       recent overrides
GET  /feedback/summary                  roll-up stats

# LLM
POST /llm/narrate                       executive brief of a decision
POST /llm/ask                           operator Q&A over a decision

# Causal
GET  /causal/graph
POST /causal/estimate-effect            DoWhy ATE on Olist
POST /causal/counterfactual             E[Y | do(T=t)]
POST /causal/informed-cvar              end-to-end causal -> penalty -> CVaR
POST /causal/calibration/record         log post-deployment outcome
GET  /causal/calibration/beta           refit penalty-sensitivity beta

# Optimize
POST /optimize/cvar-inventory           Rockafellar-Uryasev LP
POST /optimize/cvar-inventory-olist     bootstrap scenarios from Olist
POST /optimize/risk-vrp                 OR-Tools CVRP + MC CVaR makespan
POST /optimize/joint                    joint inventory + routing

# Simulate
POST /simulate/network                  SimPy digital twin, MC KPIs
POST /simulate/validate                 A/B offline backtest
```

## Frontend pages

```
/             marketing landing
/dashboard    app entry: API health, quick actions, pipeline status
/causal       counterfactual query UI
/optimize     CVaR inventory solver
/routing      risk-aware VRP
/simulate     digital twin Monte-Carlo
/validate     A/B validation with uplift table and chart
/informed     end-to-end causal -> penalty -> CVaR pipeline
/calibration  adaptive beta learner
/feedback     operator overrides log
/narrate      LLM executive brief over a decision
```

## Closed loop

```
Olist panel -> Causal (DoWhy) --Delta*ATE--> Penalty rule --beta--> CVaR LP
     ^                                                                  |
     |                                                                  v
     +------ beta learner <-- realized cost <-- Digital twin A/B <------+
```

Every stage is logged to MLflow.

## Testing

```bash
cd back && pytest -v
```

Around 30 tests covering causal, optimizer, simulator, VRP, the integration
pipeline, and adaptive β. CI runs the backend suite plus frontend
typecheck/build on every push (see `.github/workflows/ci.yml`).

## Dataset

We bootstrap on the [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
— about 100k real orders with geo, delivery times, and seller/customer
locations. Drop the CSVs under `back/data/raw/olist/` (gitignored).

## Getting started

```bash
# Full local stack: API + Postgres + Redis + MLflow + Grafana + Prometheus
cd back && docker compose up -d

# Frontend (serves on :3200)
cd front && pnpm install && pnpm dev
```

See `back/README.md` for backend details (Alembic migrations, env vars)
and `front/README.md` for the frontend.

## Deployment

- **Frontend** → Vercel at [logistic.deciwa.com](https://logistic.deciwa.com)
  (`front/` as project root). The Next.js rewrite forwards `/api/*` to
  the backend via `BACKEND_URL`.
- **Backend** → Render (FastAPI + managed PostgreSQL + Redis), see
  `render.yaml`. **All three resources must share the same region**
  (we pin `frankfurt`) — internal DNS only resolves within a region.
- **Monitoring stack** (MLflow, Prometheus, Grafana) is local-only
  via `docker compose`. The free-tier hosts don't provide the
  persistent volumes these services need to be useful.
- **External APIs** (`TRAFFIC_API_KEY`, `WEATHER_API_KEY`) are optional
  — endpoints that need them fail at request time with a clear error,
  the rest of the stack boots without them.
- A `cron-job.org` ping every 10 minutes hits `/health` to keep
  the Render free instance from cold-starting.

## License

MIT. See `LICENSE`.
