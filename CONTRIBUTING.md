# Contributing to Smart Logistics

First — thank you. This project is an ambitious attempt to combine causal
inference, risk-aware optimization, and digital-twin simulation in one open
pipeline, and it genuinely needs more hands.

## Ways to contribute

- **File a bug** — a reproducible FastAPI request or pytest failure is ideal.
- **Request a feature** — especially new causal estimators, optimizer solvers,
  or simulator scenarios.
- **Send a pull request** — see the workflow below.
- **Improve the docs** — typos, missing context, worked examples all welcome.
- **Benchmark** — plug your algorithm into the pipeline and publish uplift
  numbers on a public dataset.

## Development setup

Backend (micromamba or any Python env):

```bash
cd back
micromamba create -n procint python=3.11 -c conda-forge -y
micromamba activate procint
pip install -r requirements.txt
pytest                        # full suite must stay green
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd front
pnpm install
pnpm dev -p 3200
```

Full stack via Docker:

```bash
cd back && docker compose up -d
```

## Pull request workflow

1. Fork and create a feature branch (`feat/xyz`, `fix/abc`).
2. **Keep changes focused.** One logical change per PR.
3. **Add or update tests.** No PR that touches `back/app/` will be merged
   without a corresponding test in `back/tests/`.
4. **Run everything locally** before pushing:
   ```bash
   cd back && pytest -q
   cd front && pnpm typecheck && pnpm build
   ```
5. Describe the change in the PR body. If it relates to one of the novel
   claims, mention which one (see `README.md → Novel Claims`).
6. A maintainer will review within a few days.

## Coding conventions

- **Python**: Black + ruff defaults, type hints required on public functions,
  docstrings in NumPy style. Keep modules under ~300 lines when possible.
- **TypeScript**: strict mode, functional components, Tailwind for styling,
  no inline CSS unless it is a dynamic value.
- **No secrets in commits.** Use `.env` files (gitignored).
- **MLflow first** — any new estimator / solver / simulator must log its
  artifacts to MLflow so the audit trail stays complete.

## Commit messages

Use a Conventional-Commits-style prefix:

- `feat:` new functionality
- `fix:` bug fix
- `docs:` docs only
- `refactor:` no behavior change
- `test:` tests only
- `chore:` tooling / build

Example: `feat(optimizer): add joint inventory-routing CVaR endpoint`.

## Community

- Be kind. See `CODE_OF_CONDUCT.md`.
- For design discussions, open an issue with the `discussion` label before
  writing code — it saves everyone time.

Thanks again. ♥
