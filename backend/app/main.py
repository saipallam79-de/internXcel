from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text

from app.core.config import settings
from app.core.security import hash_password
from app.database.database import Base, SessionLocal, engine
from app.models import Certificate, Domain, Internship, Module, OfferLetter, Submission, Task, User
from app.routes import admin, auth, certificates, dashboard, domains, engagement, internships, modules, tasks, users

app = FastAPI(title="InternXcel API", version="0.1.0", description="Internship management platform API")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(domains.router)
app.include_router(internships.router)
app.include_router(modules.router)
app.include_router(tasks.router)
app.include_router(certificates.router)
app.include_router(certificates.offer_router)
app.include_router(admin.router)
app.include_router(dashboard.router)
app.include_router(engagement.router)


def bootstrap_database() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user_columns = db.execute(text("PRAGMA table_info(users)")).fetchall()
        user_column_names = {column[1] for column in user_columns}
        if "status" not in user_column_names:
            db.execute(text("ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active'"))
            db.commit()
        if "created_at" not in user_column_names:
            db.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
            db.commit()
        if db.scalar(select(User.id)) is None:
            db.add_all([
                User(
                    full_name="Admin User",
                    email="admin@internxcel.dev",
                    mobile="9999999999",
                    college="InternXcel",
                    degree="Admin",
                    branch="Operations",
                    year=0,
                    password_hash=hash_password("admin123"),
                    role="admin",
                    status="active",
                ),
                User(
                    full_name="Alice Johnson",
                    email="student1@test.com",
                    mobile="1111111111",
                    college="State University",
                    degree="B.Tech",
                    branch="CSE",
                    year=2,
                    password_hash=hash_password("test123"),
                    role="student",
                    status="active",
                ),
                User(
                    full_name="Bob Smith",
                    email="student2@test.com",
                    mobile="2222222222",
                    college="Tech Institute",
                    degree="B.E.",
                    branch="IT",
                    year=3,
                    password_hash=hash_password("test123"),
                    role="student",
                    status="active",
                ),
            ])
            db.commit()
    finally:
        db.close()


bootstrap_database()


@app.get("/api/health", tags=["system"])
@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "internxcel-api"}
