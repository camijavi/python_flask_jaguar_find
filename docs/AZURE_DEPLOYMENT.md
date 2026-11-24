# Azure Deployment Guide

This guide documents deployment of JaguarFind & JaguarMaps to the existing Azure App Service. The Flask application serves the web interface, static assets, and REST API together; they are deployed as one application.

## Current Azure Resources

| Resource | Value |
|---|---|
| Resource group | `jaguar-find-rg` |
| App Service plan | `jaguarfind-plan` |
| App Service | `jaguar-find-app-service` |
| Runtime | Linux, Python 3.12 |
| Database | SQLite at `/home/jaguarFind.db` |
| Website | <https://jaguar-find-app-service.azurewebsites.net> |

Useful URLs:

- Web application: <https://jaguar-find-app-service.azurewebsites.net/>
- Campus map: <https://jaguar-find-app-service.azurewebsites.net/map>
- Health check: <https://jaguar-find-app-service.azurewebsites.net/api/health>

## How Deployment Works

The deployment package contains the application files but excludes the local
SQLite database, environment files, and development artifacts. Azure installs
the Python dependencies from `requirements.txt` and runs `startup.sh`, which
starts Gunicorn with the root `app.py` WSGI entry point.

The Flask process serves all application parts:

- Jinja2 pages and templates in `frontend/`
- CSS, JavaScript, and images in `frontend/static/`
- API endpoints registered by `backend/app.py`
- Campus graph and navigation logic in `backend/`

No separate frontend hosting service is needed for the current architecture.

## Database Seeding and Persistence

The app uses SQLite. The repository's `jaguarFind.db` is a local-only file and
is excluded from source control and deployment packages. The live database is
at `/home/jaguarFind.db`, which is persistent App Service storage and is not
replaced by code deployments.

The startup script can copy a seed database if one is deliberately included in
a deployment package, but normal deployments do not include one. To initialize
a new App Service or restore a database, use a deliberate backup/restore or
database initialization procedure; do not rely on the local database file.

The database copy is performed only when `/home/jaguarFind.db` does not
already exist. Re-deploying code therefore preserves changes made to the live
database. Back it up before schema changes or manual data maintenance.

**SQLite is for a single App Service instance.** Do not scale this app out to multiple instances while using SQLite: each instance may have a different local database file. For multi-instance scaling, move persistence to a managed database such as Azure Database for PostgreSQL.

## Deploy or Update

### Prerequisites

- Azure CLI installed and signed in with access to `jaguar-find-rg`
- Python dependencies, including Gunicorn, listed in `requirements.txt`
- The existing App Service database is persisted under `/home/jaguarFind.db`

From the repository root on macOS or Linux:

```bash
az login
az account set --subscription "Azure for Students"

chmod +x startup.sh
zip -r /tmp/jaguarfind-deploy.zip . \
  -x '.git/*' '.venv/*' '__pycache__/*' '*.pyc' '.pytest_cache/*' \
     '.DS_Store' '.env*' 'jaguarFind.db'

az webapp deploy \
  --resource-group jaguar-find-rg \
  --name jaguar-find-app-service \
  --src-path /tmp/jaguarfind-deploy.zip \
  --type zip
```

The App Service startup command should be `./startup.sh`. To inspect or set it:

```bash
az webapp config show \
  --resource-group jaguar-find-rg \
  --name jaguar-find-app-service \
  --query appCommandLine \
  --output tsv

az webapp config set \
  --resource-group jaguar-find-rg \
  --name jaguar-find-app-service \
  --startup-file './startup.sh'
```

Configure the database path and a strong secret key in App Service settings. Do not put secret values in source control or this document:

```bash
az webapp config appsettings set \
  --resource-group jaguar-find-rg \
  --name jaguar-find-app-service \
  --settings \
    DATABASE_PATH='/home/jaguarFind.db' \
    SECRET_KEY='<set-a-strong-random-value>'
```

When setting `SECRET_KEY`, replace the placeholder with a securely generated value. Changing it invalidates existing signed Flask sessions.

## Verify the Deployment

```bash
curl --fail https://jaguar-find-app-service.azurewebsites.net/api/health
curl --fail https://jaguar-find-app-service.azurewebsites.net/map
```

Expected health response includes `"status":"healthy"`. If the app does not start, inspect recent logs:

```bash
az webapp log tail \
  --resource-group jaguar-find-rg \
  --name jaguar-find-app-service
```

## Automatic Deployment from `main`

The GitHub Actions workflow at `.github/workflows/deploy.yml` runs the campus
graph test and deploys the application to the existing App Service whenever
changes are pushed to `main`. It uses GitHub OIDC rather than a publish profile
or client secret.

Run [`scripts/setup-azure-auth-for-pipeline.sh`](../scripts/setup-azure-auth-for-pipeline.sh)
from the repository root after signing in with `az login` and `gh auth login`.
The helper configures the App Service managed identity for Speech, creates a
separate GitHub deployment identity with a federated credential, limits that
identity to this App Service, and sets the required GitHub `production`
environment variables. It also creates the `production` environment with
deployments restricted to `main`.

The App Service identity needs the **Cognitive Services Speech User** role on
the Speech resource. The separate GitHub identity needs **Website Contributor**
on the App Service. Do not grant the GitHub identity Speech data-plane access;
the application identity is responsible for that at runtime.

This workflow deploys application code, not the Speech resource or other Azure
infrastructure. Provision infrastructure separately through reviewed IaC.
The workflow excludes the local `jaguarFind.db`; the live database remains in
persistent App Service storage. `startup.sh` can copy a seed database only if
one is deliberately added to a deployment package and the persistent file
does not already exist.

## Operational Notes

- Keep the App Service at one instance while the application uses SQLite.
- Keep `DATABASE_PATH` set to `/home/jaguarFind.db`; a database under the deployment directory may be replaced during deployment.
- Back up the live database before schema changes or manual data maintenance.
- Keep the local `jaguarFind.db` out of source control and deployment packages; back up the live database before maintenance.
- Keep `SECRET_KEY` in App Service configuration and use a strong random value.
- Confirm the health endpoint and important application workflows after each deployment.

## Related Files

- `startup.sh` — initializes the persistent database location and starts Gunicorn.
- `app.py` — root Flask WSGI entry point.
- `backend/config.py` — environment-based application configuration.
- `backend/database.py` — SQLite schema, initialization, and seed behavior.
- `requirements.txt` — Python dependencies.
