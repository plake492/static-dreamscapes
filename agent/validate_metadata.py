#!/usr/bin/env python3
"""
Static Dreamscapes - Metadata Validation Script
------------------------------------------------
Validates metadata files against actual audio files in arc_library.
Checks for:
- Orphaned entries (in metadata but file doesn't exist)
- Missing entries (file exists but not in metadata)
- Inconsistent phase assignments
- Duplicate entries

Usage:
    python3 agent/validate_metadata.py
    python3 agent/validate_metadata.py --fix-orphans  # Remove orphaned entries
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
ARC_LIBRARY = PROJECT_ROOT / "arc_library"
METADATA_DIR = PROJECT_ROOT / "metadata"

def load_phase_metadata() -> Dict[str, dict]:
    """Load all phase JSON files."""
    phase_data = {}
    for phase_file in METADATA_DIR.glob("phase_*.json"):
        try:
            data = json.loads(phase_file.read_text())
            phase_name = phase_file.stem  # e.g., "phase_1_calm_intro"
            phase_data[phase_name] = data
        except Exception as e:
            print(f"⚠️  Error loading {phase_file.name}: {e}")
    return phase_data

def get_actual_mp3_files() -> Dict[str, Path]:
    """Get all MP3 files currently in arc_library."""
    mp3_files = {}
    for mp3_path in ARC_LIBRARY.rglob("*.mp3"):
        mp3_files[mp3_path.name] = mp3_path
    return mp3_files

def get_metadata_entries() -> Dict[str, Tuple[str, dict]]:
    """Get all entries from metadata files."""
    entries = {}
    phase_data = load_phase_metadata()

    for phase_name, data in phase_data.items():
        for song in data.get("songs", []):
            filename = song.get("filename")
            if filename:
                if filename in entries:
                    print(f"⚠️  Duplicate entry found: {filename}")
                entries[filename] = (phase_name, song)

    return entries

def validate_metadata(fix_orphans: bool = False):
    """
    Validate metadata against actual files.

    Args:
        fix_orphans: If True, remove orphaned entries from metadata
    """
    print("=" * 60)
    print("METADATA VALIDATION")
    print("=" * 60)

    # Load data
    print("\n📂 Loading metadata and scanning files...")
    phase_data = load_phase_metadata()
    actual_files = get_actual_mp3_files()
    metadata_entries = get_metadata_entries()

    print(f"   Phase files loaded: {len(phase_data)}")
    print(f"   MP3 files found: {len(actual_files)}")
    print(f"   Metadata entries: {len(metadata_entries)}")

    # Check for orphaned entries
    print("\n🔍 Checking for orphaned entries (in metadata but file missing)...")
    orphans = []
    for filename, (phase_name, song) in metadata_entries.items():
        if filename not in actual_files:
            orphans.append((filename, phase_name))
            print(f"   ❌ {filename} (in {phase_name})")

    if not orphans:
        print("   ✅ No orphaned entries found")
    else:
        print(f"\n   Found {len(orphans)} orphaned entries")

        if fix_orphans:
            print("\n🔧 Removing orphaned entries...")
            for filename, phase_name in orphans:
                phase_file = METADATA_DIR / f"{phase_name}.json"
                data = json.loads(phase_file.read_text())
                data["songs"] = [s for s in data["songs"] if s.get("filename") != filename]
                phase_file.write_text(json.dumps(data, indent=2))
                print(f"   ✓ Removed {filename} from {phase_name}")

    # Check for missing entries
    print("\n🔍 Checking for missing entries (file exists but not in metadata)...")
    missing = []
    for filename in actual_files.keys():
        if filename not in metadata_entries:
            missing.append(filename)
            print(f"   ⚠️  {filename}")

    if not missing:
        print("   ✅ No missing entries found")
    else:
        print(f"\n   Found {len(missing)} files not in metadata")
        print("   💡 Run analyze_audio.py to add them")

    # Check for phase mismatches
    print("\n🔍 Checking for phase assignment mismatches...")
    mismatches = []
    for filename, file_path in actual_files.items():
        if filename in metadata_entries:
            metadata_phase, song = metadata_entries[filename]

            # Determine actual phase from file path
            phase_folder = None
            for part in file_path.parts:
                if part.startswith("phase_"):
                    phase_folder = part
                    break

            if phase_folder and phase_folder != metadata_phase:
                mismatches.append((filename, phase_folder, metadata_phase))
                print(f"   ⚠️  {filename}: file in {phase_folder}, metadata in {metadata_phase}")

    if not mismatches:
        print("   ✅ No phase mismatches found")
    else:
        print(f"\n   Found {len(mismatches)} phase mismatches")

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total MP3 files:       {len(actual_files)}")
    print(f"Total metadata entries: {len(metadata_entries)}")
    print(f"Orphaned entries:      {len(orphans)}")
    print(f"Missing entries:       {len(missing)}")
    print(f"Phase mismatches:      {len(mismatches)}")

    if orphans or missing or mismatches:
        print("\n❌ Validation failed - issues found")
        return False
    else:
        print("\n✅ Validation passed - metadata is consistent")
        return True

def main():
    parser = argparse.ArgumentParser(
        description="Validate metadata files against arc_library audio files"
    )
    parser.add_argument(
        '--fix-orphans',
        action='store_true',
        help='Remove orphaned entries from metadata files'
    )

    args = parser.parse_args()

    success = validate_metadata(fix_orphans=args.fix_orphans)
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
