"""Main CLI entry point for the LoFi Track Manager."""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import logging
import sys

from ..core.database import Database
from ..core.config import get_config

# Initialize CLI app
app = typer.Typer(
    name="lofi-manager",
    help="LoFi Track Manager - Automated workflow for YouTube lofi music production",
    add_completion=False
)

console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.command()
def init_db(
    config_path: str = typer.Option("./config/settings.yaml", help="Path to config file")
):
    """Initialize the database schema."""
    try:
        config = get_config(config_path)
        db = Database(config.database_path)

        console.print("\n[bold blue]🗄️  Initializing Database[/bold blue]")
        console.print(f"Database path: {config.database_path}\n")

        db.init_schema()

        console.print("[bold green]✅ Database initialized successfully![/bold green]\n")

        # Show status
        song_count = db.get_song_count()
        track_count = db.get_track_count()

        table = Table(title="Database Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="magenta")

        table.add_row("Songs", str(song_count))
        table.add_row("Tracks", str(track_count))

        console.print(table)
        console.print()

        db.close()

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]\n")
        raise typer.Exit(code=1)


@app.command()
def import_songs(
    notion_url: str = typer.Option(..., "--notion-url", "-n", help="Notion document URL"),
    songs_dir: str = typer.Option(..., "--songs-dir", "-s", help="Directory containing audio files"),
    config_path: str = typer.Option("./config/settings.yaml", help="Path to config file"),
    force_reanalyze: bool = typer.Option(False, "--force", help="Force re-analysis of existing songs")
):
    """Import songs from a directory with Notion metadata."""
    try:
        from ..ingest.metadata_extractor import MetadataExtractor
        from ..ingest.notion_parser import NotionParser
        from ..ingest.audio_analyzer import AudioAnalyzer
        from pathlib import Path

        config = get_config(config_path)
        db = Database(config.database_path)

        console.print("\n[bold blue]📥 Importing Songs[/bold blue]\n")
        console.print(f"Notion URL: {notion_url}")
        console.print(f"Songs directory: {songs_dir}\n")

        # Initialize components
        notion_parser = NotionParser()
        audio_analyzer = AudioAnalyzer()
        extractor = MetadataExtractor(db, notion_parser, audio_analyzer)

        # Import track
        with console.status("[bold green]Processing...", spinner="dots"):
            track, songs = extractor.import_track_from_notion(
                notion_url=notion_url,
                songs_dir=Path(songs_dir),
                force_reanalyze=force_reanalyze
            )

        # Display results
        console.print("[bold green]✅ Import completed successfully![/bold green]\n")

        console.print(f"[bold]Track:[/bold] {track.title}")
        console.print(f"[bold]Theme:[/bold] {track.overall_theme}")
        console.print(f"[bold]Songs imported:[/bold] {len(songs)}\n")

        # Show sample songs
        if songs:
            table = Table(title=f"Imported Songs (showing first 10)")
            table.add_column("Filename", style="cyan")
            table.add_column("Arc", style="yellow")
            table.add_column("BPM", style="green")
            table.add_column("Duration", style="magenta")

            for song in songs[:10]:
                table.add_row(
                    song.filename,
                    f"Arc {song.arc_number}" if song.arc_number else "N/A",
                    f"{song.bpm:.1f}" if song.bpm else "N/A",
                    f"{song.duration_seconds:.0f}s" if song.duration_seconds else "N/A"
                )

            console.print(table)
            if len(songs) > 10:
                console.print(f"\n... and {len(songs) - 10} more songs\n")

        db.close()

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]\n")
        import traceback
        traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def query(
    notion_url: str = typer.Option(..., "--notion-url", "-n", help="Notion document URL for new track"),
    output: str = typer.Option("./output/playlists/playlist.json", "--output", "-o", help="Output JSON file"),
    target_duration: int = typer.Option(180, "--duration", "-d", help="Target duration in minutes"),
    songs_per_arc: int = typer.Option(11, "--songs-per-arc", help="Songs per arc"),
    min_similarity: float = typer.Option(0.6, "--min-similarity", help="Minimum similarity score"),
    config_path: str = typer.Option("./config/settings.yaml", help="Path to config file")
):
    """Query for matching songs for a new track."""
    console.print("\n[bold yellow]🚧 Query command not yet implemented[/bold yellow]")
    console.print("This will be implemented in Phase 4\n")


@app.command()
def playlist_gaps(
    playlist: str = typer.Argument(..., help="Path to playlist JSON file")
):
    """Show songs that need to be generated."""
    console.print("\n[bold yellow]🚧 Playlist gaps command not yet implemented[/bold yellow]")
    console.print("This will be implemented in Phase 4\n")


@app.command()
def scaffold_track(
    track_number: int = typer.Option(..., "--track-number", "-t", help="Track number"),
    notion_url: str = typer.Option(..., "--notion-url", "-n", help="Notion document URL"),
    config_path: str = typer.Option("./config/settings.yaml", help="Path to config file")
):
    """Create track folder structure from Notion doc."""
    console.print("\n[bold yellow]🚧 Scaffold track command not yet implemented[/bold yellow]")
    console.print("This will be implemented in Phase 5\n")


