"""
Main FastAPI application.
This is the entry point for the Movie RAG API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import mongodb
from app.embeddings import embedding_model
from app.routes import movies
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A RAG (Retrieval-Augmented Generation) API for movie search using embeddings and MongoDB Vector Search",
    debug=settings.DEBUG
)

# Add CORS middleware to allow requests from browsers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Initialize connections and models on application startup.
    This runs once when the FastAPI server starts.
    """
    logger.info("Starting up Movie RAG API...")
    
    # Connect to MongoDB
    if mongodb.connect():
        logger.info("MongoDB connection established")
    else:
        logger.error("Failed to connect to MongoDB")
    
    # Load embedding model
    if embedding_model.load_model():
        logger.info("Embedding model loaded successfully")
    else:
        logger.error("Failed to load embedding model")
    
    logger.info("Startup complete!")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up resources on application shutdown.
    """
    logger.info("Shutting down Movie RAG API...")
    mongodb.disconnect()
    logger.info("Shutdown complete!")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - provides basic API information.
    """
    return {
        "message": "Welcome to Movie RAG API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint - verifies API and database status.
    """
    # Check database connection
    db_status = "connected"
    try:
        mongodb.get_collection()
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
    
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": db_status,
        "embedding_model": settings.EMBEDDING_MODEL_NAME
    }


# Include routers
app.include_router(movies.router, prefix="/api", tags=["Movies"])


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    # Use: python -m app.main
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
