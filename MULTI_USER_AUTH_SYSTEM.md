# Multi-User Authentication & Isolated Storage System

## Overview

The Intelligent Storage System now supports multiple users with complete data isolation. Each user has their own separate storage space for:
- JSON documents (SQL and NoSQL)
- Media files
- RAG documents
- File search stores

## Key Features

✅ **JWT-Based Authentication** - Secure token-based auth with configurable expiry
✅ **User Registration** - Simple email/password registration
✅ **Storage Quotas** - Per-user storage limits (default: 5 GB)
✅ **Data Isolation** - Complete separation between users
✅ **Profile Management** - Update profile, change password
✅ **Dual Auth System** - Separate admin and user authentication

---

## User Model

### User Fields

```python
class User:
    user_id          # UUID - unique identifier
    username         # Unique username
    email            # Unique email address
    full_name        # Optional full name
    phone            # Optional phone number

    # Storage
    storage_quota    # Total allowed storage (bytes)
    storage_used     # Current storage used (bytes)

    # Status
    is_active        # Account active/disabled
    is_verified      # Email verified
    is_staff         # Staff privileges

    # Timestamps
    created_at       # Account creation date
    updated_at       # Last profile update
    last_login       # Last login time

    # Metadata
    metadata         # JSON field for custom data
```

### Storage Quota

- **Default Quota**: 5 GB (5,368,709,120 bytes)
- **Storage Used**: Automatically tracked
- **Quota Check**: `user.is_quota_exceeded()` returns True/False
- **Space Check**: `user.has_storage_space(bytes)` checks before upload

---

## API Endpoints

### 1. User Registration

**Endpoint**: `POST /api/smart/users/register`

**Request**:
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password",
    "full_name": "John Doe",    // optional
    "phone": "+1234567890"       // optional
}
```

**Response** (201 Created):
```json
{
    "success": true,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "storage_quota": 5368709120,
    "storage_used": 0,
    "message": "User registered successfully"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/smart/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "mypassword123",
    "full_name": "John Doe"
  }'
```

---

### 2. User Login

**Endpoint**: `POST /api/smart/users/login`

**Request**:
```json
{
    "email": "john@example.com",
    "password": "secure_password"
}
```

**Response** (200 OK):
```json
{
    "success": true,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "storage_quota": 5368709120,
    "storage_used": 1234567,
    "storage_used_percentage": 0.023,
    "message": "Login successful"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/smart/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "mypassword123"
  }'

# Save the token
export USER_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 3. Get User Profile

**Endpoint**: `GET /api/smart/users/profile`
**Authorization**: Bearer Token Required

**Request**:
```bash
GET /api/smart/users/profile
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
    "success": true,
    "user": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "phone": "+1234567890",
        "storage_quota": 5368709120,
        "storage_used": 1234567,
        "storage_used_percentage": 0.023,
        "is_verified": false,
        "is_active": true,
        "created_at": "2025-11-15T10:30:00Z",
        "last_login": "2025-11-16T08:15:00Z",
        "metadata": {}
    }
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8000/api/smart/users/profile \
  -H "Authorization: Bearer $USER_TOKEN"
```

---

### 4. Update Profile

**Endpoint**: `PUT /api/smart/users/profile/update`
**Authorization**: Bearer Token Required

**Request**:
```json
{
    "full_name": "John Smith",
    "phone": "+9876543210",
    "metadata": {
        "company": "Acme Corp",
        "department": "Engineering"
    }
}
```

**Response** (200 OK):
```json
{
    "success": true,
    "message": "Profile updated successfully"
}
```

---

### 5. Change Password

**Endpoint**: `POST /api/smart/users/change-password`
**Authorization**: Bearer Token Required

**Request**:
```json
{
    "current_password": "old_password",
    "new_password": "new_secure_password"
}
```

**Response** (200 OK):
```json
{
    "success": true,
    "message": "Password changed successfully"
}
```

---

### 6. Logout

**Endpoint**: `POST /api/smart/users/logout`
**Authorization**: Bearer Token Required

