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

The deployment package contains the entire repository. Azure installs the Python dependencies from `requirements.txt` and runs `startup.sh`, which starts Gunicorn with the root `app.py` WSGI entry point.

The Flask process serves all application parts:

- Jinja2 pages and templates in `frontend/`
- CSS, JavaScript, and images in `frontend/static/`
- API endpoints registered by `backend/app.py`
- Campus graph and navigation logic in `backend/`

No separate frontend hosting service is needed for the current architecture.

## Database Seeding and Persistence

The app uses SQLite. On its first start, `startup.sh` copies the deployed `jaguarFind.db` to `/home/jaguarFind.db`. The `/home` directory is persistent App Service storage, so later code deployments do not replace the live database.

To initialize a new deployment with the existing data:

1. Make sure `jaguarFind.db` is present in the deployment package. It is intentionally allowed by `.gitignore`; if deploying from a Git checkout, verify that the database is included in the package.
2. Deploy the application using the instructions below.
3. Check `/api/health` and the map page after deployment.

The database is copied only when `/home/jaguarFind.db` does not already exist. Re-deploying code therefore preserves changes made to the live database. To refresh or replace the live database, back it up first and use a deliberate database migration/replacement procedure; do not expect an ordinary code deployment to refresh its contents.

**SQLite is for a single App Service instance.** Do not scale this app out to multiple instances while using SQLite: each instance may have a different local database file. For multi-instance scaling, move persistence to a managed database such as Azure Database for PostgreSQL.

## Deploy or Update

### Prerequisites

- Azure CLI installed and signed in with access to `jaguar-find-rg`
- Python dependencies, including Gunicorn, listed in `requirements.txt`
- The intended, sanitized `jaguarFind.db` file in the repository root

From the repository root on macOS or Linux:

```bash
az login
az account set --subscription "Azure for Students"

chmod +x startup.sh
zip -r /tmp/jaguarfind-deploy.zip . \
  -x '.git/*' '.venv/*' '__pycache__/*' '*.pyc' '.pytest_cache/*' '.DS_Store'

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

## Operational Notes

- Keep the App Service at one instance while the application uses SQLite.
- Keep `DATABASE_PATH` set to `/home/jaguarFind.db`; a database under the deployment directory may be replaced during deployment.
- Back up the live database before schema changes or manual data maintenance.
- Treat any database packaged for deployment as data that will be published to the running app. Remove test accounts, personal data, and default credentials before deployment.
- Keep `SECRET_KEY` in App Service configuration and use a strong random value.
- Confirm the health endpoint and important application workflows after each deployment.

## Related Files

- `startup.sh` — initializes the persistent database location and starts Gunicorn.
- `app.py` — root Flask WSGI entry point.
- `backend/config.py` — environment-based application configuration.
- `backend/database.py` — SQLite schema, initialization, and seed behavior.
- `requirements.txt` — Python dependencies.
