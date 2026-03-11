RBAC Consolidation & Migration Plan

Summary

We consolidated duplicate `Role`, `Permission`, and `AuditLog` model definitions by aliasing canonical models from `apps.accounts.models` and `apps.common.models` inside `platform/core/models.py` to avoid DB table conflicts.

Risk & Impact

- No destructive schema changes were applied. The code now references canonical models; database tables remain unchanged.
- Recommended: run full test suite and `makemigrations` locally to ensure no pending migrations are required.

Safe rollout steps

1. Backup production database.
2. On a development/staging environment: pull latest code, create a fresh env, install requirements.
3. Run `python manage.py makemigrations` and confirm no unexpected model/table renames are detected.
4. Run `python manage.py migrate` on staging.
5. Run the test suite. If the environment cannot create test DB, run smoke tests via `manage.py` commands added earlier.
6. If all good, schedule a maintenance window for production and run migrations.

If `platform/core` must be removed entirely

- Instead of deleting files, we alias the models now. If you choose to remove `platform/core/models.py`, update imports across the codebase and create a migration that drops no tables but removes the module reference. Only remove after ensuring no imports rely on the file.

Rollback

- If issues appear, restore DB from backup and revert the code to the previous commit.

Contact

- Developers: review `docs/RBAC.md` and `apps/accounts/utils.py` for helper usage.
