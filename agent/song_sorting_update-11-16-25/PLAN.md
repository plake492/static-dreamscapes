# Song Sorting Architecture Plan

**Date:** November 16, 2025
**Version:** 1.0
**Status:** Planning

---

## 1. Executive Summary

This document outlines the architecture plan for the Static Dreamscapes automated song sorting and mix generation system. The system intelligently categorizes audio tracks into emotional arc phases, analyzes their characteristics, and generates cohesive 3-hour mixes optimized for focus, relaxation, and creative work.

**Key Goals:**
- Automated phase classification based on audio features (BPM, brightness, energy)
- Intelligent subfolder routing within phases
- Low-confidence track segregation for manual review
- Metadata-driven pipeline orchestration
- Reproducible, version-controlled audio analysis

---

## 2. Current System Architecture

### 2.1 High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     STATIC DREAMSCAPES PIPELINE                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Input: Suno-generated MP3s (unsorted_tracks/ or ~/Downloads)   │
│                                ↓                                  │
│         ┌──────────────────────────────────────┐                │
│         │   Auto-Sort Agent (auto_sort.py)     │                │
│         │   - Audio analysis (BPM, brightness) │                │
│         │   - Phase scoring & classification   │                │
│         │   - Confidence thresholding (70%)    │                │
│         │   - Subfolder routing logic          │                │
│         └──────────────────────────────────────┘                │
│                                ↓                                  │
│         ┌──────────────────────────────────────┐                │
│         │   arc_library/                       │                │
│         │   ├── phase_1_calm_intro/            │                │
│         │   │   ├── ambient_warmth/            │                │
│         │   │   ├── early_dawn/                │                │
│         │   │   └── nostalgic_haze/            │                │
│         │   ├── phase_2_flow_focus/            │                │
│         │   ├── phase_3_uplift_clarity/        │                │
│         │   ├── phase_4_reflective_fade/       │                │
│         │   └── low_confidence/                │                │
│         └──────────────────────────────────────┘                │
│                                ↓                                  │
│         ┌──────────────────────────────────────┐                │
│         │   Orchestrator (orchestrator.py)     │                │
│         │   - File monitoring (watchdog)       │                │
│         │   - Sequential script execution      │                │
│         │   - Error handling & recovery        │                │
│         └──────────────────────────────────────┘                │
│                                ↓                                  │
│         ┌──────────────────────────────────────┐                │
│         │   Processing Steps                   │                │
│         │   1. Rename by mod time              │                │
│         │   2. Add phase prefixes (A_/B_)      │                │
│         │   3. Audio analysis (analyze_audio)  │                │
│         │   4. Verify total length (~3h)       │                │
│         │   5. Build mix (FFmpeg crossfade)    │                │
│         └──────────────────────────────────────┘                │
│                                ↓                                  │
│         ┌──────────────────────────────────────┐                │
│         │   Outputs                            │                │
│         │   - rendered/<track_num>/output.mp4  │                │
│         │   - metadata/phase_*.json            │                │
│         │   - metadata/song_index.json         │                │
│         │   - metadata/build_history.json      │                │
│         └──────────────────────────────────────┘                │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Core Components

#### A. Auto-Sort Agent (`agent/auto_sort.py`)
**Responsibility:** Intelligent track classification and file organization

**Input:** Unsorted MP3 files from arbitrary directories
**Output:** Organized files in `arc_library/phase_X_*/subfolder/`

**Key Features:**
- Audio feature extraction via librosa (BPM, spectral centroid, RMS energy)
- Multi-criteria phase scoring (weighted: BPM 50%, brightness 25%, energy 25%)
- Confidence-based routing (>70% → phase folder, <70% → low_confidence/)
- Subfolder selection based on feature thresholds
- Filename keyword detection for confidence boost
- Genre/style classification (Bright/Energetic vs Dark/Atmospheric)

**Current Limitations:**
- Hardcoded phase criteria (not easily adjustable)
- No machine learning or adaptive classification
- Limited to 60-second audio samples for analysis
- No batch performance optimization

#### B. Orchestrator (`agent/orchestrator.py`)
**Responsibility:** Pipeline coordination and automation

**Modes:**
1. `--watch`: Continuous file monitoring with 60s cooldown
2. `--run-once`: Single pipeline execution
3. `--analyze-only`: Metadata refresh only

**Pipeline Steps:**
1. Rename tracks chronologically (`rename_by_mod_time.sh`)
2. Add phase prefixes (`prepend_tracks.sh`)
3. Extract audio metadata (`analyze_audio.py`)
4. Verify total duration (`track_length_report.sh`)
5. Render mix with crossfades (`build_mix.sh`)

