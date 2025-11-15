#!/bin/bash
# Start the Django backend server

cd "$(dirname "$0")/backend"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run setup first:"
    echo "  cd backend"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements_minimal.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found!"
    echo "Create .env file with database credentials."
    echo "See QUICKSTART.md for details."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "========================================="
echo "Starting Intelligent Storage Backend"
echo "========================================="
echo ""
echo "Backend will be available at: http://localhost:8000"
echo "API endpoints: http://localhost:8000/api/"
echo "Admin panel: http://localhost:8000/admin/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Django development server
python manage.py runserver
