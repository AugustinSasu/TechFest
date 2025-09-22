# TechFest — FastAPI + Oracle

Step‑by‑step guide for running the project locally.

> **Prerequisites**
>
> * Python 3.10+ (recommended 3.11)
> * Git
> * Access to an Oracle database (local or remote)
> * (Optional) Oracle Instant Client — *not required when using Thin mode with `oracledb`, but may help in some setups.*

---

## 1) Clone the repository

```bash
# HTTPS
git clone https://github.com/AugustinSasu/TechFest.git
cd TechFest
```

---

## 2) Create and activate a virtual environment (recommended)

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> To deactivate: `deactivate`

---

## 3) Install dependencies

Install individually (as required by the project):

```bash
pip install uvicorn
pip install pydantic
pip install fastapi
pip install sqlalchemy
pip install oracledb
pip install httpx 
pip install pytest
python -m pip install -U email-validator
```



## 4) Environment variables (`.env`)

At the project root, create a `.env` file with the following structure. **Do not commit it** to Git.

```env
# --- Oracle ---
ORACLE_USER=
ORACLE_PASSWORD=
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE=

# (Optional) project-specific vars
# APP_ENV=local
# LOG_LEVEL=INFO
```
---

## 5) Start Oracle Database

Ensure your Oracle instance is up and accessible.

* Example DSN (Thin mode): `host:port/service_name`, e.g. `localhost:1521/XEPDB1` or `db.example.com:1521/ORCLPDB1` or `db2024.example.com:1521/FREEPDB1`
* Test connectivity on first run.

---

## 6) Run the development server

Standard FastAPI command with Uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> **Important:** Replace `main:app` with your actual entrypoint:
>
> * if your app is in `app/main.py` ⇒ `uvicorn app.main:app --reload`
> * if in `src/app.py` ⇒ `uvicorn src.app:app --reload`

Access at: [http://localhost:8000](http://localhost:8000)

Auto-generated docs:

* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 7) Run tests

Run tests with `pytest` (after the server and/or dependencies are ready):

```bash
pytest -q
```

If using integration tests with `httpx`, ensure required endpoints are available or use `TestClient` from `fastapi`.

---

## 8) Example requests

Curl (GET):

```bash
curl -X GET "http://localhost:8000/" 
```

Curl (POST JSON):

```bash
curl -X POST "http://localhost:8000/example" \
  -H "Content-Type: application/json" \
  -d '{"field":"value"}'
```

> Replace routes with the real ones from your project (check `/docs`).

---

## 9) Production deployment (summary)

* Use a production ASGI server (`uvicorn` without `--reload`, or `gunicorn` + `uvicorn.workers.UvicornWorker`).
* Set environment variables at the host or orchestrator level.
* Enable logging and monitoring.

Example (Linux systemd, simplified):

```ini
ExecStart=/path/to/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
EnvironmentFile=/etc/techfest.env
```

---

## 10) Troubleshooting (quick FAQ)

* **`oracledb` connection issues:** double-check `ORACLE_HOST/PORT/SERVICE`, username/password, and network access. Thin mode does not require Instant Client.
* **Port 8000 already in use:** change port with `--port 8080`.
* **`.env` not loading:** ensure your code loads it (e.g. `from dotenv import load_dotenv; load_dotenv()`).

---


