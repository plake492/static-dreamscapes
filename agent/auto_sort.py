#!/usr/bin/env python3
"""
Static Dreamscapes - Auto Sort Tracks by Phase
-----------------------------------------------
Analyzes unsorted tracks and automatically moves them to the correct phase folder
based on BPM, brightness, and energy characteristics.

Usage:
    python3 agent/auto_sort.py --input ./unsorted_tracks
    python3 agent/auto_sort.py --input ./unsorted_tracks --dry-run
    python3 agent/auto_sort.py --scan-downloads  # Scans ~/Downloads
"""

import os
import sys
import json
import shutil
import argparse
import librosa
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
ARC_LIBRARY = PROJECT_ROOT / "arc_library"
LOW_CONFIDENCE_DIR = ARC_LIBRARY / "low_confidence"

# Confidence threshold for automatic sorting
CONFIDENCE_THRESHOLD = 0.70  # 70%

# Phase definitions with criteria and subfolder logic
PHASE_CRITERIA = {
    "phase_1_calm_intro": {
        "name": "Calm Intro",
        "bpm_range": (65, 78),
        "brightness_range": (1000, 2200),
        "energy_range": (0.01, 0.08),
        "subfolders": {
            "ambient_warmth": {
                "criteria": "energy < 0.04",  # Very calm/quiet
                "description": "Very low energy, deep ambient"
            },
            "early_dawn": {
                "criteria": "brightness >= 1600",  # Brighter within phase
                "description": "Lighter, brighter calm tracks"
            },
            "nostalgic_haze": {
                "criteria": "default",  # Everything else
                "description": "Warm, nostalgic, medium calm"
            }
        },
        "keywords": ["calm", "ambient", "warm", "nostalgic", "slow", "intro", "dawn", "morning"]
    },
    "phase_2_flow_focus": {
        "name": "Flow Focus",
        "bpm_range": (78, 92),
        "brightness_range": (1800, 2800),
        "energy_range": (0.05, 0.12),
        "subfolders": {
            "midtempo_groove": {
                "criteria": "bpm >= 85",  # Faster within phase
                "description": "Higher tempo groove"
            },
            "analog_pulse": {
                "criteria": "energy >= 0.09",  # More energetic
                "description": "Higher energy, pulsing"
            },
            "deep_work": {
                "criteria": "default",  # Everything else
                "description": "Steady, focused, lower tempo"
            }
        },
        "keywords": ["focus", "steady", "work", "flow", "groove", "midtempo", "pulse"]
    },
    "phase_3_uplift_clarity": {
        "name": "Uplift Clarity",
        "bpm_range": (88, 110),
        "brightness_range": (2200, 4000),
        "energy_range": (0.08, 0.20),
        "subfolders": {
            "bright_pads": {
                "criteria": "brightness >= 2800",  # Very bright
                "description": "Brightest, most uplifting"
            },
            "optimistic_melodies": {
                "criteria": "bpm <= 98",  # Moderate tempo
                "description": "Melodic, optimistic, not too fast"
            },
            "creative_energy": {
                "criteria": "default",  # Everything else
                "description": "High energy, creative momentum"
            }
        },
        "keywords": ["bright", "uplift", "optimistic", "energetic", "clarity", "peak", "high"]
    },
    "phase_4_reflective_fade": {
        "name": "Reflective Fade",
        "bpm_range": (55, 72),
        "brightness_range": (800, 2000),
        "energy_range": (0.01, 0.07),
        "subfolders": {
            "tape_hiss": {
                "criteria": "brightness < 1400",  # Darkest/warmest
                "description": "Very dark, analog, tape-like"
            },
            "vapor_trails": {
                "criteria": "bpm >= 65",  # Slightly faster
                "description": "Vaporwave aesthetic, medium fade"
            },
            "closing_ambience": {
                "criteria": "default",  # Everything else
                "description": "Ambient closing, gentle fade"
            }
        },
        "keywords": ["fade", "slow", "reflective", "ending", "outro", "tape", "vapor", "closing"]
    }
}

