# Improvements Backlog

This document tracks planned and implemented improvements to the static-dreamwaves workflow.

## Implementation Status

- ✅ **#1: Fix Auto File Naming on Render** - Completed
- ✅ **#2: Query Output Default Location** - Completed
- ✅ **#3: Illegal Phrase Detection** - Completed
- ⏳ **#4: Fix Prerender Script** - Pending
- ⏳ **#5: Standardize Track Parameter** - Pending
- ⏳ **#6: Auto-Resolve Track Paths** - Pending

---

## 1. Fix Auto File Naming on Render ✅ COMPLETED

**Issue**: When rendering tracks, the output filename is not automatically generated based on track metadata (track number, title, etc.).

**Improvement**: Automatically generate output filenames for rendered tracks using a consistent naming convention based on track metadata.

**Current Behavior**:
```bash
# May require manual output filename specification
yarn render --track 25 --output "some-manual-name.mp4"

# Or outputs to generic/unclear filename
yarn render --track 25
# Outputs to: output.mp4 or render.mp4
```

**Desired Behavior**:
```bash
# Auto-generates filename from track metadata
yarn render --track 25
# Outputs to: ./output/Track-25-Midnight-Neon-CRT-Desk-3HR-LoFi-Synthwave-Mix.mp4

# Or simplified format:
# Outputs to: ./output/track-25-midnight-neon-crt-desk.mp4

# Still allow manual override when needed
yarn render --track 25 --output custom-name.mp4
```

**Filename Convention Options**:
```bash
# Option A: Full title (sanitized)
Track-25-Midnight-Neon-CRT-Desk-3HR-LoFi-Synthwave-Mix.mp4

# Option B: Simplified (track number + shortened title)
track-25-midnight-neon-crt-desk.mp4

# Option C: Track number + upload date
track-25-2025-12-20.mp4

# Option D: Just track number (simplest)
track-25.mp4
```

**Implementation Plan**:
1. Fetch track title from Notion document or database
2. Sanitize title for filesystem (remove special chars, spaces to hyphens)
3. Apply character length limit if needed (e.g., 80 chars max)
4. Generate filename: `track-{number}-{sanitized-title}.mp4`
5. Save to `./output/` directory by default
6. Allow `--output` override for custom names

**Files to Modify**:
- `src/cli/main.py` - Update render command to auto-generate filename
- `src/render/filename_generator.py` (NEW) - Create filename sanitization utility
- `TRACK_CREATION_GUIDE.md` - Update render examples with new behavior

### Implementation Summary

**Completed:** 2025-12-20

**Changes Made:**
1. ✅ Created `src/render/filename_generator.py` with utilities:
   - `sanitize_for_filename()` - Removes emojis, special chars, converts to lowercase kebab-case
   - `generate_track_filename()` - Generates filename from track number + title
   - `get_output_path()` - Returns full output path with directory creation

2. ✅ Updated `src/cli/main.py` render command:
   - Added `--output` parameter for custom paths
   - Changed output directory from `Rendered/{track}/output_{timestamp}/` to `./Rendered/`
   - Integrated filename generator for auto-naming
   - Uses `output_filename` field from Notion document
   - Falls back to `track-{number}-{sanitized-title}.mp4` if no Notion filename

3. ✅ Updated `TRACK_CREATION_GUIDE.md`:
   - Updated test render output location examples
   - Updated full render output location examples
   - Added `--output` parameter documentation
   - Added custom output path examples

**Result:**
```bash
# Before:
yarn render --track 25
# Output: Rendered/25/output_20251220_153045/output.mp4

# After:
yarn render --track 25
# Output: Rendered/midnight-neon-crt-desk-3hr-lofi-synthwave-night-coding.mp4
# (Uses "Filename" field from Notion document)

# With custom path:
yarn render --track 25 --output ./my-videos/custom-name.mp4
```

---

## 2. Query Output Default Location ✅ COMPLETED

**Issue**: Query results are saved to the project root by default, which clutters the directory.

**Improvement**: Make `yarn query` default to saving output files in `./output/` directory.

**Current Behavior**:
```bash
yarn query --notion-url "..." --output track-25-matches.json
# Saves to: /Users/patricklake/Desktop/static-dreamwaves/track-25-matches.json
```

**Desired Behavior**:
```bash
yarn query --notion-url "..." --output track-25-matches.json
# Should save to: /Users/patricklake/Desktop/static-dreamwaves/output/track-25-matches.json

# Or with explicit output dir:
yarn query --notion-url "..." --output output/track-25-matches.json
```

**Files to Modify**:
- `src/cli/main.py` - Update query command default output path

### Implementation Summary

**Completed:** 2025-12-21

**Changes Made:**
1. ✅ Added `--track` parameter to query command
   - Auto-generates output filename: `./output/track-{number}-matches.json`
   - Makes --output parameter optional

