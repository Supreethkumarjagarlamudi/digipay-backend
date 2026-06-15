from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

import socket

DATABASE_URL = (
    f"mysql+pymysql://"
    f"{settings.DB_USER}:"
    f"{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:"
    f"{settings.DB_PORT}/"
    f"{settings.DB_NAME}"
)

# Test MySQL connection reachability to determine fallback
use_sqlite = False
if not settings.DB_HOST:
    use_sqlite = True
else:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect((settings.DB_HOST, int(settings.DB_PORT or 3306)))
        s.close()
        print("Database connection test succeeded. Connecting to MySQL production database.")
    except Exception as e:
        print(f"Could not connect to MySQL host {settings.DB_HOST} ({e}). Falling back to local SQLite.")
        use_sqlite = True

if use_sqlite:
    DATABASE_URL = "sqlite:///./digipay.db"

print("Database URL in use:", DATABASE_URL)

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=True
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=True
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()