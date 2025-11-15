# Smart Upload System - Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLIENT APPLICATION                              │
│                    (Browser, Mobile App, CLI)                           │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                                   │ HTTP/HTTPS Requests
                                   │ Authorization: Bearer <token>
                                   │
┌──────────────────────────────────▼──────────────────────────────────────┐
│                          DJANGO REST API                                │
│                      (Port 8000 - localhost)                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────┐    │
│  │           Authentication Middleware                           │    │
│  │         @require_admin decorator on all endpoints             │    │
│  │                                                               │    │
│  │  ┌─────────────────────────────────────────────────────┐     │    │
│  │  │  admin_auth.py (AdminAuthManager)                   │     │    │
│  │  │  • Token validation                                 │     │    │
│  │  │  • Admin ID extraction                              │     │    │
│  │  │  • Access control                                   │     │    │
│  │  └─────────────────────────────────────────────────────┘     │    │
│  └───────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────┐    │
│  │           API Endpoints (smart_upload_views.py)               │    │
│  ├───────────────────────────────────────────────────────────────┤    │
│  │                                                               │    │
│  │  Auth Endpoints:                                              │    │
│  │   • POST /auth/create    → Create admin                       │    │
│  │   • POST /auth/login     → Login (get token)                  │    │
│  │   • POST /auth/logout    → Logout                             │    │
│  │                                                               │    │
│  │  JSON Endpoints:                                              │    │
│  │   • POST /analyze/json   → Preview decision (no storage)      │    │
│  │   • POST /upload/json    → Upload & auto-route                │    │
│  │   • GET  /retrieve/json  → Retrieve document                  │    │
│  │   • GET  /list/json      → List all documents                 │    │
│  │   • DELETE /delete/json  → Delete document                    │    │
│  │                                                               │    │
│  │  Media Endpoints:                                             │    │
│  │   • POST /upload/media   → Upload file                        │    │
│  │   • GET  /retrieve/media → Download file/thumbnail            │    │
│  │   • GET  /list/media     → List all files                     │    │
│  │   • DELETE /delete/media → Delete file                        │    │
│  │                                                               │    │
│  │  Statistics:                                                  │    │
│  │   • GET  /stats          → Get storage stats                  │    │
│  │                                                               │    │
│  └───────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                    │                              │
                    │                              │
        ┌───────────▼────────────┐    ┌───────────▼────────────┐
        │   JSON Upload Flow     │    │   Media Upload Flow    │
        └───────────┬────────────┘    └───────────┬────────────┘
                    │                              │
                    │                              │
┌───────────────────▼──────────────┐  ┌───────────▼───────────────────────┐
│   JSON ANALYZER                  │  │   MEDIA STORAGE HANDLER           │
│   (json_analyzer.py)             │  │   (media_storage.py)              │
├──────────────────────────────────┤  ├───────────────────────────────────┤
│                                  │  │                                   │
│  Analyze JSON Structure:         │  │  File Processing:                 │
│  ┌────────────────────────┐      │  │  ┌─────────────────────────┐      │
│  │ 1. Schema Consistency  │      │  │  │ 1. Type Detection       │      │
│  │ 2. Nesting Depth       │      │  │  │    (magic bytes + MIME) │      │
│  │ 3. Array Complexity    │      │  │  │ 2. Unique Filename      │      │
│  │ 4. Field Variability   │      │  │  │    (admin+time+hash)    │      │
│  │ 5. Type Consistency    │      │  │  │ 3. Date-based Storage   │      │
│  └────────────────────────┘      │  │  │    (/YYYY/MM/DD/)       │      │
│                                  │  │  │ 4. Thumbnail Gen        │      │
│  Calculate Scores:               │  │  │    (3 sizes for images) │      │
│  • SQL Score:    0-15 points     │  │  │ 5. Metadata Extract     │      │
│  • NoSQL Score:  0-15 points     │  │  │    (dimensions, EXIF)   │      │
│  • Confidence:   0-100%          │  │  └─────────────────────────┘      │
│                                  │  │                                   │
│  Output:                         │  │  Output:                          │
│  • Recommended DB (sql/nosql)    │  │  • File ID                        │
│  • Confidence score              │  │  • Storage path                   │
│  • Detailed reasons              │  │  • Thumbnail URLs                 │
│  • Metrics & schema info         │  │  • Metadata                       │
│                                  │  │                                   │
└──────────────┬───────────────────┘  └───────────┬───────────────────────┘
               │                                   │
               │                                   │
               ▼                                   ▼
