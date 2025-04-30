#!/bin/bash

# Path to your .env file
ENV_FILE=".env"

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: .env file not found!"
    exit 1
fi

echo "🚀 Unsetting ALL variables mentioned in $ENV_FILE (commented or not)..."

# Read each line
while IFS= read -r line || [ -n "$line" ]; do
    # Remove leading "#" if present (remove comment)
    clean_line=$(echo "$line" | sed 's/^[#]*//')

    # Skip empty lines
    if [[ -z "$clean_line" ]]; then
        continue
    fi

    # Extract variable name (everything before "=")
    var_name=$(echo "$clean_line" | cut -d '=' -f 1 | xargs)

    # Unset the variable if it has a valid name
    if [[ -n "$var_name" ]]; then
        unset "$var_name"
        echo "🧹 Unset: $var_name"
    fi

done < "$ENV_FILE"

echo "✅ Done. All variables from $ENV_FILE have been unset (even commented ones)."
