#!/bin/bash
# Bash script to copy skill directory

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: bash install-skill.sh <source> <destination>"
    exit 1
fi

source="$1"
destination="$2"

if [ -d "$destination" ]; then
    echo "Destination already exists. Overwriting..."
    rm -rf "$destination"
fi

cp -r "$source" "$destination"
echo "Successfully copied $source to $destination"