┌──────────────────────────────────┐  ┌───────────────────────────────────┐
│   SMART DATABASE ROUTER          │  │   FILESYSTEM STORAGE              │
│   (smart_db_router.py)           │  │   (media_storage/)                │
├──────────────────────────────────┤  ├───────────────────────────────────┤
│                                  │  │                                   │
│  Route to Optimal Database       │  │  Directory Structure:             │
│                                  │  │  ├── images/                      │
│  If SQL:                         │  │  │   └── 2024/01/15/              │
│  └─► PostgreSQL Storage          │  │  ├── videos/                      │
│                                  │  │  │   └── 2024/01/15/              │
│  If NoSQL:                       │  │  ├── audio/                       │
│  └─► MongoDB Storage             │  │  │   └── 2024/01/15/              │
│                                  │  │  ├── documents/                   │
│  Additional:                     │  │  │   └── 2024/01/15/              │
│  • Generate doc_id               │  │  └── thumbnails/                  │
│  • Store metadata                │  │      ├── file_small.jpg           │
│  • Admin access check            │  │      ├── file_medium.jpg          │
│  • Cache results                 │  │      └── file_large.jpg           │
│                                  │  │                                   │
└──────┬─────────────┬─────────────┘  └───────────────────────────────────┘
       │             │
       │             │
       ▼             ▼
┌──────────────┐  ┌──────────────────┐
│ PostgreSQL   │  │ MongoDB          │
│ (SQL)        │  │ (NoSQL)          │
├──────────────┤  ├──────────────────┤
│              │  │                  │
│ For each     │  │ Collections:     │
│ document:    │  │                  │
│              │  │ • json_documents │
│ Dynamic      │  │   - doc_id       │
│ Tables:      │  │   - admin_id     │
│              │  │   - data         │
│ json_data_   │  │   - created_at   │
│ doc_xxxxxx   │  │   - tags         │
│              │  │   - analysis     │
│ Columns:     │  │                  │
│ • id         │  │ • metadata       │
│ • doc_id     │  │   - doc_id       │
│ • admin_id   │  │   - storage_info │
│ • created_at │  │   - confidence   │
│ • data       │  │   - reasons      │
│   (JSONB)    │  │   - metrics      │
│              │  │                  │
│ Indexes:     │  │ Indexes:         │
│ • GIN on     │  │ • doc_id         │
│   data       │  │ • admin_id       │
│ • doc_id     │  │ • created_at     │
│              │  │ • db_type        │
│              │  │ • tags           │
│              │  │                  │
└──────────────┘  └──────────────────┘
       │                   │
       └─────────┬─────────┘
                 │
                 ▼
       ┌─────────────────┐
       │  Redis Cache    │
       │  (Port 6379)    │
       ├─────────────────┤
       │                 │
       │ Cache Keys:     │
       │ • json_{doc_id} │
       │ • media_{file_id}│
       │                 │
       │ TTL: 1 hour     │
       │                 │
       │ Invalidation:   │
       │ • On delete     │
       │ • On update     │
       │                 │
       └─────────────────┘
```

---

## Data Flow Diagrams

### JSON Upload Flow

```
Client
  │
  │ POST /api/smart/upload/json
  │ Authorization: Bearer <token>
  │ Body: {...}
  │
  ▼
