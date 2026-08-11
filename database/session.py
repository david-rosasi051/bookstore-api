import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session

load_dotenv()

# Read env var or set local SQLite fallback for production hosts without DB configured
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./bookstore.db"

# Convert legacy Heroku/Render scheme if applicable
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

IS_DOCKER = os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER") == "true"

# Docker vs host resolution (only applies if using Postgres)
if "postgresql" in DATABASE_URL:
    if not IS_DOCKER and "db:5432" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("db:5432", "localhost:5433")
    elif IS_DOCKER and "localhost" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("localhost:5433", "db:5432").replace("localhost:5432", "db:5432")

# Apply SQLite-specific arguments for multi-thread support
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session