**Error Handling:**
- Steps 1, 2, 4, 5 must exit code 0 (pipeline halts on failure)
- Step 3 (analysis) can fail and pipeline continues
- Comprehensive logging to `logs/orchestrator.log`

#### C. Audio Analysis (`agent/analyze_audio.py`)
**Responsibility:** Extract audio features and update metadata

**Features Extracted:**
- Duration
- BPM (tempo via librosa.beat.beat_track)
- Brightness (spectral centroid mean)
- Energy (RMS loudness)
- Zero-crossing rate
- Key estimation (chroma-based)

**Outputs:**
- `/metadata/phase_X.json` (per-phase song collections)
- `/metadata/song_index.json` (global track lookup)

#### D. Metadata Validator (`agent/validate_metadata.py`)
**Responsibility:** Ensure metadata consistency

**Checks:**
- Orphaned entries (metadata exists, file missing)
- Missing entries (file exists, no metadata)
- Phase mismatches (file in phase_1, metadata says phase_2)
- Duplicate entries

**Repair Actions:**
- `--fix-orphans`: Remove orphaned metadata entries

---

## 3. Phase Classification System

### 3.1 Phase Definitions

#### Phase 1: Calm Intro (70-80 BPM)
**Emotional Arc:** Ambient, nostalgic, warm opening atmosphere
**Characteristics:**
- BPM: 65-78
- Brightness: 1000-2200 Hz (warm/dark)
- Energy: 0.01-0.08 (very low)

**Subfolders:**
- `ambient_warmth/`: Energy < 0.04 (very calm, deep ambient)
- `early_dawn/`: Brightness ≥ 1600 Hz (lighter, brighter calm)
- `nostalgic_haze/`: Default (warm, nostalgic, medium calm)

#### Phase 2: Flow Focus (80-90 BPM)
**Emotional Arc:** Steady mid-tempo for sustained attention
**Characteristics:**
- BPM: 78-92
- Brightness: 1800-2800 Hz (balanced)
- Energy: 0.05-0.12 (moderate)

**Subfolders:**
- `midtempo_groove/`: BPM ≥ 85 (higher tempo groove)
- `analog_pulse/`: Energy ≥ 0.09 (more energetic, pulsing)
- `deep_work/`: Default (steady, focused, lower tempo)

#### Phase 3: Uplift Clarity (90-105 BPM)
**Emotional Arc:** Bright, optimistic energy; creative momentum
**Characteristics:**
- BPM: 88-110
- Brightness: 2200-4000 Hz (bright)
- Energy: 0.08-0.20 (high)

**Subfolders:**
- `bright_pads/`: Brightness ≥ 2800 Hz (brightest, most uplifting)
- `optimistic_melodies/`: BPM ≤ 98 (melodic, moderate tempo)
- `creative_energy/`: Default (high energy, creative momentum)

#### Phase 4: Reflective Fade (55-75 BPM)
**Emotional Arc:** Slow, analog-warm closing for introspection
**Characteristics:**
- BPM: 55-72
- Brightness: 800-2000 Hz (warm/dark)
- Energy: 0.01-0.07 (very low)

**Subfolders:**
- `tape_hiss/`: Brightness < 1400 Hz (darkest, analog, tape-like)
- `vapor_trails/`: BPM ≥ 65 (vaporwave aesthetic)
- `closing_ambience/`: Default (ambient closing, gentle fade)

### 3.2 Scoring Algorithm

For each phase, calculate three weighted scores:

```python
def score_phase(track_features, phase_criteria):
    bpm_score = calculate_bpm_fit(track_features.bpm, phase_criteria.bpm_range)
    brightness_score = calculate_brightness_fit(track_features.brightness, phase_criteria.brightness_range)
    energy_score = calculate_energy_fit(track_features.energy, phase_criteria.energy_range)

    # Weighted combination
    total_score = (bpm_score * 0.50) + (brightness_score * 0.25) + (energy_score * 0.25)

    # Keyword bonus (if filename contains phase keywords)
    if has_matching_keywords(track_features.filename, phase_criteria.keywords):
        total_score *= 1.1  # 10% boost

    return total_score
```

**Within-Range Scoring:**
- If feature is within ideal range: 0.9-1.0 (based on distance from center)
- If feature is outside range: Penalized by distance (steep falloff)

**Tolerances:**
- BPM: ±10 BPM tolerance
- Brightness: ±500 Hz tolerance
- Energy: ±0.03 tolerance

**Final Classification:**
- Best phase = highest score
- Confidence = best_score / (best_score + runner_up_score)
- If confidence < 70% → route to `low_confidence/` folder

