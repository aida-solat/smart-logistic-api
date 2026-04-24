# Smart Logistics — Dashboard

Next.js frontend for the Causal Decision Copilot. Talks to the FastAPI
backend at `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`) through
a Next.js rewrite.

## Pages

- `/` — dashboard with API health and quick links to MLflow, Grafana, Prometheus
- `/causal` — counterfactual query against the DoWhy-based causal engine
- `/optimize` — CVaR inventory reallocation (Rockafellar–Uryasev LP)
- `/simulate` — SimPy digital twin with Monte-Carlo KPI aggregation

## Run

```bash
cd front
pnpm install
cp .env.local.example .env.local
pnpm dev
# http://localhost:3000
```

The backend stack should be up first (`docker compose up` in `back/`).

## Stack

- Next.js (App Router)
- TypeScript, strict
- Tailwind CSS
- Radix UI primitives (Dialog, Label, Slot, Tabs)
- lucide-react icons
- recharts for plots

## Legacy CRA code

The old `src/` folder is left over from Create React App and isn't used by
Next.js. Safe to remove:

```bash
rm -rf src
```
