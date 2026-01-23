"""
Movie routes for the FastAPI application.
Handles all movie-related endpoints including search and embedding generation.
"""

from fastapi import APIRouter, HTTPException, Query
from app.models import (
    SearchRequest, 
    SearchResponse, 
    SearchResult,
    MovieResponse,
    EmbeddingGenerationRequest,
    EmbeddingGenerationResponse
)
from app.database import mongodb
from app.embeddings import embedding_model
from typing import List
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.get("/movies", response_model=List[MovieResponse])
async def get_movies(
    limit: int = Query(10, ge=1, le=100, description="Number of movies to return"),
    skip: int = Query(0, ge=0, description="Number of movies to skip")
):
    """
    Get a list of movies from the database.
    
    - **limit**: Number of movies to return (1-100)
    - **skip**: Number of movies to skip for pagination
    """
    try:
        collection = mongodb.get_collection()
        movies = list(collection.find({}).skip(skip).limit(limit))
        
        # Convert ObjectId to string
        for movie in movies:
            if '_id' in movie:
                movie['_id'] = str(movie['_id'])
        
        return movies
        
    except Exception as e:
        logger.error(f"Error fetching movies: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching movies: {str(e)}")


@router.get("/movies/{movie_id}", response_model=MovieResponse)
async def get_movie(movie_id: str):
    """
    Get a specific movie by ID.
    
    - **movie_id**: The MongoDB ObjectId of the movie
    """
    try:
        from bson import ObjectId
        collection = mongodb.get_collection()
        
        movie = collection.find_one({"_id": ObjectId(movie_id)})
        
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        movie['_id'] = str(movie['_id'])
        return movie
        
    except Exception as e:
        logger.error(f"Error fetching movie: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching movie: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def semantic_search(request: SearchRequest):
    """
    Perform semantic search on movies using vector similarity.
    
    This endpoint:
    1. Takes your search query (e.g., "action movies with robots")
    2. Converts it to an embedding vector
    3. Finds movies with similar plot embeddings using MongoDB Vector Search
    4. Returns the most relevant movies with similarity scores
    
    - **query**: Your search text (e.g., "romantic comedy in Paris")
    - **limit**: Number of results to return (1-20)
    """
    try:
        # Generate embedding for the search query
        logger.info(f"Generating embedding for query: {request.query}")
        query_embedding = embedding_model.get_embedding(request.query)
        
        # Perform vector search
        logger.info("Performing vector search...")
        results = mongodb.vector_search(query_embedding, limit=request.limit)
        
        # Format response
        search_results = [SearchResult(**result) for result in results]
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            count=len(search_results)
        )
        
    except Exception as e:
        logger.error(f"Error performing search: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.post("/embeddings/generate", response_model=EmbeddingGenerationResponse)
async def generate_embeddings(request: EmbeddingGenerationRequest):
    """
    Generate embeddings for movies that don't have them yet.
    
    This is a batch operation that:
    1. Fetches movies from the database (with pagination)
    2. Generates embeddings for their plot descriptions
    3. Updates the database with the embeddings
    
    **Important**: You need to create a vector search index in MongoDB Atlas before using search.
    
    - **limit**: Number of movies to process in this batch (1-1000)
    - **skip**: Number of movies to skip (for processing in batches)
    """
    try:
        collection = mongodb.get_collection()
        
        # Find movies that have a plot but no embedding
        query = {
            "plot": {"$exists": True, "$ne": None, "$ne": ""},
            "plot_embedding": {"$exists": False}
        }
        
        movies = list(collection.find(query).skip(request.skip).limit(request.limit))
        
        if not movies:
            return EmbeddingGenerationResponse(
                success=True,
                processed=0,
                message="No movies found without embeddings"
            )
        
        logger.info(f"Processing {len(movies)} movies...")
        
        # Extract plots and IDs
        plots = [movie.get('plot', '') for movie in movies]
        movie_ids = [str(movie['_id']) for movie in movies]
        
        # Generate embeddings in batch
        logger.info("Generating embeddings...")
        embeddings = embedding_model.get_embeddings(plots)
        
        # Update database
        logger.info("Updating database...")
        updated_count = 0
        for movie_id, embedding in zip(movie_ids, embeddings):
            if mongodb.update_movie_embedding(movie_id, embedding):
                updated_count += 1
        
        return EmbeddingGenerationResponse(
            success=True,
            processed=updated_count,
            message=f"Successfully generated embeddings for {updated_count} movies"
        )
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating embeddings: {str(e)}")


@router.get("/embeddings/stats")
async def embedding_stats():
    """
    Get statistics about embeddings in the database.
    
    Returns:
    - Total number of movies
    - Movies with embeddings
    - Movies without embeddings
    """
    try:
        collection = mongodb.get_collection()
        
        total_movies = collection.count_documents({})
        movies_with_embeddings = collection.count_documents({"plot_embedding": {"$exists": True}})
        movies_without_embeddings = total_movies - movies_with_embeddings
        
        return {
            "total_movies": total_movies,
            "with_embeddings": movies_with_embeddings,
            "without_embeddings": movies_without_embeddings,
            "completion_percentage": round((movies_with_embeddings / total_movies * 100), 2) if total_movies > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")
