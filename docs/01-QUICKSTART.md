# LoFi Track Manager - Quick Start

Get up and running in 5 minutes.

---

## 🚀 Installation

### One-Line Setup (Recommended)
```bash
./setup.sh
```

This will:
- Create virtual environment
- Install all dependencies
- Create directory structure
- Initialize database
- Check for FFMPEG

### Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
yarn init-db
```

---

## 🔐 Configure Notion API

1. **Get your Notion API token**:
   - Go to https://www.notion.so/my-integrations
   - Click "New integration"
   - Copy the "Internal Integration Token"

2. **Add to .env file**:
   ```bash
   # Edit .env
   nano .env

   # Add this line:
   NOTION_API_TOKEN=secret_your_token_here
   ```

3. **Share your Notion pages**:
   - Open each track document in Notion
   - Click "Share" → "Invite"
   - Select your integration

---

## 📥 Import Your First Track

```bash
yarn import-songs --track 25 --notion-url "https://www.notion.so/your-track-page"
```

**What happens:**
- Fetches Notion document
- Analyzes all audio files (BPM, key, duration)
- Stores everything in database
- Shows summary table

**Takes about:** 1-2 minutes for 40-50 songs

---

## 🧠 Generate Embeddings

Required for semantic search:

```bash
yarn generate-embeddings
```

**What happens:**
- Creates 384-dimensional vector for each song
- Enables similarity search
- Caches for fast queries

**Takes about:** 30-60 seconds for 100 songs

---

## 📊 View Your Library

```bash
# View all statistics
yarn stats

# Just songs
yarn stats songs

# Just tracks
yarn stats tracks
```

---

## 🎯 Create Your First Track

### Complete Workflow

```bash
# 1. Scaffold track folder
yarn scaffold-track --track 26 --notion-url "https://notion.so/Track-26-..."

# 2. Query for matching songs
yarn query --track 26 --notion-url "https://notion.so/Track-26-..."

# 3. Analyze gaps
yarn gaps ./output/track-26-matches.json

# 4. Prepare songs for rendering
yarn prepare-render --track 26

# 5. Add background video to Tracks/26/Video/26.mp4

# 6. Test render (5 minutes)
yarn render --track 26 --duration test

# 7. Full render (3 hours)
yarn render --track 26 --duration 3
```

---

## 🔁 Building Your Library Workflow

### First Time Setup

```bash
# 1. Initialize (one time only)
./setup.sh

# 2. Import all your existing tracks
yarn import-songs --track 24 --notion-url "https://notion.so/Track-24-..."
yarn import-songs --track 25 --notion-url "https://notion.so/Track-25-..."

# 3. Generate embeddings once
yarn generate-embeddings
```

**Time:** 5-10 minutes for 2-3 tracks

### For Each New Track

```bash
# 1. Create folder structure
yarn scaffold-track --track 26 --notion-url "URL"

# 2. Find reusable songs
yarn query --track 26 --notion-url "URL"

# 3. Check what's missing
yarn gaps ./output/track-26-matches.json

# 4. Prepare matched songs
yarn prepare-render --track 26

# 5. Generate missing songs (if needed)
# Check Tracks/26/remaining-prompts.md for gaps
# Generate with your AI music tool
# Save to Tracks/26/Songs/ with correct naming

# 6. Import the complete track
yarn import-songs --track 26 --notion-url "URL"
yarn generate-embeddings

# 7. Add background video
# Place at Tracks/26/Video/26.mp4

# 8. Render
yarn render --track 26 --duration test  # Test first
yarn render --track 26 --duration 3     # Full render
```

**Time:** 2-3 hours per track (vs 4-5 hours without reuse)

---

## 💡 Key Commands Reference

```bash
# Setup & Database
yarn init-db                 # Initialize database
yarn generate-embeddings     # Generate/update embeddings

# Import & Analysis
yarn import-songs --track N --notion-url "URL"
yarn stats                   # View statistics

# Create Track
yarn scaffold-track --track N --notion-url "URL"
yarn query --track N --notion-url "URL"
yarn gaps ./output/track-N-matches.json
yarn prepare-render --track N

# Render
yarn track-duration --track N            # Check duration
yarn render --track N --duration test    # 5-min test
yarn render --track N --duration 3       # 3-hour render

# Post-Publish
yarn mark-published --track N --youtube-url "URL"
```

---

## 📖 Next Steps

### Learn More

- **[Track Creation Guide](./TRACK_CREATION_GUIDE.md)** - Detailed workflow
- **[CLI Reference](./CLI_REFERENCE.md)** - All commands
- **[Configuration](./03-CONFIGURATION.md)** - Customize settings

### Common Tasks

- **Generate missing songs:** Check `remaining-prompts.md` in track folder
- **Adjust render settings:** Use `--volume` and `--crossfade` flags
- **Find unused songs:** Run `yarn stats songs`

---

## 🐛 Troubleshooting

### "Could not find database"
```bash
yarn init-db
```

### "No embeddings found"
```bash
yarn generate-embeddings
```

### "Notion API error"
- Check token in `.env`
- Verify page is shared with integration

### "Background video not found"
- Ensure video exists at `Tracks/N/Video/N.mp4`
- Filename must match track number

---

## 🎯 Success Metrics

**What to expect:**
- **60-70% song reuse** - Most songs found in library
- **40-60% time savings** - 2-3 hours per track vs 4-5 hours
- **<30s query time** - Fast semantic search
- **<2min import** - Quick analysis and storage

---

**You're ready to go!** Start with `yarn scaffold-track` for your next track. 🚀

See **[TRACK_CREATION_GUIDE.md](./TRACK_CREATION_GUIDE.md)** for detailed workflow.
