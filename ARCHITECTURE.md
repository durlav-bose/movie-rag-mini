# System Architecture

## How Everything Works Together

```
┌─────────────────────────────────────────────────────────────────┐
│                          Your Browser                           │
│                   http://localhost:8000/docs                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTP Requests
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FastAPI Server                            │
│                       (app/main.py)                             │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Endpoints:                                                │ │
│  │  • GET  /health          - Check system status            │ │
│  │  • GET  /api/movies      - List movies                    │ │
│  │  • POST /api/search      - Semantic search                │ │
│  │  • POST /api/embeddings  - Generate embeddings            │ │
│  └───────────────────────────────────────────────────────────┘ │
└───────────┬────────────────────────┬────────────────────────────┘
            │                        │
            │                        │
            ▼                        ▼
┌─────────────────────┐    ┌──────────────────────────┐
│   Embedding Model   │    │   MongoDB Atlas          │
│   (embeddings.py)   │    │   (database.py)          │
│                     │    │                          │
│  HuggingFace Model  │    │  Database: sample_mflix  │
│  all-MiniLM-L6-v2   │    │  Collection: movies      │
│                     │    │                          │
│  Converts text to   │    │  Stores:                 │
│  384-dim vectors    │    │  • Movie data            │
│                     │    │  • Embeddings            │
└─────────────────────┘    │  • Vector search index   │
                           └──────────────────────────┘
```

## Data Flow: Generating Embeddings

```
1. User Request
   POST /api/embeddings/generate {"limit": 100}
   
2. Database Query
   database.py → MongoDB: Fetch 100 movies without embeddings
   
3. Extract Text
   Get plot text from each movie
   
4. Generate Embeddings
   embeddings.py → HuggingFace Model
   ["Plot text 1", "Plot text 2", ...] → [[0.23, -0.45, ...], [0.12, 0.67, ...], ...]
   
5. Update Database
   database.py → MongoDB: Store embeddings in plot_embedding field
   
6. Response
   {"success": true, "processed": 100}
```

## Data Flow: Semantic Search

```
1. User Search Query
   POST /api/search {"query": "action movie with robots", "limit": 5}
   
2. Generate Query Embedding
   embeddings.py → HuggingFace Model
   "action movie with robots" → [0.15, -0.32, 0.78, ..., 0.45]
   
3. Vector Search
   database.py → MongoDB Vector Search
   Compare query embedding with all movie embeddings
   Find 5 most similar using cosine similarity
   
4. Return Results
   MongoDB → API → User
   [
     {title: "The Terminator", score: 0.85, ...},
     {title: "I, Robot", score: 0.82, ...},
     ...
   ]
```

## File Responsibilities

### Core Application Files

**app/main.py**
- Creates the FastAPI application
- Initializes database and model on startup
- Defines root and health check endpoints
- Includes route modules

**app/config.py**
- Loads environment variables from .env
- Provides configuration to all modules
- Manages settings like MongoDB URI, model name, etc.

**app/database.py**
- Connects to MongoDB Atlas
- Provides functions to query movies
- Handles vector search operations
- Updates documents with embeddings

**app/embeddings.py**
- Loads the HuggingFace model
- Converts text to embedding vectors
- Handles single and batch embedding generation
- Caches model for reuse

**app/models.py**
- Defines request/response structures using Pydantic
- Validates incoming data
- Formats outgoing data
- Provides type hints for better code

**app/routes/movies.py**
- Implements all movie-related endpoints
- Orchestrates between database and embeddings
- Handles errors and logging
- Formats responses

## Key Concepts Explained

### What is an Embedding?

```
Text:      "A robot saves humanity"
           ↓
Embedding: [0.23, -0.45, 0.12, 0.67, ..., 0.89]  (384 numbers)

Similar texts have similar embeddings:
"A robot saves humanity"    → [0.23, -0.45, 0.12, ...]
"AI rescues mankind"        → [0.25, -0.43, 0.15, ...]  ← Similar!

Different texts have different embeddings:
"A romantic dinner"         → [-0.67, 0.89, -0.23, ...] ← Different!
```

