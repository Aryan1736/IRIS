# IRIS Deployment Guide

Production deployment architecture for the **IRIS (PAIMANA)** infrastructure risk intelligence platform targeting:
- **Frontend**: Vercel (Hobby Free Tier)
- **Backend API**: Render (Free Web Service)
- **Database**: Neon Serverless PostgreSQL (Free Tier)
- **ML Serving**: Embedded in FastAPI backend service via deterministic SQLite artifact

---

## Architecture Overview

```
[ Web Users ]
      │
      ▼ (HTTPS)
┌─────────────────────────────────────────────────────────┐
│               FRONTEND: Vercel (Hobby)                  │
│  - React 19 + TypeScript + Vite Single-Page Application │
│  - Client-side SPA routing via vercel.json rewrites     │
│  - Configured with VITE_API_BASE_URL                    │
└──────────────────────────┬──────────────────────────────┘
                           │ (HTTPS REST Calls)
                           ▼
┌─────────────────────────────────────────────────────────┐
│              BACKEND: Render Free Web Service           │
│  - FastAPI (Python 3.11 / Uvicorn ASGI Server)          │
│  - Listens on 0.0.0.0:$PORT                             │
│  - CORS configured via FRONTEND_ORIGIN                  │
├─────────────────────────────────────────────────────────┤
│                     DATA LAYERS                         │
│                                                         │
│  [ Primary Observations DB ]      [ Risk ML Artifact ]  │
│  • Neon PostgreSQL 16             • Read-only SQLite    │
│  • 64,608 project-months          • 25,189 risk records │
│  • 4,738 unique projects          • 250,570 TreeSHAP/   │
│  • Seeded from canonical CSV        logistic features   │
└─────────────────────────────────────────────────────────┘
```

---

## 1. Create Neon PostgreSQL Database

