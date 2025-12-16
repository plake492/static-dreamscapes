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
def generate_embeddings(
    force: bool = typer.Option(False, "--force", "-f", help="Regenerate all embeddings"),
    config_path: str = typer.Option("./config/settings.yaml", help="Path to config file")
):
    """Generate embeddings for all songs in the database."""
    try:
        from ..embeddings.generator import EmbeddingGenerator

        config = get_config(config_path)
        db = Database(config.database_path)

        console.print("\n[bold blue]🧠 Generating Embeddings[/bold blue]\n")

        # Get all songs
        songs = db.get_all_songs()
        console.print(f"Found {len(songs)} songs in database\n")

        if len(songs) == 0:
            console.print("[yellow]No songs found. Import some tracks first![/yellow]\n")
            return

        # Initialize generator
        generator = EmbeddingGenerator(config.embedding_model_name)
        console.print(f"Using model: [cyan]{config.embedding_model_name}[/cyan]")
        console.print(f"Embedding dimension: [cyan]{generator.dimension}[/cyan]\n")

        # Generate embeddings
        from pathlib import Path
        embeddings_dir = Path(config.embeddings_cache)
        embeddings_dir.mkdir(parents=True, exist_ok=True)

        import numpy as np
        import json
        from datetime import datetime

        embeddings = []
        song_ids = []

        with console.status("[bold green]Generating embeddings...") as status:
            for i, song in enumerate(songs, 1):
                status.update(f"[bold green]Processing {i}/{len(songs)}: {song.filename}")

                # Generate embedding
                embedding = generator.generate_for_song(song)
                embeddings.append(embedding)
                song_ids.append(song.id)

        # Save to cache
        embeddings_matrix = np.array(embeddings)
        cache_file = embeddings_dir / "embeddings.npz"

        np.savez(
            cache_file,
            embeddings=embeddings_matrix,
            song_ids=song_ids
        )

        # Save metadata
        metadata = {
            'model': config.embedding_model_name,
            'dimension': generator.dimension,
            'song_count': len(songs),
            'generated_at': datetime.now().isoformat()
        }

        metadata_file = embeddings_dir / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))

        console.print(f"\n[bold green]✅ Generated embeddings for {len(songs)} songs![/bold green]")
        console.print(f"Saved to: {cache_file}\n")

        db.close()

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]\n")
        logger.exception("Error generating embeddings")
        raise typer.Exit(1)


@app.command()
def query(
    notion_url: str = typer.Option(..., "--notion-url", "-n", help="Notion document URL for new track"),
    output: str = typer.Option("./output/playlists/playlist.json", "--output", "-o", help="Output JSON file"),
    target_duration: int = typer.Option(180, "--duration", "-d", help="Target duration in minutes"),
    songs_per_arc: int = typer.Option(11, "--songs-per-arc", help="Songs per arc"),
    min_similarity: float = typer.Option(0.6, "--min-similarity", help="Minimum similarity score"),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Number of matches per prompt"),
    config_path: str = typer.Option("./config/settings.yaml", help="Path to config file")
):
    """Query for matching songs for a new track."""
    try:
        from ..ingest.notion_parser import NotionParser
        from ..embeddings.generator import EmbeddingGenerator
        from ..embeddings.store import EmbeddingStore
        from ..query.matcher import SongMatcher
        from ..query.filters import SearchFilters
        from pathlib import Path
        import json

        config = get_config(config_path)
        db = Database(config.database_path)

        console.print("\n[bold blue]🔍 Querying for Matching Songs[/bold blue]\n")
        console.print(f"Notion URL: {notion_url}\n")

        # Parse Notion document
        console.print("[cyan]Parsing Notion document...[/cyan]")
        notion_parser = NotionParser(config.notion_api_token)
        track_metadata = notion_parser.parse_notion_doc(notion_url)

        console.print(f"Track: [bold]{track_metadata.title}[/bold]")
        console.print(f"Arcs: {len(track_metadata.arcs)}\n")

        # Load embeddings
        embeddings_dir = Path(config.embeddings_cache)
        cache_file = embeddings_dir / "embeddings.npz"

        if not cache_file.exists():
            console.print("[bold red]❌ No embeddings found![/bold red]")
            console.print("Run: [cyan]yarn generate-embeddings[/cyan] first\n")
            raise typer.Exit(1)

        console.print("[cyan]Loading embeddings...[/cyan]")

        # Load all songs and build embedding store
        all_songs = db.get_all_songs()
        generator = EmbeddingGenerator(config.embedding_model_name)
        store = EmbeddingStore(config.embeddings_cache)

        import numpy as np
        data = np.load(cache_file)

        # Map song IDs to songs
        song_map = {song.id: song for song in all_songs}

        for song_id, embedding in zip(data['song_ids'], data['embeddings']):
            if song_id in song_map:
                store.add_song(song_map[song_id], embedding)

        console.print(f"Loaded {len(store.song_map)} songs with embeddings\n")

        # Initialize matcher
        matcher = SongMatcher(
            embedding_generator=generator,
            embedding_store=store
        )

        # Query for each arc
        results = {}
        total_matches = 0

        for arc in track_metadata.arcs:
            console.print(f"[bold]Arc {arc.arc_number}: {arc.arc_name}[/bold]")

            arc_results = []

            for prompt in arc.prompts:
                matches = matcher.find_matches_for_prompt(
                    prompt=prompt,
                    arc=arc,
                    track_metadata=track_metadata,
                    count=top_k
                )

                arc_results.append({
                    'prompt_number': prompt.prompt_number,
                    'prompt_text': prompt.prompt_text,
                    'matches': [
                        {
                            'filename': m.song.filename,
                            'score': round(m.final_score, 3),
                            'similarity': round(m.similarity_score, 3),
                            'bpm': m.song.bpm,
                            'key': m.song.key,
                            'arc': m.song.arc_number,
                            'duration': round(m.song.duration_seconds) if m.song.duration_seconds else None
                        }
                        for m in matches
                    ]
                })

                total_matches += len(matches)
                console.print(f"  Prompt {prompt.prompt_number}: Found {len(matches)} matches")

            results[f"arc_{arc.arc_number}"] = arc_results
            console.print()

        # Save results
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_data = {
            'track_title': track_metadata.title,
            'notion_url': notion_url,
            'total_prompts': sum(len(arc.prompts) for arc in track_metadata.arcs),
            'total_matches': total_matches,
            'results': results
        }

        output_path.write_text(json.dumps(output_data, indent=2))

        console.print(f"[bold green]✅ Query complete![/bold green]")
        console.print(f"Total matches: {total_matches}")
        console.print(f"Results saved to: {output}\n")

        db.close()

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]\n")
        logger.exception("Error querying songs")
        raise typer.Exit(1)