Django API
  │
  ├─► 1. Validate Token (admin_auth.py)
  │     │
  │     ├─► Valid? → Extract admin_id
  │     └─► Invalid? → Return 401 Unauthorized
  │
  ├─► 2. Parse JSON from request body
  │
  ├─► 3. Analyze JSON Structure (json_analyzer.py)
  │     │
  │     ├─► Calculate SQL Score (0-15)
  │     │     • Schema Consistency
  │     │     • Nesting Depth
  │     │     • Array Complexity
  │     │     • Field Variability
  │     │     • Type Consistency
  │     │
  │     ├─► Calculate NoSQL Score (0-15)
  │     │     • Same criteria, opposite weights
  │     │
  │     └─► Determine Winner & Confidence
  │           • SQL if SQL_score > NoSQL_score
  │           • NoSQL otherwise
  │           • Confidence = winner_score / total_score
  │
  ├─► 4. Route to Database (smart_db_router.py)
  │     │
  │     ├─► Generate doc_id
  │     │     • Format: doc_{timestamp}_{hash[:12]}
  │     │
  │     ├─► If SQL:
  │     │     • Create dynamic table
  │     │     • Add GIN index on JSONB column
  │     │     • Insert data
  │     │
  │     └─► If NoSQL:
  │           • Insert into json_documents collection
  │           • Use compound indexes
  │
  ├─► 5. Store Metadata (MongoDB)
  │     │
  │     └─► metadata collection
  │           • doc_id, admin_id
  │           • analysis results
  │           • storage_info
  │
  ├─► 6. Cache Result (Redis)
  │     │
  │     └─► Key: json_{doc_id}
  │           • TTL: 1 hour
  │
  └─► 7. Return Response
        │
        └─► {
              "success": true,
              "doc_id": "...",
              "database_type": "sql" | "nosql",
              "confidence": 0.87,
              "reasons": [...],
              "metrics": {...},
              "storage_info": {...}
            }
```

### Media Upload Flow

```
Client
  │
  │ POST /api/smart/upload/media
  │ Authorization: Bearer <token>
  │ Content-Type: multipart/form-data
  │ file: <binary>
  │
  ▼
Django API
  │
  ├─► 1. Validate Token
  │
  ├─► 2. Extract File from Request
  │
  ├─► 3. Process Media (media_storage.py)
  │     │
  │     ├─► Detect File Type
  │     │     • Magic bytes (python-magic)
  │     │     • MIME type
  │     │     • Extension fallback
  │     │
  │     ├─► Generate Unique Filename
  │     │     • {admin_id}_{timestamp}_{hash[:12]}.ext
  │     │
  │     ├─► Determine Storage Path
  │     │     • /{type}/{YYYY}/{MM}/{DD}/
  │     │
  │     ├─► Save Original File
  │     │
  │     ├─► If Image:
  │     │     • Generate Thumbnails
  │     │       - Small: 150x150
  │     │       - Medium: 300x300
  │     │       - Large: 600x600
  │     │     • Extract EXIF data
  │     │
  │     └─► Extract Metadata
  │           • Dimensions
  │           • File size
  │           • Format
  │
  ├─► 4. Cache File Info (Redis)
  │
  └─► 5. Return Response
        │
        └─► {
              "success": true,
              "file_id": "...",
              "storage_path": "...",
              "thumbnails": {...},
              "metadata": {...}
            }
```

### Retrieval Flow (with Caching)

```
Client
  │
  │ GET /api/smart/retrieve/json/{doc_id}
  │ Authorization: Bearer <token>
  │
  ▼
Django API
  │
  ├─► 1. Validate Token
  │
  ├─► 2. Check Redis Cache
  │     │
  │     ├─► Cache HIT
  │     │     │
  │     │     └─► Return cached data (fast!)
  │     │
  │     └─► Cache MISS
  │           │
  │           ├─► 3. Check Metadata (MongoDB)
  │           │     • Determine database_type
  │           │     • Verify admin access
  │           │
  │           ├─► 4. Retrieve from Database
  │           │     │
  │           │     ├─► If SQL:
  │           │     │     • Query PostgreSQL table
  │           │     │     • Parse JSONB data
  │           │     │
  │           │     └─► If NoSQL:
  │           │           • Query MongoDB collection
  │           │           • Return document
  │           │
  │           ├─► 5. Cache Result (Redis)
  │           │     • TTL: 1 hour
  │           │
  │           └─► 6. Return Data
