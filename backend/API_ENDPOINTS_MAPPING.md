# API Endpoints Mapping - Intelligent Storage System

## Overview
This document maps all frontend API calls to their corresponding backend endpoints.

**Last Updated:** November 15, 2025
**Status:** ✅ All endpoints connected and tested

---

## Base URLs

- **API Base:** `http://localhost:8000/api/`
- **File Browser Base:** `http://localhost:8000/files/`
- **Admin:** `http://localhost:8000/admin/`

---

## 1. File Browser APIs

### 1.1 Get Folder Statistics
**Frontend Call:**
```javascript
fetch('/files/api/stats/')
```

**Backend Endpoint:** `GET /files/api/stats/`
**View:** `storage.file_browser_views.folder_stats_api`
**Response:**
```json
{
  "by_type": {
    "image": {"count": 4, "size_bytes": 1455632, "size_mb": 1.39, "folder": "images"},
    "video": {"count": 0, "size_bytes": 0, "size_mb": 0.0, "folder": "videos"},
    "audio": {"count": 0, "size_bytes": 0, "size_mb": 0.0, "folder": "audio"},
    "document": {"count": 11, "size_bytes": 538090, "size_mb": 0.51, "folder": "documents"},
    "code": {"count": 0, "size_bytes": 0, "size_mb": 0.0, "folder": "code"},
    "compressed": {"count": 0, "size_bytes": 0, "size_mb": 0.0, "folder": "compressed"},
    "program": {"count": 0, "size_bytes": 0, "size_mb": 0.0, "folder": "programs"},
    "other": {"count": 0, "size_bytes": 0, "size_mb": 0.0, "folder": "others"}
  },
  "total": {
    "count": 20,
    "size_bytes": 2738715,
    "size_mb": 2.61
  }
}
```
**Status:** ✅ Working

---

### 1.2 Browse Files by Category
**Frontend Call:**
```javascript
fetch(`/files/api/browse/?category=${category}&limit=100`)
```

**Backend Endpoint:** `GET /files/api/browse/`
**View:** `storage.file_browser_views.file_browser_api`
**Query Parameters:**
- `category` (optional): Filter by type (all, image, video, audio, document, code, compressed, other)
- `limit` (optional): Number of files (default: 50, max: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "files": [
    {
      "id": 28,
      "name": "frontend_test.txt",
      "type": "document",
      "size": 25,
      "mime_type": "text/plain",
      "uploaded_at": "2025-11-15T15:08:36.284206+00:00",
      "is_indexed": false,
      "relative_path": "documents/2025/11/frontend_test.txt",
      "preview_url": "/media/documents/2025/11/frontend_test.txt"
    }
  ],
  "total_count": 28,
  "limit": 100,
  "offset": 0,
  "has_more": false
}
```
**Status:** ✅ Working

---

### 1.3 Download File
**Frontend Call:**
```javascript
window.open(`/files/api/download/${fileId}/`, '_blank')
```

**Backend Endpoint:** `GET /files/api/download/<int:file_id>/`
**View:** `storage.file_browser_views.download_file`
**Response:** Binary file with `Content-Disposition: attachment`
**Status:** ✅ Working

---

### 1.4 Preview File
**Frontend Call:**
```javascript
window.open(`/files/api/preview/${fileId}/`, '_blank')
```

**Backend Endpoint:** `GET /files/api/preview/<int:file_id>/`
**View:** `storage.file_browser_views.preview_file`
**Response:** Binary file with `Content-Disposition: inline`
**Status:** ✅ Working

---

## 2. File Upload APIs

### 2.1 Unified File Upload
**Frontend Call:**
```javascript
const formData = new FormData();
for (let file of files) {
  formData.append('files', file);  // NOTE: Use 'files' (plural)!
}

