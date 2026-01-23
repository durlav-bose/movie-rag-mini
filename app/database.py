"""
Database module for MongoDB connection and operations.
Provides connection to MongoDB Atlas and collection access.
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection handler."""
    
    def __init__(self):
        """Initialize MongoDB client."""
        self.client = None
        self.db = None
        self.collection = None
    
    def connect(self):
        """
        Establish connection to MongoDB Atlas.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = MongoClient(settings.MONGODB_URI)
            # Test connection
            self.client.admin.command('ping')
            
            # Get database and collection
            self.db = self.client[settings.MONGODB_DB_NAME]
            self.collection = self.db[settings.MONGODB_COLLECTION_NAME]
            
            logger.info(f"Successfully connected to MongoDB: {settings.MONGODB_DB_NAME}")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def get_collection(self):
        """
        Get the movies collection.
        
        Returns:
            Collection: MongoDB collection object
        """
        if self.collection is None:
            self.connect()
        return self.collection
    
    def find_movies(self, query: dict = {}, limit: int = 10):
        """
        Find movies based on query.
        
        Args:
            query: MongoDB query dict
            limit: Maximum number of results
            
        Returns:
            list: List of movie documents
        """
        collection = self.get_collection()
        movies = list(collection.find(query).limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for movie in movies:
            if '_id' in movie:
                movie['_id'] = str(movie['_id'])
        
        return movies
    
    def vector_search(self, query_embedding: list, limit: int = 5):
        """
        Perform vector similarity search using MongoDB Atlas Vector Search.
        
        Args:
            query_embedding: The embedding vector to search with
            limit: Number of results to return
            
        Returns:
            list: List of similar movies
        """
        collection = self.get_collection()
        
        # MongoDB Atlas Vector Search aggregation pipeline
        pipeline = [
            {
                "$vectorSearch": {
                    "index": settings.VECTOR_INDEX_NAME,
                    "path": "plot_embedding",
                    "queryVector": query_embedding,
                    "numCandidates": limit * 10,
                    "limit": limit
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "title": 1,
                    "plot": 1,
                    "year": 1,
                    "genres": 1,
                    "cast": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Convert ObjectId to string
        for result in results:
            if '_id' in result:
                result['_id'] = str(result['_id'])
        
        return results
    
    def update_movie_embedding(self, movie_id: str, embedding: list):
        """
        Update a movie document with its embedding.
        
        Args:
            movie_id: The movie's ObjectId as string
            embedding: The embedding vector
            
        Returns:
            bool: True if update successful
        """
        from bson import ObjectId
        collection = self.get_collection()
        
        try:
            result = collection.update_one(
                {"_id": ObjectId(movie_id)},
                {"$set": {"plot_embedding": embedding}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating movie embedding: {e}")
            return False


# Create a global MongoDB instance
mongodb = MongoDB()