**Response** (200 OK):
```json
{
    "success": true,
    "message": "Logged out successfully"
}
```

**Note**: JWT tokens are stateless, so logout is handled client-side by removing the token.

---

## Data Isolation

### How It Works

1. **User Association**: All data models have a `user` foreign key
   - `FileSearchStore.user`
   - `MediaFile.user`
   - `JSONDataStore.user`
   - `DocumentChunk.file_search_store.user`

2. **Automatic Filtering**: All queries automatically filter by user
   ```python
   # User A can only see their data
   my_files = MediaFile.objects.filter(user=user_a)

   # User B has completely separate data
   their_files = MediaFile.objects.filter(user=user_b)
   ```

3. **JWT Authentication**: Every request includes user token
   ```
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

4. **User Injection**: The `@require_user` decorator injects the user
   ```python
   @require_user
   def upload_json(request, user):
       # user is automatically available
       # data is saved with user=user
   ```

### Storage Separation

**PostgreSQL (SQL)**:
```sql
-- json_documents table
SELECT * FROM json_documents WHERE admin_id = 'user_uuid_1';  -- User 1's data
SELECT * FROM json_documents WHERE admin_id = 'user_uuid_2';  -- User 2's data
```

**MongoDB (NoSQL)**:
```javascript
// json_documents collection
db.json_documents.find({ admin_id: 'user_uuid_1' })  // User 1's data
db.json_documents.find({ admin_id: 'user_uuid_2' })  // User 2's data
```

---

## Security Features

### 1. Password Security
- **Hashing**: Django's PBKDF2 algorithm with SHA256
- **Salting**: Automatic random salt per password
- **Validation**: Length, similarity, common password checks

### 2. JWT Tokens
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiry**: 24 hours (configurable)
- **Secret**: Django SECRET_KEY
- **Payload**:
  ```json
  {
      "user_id": "uuid",
      "email": "user@example.com",
      "username": "john_doe",
      "exp": 1700000000,  // expiration timestamp
      "iat": 1699913600   // issued at timestamp
  }
  ```

### 3. Authorization
- **Token Validation**: Every protected endpoint validates JWT
- **User Verification**: Token must belong to active user
- **Expiry Check**: Expired tokens are rejected (401)

### 4. Data Isolation
- **User-Based Filtering**: All queries filtered by user
- **Foreign Key Constraints**: CASCADE delete ensures data cleanup
- **No Cross-User Access**: User A cannot access User B's data

---

## Admin vs User Authentication

The system supports two types of authentication:

### Admin Authentication
- **Purpose**: System administration
- **Endpoints**: `/api/smart/auth/*`
- **Storage**: JSON file (`admin_auth.json`)
- **Use Cases**: Managing system, viewing all data

### User Authentication
- **Purpose**: Regular users
- **Endpoints**: `/api/smart/users/*`
- **Storage**: PostgreSQL database
- **Use Cases**: Personal data storage and retrieval

**Both can coexist** - Admins for system management, users for data storage.

---

## Frontend Integration

### 1. Registration Flow

```javascript
async function registerUser(userData) {
    const response = await fetch('http://localhost:8000/api/smart/users/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
    });

    const data = await response.json();

    if (data.success) {
        // Store token
        localStorage.setItem('userToken', data.token);
        localStorage.setItem('userId', data.user_id);
        localStorage.setItem('username', data.username);

        // Redirect to dashboard
        window.location.href = '/dashboard';
    } else {
        alert(data.error);
    }
}

// Usage
registerUser({
    username: 'john_doe',
    email: 'john@example.com',
    password: 'secure_password',
    full_name: 'John Doe'
});
```

### 2. Login Flow

```javascript
async function loginUser(email, password) {
    const response = await fetch('http://localhost:8000/api/smart/users/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (data.success) {
        // Store token and user info
        localStorage.setItem('userToken', data.token);
        localStorage.setItem('userId', data.user_id);
        localStorage.setItem('username', data.username);
        localStorage.setItem('storageQuota', data.storage_quota);
        localStorage.setItem('storageUsed', data.storage_used);

        return true;
    } else {
        throw new Error(data.error);
    }
}
```

### 3. Making Authenticated Requests

```javascript
async function uploadJSON(jsonData) {
    const token = localStorage.getItem('userToken');

    const response = await fetch('http://localhost:8000/api/smart/upload/json', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(jsonData)
    });

    return await response.json();
}

async function getUserProfile() {
    const token = localStorage.getItem('userToken');

    const response = await fetch('http://localhost:8000/api/smart/users/profile', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });

    return await response.json();
}
```

### 4. Logout

```javascript
async function logoutUser() {
    const token = localStorage.getItem('userToken');

    await fetch('http://localhost:8000/api/smart/users/logout', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });

    // Clear local storage
    localStorage.removeItem('userToken');
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    localStorage.removeItem('storageQuota');
    localStorage.removeItem('storageUsed');

    // Redirect to login
    window.location.href = '/login';
}
```

---

## Database Migrations

### Required Migration

Create and apply the migration for the User model:

```bash
cd backend
python manage.py makemigrations storage
python manage.py migrate storage
```

This will create:
1. **User table** with all fields
2. **Foreign keys** on existing models (FileSearchStore, MediaFile, JSONDataStore)
3. **Indexes** for performance

---

## Testing

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/smart/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/smart/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'

# Save the returned token
export TOKEN="<token_from_response>"
```

### 3. Get Profile

```bash
curl -X GET http://localhost:8000/api/smart/users/profile \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Upload Data (User-Specific)

```bash
curl -X POST http://localhost:8000/api/smart/upload/json \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John",
    "age": 30,
    "city": "New York"
  }'
```

### 5. List User's Documents

```bash
curl -X GET http://localhost:8000/api/smart/list/json \
  -H "Authorization: Bearer $TOKEN"
```

---

## Storage Quota Management

### Checking Quota

```python
from storage.models import User

user = User.objects.get(email='user@example.com')

print(f"Quota: {user.storage_quota / (1024**3):.2f} GB")
print(f"Used: {user.storage_used / (1024**3):.2f} GB")
print(f"Percentage: {user.storage_used_percentage:.2f}%")
print(f"Exceeded: {user.is_quota_exceeded()}")
```

### Updating Quota

```python
# Increase quota to 10 GB
user.storage_quota = 10 * 1024**3  # 10 GB in bytes
user.save()

# Check available space
required_bytes = 500 * 1024**2  # 500 MB
if user.has_storage_space(required_bytes):
    print("Upload allowed")
else:
    print("Quota exceeded")
```

---

## Error Handling

### Common Errors

**400 Bad Request**:
- Missing required fields
- Invalid JSON
- Invalid email format

**401 Unauthorized**:
- Missing Authorization header
- Invalid or expired token
- Incorrect credentials

**403 Forbidden**:
- Account disabled
- Insufficient permissions

**409 Conflict**:
- Username already exists
- Email already registered

**507 Insufficient Storage**:
- Storage quota exceeded

---

## Security Best Practices

1. **HTTPS Only**: Use HTTPS in production
2. **Token Storage**: Store JWT in httpOnly cookies (not localStorage)
3. **Token Expiry**: Implement token refresh mechanism
4. **Password Policy**: Enforce strong passwords
5. **Rate Limiting**: Add rate limiting to prevent brute force
6. **Email Verification**: Verify user emails before activation
7. **Two-Factor Auth**: Consider 2FA for sensitive operations

---

## Summary

The multi-user authentication system provides:

✅ **Complete User Management** - Registration, login, profile, password
✅ **JWT Authentication** - Secure, stateless token-based auth
✅ **Data Isolation** - Each user's data is completely separate
✅ **Storage Quotas** - Per-user storage limits with quota tracking
✅ **Dual Auth System** - Admin and user authentication coexist
✅ **RESTful API** - Clean, standard API endpoints
✅ **Frontend Ready** - Easy integration with any frontend

**Users can now register, login, and use their own isolated storage space!** 🚀
