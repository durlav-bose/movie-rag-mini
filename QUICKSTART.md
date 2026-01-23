# Quick Start Guide

Welcome! This guide will get you up and running in 5 minutes.

## ✅ Step 1: Verify Installation

All packages are already installed! Your system has:
- ✓ Python
- ✓ FastAPI
- ✓ MongoDB driver
- ✓ HuggingFace Sentence Transformers
- ✓ All dependencies

## 🚀 Step 2: Start the Server

Open a terminal and run:

```bash
cd /home/durlav-bose/rag-mini
./start.sh
```

Or manually:
```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Starting up Movie RAG API...
INFO:     MongoDB connection established
INFO:     Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
```

**Note**: The first time you run this, it will download the embedding model (~90MB). This is normal and only happens once.

## 🌐 Step 3: Open the API Documentation

Open your browser and go to:
**http://localhost:8000/docs**

This is your interactive API documentation where you can test all endpoints!

## 📊 Step 4: Check Everything is Working

In the Swagger UI (http://localhost:8000/docs):

1. Click on `GET /health`
2. Click "Try it out"
3. Click "Execute"

You should see:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
}
```

## 🎬 Step 5: Get Some Movies

Test that database connection works:

1. In Swagger UI, find `GET /api/movies`
2. Click "Try it out"
3. Set `limit` to 5
4. Click "Execute"

You should see 5 movies from your database!

## 🧠 Step 6: Generate Embeddings

Before you can search, you need to create embeddings for your movies:

1. Find `POST /api/embeddings/generate` in Swagger UI
2. Click "Try it out"
3. Use this request body:
```json
{
  "limit": 100,
  "skip": 0
}
```
4. Click "Execute"

This will process 100 movies. You'll see something like:
```json
{
  "success": true,
  "processed": 100,
  "message": "Successfully generated embeddings for 100 movies"
}
```

**Tip**: To process more movies, run this again with different `skip` values:
- `skip: 0, limit: 100` → processes movies 1-100
- `skip: 100, limit: 100` → processes movies 101-200
- `skip: 200, limit: 100` → processes movies 201-300
- And so on...

## 📈 Step 7: Check Embedding Progress

Check how many movies have embeddings:

1. Find `GET /api/embeddings/stats`
2. Click "Try it out" and "Execute"

You'll see:
```json
{
  "total_movies": 23530,
  "with_embeddings": 100,
  "without_embeddings": 23430,
  "completion_percentage": 0.42
}
```

## 🔍 Step 8: Create the Vector Search Index

**IMPORTANT**: Before you can search, you need to create an index in MongoDB Atlas.

👉 **Follow the guide**: [MONGODB_INDEX_SETUP.md](MONGODB_INDEX_SETUP.md)

Quick summary:
1. Go to https://cloud.mongodb.com/
2. Navigate to your Cluster0
3. Click "Atlas Search" tab
4. Create new index with name: `movie_embeddings_index`
5. Use the JSON config from MONGODB_INDEX_SETUP.md
6. Wait for it to become "Active"

## 🎯 Step 9: Try Semantic Search!

Once you have:
- ✅ Generated some embeddings (Step 6)
- ✅ Created the vector search index (Step 8)
- ✅ Index is "Active" in MongoDB Atlas

Try your first search:

1. Find `POST /api/search` in Swagger UI
2. Click "Try it out"
3. Use this request body:
```json
{
  "query": "action movies with robots",
  "limit": 5
}
```
4. Click "Execute"

You should get results like:
```json
{
  "query": "action movies with robots",
  "results": [
    {
      "_id": "...",
      "title": "The Terminator",
      "plot": "A cyborg assassin...",
      "score": 0.85,
      ...
    }
  ],
  "count": 5
}
```

## 🎨 Step 10: Experiment!

Try different search queries:
- "romantic comedy in New York"
- "space adventure with aliens"
- "detective solving a murder mystery"
- "animated movie about friendship"
- "historical drama set in ancient Rome"

## 🛠️ Common Commands

### Start the server:
```bash
cd /home/durlav-bose/rag-mini
./start.sh
```

### Stop the server:
Press `Ctrl+C` in the terminal

### Check if server is running:
```bash
curl http://localhost:8000/health
```

### Generate embeddings (via command line):
```bash
curl -X POST "http://localhost:8000/api/embeddings/generate" \
  -H "Content-Type: application/json" \
  -d '{"limit": 100, "skip": 0}'
```

### Search (via command line):
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "romantic comedy", "limit": 5}'
```

## 📚 Where to Find More Information

- **Detailed documentation**: [README.md](README.md)
- **MongoDB index setup**: [MONGODB_INDEX_SETUP.md](MONGODB_INDEX_SETUP.md)
- **Interactive API docs**: http://localhost:8000/docs (when server is running)
- **Alternative API docs**: http://localhost:8000/redoc

## ❓ Troubleshooting

### Server won't start?
- Check if port 8000 is already in use
- Verify all packages are installed
- Check `.env` file exists

### "Database connection failed"?
- Verify your MongoDB URI in `.env`
- Check internet connection
- Ensure IP is whitelisted in MongoDB Atlas

### "Model not loading"?
- First run downloads the model (be patient!)
- Check internet connection
- Model will be cached for future runs

### Search returns empty results?
- Did you generate embeddings?
- Is the vector index created and "Active"?
- Did you wait 1-2 minutes after index creation?

## 🎉 Success!

If you've made it this far, you now have:
- ✅ A running FastAPI server
- ✅ Connection to MongoDB Atlas
- ✅ Embeddings being generated
- ✅ Semantic search capability

**Congratulations!** You've built a RAG system! 🚀

---

**Need help?** Check the full [README.md](README.md) for detailed explanations of how everything works.
