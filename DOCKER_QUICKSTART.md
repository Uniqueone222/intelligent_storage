# 🐳 Docker Quick Start Guide

## One-Command Setup for Windows & Linux

This application is **fully containerized** with Docker, which means:
- ✅ Works identically on Windows, Mac, and Linux
- ✅ No need to install Python, PostgreSQL, MongoDB, or Ollama manually
- ✅ All dependencies bundled in containers
- ✅ One command to start everything

---

## Prerequisites

### Windows
1. **Install Docker Desktop for Windows**
   - Download: https://www.docker.com/products/docker-desktop
   - Requirements: Windows 10/11 (64-bit), WSL 2 enabled
   - System: 8GB RAM minimum, 20GB disk space

### Linux (Arch, Ubuntu, etc.)
1. **Install Docker**
   ```bash
   # Arch Linux
   sudo pacman -S docker docker-compose
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker $USER

   # Ubuntu/Debian
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker $USER
   ```

2. **Log out and back in** (required for group changes)

### macOS
1. **Install Docker Desktop for Mac**
   - Download: https://www.docker.com/products/docker-desktop
   - Requirements: macOS 10.15+, 8GB RAM, 20GB disk

---

## 🚀 Quick Start (3 Steps)

### Windows

1. **Clone the repository**
   ```cmd
   git clone https://github.com/yourusername/intelligent_storage.git
   cd intelligent_storage
   ```

2. **Run the start script**
   ```cmd
   start.bat
   ```

3. **Access the application**
   - The browser will open automatically
   - Or visit: http://localhost:8000/files/browse/

### Linux / macOS

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/intelligent_storage.git
   cd intelligent_storage
   ```

2. **Run the start script**
   ```bash
   ./start.sh
   ```

3. **Access the application**
   - Open browser: http://localhost:8000/files/browse/

---

## 📦 What Gets Installed in Containers

When you run the start script, Docker automatically:

1. **Creates 5 containers:**
   - `postgres` - PostgreSQL 15 with pgvector extension
   - `mongodb` - MongoDB 7.0 for NoSQL storage
   - `redis` - Redis for caching and task queues
   - `ollama` - Ollama AI service with Llama3 models
   - `backend` - Django application server

2. **Downloads AI models (first run only):**
   - `llama3:latest` (~4.7GB) - Text analysis
   - `llama3.2-vision` (~7.9GB) - Image analysis
   - This happens automatically in the background

3. **Creates persistent storage:**
   - Database data persists across restarts
   - Uploaded files persist in `media_files` volume
   - AI models downloaded only once

---

## 🎯 Common Tasks

### View Logs
```bash
# All services
docker-compose logs -f

# Just the backend
docker-compose logs -f backend

# Ollama AI service
docker-compose logs -f ollama
```

### Stop the Application
```bash
docker-compose stop
```

### Restart the Application
```bash
docker-compose restart
```

### Start Again (after stopping)
```bash
docker-compose up -d
```

### Complete Cleanup (removes all data!)
```bash
docker-compose down -v
```

### Force Rebuild (if you update code)
```bash
# Linux/Mac
./start.sh -f

# Windows
start.bat -f
```

---

## 🌐 Application URLs

Once started, access these URLs:

| Service | URL | Description |
|---------|-----|-------------|
| **File Browser** | http://localhost:8000/files/browse/ | Upload and browse files |
| **Admin Panel** | http://localhost:8000/admin/ | Django admin interface |
| **API Root** | http://localhost:8000/api/ | REST API endpoints |
| **Health Check** | http://localhost:8000/api/health/ | Service status |
| **API Stats** | http://localhost:8000/files/api/stats/ | File statistics |

---

## 💾 Data Persistence

All data is stored in Docker volumes and persists across restarts:

```bash
# List all volumes
docker volume ls | grep intelligent

# Inspect a volume
docker volume inspect intelligent_storage_postgres_data

# Backup a volume (Linux/Mac)
docker run --rm -v intelligent_storage_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz /data

# Restore a volume (Linux/Mac)
docker run --rm -v intelligent_storage_postgres_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

---

## 🔧 Advanced Configuration

### Using GPU for AI (Linux with NVIDIA GPU)

1. **Install NVIDIA Container Toolkit**
   ```bash
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
     sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```

2. **The docker-compose.yml already has GPU support configured!**
   - Ollama will automatically use GPU if available

### Without GPU (CPU-only mode)

If you don't have a GPU or it's not working, edit `docker-compose.yml`:

```yaml
# Comment out or remove this section from the ollama service:
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

---

## 🐛 Troubleshooting

### Container fails to start

**Check Docker daemon:**
```bash
# Linux
sudo systemctl status docker

# Windows: Check Docker Desktop is running
```

**View error logs:**
```bash
docker-compose logs backend
```

### Port already in use

If port 8000, 5432, 27017, or 11434 is already in use:

Edit `docker-compose.yml` and change the port mappings:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001 (or any free port)
```

### Ollama models not downloading

**Check ollama-init container:**
```bash
docker-compose logs ollama-init
```

**Manually pull models:**
```bash
docker exec -it intelligent_storage_ollama ollama pull llama3:latest
docker exec -it intelligent_storage_ollama ollama pull llama3.2-vision
```

### Out of disk space

**Check Docker disk usage:**
```bash
docker system df
```

**Clean up unused images/containers:**
```bash
docker system prune -a
```

### Database connection errors

**Restart database containers:**
```bash
docker-compose restart postgres mongodb
```

**Check database health:**
```bash
docker-compose ps
```

---

## 📊 System Requirements

### Minimum
- **CPU**: 4 cores
- **RAM**: 8GB
- **Disk**: 30GB free space
- **OS**: Windows 10/11, macOS 10.15+, Linux kernel 3.10+

### Recommended
- **CPU**: 8+ cores
- **RAM**: 16GB
- **Disk**: 50GB free space (SSD preferred)
- **GPU**: NVIDIA GPU with 8GB+ VRAM (optional, for faster AI)

---

## 🔄 Updates and Maintenance

### Update the application
```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose build

# Restart with new code
docker-compose up -d
```

### Update base images
```bash
# Pull latest images
docker-compose pull

# Rebuild
docker-compose up -d --build
```

---

## 🆘 Getting Help

1. **Check logs**: `docker-compose logs -f`
2. **Verify health**: http://localhost:8000/api/health/
3. **Check container status**: `docker-compose ps`
4. **Restart everything**: `docker-compose restart`

---

## 📝 Environment Variables (Optional)

Create a `.env` file in the root directory to customize:

```env
# PostgreSQL
POSTGRES_NAME=intelligent_storage_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# MongoDB
MONGODB_USER=admin
MONGODB_PASSWORD=your_secure_password

# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Ollama
OLLAMA_MODEL=llama3:latest
```

**Note**: Docker Compose will use these values automatically!

---

## ✅ Verification Checklist

After starting, verify everything works:

- [ ] All containers running: `docker-compose ps`
- [ ] Health check passes: http://localhost:8000/api/health/
- [ ] File browser loads: http://localhost:8000/files/browse/
- [ ] Can upload a file
- [ ] Admin panel accessible: http://localhost:8000/admin/
- [ ] Ollama models downloaded: `docker exec intelligent_storage_ollama ollama list`

---

## 🎉 That's It!

You now have a **fully functional AI-powered storage system** running in Docker!

- No manual installations
- Works the same on Windows, Linux, and Mac
- All services containerized and isolated
- Easy to start, stop, and update

**Share this with friends** - they just need Docker and can run `./start.sh` (Linux/Mac) or `start.bat` (Windows)!
