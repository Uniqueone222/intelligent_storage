#!/bin/bash
# Start the frontend HTTP server

cd "$(dirname "$0")/frontend"

echo "========================================="
echo "Starting Intelligent Storage Frontend"
echo "========================================="
echo ""
echo "Frontend will be available at: http://localhost:3000"
echo ""
echo "Make sure the backend is running at http://localhost:8000"
echo "Start backend with: ./start_backend.sh"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Check if index.html exists
if [ ! -f "index.html" ]; then
    echo "Error: index.html not found in frontend directory!"
    exit 1
fi

# Start HTTP server
python -m http.server 3000
