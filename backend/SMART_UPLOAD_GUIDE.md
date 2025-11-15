# Smart Upload System - Complete Guide

## Overview

The Smart Upload System is an intelligent data storage solution that automatically categorizes JSON data for optimal database storage (SQL vs NoSQL) and provides optimized media file storage with admin-only access control.

## Key Features

### 1. **Intelligent JSON Analysis**
- Automatically analyzes JSON structure
- Routes to PostgreSQL (SQL) or MongoDB (NoSQL) based on:
  - Schema consistency
  - Nesting depth
  - Data relationships
  - Array complexity
  - Field variability
  - Type consistency
- Provides detailed reasoning for database selection
- Confidence scores for each decision

### 2. **Optimized Media Storage**
- Local filesystem storage with CDN-ready structure
- Automatic thumbnail generation for images (3 sizes: small, medium, large)
- Organized by type and date (`/media/{type}/{YYYY}/{MM}/{DD}/`)
- Metadata extraction (dimensions, EXIF, etc.)
- Fast retrieval with proper MIME types

### 3. **Admin-Only Access Control**
- Token-based authentication (256-bit secure tokens)
- All operations require admin authorization
- Token expiration (default: 24 hours)
- Password hashing with salt (SHA-256)
- No public access - full data privacy

### 4. **Fast Retrieval with Caching**
- Redis caching for frequently accessed data
- 1-hour cache timeout
- Optimized database indexing:
  - PostgreSQL: JSONB with GIN indexing
  - MongoDB: Compound indexes on key fields
- Cache invalidation on updates/deletes

### 5. **Comprehensive Logging**
- Decision logging for all database categorizations
- Upload/retrieval tracking
- Error monitoring
- Statistical analysis

---

## Architecture

### Database Decision Algorithm

```
JSON Input
    ↓
Analyze Structure
    ├── Schema Consistency (uniform = SQL, varied = NoSQL)
    ├── Nesting Depth (flat ≤2 = SQL, deep >2 = NoSQL)
    ├── Array Complexity (simple = SQL, nested = NoSQL)
    ├── Field Variability (consistent = SQL, variable = NoSQL)
    └── Type Consistency (consistent = SQL, mixed = NoSQL)
    ↓
Calculate Scores
    ├── SQL Score: 0-15 points
    └── NoSQL Score: 0-15 points
    ↓
Route to Database
    ├── PostgreSQL (if SQL score > NoSQL score)
    └── MongoDB (if NoSQL score >= SQL score)
```

### Storage Structure

```
intelligent_storage/
├── backend/
│   ├── storage/
│   │   ├── json_analyzer.py         # JSON structure analysis
│   │   ├── smart_db_router.py       # Database routing logic
│   │   ├── media_storage.py         # Media file handler
│   │   ├── admin_auth.py            # Authentication system
│   │   ├── smart_upload_views.py    # API endpoints
│   │   └── smart_urls.py            # URL routing
│   ├── data/
│   │   └── admin_auth.json          # Admin credentials (secure)
│   └── media_storage/
│       ├── images/{YYYY}/{MM}/{DD}/ # Image storage
│       ├── videos/{YYYY}/{MM}/{DD}/ # Video storage
│       ├── audio/{YYYY}/{MM}/{DD}/  # Audio storage
│       ├── documents/{YYYY}/{MM}/{DD}/ # Document storage
│       └── thumbnails/              # Image thumbnails
└── README.md
```

---

## API Endpoints

Base URL: `/api/smart/`

### Authentication Endpoints

#### 1. Create Admin User
```http
POST /api/smart/auth/create
Content-Type: application/json

{
  "username": "admin",
  "password": "your-secure-password",
  "email": "admin@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "admin_id": "admin_a1b2c3d4e5f6g7h8",
  "username": "admin",
  "message": "Admin user created successfully"
}
```

#### 2. Login
```http
POST /api/smart/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "your-secure-password"
}
```

**Response:**
```json
{
  "success": true,
  "token": "Xy9aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2uV3wX4yZ5",
  "admin_id": "admin_a1b2c3d4e5f6g7h8",
  "username": "admin",
  "expires_at": "2024-01-16T12:00:00",
  "message": "Authentication successful"
}
```

