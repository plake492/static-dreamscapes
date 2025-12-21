#!/usr/bin/env python3
"""
Batch import tracks from a Notion parent folder/database.

Scans all child pages of a parent Notion page and imports matching tracks.
Only imports if:
1. Child page title matches pattern "Track X: *" (where X is a number)
2. Corresponding Tracks/X/Songs/ folder exists with MP3 files
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Set, Tuple, Optional
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Load environment variables from .env file
load_dotenv()

console = Console()


def get_notion_client() -> Client:
    """Initialize Notion client with API token from environment."""
    api_token = os.getenv("NOTION_API_TOKEN")
    if not api_token:
        console.print("[red]❌ NOTION_API_TOKEN not found in environment[/red]")
        console.print("\nSet it in your .env file:")
        console.print("  NOTION_API_TOKEN=secret_your_token_here\n")
        sys.exit(1)
    return Client(auth=api_token)


def extract_page_id(notion_url: str) -> str:
    """Extract page ID from Notion URL."""
    # Notion URLs format: https://www.notion.so/Page-Title-{page_id}
    # Page ID is the last 32 characters (with or without hyphens)
    match = re.search(r'([a-f0-9]{32}|[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', notion_url)
    if match:
        return match.group(1).replace('-', '')
    raise ValueError(f"Could not extract page ID from URL: {notion_url}")


def get_child_pages(client: Client, parent_id: str) -> List[dict]:
    """Get all child pages from a parent page."""
    try:
        # Query for blocks that are child pages
        response = client.blocks.children.list(block_id=parent_id)
        child_pages = []

        for block in response.get('results', []):
            if block['type'] == 'child_page':
                child_pages.append({
                    'id': block['id'],
                    'title': block['child_page']['title'],
                    'url': f"https://www.notion.so/{block['id'].replace('-', '')}"
                })

        return child_pages
    except APIResponseError as e:
        console.print(f"[red]❌ Error fetching child pages: {e}[/red]")
        return []


def parse_track_number(title: str) -> Optional[int]:
    """
    Extract track number from page title.

    Expected formats:
    - "Track 14: Something"
    - "Track 14 - Something"
    - "Track 14 Something"

    Returns:
        Track number as int, or None if not found
    """
    # Match "Track" followed by a number
    match = re.match(r'^Track\s+(\d+)', title, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def check_track_folder(track_number: int, base_dir: Path = Path("./Tracks")) -> Tuple[bool, int]:
    """
    Check if track folder exists with MP3 files in Songs directory.

    Returns:
        Tuple of (exists: bool, mp3_count: int)
    """
    songs_dir = base_dir / str(track_number) / "Songs"

    if not songs_dir.exists() or not songs_dir.is_dir():
        return False, 0

    mp3_files = list(songs_dir.glob("*.mp3"))
    return len(mp3_files) > 0, len(mp3_files)


def import_track(notion_url: str, track_number: int, dry_run: bool = False) -> bool:
    """
    Import a track using the import-songs command.

    Returns:
        True if successful, False otherwise
    """
    songs_dir = f"./Tracks/{track_number}/Songs"

    if dry_run:
        console.print(f"  [dim]Would run: yarn import-songs --notion-url \"{notion_url}\" --songs-dir \"{songs_dir}\"[/dim]")
        return True

    import subprocess

    cmd = [
        "yarn", "import-songs",
        "--notion-url", notion_url,
        "--songs-dir", songs_dir
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        console.print(f"[red]  ❌ Import failed: {e}[/red]")
        if e.stderr:
            console.print(f"[dim]{e.stderr}[/dim]")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Batch import tracks from a Notion parent folder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using environment variable (add to .env):
  # NOTION_PARENT_FOLDER_URL=https://notion.so/parent-page

  # Dry run to see what would be imported
  python scripts/batch_import_from_notion.py --dry-run

  # Import all matching tracks (using env var)
  python scripts/batch_import_from_notion.py

  # Or provide URL directly
  python scripts/batch_import_from_notion.py \\
    --notion-url "https://notion.so/parent-page"

  # Skip specific tracks
  python scripts/batch_import_from_notion.py \\
    --skip-tracks "14,15,20"
        """
    )

    parser.add_argument(
        "--notion-url", "-n",
        required=False,
        help="Notion parent folder/page URL (or set NOTION_PARENT_FOLDER_URL env var)"
    )

    parser.add_argument(
        "--skip-tracks", "-s",
        default="",
        help="Comma-separated list of track numbers to skip (e.g., '14,15,20')"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be imported without actually importing"
    )

    parser.add_argument(
        "--base-dir",
        default="./Tracks",
        help="Base directory for tracks (default: ./Tracks)"
    )

    args = parser.parse_args()

    # Get Notion URL from args or environment variable
    notion_url = args.notion_url or os.getenv("NOTION_PARENT_FOLDER_URL")

    if not notion_url:
        console.print("[red]❌ Notion URL not provided[/red]")
        console.print("\nProvide it via:")
        console.print("  1. --notion-url argument, OR")
        console.print("  2. NOTION_PARENT_FOLDER_URL environment variable in .env\n")
        sys.exit(1)

    # Parse skip tracks
    skip_tracks: Set[int] = set()
    if args.skip_tracks:
        try:
            skip_tracks = {int(t.strip()) for t in args.skip_tracks.split(",")}
        except ValueError:
            console.print("[red]❌ Invalid skip-tracks format. Use comma-separated numbers (e.g., '14,15,20')[/red]")
            sys.exit(1)

    console.print("\n[bold blue]📦 Batch Import from Notion Folder[/bold blue]\n")

    if args.dry_run:
        console.print("[yellow]🔍 DRY RUN MODE - No actual imports will be performed[/yellow]\n")

    # Initialize Notion client
    client = get_notion_client()

    # Extract parent page ID
    try:
        parent_id = extract_page_id(notion_url)
        console.print(f"Parent folder URL: [cyan]{notion_url}[/cyan]")
        console.print(f"Parent page ID: [cyan]{parent_id}[/cyan]")
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        sys.exit(1)

    # Get child pages
    console.print("\n[bold]Fetching child pages...[/bold]")
    child_pages = get_child_pages(client, parent_id)

    if not child_pages:
        console.print("[yellow]⚠️  No child pages found[/yellow]")
        return

    console.print(f"Found {len(child_pages)} child pages\n")

    # Analyze each child page
    results = {
        'valid': [],      # (track_num, title, url, mp3_count)
        'skipped': [],    # (track_num, title, reason)
        'invalid': []     # (title, reason)
    }

    for page in child_pages:
        title = page['title']
        url = page['url']

        # Parse track number
        track_num = parse_track_number(title)

        if track_num is None:
            results['invalid'].append((title, "Title doesn't match 'Track X: *' pattern"))
            continue

        # Check if track should be skipped
        if track_num in skip_tracks:
            results['skipped'].append((track_num, title, "Manually skipped (--skip-tracks)"))
            continue

        # Check if folder exists with MP3s
        exists, mp3_count = check_track_folder(track_num, Path(args.base_dir))

        if not exists:
            results['skipped'].append((track_num, title, f"No Tracks/{track_num}/Songs/*.mp3 files found"))
            continue

        results['valid'].append((track_num, title, url, mp3_count))

    # Display summary table
    console.print("[bold]Analysis Summary:[/bold]\n")

    summary_table = Table(show_header=True, header_style="bold cyan")
    summary_table.add_column("Category", style="bold")
    summary_table.add_column("Count", justify="right")

    summary_table.add_row("✅ Ready to Import", str(len(results['valid'])))
    summary_table.add_row("⏭️  Skipped", str(len(results['skipped'])))
    summary_table.add_row("❌ Invalid", str(len(results['invalid'])))
    summary_table.add_row("📄 Total Pages", str(len(child_pages)))

    console.print(summary_table)
    console.print()

    # Show valid tracks
    if results['valid']:
        console.print("[bold green]✅ Tracks Ready to Import:[/bold green]\n")

        valid_table = Table(show_header=True, header_style="bold green")
        valid_table.add_column("Track", justify="right")
        valid_table.add_column("Title")
        valid_table.add_column("MP3s", justify="right")

        for track_num, title, url, mp3_count in sorted(results['valid']):
            valid_table.add_row(str(track_num), title, str(mp3_count))

        console.print(valid_table)
        console.print()

    # Show skipped tracks
    if results['skipped']:
        console.print("[bold yellow]⏭️  Skipped Tracks:[/bold yellow]\n")

        skipped_table = Table(show_header=True, header_style="bold yellow")
        skipped_table.add_column("Track", justify="right")
        skipped_table.add_column("Title")
        skipped_table.add_column("Reason")

        for track_num, title, reason in sorted(results['skipped']):
            skipped_table.add_row(str(track_num), title, reason)

        console.print(skipped_table)
        console.print()

    # Show invalid pages
    if results['invalid']:
        console.print("[bold red]❌ Invalid Pages (not track documents):[/bold red]\n")

        invalid_table = Table(show_header=True, header_style="bold red")
        invalid_table.add_column("Title")
        invalid_table.add_column("Reason")

        for title, reason in results['invalid']:
            invalid_table.add_row(title, reason)

        console.print(invalid_table)
        console.print()

    # Execute imports
    if not results['valid']:
        console.print("[yellow]No tracks to import[/yellow]\n")
        return

    if not args.dry_run:
        console.print(f"[bold]Importing {len(results['valid'])} tracks...[/bold]\n")

        success_count = 0
        fail_count = 0

        for track_num, title, url, mp3_count in sorted(results['valid']):
            console.print(f"[bold cyan]Track {track_num}:[/bold cyan] {title}")
            console.print(f"  MP3 files: {mp3_count}")

            if import_track(url, track_num, dry_run=False):
                console.print("  [green]✓ Import successful[/green]\n")
                success_count += 1
            else:
                console.print("  [red]✗ Import failed[/red]\n")
                fail_count += 1

        # Final summary
        console.print("[bold]Import Complete![/bold]\n")

        final_table = Table(show_header=True, header_style="bold")
        final_table.add_column("Result", style="bold")
        final_table.add_column("Count", justify="right")

        final_table.add_row("[green]✓ Successful[/green]", str(success_count))
        final_table.add_row("[red]✗ Failed[/red]", str(fail_count))

        console.print(final_table)
        console.print()

        if success_count > 0:
            console.print("[bold yellow]💡 Next step:[/bold yellow]")
            console.print("   yarn generate-embeddings\n")
    else:
        console.print(f"[dim]Dry run complete. {len(results['valid'])} tracks would be imported.[/dim]\n")


if __name__ == "__main__":
    main()
