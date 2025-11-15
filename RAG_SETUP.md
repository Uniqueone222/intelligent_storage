# RAG (Retrieval Augmented Generation) Setup Guide

## Overview

The intelligent storage system now includes **RAG capabilities** for semantic search across your uploaded documents. This feature uses:

- **Ollama nomic-embed-text** - For generating vector embeddings
- **PostgreSQL with pgvector** - For storing and searching vectors
- **Document chunking** - Intelligently splits documents for optimal retrieval
- **Semantic search** - Find relevant content by meaning, not just keywords

## Prerequisites

1. **PostgreSQL with pgvector extension**
2. **Ollama** with the `nomic-embed-text` model
3. **Python dependencies** (already in requirements)

## Step-by-Step Setup

### 1. Enable pgvector in PostgreSQL

```bash
# Connect to PostgreSQL
sudo -u postgres psql -d intelligent_storage_db

# Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

# Verify installation
\dx vector

# Exit
\q
```

### 2. Pull the Ollama Embedding Model

```bash
# Pull the nomic-embed-text model (768 dimensions)
ollama pull nomic-embed-text

# Verify the model is available
ollama list
```

You should see `nomic-embed-text` in the list.

### 3. Run Database Migrations

```bash
cd backend
source venv/bin/activate
python manage.py migrate
```

This will create the necessary tables:
- `storage_documentchunk` - Stores text chunks with embeddings
- `storage_searchquery` - Tracks search queries for analytics

### 4. Test the System

```bash
# Check if all services are running
curl http://localhost:8000/api/storage/health/

# Should return:
# {
#   "status": "healthy",
#   "services": {
#     "django": true,
#     "postgresql": true,
#     "mongodb": true,
#     "ollama": true
#   }
# }
```

## Using the RAG System

### 1. Index a Document

After uploading a file, index it for semantic search:

```bash
curl -X POST http://localhost:8000/api/storage/rag/index/1/ \
  -H "Content-Type: application/json"
```

Replace `1` with the actual `MediaFile` ID.

**Response:**
```json
{
  "success": true,
  "chunks_created": 15,
  "file_name": "document.pdf"
}
```

### 2. Perform Semantic Search

Search across all indexed documents:

```bash
curl -X POST http://localhost:8000/api/storage/rag/search/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning algorithms",
    "limit": 5
  }'
```

**Response:**
```json
{
  "success": true,
  "query": "machine learning algorithms",
  "results_count": 5,
  "results": [
    {
      "chunk_id": 42,
      "file_name": "ml_guide.pdf",
      "file_type": "documents",
      "chunk_text": "Machine learning algorithms can be categorized into...",
      "chunk_index": 3,
      "metadata": {...}
    }
  ]
}
```

### 3. Ask Questions (RAG Query)

Get AI-generated answers with source citations:

```bash
curl -X POST http://localhost:8000/api/storage/rag/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main types of machine learning?",
    "max_sources": 5
  }'
```

**Response:**
```json
{
  "success": true,
  "answer": "Based on the provided documents, there are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning...",
  "sources": [
    {
      "file_name": "ml_guide.pdf",
      "chunk_text": "...",
      "chunk_index": 3
    }
  ]
}
```

### 4. Get RAG Statistics

```bash
curl http://localhost:8000/api/storage/rag/stats/
```

**Response:**
```json
{
  "total_chunks": 1523,
  "indexed_files": 42,
  "file_types": [
    {"file_type": "documents"},
    {"file_type": "others"}
  ]
}
```

### 5. Reindex All Documents

```bash
curl -X POST http://localhost:8000/api/storage/rag/reindex-all/ \
  -H "Content-Type: application/json"
```

## Supported File Types for RAG

The system can extract text from:

### Text Files
- `.txt`, `.md`, `.csv`, `.log`
- `.json`, `.xml`, `.yaml`, `.yml`

### Code Files
- `.py`, `.js`, `.java`, `.cpp`, `.c`, `.h`
- `.cs`, `.php`, `.rb`, `.go`, `.rs`, `.swift`
- `.kt`, `.ts`, `.jsx`, `.tsx`