#### 3. Logout
```http
POST /api/smart/auth/logout
Authorization: Bearer <token>
```

---

### JSON Upload Endpoints

#### 1. Analyze JSON (Preview)
Analyze without storing to see database recommendation.

```http
POST /api/smart/analyze/json
Authorization: Bearer <token>
Content-Type: application/json

{
  "users": [
    {"id": 1, "name": "Alice", "age": 30},
    {"id": 2, "name": "Bob", "age": 25}
  ]
}
```

**Response:**
```json
{
  "recommended_db": "sql",
  "confidence": 0.87,
  "reasons": [
    "✓ SQL: Highly consistent schema (100% field consistency)",
    "✓ SQL: Shallow nesting (depth=2) - suitable for relational tables",
    "✓ SQL: Simple arrays at top level - can normalize to SQL tables",
    "✓ SQL: 3/3 fields always present - fixed schema works well",
    "✓ SQL: All fields have consistent types - strong typing possible"
  ],
  "metrics": {
    "max_depth": 2,
    "total_objects": 2,
    "unique_fields": 3,
    "total_fields": 6,
    "has_nested_arrays": false,
    "has_mixed_types": false,
    "sql_score": 10.0,
    "nosql_score": 1.5
  },
  "schema_info": {
    "fields": {
      "id": {
        "types": ["int"],
        "primary_type": "int",
        "occurrence_rate": 1.0,
        "required": true
      },
      "name": {
        "types": ["str"],
        "primary_type": "str",
        "occurrence_rate": 1.0,
        "required": true
      },
      "age": {
        "types": ["int"],
        "primary_type": "int",
        "occurrence_rate": 1.0,
        "required": true
      }
    },
    "estimated_objects": 2,
    "max_nesting_depth": 2,
    "has_arrays": true
  }
}
```

#### 2. Upload JSON (Store)
Upload and store JSON in the optimal database.

```http
POST /api/smart/upload/json?tags=users,customers
Authorization: Bearer <token>
Content-Type: application/json

{
  "users": [
    {"id": 1, "name": "Alice", "age": 30},
    {"id": 2, "name": "Bob", "age": 25}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "doc_id": "doc_20240115120000_a1b2c3d4e5f6",
  "database_type": "sql",
  "confidence": 0.87,
  "reasons": ["..."],
  "metrics": {"..."},
  "storage_info": {
    "table_name": "json_data_doc_20240115120000_a1b2c3d4e5f6",
    "database": "postgresql",
    "indexed_fields": ["data (GIN)", "doc_id"],
    "optimization": "JSONB with GIN indexing for fast queries"
  },
  "timestamp": "2024-01-15T12:00:00"
}
```

---

### Media Upload Endpoints

#### Upload Media File
```http
POST /api/smart/upload/media
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary file data>
```

**Response (Image):**
```json
{
  "success": true,
  "file_id": "image_20240115120000_a1b2c3d4e5f6",
  "filename": "admin_xyz_20240115_120000_a1b2c3d4e5f6.jpg",
  "original_filename": "photo.jpg",
  "file_type": "image",
  "mime_type": "image/jpeg",
  "file_size": 1234567,
  "storage_path": "images/2024/01/15/admin_xyz_20240115_120000_a1b2c3d4e5f6.jpg",
  "full_path": "/path/to/media_storage/images/2024/01/15/...",
  "admin_id": "admin_xyz",
  "created_at": "2024-01-15T12:00:00",
  "url_path": "/media/image/2024/01/15/admin_xyz_20240115_120000_a1b2c3d4e5f6.jpg",
  "thumbnails": {
    "small": {
      "path": "thumbnails/admin_xyz_20240115_120000_a1b2c3d4e5f6_small.jpg",
      "url": "/media/thumbnails/admin_xyz_20240115_120000_a1b2c3d4e5f6_small.jpg",
      "width": 150,
      "height": 150
    },
    "medium": {
      "path": "thumbnails/admin_xyz_20240115_120000_a1b2c3d4e5f6_medium.jpg",
      "url": "/media/thumbnails/admin_xyz_20240115_120000_a1b2c3d4e5f6_medium.jpg",
      "width": 300,
      "height": 300
    },
    "large": {
      "path": "thumbnails/admin_xyz_20240115_120000_a1b2c3d4e5f6_large.jpg",
      "url": "/media/thumbnails/admin_xyz_20240115_120000_a1b2c3d4e5f6_large.jpg",
      "width": 600,
      "height": 600
    }
  },
  "metadata": {
    "file_size_bytes": 1234567,
    "file_size_human": "1.18 MB",
    "width": 1920,
    "height": 1080,
    "format": "JPEG",
    "mode": "RGB",
    "has_transparency": false
  }
}
```

