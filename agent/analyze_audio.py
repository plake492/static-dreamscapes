#!/usr/bin/env python3
"""
Static Dreamscapes - Audio Analysis Script
------------------------------------------
Scans all MP3 files inside arc_library, extracts detailed audio metadata
(duration, BPM, key, loudness, brightness, etc.) using librosa, and writes
JSON metadata into /metadata/phase_X.json + /metadata/song_index.json.

Run manually or via Bash pipeline:
    python3 agent/analyze_audio.py --input ./arc_library --output ./metadata
"""

import os, json, argparse, librosa, numpy as np
from pathlib import Path
from datetime import datetime

def analyze_audio(file_path: Path):
    """Extract key audio features from an MP3 file."""
    y, sr = librosa.load(file_path, sr=None, mono=True)
    duration = librosa.get_duration(y=y, sr=sr)

    # Tempo (BPM)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    # RMS Energy
    rms = float(np.mean(librosa.feature.rms(y=y)))

    # Brightness (spectral centroid)
    brightness = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))

    # Zero-crossing rate (texture/roughness)
    zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)))

    # Rough tonal centroid-based key estimation
    try:
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        key_idx = np.argmax(np.mean(chroma, axis=1))
        key_guess = [
            "C","C#","D","D#","E","F","F#","G","G#","A","A#","B"
        ][key_idx]
    except Exception:
        key_guess = "Unknown"

    return {
        "filename": file_path.name,
        "duration_sec": round(duration, 2),
        "bpm": round(float(tempo), 1),
        "rms": round(rms, 5),
        "brightness": round(brightness, 2),
        "zcr": round(zcr, 5),
        "key_guess": key_guess,
        "analyzed_at": datetime.utcnow().isoformat() + "Z"
    }

def update_metadata(output_dir: Path, file_info: dict, phase: str):
    """Merge results into the correct phase file and global index."""
    phase_json = output_dir / f"{phase}.json"
    index_json = output_dir / "song_index.json"

    # Load or initialize
    phase_data = json.loads(phase_json.read_text()) if phase_json.exists() else {"phase": phase, "songs": []}
    index_data = json.loads(index_json.read_text()) if index_json.exists() else {}

    # Insert
    phase_data["songs"].append(file_info)
    index_data[file_info["filename"]] = {"phase": phase, "path": str(phase_json)}

    # Write back
    phase_json.write_text(json.dumps(phase_data, indent=2))
    index_json.write_text(json.dumps(index_data, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Analyze audio files for metadata extraction.")
    parser.add_argument("--input", required=True, help="Input folder (arc_library root)")
    parser.add_argument("--output", required=True, help="Output folder (metadata root)")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Iterate through all MP3s in arc_library
    for mp3 in input_dir.rglob("*.mp3"):
        phase = mp3.parent.parent.name  # assumes phase_X_... structure
        print(f"Analyzing {mp3.name} → {phase}")
        try:
            features = analyze_audio(mp3)
            features["phase_name"] = phase
            features["file_path"] = str(mp3)
            update_metadata(output_dir, features, phase)
        except Exception as e:
            print(f"⚠️  Skipped {mp3.name}: {e}")

    print("✅ Audio analysis complete.")

if __name__ == "__main__":
    main()
