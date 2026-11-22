#!/bin/bash
map_file="D:/memory/dynamics365-fo-developer-handbook/scripts/renumber_map.txt"
input_file="D:/memory/dynamics365-fo-developer-handbook/d365-learning-guide.md"
output_file="D:/memory/dynamics365-fo-developer-handbook/d365-learning-guide-new.md"

# Copy content
cp "$input_file" "$output_file"

# Read map file and perform replacements
while IFS=' -> ' read -r old new; do
    # Skip empty lines
    [[ -z "$old" ]] && continue

    # Escape dots for regex
    old_escaped=$(echo "$old" | sed 's/\./\\./g')

    # Replace occurrences in text (headings and references)
    # Using 's/Chapter '$old_escaped'/'Chapter '$new'/g' for references
    # Using 's/^## '$old_escaped'/'## '$new'/g' for headings

    # We need to handle variations: "Chapter 1.1", "1.1 ", "Chapter 1.1" etc.
    # The proposal used "1.1-1.2" style.

    # Perform global replacement
    sed -i "s/\b$old\b/$new/g" "$output_file"
done < "$map_file"
