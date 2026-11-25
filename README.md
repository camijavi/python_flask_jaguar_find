# JaguarFind & JaguarMaps

**JaguarFind & JaguarMaps** is a bilingual campus navigation and lost-and-found management system developed for Universidad Americana (UAM) in Managua, Nicaragua.

The project provides a pedestrian wayfinding system for students and visitors and a traceable custody system for lost objects found on campus.

## Project Context

UAM visitors and new students often need to find buildings, classrooms, clinics, laboratories, cafeterias, entrances, and administrative offices across a large campus. Physical signs and fixed maps do not always provide a route from the user's current location.

At the same time, lost objects at the university are traditionally recorded in a physical notebook at Building A. JaguarFind replaces that process with an authenticated digital workflow that records the item, physical custody, and final claim.

The system combines both needs into a shared campus graph:

- **JaguarMaps** lets users calculate pedestrian routes, use GPS or choose a campus location manually, and optionally exclude inaccessible walkways.
- **JaguarFind** lets authorized users report and manage lost objects while administrators control custody and claims.

## Main Features

### JaguarMaps campus navigation

- Public campus map, building directory, and place search for buildings, rooms, and facilities
- Responsive 2D map and 2.5D campus view
- Manual origin and destination selection, plus browser GPS location matching
- Campus and indoor building routes calculated with Dijkstra's algorithm
- Optional accessible routing that avoids stairs where accessible alternatives exist
- Turn-by-turn directions with English and Spanish Azure Speech audio
- English and Spanish interface and route instructions

### QR codes for official university adoption

**Status: planned, not implemented.** The current application does not read QR-code
location links or provide QR-code deployment support. If UAM adopts JaguarFind as
an official campus site, QR-code entry points should be implemented before that
launch. Scanning a campus QR code with a phone should open the public map and set
the correct, validated campus location as the origin. The university should also
approve the locations, destination URLs, and physical signage.

### JaguarFind lost-and-found

- Account registration and sign-in for students, collaborators, and visitors, with administrator access
- Lost-object reports with category, location, description, photo, and private identifying details
- Searchable catalog with category, custody-state, and building filters
- Three-state tracking: reported, in custody, and claimed
- Claim requests with private-detail verification for ownership review
- Map pins for active lost-and-found reports
- Administrator dashboard for custody, reports, and user management

## Graph Structure

The core campus representation is a **weighted, directed, non-complete graph**:

\[
G = (V,E,W)
\]

- **Nodes (`V`)** represent buildings, gates, entrances, classrooms, plazas, cafeterias, sports facilities, and indoor waypoints.
- **Edges (`E`)** represent pedestrian walkways, corridors, ramps, stairs, crosswalks, and skybridges.
- **Weights (`W`)** are walking distances in meters.
- **Bidirectional walkways** are represented as two directed edges.
- **Accessibility** is a boolean edge property used to remove stairs or inaccessible segments from a route.

The campus graph is constructed in [`backend/graph/campusGraphBuilder.py`](/Users/camijavi/Projects/python/python_flask_jaguar_find/backend/graph/campusGraphBuilder.py). The graph implementation uses an adjacency-list representation in [`backend/graph/directedGraph.py`](/Users/camijavi/Projects/python/python_flask_jaguar_find/backend/graph/directedGraph.py).

### Dijkstra routing

The shortest-path engine in [`backend/graph/dijkstraRouter.py`](/Users/camijavi/Projects/python/python_flask_jaguar_find/backend/graph/dijkstraRouter.py) uses:

- A binary min-heap from Python's `heapq` module
- An average walking speed of 72 meters per minute
- Optional accessibility pruning
- Predecessor tracking to reconstruct the complete route
- Translated, turn-by-turn edge instructions

The expected complexity is \(O((V+E)\log V)\). Building subgraphs and room-level structures are located in [`backend/subgraphs/`](/Users/camijavi/Projects/python/python_flask_jaguar_find/backend/subgraphs).

## Technology Stack

| Area | Technology |
|---|---|
| Backend and web framework | Python 3, Flask, Werkzeug |
| Templates | Jinja2 |
| Production server | Gunicorn |
| Database | SQLite (`sqlite3`) |
| Frontend | HTML5, custom CSS, and vanilla JavaScript |
| UI styling | Tailwind CSS CDN and custom CSS |
| Routing algorithm | Dijkstra's algorithm using Python's `heapq` |
| Geolocation | Browser Geolocation API, campus GPS matching, and Haversine calculations |
| Voice instructions | Azure AI Speech REST API, authenticated with Microsoft Entra ID |
| Internationalization | JSON translation dictionaries for English and Spanish |
| Azure integration | `azure-identity`, `requests`, and `python-dotenv` |
| Deployment | Azure App Service for Linux |

## Project Structure

```text
app.py                         Flask application entry point
backend/
  app.py                       Flask application factory
  api/                         REST API route modules
  controllers/                 Web and API controllers
  graph/                       Campus graph and Dijkstra engine
  subgraphs/                   Building and sports-complex subgraphs
  services/                    Business and navigation services
  database.py                  SQLite schema and repositories
  config.py                    Environment-based configuration
frontend/
  screens/                     Jinja2 application screens
  components/                  Reusable Jinja2 components
  static/                      CSS, JavaScript, and images
languages/                     English and Spanish translations
docs/                          Technical and functional documentation
jaguarFind.db                  Local-only SQLite database (ignored by Git)
startup.sh                     Azure App Service startup script
requirements.txt               Python dependencies
```

## Local Development

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Initialize the SQLite database:

```bash
python3 -c "from backend.database import initDb; initDb()"
```

Run the development server:

```bash
python3 app.py
```

Open `http://127.0.0.1:5000`.

Run the campus graph tests:

```bash
python3 testCampusGraph.py
```

## Production

The production entry point is:

```text
gunicorn --bind=0.0.0.0:$PORT --timeout=600 --workers=1 app:app
```

For Azure App Service, set:

```text
DATABASE_PATH=/home/jaguarFind.db
SECRET_KEY=<a strong random secret>
```

The deployment workflow excludes the local `jaguarFind.db`. The live database
is stored at `/home/jaguarFind.db` in persistent App Service storage and is
preserved across code deployments. Initialize or restore a new deployment's
database separately.

## Database Notes

SQLite is appropriate for this class project and a single-instance Azure App Service deployment. For reliable development and deployment:

- Keep App Service scale-out disabled or use one instance.
- Keep the database under `/home`, which is persistent.
- Keep the local `jaguarFind.db` out of Git and deployment packages.
- Back up the live database before schema changes or manual data maintenance.
- For multiple instances or production multi-user scaling, migrate to Azure Database for PostgreSQL or MySQL.

## Authors

- Camila Javiera Navarro Centeno
- Francis Alejandra Solórzano Morales

## Institution

Universidad Americana (UAM)  
Managua, Nicaragua

## Academic Context

Developed for the Structured Programming and Algorithms / Data Structures course.
