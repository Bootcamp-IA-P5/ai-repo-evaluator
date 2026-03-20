import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from core.logging_config import logger

# Build database URL from individual environment variables
# This approach handles special characters in passwords (like @, #, etc.)
DB_USER = os.getenv("POSTGRES_USER", "")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "")

# URL-encode the password to handle special characters safely
encoded_password = quote_plus(DB_PASSWORD)
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the Engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal will be used to create a new session for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Triggers table creation based on models.py"""
    try:
        logger.debug("🛠️  Synchronizing database schema...")
        Base.metadata.create_all(bind=engine)
        logger.debug("✅ Database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise e

# Dependency to get DB session in FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()