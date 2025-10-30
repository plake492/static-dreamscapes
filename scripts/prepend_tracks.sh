#!/bin/bash

# Script to prepend files in a folder with a custom prefix
# Files will be renamed to include the prefix at the beginning

# Check if required arguments are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <folder_path> <prefix> [--dry-run]"
    echo "Examples:"
    echo "  $0 Tracks/5/Songs 'LoFi_'               # Prepend 'LoFi_' to all files"
    echo "  $0 songs/Analog-1 'Chill-' --dry-run    # Preview changes without renaming"
    echo "  $0 Tracks/3/Songs 'Mix_01_'             # Prepend 'Mix_01_' to all files"
    echo "  $0 . 'Test_'                           # Prepend to files in current directory"
    echo ""
    echo "Folder path should be relative to project root"
    exit 1
fi

FOLDER="$1"
PREFIX="$2"
DRY_RUN=false

# Check for dry-run flag
if [ "$3" = "--dry-run" ] || [ "$3" = "-n" ]; then
    DRY_RUN=true
fi

# Validate that prefix is not empty
if [ -z "$PREFIX" ]; then
    echo "Error: Prefix cannot be empty"
    echo "Usage: $0 <folder_path> <prefix> [--dry-run]"
    exit 1
fi

# Check if folder exists
if [ ! -d "$FOLDER" ]; then
    echo "Error: Folder not found: $FOLDER"
    echo "Make sure the path is correct and relative to the project root"
    exit 1
fi

echo "Prepending files in: $FOLDER"
echo "Prefix: '$PREFIX'"
if [ "$DRY_RUN" = true ]; then
    echo "DRY RUN MODE - No files will be renamed"
fi
echo "-----------------------------------"

# Initialize counter
file_count=0
renamed_count=0

# Process all files in the directory
for filepath in "$FOLDER"/*; do
    # Skip if not a file
    if [ ! -f "$filepath" ]; then
        continue
    fi
    
    filename=$(basename "$filepath")
    directory=$(dirname "$filepath")
    
    # Skip if filename already starts with the prefix
    if [[ "$filename" == "$PREFIX"* ]]; then
        echo "Skipping (already has prefix): $filename"
        file_count=$((file_count + 1))
        continue
    fi
    
    # Create new filename with prefix
    new_filename="${PREFIX}${filename}"
    new_filepath="${directory}/${new_filename}"
    
    file_count=$((file_count + 1))
    
    if [ "$DRY_RUN" = true ]; then
        echo "Would rename: $filename -> $new_filename"
    else
        # Check if target filename already exists
        if [ -e "$new_filepath" ]; then
            echo "Warning: Target file already exists, skipping: $new_filename"
        else
            mv "$filepath" "$new_filepath"
            if [ $? -eq 0 ]; then
                echo "Renamed: $filename -> $new_filename"
                renamed_count=$((renamed_count + 1))
            else
                echo "Error: Failed to rename $filename"
            fi
        fi
    fi
done

echo "-----------------------------------"
if [ "$DRY_RUN" = true ]; then
    echo "Preview complete. Found $file_count files."
    echo "Run without --dry-run to actually rename files."
else
    echo "Renaming complete. Processed $file_count files, renamed $renamed_count files."
fi