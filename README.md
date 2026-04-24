# Smart Logistics — Causal Decision Copilot

> A prescriptive, causal, risk-aware decision engine for logistics operations.
> Not another dashboard. Not another ETA predictor. A **decision copilot**.

---

## Vision

Most logistics AI answers the wrong question:

- ❌ _"How late will this shipment be?"_ (predictive)
- ✅ _"What should I do right now, and what happens if I don't?"_ (prescriptive + causal)

This system combines **causal inference**, **risk-aware stochastic optimization**, and
**explainable AI** to produce ranked, auditable, counterfactual-backed decision
recommendations for operations managers — in real time.

## The Novel Bet (implemented)

A unified pipeline that:

1. **Learns causal effects** of logistics decisions (not just correlations) from
   historical operations data using do-calculus (DoWhy backdoor adjustment).
2. **Adjusts the penalty** of the downstream optimizer using the causal delay
   shift `Δ·ATE`, via a rule `penalty' = base · exp(−β · Δ·ATE)`.
3. **Optimizes under tail risk** with a Rockafellar–Uryasev CVaR LP over
   bootstrapped Olist demand scenarios (inventory) and OR-Tools CVRP scored by
   Monte-Carlo CVaR of makespan (routing).
4. **Validates every decision offline** in a SimPy digital twin (A/B backtest
   with baseline vs decision, per-KPI uplift, Pareto flag).
5. **Closes the loop** by logging post-deployment realized costs and refitting
   the penalty-sensitivity β via OLS (`adaptive β`).

### Novel Claims

- **Claim 1:** A system and method for joint route–inventory decision
  optimization in which a causal average-treatment-effect estimate modulates
  the CVaR penalty of a Rockafellar–Uryasev linear program.
- **Claim 2:** A closed-loop calibration procedure that refits the penalty
  sensitivity parameter β from the ratio of realized to baseline cost across
  deployed decisions.
- **Claim 3:** An offline validation method using a SimPy digital twin to
  certify Pareto-improvement of a prescriptive decision before deployment.
- **Claim 4:** A risk-aware VRP scoring combining deterministic OR-Tools CVRP
  with Monte-Carlo CVaR of makespan under travel-time noise.

---

## Architecture

```
smart logistic api/
├── back/                     FastAPI backend
│   ├── app/
│   │   ├── core/             API routing, config, database, auth
│   │   ├── ml/               Baseline ML (existing RandomForest models)
│   │   ├── causal/           Causal graph + DoWhy/EconML effect estimation
│   │   ├── optimizer/        CVaR stochastic optimization (OR-Tools / CVXPY)
│   │   ├── simulator/        Digital twin + agent-based what-if simulation
│   │   ├── explain/          SHAP + causal path tracer + decision ledger
│   │   ├── llm/              Decision narrator & Q&A agent (phase 4)
│   │   └── feedback/         Active learning loop from user overrides
│   ├── experiments/          MLflow runs, notebooks, A/B policy tests
│   ├── data/                 Datasets (gitignored)
│   ├── tests/                Pytest suite
│   └── bruno/                API test collection (Bruno)
└── front/                    Next.js 14 + Radix UI Decision Cockpit (phase 5)
```

## Tech Stack

- **Backend:** FastAPI · Pydantic · SQLAlchemy · PostgreSQL · Redis
- **Causal ML:** DoWhy · EconML · scikit-learn · statsmodels
- **Optimization:** OR-Tools · CVXPY · PuLP
- **Simulation:** SimPy / Mesa (digital twin)
- **Explainability:** SHAP · custom causal path tracer
- **Tracking:** MLflow (experiment registry, audit trail)
- **Monitoring:** Prometheus · Grafana
- **Frontend:** Next.js 14 · Radix UI · TailwindCSS · react-map-gl · visx
- **Deployment:** Docker Compose

## Roadmap

