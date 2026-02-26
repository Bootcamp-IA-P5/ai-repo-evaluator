from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from contextlib import asynccontextmanager

from core.database import init_db, get_db
from core.logging_config import setup_logging, logger

# 1. Setup Logging (with colorlog!)
setup_logging()

# 2. Define Lifecycle (Startup/Shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Logic
    logger.info("🚀 Starting Evaluator RAG Backend...")
    init_db() 
    yield
    # Shutdown Logic
    logger.info("🛑 Shutting down Evaluator RAG Backend...")

# 3. Initialize FastAPI
app = FastAPI(
    title="Evaluador RAG API",
    description="Automated GitHub Repository Grading with RAG",
    version="1.0.0",
    lifespan=lifespan
)

# 4. Basic Health Check Endpoint
@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    try:
        # Simple query to verify DB connection is alive
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected"}

@app.get("/", tags=["System"])
def root():
    return {"message": "Welcome to the Evaluador RAG API. Navigate to /docs for Swagger."}  