```

---

## Component Responsibilities

### 1. Authentication Layer
**File:** `admin_auth.py`
- Token generation and validation
- Password hashing (SHA-256 + salt)
- Admin user management
- Access control enforcement

### 2. Analysis Engine
**File:** `json_analyzer.py`
- JSON structure analysis
- 5-factor scoring algorithm
- Confidence calculation
- Schema extraction
- Reason generation

### 3. Database Router
**File:** `smart_db_router.py`
- Database selection based on analysis
- SQL table creation and management
- NoSQL document insertion
- Metadata tracking
- CRUD operations

### 4. Media Handler
**File:** `media_storage.py`
- File type detection
- Filesystem organization
- Thumbnail generation (images)
- Metadata extraction
- Efficient file serving

### 5. API Layer
**File:** `smart_upload_views.py`
- HTTP request handling
- JSON/file parsing
- Response formatting
- Error handling
- Logging

### 6. URL Routing
**File:** `smart_urls.py`
- Endpoint mapping
- URL pattern matching

---

## Database Optimization Strategies

### PostgreSQL (SQL)
```sql
-- Dynamic table per document
CREATE TABLE json_data_doc_20240115120000_xxxx (
    id SERIAL PRIMARY KEY,
    doc_id VARCHAR(100) NOT NULL,
    admin_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data JSONB NOT NULL
);

-- GIN index for fast JSON queries
CREATE INDEX json_data_doc_xxx_data_gin_idx
ON json_data_doc_xxx USING GIN (data);

-- B-tree index for doc_id lookups
CREATE INDEX json_data_doc_xxx_doc_id_idx
ON json_data_doc_xxx (doc_id);

-- Example queries (optimized by indexes):
SELECT * FROM json_data_doc_xxx WHERE doc_id = 'xxx';  -- Fast (B-tree)
SELECT * FROM json_data_doc_xxx WHERE data @> '{"age": 30}';  -- Fast (GIN)
```

### MongoDB (NoSQL)
```javascript
// Compound indexes for common queries
db.json_documents.createIndex({doc_id: 1}, {unique: true})
db.json_documents.createIndex({admin_id: 1, created_at: -1})
db.json_documents.createIndex({db_type: 1})
db.json_documents.createIndex({tags: 1})

// Example queries (optimized by indexes):
db.json_documents.findOne({doc_id: "xxx"})  // Fast (unique index)
db.json_documents.find({admin_id: "xxx"}).sort({created_at: -1})  // Fast (compound)
```

### Redis (Cache)
```
# Key patterns
json_{doc_id}       → JSON document data (TTL: 1h)
media_{file_id}     → Media file info (TTL: 1h)

# Cache operations
GET json_doc_xxx    → Retrieve cached document
SET json_doc_xxx    → Cache new document
DEL json_doc_xxx    → Invalidate on delete
```

---

## Security Layers

```
┌─────────────────────────────────────────┐
│  Layer 1: HTTPS (Transport Security)   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Layer 2: Token Authentication         │
│  • Bearer token required                │
│  • 256-bit cryptographic tokens         │
│  • Server-side validation               │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Layer 3: Admin Authorization           │
│  • @require_admin decorator             │
│  • Admin ID extraction                  │
│  • Access control checks                │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Layer 4: Data Isolation                │
│  • Admin ID in all queries              │
│  • File path isolation                  │
│  • No cross-admin access                │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Layer 5: Input Validation              │
│  • JSON schema validation               │
│  • File type verification               │
│  • SQL injection prevention (ORM)       │
└─────────────────────────────────────────┘
```

---

## Performance Optimization Stack

```
Request
  │
  ├─► Cache Layer (Redis)
  │     • 1-hour TTL
  │     • Sub-5ms response
  │     • ~1000+ req/sec
  │
  ├─► Application Layer (Django)
  │     • Connection pooling
  │     • Async-ready
  │     • ~100-500 req/sec
  │
  ├─► Database Layer
  │     │
  │     ├─► PostgreSQL
  │     │     • GIN indexes (JSON)
  │     │     • B-tree indexes (IDs)
  │     │     • JSONB compression
  │     │     • ~200-500 req/sec
  │     │
  │     └─► MongoDB
  │           • Compound indexes
  │           • BSON compression
  │           • Memory-mapped files
  │           • ~500-1000 req/sec
  │
  └─► Filesystem Layer
        • Date-based partitioning
        • Pre-generated thumbnails
        • Direct file serving
        • ~50-200 req/sec (media)
```

---

**This architecture provides:**
- ✅ Automatic optimization
- ✅ Fast performance
- ✅ Strong security
- ✅ Complete privacy
- ✅ Scalable design
- ✅ Easy maintenance
