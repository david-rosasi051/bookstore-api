import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5433/bookstore_db"
)

IS_DOCKER = os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER") == "true"

# 1. Running OUTSIDE Docker: map internal 'db:5432' to host 'localhost:5433'
if not IS_DOCKER and "db:5432" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("db:5432", "localhost:5433")

# 2. Running INSIDE Docker: map host 'localhost:5433' or 'localhost:5432' to internal 'db:5432'
elif IS_DOCKER and "localhost" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("localhost:5433", "db:5432").replace("localhost:5432", "db:5432")

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session