def analyze_track(file_path: Path) -> Dict:
    """
    Analyze a single track and extract features.

    Returns:
        Dict with duration, bpm, brightness, energy, key, plus audio data (y, sr) for genre detection
    """
    print(f"  Analyzing: {file_path.name}")

    try:
        # Load audio
        y, sr = librosa.load(file_path, sr=None, mono=True, duration=60)  # Only analyze first 60s for speed

        # Duration
        duration = librosa.get_duration(path=str(file_path))

        # BPM
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(tempo)

        # Brightness (spectral centroid)
        brightness = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))

        # Energy (RMS)
        rms = float(np.mean(librosa.feature.rms(y=y)))

        # Zero-crossing rate (texture)
        zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)))

        # Key estimation
        try:
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            key_idx = np.argmax(np.mean(chroma, axis=1))
            key = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"][key_idx]
        except:
            key = "Unknown"

        return {
            "duration": duration,
            "bpm": bpm,
            "brightness": brightness,
            "energy": rms,
            "zcr": zcr,
            "key": key,
            "success": True,
            "y": y,  # Include audio data for genre detection
            "sr": sr
        }

    except Exception as e:
        print(f"    ⚠️  Analysis failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def detect_genre(features: Dict, y: np.ndarray, sr: int) -> Tuple[str, Dict]:
    """
    Detect style: Bright/Energetic or Dark/Atmospheric.

    Args:
        features: Basic audio features (bpm, brightness, energy, etc.)
        y: Audio time series
        sr: Sample rate

    Returns:
        (style_name, style_info)
    """
    # Additional spectral features for style detection

    # 1. Spectral rolloff (frequency below which 85% of energy is contained)
    rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))

    # 2. Spectral contrast (difference between peaks and valleys in spectrum)
    contrast = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr))

    # 3. Spectral flatness (how noise-like vs tone-like)
    flatness = np.mean(librosa.feature.spectral_flatness(y=y))

    brightness = features["brightness"]
    energy = features["energy"]
    zcr = features["zcr"]
    bpm = features["bpm"]

    # Initialize scores
    scores = {
        "bright_energetic": 0.0,
        "dark_atmospheric": 0.0
    }

    # BRIGHT/ENERGETIC characteristics:
    # - High brightness (1800+), higher energy
    # - Driving beats, clear melodic elements
    # - Higher BPM (80-110+)
    # - Higher spectral contrast (distinct melodic/harmonic elements)
    if brightness >= 2000:
        scores["bright_energetic"] += 0.4
    elif brightness >= 1500:
        scores["bright_energetic"] += 0.2

    if energy > 0.10:
        scores["bright_energetic"] += 0.3
    elif energy > 0.08:
        scores["bright_energetic"] += 0.15

    if contrast > 22:
        scores["bright_energetic"] += 0.2

    if bpm >= 90:
        scores["bright_energetic"] += 0.25
    elif bpm >= 80:
        scores["bright_energetic"] += 0.15

    if rolloff > 4000:  # Extended high-frequency content
        scores["bright_energetic"] += 0.15

    # DARK/ATMOSPHERIC characteristics:
    # - Lower brightness (<1500), lower-to-moderate energy
    # - Reverb-heavy, ambient, spacious
    # - Slower-to-moderate BPM (65-90)
    # - Warmer, darker tone
    if brightness < 1000:
        scores["dark_atmospheric"] += 0.7  # Very strong signal for very dark tracks
    elif brightness < 1200:
        scores["dark_atmospheric"] += 0.5
    elif brightness < 1800:
        scores["dark_atmospheric"] += 0.3

    if energy <= 0.10:
        scores["dark_atmospheric"] += 0.2

    if bpm <= 85:
        scores["dark_atmospheric"] += 0.25
    elif bpm <= 95:
        scores["dark_atmospheric"] += 0.1

    if rolloff < 3000:  # Less high-frequency content = warmer/darker
        scores["dark_atmospheric"] += 0.2

    if contrast < 22:  # Less distinct elements = more atmospheric
        scores["dark_atmospheric"] += 0.15

    # Determine winner
    style_name = max(scores, key=scores.get)

    # Format for display
    style_display = {
        "bright_energetic": "Bright/Energetic",
        "dark_atmospheric": "Dark/Atmospheric"
    }

    return style_display[style_name], {
        "scores": scores,
        "rolloff": rolloff,
        "contrast": contrast,
        "flatness": flatness
    }