---

### Retrieval Endpoints

#### 1. Retrieve JSON Document
```http
GET /api/smart/retrieve/json/<doc_id>
Authorization: Bearer <token>
```

**Response:**
```json
{
  "cached": false,
  "doc_id": "doc_20240115120000_a1b2c3d4e5f6",
  "data": {
    "users": [
      {"id": 1, "name": "Alice", "age": 30},
      {"id": 2, "name": "Bob", "age": 25}
    ]
  },
  "database_type": "sql",
  "metadata": {
    "created_at": "2024-01-15T12:00:00",
    "confidence": 0.87,
    "metrics": {"..."}
  }
}
```

#### 2. Retrieve Media File
```http
GET /api/smart/retrieve/media/<file_id>?thumbnail=medium
Authorization: Bearer <token>
```

Returns binary file content with appropriate MIME type.

---

### List Endpoints

#### 1. List JSON Documents
```http
GET /api/smart/list/json?db_type=sql&limit=50
Authorization: Bearer <token>
```

**Query Parameters:**
- `db_type` (optional): `sql` or `nosql`
- `limit` (optional): Maximum results (default: 100)

#### 2. List Media Files
```http
GET /api/smart/list/media?file_type=image&limit=50
Authorization: Bearer <token>
```

**Query Parameters:**
- `file_type` (optional): `image`, `video`, `audio`, `document`
- `limit` (optional): Maximum results (default: 100)

---

### Delete Endpoints

#### 1. Delete JSON Document
```http
DELETE /api/smart/delete/json/<doc_id>
Authorization: Bearer <token>
```

#### 2. Delete Media File
```http
DELETE /api/smart/delete/media/<file_id>
Authorization: Bearer <token>
```

---

### Statistics Endpoint

```http
GET /api/smart/stats
Authorization: Bearer <token>
```

**Response:**
```json
{
  "admin_id": "admin_xyz",
  "json_documents": {
    "total": 150,
    "sql": 95,
    "nosql": 55
  },
  "media_files": {
    "total": 234,
    "images": 120,
    "videos": 45,
    "audio": 23,
    "documents": 46,
    "total_size_bytes": 5234567890,
    "total_size_human": "4.87 GB"
  }
}
```

---

## Decision Examples

### Example 1: SQL-Friendly Data

**Input:**
```json
[
  {"id": 1, "name": "Product A", "price": 99.99, "category": "Electronics"},
  {"id": 2, "name": "Product B", "price": 149.99, "category": "Electronics"},
  {"id": 3, "name": "Product C", "price": 79.99, "category": "Books"}
]
```

**Decision:** → **SQL (PostgreSQL)**

**Reasons:**
- ✓ Highly consistent schema (100% consistency)
- ✓ Shallow nesting (depth=2)
- ✓ Simple array structure
- ✓ All fields present in every object
- ✓ Consistent data types

**Confidence:** 92%

---

### Example 2: NoSQL-Friendly Data

