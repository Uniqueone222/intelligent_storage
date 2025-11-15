# Git Ignore Configuration

## What's Ignored

The `.gitignore` file now excludes all unnecessary files from version control:

### Python Cache Files
- `__pycache__/` - Python bytecode cache directories
- `*.pyc` - Compiled Python files
- `*.pyo` - Optimized Python files
- `*.py[cod]` - All Python compiled variations

### Environment Files
- `.env` - Main environment variables file
- `.env.local` - Local environment overrides
- `.env.*.local` - Environment-specific local files

### Virtual Environment
- `venv/` - Your Python virtual environment
- `env/` - Alternative venv name
- `.venv` - Hidden venv directory

### Django Files
- `*.log` - Log files
- `db.sqlite3` - SQLite database (if used)
- `/staticfiles/` - Collected static files
- `/media/` - Uploaded media files

### IDE Files
- `.vscode/` - VS Code settings
- `.idea/` - PyCharm/IntelliJ settings
- `*.swp`, `*.swo` - Vim swap files
- `.DS_Store` - Mac OS metadata

### Testing & Coverage
- `.pytest_cache/` - Pytest cache
- `.coverage` - Coverage data
- `htmlcov/` - Coverage HTML reports
- `.mypy_cache/` - Type checker cache

### Build & Distribution
- `build/` - Build artifacts
- `dist/` - Distribution packages
- `*.egg-info/` - Package metadata

---

## Cleanup

### Already Cleaned
✓ Removed all `__pycache__` directories (excluding venv)
✓ Removed all `.pyc` files (excluding venv)

### Cleanup Script

Run the cleanup script anytime to remove cached files:

```bash
./cleanup.sh
```

This will remove:
- Python cache files (`__pycache__`, `.pyc`, `.pyo`)
- Temporary files (`*.tmp`, `*.bak`, `*~`)
- Test artifacts (`.pytest_cache`, `.coverage`)
- OS metadata (`.DS_Store`)
- Type checker cache (`.mypy_cache`)

---

## Usage

### Check What Git Will Ignore

```bash
# See what files are ignored
git status --ignored

# Check if a specific file is ignored
git check-ignore -v filename
```

### Force Add Ignored File (if needed)

```bash
# If you really need to track an ignored file
git add -f path/to/file
```

### Update Gitignore

If you need to add more patterns:

```bash
echo "new_pattern/" >> .gitignore
```

---

## Important Notes

### Files Already Excluded

These important files are safely ignored and won't be committed:

1. **`.env`** - Contains sensitive environment variables, API keys, database passwords
2. **`venv/`** - Large virtual environment (can be recreated with `requirements.txt`)
3. **`__pycache__/`** - Automatically regenerated Python cache
4. **`media/`** - User-uploaded files (should be backed up separately)
5. **`staticfiles/`** - Collected static files (generated with `collectstatic`)
6. **`.pyc` files** - Compiled Python bytecode (automatically regenerated)

### Files You SHOULD Commit

These are tracked in git:

- ✓ `*.py` - Your Python source code
- ✓ `requirements.txt` - Python dependencies
- ✓ `manage.py` - Django management script
- ✓ `*.html` - Templates
- ✓ `*.js`, `*.css` - Frontend assets
- ✓ `*.md` - Documentation
- ✓ `*.sh` - Shell scripts (like `run.sh`, `cleanup.sh`)

### Sensitive Data Protection

The `.env` file is ignored, which protects:
- Database passwords
- Secret keys
- API keys
- Email credentials
- OAuth tokens

**Never commit `.env` to git!** Instead, create a `.env.example` file with dummy values:

```bash
# Create example env file (safe to commit)
cp .env .env.example
# Edit .env.example to remove real values
```

---

## Git Commands Quick Reference

```bash
# Initialize git (if not already done)
git init

# Add files (respects .gitignore)
git add .

# Check status (shows ignored files with --ignored)
git status
git status --ignored

# Commit changes
git commit -m "Your commit message"

# Push to remote
git push origin main

# Clean up untracked files (CAREFUL!)
git clean -fd  # Removes untracked files/directories
git clean -fX  # Removes only ignored files
```

---

## Summary

Your `.gitignore` is now configured to:
- ✅ Exclude `__pycache__` directories
- ✅ Exclude `.env` files
- ✅ Exclude `venv/` virtual environment
- ✅ Exclude all Python cache files
- ✅ Exclude media uploads
- ✅ Exclude IDE settings
- ✅ Exclude logs and temporary files

This keeps your repository clean and protects sensitive data!
