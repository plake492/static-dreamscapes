"""
Prompt Validator - Detects forbidden technical phrases in song prompts.

This module validates prompts after import to ensure they use evocative
vocabulary instead of technical production terms, maintaining semantic
consistency for song matching across tracks.
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class PromptViolation:
    """Represents a forbidden phrase found in a prompt."""
    arc_number: int
    arc_name: str
    prompt_number: int
    prompt_text: str
    violations: List[str]


# Forbidden technical phrases (from PROMPT_CRAFTING_GUIDE.md)
FORBIDDEN_PHRASES = [
    # Production/mixing terms
    "slow attack and long release",
    "slow attack",
    "long release",
    "mid-low register",
    "mid-frequency range",
    "upper register",
    "lower register",
    "wide stereo field",
    "stereo field",
    "low-pass filtered",
    "high-pass filtered",
    "band-pass",
    "filter cutoff",
    "resonance sweep",
    "sidechain",
    "sidechained",

    # Negative phrasing
    "no percussion",
    "no drums",
    "no rhythmic elements",
    "zero percussion",
    "zero rhythmic drive",
    "zero rhythmic",
    "beatless structure",
    "beatless",
    "no beat",
    "without percussion",
    "without drums",

    # Technical density terms
    "extremely low event density",
    "event density",
    "low event density",
    "high event density",

    # Overly specific technical terms
    "chord cycling every 8 bars",
    "chord cycling every",
    "cycling every",
    "extended complex chords",
    "minimal harmonic change",
    "faint static noise bed",
    "static noise bed",
    "vocal pads in upper register",

    # Production-specific terms
    "attack envelope",
    "release envelope",
    "adsr",
    "LFO",
    "oscillator",
    "filter envelope",
    "modulation depth",
    "velocity sensitivity",
]

# Patterns to check with regex (case-insensitive)
FORBIDDEN_PATTERNS = [
    r"\b(no|zero|without)\s+(percussion|drums|beat|rhythm)",
    r"\b(attack|release|sustain|decay)\s+(time|envelope)",
    r"\b(low|mid|high|upper|lower)-?(pass|band|frequency)?\s+(filter|range|register)",
    r"\bchord\s+cycling\s+every\s+\d+\s+bars?",
    r"\bevent\s+density",
]


def check_prompt_for_violations(prompt_text: str) -> List[str]:
    """
    Check a single prompt for forbidden technical phrases.

    Args:
        prompt_text: The prompt text to validate

    Returns:
        List of forbidden phrases found in the prompt
    """
    violations = []
    prompt_lower = prompt_text.lower()

    # Check exact phrases
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in prompt_lower:
            violations.append(phrase)

    # Check regex patterns
    for pattern in FORBIDDEN_PATTERNS:
        matches = re.finditer(pattern, prompt_lower, re.IGNORECASE)
        for match in matches:
            matched_text = match.group(0)
            if matched_text not in [v.lower() for v in violations]:
                violations.append(matched_text)

    return violations


def validate_track_prompts(db, track_id: str) -> List[PromptViolation]:
    """
    Validate all prompts for a track after import.

    Args:
        db: Database connection
        track_id: Track ID to validate prompts for

    Returns:
        List of PromptViolation objects for prompts with forbidden phrases
    """
    violations = []

    cursor = db.conn.cursor()

    # Get unique prompts for this track from songs table
    # Group by arc_number and prompt_number to get unique prompts
    query = """
        SELECT DISTINCT
            arc_number,
            arc_name,
            prompt_number,
            prompt_text
        FROM songs
        WHERE track_id = ?
          AND prompt_text IS NOT NULL
        ORDER BY arc_number, prompt_number
    """

    cursor.execute(query, (track_id,))
    prompts = cursor.fetchall()

    for arc_num, arc_name, prompt_num, prompt_text in prompts:
        # Check this prompt for violations
        found_violations = check_prompt_for_violations(prompt_text)

        if found_violations:
            violations.append(PromptViolation(
                arc_number=arc_num,
                arc_name=arc_name,
                prompt_number=prompt_num,
                prompt_text=prompt_text,
                violations=found_violations
            ))

    return violations


def format_violation_report(violations: List[PromptViolation], track_number: int = None) -> str:
    """
    Format a human-readable report of prompt violations.

    Args:
        violations: List of PromptViolation objects
        track_number: Optional track number for context

    Returns:
        Formatted report string with Rich markup
    """
    if not violations:
        return ""

    report_lines = []
    report_lines.append("")
    report_lines.append("[yellow]⚠️  WARNING: Found forbidden technical phrases in prompts:[/yellow]")
    report_lines.append("")

    for violation in violations:
        # Format as "Arc X - Prompt Y: phrase1, phrase2"
        arc_label = f"Arc {violation.arc_number}"
        prompt_label = f"Prompt {violation.prompt_number}"
        phrases = ", ".join([f'"{p}"' for p in violation.violations])

        report_lines.append(f"  [dim]•[/dim] {arc_label} - {prompt_label}: {phrases}")

    report_lines.append("")
    report_lines.append("[dim]📖 See PROMPT_CRAFTING_GUIDE.md for approved evocative vocabulary[/dim]")
    report_lines.append("")

    # Summary stats
    total_prompts_with_violations = len(violations)
    total_unique_violations = len(set(v for violation in violations for v in violation.violations))

    report_lines.append(f"[yellow]Summary:[/yellow]")
    report_lines.append(f"  • {total_prompts_with_violations} prompt(s) with violations")
    report_lines.append(f"  • {total_unique_violations} unique forbidden phrase(s)")
    report_lines.append("")

    return "\n".join(report_lines)
