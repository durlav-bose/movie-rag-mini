# Movie RAG API

A FastAPI-based RAG (Retrieval-Augmented Generation) system for semantic movie search using HuggingFace embeddings and MongoDB Atlas Vector Search.

## 🎯 What This Project Does

This API allows you to:
- **Search movies semantically**: Search for movies using natural language (e.g., "romantic movies set in Paris")
- **Generate embeddings**: Convert movie plots into vector embeddings using AI
- **Vector similarity search**: Find similar movies based on plot content using MongoDB Atlas Vector Search

## 🏗️ Project Structure

```
rag-mini/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and environment variables
│   ├── database.py          # MongoDB connection and operations
│   ├── embeddings.py        # HuggingFace embedding model handling
│   ├── models.py            # Pydantic models for request/response
│   └── routes/
│       ├── __init__.py
│       └── movies.py        # Movie-related API endpoints
├── .env                     # Environment variables (DO NOT commit to Git)
├── .env.example             # Example environment file
├── .gitignore              # Git ignore file
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 📋 Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account with a cluster
- HuggingFace account (for access token)

## 🚀 Setup Instructions

### 1. Install Python Dependencies

The required packages are already installed:
```bash
# Already installed:
# - fastapi
# - uvicorn
# - sentence-transformers
# - pymongo
# - python-dotenv
# - pydantic
```

### 2. Environment Variables

Your environment is already configured in `.env`. The file contains:
- MongoDB connection URI
- Database name: `sample_mflix`
- HuggingFace access token
- Embedding model configuration

### 3. Create MongoDB Vector Search Index

**IMPORTANT**: Before you can use the search functionality, you need to create a vector search index in MongoDB Atlas.

#### Steps to create the index:

1. Go to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Navigate to your cluster
3. Click on "Search" tab
4. Click "Create Search Index"
5. Choose "JSON Editor"
6. Use the following configuration:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "plot_embedding",
      "numDimensions": 384,
      "similarity": "cosine"
    }
  ]
}
```

7. Name the index: `movie_embeddings_index`
8. Select database: `sample_mflix`
9. Select collection: `movies`
10. Click "Create Search Index"

**Note**: Index creation may take a few minutes.

## 🏃 Running the Application

### Start the FastAPI server:

```bash
cd /home/durlav-bose/rag-mini
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the simpler command:
```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

### Access the Interactive API Documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 API Endpoints

### 1. Root Endpoint
```
GET /
```
Returns basic API information.

### 2. Health Check
```
GET /health
```
Checks API and database connection status.

### 3. Get Movies
```
GET /api/movies?limit=10&skip=0
```
Retrieve a list of movies with pagination.

**Parameters:**
- `limit`: Number of movies to return (1-100)
- `skip`: Number of movies to skip

### 4. Get Single Movie
```
GET /api/movies/{movie_id}
```
Get details of a specific movie by ID.

### 5. Semantic Search (Main Feature!)
```
POST /api/search
```

Search for movies using natural language queries.

**Request Body:**
```json
{
  "query": "action movies with robots and AI",
  "limit": 5
}
```

**Response:**
```json
{
  "query": "action movies with robots and AI",
  "results": [
    {
      "_id": "573a1390f29313caabcd42e8",
      "title": "The Terminator",
      "plot": "A cyborg assassin from the future...",
      "year": 1984,
      "genres": ["Action", "Sci-Fi"],
      "cast": ["Arnold Schwarzenegger"],
      "score": 0.85
    }
  ],
  "count": 5
}
```

### 6. Generate Embeddings
```
POST /api/embeddings/generate
```

Generate embeddings for movies that don't have them yet.

**Request Body:**
```json
{
  "limit": 100,
  "skip": 0
}
```

This processes movies in batches and adds embeddings to their database records.

### 7. Embedding Statistics
```
GET /api/embeddings/stats
```

Get statistics about how many movies have embeddings.