@app.command()
def playlist_gaps(
    playlist: str = typer.Argument(..., help="Path to playlist JSON file"),
    min_similarity: float = typer.Option(0.6, "--min-similarity", "-m", help="Minimum acceptable similarity score")
):
    """Analyze playlist to identify prompts that need new song generation."""
    try:
        from pathlib import Path
        import json
        from rich.table import Table

        console.print("\n[bold blue]🔍 Analyzing Playlist Gaps[/bold blue]\n")

        # Load playlist JSON
        playlist_file = Path(playlist)
        if not playlist_file.exists():
            console.print(f"[bold red]❌ Playlist file not found: {playlist}[/bold red]\n")
            raise typer.Exit(1)

        with open(playlist_file) as f:
            data = json.load(f)

        console.print(f"Track: [bold]{data.get('track_title', 'Unknown')}[/bold]")
        console.print(f"Total prompts: {data.get('total_prompts', 0)}")
        console.print(f"Total matches: {data.get('total_matches', 0)}\n")

        # Analyze gaps
        gaps_by_arc = {}
        low_quality_by_arc = {}
        good_matches_by_arc = {}

        for arc_name, prompts in data.get('results', {}).items():
            gaps = []
            low_quality = []
            good_matches = []

            for prompt_data in prompts:
                prompt_num = prompt_data.get('prompt_number')
                prompt_text = prompt_data.get('prompt_text', '')
                matches = prompt_data.get('matches', [])

                # Truncate prompt text for display
                display_text = prompt_text[:60] + "..." if len(prompt_text) > 60 else prompt_text

                if not matches:
                    # No matches at all
                    gaps.append((prompt_num, display_text))
                elif matches and matches[0]['similarity'] < min_similarity:
                    # Has matches but quality is low
                    best_score = matches[0]['similarity']
                    low_quality.append((prompt_num, display_text, best_score))
                else:
                    # Good match found
                    best_score = matches[0]['similarity']
                    good_matches.append((prompt_num, best_score))

            if gaps or low_quality:
                gaps_by_arc[arc_name] = gaps
                low_quality_by_arc[arc_name] = low_quality
            good_matches_by_arc[arc_name] = good_matches

        # Display results
        total_gaps = sum(len(g) for g in gaps_by_arc.values())
        total_low_quality = sum(len(lq) for lq in low_quality_by_arc.values())
        total_good = sum(len(gm) for gm in good_matches_by_arc.values())

        # Summary table
        summary_table = Table(title="Gap Analysis Summary", show_header=True, header_style="bold cyan")
        summary_table.add_column("Category", style="white")
        summary_table.add_column("Count", justify="right", style="cyan")
        summary_table.add_column("Percentage", justify="right", style="yellow")

        total = data.get('total_prompts', 1)
        summary_table.add_row("No matches (need generation)", str(total_gaps), f"{(total_gaps/total*100):.1f}%")
        summary_table.add_row(f"Low quality (< {min_similarity:.0%})", str(total_low_quality), f"{(total_low_quality/total*100):.1f}%")
        summary_table.add_row(f"Good matches (≥ {min_similarity:.0%})", str(total_good), f"{(total_good/total*100):.1f}%")

        console.print(summary_table)
        console.print()

        # Show gaps by arc
        if total_gaps > 0:
            console.print("[bold red]❌ Prompts Needing New Generation:[/bold red]\n")
            for arc_name, gaps in gaps_by_arc.items():
                if gaps:
                    console.print(f"[bold]{arc_name}:[/bold]")
                    for prompt_num, prompt_text in gaps:
                        console.print(f"  {prompt_num}. {prompt_text}")
            console.print()

        # Show low quality matches
        if total_low_quality > 0:
            console.print(f"[bold yellow]⚠️  Low Quality Matches (< {min_similarity:.0%}):[/bold yellow]\n")
            for arc_name, low_quality in low_quality_by_arc.items():
                if low_quality:
                    console.print(f"[bold]{arc_name}:[/bold]")
                    for prompt_num, prompt_text, score in low_quality:
                        console.print(f"  {prompt_num}. {prompt_text} ([yellow]{score:.1%}[/yellow])")
            console.print()

        # Recommendation
        songs_to_generate = total_gaps + total_low_quality
        if songs_to_generate == 0:
            console.print("[bold green]✅ All prompts have good matches! No new generation needed.[/bold green]\n")
        else:
            console.print(f"[bold cyan]💡 Recommendation:[/bold cyan]")
            console.print(f"Generate approximately [bold]{songs_to_generate}[/bold] new songs")
            console.print(f"This represents {(songs_to_generate/total*100):.1f}% of the track\n")

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]\n")
        logger.exception("Error analyzing playlist gaps")
        raise typer.Exit(1)


