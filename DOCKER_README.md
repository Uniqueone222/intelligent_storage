# 🐳 Intelligent Storage System - Docker Edition

## The "Works Everywhere" Solution

**One command. Any platform. Zero configuration.**

This is the **recommended way** to run the Intelligent Storage System on **any operating system**.

---

## ✨ Why Docker?

### The Problem
- ❌ "It works on my machine but not yours"
- ❌ Different Python versions
- ❌ Missing system libraries
- ❌ Database configuration hell
- ❌ OS-specific bugs

### The Solution
- ✅ **One click setup** - Works identically on Windows, Mac, Linux
- ✅ **All dependencies included** - Python, PostgreSQL, MongoDB, Ollama, AI models
- ✅ **Isolated environment** - Doesn't affect your system
- ✅ **Share with anyone** - They just run one command

---

## 🚀 Quick Start (Literally 2 Commands)

### Windows
```cmd
git clone https://github.com/yourusername/intelligent_storage.git
cd intelligent_storage
start.bat
```

### Linux / macOS
```bash
git clone https://github.com/yourusername/intelligent_storage.git
cd intelligent_storage
./start.sh
```

**That's it!** Everything installs automatically.

---

## 📦 What You Get

When you run the start script, Docker creates:

| Service | Container | What it does |
|---------|-----------|--------------|
| **PostgreSQL** | `postgres` | Stores file metadata with vector search |
| **MongoDB** | `mongodb` | NoSQL document storage |
| **Redis** | `redis` | Caching and task queues |
| **Ollama** | `ollama` | AI models for file analysis |
| **Django** | `backend` | Main application server |

**Total size**: ~15GB (includes AI models)
**First start**: 10-15 minutes (downloads everything)
**Subsequent starts**: 30 seconds

---

## 🎯 Installation Requirements

### All You Need
1. **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
2. **8GB RAM minimum** (16GB recommended)
3. **30GB free disk space**
4. **Internet connection** (for first-time setup)

That's it. No Python, no PostgreSQL, no MongoDB, no Ollama needed!

---

## 📖 Step-by-Step Setup

### For Windows Users

#### Step 1: Install Docker Desktop
1. Download from: https://www.docker.com/products/docker-desktop
2. Run the installer
3. Restart your computer
4. Open Docker Desktop and wait for it to start

#### Step 2: Clone and Run
1. Open **Command Prompt** or **PowerShell**
2. Run:
   ```cmd
   git clone https://github.com/yourusername/intelligent_storage.git
   cd intelligent_storage
   start.bat
   ```

3. **First run**: Wait 10-15 minutes while it:
   - Downloads Docker images (~5GB)
   - Downloads AI models (~10GB)
   - Sets up databases
   - Starts all services

4. Browser opens automatically to: http://localhost:8000/files/browse/

#### Step 3: Use the Application
- Upload files
- Browse by category
- AI automatically analyzes and organizes everything

---

### For Linux Users (Arch, Ubuntu, Debian, etc.)

#### Step 1: Install Docker

**Arch Linux:**
```bash
sudo pacman -S docker docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and back in
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and back in
```

#### Step 2: Clone and Run
```bash
git clone https://github.com/yourusername/intelligent_storage.git
cd intelligent_storage
./start.sh
```

#### Step 3: Access Application
Open browser: http://localhost:8000/files/browse/

---

### For macOS Users

#### Step 1: Install Docker Desktop
1. Download from: https://www.docker.com/products/docker-desktop
2. Drag to Applications
3. Open Docker Desktop
4. Follow setup wizard

#### Step 2: Clone and Run
```bash
git clone https://github.com/yourusername/intelligent_storage.git
cd intelligent_storage
./start.sh
```

#### Step 3: Access Application
Open browser: http://localhost:8000/files/browse/

---

## 🎮 Using the Application

### Access Points
- **File Browser**: http://localhost:8000/files/browse/
- **Upload Files**: Drag & drop or click to upload
- **Admin Panel**: http://localhost:8000/admin/
- **API**: http://localhost:8000/api/
- **Health Check**: http://localhost:8000/api/health/

### Features
- ✅ Upload any file type
- ✅ AI automatically detects and categorizes
- ✅ Organized into smart folders
- ✅ Semantic search across documents
- ✅ Image content analysis
- ✅ Metadata extraction

---

## 🔧 Common Tasks

### View Logs
```bash
# All services
docker-compose logs -f

# Just backend
docker-compose logs -f backend

# AI service
docker-compose logs -f ollama
```

### Stop Application
```bash
docker-compose stop
```

### Start Again
```bash
docker-compose up -d
```

### Complete Reset (removes all data!)
```bash
docker-compose down -v
```

### Update to Latest Version
```bash
git pull origin main
./start.sh -f  # Linux/Mac
start.bat -f   # Windows
```

---

## 💡 Tips & Tricks

### For Windows Users

**Use WSL 2 Backend** (recommended):
- Docker Desktop > Settings > General
- Check "Use WSL 2 based engine"
- Much faster performance!

