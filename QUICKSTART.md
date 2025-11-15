# Quick Start Guide

This guide will get you up and running in minutes!

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.10+ installed
- ✅ PostgreSQL installed and running
- ✅ MongoDB installed and running
- ✅ Ollama installed with llama3 model

## Setup Steps

### 1. Create Databases

**PostgreSQL:**
```bash
sudo -u postgres psql
```

In PostgreSQL shell:
```sql
CREATE DATABASE intelligent_storage_db;
CREATE USER postgres WITH PASSWORD 'postgres123';
GRANT ALL PRIVILEGES ON DATABASE intelligent_storage_db TO postgres;
\q
```

**MongoDB:**
```bash
mongosh
```

In MongoDB shell:
```javascript
use admin
db.createUser({
  user: "admin",
  pwd: "admin123",
  roles: [
    { role: "userAdminAnyDatabase", db: "admin" },
    "readWriteAnyDatabase"
  ]
})
exit
```

### 2. Pull AI Models

```bash
ollama pull llama3:latest
ollama pull llama3.2-vision
```

### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements_minimal.txt

# Create .env file (copy from below)
cat > .env << 'EOF'
POSTGRES_NAME=intelligent_storage_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USER=admin
MONGODB_PASSWORD=admin123
MONGODB_DB=intelligent_storage_nosql

OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3:latest

DJANGO_SECRET_KEY=your-secret-key-change-in-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
EOF

# Run migrations
python manage.py migrate

# Create admin user (optional)
python manage.py createsuperuser
```

### 4. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python -m http.server 3000
```

### 5. Access the Application

Open your browser to: **http://localhost:3000**

## Test the System

### Upload a File

1. Click "Upload Files" tab
2. Drag and drop an image
3. Click "Upload Files"
4. Watch the AI categorize it!

### Upload JSON Data

1. Click "Upload JSON Data" tab
2. Paste this example:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30
}
```
3. Click "Upload JSON Data"
4. See the AI recommend SQL or NoSQL!

## Troubleshooting

### "Connection refused" errors

Check if services are running:
```bash
# PostgreSQL
sudo systemctl status postgresql
sudo systemctl start postgresql

# MongoDB (Arch: mongodb, Others: mongod)
sudo systemctl status mongodb
sudo systemctl start mongodb

# Ollama
ollama list
ollama serve
```

### "Database does not exist"

Make sure you created the databases in Step 1.

### "Module not found" errors

Make sure virtual environment is activated:
```bash
source venv/bin/activate
```

### Import errors

Install dependencies:
```bash
pip install -r requirements_minimal.txt
```

## API Endpoints

Once running, test the API:

```bash
# Health check
curl http://localhost:8000/api/health/

# Upload a file
curl -X POST http://localhost:8000/api/upload/file/ \
  -F "file=@/path/to/image.jpg"

# Upload JSON
curl -X POST http://localhost:8000/api/upload/json/ \
  -H "Content-Type: application/json" \
  -d '{"data": {"name": "Test"}}'
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [ARCH_LINUX_GUIDE.md](ARCH_LINUX_GUIDE.md) if you're on Arch
- Explore the API at http://localhost:8000/api/
- View admin panel at http://localhost:8000/admin/

## Default Credentials

**⚠️ Change these in production!**

- PostgreSQL: `postgres` / `postgres123`
- MongoDB: `admin` / `admin123`
- Django Admin: (created during createsuperuser step)

Enjoy your Intelligent Storage System! 🚀