---

## 4. Data Model

### 4.1 Phase Metadata Schema

**File:** `/metadata/phase_X_Y.json`

```json
{
  "phase_name": "phase_1_calm_intro",
  "phase_display_name": "Calm Intro",
  "description": "Ambient, nostalgic, warm opening atmosphere",
  "bpm_range": [65, 78],
  "total_tracks": 6,
  "total_duration": 2740.5,
  "last_updated": "2025-11-16T14:32:00Z",
  "tracks": [
    {
      "track_id": "A_001_morning_haze",
      "filename": "A_001_morning_haze.mp3",
      "path": "arc_library/phase_1_calm_intro/ambient_warmth/A_001_morning_haze.mp3",
      "subfolder": "ambient_warmth",
      "duration": 456.7,
      "bpm": 72.3,
      "brightness": 1842.5,
      "energy": 0.034,
      "zcr": 0.045,
      "key": "D minor",
      "analysis_timestamp": "2025-11-16T14:30:12Z"
    }
  ]
}
```

### 4.2 Song Index Schema

**File:** `/metadata/song_index.json`

```json
{
  "_comment": "Global track lookup table",
  "version": "1.0",
  "last_updated": "2025-11-16T14:32:00Z",
  "tracks": {
    "A_001_morning_haze.mp3": {
      "phase": "phase_1_calm_intro",
      "subfolder": "ambient_warmth",
      "path": "arc_library/phase_1_calm_intro/ambient_warmth/A_001_morning_haze.mp3",
      "track_id": "A_001_morning_haze"
    }
  }
}
```

### 4.3 Build History Schema

**File:** `/metadata/build_history.json`

```json
{
  "builds": [
    {
      "build_id": "20251116_143200",
      "track_number": 5,
      "duration_hours": 3.0,
      "total_tracks": 24,
      "output_path": "rendered/5/output_20251116_143200/output.mp4",
      "phases_used": {
        "phase_1_calm_intro": 6,
        "phase_2_flow_focus": 8,
        "phase_3_uplift_clarity": 6,
        "phase_4_reflective_fade": 4
      },
      "total_duration_seconds": 10812,
      "timestamp": "2025-11-16T14:32:00Z",
      "status": "success"
    }
  ]
}
```

---

## 5. Proposed Improvements

### 5.1 Short-Term (Phase 1)

#### A. Enhanced Metadata Schema
**Problem:** Current metadata lacks provenance, confidence scores, and versioning
**Solution:**
- Add `confidence_score` field to track entries
- Add `classification_method` field (manual, auto_v1, auto_v2, etc.)
- Add `metadata_version` to enable schema migrations

#### B. Improved Logging
**Problem:** Difficult to debug classification decisions
**Solution:**
- Structured JSON logging for auto_sort decisions
- Separate log files: `auto_sort.log`, `orchestrator.log`, `analysis.log`
- Log rotation (keep last 10 runs)

#### C. Configuration Externalization
**Problem:** Phase criteria hardcoded in Python
**Solution:**
- Move PHASE_CRITERIA to `/config/phase_criteria.yaml`
- Allow runtime configuration without code changes
- Support multiple configuration profiles (strict, relaxed, experimental)

#### D. Dry-Run Improvements
**Problem:** Dry-run output is verbose, hard to parse
**Solution:**
- JSON output mode for dry-runs
- Summary statistics (phase distribution, confidence histogram)
- CSV export for spreadsheet analysis

### 5.2 Medium-Term (Phase 2)

#### A. Machine Learning Classification
**Problem:** Rule-based scoring is brittle and requires manual tuning
**Solution:**
- Train supervised model on manually curated training set
- Use scikit-learn RandomForest or XGBoost
- Features: BPM, brightness, energy, spectral rolloff, MFCCs
- Store model in `/models/phase_classifier_v1.pkl`
- Fallback to rule-based if model confidence < threshold

#### B. Advanced Audio Features
**Problem:** Limited feature set (BPM, brightness, energy)
**Solution:**
- Add spectral contrast (harmonic richness)
- Add chroma features (tonal quality)
- Add onset strength (rhythmic complexity)
- Add harmony analysis (chord progressions)

#### C. Batch Processing Optimization
**Problem:** Serial processing of large batches is slow
**Solution:**
- Parallel audio analysis (multiprocessing pool)
- Cache analysis results (hash-based, invalidate on file change)
- Progress bar for large batches (tqdm)

#### D. Interactive Review Interface
**Problem:** Manual review of low-confidence tracks is tedious
**Solution:**
- CLI interactive mode: play sample, show scores, accept/override
- Web UI (Flask/FastAPI): drag-drop interface for reclassification
- Bulk operations (accept all, reject all, filter by confidence)