**Response:**
```json
{
  "total_movies": 23530,
  "with_embeddings": 5000,
  "without_embeddings": 18530,
  "completion_percentage": 21.25
}
```

## 🔄 Workflow for Using the API

### Step 1: Start the Server
```bash
uvicorn app.main:app --reload
```

### Step 2: Check Health
Visit `http://localhost:8000/health` to ensure everything is connected.

### Step 3: Generate Embeddings
Before searching, you need to generate embeddings for your movies:

```bash
curl -X POST "http://localhost:8000/api/embeddings/generate" \
  -H "Content-Type: application/json" \
  -d '{"limit": 100, "skip": 0}'
```

Run this multiple times to process all movies (adjusting `skip` parameter).

### Step 4: Create Vector Index
Follow the MongoDB Atlas steps above to create the vector search index.

### Step 5: Perform Searches
Now you can search for movies:

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "romantic comedy in New York", "limit": 5}'
```

## 🧠 Understanding the Code

### What are Embeddings?
Embeddings are numerical representations (vectors) of text. Similar text has similar vectors. This allows us to find movies with similar plots mathematically.

### How Does Vector Search Work?
1. Your search query is converted to an embedding vector
2. MongoDB compares this vector to all movie plot embeddings
3. Movies with the most similar vectors (closest in meaning) are returned
4. Results include a similarity score (0-1, higher is more similar)

### Key Components:

- **config.py**: Loads your credentials and settings from `.env`
- **database.py**: Handles MongoDB connections and queries
- **embeddings.py**: Uses HuggingFace model to create embeddings
- **models.py**: Defines the structure of API requests/responses
- **main.py**: The FastAPI application that ties everything together
- **routes/movies.py**: The actual API endpoints

## 🛠️ Common Operations

### Process all movies in batches:
```python
# In Python or using curl in a loop
for i in range(0, 24000, 100):  # Assuming ~24k movies
    # Generate embeddings for batch
    POST /api/embeddings/generate with {"limit": 100, "skip": i}
```

### Test different searches:
```json
{"query": "space adventure with aliens"}
{"query": "detective solving mysteries"}
{"query": "romantic drama set in the past"}
{"query": "comedy about friendship"}
```

## ⚠️ Troubleshooting

### Database Connection Issues
- Verify your MongoDB URI in `.env`
- Check if your IP is whitelisted in MongoDB Atlas
- Ensure network connectivity

### Embedding Model Not Loading
- First run downloads the model (~90MB)
- Requires internet connection
- Model is cached locally after first download

### Search Returns No Results
- Ensure embeddings are generated first
- Verify the vector search index is created in Atlas
- Check index name matches `movie_embeddings_index`

### "plot_embedding field not found" Error
- You need to generate embeddings first using `/api/embeddings/generate`
- The vector index needs this field to exist in documents

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Atlas Vector Search](https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-overview/)
- [Sentence Transformers](https://www.sbert.net/)
- [HuggingFace Models](https://huggingface.co/models)

## 🎓 Learning More

As you're new to these technologies, here are key concepts:

- **FastAPI**: A modern Python web framework for building APIs
- **Embeddings**: Converting text to numbers that capture meaning
- **Vector Search**: Finding similar items by comparing their embeddings
- **RAG**: Retrieval-Augmented Generation - retrieving relevant information to augment responses
- **Pydantic**: Data validation using Python type hints

## 📝 Next Steps

1. Start the server and access the Swagger UI at `/docs`
2. Generate embeddings for your movies
3. Create the vector search index in MongoDB Atlas
4. Try different search queries
5. Experiment with the code to learn how it works!

## 🔒 Security Notes

- Never commit `.env` to version control (it's in `.gitignore`)
- In production, use proper secret management
- Restrict CORS origins in production (currently set to allow all)

---

**Happy Coding! 🚀**

If you have questions, check the interactive docs at `http://localhost:8000/docs` for detailed endpoint information.
