# Database

The initial schema targets MySQL 8 and mirrors the SQLAlchemy domain model. The local FastAPI default uses SQLite so the API can start without infrastructure; set `DATABASE_URL` in `backend/.env` to switch to MySQL.
