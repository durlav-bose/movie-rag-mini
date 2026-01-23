"""
Pydantic models for request/response validation.
These models define the structure of data sent to and from the API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class MovieResponse(BaseModel):
    """Response model for a single movie."""
    
    id: str = Field(alias="_id", description="Movie ID")
    title: str = Field(description="Movie title")
    plot: Optional[str] = Field(None, description="Movie plot/description")
    year: Optional[int] = Field(None, description="Release year")
    genres: Optional[List[str]] = Field(None, description="Movie genres")
    cast: Optional[List[str]] = Field(None, description="Cast members")
    
    class Config:
        populate_by_name = True


class SearchRequest(BaseModel):
    """Request model for semantic search."""
    
    query: str = Field(..., description="Search query text", min_length=1)
    limit: int = Field(5, description="Number of results to return", ge=1, le=20)


class SearchResult(BaseModel):
    """Response model for search results with similarity score."""
    
    id: str = Field(alias="_id", description="Movie ID")
    title: str = Field(description="Movie title")
    plot: Optional[str] = Field(None, description="Movie plot")
    year: Optional[int] = Field(None, description="Release year")
    genres: Optional[List[str]] = Field(None, description="Movie genres")
    cast: Optional[List[str]] = Field(None, description="Cast members")
    score: float = Field(description="Similarity score")
    
    class Config:
        populate_by_name = True


class SearchResponse(BaseModel):
    """Response model for search endpoint."""
    
    query: str = Field(description="Original search query")
    results: List[SearchResult] = Field(description="List of matching movies")
    count: int = Field(description="Number of results returned")


class EmbeddingGenerationRequest(BaseModel):
    """Request model for generating embeddings."""
    
    limit: Optional[int] = Field(100, description="Number of movies to process", ge=1, le=1000)
    skip: Optional[int] = Field(0, description="Number of movies to skip", ge=0)


class EmbeddingGenerationResponse(BaseModel):
    """Response model for embedding generation."""
    
    success: bool = Field(description="Whether operation was successful")
    processed: int = Field(description="Number of movies processed")
    message: str = Field(description="Status message")


class HealthResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(description="API status")
    version: str = Field(description="API version")
    database: str = Field(description="Database connection status")
