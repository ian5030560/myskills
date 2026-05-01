#!/bin/bash
# Bash script to copy skill directory

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: bash install-skill.sh <source> <destination> [skill_name]"
    echo "Example: bash install-skill.sh /path/to/write-paper-notes ~/.agents/skills write-paper-notes"
    exit 1
fi

source="$1"
destination="$2"
skill_name="${3:-$(basename "$source")}"  # Use $3 or derive from source folder name

dest_path="$destination/$skill_name"

if [ -d "$dest_path" ]; then
    echo "Destination already exists. Overwriting..."
    rm -rf "$dest_path"
fi

cp -r "$source" "$dest_path"
echo "Successfully installed $skill_name to $destination"
