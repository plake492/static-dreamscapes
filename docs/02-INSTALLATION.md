# Installation Guide

Complete installation instructions for the LoFi Track Manager.

---

## Prerequisites

- **Python:** 3.10 or higher
- **SQLite3:** Usually pre-installed on macOS/Linux
- **FFMPEG:** For video rendering (optional)
- **Node.js/Yarn:** For package scripts (optional, can use Python directly)
- **RAM:** ~2GB minimum
- **Disk Space:** ~500MB (excluding audio files)

---

## Quick Setup (Recommended)

### One-Command Installation

```bash
./setup.sh
```

This script will:
1. Create Python virtual environment
2. Install all Python dependencies
3. Create necessary directory structure
4. Initialize SQLite database
5. Check for FFMPEG installation

**Time:** 2-3 minutes

---

## Manual Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-org/static-dreamwaves.git
cd static-dreamwaves
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Verify installation
python -c "import librosa, sentence_transformers; print('Success!')"
```

### 4. Initialize Database

```bash
# Using yarn (if available)
yarn init-db

# Or directly with Python
python -m src.cli.main init-db
```

### 5. Create Directory Structure

```bash
mkdir -p data/embeddings
mkdir -p data/cache/notion_docs
mkdir -p output
mkdir -p Tracks
mkdir -p Rendered
```

---

## Notion API Setup

### 1. Create Integration

1. Go to https://www.notion.so/my-integrations
2. Click **"New integration"**
3. Name it (e.g., "LoFi Track Manager")
4. Select workspace
5. Click **"Submit"**
6. Copy the **"Internal Integration Token"**

### 2. Configure Token

Create a `.env` file in project root:

```bash
# .env
NOTION_API_TOKEN=secret_your_token_here_from_step_1
```

Or update `config/settings.yaml`:

```yaml
notion_api_token: "secret_your_token_here_from_step_1"
```

### 3. Share Pages with Integration

For each Notion track document:
1. Open the page in Notion
2. Click **"Share"** (top right)
3. Click **"Invite"**
4. Select your integration name
5. Click **"Invite"**

---

## FFMPEG Installation (For Rendering)

### macOS
```bash
brew install ffmpeg
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

### Windows
Download from https://ffmpeg.org/download.html and add to PATH

### Verify
```bash
ffmpeg -version
```

---

## Verify Installation

### Check Python Environment

```bash
# Activate venv if not already active
source venv/bin/activate

# Check Python version
python --version  # Should be 3.10+

# Check key packages
python -c "
import librosa
import sentence_transformers
import notion_client
print('All packages installed successfully!')
"
```

### Check Database

```bash
# Initialize database (safe to run multiple times)
yarn init-db

# Check database was created
ls -lh data/tracks.db
```

### Check CLI

```bash
# Show version
yarn version-info

# Show help
python -m src.cli.main --help
```

---

## Optional: Yarn Setup

If you don't have yarn/node installed, you can use Python directly:

```bash
# Instead of: yarn init-db
python -m src.cli.main init-db

# Instead of: yarn import-songs --track 25 --notion-url "..."
python -m src.cli.main import-songs --track 25 --notion-url "..."
```

**Yarn is recommended** for convenience but not required.

---

## Directory Structure After Setup

```
static-dreamwaves/
├── venv/                    # ✅ Virtual environment
├── data/
│   ├── tracks.db            # ✅ SQLite database
│   ├── embeddings/          # ✅ Embedding cache (empty initially)
│   └── cache/               # ✅ Notion cache
├── output/                  # ✅ Query results
├── Tracks/                  # ✅ Track folders (empty initially)
├── Rendered/                # ✅ Rendered videos (empty initially)
├── .env                     # ✅ API tokens (create manually)
├── config/
│   └── settings.yaml        # ✅ Configuration
└── src/                     # ✅ Source code
```

---

## First Import Test

Verify everything works by importing a test track:

```bash
# 1. Make sure you have a track folder with songs
ls Tracks/25/Songs/

# 2. Import the track
yarn import-songs --track 25 --notion-url "https://notion.so/your-track-page"

# 3. Generate embeddings
yarn generate-embeddings

# 4. Check stats
yarn stats
```

If this works, you're ready to go!

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'librosa'"

**Solution:**
```bash
source venv/bin/activate  # Make sure venv is active
pip install -r requirements.txt
```

### "notion_client.errors.APIResponseError: Could not find database"

**Solution:**
- Make sure you shared the Notion page with your integration
- Verify your API token in `.env` or `config/settings.yaml`

### "FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'"

**Solution:**
- Install FFMPEG (see FFMPEG Installation section above)
- Only needed for video rendering, not required for import/query

### "permission denied: ./setup.sh"

**Solution:**
```bash
chmod +x setup.sh
./setup.sh
```

---

## Updating

To update to the latest version:

```bash
# Pull latest code
git pull origin main

# Activate venv
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt --upgrade

# Database migrations (if any)
yarn init-db  # Safe to run, won't delete data
```

---

## Uninstallation

To remove the project:

```bash
# 1. Deactivate virtual environment
deactivate

# 2. Delete project folder
cd ..
rm -rf static-dreamwaves

# 3. (Optional) Remove Notion integration
# Go to https://www.notion.so/my-integrations and delete the integration
```

---

## Next Steps

After installation:

1. **Import existing tracks:** [TRACK_CREATION_GUIDE.md](./TRACK_CREATION_GUIDE.md)
2. **Learn the workflow:** [04-WORKFLOW.md](./04-WORKFLOW.md)
3. **Browse commands:** [CLI_REFERENCE.md](./CLI_REFERENCE.md)

---

## Support

- **Documentation:** [docs/README.md](./README.md)
- **Quick Start:** [01-QUICKSTART.md](./01-QUICKSTART.md)
- **CLI Reference:** [CLI_REFERENCE.md](./CLI_REFERENCE.md)