2. ✅ Updated default output behavior:
   - With `--track`: saves to `./output/track-{number}-matches.json`
   - Without `--track`: saves to `./output/query-results.json`
   - Custom `--output` still works and overrides defaults
   - Auto-creates output directory if it doesn't exist

3. ✅ Consistent with import-songs and render commands:
   - All commands now support `--track` parameter
   - All commands auto-resolve paths from track number
   - All commands allow explicit path overrides

**Result:**
```bash
# Before:
yarn query --notion-url "..." --output track-25-matches.json
# Output: ./track-25-matches.json (clutters root)

# After (simplified with --track):
yarn query --track 25 --notion-url "..."
# Output: ./output/track-25-matches.json

# After (without --track):
yarn query --notion-url "..."
# Output: ./output/query-results.json

# Custom output still works:
yarn query --track 25 --notion-url "..." --output ./custom/my-query.json
```

---

## 3. Illegal Phrase Detection After Import ✅ COMPLETED

**Issue**: When tracks are imported with forbidden technical phrases (e.g., "slow attack and long release", "low-pass filtered"), there's no immediate feedback. The issue only becomes apparent during query when matches are poor.

**Improvement**: After importing songs, scan all prompts for illegal/technical phrases and report them to the user.

**Desired Behavior**:
```bash
yarn import-songs --notion-url "..." --songs-dir "..."

✅ Imported 150 songs

⚠️  WARNING: Found forbidden technical phrases in prompts:
  - Prompt 1.1: "slow attack and long release"
  - Prompt 2.3: "low-pass filtered warmth"
  - Prompt 3.8: "sidechained pad chords"

📖 See PROMPT_CRAFTING_GUIDE.md for approved evocative vocabulary
```

**Implementation Plan**:
1. Create a list of forbidden technical terms (reference: PROMPT_CRAFTING_GUIDE.md)
2. After import completes, scan all newly imported song prompts
3. Report any matches with prompt number and location
4. Provide link to PROMPT_CRAFTING_GUIDE.md

**Files to Modify**:
- `src/cli/main.py` - Add post-import validation step
- `src/ingest/prompt_validator.py` (NEW) - Create validator with forbidden terms list

### Implementation Summary

**Completed:** 2025-12-21

**Changes Made:**
1. ✅ Created `src/ingest/prompt_validator.py` with:
   - `FORBIDDEN_PHRASES` - List of 40+ forbidden technical terms from PROMPT_CRAFTING_GUIDE.md
   - `FORBIDDEN_PATTERNS` - Regex patterns to catch variations (e.g., "no percussion", "zero drums")
   - `check_prompt_for_violations()` - Scans single prompt for forbidden phrases
   - `validate_track_prompts()` - Validates all prompts for a track from database
   - `format_violation_report()` - Formats violations as Rich-styled warning table
   - `PromptViolation` dataclass - Structured violation data

2. ✅ Updated `src/cli/main.py` import-songs command:
   - Added validator call after successful import (line 139-145)
   - Displays violations with arc/prompt location
   - Shows summary with violation counts
   - Links to PROMPT_CRAFTING_GUIDE.md

3. ✅ Forbidden phrase categories detected:
   - Production/mixing terms: "slow attack and long release", "low-pass filtered", "sidechain"
   - Negative phrasing: "no percussion", "no drums", "beatless", "zero rhythmic"
   - Technical density: "event density", "extremely low event density"
   - Overly specific: "chord cycling every 8 bars", "vocal pads in upper register"

**Result:**
```bash
# Before:
yarn import-songs --track 10 --notion-url "..."
✅ Import completed successfully!
Songs imported: 45
# (No feedback on prompt quality)

# After:
yarn import-songs --track 10 --notion-url "..."
✅ Import completed successfully!
Songs imported: 45

⚠️  WARNING: Found forbidden technical phrases in prompts:

  • Arc 1 - Prompt 1: "slow attack and long release", "slow attack", "long release", "no drums"
  • Arc 1 - Prompt 2: "no rhythm"
  • Arc 2 - Prompt 5: "sidechain", "sidechained"
  • Arc 4 - Prompt 12: "beatless"
  • Arc 4 - Prompt 13: "long release"

📖 See PROMPT_CRAFTING_GUIDE.md for approved evocative vocabulary

Summary:
  • 5 prompt(s) with violations
  • 8 unique forbidden phrase(s)
```

**Benefits:**
- Immediate feedback on prompt quality during import
- Clear identification of which prompts need revision
- Links to approved vocabulary guide
- Helps maintain semantic consistency across track library
- Prevents poor query matches due to technical language

---

## 4. Fix Prerender Script

**Issue**: The prerender script referenced in TRACK_CREATION_GUIDE.md does not work as documented.

**Current Documentation** (from TRACK_CREATION_GUIDE.md):
```bash
yarn prepare-render --track 25 --playlist track-25-matches.json --duration 180
```

