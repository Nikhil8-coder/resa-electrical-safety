# RESA (Reliable Electrical System Addresser) - Stage 2

> **Digital safety coordination platform for electrical grid breakdown management, field Lock-Out / Tag-Out (LOTO) verification, and power restoration clearances.**
> 
> *Disclaimer: Digital coordination only; never replaces physical LOTO, voltage testing, earthing, or field safety standard operating procedures (SOPs). Grid data is mock/emulated.*

---

## 🚀 Live Access Details

- **Public Web Application:** [https://tall-cities-poke.loca.lt/app](https://tall-cities-poke.loca.lt/app) (or `http://127.0.0.1:8000/app`)
- **Interactive Swagger API Docs:** [https://tall-cities-poke.loca.lt/docs](https://tall-cities-poke.loca.lt/docs) (or `http://127.0.0.1:8000/docs`)
- **Localtunnel Password (if prompted):** `106.76.195.198`

### 🔑 Demo Accounts (Password for all: `change-me`)
| Username | Role | Description |
| :--- | :--- | :--- |
| `cit1` | **Citizen** | Emergency breakdown filing, GPS tagging, photo evidence, ticket tracking |
| `op1` | **Substation Operator** | Grid feeder triage, line isolation permits, clearances, restoration authorization |
| `worker1` | **Line Worker** | Field work orders, isolation requests, mandatory 4-step LOTO checklist |
| `pan1` | **Panchayat Admin** | Real-time executive KPIs, incident distributions, SLA resolution metrics |
| `admin` | **System Admin** | Global administrative access, full audit trail visibility, system oversight |

---

## 🛠️ Summary of Diagnosed Issues & Fixes Applied

1. **Pytest Module Collection Failure**
   - Configured `pytest.ini` with `pythonpath = .` and `testpaths = tests` so test discovery runs seamlessly from `backend/`.

2. **Test State Isolation & Database Persistence**
   - Added `load_db: bool = False` by default for isolated, clean unit test runs (`test_acceptance.py`), and `load_db=True` in production (`app/main.py`).
   - Implemented safe upsert patterns with SQLite persistence (`resa.db`) for idempotency across complaints, work orders, and isolation requests.

3. **Multi-Threaded SQLite Crash (`ProgrammingError`)**
   - Resolved multi-threading crash across FastAPI worker threads by configuring `check_same_thread=False` on SQLite database connections.

4. **Frontend API Endpoints & CORS**
   - Added RBAC-filtered endpoints:
     - `GET /api/complaints`: Citizens view own; Workers view assigned; Operators/Admins view all.
     - `GET /api/auth/me`: Active session credentials and role permissions.
     - `GET /api/work-orders`: Assigned work order queue.
     - `GET /api/isolation-requests`: Active and historical isolation permits.
     - `GET /api/users`: Available workers list for dispatching.
     - `GET /app` and `GET /`: Serves the responsive Web Portal.
     - Mounted `CORSMiddleware` with permissive headers for browser and cross-origin access.

5. **Modern Web Portal & UI Suite**
   - 1-Click Persona Switcher toolbar for instant role switching without logout hassle.
   - Live Feeder Line telemetry cards (`LN-204`, `LN-205`, `LN-311`).
   - Interactive OSHA/IEEE Field Safety LOTO verification checklist.
   - Gram Panchayat executive KPI meters and category distribution bar charts.
   - SQLite trigger-enforced immutable audit trail explorer.
   - Automated 1-Click 10-Stage SOP Lifecycle runner.

---

## 🧪 Verification & Test Execution

Run the complete test suite (13 passing tests):
```bash
cd backend
python -m pytest -vv
```

Run the end-to-end demo lifecycle script:
```bash
cd backend
python demo.py
```

Start the FastAPI local development server:
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 🌐 Public Cloud Deployment

### Option 1: Docker
```bash
docker build -t resa-portal .
docker run -p 8000:8000 resa-portal
```

### Option 2: Render
Deploy automatically using the included `render.yaml` or connect this GitHub repo.

### Option 3: Railway / Heroku
Deploy directly via the included `Procfile`.
