#!/bin/bash
# Cleanup script for Django project
# Removes Python cache files, temporary files, and other clutter

echo "🧹 Cleaning up Django project..."

# Remove __pycache__ directories (excluding venv)
echo "  → Removing __pycache__ directories..."
find . -type d -name "__pycache__" -not -path "*/venv/*" -exec rm -rf {} + 2>/dev/null
echo "  ✓ Removed __pycache__"

# Remove .pyc files
echo "  → Removing .pyc files..."
find . -type f -name "*.pyc" -not -path "*/venv/*" -delete 2>/dev/null
echo "  ✓ Removed .pyc files"

# Remove .pyo files
echo "  → Removing .pyo files..."
find . -type f -name "*.pyo" -not -path "*/venv/*" -delete 2>/dev/null
echo "  ✓ Removed .pyo files"

# Remove .DS_Store (Mac)
echo "  → Removing .DS_Store files..."
find . -type f -name ".DS_Store" -delete 2>/dev/null
echo "  ✓ Removed .DS_Store files"

# Remove temporary files
echo "  → Removing temporary files..."
find . -type f -name "*.tmp" -delete 2>/dev/null
find . -type f -name "*.bak" -delete 2>/dev/null
find . -type f -name "*~" -delete 2>/dev/null
echo "  ✓ Removed temporary files"

# Remove pytest cache
echo "  → Removing pytest cache..."
find . -type d -name ".pytest_cache" -not -path "*/venv/*" -exec rm -rf {} + 2>/dev/null
echo "  ✓ Removed pytest cache"

# Remove coverage files
echo "  → Removing coverage files..."
find . -type f -name ".coverage" -not -path "*/venv/*" -delete 2>/dev/null
find . -type d -name "htmlcov" -not -path "*/venv/*" -exec rm -rf {} + 2>/dev/null
echo "  ✓ Removed coverage files"

# Remove mypy cache
echo "  → Removing mypy cache..."
find . -type d -name ".mypy_cache" -not -path "*/venv/*" -exec rm -rf {} + 2>/dev/null
echo "  ✓ Removed mypy cache"

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Summary:"
echo "  - Python cache files removed"
echo "  - Temporary files removed"
echo "  - Test/coverage artifacts removed"
echo ""
