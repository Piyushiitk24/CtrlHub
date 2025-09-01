#!/bin/bash

# CtrlHub Development Server Launcher
# One command to rule them all! 🚀

set -e  # Exit on any error

echo "🎛️  Starting CtrlHub Development Environment..."
echo "=============================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to kill processes on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down CtrlHub development servers...${NC}"
    
    # Kill Python local agent (port 8003)
    if lsof -Pi :8003 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "   Stopping local agent (port 8003)..."
        lsof -Pi :8003 -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
    fi
    
    # Kill React dev server (port 3000)
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "   Stopping React dev server (port 3000)..."
        lsof -Pi :3000 -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
    fi
    
    # Kill any remaining node processes for this project
    pkill -f "npm start" 2>/dev/null || true
    pkill -f "react-scripts start" 2>/dev/null || true
    
    echo -e "${GREEN}✅ All servers stopped cleanly!${NC}"
    exit 0
}

# Set up cleanup trap
trap cleanup EXIT INT TERM

# Step 1: Clean up any existing processes
echo -e "${BLUE}🧹 Cleaning up existing processes...${NC}"
lsof -Pi :8003 -sTCP:LISTEN -t 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -Pi :3000 -sTCP:LISTEN -t 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 2

# Step 2: Check virtual environment
echo -e "${BLUE}🐍 Checking Python environment...${NC}"
if [ ! -d "$PROJECT_ROOT/ctrlhub_env" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Creating virtual environment..."
    cd "$PROJECT_ROOT"
    python3 -m venv ctrlhub_env
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
source "$PROJECT_ROOT/ctrlhub_env/bin/activate"
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Step 3: Install/update Python dependencies
echo -e "${BLUE}📦 Checking Python dependencies...${NC}"
cd "$PROJECT_ROOT/local_agent"
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Python dependencies ready${NC}"

# Step 4: Install/update Node dependencies
echo -e "${BLUE}📦 Checking Node.js dependencies...${NC}"
cd "$PROJECT_ROOT/frontend"
if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
    echo "Installing/updating Node.js dependencies..."
    npm install --silent
fi
echo -e "${GREEN}✅ Node.js dependencies ready${NC}"

# Step 5: Start the local agent in background
echo -e "${BLUE}🖥️  Starting CtrlHub Local Agent...${NC}"
cd "$PROJECT_ROOT/local_agent"
python main.py &
LOCAL_AGENT_PID=$!

# Wait for local agent to start
echo "   Waiting for local agent to initialize..."
sleep 3

# Check if local agent started successfully
if ! kill -0 $LOCAL_AGENT_PID 2>/dev/null; then
    echo -e "${RED}❌ Local agent failed to start!${NC}"
    exit 1
fi

# Verify local agent is responding
for i in {1..10}; do
    if curl -s http://localhost:8003/status >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Local agent running on http://localhost:8003${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ Local agent not responding after 10 seconds${NC}"
        exit 1
    fi
    sleep 1
done

# Step 6: Start React development server
echo -e "${BLUE}🌐 Starting React Development Server...${NC}"
cd "$PROJECT_ROOT/frontend"

# Start React dev server in background and capture its output
npm start &
REACT_PID=$!

# Wait for React dev server to start
echo "   Waiting for React server to initialize..."
sleep 5

# Check if React dev server started successfully
if ! kill -0 $REACT_PID 2>/dev/null; then
    echo -e "${RED}❌ React dev server failed to start!${NC}"
    exit 1
fi

# Verify React dev server is responding
for i in {1..20}; do
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ React dev server running on http://localhost:3000${NC}"
        break
    fi
    if [ $i -eq 20 ]; then
        echo -e "${RED}❌ React dev server not responding after 20 seconds${NC}"
        exit 1
    fi
    sleep 1
done

# Step 7: Open browser
echo -e "${BLUE}🌍 Opening CtrlHub in browser...${NC}"
sleep 2
if command -v open >/dev/null 2>&1; then
    # macOS
    open http://localhost:3000/components/dc-motor/parameter-extraction
elif command -v xdg-open >/dev/null 2>&1; then
    # Linux
    xdg-open http://localhost:3000/components/dc-motor/parameter-extraction
elif command -v start >/dev/null 2>&1; then
    # Windows
    start http://localhost:3000/components/dc-motor/parameter-extraction
fi

# Step 8: Show status and keep running
echo ""
echo -e "${GREEN}🎉 CtrlHub Development Environment Ready!${NC}"
echo "=============================================="
echo -e "${GREEN}✅ Local Agent:${NC}     http://localhost:8003"
echo -e "${GREEN}✅ Web Interface:${NC}   http://localhost:3000"
echo -e "${GREEN}✅ Parameter Page:${NC}  http://localhost:3000/components/dc-motor/parameter-extraction"
echo ""
echo -e "${YELLOW}💡 Development Tips:${NC}"
echo "   • Both servers will auto-reload on file changes"
echo "   • Press Ctrl+C to stop all servers"
echo "   • Check terminal output for any errors"
echo ""
echo -e "${BLUE}📊 Monitoring servers... (Press Ctrl+C to stop)${NC}"

# Keep the script running and monitor the servers
while true; do
    # Check if local agent is still running
    if ! kill -0 $LOCAL_AGENT_PID 2>/dev/null; then
        echo -e "${RED}❌ Local agent stopped unexpectedly!${NC}"
        exit 1
    fi
    
    # Check if React dev server is still running
    if ! kill -0 $REACT_PID 2>/dev/null; then
        echo -e "${RED}❌ React dev server stopped unexpectedly!${NC}"
        exit 1
    fi
    
    sleep 5
done
