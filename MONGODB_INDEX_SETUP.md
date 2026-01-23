# MongoDB Atlas Vector Search Index Setup

## Why do you need this?

Before you can use the semantic search feature, you need to create a **Vector Search Index** in MongoDB Atlas. This index allows MongoDB to efficiently search through embedding vectors.

## Step-by-Step Instructions

### 1. Login to MongoDB Atlas
Go to https://cloud.mongodb.com/ and login with your credentials.

### 2. Navigate to Your Cluster
- Find your cluster: **Cluster0**
- Click on "Browse Collections" or the cluster name

### 3. Access Atlas Search
- Click on the "Atlas Search" tab (or "Search" tab)
- You should see your database: `sample_mflix`

### 4. Create Search Index
- Click the **"Create Search Index"** button
- Choose **"Atlas Vector Search"** (or "JSON Editor" if that's the only option)

### 5. Configure the Index

#### If using Visual Editor:
- **Index Name**: `movie_embeddings_index`
- **Database**: `sample_mflix`
- **Collection**: `movies`
- Add a Vector field:
  - **Field Name**: `plot_embedding`
  - **Dimensions**: `384`
  - **Similarity**: `cosine`

#### If using JSON Editor:
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

### 6. Index Details

- **Index Name**: `movie_embeddings_index` (must match exactly!)
- **Database**: `sample_mflix`
- **Collection**: `movies`
- **Field Path**: `plot_embedding` (this is where embeddings will be stored)
- **Vector Dimensions**: `384` (size of the all-MiniLM-L6-v2 model embeddings)
- **Similarity Function**: `cosine` (how to measure similarity between vectors)

### 7. Create and Wait
- Click **"Create Search Index"**
- The index will show as "Building" or "Pending"
- Wait for it to show "Active" (usually takes 2-10 minutes)
- ☕ Grab a coffee while it builds!

### 8. Verify the Index
Once active, you should see:
- Index Name: `movie_embeddings_index`
- Status: Active (green checkmark)
- Collection: `sample_mflix.movies`

## What if I see errors?

### "Index name already exists"
- You might already have an index with this name
- Either use the existing one or delete it and create a new one

### "Collection not found"
- Make sure you're in the right database: `sample_mflix`
- Verify the collection name is exactly `movies`

### "Cannot create index"
- Ensure your cluster has Atlas Search enabled (free tier has it!)
- Check you have write permissions

## Testing the Index

After creating the index and generating embeddings, test it with:

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "romantic movie", "limit": 3}'
```

## Understanding the Configuration

- **numDimensions: 384** 
  - The all-MiniLM-L6-v2 model produces 384-dimensional vectors
  - This must match your embedding model's output size

- **similarity: cosine**
  - Cosine similarity measures the angle between vectors
  - Good for text embeddings where magnitude doesn't matter
  - Other options: euclidean, dotProduct

- **path: plot_embedding**
  - The field in your MongoDB documents that stores the embedding
  - Must match what your API writes to the database

## Troubleshooting Search Issues

If search doesn't work after index creation:

1. ✅ Check index is "Active" in Atlas
2. ✅ Verify index name is exactly `movie_embeddings_index`
3. ✅ Ensure you've generated embeddings: `POST /api/embeddings/generate`
4. ✅ Check embeddings exist: `GET /api/embeddings/stats`
5. ✅ Wait 1-2 minutes after index becomes active (propagation delay)

## Additional Resources

- [MongoDB Atlas Vector Search Docs](https://www.mongodb.com/docs/atlas/atlas-vector-search/create-index/)
- [Atlas Search Tutorial](https://www.mongodb.com/docs/atlas/atlas-search/tutorial/)

---

**Once your index is active, you're ready to search! 🎉**
