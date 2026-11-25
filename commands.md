# JaguarFind - Developer Commands & Build Guide

Guide for running, testing, and building the JaguarFind Python Flask application (Backend + Frontend).

---

## 1. Virtual Environment Setup

### Create Virtual Environment
```bash
# Windows
python -m venv .venv

# macOS / Linux
python3 -m venv .venv
```

### Activate Virtual Environment
```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.\.venv\Scripts\activate.bat

# macOS / Linux (Bash/Zsh)
source .venv/bin/activate
```

### Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2. Running in Development Environment

Because JaguarFind uses Python Flask for both backend services (APIs, Dijkstra routing, database) and frontend rendering (Jinja2 screens, component partials, and static CSS/JS), a single server command boots both simultaneously.

### Option A: Using Flask CLI (Recommended with Live Reload)

#### Windows (PowerShell)
```powershell
$env:FLASK_APP = "backend/app.py"
$env:FLASK_DEBUG = "1"
flask run --host=127.0.0.1 --port=5000
```

#### Windows (CMD)
```cmd
set FLASK_APP=backend/app.py
set FLASK_DEBUG=1
flask run --host=127.0.0.1 --port=5000
```

#### macOS / Linux
```bash
export FLASK_APP=backend/app.py
export FLASK_DEBUG=1
flask run --host=127.0.0.1 --port=5000
```

### Option B: Running Directly with Python
```bash
python -m backend.app
```

Once running, access the application in your browser:
- **Web App (Frontend Screens):** [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **API Endpoints (Backend Services):** [http://127.0.0.1:5000/api](http://127.0.0.1:5000/api)

---

## 3. Running Verification & Graph Tests

Run the full campus graph test suite (Dijkstra algorithm, wheelchair accessibility pruning, POI discovery, and GPS Haversine detection):

```bash
# Windows (PowerShell with UTF-8 support)
$env:PYTHONUTF8 = "1"; python -m tests.testCampusGraph

# macOS / Linux
python3 -m tests.testCampusGraph
```

---

## 4. Database Setup & Seeding

Initialize the SQLite database schema and seed default data (campus nodes, catalog categories):

```bash
# Initialize SQLite database tables
python -c "from backend.database import initDb; initDb()"
```

---

## 5. Production Build & Deployment

In a Python Flask stack, building and deploying involves preparing production WSGI workers, locking dependencies, and optionally creating a container build:

### Step 1: Update Dependency Lockfile
```bash
pip freeze > requirements.txt
```

### Step 2: Run Production WSGI Server

#### Windows (Waitress)
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 backend.app:app
```

#### Linux / macOS (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "backend.app:app"
```

### Step 3: Container Build (Docker)
```bash
# Build the production image
docker build -t jaguarfind:latest .

# Run the container
docker run -d -p 5000:5000 --name jaguarfind-prod jaguarfind:latest
```

---

## 6. Project Directory Reference

- **Backend Logic & Services:** [`backend/`](file:///c:/Users/user/Documents/projects/python_flask_jaguar_find/backend)
  - APIs, Controllers, Services, Models, Database, and Dijkstra Campus Graph.
- **Frontend Screens & Components:** [`frontend/`](file:///c:/Users/user/Documents/projects/python_flask_jaguar_find/frontend)
  - `screens/`: Jinja2 HTML templates for each app page.
  - `components/`: Modular HTML partials and dialogs.
  - `static/`: Modular CSS stylesheets (`static/css/`) and JavaScript scripts (`static/js/`).
