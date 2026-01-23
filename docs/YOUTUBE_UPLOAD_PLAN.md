# Comprehensive Plan: Auto YouTube Upload System

## Overview

A complete YouTube upload automation system that handles video uploads, metadata, scheduling, and advanced features like end screens and pinned comments.

---

## Phase 1: YouTube API Setup & Authentication

### 1.1 Prerequisites
- **YouTube Data API v3** credentials from Google Cloud Console
- OAuth 2.0 client ID and secret
- Required scopes:
  - `https://www.googleapis.com/auth/youtube.upload`
  - `https://www.googleapis.com/auth/youtube` (for playlists, comments, etc.)
  - `https://www.googleapis.com/auth/youtube.force-ssl`

### 1.2 Configuration Files
```yaml
# config/settings.yaml
youtube:
  client_secrets_file: "./config/client_secrets.json"
  credentials_file: "./config/youtube_credentials.json"
  channel_id: "YOUR_CHANNEL_ID"
  default_category: "10"  # Music
  default_privacy: "private"  # private/public/unlisted
```

### 1.3 Authentication Flow
- First-time setup: OAuth flow to get refresh token
- Store credentials securely
- Auto-refresh tokens when expired
- Command: `yarn youtube-auth` to authenticate

---

## Phase 2: Core Upload Functionality

### 2.1 Upload Command Structure
```bash
yarn youtube-upload --track 37 [--dry-run] [--schedule]
```

### 2.2 Workflow Steps

#### Step 1: Pre-Upload Validation
1. **Find latest render folder**
   - Check `Rendered/{track}/output_{timestamp}/`
   - Get most recent by timestamp
   - Prompt user if multiple renders exist

2. **Validate video file**
   - Look for `.mp4` file
   - Check filename matches Notion `output_filename` field
   - If mismatch: offer to rename or abort
   - Verify file size < 256GB (YouTube limit)

3. **Validate required assets**
   - Video file exists ✓
   - Description file exists ✓
   - Thumbnail image exists (from Image folder) ✓
   - Track metadata in database ✓

#### Step 2: Metadata Preparation
1. **Load track from database**
   - Get title, output_filename, notion_url
   - Parse Notion doc for latest data

2. **Title**
   - Use `title` field from Notion Track Overview table
   - Max 100 characters (YouTube limit)
   - Format: Already formatted in Notion

3. **Description**
   - Load from `youtube-description.txt` in render folder
   - Parse sections:
     - Main description text
     - "Chapters" section
     - Visible hashtags at the end
   - Max 5000 characters (YouTube limit)

4. **Tags (Hidden/Searchable)**
   - Parse from Notion "Hidden Tags" section
   - Split by comma
   - Max 500 characters total (YouTube limit)
   - Max 30 tags per video
   - Individual tag max 30 characters

5. **Thumbnail**
   - Look in `Rendered/{track}/output_{timestamp}/Image/`
   - Priority order:
     1. `thumbnail.jpg/png` (if exists)
     2. `{track}.jpg/png`
     3. First image file found
   - Validate:
     - Format: JPG, PNG, GIF, BMP
     - Size: < 2MB
     - Resolution: 1280x720 (recommended)

6. **Category**
   - Use category ID `10` (Music)
   - Or make configurable in Notion

#### Step 3: Scheduling
1. **Parse schedule from Notion**
   - Field: "Upload Schedule" from Track Overview
   - Format: "Wednesday @ 10 AM ET"
   - Convert to ISO 8601 timestamp
   - Handle timezones (ET → UTC conversion)

2. **Privacy Settings**
   - If scheduled: set to `private` initially
   - YouTube auto-publishes at scheduled time
   - Or set to `public` if no schedule

#### Step 4: Upload Process
1. **Resumable upload** (for large files)
   - Chunk size: 10MB
   - Progress bar with percentage
   - Handle network interruptions
   - Resume from last chunk on failure

2. **Set basic metadata** (during upload)
   - Title
   - Description
   - Tags
   - Category
   - Privacy status
   - Publish time (if scheduled)

3. **Post-upload operations**
   - Set thumbnail
   - Add to playlists
   - Set end screens
   - Add cards
   - Post pinned comment

---

## Phase 3: Playlist Management

### 3.1 Playlist Configuration
```yaml
# config/youtube_playlists.yaml
playlists:
  - id: "PLxxxxxxxxxxxxxxxx"
    name: "3-Hour LoFi Mixes"
    description: "All 3-hour focus tracks"
    match_criteria:
      duration_target: 180

  - id: "PLyyyyyyyyyyyyyyyy"
    name: "Synthwave Collection"
    description: "Synthwave and retrowave tracks"
    match_criteria:
      tags_include: ["synthwave", "retrowave"]

  - id: "PLzzzzzzzzzzzzzzzz"
    name: "All Uploads"
    description: "Complete channel uploads"
    match_criteria: {}  # Match all
```