@app.command()
def scaffold_track(
    track_number: int = typer.Option(..., "--track-number", "-t", help="Track number"),
    notion_url: str = typer.Option(..., "--notion-url", "-n", help="Notion document URL"),
    config_path: str = typer.Option("./config/settings.yaml", help="Path to config file")
):
    """Create track folder structure from Notion doc."""
    try:
        from ..ingest.notion_parser import NotionParser
        from pathlib import Path

        config = get_config(config_path)

        console.print("\n[bold blue]📁 Scaffolding Track Folder[/bold blue]\n")
        console.print(f"Track number: {track_number}")
        console.print(f"Notion URL: {notion_url}\n")

        # Parse Notion doc
        console.print("[cyan]Parsing Notion document...[/cyan]")
        notion_parser = NotionParser(config.notion_api_token)
        track_metadata = notion_parser.parse_notion_doc(notion_url)

        console.print(f"Track title: [bold]{track_metadata.title}[/bold]\n")

        # Create folder structure
        track_dir = Path(f"./Tracks/{track_number}")

        if track_dir.exists():
            console.print(f"[yellow]⚠️  Track folder already exists: {track_dir}[/yellow]")
            if not typer.confirm("Continue anyway?"):
                console.print("[red]Cancelled[/red]\n")
                return

        # Create directories
        dirs_to_create = [
            track_dir,
            track_dir / "Songs",
            track_dir / "Rendered",
            track_dir / "metadata"
        ]

        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
            console.print(f"✅ Created: {dir_path}")

        # Create metadata file
        import json
        metadata_file = track_dir / "metadata" / "track_info.json"
        metadata_content = {
            "track_number": track_number,
            "title": track_metadata.title,
            "notion_url": notion_url,
            "duration_target_minutes": track_metadata.duration_target_minutes,
            "overall_theme": track_metadata.overall_theme,
            "arcs": [
                {
                    "arc_number": arc.arc_number,
                    "arc_name": arc.arc_name,
                    "prompts": len(arc.prompts)
                }
                for arc in track_metadata.arcs
            ],
            "created_at": str(Path.cwd())
        }

        metadata_file.write_text(json.dumps(metadata_content, indent=2))
        console.print(f"✅ Created: {metadata_file}")

        # Create README
        readme_file = track_dir / "README.md"
        readme_content = f"""# Track {track_number}: {track_metadata.title}

## Overview
- **Duration Target**: {track_metadata.duration_target_minutes} minutes
- **Theme**: {track_metadata.overall_theme}
- **Notion**: [View Document]({notion_url})

## Arcs
"""
        for arc in track_metadata.arcs:
            readme_content += f"\n### Arc {arc.arc_number}: {arc.arc_name}\n"
            readme_content += f"- Prompts: {len(arc.prompts)}\n"

        readme_file.write_text(readme_content)
        console.print(f"✅ Created: {readme_file}")

        console.print(f"\n[bold green]✅ Track {track_number} scaffolded successfully![/bold green]")
        console.print(f"Location: {track_dir}\n")

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]\n")
        logger.exception("Error scaffolding track")
        raise typer.Exit(1)


