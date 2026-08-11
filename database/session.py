import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session

load_dotenv()

# Get database URL or fall back to local SQLite for zero-config environments (e.g. Render)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./bookstore.db"

# Fix legacy Heroku/Render Postgres URL scheme if needed
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

IS_DOCKER = os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER") == "true"

# 1. Running OUTSIDE Docker: map internal 'db:5432' to host 'localhost:5433'
if not IS_DOCKER and "db:5432" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("db:5432", "localhost:5433")

# 2. Running INSIDE Docker: map host 'localhost' to internal 'db:5432'
elif IS_DOCKER and "localhost" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("localhost:5433", "db:5432").replace("localhost:5432", "db:5432")

# SQLite requires specific multi-threading arguments
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session