### 3.2 Auto-Add Logic
- Check each playlist's `match_criteria`
- Add video to matching playlists
- Position: end of playlist (or configurable)
- Log which playlists video was added to

---

## Phase 4: Advanced Features

### 4.1 End Screens
```python
end_screen_config = {
    "duration": 20,  # Last 20 seconds
    "elements": [
        {
            "type": "video",
            "position": "topLeft",
            "video_id": "PREVIOUS_VIDEO_ID",  # Most recent upload
            "start_ms": 0,  # 20 seconds before end
            "end_ms": 20000,
            "width": 0.3,
            "left": 0.05,
            "top": 0.45
        },
        {
            "type": "playlist",
            "position": "topRight",
            "playlist_id": "MAIN_PLAYLIST_ID",
            "start_ms": 0,
            "end_ms": 20000,
            "width": 0.3,
            "left": 0.65,
            "top": 0.45
        },
        {
            "type": "subscribe",
            "position": "bottomRight",
            "start_ms": 0,
            "end_ms": 20000,
        }
    ]
}
```

**Implementation:**
- Store last video ID in database after each upload
- Use YouTube API `videos.insert` with `endScreen` parameter
- Template-based: same layout for all videos
- Dynamic: previous video changes each time

### 4.2 Cards (Video Annotations)
```python
card_config = {
    "position_ms": 600000,  # 10 minutes before end (in milliseconds from start)
    "type": "video",
    "video_id": "PREVIOUS_VIDEO_ID",
    "message": "Check out the previous track →"
}
```

**Implementation:**
- Calculate card timestamp: `total_duration - 600` (10 min before end)
- Use YouTube API `cards.insert`
- Add card pointing to previous video

### 4.3 Pinned Comment
```python
comment_text = """
🎵 Listen to the previous track: [PREVIOUS_TITLE]
👉 [PREVIOUS_VIDEO_URL]

Full playlist: [PLAYLIST_URL]
"""
```

**Implementation:**
- Use YouTube API `commentThreads.insert`
- Post comment after upload
- Pin using `comments.setModerationStatus` with `heldForReview=false`
- Requires `youtube.force-ssl` scope

---

## Phase 5: Database Schema Updates

### 5.1 New Fields for Tracks Table
```sql
ALTER TABLE tracks ADD COLUMN youtube_video_id TEXT;
ALTER TABLE tracks ADD COLUMN youtube_upload_date TEXT;
ALTER TABLE tracks ADD COLUMN youtube_scheduled_date TEXT;
ALTER TABLE tracks ADD COLUMN youtube_url TEXT;
ALTER TABLE tracks ADD COLUMN youtube_playlist_ids TEXT;  -- JSON array
```

### 5.2 New Table: Upload History
```sql
CREATE TABLE youtube_uploads (
    id TEXT PRIMARY KEY,
    track_number INTEGER,
    video_id TEXT NOT NULL,
    video_url TEXT NOT NULL,
    upload_date TEXT NOT NULL,
    scheduled_date TEXT,
    title TEXT,
    status TEXT,  -- uploaded, scheduled, published, failed
    error_message TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## Phase 6: Implementation Plan

### 6.1 File Structure
```
src/
├── youtube/
│   ├── __init__.py
│   ├── auth.py              # OAuth authentication
│   ├── uploader.py          # Core upload logic
│   ├── metadata.py          # Title, description, tags parsing
│   ├── thumbnail.py         # Thumbnail handling
│   ├── scheduler.py         # Parse schedule from Notion
│   ├── playlists.py         # Playlist management
│   ├── end_screens.py       # End screen configuration
│   ├── cards.py             # Card management
│   └── comments.py          # Pinned comment posting

config/
├── youtube_playlists.yaml   # Playlist configuration
└── client_secrets.json      # OAuth credentials (gitignored)
```

### 6.2 CLI Commands

#### 6.2.1 Authentication
```bash
# Initial setup
yarn youtube-auth

# Test authentication
yarn youtube-auth --test

# Revoke and re-authenticate
yarn youtube-auth --reset
```

#### 6.2.2 Upload
```bash
# Basic upload
yarn youtube-upload --track 37

# Dry run (validate only, no upload)
yarn youtube-upload --track 37 --dry-run

# Skip scheduling (upload immediately as public)
yarn youtube-upload --track 37 --no-schedule

# Force schedule date override
yarn youtube-upload --track 37 --schedule "2026-01-25T10:00:00-05:00"

# Skip playlists
yarn youtube-upload --track 37 --no-playlists

# Upload without end screens/cards
yarn youtube-upload --track 37 --no-extras
```

#### 6.2.3 Playlist Management
```bash
# List all playlists
yarn youtube-playlists list

# Add video to playlist manually
yarn youtube-playlists add --video-id "abc123" --playlist-id "PLxxx"

# Remove from playlist
yarn youtube-playlists remove --video-id "abc123" --playlist-id "PLxxx"
```

#### 6.2.4 Update Existing Videos
```bash
# Update description only
yarn youtube-update --track 37 --description