**Input:**
```json
{
  "user": {
    "profile": {
      "personal": {
        "name": "Alice",
        "addresses": [
          {
            "type": "home",
            "street": "123 Main St",
            "city": "Springfield",
            "coordinates": {"lat": 40.7128, "lng": -74.0060}
          },
          {
            "type": "work",
            "building": "Office Tower",
            "floor": 15,
            "city": "New York"
          }
        ]
      },
      "preferences": {
        "notifications": {"email": true, "sms": false, "push": {"enabled": true, "frequency": "daily"}},
        "privacy": {"profile_visible": true}
      }
    },
    "activity": [
      {"timestamp": "2024-01-15T10:00:00", "events": [{"type": "login", "device": "mobile"}]},
      {"timestamp": "2024-01-15T11:30:00", "action": "purchase", "items": [1, 2, 3]}
    ]
  }
}
```

**Decision:** → **NoSQL (MongoDB)**

**Reasons:**
- ✓ Deep nesting (depth=6)
- ✓ Complex nested arrays
- ✓ Variable schema (different fields in array items)
- ✓ Hierarchical structure
- ✓ Document-oriented data

**Confidence:** 95%

---

## Setup Instructions

### 1. Database Setup

**PostgreSQL:**
```bash
# Create database
createdb intelligent_storage_sql

# The system will automatically create tables as needed
```

**MongoDB:**
```bash
# Start MongoDB
mongod --dbpath /path/to/data

# Database and collections are created automatically
```

### 2. Django Configuration

Ensure your `settings.py` includes:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'intelligent_storage_sql',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'mongodb': {
        'ENGINE': '',  # Not used by Django ORM
        'NAME': 'intelligent_storage_nosql',
        'HOST': 'localhost',
        'PORT': 27017,
    }
}

# Caching (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3. Create Admin User

```bash
curl -X POST http://localhost:8000/api/smart/auth/create \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your-secure-password",
    "email": "admin@example.com"
  }'
```

### 4. Test Upload

```bash
# Login
TOKEN=$(curl -X POST http://localhost:8000/api/smart/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-secure-password"}' \
  | jq -r '.token')

# Upload JSON
curl -X POST http://localhost:8000/api/smart/upload/json \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"test":"data","items":[1,2,3]}'
```

---

## Security Features

1. **Token-Based Authentication**
   - 256-bit secure tokens
   - Automatic expiration (24 hours default)
   - Server-side validation

2. **Password Security**
   - SHA-256 hashing with salt
   - 32-byte random salt per user
   - No plaintext storage

3. **Access Control**
   - All endpoints require authentication
   - Admin-only access to all data
   - No public endpoints

4. **Data Privacy**
   - All data stored on your server
   - No external API calls
   - No data sharing

---

## Performance Optimizations

### 1. Database Indexing
- **PostgreSQL:** GIN indexes on JSONB columns
- **MongoDB:** Compound indexes on frequently queried fields

### 2. Caching
- Redis caching with 1-hour TTL
- Cache invalidation on updates/deletes
- Automatic cache warming for popular items

### 3. Media Storage
- Date-based partitioning
- Thumbnail pre-generation
- Efficient file organization

### 4. Query Optimization
- Selective field retrieval
- Pagination support
- Batch operations

---

## Monitoring and Logging

All operations are logged with:
- Timestamp
- Admin ID
- Operation type
- Database decision (with confidence)
- Error details (if any)

View logs in Django console or configure file logging in `settings.py`.

---

## Troubleshooting

### Issue: "Invalid or expired token"
**Solution:** Login again to get a new token.

### Issue: "Document not found"
**Solution:** Verify doc_id and ensure you're using the correct admin account.

### Issue: "Database connection failed"
**Solution:** Check PostgreSQL and MongoDB are running.

### Issue: Media files not saving
**Solution:** Check filesystem permissions for `media_storage/` directory.

---

## Future Enhancements

- [ ] Multi-admin support with role-based access
- [ ] Advanced caching strategies
- [ ] Database replication
- [ ] Batch upload API
- [ ] Webhook notifications
- [ ] Advanced analytics dashboard
- [ ] Cloud storage integration (S3, etc.)

---

## Support

For issues or questions, check the logs or review the source code:
- `storage/json_analyzer.py` - Analysis logic
- `storage/smart_db_router.py` - Routing logic
- `storage/smart_upload_views.py` - API endpoints

---

**Built with Django, PostgreSQL, MongoDB, and Redis for intelligent data storage.**