def score_phase_match(features: Dict, phase_name: str) -> Tuple[float, Dict]:
    """
    Score how well a track matches a phase (0.0 to 1.0).
    Higher score = better match.

    Returns:
        (total_score, score_breakdown)
    """
    criteria = PHASE_CRITERIA[phase_name]

    # BPM score (weighted 50% - most important)
    bpm = features["bpm"]
    bpm_min, bpm_max = criteria["bpm_range"]
    bpm_center = (bpm_min + bpm_max) / 2

    if bpm_min <= bpm <= bpm_max:
        # Within range - score based on how close to center
        distance_from_center = abs(bpm - bpm_center)
        bpm_score = 1.0 - (distance_from_center / ((bpm_max - bpm_min) / 2)) * 0.2
    else:
        # Outside range - harsh penalty
        distance = min(abs(bpm - bpm_min), abs(bpm - bpm_max))
        bpm_score = max(0, 1.0 - (distance / 10))  # 10 BPM tolerance

    # Brightness score (weighted 25%)
    brightness = features["brightness"]
    bright_min, bright_max = criteria["brightness_range"]
    bright_center = (bright_min + bright_max) / 2

    if bright_min <= brightness <= bright_max:
        distance_from_center = abs(brightness - bright_center)
        brightness_score = 1.0 - (distance_from_center / ((bright_max - bright_min) / 2)) * 0.3
    else:
        distance = min(abs(brightness - bright_min), abs(brightness - bright_max))
        brightness_score = max(0, 1.0 - (distance / 500))  # 500 Hz tolerance

    # Energy score (weighted 25%)
    energy = features["energy"]
    energy_min, energy_max = criteria["energy_range"]
    energy_center = (energy_min + energy_max) / 2

    if energy_min <= energy <= energy_max:
        distance_from_center = abs(energy - energy_center)
        energy_score = 1.0 - (distance_from_center / ((energy_max - energy_min) / 2)) * 0.3
    else:
        distance = min(abs(energy - energy_min), abs(energy - energy_max))
        energy_score = max(0, 1.0 - (distance / 0.03))  # 0.03 tolerance

    # Weighted average: BPM 50%, Brightness 25%, Energy 25%
    total_score = (bpm_score * 0.5) + (brightness_score * 0.25) + (energy_score * 0.25)

    breakdown = {
        "bpm_score": bpm_score,
        "brightness_score": brightness_score,
        "energy_score": energy_score,
        "bpm": bpm,
        "brightness": brightness,
        "energy": energy
    }

    return total_score, breakdown

def determine_phase(features: Dict, filename: str) -> Tuple[str, float, str, Dict]:
    """
    Determine the best phase for a track.

    Returns:
        (phase_name, confidence_score, reasoning, all_scores)
    """
    # Check filename for keywords
    filename_lower = filename.lower()
    keyword_matches = {}

    for phase_name, criteria in PHASE_CRITERIA.items():
        for keyword in criteria["keywords"]:
            if keyword in filename_lower:
                keyword_matches[phase_name] = keyword_matches.get(phase_name, 0) + 1

    # Score each phase
    phase_scores = {}
    phase_breakdowns = {}

    for phase_name in PHASE_CRITERIA.keys():
        score, breakdown = score_phase_match(features, phase_name)

        # Boost score if filename has keywords
        if phase_name in keyword_matches:
            score += 0.05 * keyword_matches[phase_name]  # Reduced boost
            score = min(score, 1.0)  # Cap at 1.0

        phase_scores[phase_name] = score
        phase_breakdowns[phase_name] = breakdown

    # Get best match and runner-up
    sorted_phases = sorted(phase_scores.items(), key=lambda x: x[1], reverse=True)
    best_phase = sorted_phases[0][0]
    confidence = sorted_phases[0][1]

    # Build reasoning
    criteria = PHASE_CRITERIA[best_phase]
    breakdown = phase_breakdowns[best_phase]
    reasoning_parts = []

    bpm = features["bpm"]
    bpm_min, bpm_max = criteria["bpm_range"]
    if bpm_min <= bpm <= bpm_max:
        reasoning_parts.append(f"BPM {bpm:.0f} in range [{bpm_min}-{bpm_max}]")
    else:
        reasoning_parts.append(f"BPM {bpm:.0f} outside [{bpm_min}-{bpm_max}]")

    brightness = features["brightness"]
    if brightness < 1800:
        reasoning_parts.append("warm/dark tone")
    elif brightness > 2800:
        reasoning_parts.append("bright tone")
    else:
        reasoning_parts.append("balanced tone")

    energy = features["energy"]
    if energy < 0.06:
        reasoning_parts.append("low energy")
    elif energy > 0.10:
        reasoning_parts.append("high energy")
    else:
        reasoning_parts.append("moderate energy")

    if best_phase in keyword_matches:
        reasoning_parts.append(f"filename keyword match")

    reasoning = ", ".join(reasoning_parts)

    # Build all_scores dict with detailed info
    all_scores = {
        "scores": {
            PHASE_CRITERIA[phase]["name"]: f"{score:.2f}"
            for phase, score in sorted_phases
        },
        "breakdown": breakdown,
        "runner_up": PHASE_CRITERIA[sorted_phases[1][0]]["name"] if len(sorted_phases) > 1 else None,
        "runner_up_score": sorted_phases[1][1] if len(sorted_phases) > 1 else 0
    }

    return best_phase, confidence, reasoning, all_scores

