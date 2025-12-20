# LoFi Track Manager - Quick Start

Get up and running in 5 minutes.

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
yarn import \
  --notion-url "https://www.notion.so/your-track-page" \
  --songs-dir "./Tracks/17-analogue-study-console/Songs"
```

**What happens:**
- Fetches Notion document
- Analyzes all audio files (BPM, key, duration)
- Stores everything in database
- Shows summary table

**Takes about:** 1-2 minutes for 40-50 songs

---

## 📊 View Your Library

```bash
# View all statistics
yarn stats

# Just songs
yarn stats:songs

# Just tracks
yarn stats:tracks
```

---

## 🎯 Typical Workflow

### 1. First Time - Build Your Library
```bash
# Initialize (one time only)
./setup.sh

# Import all your existing tracks
yarn import --notion-url "URL_TRACK_17" --songs-dir "./Tracks/17-*/Songs"
yarn import --notion-url "URL_TRACK_16" --songs-dir "./Tracks/16-*/Songs"
yarn import --notion-url "URL_TRACK_15" --songs-dir "./Tracks/15-*/Songs"

# Check your library
yarn stats
```

**After importing 3-5 tracks, you'll have:**
- 150-250 songs cataloged
- All with BPM, key, duration metadata
- Ready for semantic search (Phase 4)

---

### 2. Create New Tracks (Full Workflow)
```bash
# Step 1: Query for matches
yarn query \
  --notion-url "https://notion.so/new-track" \
  --output "./output/playlists/track-20-matches.json"

# Step 2: Analyze gaps
yarn gaps "./output/playlists/track-20-matches.json"

# Step 3: Scaffold track folder
yarn scaffold-track --track-number 20 --notion-url "https://notion.so/new-track"

# Step 4: Prepare for rendering
yarn prepare-render --track 20 --playlist "./output/playlists/track-20-matches.json"

# Step 5: Generate missing songs (if needed)
# Use AI generator for gaps identified in Step 2

# Step 6: Render video with automated FFmpeg
yarn render --track 20 --duration 3  # 3-hour render

# Step 7: Import rendered songs
yarn post-render --track 20
yarn generate-embeddings

# Step 8: Publish
yarn publish --track 20 --youtube-url "https://youtube.com/watch?v=..."
```

**Results:**
- 60-70% song reuse from library
- 30-40% new generation needed
- 40-60% time savings per track!

---

## 🔧 Common Commands

### Database & Setup
```bash
yarn init-db                # Initialize database (first time only)
yarn generate-embeddings    # Generate embeddings (after importing songs)
yarn stats                  # View statistics
yarn help                   # Show all commands
```

### Import & Analysis
```bash
# Basic import
yarn import-songs --notion-url "URL" --songs-dir "PATH"

# Force re-analysis
yarn import:force --notion-url "URL" --songs-dir "PATH"
```

### Query & Gaps
```bash
# Query for new track
yarn query --notion-url "URL" --output "./output/playlists/track-X.json"

# Analyze gaps
yarn gaps "./output/playlists/track-X.json"
yarn gaps "./output/playlists/track-X.json" --min-similarity 0.7
```

### Track Management
```bash
yarn scaffold-track --track-number X --notion-url "URL"
yarn track-duration --track X
yarn prepare-render --track X --playlist "FILE"
yarn post-render --track X
yarn publish --track X --youtube-url "URL"
```

### Statistics
```bash
yarn stats               # All stats
yarn stats:songs         # Song details
yarn stats:tracks        # Track overview
```

### Database Viewing
```bash
./scripts/view_db.sh songs     # View all songs
./scripts/view_db.sh tracks    # View all tracks
./scripts/view_db.sh arc 2     # Songs in Arc 2
./scripts/view_db.sh stats     # Quick stats
```

---

## 📁 File Organization

Your audio files should be named: `arc_prompt_song[order].mp3`

**Examples:**
- `1_1_45a.mp3` → Arc 1, Prompt 1, Song 45, Order a
- `2_6_19a.mp3` → Arc 2, Prompt 6, Song 19, Order a
- `3_2_88b.mp3` → Arc 3, Prompt 2, Song 88, Order b

**Typical structure:**
```
Tracks/
├── 17-analogue-study-console/
│   └── Songs/
│       ├── 1_1_45a.mp3
│       ├── 1_2_46a.mp3
│       ├── 2_1_47a.mp3
│       └── ...
```

---

## ❓ Troubleshooting

### "Notion API authentication failed"
- Check `.env` has `NOTION_API_TOKEN`
- Make sure you shared the Notion page with your integration

### "No songs found in directory"
- Check files match pattern: `arc_prompt_song[order].mp3`
- Make sure path is correct

### "Module not found"
- Run `source venv/bin/activate`
- Then `pip install -r requirements.txt`

### "Command not found: yarn"
```bash
npm install -g yarn
```

---

## 📖 Documentation

- **SYSTEM_COMPLETE.md** - Complete system overview (all phases)
- **PHASE_6_COMPLETE.md** - Phase 6 workflow automation details
- **QUICKSTART.md** - This file (quick reference)
- **README.md** - Project overview

---

## ✅ Verify Installation

```bash
# Should show version
yarn version

# Should show empty database
yarn stats

# Should show help
yarn help
```

---

## 🎉 Next Steps

1. ✅ Run `./setup.sh` (or manual setup)
2. ✅ Configure `.env` with Notion token
3. ✅ Import 3-5 existing tracks
4. ✅ Generate embeddings: `yarn generate-embeddings`
5. ✅ View your library with `yarn stats`
6. ✅ Query for new tracks!
7. ✅ Start creating tracks 40-60% faster!

**System Status:** All 6 phases complete and production-ready! 🚀

---

## 💡 Pro Tips

**Use aliases** for common commands:
```bash
# Add to ~/.bashrc or ~/.zshrc
alias lofi="cd ~/Dev/personal/static-dreamwaves && source venv/bin/activate"
alias lofi-import="yarn import"
alias lofi-stats="yarn stats"
```

Then use:
```bash
lofi
lofi-stats
lofi-import --notion-url "URL" --songs-dir "PATH"
```

**Batch import** multiple tracks:
```bash
# Create a script
cat > import_all.sh << 'EOF'
#!/bin/bash
yarn import --notion-url "$1" --songs-dir "$2"
EOF

chmod +x import_all.sh

# Use it
./import_all.sh "URL_17" "./Tracks/17-*/Songs"
./import_all.sh "URL_16" "./Tracks/16-*/Songs"
```

---

**That's it! You're ready to start organizing your lofi empire!** 🎵
