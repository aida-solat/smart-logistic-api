# Security Policy

## Supported Versions

Only the `main` branch is actively supported with security patches while the
project is in `v0.x`. Tagged releases will be added to this table once `v1.0`
ships.

| Version | Supported          |
| ------- | ------------------ |
| `main`  | :white_check_mark: |
| `< 1.0` | :x:                |

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security bugs.**

If you believe you have found a security vulnerability in Smart Logistics —
especially anything that could leak training data, bypass authentication, or
let a crafted request exfiltrate data from the causal/optimizer pipeline —
report it privately through **one** of the following channels:

1. **GitHub Security Advisory** (preferred) — use the
   [Report a vulnerability](../../security/advisories/new) button on the
   repository.
2. **Email** — `security@deciwa.com` (PGP key available on request).

Please include:

- A description of the issue and its impact.
- Steps to reproduce (minimal proof-of-concept is ideal).
- The commit hash or released version affected.
- Your name / handle for the acknowledgement (optional).

### What to expect

- We will acknowledge receipt within **72 hours**.
- We aim to provide an initial assessment within **7 days**.
- For confirmed issues, a fix or mitigation will be prepared on a private
  branch, followed by a coordinated disclosure once users have had a chance
  to upgrade.
- Reporters are credited in the release notes unless they prefer to remain
  anonymous.

## Scope

In scope:

- Backend API (`back/app/**`) including causal, optimizer, simulator, and
  auth code.
- Frontend (`front/**`) including any endpoints it proxies.
- CI/CD pipelines under `.github/workflows/`.
- Docker images produced from this repository.

Out of scope:

- Vulnerabilities in upstream dependencies (please report upstream).
- Issues that require a compromised developer machine or admin credentials.
- Denial-of-service on the public demo instance.

## Hardening recommendations for operators

- Rotate the `JWT_SECRET` and database credentials before deploying.
- Do **not** expose the Postgres, Redis, or MLflow ports publicly — put them
  behind a VPN or private network.
- Run the stack behind a reverse proxy that enforces HTTPS and rate limits.
- Keep the Olist dataset (or any real operational data) outside of any
  container image you publish.