1. Sign up or log in at [neon.tech](https://neon.tech).
2. Click **Create Project**:
   - **Project Name**: `iris-production`
   - **Region**: Select the region closest to your users or Render service (e.g., `us-east-2` Ohio or `eu-central-1` Frankfurt).
   - **PostgreSQL Version**: `16`
3. After creation, copy the **Connection string** from the Neon dashboard.
   - Choose **Pooled connection** (recommended for serverless connection pooling).
   - Ensure `sslmode=require` is present in the connection string.
   - Example connection string:
     ```text
     postgresql://neondb_owner:npg_SECRET@ep-xyz-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
     ```

---

## 2. Initialize Database (Schema Migrations)

Apply Alembic migrations to set up the `dataset_metadata` and `project_month_observations` tables in your Neon database.

From the repository root on your local terminal:

```bash
# On Linux/macOS:
export DATABASE_URL="postgresql://neondb_owner:npg_SECRET@ep-xyz-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
python -m alembic -c backend/alembic.ini upgrade head

# On Windows PowerShell:
$env:DATABASE_URL="postgresql://neondb_owner:npg_SECRET@ep-xyz-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
.\.venv\Scripts\python.exe -m alembic -c backend/alembic.ini upgrade head
# (or activate venv: .\.venv\Scripts\Activate.ps1 && python -m alembic -c backend/alembic.ini upgrade head)
```

---

## 3. Load Canonical Dataset

Populate the 64,608 historical project-month observations and lineage metadata into the Neon database using the explicit ingestion CLI:

```bash
# Using the --database-url flag directly:
python -m backend.cli.ingest --csv data/processed/projects_monthly.csv --database-url "postgresql://neondb_owner:npg_SECRET@ep-xyz-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require" --dev

# OR using the DATABASE_URL environment variable:
python -m backend.cli.ingest --csv data/processed/projects_monthly.csv --dev
```

*Note: Ingestion completes in approximately 3 to 6 seconds.*

---

## 4. Verify Database

Verify that records are successfully loaded by querying the dataset endpoint or database directly:

```bash
# Run quick verification one-liner:
python -c "from backend.app.db.session import create_db_engine; from sqlalchemy import text; engine=create_db_engine('$env:DATABASE_URL'); conn=engine.connect(); print('Observations:', conn.execute(text('SELECT count(*) FROM project_month_observations')).scalar()); print('Active Dataset:', conn.execute(text('SELECT dataset_version, status, row_count FROM dataset_metadata WHERE status=\'ACTIVE\'')).fetchone()); conn.close()"
```

**Expected Counts**:
- `project_month_observations`: **64,608 rows**
- `unique projects`: **4,738 projects**
- `dataset_metadata`: **1 ACTIVE record** with SHA-256 `9512A9881E17DFDED6E182D87A8DFB1C4EDBD36C0D9B8A7DA9FD1ABB7E002FBF`

---

## 5. Deploy Render Backend

### Option A: Via Render Dashboard
1. Go to [dashboard.render.com](https://dashboard.render.com) and click **New +** → **Web Service**.
2. Connect your Git repository.
3. Configure the service:
   - **Name**: `iris-backend`
   - **Region**: Same or close to Neon region (e.g. `Ohio (US East)`)
   - **Branch**: `main`
   - **Root Directory**: Leave blank (repository root)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt -r backend/requirements.txt`
   - **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
4. Add **Environment Variables**:
   | Variable | Value | Description |
   |---|---|---|
   | `PYTHON_VERSION` | `3.11.9` | Python runtime version |
   | `ENVIRONMENT` | `production` | Production environment flag |
   | `DEBUG` | `false` | Disable debug logs |
   | `DATABASE_URL` | `postgresql://...sslmode=require` | Your Neon connection string |
   | `SERVING_DIR` | `data/serving` | Serving artifact location |
   | `FRONTEND_ORIGIN` | `https://iris-frontend.vercel.app` | Your Vercel frontend URL |
5. Click **Create Web Service**.
6. Once deployed, copy your Render service URL (e.g., `https://iris-backend.onrender.com`).

### Option B: Via Render Blueprint (`render.yaml`)
1. Click **New +** → **Blueprint**.
2. Select your repository. Render will automatically parse `render.yaml`.
3. Provide the secret environment variables (`DATABASE_URL`, `FRONTEND_ORIGIN`) when prompted.

---

## 6. Deploy Vercel Frontend

1. Go to [vercel.com](https://vercel.com) and click **Add New...** → **Project**.
2. Import your Git repository.
3. Configure Project Settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (or `tsc -b && vite build`)
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`
4. Add **Environment Variables**:
   | Variable | Value | Description |
   |---|---|---|
   | `VITE_API_BASE_URL` | `https://iris-backend.onrender.com` | Your deployed Render backend URL |
5. Click **Deploy**.
6. Vercel will build and assign a production URL (e.g., `https://iris-frontend.vercel.app`).

---

## 7. Configure CORS

Update the `FRONTEND_ORIGIN` on your Render service to match your exact Vercel production domain:

1. In the Render dashboard, navigate to `iris-backend` → **Environment**.
2. Set `FRONTEND_ORIGIN` = `https://iris-frontend.vercel.app` (or comma-separated list if using multiple preview domains).
3. Save changes. Render will automatically redeploy with updated CORS origins.

---

## 8. Verify API Endpoints

Test the live backend endpoints using `curl` or a browser:

```bash
# 1. Health check
curl -s https://iris-backend.onrender.com/api/v1/health
# Expected: {"status":"HEALTHY","database":"CONNECTED","environment":"production","version":"0.1.0",...}

# 2. System dataset lineage
curl -s https://iris-backend.onrender.com/api/v1/system/dataset-info
# Expected: {"status":"ACTIVE","row_count":64608,"canonical_sha256":"9512A9881E17DFDED6E182D87A8DFB1C4EDBD36C0D9B8A7DA9FD1ABB7E002FBF",...}

# 3. Project listing
curl -s "https://iris-backend.onrender.com/api/v1/projects?page=1&page_size=5"
# Expected: {"items":[...],"total":64608,"page":1,"page_size":5,"total_pages":12922}

# 4. Risk intelligence dashboard options
curl -s https://iris-backend.onrender.com/api/v1/risk/options
# Expected: {"report_months":["2023-07",...,"2026-04"],"default_report_month":"2026-04",...}

# 5. Model governance information
curl -s https://iris-backend.onrender.com/api/v1/risk/model-info
# Expected: {"status":"READY","target":"target_effective_schedule_ext_3m","models":[...]}

# 6. Portfolio risk summary
curl -s "https://iris-backend.onrender.com/api/v1/risk/summary?report_month=2026-04&top_n=5"
# Expected: {"report_month":"2026-04","project_count":1625,"score_distribution":{...},"top_risk_projects":[...]}
```

---

## 9. Verify Frontend Routes

Open your Vercel URL in a browser and verify each page and interaction:

1. **Landing Page (`/`)**:
   - Verify Hero section, Typing headline, Architecture manifesto, and navigation buttons.
2. **Dashboard Overview (`/dashboard`)**:
   - Verify live KPI grid, portfolio score distribution chart, and early warning risk section.
3. **Projects Discovery (`/projects`)**:
   - Test search by project code/name, dropdown filters (Sector, Agency, State, Month), and pagination.
4. **Project Detail (`/projects/:projectCode`)**:
   - Navigate to a project (e.g. `/projects/200101` or `/projects/201234`).
   - Verify 31-field latest snapshot, chronological trajectory charts, cost revision ratio, and milestone timeline.
   - **Test browser refresh** (press F5 / Cmd+R) to confirm SPA routing fallback works without 404.
5. **Analytics (`/analytics`)**:
   - Verify portfolio time-series trendlines, expenditure trajectories, and sector distributions.
6. **Intelligence (`/intelligence`)**:
   - Verify server-ranked risk table, TreeSHAP / logistic feature contributor drawer, and chronological risk history.

---

## 10. Troubleshooting & FAQ

### Issue: Initial API Request Takes 30–50 Seconds (Cold Start)
- **Cause**: Render Free Web Services sleep after 15 minutes of inactivity.
- **Solution**: This is expected free-tier behavior. The frontend displays graceful loading indicators. Once awake, response latency is < 50ms. To prevent sleep during live demos, set up a free uptime monitor (e.g. [cron-job.org](https://cron-job.org) or [uptimerobot.com](https://uptimerobot.com)) pinging `GET /api/v1/health` every 10 minutes.

### Issue: CORS Error in Browser Console
- **Cause**: The backend `FRONTEND_ORIGIN` does not match the frontend's actual URL.
- **Solution**: Add your exact Vercel URL (e.g., `https://iris-frontend.vercel.app`) to `FRONTEND_ORIGIN` in the Render environment settings.

### Issue: Direct URL Refresh Returns 404 on Vercel
- **Cause**: Missing SPA fallback rewrite configuration.
- **Solution**: Ensure `frontend/vercel.json` contains the rewrite rule:
  ```json
  {
    "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
  }
  ```

### Issue: 503 "Serving artifact is unavailable"
- **Cause**: The locked SQLite file `data/serving/iris_risk_serving_v1.sqlite3` was omitted or its hash was modified.
- **Solution**: Ensure `data/serving/iris_risk_serving_v1.sqlite3` is committed in Git (un-ignored in `.gitignore`) and present in the deployed filesystem at `SERVING_DIR`.

---

## 11. Free-Tier Reality & SLA Notes

- **Vercel Hobby**: 100 GB bandwidth/month, unlimited static deployments. 100% Free.
- **Render Free**: 512 MB RAM, 0.1 CPU, 750 free instance hours/month (spins down on idle).
- **Neon Free**: 0.5 GB storage (IRIS uses ~45 MB), pooled connections, automated branching.
- **Total Cost**: **$0.00 / month** on standard free tiers.
