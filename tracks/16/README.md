# Track 16

## Status: In Progress

### Created: 2025-11-19 21:54

---

## Workflow

1. **Select songs from bank** (optional):
   ```bash
   # By count (e.g., 5 songs)
   ./venv/bin/python3 agent/select_bank_songs.py --track 16 --count 5 --flow-id 04

   # By duration (e.g., 30 minutes)
   ./venv/bin/python3 agent/select_bank_songs.py --track 16 --duration 30 --flow-id 04

   # Execute the selection
   ./venv/bin/python3 agent/select_bank_songs.py --track 16 --execute
   ```

2. **Add new songs manually**:
   - Generate songs in Suno
   - Download to ~/Downloads/
   - Move to half_1/ or half_2/:
     ```bash
     mv ~/Downloads/new_song*.mp3 /Users/patricklake/Dev/personal/static-dreamwaves/tracks/16/half_1/
     ```

3. **Add video and image**:
   ```bash
   cp ~/path/to/background.mp4 /Users/patricklake/Dev/personal/static-dreamwaves/tracks/16/video/16.mp4
   cp ~/path/to/cover.jpg /Users/patricklake/Dev/personal/static-dreamwaves/tracks/16/image/16.jpg
   ```

4. **Build track** (auto A_/B_ prefixing):
   ```bash
   ./venv/bin/python3 agent/build_track.py --track 16 --duration 3
   ```

5. **Add new songs to bank** (after successful render):
   ```bash
   ./venv/bin/python3 agent/add_to_bank.py --track 16 --flow-id 04
   ```

---

## Folder Structure

- `half_1/` - Songs for first half (A_ prefix applied during render)
- `half_2/` - Songs for second half (B_ prefix applied during render)
- `video/` - Background video (16.mp4)
- `image/` - Cover art (16.jpg)
- `metadata.json` - Track metadata
- `bank_selection.json` - Songs selected from bank (auto-generated)

---

## Notes

Add your notes here about theme, mood, track flow references, etc.
