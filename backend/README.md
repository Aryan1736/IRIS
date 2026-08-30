# IRIS / PAIMANA Backend Serving Layer

The backend provides a FastAPI serving layer for the PAIMANA / OCMS project observations derived from historical Flash Report PDF extraction.

> [!IMPORTANT]
> **Data Integrity Principles**:
> - The database is a **derived serving layer** and is never the authoritative source over extraction outputs (`data/processed/projects_monthly.csv`).
> - Canonical data is never modified, normalized, or imputed by the backend.
> - Structurally absent values (such as `start_date` or `ministry` in legacy reports) remain `null` and are never converted to zero or inferred.
> - ML prediction, risk scoring, and alert endpoints use explicit status interfaces (e.g. `NOT_TRAINED`, `MODEL_NOT_DEPLOYED`) and never produce synthetic or mock scores.

---

## 1. Architecture Overview

```
backend/
├── app/
│   ├── api/v1/          # Versioned API routes (/health, /system, /projects)
│   ├── core/            # Configuration (Pydantic Settings), logging, error contracts
│   ├── db/              # SQLAlchemy 2.x base and session management
│   ├── models/          # SQLAlchemy ORM models (ProjectMonthObservation, DatasetMetadata)
│   ├── repositories/    # Data access layer (ProjectRepository, DatasetMetadataRepository)
│   ├── schemas/         # Pydantic v2 schemas and response envelopes
│   ├── services/        # Business logic & ML protocol interfaces (ProjectService, SystemService)
│   └── main.py          # FastAPI application factory and middleware
├── cli/
│   └── ingest.py        # Explicit canonical dataset ingestion CLI with activation safety
├── alembic/             # Database migration scripts
├── tests/               # Pytest suite with hermetic in-memory SQLite fixtures
├── alembic.ini          # Migration configuration
├── requirements.txt     # Backend dependencies
└── README.md
```

---

## 2. Quickstart & Setup

### Prerequisites
- Python 3.13+ (or 3.11+)
- `uv` (recommended) or standard `python -m venv`
- Docker / Docker Compose (optional, for local PostgreSQL)

### 1. Create Virtual Environment and Install Dependencies

```bash
# Using uv (fast)
uv venv .venv
uv pip install -r requirements.txt -r backend/requirements.txt

# Or using standard venv + pip
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt -r backend/requirements.txt
```

### 2. Configure Environment Variables

Copy the template configuration:
```bash
cp backend/.env.example .env
```

Key variables in `.env`:
- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql+psycopg2://postgres:postgres@localhost:5432/paimana_db`)
- `ENVIRONMENT`: `development` | `testing` | `production`
- `API_V1_PREFIX`: `/api/v1`
- `BACKEND_CORS_ORIGINS`: JSON list of allowed origins (e.g. `["http://localhost:3000", "http://localhost:5173"]`)

### 3. Start PostgreSQL (Docker)

To run a local PostgreSQL 16 container:
```bash
docker compose up -d db
```

### 4. Run Database Migrations

Apply Alembic migrations to set up the database schema:
```bash
alembic -c backend/alembic.ini upgrade head
```

To roll back:
```bash
alembic -c backend/alembic.ini downgrade -1
```

To preview raw SQL without executing:
```bash
alembic -c backend/alembic.ini upgrade head --sql
```

### 5. Ingest Canonical Dataset (Explicit CLI)

The backend never automatically ingests CSVs on startup. Use the explicit CLI:

```bash
# For local development/testing (marks dataset ACTIVE):
python -m backend.cli.ingest --csv data/processed/projects_monthly.csv --dev

# For production deployment (verifies exact SHA-256):
python -m backend.cli.ingest --csv data/processed/projects_monthly.csv --expected-sha256 FE115E5FE71CC70552669FC4E0ACC2699B14CFE7545A319EEAEAF577E4DB95C3

# Optional: To clear and reload observations:
python -m backend.cli.ingest --csv data/processed/projects_monthly.csv --dev --clear-existing
```

