#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting K Fund Allocation API Server...${NC}"

# Check for python3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed.${NC}"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Install dependencies if needed
if [ -f "prototype/requirements.txt" ]; then
    echo -e "${BLUE}📦 Checking dependencies...${NC}"
    pip install -q -r prototype/requirements.txt
fi

# Kill any existing process on port 8002
if lsof -i :8002 > /dev/null; then
    echo -e "${BLUE}⚠️  Port 8002 in use. Stopping existing server...${NC}"
    kill $(lsof -t -i:8002) 2>/dev/null
    sleep 1
fi

# Start the server
echo -e "${GREEN}✅ Starting API server on http://localhost:8002${NC}"
echo -e "${BLUE}📝 Logs will be shown below (Press Ctrl+C to stop)${NC}"
echo ""

python3 prototype/api_server.py