@app.command()
def track_duration(
    track: Optional[int] = typer.Option(None, "--track", "-t", help="Track number"),
    songs_dir: Optional[str] = typer.Option(None, "--songs-dir", "-s", help="Songs directory"),
    config_path: str = typer.Option("./config/settings.yaml", help="Path to config file")
):
    """Calculate total duration of songs in a track."""
    try:
        from ..ingest.audio_analyzer import AudioAnalyzer
        from ..ingest.filename_parser import FilenameParser
        from pathlib import Path

        console.print("\n[bold blue]⏱️  Calculating Track Duration[/bold blue]\n")

        # Determine songs directory
        if songs_dir:
            songs_path = Path(songs_dir)
        elif track:
            songs_path = Path(f"./Tracks/{track}/Songs")
        else:
            console.print("[red]Error: Provide either --track or --songs-dir[/red]\n")
            raise typer.Exit(1)

        if not songs_path.exists():
            console.print(f"[red]Error: Directory not found: {songs_path}[/red]\n")
            raise typer.Exit(1)

        console.print(f"Scanning: {songs_path}\n")

        # Find all audio files recursively (mp3 and wav)
        audio_files = []
        audio_files.extend(songs_path.glob('**/*.mp3'))
        audio_files.extend(songs_path.glob('**/*.wav'))

        if not audio_files:
            console.print("[yellow]No audio files found (.mp3, .wav)[/yellow]\n")
            return

        console.print(f"Found {len(audio_files)} songs\n")
        console.print("[cyan]Analyzing audio files...[/cyan]")
        console.print("─" * 70)

        # Analyze durations
        analyzer = AudioAnalyzer()
        parser = FilenameParser()
        arc_durations = {}
        total_duration = 0
        file_details = []

        for file_path in sorted(audio_files):
            # Get duration
            analysis = analyzer.analyze(file_path)
            duration = analysis.duration_seconds or 0
            total_duration += duration

            # Format duration as MM:SS
            minutes = int(duration // 60)
            seconds = int(duration % 60)

            # Store file details
            file_details.append({
                'filename': file_path.name,
                'duration': duration,
                'formatted': f"{minutes:3d}:{seconds:02d}"
            })

            # Parse filename for arc grouping (optional)
            try:
                components = parser.parse(file_path.name)
                if components:
                    arc = components.arc_number
                    if arc not in arc_durations:
                        arc_durations[arc] = {'count': 0, 'duration': 0}
                    arc_durations[arc]['count'] += 1
                    arc_durations[arc]['duration'] += duration
            except:
                # Skip arc parsing if filename doesn't match pattern
                pass

        # Display individual files
        for file_info in file_details:
            console.print(f"{file_info['filename']:<50} {file_info['formatted']}")

        console.print("─" * 70)

        # Display arc summary
        if arc_durations:
            console.print()
            table = Table(title="Duration by Arc", show_header=True, header_style="bold cyan")
            table.add_column("Arc", style="cyan")
            table.add_column("Songs", justify="right", style="green")
            table.add_column("Duration", justify="right", style="yellow")

            for arc in sorted(arc_durations.keys()):
                data = arc_durations[arc]
                minutes = int(data['duration'] // 60)
                seconds = int(data['duration'] % 60)
                table.add_row(
                    f"Arc {arc}",
                    str(data['count']),
                    f"{minutes}m {seconds}s"
                )

            console.print(table)

        # Total duration
        console.print(f"\n[bold cyan]Total files:[/bold cyan] {len(audio_files)}")

        total_hours = int(total_duration // 3600)
        total_minutes = int((total_duration % 3600) // 60)
        total_seconds = int(total_duration % 60)

        console.print(f"[bold cyan]Total duration:[/bold cyan] {total_hours}h {total_minutes}m {total_seconds}s")
        console.print(f"[bold cyan]Total seconds:[/bold cyan] {int(total_duration)}s")

        # Loop calculations
        console.print(f"\n[bold yellow]Loop calculations:[/bold yellow]")
        console.print(f"  • For 15 min video: need {int((900 / total_duration) + 1)} loops")
        console.print(f"  • For 30 min video: need {int((1800 / total_duration) + 1)} loops")
        console.print(f"  • For 60 min video: need {int((3600 / total_duration) + 1)} loops")
        console.print(f"  • For 90 min video: need {int((5400 / total_duration) + 1)} loops")
        console.print(f"  • For 180 min video: need {int((10800 / total_duration) + 1)} loops")
        console.print()

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]\n")
        logger.exception("Error calculating track duration")
        raise typer.Exit(1)


@app.command()
def prepare_render(
    track: int = typer.Option(..., "--track", "-t", help="Track number"),
    playlist: str = typer.Option(..., "--playlist", "-p", help="Path to playlist JSON file"),
    copy: bool = typer.Option(True, "--copy/--move", help="Copy files (default) or move them"),
    target_duration: int = typer.Option(None, "--duration", "-d", help="Target duration in minutes (auto-selects songs)"),
    config_path: str = typer.Option("./config/settings.yaml", help="Path to config file")
):
    """Prepare track for rendering by organizing matched songs into track folder."""
    try:
        from pathlib import Path
        import json
        import shutil
        from rich.table import Table

        config = get_config(config_path)
        db = Database(config.database_path)

        console.print("\n[bold blue]🎬 Preparing Track for Render[/bold blue]\n")
        console.print(f"Track: {track}")
        console.print(f"Playlist: {playlist}\n")

        # Load playlist
        playlist_file = Path(playlist)
        if not playlist_file.exists():
            console.print(f"[bold red]❌ Playlist file not found: {playlist}[/bold red]\n")
            raise typer.Exit(1)

        with open(playlist_file) as f:
            data = json.load(f)

        # Prepare destination
        track_dir = Path(f"./Tracks/{track}")
        songs_dir = track_dir / "Songs"

        if not track_dir.exists():
            console.print(f"[yellow]Track folder doesn't exist. Creating: {track_dir}[/yellow]")
            songs_dir.mkdir(parents=True, exist_ok=True)

        console.print(f"Destination: {songs_dir}\n")

        # Collect all matched songs
        songs_to_copy = []

        if target_duration:
            # Duration-aware selection: intelligently select songs to fill target duration
            console.print(f"[cyan]Target duration: {target_duration} minutes ({target_duration * 60} seconds)[/cyan]")

            target_seconds = target_duration * 60
            current_duration = 0

            # Organize matches by arc for balanced selection
            arc_matches = {}
            for arc_name, prompts in data.get('results', {}).items():
                arc_matches[arc_name] = []
                for prompt_data in prompts:
                    prompt_num = prompt_data.get('prompt_number')
                    matches = prompt_data.get('matches', [])
                    if matches:
                        # Add all matches with metadata
                        for match in matches:
                            arc_matches[arc_name].append({
                                'match': match,
                                'prompt_num': prompt_num,
                                'arc_name': arc_name
                            })

            # Calculate how much duration per arc (equal distribution)
            num_arcs = len(arc_matches)
            duration_per_arc = target_seconds / num_arcs if num_arcs > 0 else target_seconds

            console.print(f"[cyan]Distributing ~{duration_per_arc / 60:.1f} minutes per arc[/cyan]\n")

            # Select songs for each arc
            for arc_name, matches in arc_matches.items():
                arc_duration = 0
                match_index = 0

                # Keep adding songs until we hit the arc's duration target
                while arc_duration < duration_per_arc and match_index < len(matches):
                    match_data = matches[match_index]
                    match = match_data['match']
                    prompt_num = match_data['prompt_num']

                    filename = match['filename']
                    duration = match.get('duration', 180)  # Default 3 min if unknown

                    # Find the song in database to get file path
                    song = db.get_song_by_filename(filename)
                    if song and song.file_path:
                        source_path = Path(song.file_path)
                        if source_path.exists():
                            songs_to_copy.append((source_path, filename, prompt_num, arc_name, duration))
                            arc_duration += duration
                            current_duration += duration
                        else:
                            console.print(f"[yellow]⚠️  Source file not found: {source_path}[/yellow]")

                    match_index += 1

            console.print(f"[cyan]Selected {len(songs_to_copy)} songs totaling {current_duration / 60:.1f} minutes[/cyan]\n")

        else:
            # Original behavior: take best match per prompt
            for arc_name, prompts in data.get('results', {}).items():
                for prompt_data in prompts:
                    prompt_num = prompt_data.get('prompt_number')
                    matches = prompt_data.get('matches', [])

                    if matches:
                        # Take the best match
                        best_match = matches[0]
                        filename = best_match['filename']
                        duration = best_match.get('duration', 180)

                        # Find the song in database to get file path
                        song = db.get_song_by_filename(filename)
                        if song and song.file_path:
                            source_path = Path(song.file_path)
                            if source_path.exists():
                                songs_to_copy.append((source_path, filename, prompt_num, arc_name, duration))
                            else:
                                console.print(f"[yellow]⚠️  Source file not found: {source_path}[/yellow]")

        if not songs_to_copy:
            console.print("[yellow]No songs to copy. All prompts need new generation.[/yellow]\n")
            return

        console.print(f"[cyan]Found {len(songs_to_copy)} songs to {'copy' if copy else 'move'}[/cyan]\n")

        # Copy/move files
        copied_count = 0
        operation = "Copying" if copy else "Moving"

        for source_path, filename, prompt_num, arc_name, duration in songs_to_copy:
            dest_path = songs_dir / filename

            try:
                if copy:
                    shutil.copy2(source_path, dest_path)
                else:
                    shutil.move(str(source_path), str(dest_path))

                copied_count += 1
                console.print(f"  ✓ {filename} ({arc_name}, prompt {prompt_num})")

            except Exception as e:
                console.print(f"  [red]✗ Failed to copy {filename}: {e}[/red]")

        console.print(f"\n[bold green]✅ Prepared {copied_count} songs for rendering[/bold green]")
        console.print(f"Location: {songs_dir}\n")

        # Show summary by arc
        from collections import defaultdict
        arc_counts = defaultdict(int)
        arc_durations = defaultdict(float)
        for _, _, _, arc_name, duration in songs_to_copy:
            arc_counts[arc_name] += 1
            arc_durations[arc_name] += duration

        summary_table = Table(title="Songs by Arc", show_header=True, header_style="bold cyan")
        summary_table.add_column("Arc", style="white")
        summary_table.add_column("Songs", justify="right", style="cyan")
        summary_table.add_column("Duration (min)", justify="right", style="green")

        for arc_name in sorted(arc_counts.keys()):
            duration_min = arc_durations[arc_name] / 60
            summary_table.add_row(arc_name, str(arc_counts[arc_name]), f"{duration_min:.1f}")

        console.print(summary_table)
        console.print()

        # Generate markdown file with remaining prompts
        console.print("[cyan]Generating remaining prompts document...[/cyan]")

        # Track which prompts were used
        used_prompts = set()
        for _, _, prompt_num, arc_name, _ in songs_to_copy:
            used_prompts.add((arc_name, prompt_num))

        # Build markdown content
        md_lines = [
            f"# Track {track} - Remaining Prompts",
            f"\n**Track:** {data.get('track_title', f'Track {track}')}",
            f"\n**Songs Selected:** {len(songs_to_copy)}",
            f"\n---\n"
        ]

        # Get all prompts and identify gaps
        remaining_count = 0
        for arc_name, prompts in data.get('results', {}).items():
            arc_num = arc_name.replace('arc_', '')
            arc_has_gaps = False
            arc_prompts = []

            for prompt_data in prompts:
                prompt_num = prompt_data.get('prompt_number')
                prompt_text = prompt_data.get('prompt_text', '')
                matches = prompt_data.get('matches', [])

                # Check if this prompt was used
                if (arc_name, prompt_num) not in used_prompts:
                    if not arc_has_gaps:
                        arc_prompts.append(f"\n## Arc {arc_num}\n")
                        arc_has_gaps = True

                    # Show prompt number and text
                    arc_prompts.append(f"### Prompt {prompt_num}")
                    arc_prompts.append(f"{prompt_text}\n")
                    remaining_count += 1

            if arc_has_gaps:
                md_lines.extend(arc_prompts)

        if remaining_count == 0:
            md_lines.append("\n✅ **All prompts have been filled!**\n")
        else:
            md_lines.insert(3, f"**Prompts Remaining:** {remaining_count}\n")

        # Write markdown file
        md_path = track_dir / "remaining-prompts.md"
        md_path.write_text('\n'.join(md_lines))

        console.print(f"[green]✓[/green] Created: {md_path}")
        console.print(f"[yellow]{remaining_count} prompts remaining[/yellow]\n")

        db.close()

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]\n")
        logger.exception("Error preparing render")
        raise typer.Exit(1)


@app.command()
def render(
    track: int = typer.Option(..., "--track", "-t", help="Track number"),
    duration: str = typer.Option("auto", "--duration", "-d", help="Duration: 'auto', 'test' (5min), or hours (e.g., '1', '0.5', '3')"),
    volume_boost: float = typer.Option(1.75, "--volume", "-v", help="Volume multiplier"),
    crossfade_duration: int = typer.Option(5, "--crossfade", help="Crossfade duration in seconds"),
    config_path: str = typer.Option("./config/settings.yaml", help="Path to config file")
):
    """Render track by concatenating songs with crossfades over looping background video."""
    try:
        from pathlib import Path
        from datetime import datetime
        import subprocess
        import re
        import shutil

        console.print(f"\n[bold blue]🎬 Rendering Track {track}[/bold blue]\n")

        # Get track info from database
        track_title = None
        output_filename = None
        try:
            db = Database()
            cursor = db.conn.cursor()
            # Try to find by track_number first, then by id
            cursor.execute("SELECT title, output_filename FROM tracks WHERE track_number = ? OR id = ?", (track, str(track)))
            result = cursor.fetchone()
            if result:
                track_title = result[0]
                output_filename = result[1]
                console.print(f"[cyan]Track title:[/cyan] {track_title}")
                if output_filename:
                    console.print(f"[cyan]Output filename:[/cyan] {output_filename}\n")
                else:
                    console.print()
            db.close()
        except Exception as e:
            logger.warning(f"Could not fetch track info: {e}")

        # Setup paths
        track_dir = Path(f"Tracks/{track}")
        bg_video = track_dir / "Video" / f"{track}.mp4"
        songs_dir = track_dir / "Songs"
        image_dir = track_dir / "Image"

        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"Rendered/{track}/output_{timestamp}")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create filename from database field or sanitized title
        if output_filename:
            # Use the filename from Notion doc (already formatted)
            # Ensure it ends with .mp4
            if not output_filename.endswith('.mp4'):
                output_filename = f"{output_filename}.mp4"
            output_file = output_dir / output_filename
        elif track_title:
            # Fallback: Sanitize title for filename
            sanitized_title = re.sub(r'[^\w\s-]', '', track_title)
            sanitized_title = re.sub(r'[-\s]+', '_', sanitized_title).strip('_')
            output_file = output_dir / f"{sanitized_title}.mp4"
        else:
            output_file = output_dir / "output.mp4"

        # Validate inputs
        if not bg_video.exists():
            console.print(f"[red]❌ Background video not found: {bg_video}[/red]\n")
            raise typer.Exit(1)

        if not songs_dir.exists():
            console.print(f"[red]❌ Songs directory not found: {songs_dir}[/red]\n")
            raise typer.Exit(1)

        # Find all MP3 files
        mp3_files = sorted(songs_dir.glob("*.mp3"))

        if not mp3_files:
            console.print(f"[yellow]No MP3 files found in {songs_dir}[/yellow]\n")
            raise typer.Exit(1)

        console.print(f"[cyan]Background video:[/cyan] {bg_video}")
        console.print(f"[cyan]Songs directory:[/cyan] {songs_dir}")
        console.print(f"[cyan]Found {len(mp3_files)} songs[/cyan]\n")

        # Get duration of each song using ffprobe
        console.print("[cyan]Analyzing song durations...[/cyan]")
        song_durations = []
        total_songs_duration = 0

        for song_file in mp3_files:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', str(song_file)],
                capture_output=True,
                text=True
            )
            dur = float(result.stdout.strip())
            dur_int = int(dur)
            song_durations.append(dur_int)
            total_songs_duration += dur_int

        # Calculate target duration
        if duration == "test":
            target_duration = 300  # 5 minutes
            console.print(f"[green]Duration: 5 minutes (test mode)[/green]")
        elif duration == "auto":
            target_duration = total_songs_duration
            hours = target_duration // 3600
            minutes = (target_duration % 3600) // 60
            seconds = target_duration % 60
            console.print(f"[green]Duration: {hours}h {minutes}m {seconds}s (total songs duration)[/green]")
        else:
            try:
                hours_float = float(duration)
                target_duration = int(hours_float * 3600)
                console.print(f"[green]Duration: {hours_float} hours ({target_duration} seconds)[/green]")
            except ValueError:
                console.print(f"[red]❌ Invalid duration: {duration}[/red]")
                console.print("Use 'auto', 'test', or a number (hours)")
                raise typer.Exit(1)

        # Calculate sequence duration and repeats
        total_sequence_duration = sum(song_durations) - (len(song_durations) - 1) * crossfade_duration
        num_repeats = (target_duration // total_sequence_duration) + 2

        console.print(f"[cyan]Sequence duration: {total_sequence_duration}s[/cyan]")
        console.print(f"[cyan]Repeating sequence {num_repeats} times[/cyan]\n")

        # Build ffmpeg command
        console.print("[cyan]Building ffmpeg command...[/cyan]")

        ffmpeg_args = [
            'ffmpeg', '-y',
            '-stream_loop', '-1',
            '-i', str(bg_video)
        ]

        # Add each song as input
        for song in mp3_files:
            ffmpeg_args.extend(['-i', str(song)])

        # Build filter_complex
        filter_parts = []

        # Apply volume boost to all songs for all repeats
        for repeat in range(num_repeats):
            for i, song in enumerate(mp3_files):
                stream_index = i + 1
                filter_parts.append(
                    f"[{stream_index}:a]volume={volume_boost},"
                    f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo"
                    f"[a{stream_index}_r{repeat}]"
                )

        # Chain crossfades
        previous_label = "a1_r0"
        segment_count = 0

        for repeat in range(num_repeats):
            for i in range(len(mp3_files)):
                stream_index = i + 1

                if segment_count == 0:
                    segment_count += 1
                    continue

                current_input = f"a{stream_index}_r{repeat}"
                crossfade_label = f"xf{segment_count}"

                filter_parts.append(
                    f"[{previous_label}][{current_input}]"
                    f"acrossfade=d={crossfade_duration}:c1=tri:c2=tri"
                    f"[{crossfade_label}]"
                )

                previous_label = crossfade_label
                segment_count += 1

        # Final trim and fades
        fadeout_start = target_duration - 10
        filter_parts.append(
            f"[{previous_label}]atrim=0:{target_duration},"
            f"afade=t=in:st=0:d=3,"
            f"afade=t=out:st={fadeout_start}:d=10"
            f"[a]"
        )

        # Video scaling
        filter_parts.append(
            "[0:v]scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p[v]"
        )

        filter_complex = ";".join(filter_parts)

        ffmpeg_args.extend([
            '-filter_complex', filter_complex,
            '-map', '[v]',
            '-map', '[a]',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-t', str(target_duration),
            str(output_file)
        ])

        # Save command and filter for debugging
        (output_dir / "ffmpeg_command.txt").write_text(' '.join(ffmpeg_args))
        (output_dir / "filter_complex.txt").write_text(filter_complex)

        console.print(f"[green]✓[/green] Saved ffmpeg command to {output_dir}/ffmpeg_command.txt")
        console.print(f"[green]✓[/green] Saved filter_complex to {output_dir}/filter_complex.txt\n")

        # Execute ffmpeg
        console.print("[bold yellow]🎥 Rendering... (this may take a while)[/bold yellow]\n")

        result = subprocess.run(ffmpeg_args, capture_output=False)

        if result.returncode == 0:
            console.print(f"\n[bold green]✅ Render complete![/bold green]")
            console.print(f"[cyan]Output:[/cyan] {output_file}\n")

            # Copy Image folder to output directory
            if image_dir.exists():
                output_image_dir = output_dir / "Image"
                try:
                    shutil.copytree(image_dir, output_image_dir)
                    console.print(f"[green]✓[/green] Copied Image folder to {output_image_dir}")
                except Exception as e:
                    logger.warning(f"Could not copy Image folder: {e}")
                    console.print(f"[yellow]⚠[/yellow] Could not copy Image folder: {e}")
            else:
                console.print(f"[yellow]⚠[/yellow] No Image folder found at {image_dir}")
        else:
            console.print(f"\n[bold red]❌ Render failed with exit code {result.returncode}[/bold red]\n")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]\n")
        logger.exception("Error rendering track")
        raise typer.Exit(1)


