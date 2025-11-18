#!/usr/bin/env python3
"""
Static Dreamscapes - Orchestrator
----------------------------------
Main automation pipeline for detecting, processing, and rendering 3-hour mixes.
Coordinates shell scripts, audio analysis, and metadata updates.

Usage:
    python3 agent/orchestrator.py --watch              # Continuous monitoring mode
    python3 agent/orchestrator.py --run-once           # Single pipeline execution
    python3 agent/orchestrator.py --analyze-only       # Just run audio analysis
"""

import os
import sys
import json
import time
import argparse
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
ARC_LIBRARY = PROJECT_ROOT / "arc_library"
METADATA_DIR = PROJECT_ROOT / "metadata"
RENDERED_DIR = PROJECT_ROOT / "rendered"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
LOGS_DIR = PROJECT_ROOT / "logs"

# Script paths
RENAME_SCRIPT = SCRIPTS_DIR / "rename_by_mod_time.sh"
PREPEND_SCRIPT = SCRIPTS_DIR / "prepend_tracks.sh"
LENGTH_REPORT_SCRIPT = SCRIPTS_DIR / "track_length_report.sh"
BUILD_MIX_SCRIPT = SCRIPTS_DIR / "build_mix.sh"
ANALYZE_AUDIO_SCRIPT = PROJECT_ROOT / "agent" / "analyze_audio.py"

# Pipeline configuration
TARGET_DURATION = 10800  # 3 hours in seconds
DURATION_TOLERANCE = 60  # ±60 seconds acceptable

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Initialize logging system with file and console handlers."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "orchestrator.log"

    # Create formatters
    file_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logging()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def run_script(script_path: Path, args: List[str] = None, can_fail: bool = False) -> Tuple[bool, str]:
    """
    Execute a shell script or Python script with error handling.

    Args:
        script_path: Path to the script
        args: Optional list of arguments
        can_fail: If True, pipeline continues even if script fails

    Returns:
        Tuple of (success: bool, output: str)
    """
    script_name = script_path.name
    cmd = []

    if script_path.suffix == '.py':
        cmd = ['python3', str(script_path)]
    elif script_path.suffix == '.sh':
        cmd = ['bash', str(script_path)]
    else:
        logger.error(f"Unknown script type: {script_path}")
        return False, ""

    if args:
        cmd.extend(args)

    logger.info(f"Executing: {script_name}")
    logger.debug(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        output = result.stdout + result.stderr

        if result.returncode == 0:
            logger.info(f"✓ {script_name} completed successfully")
            logger.debug(f"Output: {output[:500]}")  # Log first 500 chars
            return True, output
        else:
            if can_fail:
                logger.warning(f"⚠ {script_name} failed (continuing anyway)")
                logger.debug(f"Error output: {output}")
                return False, output
            else:
                logger.error(f"✗ {script_name} failed with return code {result.returncode}")
                logger.error(f"Error output: {output}")
                return False, output

    except subprocess.TimeoutExpired:
        logger.error(f"✗ {script_name} timed out after 10 minutes")
        return False, ""
    except Exception as e:
        logger.error(f"✗ Exception running {script_name}: {e}")
        return False, str(e)

def count_mp3_files() -> int:
    """Count total MP3 files in arc_library."""
    return len(list(ARC_LIBRARY.rglob("*.mp3")))

def get_total_duration() -> Optional[float]:
    """
    Parse total_length.txt if it exists and return duration in seconds.
    """
    length_file = PROJECT_ROOT / "total_length.txt"
    if not length_file.exists():
        return None

    try:
        content = length_file.read_text().strip()
        # Parse first number (should be seconds)
        seconds = float(content.split()[0])
        return seconds
    except Exception as e:
        logger.error(f"Failed to parse total_length.txt: {e}")
        return None

def update_build_history(track_num: Optional[int] = None, metadata: Dict = None):
    """
    Update build_history.json with information about the completed render.
    """
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    history_file = METADATA_DIR / "build_history.json"

    # Load existing history
    if history_file.exists():
        history = json.loads(history_file.read_text())
    else:
        history = {"builds": []}

    # Create new build entry
    build_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "track_number": track_num,
        "total_files": count_mp3_files(),
        "metadata": metadata or {}
    }

    history["builds"].append(build_entry)

    # Write back
    history_file.write_text(json.dumps(history, indent=2))
    logger.info(f"Updated build history: {history_file}")

# ============================================================================
# PIPELINE ORCHESTRATION
# ============================================================================

