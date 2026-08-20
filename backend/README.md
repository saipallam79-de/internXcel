# InternXcel API

FastAPI service for authentication, internship enrollment, modules, tasks, documents, and admin statistics.

The default local database is SQLite. Copy `.env.example` to `.env` for local overrides or set a MySQL `DATABASE_URL`.

```powershell
pip install -r requirements.txt
uvicorn app.main:app --reload
```
