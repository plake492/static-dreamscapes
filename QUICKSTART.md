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

### 2. Later - Query for New Tracks (Phase 4 - Coming Soon)
```bash
# Create new track in Notion first, then:
yarn query \
  --notion-url "https://notion.so/new-track" \
  --output "./playlists/new-track.json"

# Shows:
# - 60-70% matching songs from your library
# - 30-40% gaps to fill with new generation
```

---

## 🔧 Common Commands

### Database
```bash
yarn init-db          # Initialize database (first time only)
yarn stats           # View statistics
yarn help            # Show all commands
```

### Import
```bash
# Basic import
yarn import --notion-url "URL" --songs-dir "PATH"

# Force re-analysis
yarn import:force --notion-url "URL" --songs-dir "PATH"
```

### Statistics
```bash
yarn stats           # All stats
yarn stats:songs     # Song details
yarn stats:tracks    # Track overview
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

- **YARN_COMMANDS.md** - All yarn commands with examples
- **.agent-docs/** - Complete technical documentation
- **README.md** - Existing project README

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

1. ✅ Run `./setup.sh`
2. ✅ Configure `.env` with Notion token
3. ✅ Import 3-5 existing tracks
4. ✅ View your library with `yarn stats`
5. ⏳ Wait for Phase 4 (query/matching)
6. ⏳ Start creating new tracks faster!

**Goal:** After importing your library, you'll reduce new track creation time by 40-60%!

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
