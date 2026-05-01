#!/bin/bash
# Bash script to uninstall/remove a skill directory

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: bash uninstall-skill.sh <destination> <skill_name>"
    echo "Example: bash uninstall-skill.sh ~/.agents/skills write-paper-notes"
    exit 1
fi

destination="$1"
skill_name="$2"
skill_path="$destination/$skill_name"

if [ -d "$skill_path" ]; then
    echo "Removing skill '$skill_name' from $destination..."
    rm -rf "$skill_path"
    echo "Successfully removed $skill_path"
else
    echo "Skill not found: $skill_path"
    exit 1
fi
