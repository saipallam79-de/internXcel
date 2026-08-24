# InternXcel

InternXcel is a full-stack internship management platform for students and administrators.

## Run locally

### Backend

```powershell
cd D:\internXcel
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

API docs: http://127.0.0.1:8000/docs

### Frontend

Open `frontend/index.html` directly, or serve the repository with any static server.

The frontend is wired to the live FastAPI routes and keeps all student data scoped to the authenticated user account.

## Product promise

**Learn. Build. Complete. Get Certified.**
