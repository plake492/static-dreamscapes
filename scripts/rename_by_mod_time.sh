#!/bin/bash

# Script to rename files in a folder with numbers prepended based on modification date
# Files are numbered starting from 01, with oldest files first

# Check if folder argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <folder_path> [--dry-run]"
    echo "Examples:"
    echo "  $0 tracks/5/songs"
    echo "  $0 songs/Analog-1 --dry-run  (to preview changes without renaming)"
    echo "  $0 tracks/3/songs"
    echo "  $0 . --dry-run               (current directory, preview mode)"
    echo ""
    echo "Folder path should be relative to project root"
    exit 1
fi

FOLDER="$1"
DRY_RUN=false

# Check for dry-run flag
if [ "$2" = "--dry-run" ] || [ "$2" = "-n" ]; then
    DRY_RUN=true
fi

# Check if folder exists
if [ ! -d "$FOLDER" ]; then
    echo "Error: Folder not found: $FOLDER"
    echo "Make sure the path is correct and relative to the project root"
    exit 1
fi

echo "Analyzing files in: $FOLDER"
if [ "$DRY_RUN" = true ]; then
    echo "DRY RUN MODE - No files will be renamed"
fi
echo "-----------------------------------"

# Create temporary file to store file info
temp_file=$(mktemp)

# Get all files (not directories) with their modification times
find "$FOLDER" -maxdepth 1 -type f -exec stat -f "%m %N" {} \; | sort -n > "$temp_file"

# Check if any files were found
if [ ! -s "$temp_file" ]; then
    echo "No files found in the specified folder"
    rm -f "$temp_file"
    exit 0
fi

# Count total files to determine padding
total_files=$(wc -l < "$temp_file")
# Use minimum of 2 digits, but expand if needed for larger collections
if [ "$total_files" -lt 100 ]; then
    padding=2
elif [ "$total_files" -lt 1000 ]; then
    padding=3
else
    padding=4
fi

# Initialize counter
counter=1

# Process each file
while IFS=' ' read -r timestamp filepath; do
    # Get just the filename without path
    filename=$(basename "$filepath")
    directory=$(dirname "$filepath")
    
    # Skip if filename already starts with a number pattern (e.g., "01_", "001-", etc.)
    if [[ "$filename" =~ ^[0-9]+[_\-\.\ ] ]]; then
        echo "Skipping (already numbered): $filename"
        counter=$((counter + 1))
        continue
    fi
    
    # Create new filename with padded counter
    printf -v padded_counter "%0${padding}d" "$counter"
    new_filename="${padded_counter}_${filename}"
    new_filepath="${directory}/${new_filename}"
    
    # Get file modification date for display
    mod_date=$(date -r "$timestamp" "+%Y-%m-%d %H:%M:%S")
    
    if [ "$DRY_RUN" = true ]; then
        echo "Would rename: $filename -> $new_filename (Modified: $mod_date)"
    else
        # Check if target filename already exists
        if [ -e "$new_filepath" ]; then
            echo "Warning: Target file already exists, skipping: $new_filename"
        else
            mv "$filepath" "$new_filepath"
            if [ $? -eq 0 ]; then
                echo "Renamed: $filename -> $new_filename (Modified: $mod_date)"
            else
                echo "Error: Failed to rename $filename"
            fi
        fi
    fi
    
    counter=$((counter + 1))
done < "$temp_file"

# Clean up
rm -f "$temp_file"

echo "-----------------------------------"
if [ "$DRY_RUN" = true ]; then
    echo "Preview complete. Run without --dry-run to actually rename files."
else
    echo "Renaming complete. Processed $((counter - 1)) files."
fi