**Problem**:
- Script may not exist
- Parameters may not match documentation
- Functionality may not work as expected

**Investigation Needed**:
1. Check if `yarn prepare-render` command exists
2. Verify what it's supposed to do (copy matched songs to track folder?)
3. Test if it actually works
4. Update documentation or fix script to match

**Files to Check**:
- `package.json` - Check if prepare-render script exists
- `scripts/prepare_render.py` or similar - Find the actual script
- `TRACK_CREATION_GUIDE.md` - Update documentation if needed

---

## 5. Standardize Track Parameter Naming

**Issue**: Different scripts use inconsistent parameter names for specifying tracks: `--track-number`, `--track-id`, `--track`

**Improvement**: Standardize all scripts to use `--track` for consistency.

**Current Inconsistencies**:
```bash
# Some scripts use:
yarn import-songs --track-number 25

# Others might use:
yarn query --track-id 25

# Others might use:
yarn something --track 25
```

**Desired Standard**:
```bash
# All scripts should use:
--track 25
```

**Files to Audit and Modify**:
- `src/cli/main.py` - All CLI commands
- `scripts/*.py` - All Python scripts
- `package.json` - Update command documentation
- `AGENT_CONTEXT.md` - Update usage examples
- `TRACK_CREATION_GUIDE.md` - Update workflow documentation

**Migration Strategy**:
1. Audit all scripts to find current parameter names
2. Update argument parsers to use `--track` (keep old names as deprecated aliases for backwards compatibility)
3. Add deprecation warnings for old parameter names
4. Update all documentation
5. After one release cycle, remove deprecated aliases

---

## 6. Auto-Resolve Track Paths from Track Number

**Issue**: Many commands require full file paths or output paths that reference track-specific files (e.g., `./output/track-25-matches.json`, `./Tracks/25/Songs`). This is verbose and error-prone.

**Improvement**: All commands should accept just `--track <number>` and automatically resolve all track-related paths based on conventions.

**Current Verbose Behavior**:
```bash
# Query requires full output path
yarn query --notion-url "..." --output ./output/track-25-matches.json

# Import requires full songs directory path
yarn import-songs --notion-url "..." --songs-dir ./Tracks/25/Songs

# Duration check might require full path
yarn track-duration --songs-dir ./Tracks/25/Songs

# Prepare render requires full playlist path
yarn prepare-render --track 25 --playlist ./output/track-25-matches.json
```

**Desired Simplified Behavior**:
```bash
# Query auto-creates ./output/track-25-matches.json
yarn query --track 25 --notion-url "..."

# Import auto-resolves to ./Tracks/25/Songs
yarn import-songs --track 25 --notion-url "..."

# Duration check auto-resolves to ./Tracks/25/Songs
yarn track-duration --track 25

# Prepare render auto-finds ./output/track-25-matches.json
yarn prepare-render --track 25

# Still allow overrides when needed
yarn query --track 25 --notion-url "..." --output custom-name.json
```

**Path Resolution Conventions**:
- `--track 25` → Songs directory: `./Tracks/25/Songs/`
- `--track 25` → Query output: `./output/track-25-matches.json`
- `--track 25` → Notion cache: `./data/cache/notion_docs/<page-id>.md`
- `--track 25` → Render output: `./output/track-25-final.mp4`

**Benefits**:
1. **Less typing** - No need to specify full paths every time
2. **Less error-prone** - Can't typo the path structure
3. **Convention over configuration** - Standard paths are automatic
4. **Flexibility preserved** - Can still override with explicit paths when needed

**Implementation Plan**:
1. Create path resolver utility that takes track number and returns standard paths
2. Update all CLI commands to:
   - Accept `--track <number>` parameter
   - Auto-resolve paths using conventions
   - Make explicit path parameters optional (for overrides)
3. Maintain backwards compatibility by keeping explicit path parameters working

**Files to Modify**:
- `src/core/path_resolver.py` (NEW) - Create path resolution utility
- `src/cli/main.py` - Update all commands (query, import-songs, etc.)
- `scripts/*.py` - Update standalone scripts to use path resolver
- All documentation files - Update examples to show simplified usage

**Example Path Resolver**:
```python
class TrackPathResolver:
    def __init__(self, track_number: int, base_dir: Path = Path(".")):
        self.track_number = track_number
        self.base_dir = base_dir

    def songs_dir(self) -> Path:
        return self.base_dir / "Tracks" / str(self.track_number) / "Songs"

    def query_output(self) -> Path:
        return self.base_dir / "output" / f"track-{self.track_number}-matches.json"

    def render_output(self) -> Path:
        return self.base_dir / "output" / f"track-{self.track_number}-final.mp4"
```

---

## Priority

Not yet prioritized - this is a backlog of improvements to be scheduled later.

---

**Last Updated**: 2025-12-21