def determine_subfolder(phase_name: str, features: Dict) -> Tuple[str, str]:
    """
    Determine which subfolder within a phase a track should go to.

    Returns:
        (subfolder_name, reason)
    """
    phase = PHASE_CRITERIA[phase_name]
    subfolders = phase["subfolders"]

    bpm = features["bpm"]
    brightness = features["brightness"]
    energy = features["energy"]

    # Check each subfolder criteria in order
    for subfolder_name, subfolder_info in subfolders.items():
        criteria = subfolder_info["criteria"]

        # Evaluate criteria
        if criteria == "default":
            return subfolder_name, subfolder_info["description"]

        # Parse and evaluate criteria string
        try:
            if eval(criteria):
                return subfolder_name, subfolder_info["description"]
        except Exception as e:
            # If eval fails, continue to next
            continue

    # Fallback to first subfolder
    first_subfolder = list(subfolders.keys())[0]
    return first_subfolder, subfolders[first_subfolder]["description"]

def auto_sort_tracks(input_dir: Path, dry_run: bool = False):
    """
    Auto-sort all MP3 files from input directory into arc_library phases.

    Args:
        input_dir: Directory containing unsorted MP3 files
        dry_run: If True, only show what would happen without moving files
    """
    print("=" * 80)
    print("AUTO-SORT TRACKS INTO PHASES")
    print("=" * 80)

    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return

    # Find all MP3 files
    mp3_files = list(input_dir.rglob("*.mp3"))

    if not mp3_files:
        print(f"❌ No MP3 files found in {input_dir}")
        return

    print(f"\n📂 Found {len(mp3_files)} MP3 files to sort")

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be moved\n")
    else:
        print("⚠️  FILES WILL BE MOVED\n")

    # Track results
    results = []
    successful = 0
    failed = 0

    for mp3_file in mp3_files:
        print(f"\n{'='*80}")
        print(f"📀 {mp3_file.name}")
        print(f"{'='*80}")

        # Analyze
        features = analyze_track(mp3_file)

        if not features.get("success"):
            print(f"  ❌ Analysis failed - skipping")
            failed += 1
            continue

        # Detect genre
        genre, genre_info = detect_genre(features, features["y"], features["sr"])

        # Determine phase
        phase_name, confidence, reasoning, all_scores = determine_phase(features, mp3_file.name)
        criteria = PHASE_CRITERIA[phase_name]
        breakdown = all_scores["breakdown"]

        # Determine subfolder
        subfolder, subfolder_reason = determine_subfolder(phase_name, features)

        print(f"\n  🎯 Best Match: {criteria['name']}")
        print(f"  📊 Confidence: {confidence*100:.0f}%")
        print(f"  🎵 Style: {genre} (Bright: {genre_info['scores']['bright_energetic']:.2f}, Dark: {genre_info['scores']['dark_atmospheric']:.2f})")
        print(f"  💡 Reasoning: {reasoning}")
        print(f"  📈 Features: BPM={features['bpm']:.0f}, Brightness={features['brightness']:.0f}, Energy={features['energy']:.4f}")
        print(f"  📊 Score Breakdown: BPM={breakdown['bpm_score']:.2f} (50%), Bright={breakdown['brightness_score']:.2f} (25%), Energy={breakdown['energy_score']:.2f} (25%)")
        print(f"  🏆 All Scores: {', '.join([f'{k}={v}' for k, v in all_scores['scores'].items()])}")
        if all_scores['runner_up']:
            print(f"  🥈 Runner-up: {all_scores['runner_up']} ({all_scores['runner_up_score']*100:.0f}%)")
        print(f"  📂 Subfolder: {subfolder} ({subfolder_reason})")

        # Check if confidence is below threshold
        if confidence < CONFIDENCE_THRESHOLD:
            # Low confidence - move to separate folder with descriptive filename
            confidence_pct = int(confidence * 100)
            phase_short = phase_name.replace("Phase_", "P").replace("_", "")  # e.g., "P1CalmIntro"
            style_short = genre.replace("/", "").replace(" ", "")  # "Bright/Energetic" → "BrightEnergetic"
            new_filename = f"{phase_short}_{confidence_pct}pct_{style_short}_{mp3_file.name}"

            dest_folder = LOW_CONFIDENCE_DIR
            dest_file = dest_folder / new_filename

            print(f"  ⚠️  LOW CONFIDENCE - Moving to review folder")
            print(f"  📝 New name: {new_filename}")
        else:
            # Normal confidence - proceed with phase folder
            dest_folder = ARC_LIBRARY / phase_name / subfolder
            dest_file = dest_folder / mp3_file.name

        # Check if file already exists
        if dest_file.exists():
            print(f"  ⚠️  File already exists at destination - skipping")
            failed += 1
            continue

        print(f"  📁 Destination: {dest_folder.relative_to(PROJECT_ROOT)}/")

        # Move file
        if not dry_run:
            try:
                dest_folder.mkdir(parents=True, exist_ok=True)
                shutil.move(str(mp3_file), str(dest_file))
                print(f"  ✅ Moved successfully")
                successful += 1
            except Exception as e:
                print(f"  ❌ Move failed: {e}")
                failed += 1
        else:
            print(f"  🔍 Would move to: {dest_file.relative_to(PROJECT_ROOT)}")
            successful += 1

        # Store result
        results.append({
            "filename": mp3_file.name,
            "phase": phase_name,
            "confidence": confidence,
            "genre": genre,
            "low_confidence": confidence < CONFIDENCE_THRESHOLD,
            "features": features,
            "reasoning": reasoning
        })

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files:    {len(mp3_files)}")
    print(f"Successfully processed: {successful}")
    print(f"Failed:         {failed}")

    if dry_run:
        print("\n💡 Run without --dry-run to actually move files")
    else:
        print("\n✅ Files have been moved to arc_library")
        print("💡 Run 'yarn analyze' to update metadata")

    # Show phase distribution
    print("\n📊 Phase Distribution:")
    phase_counts = {}
    for result in results:
        phase = PHASE_CRITERIA[result["phase"]]["name"]
        phase_counts[phase] = phase_counts.get(phase, 0) + 1

    for phase, count in sorted(phase_counts.items()):
        print(f"  {phase}: {count} tracks")

    # Show low-confidence tracks
    low_confidence_tracks = [r for r in results if r["low_confidence"]]
    if low_confidence_tracks:
        print(f"\n⚠️  Low Confidence Tracks ({len(low_confidence_tracks)}):")
        for result in low_confidence_tracks:
            phase = PHASE_CRITERIA[result["phase"]]["name"]
            print(f"  {result['filename']} → {phase} ({result['confidence']*100:.0f}%, {result['genre']})")

    # Show style distribution
    print("\n🎵 Style Distribution:")
    style_counts = {}
    for result in results:
        style = result["genre"]  # Variable named 'genre' but contains style
        style_counts[style] = style_counts.get(style, 0) + 1

    for style, count in sorted(style_counts.items()):
        print(f"  {style}: {count} tracks")

def main():
    parser = argparse.ArgumentParser(
        description="Auto-sort tracks into phase folders based on audio analysis"
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Input directory containing unsorted MP3 files"
    )
    parser.add_argument(
        "--scan-downloads",
        action="store_true",
        help="Scan ~/Downloads for MP3 files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without moving files"
    )

    args = parser.parse_args()

    # Determine input directory
    if args.scan_downloads:
        input_dir = Path.home() / "Downloads"
    elif args.input:
        input_dir = Path(args.input)
    else:
        print("❌ Must specify either --input or --scan-downloads")
        parser.print_help()
        sys.exit(1)

    # Run auto-sort
    auto_sort_tracks(input_dir, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