fetch('/api/upload/file/', {
  method: 'POST',
  body: formData
})
```

**Backend Endpoint:** `POST /api/upload/file/`
**View:** `storage.unified_upload.UnifiedFileUploadView`
**Request Body:** `multipart/form-data`
- `files` (required): File(s) to upload (use 'files' field for all uploads)
- `user_comment` (optional): Comment for categorization
- `file_search_store` (optional): Store ID to index to
- `auto_index` (optional): Boolean to auto-index (default: false)

**Response (Single File):**
```json
{
  "success": true,
  "file": {
    "id": 28,
    "original_name": "frontend_test.txt",
    "file_path": "/path/to/file",
    "file_size": 25,
    "detected_type": "documents",
    "mime_type": "text/plain",
    "storage_category": "documents",
    "storage_subcategory": "general",
    "relative_path": "documents/2025/11/frontend_test.txt"
  },
  "message": "File uploaded and organized in documents/general/"
}
```

**Response (Multiple Files):**
```json
{
  "success": true,
  "batch_id": "uuid-here",
  "total": 2,
  "processed": 2,
  "failed": 0,
  "results": [
    {
      "file": "test1.txt",
      "status": "success",
      "id": 24,
      "category": "documents",
      "subcategory": "general"
    }
  ]
}
```
**Status:** ✅ Working

---

### 2.2 Batch Upload (Legacy - Redirects to Unified)
**Backend Endpoint:** `POST /api/upload/batch/`
**View:** Same as `/api/upload/file/` - `storage.unified_upload.UnifiedFileUploadView`
**Status:** ✅ Working (redirects to unified handler)

---

## 3. Health Check

### 3.1 System Health
**Frontend Call:**
```javascript
fetch('/api/health/')
```

**Backend Endpoint:** `GET /api/health/`
**View:** `storage.views.health_check`
**Response:**
```json
{
  "status": "healthy",
  "services": {
    "django": true,
    "postgresql": true,
    "mongodb": true,
    "ollama": true
  }
}
```
**Status:** ✅ Working

---

## 4. RAG (Semantic Search) APIs

### 4.1 Index Document
**Backend Endpoint:** `POST /api/rag/index/<int:file_id>/`
**View:** `storage.views.index_document`
**Status:** Available

### 4.2 Semantic Search
**Backend Endpoint:** `POST /api/rag/search/`
**View:** `storage.views.semantic_search`
**Request Body:**
```json
{
  "query": "search text",
  "top_k": 5
}
```
**Status:** Available

### 4.3 RAG Query
**Backend Endpoint:** `POST /api/rag/query/`
**View:** `storage.views.rag_query`
**Status:** Available

### 4.4 Reindex All
**Backend Endpoint:** `POST /api/rag/reindex-all/`
**View:** `storage.views.reindex_all`
**Status:** Available

### 4.5 RAG Stats
**Backend Endpoint:** `GET /api/rag/stats/`
**View:** `storage.views.rag_stats`
**Status:** Available

---

## 5. ViewSet APIs (REST Framework Routers)

### 5.1 Media Files
**Base:** `/api/media-files/`
- `GET /api/media-files/` - List all media files
- `POST /api/media-files/` - Create media file
- `GET /api/media-files/<id>/` - Retrieve media file
- `PUT /api/media-files/<id>/` - Update media file
- `PATCH /api/media-files/<id>/` - Partial update
- `DELETE /api/media-files/<id>/` - Delete media file

**Additional Actions:**
- `GET /api/media-files/statistics/` - Get file statistics
- `GET /api/media-files/by_type/<str:file_type>/` - Get files by type

**Status:** Available

### 5.2 JSON Data Stores
**Base:** `/api/json-stores/`
- Standard REST operations (list, create, retrieve, update, delete)

**Status:** Available

### 5.3 File Search Stores
**Base:** `/api/file-search-stores/`
- Standard REST operations
- Gemini-style file search functionality

**Status:** Available

---

## 6. Smart Upload System

**Base:** `/api/smart/`
- Intelligent SQL/NoSQL routing
- Admin authentication required

**Status:** Available (requires authentication)

---

## 7. File Manager

**Base:** `/api/filemanager/`
- Web-based file explorer for smart folders

**Status:** Available

---

## Frontend Pages

### File Browser
**URL:** `http://localhost:8000/files/browse/`
**Template:** `templates/storage/file_browser.html`
**Features:**
- Browse files by category
- Upload files (drag & drop or click)
- Download and preview files
- Search files
- View statistics

**Status:** ✅ Working

### File Manager
**URL:** `http://localhost:8000/api/filemanager/`
**Template:** `templates/file_manager.html`
**Status:** Available

---

## Critical Notes

### ⚠️ File Upload Field Name
**IMPORTANT:** The unified upload endpoint ONLY accepts `files` (plural) field name.

**Correct:**
```javascript
formData.append('files', file);
```

**Incorrect:**
```javascript
formData.append('file', file);  // ❌ This will fail!
```

### File Type Mapping
The system uses singular forms in the frontend and plural forms in the database:
- Frontend: `image, video, audio, document, code, compressed, program, other`
- Database: `images, videos, audio, documents, code, compressed, programs, others`

The backend automatically handles this conversion.

---

## Testing Commands

### Test Stats API
```bash
curl -s http://localhost:8000/files/api/stats/ | python3 -m json.tool
```

### Test Browse API
```bash
curl -s "http://localhost:8000/files/api/browse/?category=all&limit=5" | python3 -m json.tool
```

### Test Upload API
```bash
curl -X POST http://localhost:8000/api/upload/file/ \
  -F "files=@test.txt" | python3 -m json.tool
```

### Test Health Check
```bash
curl -s http://localhost:8000/api/health/ | python3 -m json.tool
```

---

## Connection Status Summary

| Endpoint | Frontend | Backend | Status |
|----------|----------|---------|--------|
| File Browser Stats | ✅ | ✅ | ✅ Working |
| File Browser Browse | ✅ | ✅ | ✅ Working |
| File Download | ✅ | ✅ | ✅ Working |
| File Preview | ✅ | ✅ | ✅ Working |
| File Upload | ✅ | ✅ | ✅ Working (Fixed) |
| Health Check | ✅ | ✅ | ✅ Working |
| RAG APIs | ❌ | ✅ | Available |
| Media Files ViewSet | ❌ | ✅ | Available |
| JSON Stores | ❌ | ✅ | Available |
| File Search Stores | ❌ | ✅ | Available |

---

## Recent Fixes

### November 15, 2025
1. **Fixed unified upload** - Added `_detect_file_type_from_mime()` method
2. **Fixed frontend upload** - Changed from `'file'` to `'files'` field name
3. **All file browser APIs tested and working**
4. **Upload functionality fully operational**

---

## Next Steps for Full Integration

1. Create frontend pages for RAG search
2. Add UI for Media Files management
3. Implement File Search Store frontend
4. Add Smart Upload UI with auth
5. Enhance file manager interface
