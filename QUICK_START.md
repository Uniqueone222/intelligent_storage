# Smart Upload System - Quick Start Guide

## What This System Does

**Automatically categorizes your JSON data** and routes it to the optimal database:
- **SQL (PostgreSQL)** → for structured, relational data
- **NoSQL (MongoDB)** → for nested, hierarchical data

Plus **optimized media storage** with automatic thumbnail generation and **admin-only access control**.

---

## 🚀 Quick Setup (5 Minutes)

### 1. Install Dependencies

```bash
cd intelligent_storage/backend
source venv/bin/activate  # Already created
pip install -r requirements_minimal.txt  # Already done
```

### 2. Start Databases

**PostgreSQL:**
```bash
# If not running, start it:
sudo systemctl start postgresql
# Or on macOS:
brew services start postgresql

# Create database:
createdb intelligent_storage_sql
```

**MongoDB:**
```bash
# Start MongoDB
sudo systemctl start mongodb
# Or on macOS:
brew services start mongodb-community
```

**Redis (for caching):**
```bash
# Start Redis
sudo systemctl start redis
# Or on macOS:
brew services start redis
```

### 3. Configure Django

The system is already configured! Just verify your database credentials in `backend/core/settings.py` if needed.

### 4. Run Migrations

```bash
cd backend
python manage.py migrate
```

### 5. Start Server

```bash
python manage.py runserver
```

Server will start at: `http://localhost:8000`

---

## 🎯 Test the System (2 Minutes)

### Test the Analyzer

```bash
cd backend
python test_smart_system.py
```

This will show you how the system categorizes different JSON structures.

### Create Admin User

```bash
curl -X POST http://localhost:8000/api/smart/auth/create \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123",
    "email": "admin@example.com"
  }'
```

**Response:**
```json
{
  "success": true,
  "admin_id": "admin_xxxxxxxxxx",
  "username": "admin",
  "message": "Admin user created successfully"
}
```

### Login and Get Token

```bash
curl -X POST http://localhost:8000/api/smart/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Copy the token from the response!**

### Upload JSON Data

**Test 1: Structured Data (will go to SQL)**
```bash
TOKEN="your-token-here"

curl -X POST http://localhost:8000/api/smart/upload/json \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {"id": 1, "name": "Alice", "age": 30, "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "age": 25, "email": "bob@example.com"}
  ]'
```

**Expected Response:**
```json
{
  "success": true,
  "doc_id": "doc_20240115120000_xxxxxxxxxxxx",
  "database_type": "sql",
  "confidence": 0.87,
  "reasons": [
    "✓ SQL: Highly consistent schema (100% field consistency)",
    "✓ SQL: Shallow nesting (depth=2) - suitable for relational tables",
    ...
  ],
  "storage_info": {
    "table_name": "json_data_doc_...",
    "database": "postgresql",
    "optimization": "JSONB with GIN indexing for fast queries"
  }
}
```

**Test 2: Nested Data (will go to NoSQL)**
```bash
curl -X POST http://localhost:8000/api/smart/upload/json \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user": {
      "profile": {
        "name": "Alice",
        "contacts": [
          {"type": "email", "value": "alice@example.com"},
          {"type": "phone", "value": "+1234567890"}
        ],
        "preferences": {
          "theme": "dark",
          "notifications": {"email": true, "sms": false}
        }
      }
    }
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "doc_id": "doc_20240115120100_xxxxxxxxxxxx",
  "database_type": "nosql",
  "confidence": 0.92,
  "reasons": [
    "✓ NoSQL: Deep nesting (depth=4) - optimal for document storage",
    "✓ NoSQL: Complex nested arrays - better suited for document storage",
    ...
  ],
  "storage_info": {
    "collection": "json_documents",
    "database": "mongodb",
    "optimization": "Document storage with compound indexes"
  }
}
```

### Upload Media File

```bash
curl -X POST http://localhost:8000/api/smart/upload/media \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/your/image.jpg"
```

**Response includes:**
- File ID for retrieval
- 3 thumbnail URLs (small, medium, large) for images
- Metadata (dimensions, file size, etc.)

### Retrieve Data

**Get JSON:**
```bash
curl -X GET http://localhost:8000/api/smart/retrieve/json/<doc_id> \
  -H "Authorization: Bearer $TOKEN"
```

**Get Media:**
```bash
curl -X GET http://localhost:8000/api/smart/retrieve/media/<file_id> \
  -H "Authorization: Bearer $TOKEN" \
  --output downloaded_file.jpg