**Increase Resources**:
- Docker Desktop > Settings > Resources
- RAM: 8GB minimum (16GB recommended)
- CPU: 4 cores minimum
- Disk: 50GB recommended

### For All Users

**First Run Checklist**:
- [ ] Docker is running (check system tray/menu bar)
- [ ] No other services using ports 8000, 5432, 27017, 11434
- [ ] At least 30GB free disk space
- [ ] Stable internet connection

**Speed Up First Start**:
```bash
# Pre-download images
docker-compose pull

# Then start
./start.sh  # or start.bat
```

---

## 🐛 Troubleshooting

### "Docker is not running"
- **Windows**: Start Docker Desktop from Start Menu
- **Linux**: `sudo systemctl start docker`
- **Mac**: Open Docker Desktop from Applications

### "Port already in use"
Another service is using the port. Find and stop it, or edit `docker-compose.yml` to use different ports.

### "Out of disk space"
```bash
# Clean up Docker
docker system prune -a

# Remove old volumes
docker volume prune
```

### Models not downloading
```bash
# Manually pull models
docker exec -it intelligent_storage_ollama ollama pull llama3:latest
docker exec -it intelligent_storage_ollama ollama pull llama3.2-vision
```

### Application slow on Windows
1. Enable WSL 2 in Docker Desktop settings
2. Increase RAM allocation (Settings > Resources)
3. Store project in WSL filesystem (not Windows)

---

## 🔐 Security Notes

### Development Mode (default)
- Debug mode enabled
- Default passwords
- All hosts allowed
- **DO NOT USE IN PRODUCTION!**

### Production Mode
1. Create `.env` file with secure credentials
2. Set `DJANGO_DEBUG=False`
3. Change all default passwords
4. Configure `DJANGO_ALLOWED_HOSTS`
5. Use HTTPS
6. Enable firewall rules

---

## 📊 System Resources

### Typical Usage
- **CPU**: 10-30% (idle), 50-100% (AI processing)
- **RAM**: 4-6GB (idle), 8-12GB (AI active)
- **Disk**: 15GB (base), grows with uploaded files
- **Network**: ~15GB download on first start

### With GPU (Linux + NVIDIA)
- **GPU Memory**: 4-8GB during AI analysis
- **CPU**: Much lower (~10-20%)
- **Processing**: 3-5x faster

---

## 🎯 Comparison: Docker vs Manual Install

| Aspect | Docker 🐳 | Manual Install 🔧 |
|--------|-----------|------------------|
| **Setup time** | 2 commands | 30+ commands |
| **Works on** | Windows, Mac, Linux | Depends on OS |
| **Dependencies** | Automatic | Manual |
| **Conflicts** | Isolated | Can break system |
| **Updates** | One command | Reinstall everything |
| **Sharing** | Easy | Impossible |
| **Consistency** | 100% | "Works on my machine" |

**Winner**: Docker 🏆

---

## 🌟 Advanced: GPU Acceleration (Linux)

### Enable GPU for Faster AI

1. **Install NVIDIA Docker**:
   ```bash
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
     sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```

2. **Use default docker-compose.yml** (already configured for GPU)

3. **Verify**:
   ```bash
   docker exec intelligent_storage_ollama nvidia-smi
   ```

### Without GPU (Windows, Mac, CPU-only Linux)
Use the CPU-only version:
```bash
docker-compose -f docker-compose.no-gpu.yml up -d
```

---

## 📚 Additional Resources

- **Full Documentation**: See [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)
- **API Documentation**: See [API_ENDPOINTS_MAPPING.md](backend/API_ENDPOINTS_MAPPING.md)
- **Original README**: See [README.md](README.md) for manual installation
- **Docker Documentation**: https://docs.docker.com/

---

## ❓ FAQ

**Q: Do I need to know Docker?**
A: No! Just run `start.sh` or `start.bat`

**Q: Can I develop while Docker is running?**
A: Yes! Code changes are reflected immediately (hot reload)

**Q: What if I already have PostgreSQL/MongoDB installed?**
A: No problem! Docker containers are isolated. No conflicts.

**Q: How do I backup my data?**
A: All data is in Docker volumes. See [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) for backup commands.

**Q: Can I use this in production?**
A: Yes, but change default passwords and disable debug mode first!

**Q: Does this work on ARM/M1 Macs?**
A: Yes! All images support ARM64 architecture.

---

## 🎉 Success!

If everything worked, you should see:

✅ Containers running: `docker-compose ps`
✅ Health check: http://localhost:8000/api/health/
✅ File browser: http://localhost:8000/files/browse/
✅ Can upload files
✅ AI analysis working

**Welcome to the Intelligent Storage System!** 🚀

---

## 💬 Support

Having issues? Check:
1. [Troubleshooting section](#-troubleshooting) above
2. [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) for detailed help
3. Docker logs: `docker-compose logs -f`
4. Health check: http://localhost:8000/api/health/

---

**Made with** ❤️ **and** 🐳 **Docker**
