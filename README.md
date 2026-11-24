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

### Campus navigation

- Public access without account registration
- Manual origin and destination selection
- Browser GPS-based nearest-node detection
- GPS-based current-location detection
- Shortest pedestrian route calculation with Dijkstra's algorithm
- Optional accessible-route filtering
- Turn-by-turn instructions
- English and Spanish interfaces
- Browser text-to-speech support

### QR codes for official university adoption

**Status: planned, not implemented.** The current application does not read QR-code
location links or provide QR-code deployment support. If UAM adopts JaguarFind as
an official campus site, QR-code entry points should be implemented before that
launch. Scanning a campus QR code with a phone should open the public map and set
the correct, validated campus location as the origin. The university should also
approve the locations, destination URLs, and physical signage.

### Lost-and-found management

- Student, collaborator, visitor, and administrator roles
- Lost-object reporting and categorization
- Three-state custody lifecycle: reported, in custody, and claimed
- Secret-detail anti-fraud validation
- Administrator dashboard and user management
- SQLite-backed persistence

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
| Backend | Python 3, Flask |
| Templates | Jinja2 |
| Production server | Gunicorn |
| Database | SQLite3 |
| Frontend | HTML5, CSS, JavaScript |
| UI styling | Tailwind CSS CDN and custom CSS |
| Routing algorithm | Python `heapq` implementation of Dijkstra |
| Geolocation | Browser Geolocation API and Haversine matching |
| Voice instructions | Browser Web Speech API |
| Internationalization | JSON dictionaries for English and Spanish |
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

- **Camila Javiera Navarro Centeno** - data structures and algorithms
- **Francis Alejandra Solórzano Morales** - backend and persistence
- **James Santiago Fernandez Obregon** - frontend and user experience
- **Elias Abraham Solis Guevara** - administrator panel, QR codes, and integration

## Institution

Universidad Americana (UAM)  
Managua, Nicaragua

## Academic Context

Developed for the Structured Programming and Algorithms / Data Structures course.
