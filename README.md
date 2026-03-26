# JudgeBox

A robust, full-featured Online Judge platform built with Django. JudgeBox allows users to solve algorithmic challenges, submit code for execution, and participate in competitive programming contests.

## Features
- **Problem Catalog**: Browse, sort, and filter algorithm problems by difficulty, tags, and status.
- **Code Execution Engine**: Built-in compiler app isolating submissions in Docker volumes to prevent system pollution.
- **Contests**: Structured programming competitions and leaderboards.
- **Community**: Discussion forums and social engagement.
- **Secure Authentication**: User profiles, submission tracking, and login flows.
- **Idempotent Seeding**: Automated tools to populate the platform with problems, test cases, and development users natively.

## Tech Stack
- **Backend:** Python 3, Django 5
- **Database:** PostgreSQL (Production/Docker), SQLite (Local fallback)
- **Frontend:** HTML5, Vanilla JavaScript, CSS, Bootstrap 5 (`django_bootstrap5`)
- **Infrastructure:** Docker & Docker Compose
- **Execution:** Python Subprocess within Docker isolation

## Installation Steps (Development)

### 1. Prerequisites
Ensure you have the following installed:
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- [Python 3.10+](https://www.python.org/downloads/) (for local shell/management commands)

### 2. Clone the Repository
```bash
git clone https://github.com/devagyasv22/Judgebox.git
cd Judgebox
```

### 3. Build & Run via Docker
```bash
docker compose up --build -d
```
The application will be accessible at `http://127.0.0.1:8001/`.

**Static Files:**
Static files (CSS, JS) are served directly by WhiteNoise through the Django application. The Docker setup automatically runs `collectstatic --noinput` on startup.
To rebuild and restart the web container after making static file changes or installing new packages:
```bash
docker compose build web
docker compose up -d web
```

### 4. Fresh Start & Dev DB Workflow
To completely wipe your local database and start fresh with sample data:
```bash
# Bring down containers and wipe volumes
docker compose down -v
docker compose up --build -d

# Run migrations to set up Postgres
docker compose exec web python manage.py migrate

# Seed developer users and problem data
docker compose exec web python manage.py seed_dev_data
```

## Advanced Usage & Maintenance

### Seed Problems + Testcases
Problems and their judging testcases are seeded from `OJ/data/problems_seed.json`.
To (re)import into the database (this UPSERTS safely based on title):
```bash
docker compose exec web python manage.py import_problems
```

### Inspect the Database
To open a psql shell to the running PostgreSQL container:
```bash
docker compose exec db psql -U oj_user -d oj_database
```

### Runner Verification (Dev Only)
To verify that the judge runner’s expected outputs map correctly against a problem test case:
```bash
# Replace '1' with your target problem ID
docker compose exec web python manage.py verify_problem_runner --problem-id 1
```

### Safe Submission Directory
When users submit code, temporary files are safely created in a centralized isolated container folder bypassing your local host. 
- Uses a dedicated Docker volume `submissions_data:/data/submissions`.
- Configured via the `SUBMISSION_WORKDIR` environment variable safely isolated per execution UUID.

If the disk space used by temporary test artifacts ever gets too large, easily drop the volume:
```bash
docker compose down
docker volume rm oj_project-main_submissions_data
docker compose up -d
```

## Folder Structure
```text
OJ_Project-main/
├── OJ/                 # Main Django project settings & routing
├── accounts/           # User authentication and profiles
├── community/          # Social and discussion features
├── compiler/           # Core code execution engine
├── contests/           # Programming competitions
├── problems/           # Problem catalog and management
├── static/             # Global static files (CSS, JS)
├── templates/          # Global Django HTML templates
├── docker-compose.yml  # Docker infrastructure setup
└── Dockerfile          # Django application container definition
```

## Future Improvements
- Expand remote execution sandbox capabilities (e.g. gVisor).
- Add Monaco/CodeMirror integrated IDE for the browser.
- Multi-language bindings (C++, Java, Rust).
- Rank-based Elo leaderboards for community competitions.

## Author
[Devagya Vats](https://github.com/devagyasv22)
