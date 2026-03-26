# Devagya OJ (OJ_Project-main)

## Seed Problems + Testcases

Problems and their judging testcases are seeded from:
`OJ/data/problems_seed.json`

To (re)import into the database (safe to run multiple times):

```bash
cd /Users/devagyavats/Downloads/OJ_Project-main
source .venv/bin/activate
python manage.py import_problems
```

This command is **idempotent**:
- Problems are upserted by case-insensitive `title`
- Existing testcases for a problem are deleted and recreated from the JSON

To import from a custom JSON path:
```bash
python manage.py import_problems /path/to/problems_seed.json
```

## Runner Verification (Dev Only)

To verify that the judge runner’s expected outputs map correctly:

```bash
python manage.py verify_problem_runner --problem-id 1
python manage.py verify_problem_runner --problem-id 2
```

## Dev DB Workflow

### Fresh Start
To completely wipe your local database and start fresh:
```bash
docker compose down -v
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_dev_data
```

### Inspect the Database
To open a psql shell to the PostgreSQL container:
```bash
docker compose exec db psql -U oj_user -d oj_database
```

### Migration from SQLite to Postgres
If you have data in your old SQLite database that you want to migrate to Postgres:
1. Ensure your `.env` or settings are pointing to `db.sqlite3`.
2. Dump only project apps to avoid conflicting internal Django data:
   ```bash
   python manage.py dumpdata accounts problems contests community compiler > fixtures/initial_data.json
   ```
3. Update your settings or `.env` to point to PostgreSQL, and start Postgres via docker.
4. Run migrations first so tables exist in Postgres:
   ```bash
   python manage.py migrate
   ```
5. Finally, load your data:
   ```bash
   python manage.py loaddata fixtures/initial_data.json
   ```

### Data Import & Verification
If you need to manually run the problem import from the seed file, or want to verify data in the database:

1. **Run Import**:
   ```bash
   docker compose exec web python manage.py import_problems \
       OJ/data/problems_seed.json
   ```
2. **Verify via Django Shell**:
   ```bash
   docker compose exec web python manage.py shell -c "from problems.models import Problem; print('Problem count:', Problem.objects.count())"
   ```
3. **Verify via Raw SQL (Inside Postgres Container)**:
   ```bash
   docker compose exec db psql -U oj_user -d oj_database -c "SELECT COUNT(*) FROM problems_problem;"
   ```
4. **Verify Queryset vs DB directly**:
   ```bash
   docker compose exec web python manage.py shell -c "from problems.models import Problem; print('DB Count:', Problem.objects.count(), '| Queryset Count:', Problem.objects.all().count())"
   ```

### Verify Idempotency
You can verify that seeding is idempotent by running it twice. The object counts (problems, testcases, users) should not duplicate:
```bash
python manage.py seed_dev_data
python manage.py seed_dev_data
```

## Safe Submission Directory

Previously, when users submitted code or when you ran test cases, temporary files (`temp_*`, `input_*`, `output_*`, `prog_*`, `Main*.java`) were created directly in the project root. Due to Docker's bind mount (`- .:/app`), these files "leaked" into the host repository and polluted it.

To fix this:
1. **`SUBMISSION_WORKDIR` Setting**: A centralized folder is used, driven by the `SUBMISSION_WORKDIR` environment variable (defaults to `/tmp/judgebox`). 
2. **Dedicated Volume/Container Paths**: In Docker Compose, a separate named volume `submissions_data:/data/submissions` is mounted, setting `SUBMISSION_WORKDIR=/data/submissions`. This completely bypasses the `/app` bind mount.
3. **Per-Run Isolation**: Each code execution generates its own unique subfolder (e.g., `/data/submissions/<uuid>`) ensuring parallel submissions never overwrite files.
4. **Gitignore Safety**: Runtime patterns are added to `.gitignore` as a fallback.

### Resetting Submissions Volume
If the disk space used by temporary test artifacts ever gets too large, you can easily drop the volume and have Docker recreate it:
```bash
docker compose down
docker volume rm oj_project-main_submissions_data
docker compose up -d
```
