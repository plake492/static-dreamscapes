#!/bin/bash

# LoFi Track Manager - Setup Script
# This script sets up the complete environment

set -e  # Exit on error

echo "🎵 LoFi Track Manager - Setup Script"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python 3
echo "📋 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Found Python $PYTHON_VERSION${NC}"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet
echo -e "${GREEN}✅ pip upgraded${NC}"
echo ""

# Install dependencies
echo "📚 Installing dependencies (this may take a few minutes)..."
echo "   - Core dependencies (typer, rich, pydantic, etc.)"
pip install typer rich pydantic pyyaml python-dotenv --quiet

echo "   - Notion integration"
pip install notion-client --quiet

echo "   - Audio analysis (librosa, soundfile)"
pip install librosa soundfile --quiet

echo "   - Machine learning (sentence-transformers, scikit-learn)"
pip install sentence-transformers scikit-learn --quiet

echo "   - Video processing (ffmpeg-python)"
pip install ffmpeg-python --quiet

echo -e "${GREEN}✅ All dependencies installed${NC}"
echo ""

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p data
mkdir -p data/cache/notion_docs
mkdir -p data/cache/audio_analysis
mkdir -p data/embeddings
mkdir -p output/playlists
mkdir -p output/logs
mkdir -p Tracks
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Create .env file if it doesn't exist
echo "🔐 Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file from template${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env and add your NOTION_API_TOKEN${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
fi
echo ""

# Initialize database
echo "🗄️  Initializing database..."
python3 -m src.cli.main init-db
echo ""

# Check for FFMPEG
echo "🎬 Checking for FFMPEG..."
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version | head -n1 | cut -d' ' -f3)
    echo -e "${GREEN}✅ FFMPEG installed (version $FFMPEG_VERSION)${NC}"
else
    echo -e "${YELLOW}⚠️  FFMPEG not found${NC}"
    echo "   FFMPEG is required for video generation (Phase 5)"
    echo "   Install with: brew install ffmpeg (macOS)"
    echo "               or: apt install ffmpeg (Linux)"
fi
echo ""

# Summary
echo "======================================"
echo "🎉 Setup Complete!"
echo "======================================"
echo ""
echo "✅ Virtual environment created and activated"
echo "✅ All Python dependencies installed"
echo "✅ Directory structure created"
echo "✅ Database initialized"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Configure Notion API:"
echo "   - Edit .env file"
echo "   - Add your NOTION_API_TOKEN"
echo "   - Get token from: https://www.notion.so/my-integrations"
echo ""
echo "2. Test the system:"
echo "   yarn help                    # View all commands"
echo "   yarn stats                   # Check database status"
echo ""
echo "3. Import your first track:"
echo "   yarn import \\"
echo "     --notion-url \"https://notion.so/your-track\" \\"
echo "     --songs-dir \"./Tracks/17-analogue-study-console/Songs\""
echo ""
echo "📚 Documentation:"
echo "   - YARN_COMMANDS.md          # All yarn commands"
echo "   - .agent-docs/              # Complete documentation"
echo ""
echo "🔧 Activate environment later with:"
echo "   source venv/bin/activate"
echo ""
echo "Happy organizing! 🎵"
