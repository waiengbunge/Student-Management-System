Deployment & Migration Notes
===========================

Quick steps to run migrations and deploy (development / CI):

- Ensure environment variables for DB are set, e.g. `DATABASE_URL=postgres://user:pass@host:5432/dbname`.
- Create or migrate the database:

```bash
# apply Django migrations
python -m config.manage migrate --noinput

# create initial RBAC seeds (optional)
python -m config.manage seed_rbac

# run demo seed + smoke checks
python -m config.manage seed_smoke
```

CI
--
The repository contains a GitHub Actions workflow at `.github/workflows/ci.yml` which:

- spins up a Postgres service
- installs dependencies from `requirements.txt`
- runs migrations
- runs `seed_smoke` (if available)
- executes the Django test suite

Local dev notes
---------------
- Use a Python virtualenv and ensure `psycopg2` or `psycopg[binary]` is installed for Postgres support.
- If your local environment cannot create test databases, use the CI workflow to run tests.

Rollback / backups
------------------
- Back up DB before running potentially-destructive migrations in production.
- Use standard Postgres tools or your cloud provider's snapshot features.