@app.command()
def post_render(
    track: int = typer.Option(..., "--track", "-t", help="Track number"),
    rendered_dir: Optional[str] = typer.Option(None, "--rendered-dir", "-r", help="Rendered songs directory (default: Tracks/{N}/Rendered)"),
    config_path: str = typer.Option("./config/settings.yaml", help="Path to config file")
):
    """Import rendered songs back to the database for future reuse."""
    try:
        from pathlib import Path
        from ..ingest.audio_analyzer import AudioAnalyzer
        from ..ingest.filename_parser import FilenameParser

        config = get_config(config_path)
        db = Database(config.database_path)

        console.print("\n[bold blue]📥 Importing Rendered Songs[/bold blue]\n")
        console.print(f"Track: {track}\n")

        # Determine rendered directory
        if rendered_dir:
            rendered_path = Path(rendered_dir)
        else:
            rendered_path = Path(f"./Tracks/{track}/Rendered")

        if not rendered_path.exists():
            console.print(f"[bold red]❌ Rendered directory not found: {rendered_path}[/bold red]\n")
            console.print("Make sure you've rendered the track first.\n")
            raise typer.Exit(1)

        console.print(f"Scanning: {rendered_path}\n")

        # Find all audio files
        audio_extensions = ['.mp3', '.wav', '.m4a', '.flac']
        audio_files = []
        for ext in audio_extensions:
            audio_files.extend(rendered_path.glob(f"*{ext}"))

        if not audio_files:
            console.print("[yellow]No audio files found in rendered directory.[/yellow]\n")
            return

        console.print(f"Found {len(audio_files)} audio files\n")

        # Process each file
        analyzer = AudioAnalyzer()
        parser = FilenameParser()
        imported_count = 0
        skipped_count = 0

        for file_path in audio_files:
            filename = file_path.name

            # Check if already in database
            existing = db.get_song_by_filename(filename)
            if existing:
                console.print(f"  [yellow]⊘ {filename} (already in database)[/yellow]")
                skipped_count += 1
                continue

            try:
                # Parse filename
                parsed = parser.parse(filename)
                if not parsed:
                    console.print(f"  [red]✗ {filename} (invalid filename format)[/red]")
                    continue

                # Analyze audio
                analysis = analyzer.analyze(file_path)

                # Create song model
                from ..models import Song

                song = Song(
                    filename=filename,
                    source_path=str(file_path.absolute()),
                    arc_number=parsed.arc,
                    prompt_number=parsed.prompt,
                    song_number=parsed.song,
                    order=parsed.order,
                    bpm=analysis.bpm,
                    key=analysis.key,
                    duration_seconds=analysis.duration_seconds,
                    usage_count=0
                )

                # Add to database
                db.add_song(song)
                imported_count += 1
                console.print(f"  ✓ {filename} (Arc {song.arc_number}, BPM: {song.bpm:.1f})")

            except Exception as e:
                console.print(f"  [red]✗ {filename} (error: {e})[/red]")

        console.print(f"\n[bold green]✅ Imported {imported_count} new songs[/bold green]")
        if skipped_count > 0:
            console.print(f"Skipped {skipped_count} existing songs\n")

        # Suggest regenerating embeddings
        if imported_count > 0:
            console.print("[cyan]💡 Next step: Regenerate embeddings[/cyan]")
            console.print("   [dim]yarn generate-embeddings[/dim]\n")

        db.close()

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]\n")
        logger.exception("Error importing rendered songs")
        raise typer.Exit(1)


