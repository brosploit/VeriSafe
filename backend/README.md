# VeriSafe - Backend

Backend service for **VeriSafe** (by Team Shadow Paradox: *Detect. Understand. Verify.*), built with FastAPI and Uvicorn.

---

## 1. Setup & Installation (Windows PowerShell)

Ensure Python 3.10+ is installed.

### 1.1 Activate the Virtual Environment
A virtual environment has already been created at `backend/.venv`. Activate it using Windows PowerShell:

```powershell
# Navigate to the backend directory if not already there:
cd backend

# If running scripts is restricted by PowerShell execution policy, run:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

# Activate the virtual environment:
.\.venv\Scripts\Activate.ps1
```

*(Note: In Git Bash / Linux / macOS, use `source .venv/Scripts/activate` or `source .venv/bin/activate`.)*

### 1.2 Install Dependencies
Install the required packages from `requirements.txt`:

```powershell
pip install -r requirements.txt
```

---

## 2. Running the Development Server

From inside the `backend/` directory with the virtual environment activated:

```powershell
uvicorn app.main:app --reload --port 8000
```

The server will be available at:
- **Base URL:** http://127.0.0.1:8000/
- **Interactive API Docs (Swagger UI):** http://127.0.0.1:8000/docs
- **Alternative Docs (ReDoc):** http://127.0.0.1:8000/redoc
- **Health Check Endpoint:** http://127.0.0.1:8000/api/health

---

## 3. Directory Layout

```text
backend/
├── .venv/               # Python virtual environment
├── app/
│   ├── __init__.py      # Package indicator
│   └── main.py          # FastAPI application entrypoint
├── requirements.txt     # Python dependencies
└── README.md            # Backend setup instructions
```