```

**Get Thumbnail:**
```bash
curl -X GET "http://localhost:8000/api/smart/retrieve/media/<file_id>?thumbnail=medium" \
  -H "Authorization: Bearer $TOKEN" \
  --output thumbnail.jpg
```

### Get Statistics

```bash
curl -X GET http://localhost:8000/api/smart/stats \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📚 Key Endpoints

All endpoints are under `/api/smart/`

**Authentication:**
- `POST /auth/create` - Create admin
- `POST /auth/login` - Login (get token)
- `POST /auth/logout` - Logout

**JSON Operations:**
- `POST /analyze/json` - Preview categorization (no storage)
- `POST /upload/json` - Upload and store
- `GET /retrieve/json/<doc_id>` - Retrieve
- `GET /list/json` - List all
- `DELETE /delete/json/<doc_id>` - Delete

**Media Operations:**
- `POST /upload/media` - Upload file
- `GET /retrieve/media/<file_id>` - Download file
- `GET /retrieve/media/<file_id>?thumbnail=small` - Get thumbnail
- `GET /list/media` - List all files
- `DELETE /delete/media/<file_id>` - Delete file

**Statistics:**
- `GET /stats` - Get storage statistics

---

## 🔍 How It Decides: SQL vs NoSQL

The analyzer scores your JSON based on:

### → SQL (PostgreSQL) if:
- ✅ Consistent schema (same fields across objects)
- ✅ Shallow nesting (≤2 levels deep)
- ✅ Simple arrays (no nested arrays)
- ✅ Consistent data types
- ✅ Relational structure

### → NoSQL (MongoDB) if:
- ✅ Variable schema (different fields)
- ✅ Deep nesting (>2 levels)
- ✅ Complex nested arrays
- ✅ Mixed data types
- ✅ Hierarchical structure

**Confidence Score:** The system tells you how confident it is (0-100%)

---

## 🔐 Security Features

1. **Admin-Only Access**
   - All endpoints require authentication
   - Token-based (Bearer token in Authorization header)
   - Tokens expire after 24 hours

2. **Data Privacy**
   - All data stored on YOUR server
   - No external API calls
   - No data sharing

3. **Access Control**
   - Each admin can only access their own data
   - File isolation by admin ID

---

## 📁 File Organization

### Media Files
```
media_storage/
├── images/2024/01/15/      # Images by date
├── videos/2024/01/15/      # Videos by date
├── audio/2024/01/15/       # Audio by date
├── documents/2024/01/15/   # Documents by date
└── thumbnails/             # Auto-generated thumbnails
```

### Database Storage
- **PostgreSQL:** Dynamic tables per document with JSONB + GIN indexing
- **MongoDB:** `json_documents` collection with compound indexes

---

## 🎨 Example Use Cases

### Use Case 1: E-commerce Product Catalog
```bash
# Structured product data → SQL
POST /upload/json
[
  {"id": 1, "name": "Laptop", "price": 999, "category": "Electronics"},
  {"id": 2, "name": "Mouse", "price": 29, "category": "Electronics"}
]
```
**Result:** → PostgreSQL (consistent schema, perfect for queries)

### Use Case 2: User Profiles
```bash
# Complex user data → NoSQL
POST /upload/json
{
  "user": {
    "profile": {...},
    "preferences": {...},
    "activity": [...]
  }
}
```
**Result:** → MongoDB (deep nesting, hierarchical)

### Use Case 3: Image Gallery
```bash
# Upload images
POST /upload/media
file: image1.jpg

# System creates:
# - Original: /images/2024/01/15/admin_xxx_timestamp_hash.jpg
# - Small thumbnail: 150x150
# - Medium thumbnail: 300x300
# - Large thumbnail: 600x600
```

---

## 🚨 Troubleshooting

**"Invalid or expired token"**
→ Login again to get new token

**"Document not found"**
→ Check doc_id, verify you're the owner

**"Database connection failed"**
→ Ensure PostgreSQL/MongoDB/Redis are running

**Media not saving**
→ Check permissions on `media_storage/` directory

---

## 📖 Full Documentation

See `SMART_UPLOAD_GUIDE.md` for:
- Complete API reference
- All response examples
- Advanced configuration
- Performance optimization tips

---

## 🎯 Next Steps

1. ✅ Test the analyzer: `python test_smart_system.py`
2. ✅ Create admin user
3. ✅ Upload some JSON data
4. ✅ Upload media files
5. ✅ Check statistics
6. 📚 Read `SMART_UPLOAD_GUIDE.md` for advanced features

---

**You're all set! Start uploading and the system will automatically optimize storage for you! 🚀**