### 6. Start the FastAPI Development Server

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Interactive API documentation is available at:
- **Swagger UI**: [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)
- **ReDoc**: [http://127.0.0.1:8000/api/v1/redoc](http://127.0.0.1:8000/api/v1/redoc)
- **OpenAPI Schema**: [http://127.0.0.1:8000/api/v1/openapi.json](http://127.0.0.1:8000/api/v1/openapi.json)

---

## 3. Core Project API Endpoints (Pass 2)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/projects` | Paginated project listing with sector, state, agency, report_month, and search filters |
| `GET` | `/api/v1/projects/filters/options` | Dynamic distinct filter values for UI dropdowns |
| `GET` | `/api/v1/projects/search/quick` | Fast autocomplete/discovery search by project code or name |
| `GET` | `/api/v1/projects/{project_code}` | Project-level summary metrics, observation span, and latest snapshot |
| `GET` | `/api/v1/projects/{project_code}/latest-snapshot` | Complete 31-field observation record from the latest report month |
| `GET` | `/api/v1/projects/{project_code}/trajectory` | Full chronological timeline of monthly observations ordered by `report_month ASC` |
| `GET` | `/api/v1/projects/{project_code}/cost-revisions` | Historical cost revisions and cost revision ratio |
| `GET` | `/api/v1/projects/{project_code}/schedule-extensions` | Historical milestones, start dates, and original vs revised completion dates |

### Endpoint Details & Examples

#### 1. `GET /api/v1/projects`
**Query Parameters**:
- `page` (int, default `1`): Page number (1-indexed).
- `page_size` (int, default `20`, max `100`): Number of items per page.
- `project_code` (str, optional): Substring filter for project code.
- `report_month` (str, optional): Exact month filter, e.g. `2026-07`.
- `sector`, `state`, `agency`, `ministry` (str, optional): Case-insensitive category filters.
- `search` (str, optional): Searches across project name, code, and agency.
- `sort_by` (str, default `report_month`): Column to sort by.
- `sort_order` (`asc` | `desc`, default `desc`): Sort direction.

**Example Response**:
```json
{
  "items": [
    {
      "id": 1,
      "project_code": "201234",
      "project_name": "Mumbai Metro Line 4",
      "agency": "MMRDA",
      "ministry": "HOUSING AND URBAN AFFAIRS",
      "sector": "URBAN DEVELOPMENT",
      "state": "MAHARASHTRA",
      "report_month": "2026-07",
      "approval_date": "2016-10",
      "original_completion_date": "2022-12",
      "revised_completion_date": "2026-12",
      "original_cost": 14549.0,
      "revised_cost": 18500.0,
      "cumulative_expenditure": 9400.0,
      "physical_progress": 57.0
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

#### 2. `GET /api/v1/projects/filters/options`
Returns non-null distinct options currently present in the database:
```json
{
  "sectors": ["RAILWAYS", "ROAD TRANSPORT AND HIGHWAYS", "URBAN DEVELOPMENT"],
  "states": ["KARNATAKA", "MAHARASHTRA", "TELANGANA"],
  "agencies": ["DFCCIL", "MMRDA", "NHAI"],
  "ministries": ["HOUSING AND URBAN AFFAIRS", "RAILWAYS", "ROAD TRANSPORT AND HIGHWAYS"],
  "report_months": ["2026-07", "2026-06", "2024-06"]
}
```

#### 3. `GET /api/v1/projects/search/quick?q=metro`
Returns lightweight discovery matches:
```json
[
  {
    "project_code": "201234",
    "project_name": "Mumbai Metro Line 4",
    "agency": "MMRDA",
    "latest_report_month": "2026-07"
  }
]
```

#### 4. `GET /api/v1/projects/{project_code}`
Returns high-level summary and latest observation:
```json
{
  "project_code": "201234",
  "project_name": "Mumbai Metro Line 4",
  "agency": "MMRDA",
  "ministry": "HOUSING AND URBAN AFFAIRS",
  "sector": "URBAN DEVELOPMENT",
  "state": "MAHARASHTRA",
  "first_reported_month": "2024-06",
  "latest_report_month": "2026-07",
  "total_observations_count": 25,
  "latest_observation": { ... }
}
```

#### 5. `GET /api/v1/projects/{project_code}/trajectory`
Returns chronological observations ordered by `report_month ASC`:
```json
{
  "project_code": "201234",
  "project_name": "Mumbai Metro Line 4",
  "observations_count": 2,
  "trajectory": [
    {
      "report_month": "2025-08",
      "original_cost": 14549.0,
      "revised_cost": 18500.0,
      "cumulative_expenditure": 9200.0,
      "physical_progress": 55.0,
      "approval_date": "2016-10",
      "start_date": "2018-06",
      "original_completion_date": "2022-12",
      "revised_completion_date": "2026-12",
      "agency": "MMRDA",
      "ministry": "HOUSING AND URBAN AFFAIRS",
      "sector": "URBAN DEVELOPMENT",
      "state": "MAHARASHTRA"
    }
  ]
}
```

---

## 4. Risk Intelligence Endpoints

Backed by the deterministic, locked serving artifact (`data/serving/iris_risk_serving_v1.sqlite3`):

- `GET /api/v1/risk/options` — Available evaluation report months, default active month, available regimes, and distinct non-null metadata filter values.
- `GET /api/v1/risk/summary` — Portfolio score distribution quantiles (p25, median, p75, p90, p95), regime metadata, sector summaries, and top-N ranked projects.
- `GET /api/v1/risk/projects` — Paginated list of projects ordered by `risk_rank`, with calibrated probabilities, percentiles, and signed feature contributors.
- `GET /api/v1/risk/project/{project_code}` — Single project `RiskRecord` for a specific report month with top positive/negative TreeSHAP/logistic contributors.
- `GET /api/v1/risk/project/{project_code}/history` — Chronological risk history for an exact project code.
- `GET /api/v1/risk/model-info` — Model governance, methodology, target specification, and feature counts.

---

## 5. Foundation Endpoints

- `GET /api/v1/health` — Verifies API health and live database connection (`SELECT 1`).
- `GET /api/v1/system/dataset-info` — Inspects currently active dataset version, canonical SHA-256 hash, and monthly coverage.

---

## 6. Structured Error Envelope & Request Tracing

All API errors return a standard JSON envelope with correlation tracing:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Project with code 'NON_EXISTENT' was not found in the serving layer.",
    "details": null
  },
  "request_id": "req-9a3b7c8d1e2f"
}
```

---

## 7. Running Automated Tests

The test suite runs hermetically against in-memory SQLite and temporary serving artifacts:

```bash
# Run all backend tests (51 tests)
pytest backend/tests/ -v

# Run extraction parser & validation regression tests (22 tests)
python -m unittest tests.test_parsers tests.test_validation -v
```