| Phase | Goal                                                         | Status  |
| ----- | ------------------------------------------------------------ | ------- |
| **0** | Cleanup, restructure, scaffolding                            | ✅ done |
| **1** | Causal MVP on Olist (DoWhy ATE + counterfactual)             | ✅ done |
| **2** | CVaR stochastic inventory optimizer (Rockafellar–Uryasev LP) | ✅ done |
| **3** | Digital twin simulator (SimPy) + A/B validation              | ✅ done |
| **4** | Risk-aware VRP (OR-Tools + Monte-Carlo CVaR)                 | ✅ done |
| **5** | Causal-informed CVaR end-to-end pipeline                     | ✅ done |
| **6** | Next.js + Radix Decision Cockpit UI                          | ✅ done |
| **7** | Adaptive β calibration from deployment feedback              | ✅ done |
| **8** | LLM-based narrator + Q&A over decisions                      | ⏳      |
| **9** | Active learning / override-feedback retraining               | ⏳      |

## Services (docker compose)

| Service    | URL                   | Purpose                          |
| ---------- | --------------------- | -------------------------------- |
| FastAPI    | http://localhost:8000 | Backend API + OpenAPI at `/docs` |
| Next.js    | http://localhost:3200 | Decision Cockpit UI              |
| MLflow     | http://localhost:5500 | Experiment audit trail           |
| Grafana    | http://localhost:3100 | KPI dashboards                   |
| Prometheus | http://localhost:9090 | Metrics scraping                 |

## Key API Endpoints

```
# Causal
GET  /causal/graph
POST /causal/estimate-effect            # DoWhy ATE on Olist
POST /causal/counterfactual             # E[Y | do(T=t)]
POST /causal/informed-cvar              # ★ end-to-end: causal → penalty → CVaR
POST /causal/calibration/record         # log post-deployment outcome
GET  /causal/calibration/beta           # refit penalty-sensitivity β

# Optimize
POST /optimize/cvar-inventory           # Rockafellar–Uryasev LP
POST /optimize/cvar-inventory-olist     # same, with bootstrap scenarios from Olist
POST /optimize/risk-vrp                 # OR-Tools CVRP + Monte-Carlo CVaR makespan
POST /optimize/joint                    # joint inventory + routing

# Simulate
POST /simulate/network                  # SimPy digital twin, Monte-Carlo KPIs
POST /simulate/validate                 # A/B offline backtest (baseline vs decision)
```

## Frontend Pages

```
/             Dashboard + API health + login
/causal       Counterfactual query UI
/optimize     CVaR inventory solver
/routing      Risk-aware VRP
/simulate     Digital twin Monte-Carlo
/validate     A/B validation with uplift table + chart
/informed ★   End-to-end causal → penalty → CVaR pipeline
/calibration  Adaptive β learner (scatter + regression fit)
```

## Closed Loop

```
Olist panel ──► Causal (DoWhy)  ──Δ·ATE──►  Penalty rule  ──β──►  CVaR LP
       ▲                                                              │
       │                                                              ▼
       └─────── β learner  ◄── realized cost  ◄── Digital twin A/B ◄──┘
```

Every stage is logged to MLflow as experimental evidence.

## Testing

```bash
cd back && pytest -v      # 30+ tests: causal, optimizer, simulator, vrp,
                          # integration pipeline, adaptive β
```

CI runs the backend suite + frontend typecheck/build on every push
(see `.github/workflows/ci.yml`).

## Initial Dataset

Bootstrap on **[Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)**
— 100k real orders with geo, delivery times, and seller/customer locations.
Place CSVs under `back/data/raw/olist/` (gitignored).

## Getting Started

```bash
# Backend + Mlflow + Postgres + Grafana + Prometheus
cd back && docker compose up -d

# Frontend
cd front && pnpm install && pnpm dev  # serves on :3200
```

See `back/README.md` for detailed backend setup (Alembic migrations,
env vars, etc.) and `front/README.md` for frontend setup.

## License

MIT. See `LICENSE`.