# Update thumbnail
yarn youtube-update --track 37 --thumbnail

# Update end screens
yarn youtube-update --track 37 --end-screens
```

---

## Phase 7: Error Handling & Recovery

### 7.1 Common Errors
- **Quota exceeded**: YouTube API has daily quota limits
  - Handle: Log error, schedule retry next day
  - Alert user via console

- **Upload interrupted**: Network failure mid-upload
  - Handle: Resume from last chunk
  - Save progress state

- **Invalid metadata**: Title/description too long
  - Handle: Truncate with "..." and warn user
  - Provide fix suggestions

- **Authentication expired**: Refresh token invalid
  - Handle: Prompt for re-authentication
  - Clear stored credentials

### 7.2 Validation Safeguards
- Filename check: Must match Notion `output_filename`
- Title length: Max 100 chars
- Description: Max 5000 chars
- Tags: Max 500 chars total, max 30 tags
- Thumbnail: Validate format and size
- Schedule date: Must be in future

---

## Phase 8: Dependencies

### 8.1 Python Packages
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2
pip install google-api-python-client
pip install python-dateutil  # For timezone handling
```

### 8.2 Update requirements.txt
```txt
google-auth>=2.16.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.1.0
google-api-python-client>=2.80.0
python-dateutil>=2.8.2
```

---

## Phase 9: Testing Strategy

### 9.1 Dry Run Mode
- Validate all inputs
- Show what would be uploaded
- Don't actually upload
- Check API authentication

### 9.2 Test Video Upload
- Upload to test/private first
- Verify all metadata
- Check thumbnail rendering
- Confirm playlist additions
- Test end screens/cards

### 9.3 Integration Tests
```bash
# Test full workflow
yarn youtube-upload --track 999 --dry-run

# Test authentication
yarn youtube-auth --test

# Test playlist matching
yarn youtube-playlists test --track 37
```

---

## Phase 10: Documentation Updates

### 10.1 New CLI Reference Section
Add to `docs/CLI_REFERENCE.md`:
- `youtube-auth` - Authentication setup
- `youtube-upload` - Upload video
- `youtube-playlists` - Manage playlists
- `youtube-update` - Update existing videos

### 10.2 Setup Guide
Create `docs/YOUTUBE_SETUP.md`:
1. Google Cloud Console setup
2. Enable YouTube Data API v3
3. Create OAuth credentials
4. Initial authentication
5. Playlist configuration
6. First upload walkthrough

---

## Implementation Priority

### **Phase 1: MVP (Minimum Viable Product)**
1. ✅ YouTube authentication (`youtube-auth`)
2. ✅ Basic upload (`youtube-upload`)
3. ✅ Title, description, tags
4. ✅ Thumbnail upload
5. ✅ Basic error handling

### **Phase 2: Scheduling & Playlists**
6. ✅ Schedule parsing from Notion
7. ✅ Playlist auto-add
8. ✅ Database updates

### **Phase 3: Advanced Features**
9. ✅ End screens
10. ✅ Cards (10 min before end)
11. ✅ Pinned comments

### **Phase 4: Polish**
12. ✅ Comprehensive error handling
13. ✅ Update existing videos command
14. ✅ Full documentation

---

## Typical Workflow

```bash
# 1. First time setup (once)
yarn youtube-auth

# 2. Normal upload workflow
yarn render --track 37 -d 3
# ↓ Description auto-generated in render folder

yarn youtube-upload --track 37
# ↓ Validates everything, prompts for confirmation
# ↓ Uploads video with all metadata
# ↓ Schedules based on Notion
# ↓ Adds to playlists
# ↓ Sets end screens/cards
# ↓ Posts pinned comment

# 3. Check status
yarn stats tracks  # Shows YouTube video ID and URL
```

---

## Notes & Considerations

### API Quotas
- YouTube API has 10,000 units/day default quota
- Video upload: ~1600 units
- You can upload ~6 videos/day within quota
- Request quota increase from Google if needed

### Filename Validation
- Compare render output filename to Notion `output_filename`
- If mismatch: show diff and offer to rename
- Prevent wrong video being uploaded

### Hidden Tags via API
- YouTube API **does support tags**
- Use `snippet.tags` field in upload request
- These are searchable but not visible to users
- Perfect for your "Hidden Tags" section from Notion

### Previous Video Linking
- Store `youtube_video_id` after each upload
- Query database for most recent video
- Use for end screen, card, and pinned comment

---

## Next Steps

Ready to implement! The recommended approach:

1. **Start with Phase 1 (MVP)**: Get basic uploads working
2. **Add Phase 2**: Scheduling and playlists
3. **Enhance with Phase 3**: End screens, cards, comments
4. **Polish with Phase 4**: Error handling and updates

Each phase builds on the previous one, allowing for incremental testing and deployment.