### Documents
- `.pdf` - PDF documents
- `.docx` - Microsoft Word documents
- `.html`, `.htm` - HTML files

## How It Works

### 1. Document Upload
When you upload a file, it's stored and categorized as before.

### 2. Indexing Process
```
File → Extract Text → Split into Chunks → Generate Embeddings → Store in DB
```

- **Chunking**: Documents are split into ~500 character chunks with 50 character overlap
- **Embedding**: Each chunk is converted to a 768-dimensional vector using `nomic-embed-text`
- **Storage**: Chunks and vectors are stored in PostgreSQL with pgvector

### 3. Search Process
```
Query → Generate Embedding → Vector Similarity Search → Rank Results
```

- Your search query is converted to a vector
- pgvector finds the most similar document chunks using L2 distance
- Results are ranked by relevance

### 4. RAG Query Process
```
Query → Retrieve Context → Build Prompt → Generate Answer → Return with Sources
```

- Relevant chunks are retrieved
- Context is injected into the LLM prompt
- Ollama generates an answer based on your documents
- Sources are included for verification

## Configuration

### Chunking Settings

Edit `backend/storage/chunking_service.py`:

```python
chunking_service = ChunkingService(
    max_chunk_size=500,      # Maximum characters per chunk
    overlap_size=50,         # Overlap between chunks
    separators=['\n\n', '\n', '. ', ' ', '']  # Split priority
)
```

### Search Settings

In your API calls, you can configure:

```json
{
  "query": "your search",
  "limit": 10,                    // Max results to return
  "file_type": "documents",       // Filter by file type
  "similarity_threshold": 0.7     // Minimum similarity score
}
```

## Troubleshooting

### pgvector Not Found

```bash
# Install pgvector on Arch Linux
yay -S postgresql-pgvector

# Or build from source
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### nomic-embed-text Model Not Found

```bash
# Pull the model
ollama pull nomic-embed-text

# If it fails, check Ollama is running
systemctl status ollama

# Start Ollama if needed
ollama serve
```

### Migration Fails

```bash
# Make sure pgvector extension is enabled first
sudo -u postgres psql -d intelligent_storage_db -c "CREATE EXTENSION vector;"

# Then run migrations
python manage.py migrate
```

### Slow Search Performance

For large document collections:

1. **Create indexes** (automatically done in migrations)
2. **Limit chunk size** - Smaller collections = faster search
3. **Filter by file_type** - Reduce search space
4. **Adjust limit parameter** - Request fewer results

## Performance Considerations

### Embedding Generation
- **Speed**: ~100ms per chunk on CPU
- **Optimization**: Embeddings are generated once during indexing

### Search Performance
- **Speed**: ~50ms for 1000 chunks, ~200ms for 10,000 chunks
- **Scalability**: pgvector uses HNSW index for fast nearest neighbor search

### Storage Requirements
- **Embeddings**: ~3KB per chunk (768 dimensions × 4 bytes)
- **Text**: Variable, depends on chunk size
- **Total**: ~5-10KB per chunk on average

### Recommendations
- **Small collections** (<1000 chunks): All file types
- **Medium collections** (1000-10,000 chunks): Use file type filters
- **Large collections** (>10,000 chunks): Consider separate indexes per type

## API Endpoint Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/storage/rag/index/<file_id>/` | POST | Index a specific file |
| `/api/storage/rag/search/` | POST | Semantic search |
| `/api/storage/rag/query/` | POST | Ask questions with AI |
| `/api/storage/rag/reindex-all/` | POST | Reindex all documents |
| `/api/storage/rag/stats/` | GET | Get system statistics |

## Next Steps

1. **Upload some documents** through the web interface
2. **Index them** using the API or web UI
3. **Try semantic search** to find content by meaning
4. **Ask questions** and get AI-generated answers with sources

The RAG system will automatically improve as you add more documents!

---

**Need help?** Check the logs at `backend/logs/` or raise an issue on GitHub.
