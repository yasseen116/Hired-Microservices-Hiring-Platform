#!/bin/bash

echo "================================================"
echo "  Starting Hired Platform Services (Dev Mode)"
echo "================================================"

# Kill any existing processes
pkill -f "uvicorn.*8000" 2>/dev/null
pkill -f "uvicorn.*8002" 2>/dev/null
pkill -f "uvicorn.*8003" 2>/dev/null
pkill -f "uvicorn.*5000" 2>/dev/null
sleep 2

# Base directory
BASE_DIR="/home/main/SAMS/college/hired"

# Start Job Service (port 8000)
echo ""
echo "Starting Job Service on port 8000..."
cd "$BASE_DIR/job-service/jobs-service"
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -q -r requirements.txt
uvicorn main:app --port 8000 --reload > /tmp/job-service.log 2>&1 &
echo "✓ Job Service started (PID: $!)"

# Start Auth Service (port 8002)
echo ""
echo "Starting Auth Service on port 8002..."
cd "$BASE_DIR/auth-service/auth-service"
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -q -r requirements.txt
uvicorn main:app --port 8002 --reload > /tmp/auth-service.log 2>&1 &
echo "✓ Auth Service started (PID: $!)"

# Start Application Service (port 8003)
echo ""
echo "Starting Application Service on port 8003..."
cd "$BASE_DIR/omar-application-service"
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -q -r requirements.txt
uvicorn main:app --port 8003 --reload > /tmp/app-service.log 2>&1 &
echo "✓ Application Service started (PID: $!)"

# Start Frontend (port 5000, accessible from outside)
echo ""
echo "Starting Frontend on port 5000 (0.0.0.0)..."
cd "$BASE_DIR/hired-front-end"
pip install -q -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 5000 --reload > /tmp/frontend.log 2>&1 &
echo "✓ Frontend started (PID: $!)"

sleep 3

echo ""
echo "================================================"
echo "  All Services Running!"
echo "================================================"
echo ""
echo "Frontend:     http://localhost:5000"
echo "Jobs API:     http://localhost:8000/docs"
echo "Auth API:     http://localhost:8002/docs"
echo "Apps API:     http://localhost:8003/docs"
echo ""
echo "Logs:"
echo "  tail -f /tmp/frontend.log"
echo "  tail -f /tmp/job-service.log"
echo "  tail -f /tmp/auth-service.log"
echo "  tail -f /tmp/app-service.log"
echo ""
echo "To stop all services:"
echo "  pkill -f 'uvicorn.*(8000|8002|8003|5000)'"
echo ""