### Vector Similarity Search

```
Query: "romantic movie"
Embedding: [0.8, 0.6, -0.2, ...]

Database Movies:
Movie 1: [0.7, 0.5, -0.1, ...]  ← Cosine Similarity: 0.95 (Very similar!)
Movie 2: [-0.3, 0.9, 0.4, ...]  ← Cosine Similarity: 0.42 (Not similar)
Movie 3: [0.75, 0.55, -0.15, ...] ← Cosine Similarity: 0.93 (Very similar!)

Results: Movie 1, Movie 3 (highest similarity scores)
```

### MongoDB Vector Search Index

The index is like a specialized database structure that:
1. Knows where to find embeddings (plot_embedding field)
2. Knows the embedding size (384 dimensions)
3. Uses efficient algorithms to find similar vectors quickly
4. Without it, searching would be too slow

## Environment Variables (.env)

```
MONGODB_URI          → Where to find your database
MONGODB_DB_NAME      → Which database to use (sample_mflix)
MONGODB_COLLECTION   → Which collection to use (movies)
HUGGINGFACE_TOKEN    → Authorization for HuggingFace
EMBEDDING_MODEL_NAME → Which AI model to use
VECTOR_INDEX_NAME    → Name of the search index
VECTOR_DIMENSION     → Size of embeddings (384)
```

## Request/Response Flow

### Example: Searching for movies

```
User Browser
    ↓ POST /api/search {"query": "space adventure"}
FastAPI (main.py)
    ↓ Route to movies.py
movies.py
    ↓ Call embeddings.get_embedding("space adventure")
embeddings.py
    ↓ Use HuggingFace model
    ↓ Return [0.15, -0.32, ...]
movies.py
    ↓ Call database.vector_search([0.15, -0.32, ...])
database.py
    ↓ Query MongoDB with vector search
    ↓ Return similar movies
movies.py
    ↓ Format as SearchResponse
FastAPI
    ↓ Convert to JSON
User Browser
    ↓ Display results
```

## Technology Stack

```
┌─────────────────────────────────────┐
│          Frontend Layer             │
│    Browser (Swagger UI/ReDoc)       │
└─────────────────────────────────────┘
                 ↕
┌─────────────────────────────────────┐
│         API Layer                   │
│  FastAPI (Python web framework)     │
│  Pydantic (data validation)         │
│  Uvicorn (ASGI server)              │
└─────────────────────────────────────┘
                 ↕
┌─────────────────────────────────────┐
│       Business Logic                │
│  Custom route handlers              │
│  Embedding generation logic         │
│  Search orchestration               │
└─────────────────────────────────────┘
                 ↕
┌─────────────────────────────────────┐
│       Data Layer                    │
│  PyMongo (MongoDB driver)           │
│  Sentence Transformers              │
│  (HuggingFace embeddings)           │
└─────────────────────────────────────┘
                 ↕
┌─────────────────────────────────────┐
│      External Services              │
│  MongoDB Atlas (cloud database)     │
│  HuggingFace (model hosting)        │
└─────────────────────────────────────┘
```

## Scaling Considerations

**Current Setup (Good for learning/development):**
- Single server instance
- Synchronous embedding generation
- All operations in one process

**For Production (If you grow):**
- Use background tasks for embedding generation
- Cache embeddings in memory (Redis)
- Deploy on cloud (AWS, GCP, Azure)
- Use load balancer for multiple instances
- Monitor with logging services

## Security Layers

```
.env file              → Stores secrets (not in Git!)
.gitignore            → Prevents committing secrets
MongoDB Atlas         → Network security, IP whitelist
FastAPI validation    → Input sanitization (Pydantic)
CORS middleware       → Controls browser access
```

---

This architecture follows the **separation of concerns** principle:
- Each file has a specific purpose
- Changes in one area don't break others
- Easy to test and maintain
- Clear data flow