### 5.3 Long-Term (Phase 3)

#### A. Adaptive Classification
**Problem:** User preferences may differ from default criteria
**Solution:**
- Track user overrides (manual reclassifications)
- Retrain model on user feedback
- Personalized classification profiles

#### B. Playlist Generation
**Problem:** Static phase order (always 1→2→3→4)
**Solution:**
- Generate themed playlists (rainy night, sunrise, late work session)
- Dynamic phase transitions based on BPM/key compatibility
- Smooth crossfades based on harmonic similarity

#### C. Cloud Deployment
**Problem:** Local-only, manual trigger
**Solution:**
- Docker containerization
- Cloud storage integration (S3, Google Drive)
- Automated YouTube upload via API
- Serverless processing (AWS Lambda, Google Cloud Functions)

#### D. Analytics Dashboard
**Problem:** No visibility into collection health, trends
**Solution:**
- Phase distribution over time
- BPM/brightness/energy histograms
- Track age analysis (last played, upload date)
- Mix performance metrics (if YouTube analytics integrated)

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Externalize phase criteria to YAML config
- [ ] Add confidence scores to metadata schema
- [ ] Implement structured JSON logging
- [ ] Add dry-run JSON export
- [ ] Write unit tests for scoring algorithm

### Phase 2: Intelligence (Weeks 3-4)
- [ ] Implement parallel audio analysis
- [ ] Add advanced audio features (spectral contrast, chroma)
- [ ] Create training dataset (100 manually curated tracks)
- [ ] Train initial ML classifier (RandomForest)
- [ ] A/B test ML vs rule-based classification

### Phase 3: Usability (Weeks 5-6)
- [ ] Build CLI interactive review mode
- [ ] Implement analysis result caching
- [ ] Add progress bars and better UX
- [ ] Create comprehensive user documentation
- [ ] Video tutorial for new users

### Phase 4: Scale (Weeks 7-8)
- [ ] Dockerize application
- [ ] Implement cloud storage sync
- [ ] Build web UI for remote management
- [ ] Set up automated YouTube upload
- [ ] Deploy analytics dashboard

---

## 7. Testing Strategy

### 7.1 Unit Tests
- Audio feature extraction accuracy
- Phase scoring algorithm correctness
- Confidence calculation edge cases
- Subfolder routing logic

### 7.2 Integration Tests
- Full auto-sort pipeline (download → classify → organize)
- Orchestrator error handling (script failures)
- Metadata consistency after pipeline run

### 7.3 Regression Tests
- Golden dataset (known classifications should not change)
- Performance benchmarks (classification time per track)

### 7.4 User Acceptance Testing
- Blind listening tests (do phase classifications "feel" right?)
- Compare ML classifier vs human classification
- Edge case validation (very slow/fast tracks, unusual genres)

---

## 8. Risk Assessment

### High Risk
- **ML model accuracy:** May perform worse than rules initially
  - Mitigation: Hybrid approach, confidence thresholds, human review

- **Performance degradation:** Parallel processing bugs, race conditions
  - Mitigation: Thorough testing, conservative rollout

### Medium Risk
- **Configuration complexity:** YAML config may introduce errors
  - Mitigation: Schema validation, default fallbacks

- **Breaking changes:** Metadata schema changes affect existing data
  - Mitigation: Migration scripts, backward compatibility

### Low Risk
- **UI adoption:** Users may prefer CLI
  - Mitigation: Keep CLI as primary interface, UI is optional

---

## 9. Success Metrics

### Primary KPIs
- **Classification accuracy:** >90% agreement with manual review
- **Confidence calibration:** 70% threshold should yield 70% precision
- **Processing speed:** <5 seconds per track on average
- **Pipeline uptime:** >95% successful runs (no critical failures)

### Secondary KPIs
- **Low-confidence rate:** <10% of tracks (system is confident most of the time)
- **User override rate:** <5% manual reclassifications
- **Time savings:** 80% reduction in manual sorting effort

---

## 10. Conclusion

The Static Dreamscapes song sorting system is currently functional but has significant room for improvement in intelligence, scalability, and usability. This plan proposes a phased approach to enhance the system with machine learning, better UX, and cloud deployment while maintaining backward compatibility and stability.

**Next Steps:**
1. Review and approve architecture plan
2. Prioritize Phase 1 improvements
3. Create detailed technical specifications for each component
4. Begin implementation with foundation layer

---

**Document Maintained By:** Static Dreamscapes Development Team
**Last Updated:** November 16, 2025
**Next Review:** December 1, 2025
