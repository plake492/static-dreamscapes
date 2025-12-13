# Yarn Command Reference

Quick reference for all available yarn scripts.

## 🚀 Setup Commands

### Initialize Database
```bash
yarn init-db
```
Creates the SQLite database and schema. **Run this first!**

### View Help
```bash
yarn help
```
Shows all available CLI commands with descriptions.

### Check Version
```bash
yarn version
```
Shows the LoFi Track Manager version.

---

## 📥 Import Commands

### Import Songs from Track
```bash
yarn import --notion-url "https://notion.so/your-track" --songs-dir "./path/to/songs"
```

**Example:**
```bash
yarn import \
  --notion-url "https://www.notion.so/analogue-study-console-abc123" \
  --songs-dir "./Tracks/17-analogue-study-console/Songs"
```

### Force Re-import (Re-analyze existing songs)
```bash
yarn import:force --notion-url "URL" --songs-dir "PATH"
```

**When to use:**
- Songs already imported but you want fresh analysis
- Updated audio files
- Changed Notion document

---

## 📊 Statistics Commands

### View Song Statistics
```bash
yarn stats:songs
```
Shows:
- Total songs in database
- Most used songs
- Unused songs
- BPM and arc information

### View Track Statistics
```bash
yarn stats:tracks
```
Shows:
- Total tracks in database
- Track titles and status
- Track numbers and durations

### Quick Stats (alias for songs)
```bash
yarn stats
```
Same as `yarn stats:songs`

---

## 🔍 Query Commands (Coming Soon - Phase 4)

### Query for Matching Songs
```bash
yarn query --notion-url "https://notion.so/new-track" --output "./playlists/new-track.json"
```
**Status:** 🚧 Not yet implemented

### View Playlist Gaps
```bash
yarn gaps --playlist "./playlists/new-track.json"
```
**Status:** 🚧 Not yet implemented

---

## 🎬 Rendering Commands (Coming Soon - Phase 5)

### Scaffold New Track
```bash
yarn scaffold --track-number 18 --notion-url "https://notion.so/new-track"
```
**Status:** 🚧 Not yet implemented

### Calculate Track Duration
```bash
yarn duration --track 18
```
**Status:** 🚧 Not yet implemented

### Prepare for Rendering
```bash
yarn prepare --track 18
```
**Status:** 🚧 Not yet implemented

### Post-Render Import
```bash
yarn post-render --track 18
```
**Status:** 🚧 Not yet implemented

### Mark as Published
```bash
yarn publish --track 18 --youtube-url "https://youtube.com/watch?v=xxx"
```
**Status:** 🚧 Not yet implemented

---

## 📖 Common Workflows

### First Time Setup
```bash
# 1. Initialize database
yarn init-db

# 2. Import your first track
yarn import \
  --notion-url "https://notion.so/track-17" \
  --songs-dir "./Tracks/17-analogue-study-console/Songs"

# 3. Check the results
yarn stats:songs
```

### Import Multiple Tracks
```bash
# Import track 17
yarn import \
  --notion-url "https://notion.so/track-17" \
  --songs-dir "./Tracks/17-analogue-study-console/Songs"

# Import track 16
yarn import \
  --notion-url "https://notion.so/track-16" \
  --songs-dir "./Tracks/16-whatever/Songs"

# Import track 15
yarn import \
  --notion-url "https://notion.so/track-15" \
  --songs-dir "./Tracks/15-another-one/Songs"

# View your growing library
yarn stats:songs
```

### Check System Status
```bash
# Quick overview
yarn stats

# Detailed song info
yarn stats:songs

# Track overview
yarn stats:tracks

# Version check
yarn version
```

---

## 🔧 Troubleshooting

### "Command not found: yarn"
Install yarn first:
```bash
npm install -g yarn
```

### "venv/bin/activate: No such file or directory"
Create the virtual environment first:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### "Module not found" errors
Make sure dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Notion API authentication failed"
1. Check `.env` file exists and has `NOTION_API_TOKEN`
2. Get token from: https://www.notion.so/my-integrations
3. Make sure Notion integration has access to your pages

---

## 💡 Tips

### Combine Commands
```bash
# Import and view stats in one go
yarn import --notion-url "URL" --songs-dir "PATH" && yarn stats
```

### Use Shell Aliases
Add to your `.bashrc` or `.zshrc`:
```bash
alias lofi-import="yarn import"
alias lofi-stats="yarn stats"
alias lofi-help="yarn help"
```

Then use:
```bash
lofi-import --notion-url "URL" --songs-dir "PATH"
lofi-stats
```

### Tab Completion
Most shells support tab completion for long paths:
```bash
yarn import \
  --notion-url "URL" \
  --songs-dir "./Tracks/17-ana[TAB]"
  # Expands to: ./Tracks/17-analogue-study-console/
```

---

## 📋 Quick Reference Card

| Command | What It Does | Status |
|---------|-------------|--------|
| `yarn init-db` | Initialize database | ✅ Working |
| `yarn import` | Import songs from track | ✅ Working |
| `yarn import:force` | Re-import with fresh analysis | ✅ Working |
| `yarn stats` | View song statistics | ✅ Working |
| `yarn stats:songs` | View song statistics | ✅ Working |
| `yarn stats:tracks` | View track statistics | ✅ Working |
| `yarn query` | Find matching songs | 🚧 Phase 4 |
| `yarn gaps` | Show songs to generate | 🚧 Phase 4 |
| `yarn scaffold` | Create track folder | 🚧 Phase 5 |
| `yarn duration` | Calculate duration | 🚧 Phase 5 |
| `yarn prepare` | Prepare for rendering | 🚧 Phase 5 |
| `yarn post-render` | Import after rendering | 🚧 Phase 5 |
| `yarn publish` | Mark as published | 🚧 Phase 6 |
| `yarn help` | Show CLI help | ✅ Working |
| `yarn version` | Show version | ✅ Working |

---

## 🎯 Next Steps

1. **Build your library** - Import 3-5 existing tracks
2. **Check statistics** - See what you have
3. **Wait for Phase 4** - Then start querying for matches!

After Phase 4 is complete, you'll be able to use `yarn query` to find matching songs for new tracks.