@app.command()
def mark_published(
    track: int = typer.Option(..., "--track", "-t", help="Track number"),
    youtube_url: str = typer.Option(..., "--youtube-url", "-u", help="YouTube video URL"),
    published_date: Optional[str] = typer.Option(None, "--date", "-d", help="Published date (YYYY-MM-DD, default: today)"),
    config_path: str = typer.Option("./config/settings.yaml", help="Path to config file")
):
    """Mark track as published with YouTube URL and increment usage counts."""
    try:
        from pathlib import Path
        from datetime import datetime
        import json

        config = get_config(config_path)
        db = Database(config.database_path)

        console.print("\n[bold blue]📺 Marking Track as Published[/bold blue]\n")
        console.print(f"Track: {track}")
        console.print(f"YouTube URL: {youtube_url}\n")

        # Parse or use today's date
        if published_date:
            try:
                pub_date = datetime.strptime(published_date, "%Y-%m-%d")
            except ValueError:
                console.print("[red]Invalid date format. Use YYYY-MM-DD[/red]\n")
                raise typer.Exit(1)
        else:
            pub_date = datetime.now()

        # Get track from database
        track_record = db.get_track_by_number(track)
        if not track_record:
            console.print(f"[red]Track {track} not found in database.[/red]")
            console.print("[yellow]Make sure you've imported the track first.[/yellow]\n")
            raise typer.Exit(1)

        # Update track with YouTube URL and published date
        db.mark_track_published(
            track_id=track_record.id,
            youtube_url=youtube_url,
            published_date=pub_date
        )

        console.print(f"[green]✓ Updated track record[/green]")

        # Get all songs from this track and increment their usage counts
        track_dir = Path(f"./Tracks/{track}/Songs")
        if track_dir.exists():
            audio_extensions = ['.mp3', '.wav', '.m4a', '.flac']
            audio_files = []
            for ext in audio_extensions:
                audio_files.extend(track_dir.glob(f"*{ext}"))

            updated_songs = 0
            for audio_file in audio_files:
                filename = audio_file.name
                song = db.get_song_by_filename(filename)
                if song:
                    db.increment_song_usage(song.id)
                    updated_songs += 1

            console.print(f"[green]✓ Incremented usage count for {updated_songs} songs[/green]\n")
        else:
            console.print(f"[yellow]⚠️  Songs directory not found: {track_dir}[/yellow]")
            console.print("[yellow]Usage counts not updated[/yellow]\n")

        # Save metadata file
        track_metadata_dir = Path(f"./Tracks/{track}/metadata")
        track_metadata_dir.mkdir(parents=True, exist_ok=True)

        metadata_file = track_metadata_dir / "published.json"
        metadata = {
            "track_number": track,
            "youtube_url": youtube_url,
            "published_date": pub_date.strftime("%Y-%m-%d"),
            "marked_at": datetime.now().isoformat()
        }

        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        console.print(f"[green]✓ Saved metadata: {metadata_file}[/green]\n")

        console.print("[bold green]✅ Track marked as published successfully![/bold green]\n")

        # Show summary
        from rich.table import Table
        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Field", style="cyan")
        summary_table.add_column("Value", style="white")

        summary_table.add_row("Track", str(track))
        summary_table.add_row("YouTube", youtube_url)
        summary_table.add_row("Published", pub_date.strftime("%Y-%m-%d"))
        summary_table.add_row("Songs Used", str(updated_songs) if track_dir.exists() else "N/A")

        console.print(summary_table)
        console.print()

        db.close()

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]\n")
        logger.exception("Error marking track as published")
        raise typer.Exit(1)


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
def batch_import(
    folder_id: str = typer.Option(..., "--folder-id", "-f", help="Notion folder/page ID containing track pages"),
    base_dir: str = typer.Option("./Tracks", "--base-dir", "-d", help="Base directory for track folders"),
    skip_existing: bool = typer.Option(True, "--skip-existing/--reimport", help="Skip tracks already in database"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
    config_path: str = typer.Option("./config/settings.yaml", help="Path to config file")
):
    """Batch import all tracks from a Notion folder."""
    try:
        from notion_client import Client
        import re
        from rich.progress import Progress, SpinnerColumn, TextColumn

        config = get_config(config_path)
        db = Database(config.database_path)

        console.print("\n[bold blue]📦 Batch Import from Notion Folder[/bold blue]\n")
        console.print(f"Folder ID: {folder_id}")
        console.print(f"Base directory: {base_dir}\n")

        # Initialize Notion client
        client = Client(auth=config.notion_api_token)

        # Get child pages from folder
        console.print("[cyan]Fetching track pages from Notion...[/cyan]")
        blocks = client.blocks.children.list(block_id=folder_id)

        # Find all track pages
        track_pages = []
        for block in blocks['results']:
            if block['type'] == 'child_page':
                title = block['child_page']['title']
                page_id = block['id']

                # Check if it starts with "Track"
                if title.startswith('Track'):
                    # Extract track number
                    match = re.search(r'Track\s+(\d+)', title)
                    track_num = int(match.group(1)) if match else None

                    if track_num:
                        track_pages.append({
                            'title': title,
                            'id': page_id,
                            'number': track_num,
                            'url': f"https://www.notion.so/{page_id.replace('-', '')}"
                        })

        # Sort by track number
        track_pages.sort(key=lambda x: x['number'])

        console.print(f"[green]Found {len(track_pages)} track pages[/green]\n")

        if not track_pages:
            console.print("[yellow]No track pages found in folder.[/yellow]\n")
            return

        # Show tracks found
        tracks_table = Table(title="Tracks Found", show_header=True, header_style="bold cyan")
        tracks_table.add_column("Track", style="cyan", width=8)
        tracks_table.add_column("Title", style="white")
        tracks_table.add_column("Songs Dir", style="dim")

        for track in track_pages:
            songs_dir = f"{base_dir}/{track['number']}/Songs"
            tracks_table.add_row(
                str(track['number']),
                track['title'][:60] + "..." if len(track['title']) > 60 else track['title'],
                songs_dir
            )

        console.print(tracks_table)
        console.print()

        # Confirm before proceeding
        if not yes and not typer.confirm("Proceed with batch import?"):
            console.print("[yellow]Cancelled[/yellow]\n")
            return

        # Import each track
        from ..ingest.metadata_extractor import MetadataExtractor
        from ..ingest.notion_parser import NotionParser
        from ..ingest.audio_analyzer import AudioAnalyzer

        # Initialize components
        notion_parser = NotionParser()
        audio_analyzer = AudioAnalyzer()
        extractor = MetadataExtractor(db, notion_parser, audio_analyzer)

        imported_count = 0
        skipped_count = 0
        error_count = 0

        for i, track_info in enumerate(track_pages, 1):
            track_num = track_info['number']
            track_title = track_info['title']
            notion_url = track_info['url']

            console.print(f"\n[bold cyan]({i}/{len(track_pages)})[/bold cyan] Track {track_num}: {track_title[:50]}...")

            # Check if already imported
            if skip_existing:
                existing = db.get_track_by_notion_url(notion_url)
                if existing:
                    console.print(f"  [yellow]⊘ Already imported[/yellow]")
                    skipped_count += 1
                    continue

            # Find songs directory
            songs_dir = Path(base_dir) / str(track_num) / "Songs"

            if not songs_dir.exists():
                console.print(f"  [red]✗ Songs directory not found: {songs_dir}[/red]")
                error_count += 1
                continue

            # Import
            try:
                track, songs = extractor.import_track_from_notion(
                    notion_url=notion_url,
                    songs_dir=songs_dir,
                    force_reanalyze=False
                )

                console.print(f"  [green]✓ Imported {len(songs)} songs[/green]")
                imported_count += 1

            except Exception as e:
                console.print(f"  [red]✗ Error: {str(e)[:100]}[/red]")
                logger.exception(f"Failed to import track {track_num}")
                error_count += 1

        # Summary
        console.print("\n[bold]Batch Import Summary[/bold]")
        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Status", style="cyan")
        summary_table.add_column("Count", justify="right", style="white")

        summary_table.add_row("✓ Imported", str(imported_count))
        summary_table.add_row("⊘ Skipped", str(skipped_count))
        summary_table.add_row("✗ Errors", str(error_count))
        summary_table.add_row("Total", str(len(track_pages)))

        console.print(summary_table)
        console.print()

        if imported_count > 0:
            console.print("[cyan]💡 Next step: Regenerate embeddings[/cyan]")
            console.print("   [dim]yarn generate-embeddings[/dim]\n")

        db.close()

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]\n")
        logger.exception("Error in batch import")
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    from .. import __version__
    console.print(f"\n[bold]LoFi Track Manager[/bold] version [cyan]{__version__}[/cyan]\n")


if __name__ == "__main__":
    app()
