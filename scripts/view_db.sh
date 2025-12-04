#!/bin/bash
# Database viewer helper script

DB_PATH="data/tracks.db"

case "$1" in
    "tables")
        sqlite3 $DB_PATH '.tables'
        ;;
    "songs")
        sqlite3 $DB_PATH -header -column \
            'SELECT filename, arc_number, prompt_number, bpm, key,
                    CAST(duration_seconds AS INT) as duration
             FROM songs
             ORDER BY arc_number, prompt_number
             LIMIT 20;'
        ;;
    "tracks")
        sqlite3 $DB_PATH -header -column \
            'SELECT title, duration_target, status, created_at
             FROM tracks;'
        ;;
    "arc")
        if [ -z "$2" ]; then
            echo "Usage: ./scripts/view_db.sh arc <arc_number>"
            exit 1
        fi
        sqlite3 $DB_PATH -header -column \
            "SELECT filename, prompt_number, bpm, key, prompt_text
             FROM songs
             WHERE arc_number = $2
             ORDER BY prompt_number;"
        ;;
    "stats")
        echo "=== Database Statistics ==="
        echo ""
        echo "Total songs:"
        sqlite3 $DB_PATH 'SELECT COUNT(*) FROM songs;'
        echo ""
        echo "Songs per arc:"
        sqlite3 $DB_PATH -header -column \
            'SELECT arc_number, COUNT(*) as count
             FROM songs
             GROUP BY arc_number;'
        echo ""
        echo "Total tracks:"
        sqlite3 $DB_PATH 'SELECT COUNT(*) FROM tracks;'
        ;;
    "shell")
        sqlite3 $DB_PATH
        ;;
    *)
        echo "Database Viewer"
        echo ""
        echo "Usage: ./scripts/view_db.sh <command>"
        echo ""
        echo "Commands:"
        echo "  tables     - List all tables"
        echo "  songs      - View all songs (first 20)"
        echo "  tracks     - View all tracks"
        echo "  arc <N>    - View songs in specific arc"
        echo "  stats      - Show database statistics"
        echo "  shell      - Open SQLite shell"
        echo ""
        echo "Examples:"
        echo "  ./scripts/view_db.sh songs"
        echo "  ./scripts/view_db.sh arc 1"
        echo "  ./scripts/view_db.sh stats"
        ;;
esac