@app.command()
def track_duration(
    track: Optional[int] = typer.Option(None, "--track", "-t", help="Track number"),
    current_dir: bool = typer.Option(False, "--current-dir", help="Use current directory")
):
    """Calculate total duration of songs in a track."""
    console.print("\n[bold yellow]🚧 Track duration command not yet implemented[/bold yellow]")
    console.print("This will be implemented in Phase 5\n")


@app.command()
def prepare_render(
    track: int = typer.Option(..., "--track", "-t", help="Track number"),
    config_path: str = typer.Option("./config/settings.yaml", help="Path to config file")
):
    """Prepare track for rendering (sort and organize songs)."""
    console.print("\n[bold yellow]🚧 Prepare render command not yet implemented[/bold yellow]")
    console.print("This will be implemented in Phase 5\n")


@app.command()
def post_render(
    track: int = typer.Option(..., "--track", "-t", help="Track number"),
    config_path: str = typer.Option("./config/settings.yaml", help="Path to config file")
):
    """Import new songs to bank after rendering."""
    console.print("\n[bold yellow]🚧 Post render command not yet implemented[/bold yellow]")
    console.print("This will be implemented in Phase 5\n")


@app.command()
def mark_published(
    track: int = typer.Option(..., "--track", "-t", help="Track number"),
    youtube_url: str = typer.Option(..., "--youtube-url", "-u", help="YouTube video URL"),
    config_path: str = typer.Option("./config/settings.yaml", help="Path to config file")
):
    """Mark track as published with YouTube URL."""
    console.print("\n[bold yellow]🚧 Mark published command not yet implemented[/bold yellow]")
    console.print("This will be implemented in Phase 6\n")


@app.command()
def stats(
    type: str = typer.Argument("songs", help="Type: 'songs' or 'tracks'"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of results to show"),
    config_path: str = typer.Option("./config/settings.yaml", help="Path to config file")
):
    """Show statistics about songs or tracks."""
    try:
        config = get_config(config_path)
        db = Database(config.database_path)

        if type == "songs":
            console.print("\n[bold blue]📊 Song Statistics[/bold blue]\n")

            # Basic counts
            total_songs = db.get_song_count()
            console.print(f"Total songs in database: [bold]{total_songs}[/bold]\n")

            if total_songs == 0:
                console.print("[yellow]No songs in database yet. Import some songs first![/yellow]\n")
                return

            # Most used songs
            console.print("[bold]Most Used Songs:[/bold]")
            most_used = db.get_most_used_songs(limit)
            if most_used:
                table = Table()
                table.add_column("Filename", style="cyan")
                table.add_column("Times Used", style="magenta")
                table.add_column("BPM", style="green")
                table.add_column("Arc", style="yellow")

                for song in most_used:
                    table.add_row(
                        song.filename,
                        str(song.times_used),
                        f"{song.bpm:.1f}" if song.bpm else "N/A",
                        f"Arc {song.arc_number}" if song.arc_number else "N/A"
                    )

                console.print(table)
            else:
                console.print("[yellow]No songs have been used yet[/yellow]")

            console.print()

            # Unused songs
            console.print("[bold]Unused Songs:[/bold]")
            unused = db.get_unused_songs(limit)
            if unused:
                table = Table()
                table.add_column("Filename", style="cyan")
                table.add_column("BPM", style="green")
                table.add_column("Arc", style="yellow")

                for song in unused:
                    table.add_row(
                        song.filename,
                        f"{song.bpm:.1f}" if song.bpm else "N/A",
                        f"Arc {song.arc_number}" if song.arc_number else "N/A"
                    )

                console.print(table)

            console.print()

        elif type == "tracks":
            console.print("\n[bold blue]📊 Track Statistics[/bold blue]\n")

            total_tracks = db.get_track_count()
            console.print(f"Total tracks in database: [bold]{total_tracks}[/bold]\n")

            if total_tracks == 0:
                console.print("[yellow]No tracks in database yet.[/yellow]\n")
                return

            # List all tracks
            tracks = db.get_all_tracks()
            table = Table(title="All Tracks")
            table.add_column("Number", style="cyan")
            table.add_column("Title", style="white")
            table.add_column("Status", style="magenta")
            table.add_column("Duration", style="green")

            for track in tracks:
                table.add_row(
                    str(track.track_number) if track.track_number else "N/A",
                    track.title,
                    track.status.value,
                    f"{track.duration_target} min"
                )

            console.print(table)
            console.print()

        else:
            console.print(f"\n[bold red]❌ Unknown type: {type}[/bold red]")
            console.print("Use 'songs' or 'tracks'\n")
            raise typer.Exit(code=1)

        db.close()

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]\n")
        raise typer.Exit(code=1)


@app.command()
def version():
    """Show version information."""
    from .. import __version__
    console.print(f"\n[bold]LoFi Track Manager[/bold] version [cyan]{__version__}[/cyan]\n")


if __name__ == "__main__":
    app()
