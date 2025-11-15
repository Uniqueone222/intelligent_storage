# Arch Linux Quick Start Guide

This guide is specifically tailored for Arch Linux users setting up the Intelligent Multi-Modal Storage System.

## One-Command Setup

For the fastest setup, use the automated script:

```bash
cd intelligent_storage
./setup_arch.sh
```

This will handle everything automatically!

## Key Differences for Arch Linux

### 1. Package Management
```bash
# Arch uses pacman and AUR
sudo pacman -S postgresql file python
yay -S mongodb-bin ollama  # From AUR
```

### 2. Service Names
```bash
# MongoDB service is 'mongodb' (not 'mongod')
sudo systemctl start mongodb    # Arch
sudo systemctl start mongod     # Other distros

# PostgreSQL uses standard name
sudo systemctl start postgresql
```

### 3. Python Environment (Important!)
Arch enforces PEP 668 - you **must** use virtual environments:
```bash
# This will fail on Arch:
pip install django  # ❌ Error: externally-managed-environment

# Always use venv:
python -m venv venv
source venv/bin/activate
pip install django  # ✅ Works!
```

### 4. PostgreSQL Initialization
On Arch, you must manually initialize PostgreSQL:
```bash
sudo -u postgres initdb -D /var/lib/postgres/data
```

## Step-by-Step Manual Setup

### 1. Install System Packages
```bash
sudo pacman -S postgresql file python base-devel git
```

### 2. Install AUR Packages
Using yay:
```bash
yay -S mongodb-bin ollama
```

Or manually:
```bash
# MongoDB
git clone https://aur.archlinux.org/mongodb-bin.git
cd mongodb-bin && makepkg -si

# Ollama
git clone https://aur.archlinux.org/ollama.git
cd ollama && makepkg -si
```

### 3. Initialize PostgreSQL
```bash
sudo -u postgres initdb -D /var/lib/postgres/data
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 4. Start Services
```bash
sudo systemctl start mongodb ollama postgresql
sudo systemctl enable mongodb ollama postgresql
```

### 5. Pull AI Models
```bash
ollama pull llama3:latest
ollama pull llama3.2-vision
```

### 6. Setup Project
```bash
cd intelligent_storage/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements_minimal.txt
```

### 7. Configure Databases

Create `.env` file:
```bash
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

DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
EOF
```

Setup PostgreSQL:
```bash
sudo -u postgres psql << 'EOF'
CREATE DATABASE intelligent_storage_db;
CREATE USER postgres WITH PASSWORD 'postgres123';
GRANT ALL PRIVILEGES ON DATABASE intelligent_storage_db TO postgres;
\q
EOF
```

Setup MongoDB:
```bash
mongosh << 'EOF'
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
EOF
```

### 8. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 9. Start the Application

Terminal 1 - Backend:
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

Terminal 2 - Frontend:
```bash
cd frontend
python -m http.server 3000
```

Access at: http://localhost:3000

## Common Arch-Specific Issues

### Pip Install Fails
```bash
# Error: externally-managed-environment
# Solution: Always use venv
python -m venv venv
source venv/bin/activate
```

### MongoDB Won't Start
```bash
# Check service name (it's 'mongodb' not 'mongod' on Arch)
sudo systemctl status mongodb
sudo systemctl start mongodb
```

### PostgreSQL Won't Start
```bash
# Likely not initialized
sudo -u postgres initdb -D /var/lib/postgres/data
sudo systemctl start postgresql
```

### Python 3.13 Package Conflicts
```bash
# Some older packages may not support Python 3.13 yet
# Install an older Python version if needed
yay -S python311
python3.11 -m venv venv
```

### Ollama Not Found
```bash
# Install from AUR
yay -S ollama

# Or use official script
curl -fsSL https://ollama.com/install.sh | sh

# Start the service
sudo systemctl start ollama
```

### Missing Build Dependencies
```bash
# For Pillow and other packages that need compilation
sudo pacman -S libjpeg-turbo zlib libtiff libwebp
```

## Verification Commands

Check all services are running:
```bash
# PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -c "SELECT version();"

# MongoDB
sudo systemctl status mongodb
mongosh --eval "db.version()"

# Ollama
sudo systemctl status ollama
ollama list

# Python packages
source venv/bin/activate
pip list
```

## Performance Tips for Arch

1. **Use systemd services** instead of manual starts for better management
2. **Enable services** to start on boot:
   ```bash
   sudo systemctl enable postgresql mongodb ollama
   ```
3. **Monitor logs** with journalctl:
   ```bash
   journalctl -u ollama -f
   journalctl -u mongodb -f
   ```

## Uninstallation

To completely remove:
```bash
# Stop services
sudo systemctl stop postgresql mongodb ollama
sudo systemctl disable postgresql mongodb ollama

# Remove packages
sudo pacman -Rns postgresql file
yay -Rns mongodb-bin ollama

# Remove data
sudo rm -rf /var/lib/postgres
sudo rm -rf /var/lib/mongodb
```

## Additional Resources

- [Arch Wiki - PostgreSQL](https://wiki.archlinux.org/title/PostgreSQL)
- [Arch Wiki - MongoDB](https://wiki.archlinux.org/title/MongoDB)
- [AUR - Ollama](https://aur.archlinux.org/packages/ollama)
- Main README.md for detailed feature documentation

## Need Help?

1. Check the main [README.md](README.md) for detailed documentation
2. Review the [Troubleshooting section](README.md#troubleshooting)
3. Verify all services are running: `systemctl status postgresql mongodb ollama`
4. Check logs: `journalctl -xe`
