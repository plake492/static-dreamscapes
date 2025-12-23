#!/usr/bin/env python3
"""
Database migration: Add usage tracking fields to songs table.

Adds:
- last_used_track_id: Track ID where song was last used
- last_used_at: Timestamp of last usage
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.table import Table

console = Console()


def check_columns_exist(cursor: sqlite3.Cursor) -> dict:
    """Check which new columns already exist."""
    cursor.execute("PRAGMA table_info(songs)")
    columns = {row[1] for row in cursor.fetchall()}

    return {
        'last_used_track_id': 'last_used_track_id' in columns,
        'last_used_at': 'last_used_at' in columns
    }


def migrate_database(db_path: str, dry_run: bool = False):
    """Add usage tracking fields to songs table."""

    console.print(f"\n[bold blue]🔄 Database Migration: Add Usage Tracking Fields[/bold blue]\n")
    console.print(f"Database: {db_path}")
    console.print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}\n")

    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
    except Exception as e:
        console.print(f"[bold red]❌ Failed to connect to database: {e}[/bold red]")
        return False

    # Check current state
    existing = check_columns_exist(cursor)

    table = Table(title="Migration Plan")
    table.add_column("Field", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Action", style="magenta")

    migrations_needed = []

    # Check last_used_track_id
    if existing['last_used_track_id']:
        table.add_row("last_used_track_id", "TEXT", "EXISTS", "Skip")
    else:
        table.add_row("last_used_track_id", "TEXT", "MISSING", "Add column")
        migrations_needed.append(
            "ALTER TABLE songs ADD COLUMN last_used_track_id TEXT"
        )

    # Check last_used_at
    if existing['last_used_at']:
        table.add_row("last_used_at", "TIMESTAMP", "EXISTS", "Skip")
    else:
        table.add_row("last_used_at", "TIMESTAMP", "MISSING", "Add column")
        migrations_needed.append(
            "ALTER TABLE songs ADD COLUMN last_used_at TIMESTAMP"
        )

    console.print(table)
    console.print()

    # Execute migrations
    if not migrations_needed:
        console.print("[bold green]✅ All fields already exist. No migration needed.[/bold green]\n")
        conn.close()
        return True

    if dry_run:
        console.print("[bold yellow]📋 DRY RUN - SQL statements that would be executed:[/bold yellow]\n")
        for sql in migrations_needed:
            console.print(f"  {sql}")
        console.print()
        console.print("[dim]Run without --dry-run to apply changes[/dim]\n")
        conn.close()
        return True

    # Apply migrations
    try:
        console.print("[bold yellow]⚙️  Applying migrations...[/bold yellow]\n")

        for i, sql in enumerate(migrations_needed, 1):
            console.print(f"  [{i}/{len(migrations_needed)}] {sql}")
            cursor.execute(sql)

        conn.commit()
        console.print()
        console.print("[bold green]✅ Migration completed successfully![/bold green]\n")

        # Verify
        console.print("[bold blue]🔍 Verifying changes...[/bold blue]\n")
        after_migration = check_columns_exist(cursor)

        verify_table = Table()
        verify_table.add_column("Field", style="cyan")
        verify_table.add_column("Status", style="green")

        verify_table.add_row("last_used_track_id", "✅ Exists" if after_migration['last_used_track_id'] else "❌ Missing")
        verify_table.add_row("last_used_at", "✅ Exists" if after_migration['last_used_at'] else "❌ Missing")

        console.print(verify_table)
        console.print()

        # Show sample data
        cursor.execute("SELECT COUNT(*) FROM songs")
        song_count = cursor.fetchone()[0]
        console.print(f"Total songs in database: [bold]{song_count}[/bold]")
        console.print(f"All songs now have usage tracking fields initialized to NULL\n")

        return True

    except Exception as e:
        console.print(f"[bold red]❌ Migration failed: {e}[/bold red]\n")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Migrate database to add usage tracking fields")
    parser.add_argument(
        "--db-path",
        default="./data/tracks.db",
        help="Path to database file (default: ./data/tracks.db)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them"
    )

    args = parser.parse_args()

    # Check if database exists
    db_path = Path(args.db_path)
    if not db_path.exists():
        console.print(f"[bold red]❌ Database not found: {args.db_path}[/bold red]\n")
        sys.exit(1)

    # Run migration
    success = migrate_database(str(db_path), dry_run=args.dry_run)

    sys.exit(0 if success else 1)