class PipelineOrchestrator:
    """Main orchestrator for the automation pipeline."""

    def __init__(self):
        self.ensure_directories()

    def ensure_directories(self):
        """Create required directories if they don't exist."""
        for directory in [ARC_LIBRARY, METADATA_DIR, RENDERED_DIR, LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")

    def run_full_pipeline(self, track_num: Optional[int] = None) -> bool:
        """
        Execute the complete automation pipeline.

        Pipeline steps:
        1. rename_by_mod_time.sh (must succeed)
        2. prepend_tracks.sh (must succeed)
        3. analyze_audio.py (can fail)
        4. track_length_report.sh (must succeed)
        5. build_mix.sh (must succeed)

        Args:
            track_num: Optional track number for build_mix.sh

        Returns:
            True if pipeline completed successfully
        """
        logger.info("=" * 60)
        logger.info("STARTING FULL AUTOMATION PIPELINE")
        logger.info("=" * 60)

        start_time = time.time()

        # Step 1: Rename by modification time
        logger.info("\n[STEP 1/5] Renaming tracks by modification time...")

        # Find all phase folders
        phase_folders = sorted([d for d in ARC_LIBRARY.iterdir() if d.is_dir() and d.name.startswith("phase_")])

        if not phase_folders:
            logger.error("No phase folders found in arc_library")
            return False

        # Run rename script for each phase folder
        for phase_folder in phase_folders:
            success, _ = run_script(RENAME_SCRIPT, [str(phase_folder)])
            if not success:
                logger.error(f"Pipeline halted at step 1 (rename) for {phase_folder.name}")
                return False

        # Step 2: Prepend phase prefixes
        logger.info("\n[STEP 2/5] Adding phase prefixes...")
        success, _ = run_script(PREPEND_SCRIPT)
        if not success:
            logger.error("Pipeline halted at step 2 (prepend)")
            return False

        # Step 3: Analyze audio (can fail)
        logger.info("\n[STEP 3/5] Analyzing audio features...")
        success, _ = run_script(
            ANALYZE_AUDIO_SCRIPT,
            ['--input', str(ARC_LIBRARY), '--output', str(METADATA_DIR)],
            can_fail=True
        )
        # Continue regardless of analysis success

        # Step 4: Verify total length
        logger.info("\n[STEP 4/5] Verifying total runtime...")
        success, _ = run_script(LENGTH_REPORT_SCRIPT)
        if not success:
            logger.error("Pipeline halted at step 4 (length verification)")
            return False

        # Check if duration is within tolerance
        total_duration = get_total_duration()
        if total_duration:
            diff = abs(total_duration - TARGET_DURATION)
            logger.info(f"Total duration: {total_duration:.0f}s (target: {TARGET_DURATION}s, diff: {diff:.0f}s)")

            if diff > DURATION_TOLERANCE:
                logger.warning(f"Duration difference ({diff:.0f}s) exceeds tolerance ({DURATION_TOLERANCE}s)")
                logger.warning("Consider adding or removing tracks to reach ~3 hours")

        # Step 5: Build the mix
        logger.info("\n[STEP 5/5] Building final mix...")

        build_args = []
        if track_num:
            build_args = [str(track_num)]

        success, _ = run_script(BUILD_MIX_SCRIPT, build_args)
        if not success:
            logger.error("Pipeline halted at step 5 (build mix)")
            return False

        # Update build history
        elapsed_time = time.time() - start_time
        update_build_history(track_num, {
            "duration_seconds": total_duration,
            "pipeline_runtime": elapsed_time,
            "success": True
        })

        logger.info("\n" + "=" * 60)
        logger.info(f"PIPELINE COMPLETED SUCCESSFULLY in {elapsed_time:.1f}s")
        logger.info("=" * 60)

        return True

    def analyze_only(self):
        """Run only the audio analysis step."""
        logger.info("Running audio analysis only...")
        success, _ = run_script(
            ANALYZE_AUDIO_SCRIPT,
            ['--input', str(ARC_LIBRARY), '--output', str(METADATA_DIR)],
            can_fail=False
        )
        return success

# ============================================================================
# FILE WATCHING
# ============================================================================

class MP3FileHandler(FileSystemEventHandler):
    """Watches for new MP3 files and triggers the pipeline."""

    def __init__(self, orchestrator: PipelineOrchestrator):
        self.orchestrator = orchestrator
        self.cooldown_time = 60  # Wait 60s after last file before triggering
        self.last_file_time = None
        self.pending_trigger = False

    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return

        if event.src_path.endswith('.mp3'):
            logger.info(f"New MP3 detected: {Path(event.src_path).name}")
            self.last_file_time = time.time()
            self.pending_trigger = True

    def check_trigger(self):
        """Check if enough time has passed to trigger pipeline."""
        if not self.pending_trigger:
            return

        if self.last_file_time and (time.time() - self.last_file_time > self.cooldown_time):
            logger.info(f"Cooldown period elapsed. Triggering pipeline...")
            self.pending_trigger = False
            self.orchestrator.run_full_pipeline()

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Static Dreamscapes Orchestrator - Automate mix generation"
    )
    parser.add_argument(
        '--watch',
        action='store_true',
        help='Watch arc_library for new files and auto-trigger pipeline'
    )
    parser.add_argument(
        '--run-once',
        action='store_true',
        help='Run the pipeline once immediately'
    )
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Only run audio analysis step'
    )
    parser.add_argument(
        '--track-num',
        type=int,
        help='Track number for build_mix.sh'
    )

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = PipelineOrchestrator()

    # Analyze only mode
    if args.analyze_only:
        logger.info("Starting in analyze-only mode")
        success = orchestrator.analyze_only()
        sys.exit(0 if success else 1)

    # Run once mode
    if args.run_once:
        logger.info("Starting in run-once mode")
        success = orchestrator.run_full_pipeline(args.track_num)
        sys.exit(0 if success else 1)

    # Watch mode
    if args.watch:
        logger.info("Starting in watch mode")
        logger.info(f"Monitoring: {ARC_LIBRARY}")
        logger.info(f"Cooldown period: 60 seconds after last file")
        logger.info("Press Ctrl+C to stop")

        event_handler = MP3FileHandler(orchestrator)
        observer = Observer()
        observer.schedule(event_handler, str(ARC_LIBRARY), recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(5)
                event_handler.check_trigger()
        except KeyboardInterrupt:
            logger.info("Stopping file watcher...")
            observer.stop()

        observer.join()
        sys.exit(0)

    # No mode specified
    parser.print_help()
    sys.exit(1)

if __name__ == "__main__":
    main()
