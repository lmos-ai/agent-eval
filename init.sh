#!/bin/bash

# Check if .env file exists
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: .env file not found!"
    exit 1
fi

# Unset previously set environment variables before loading new ones
# (Optional, but important if you want to be very strict)

while IFS='=' read -r key value; do
    # Skip empty lines or comments
    if [[ "$key" =~ ^#.*$ || -z "$key" ]]; then
        continue
    fi
    unset "$key"
done < <(grep -v '^#' "$ENV_FILE")

# Now load and export only the fresh values from .env
set -o allexport
source "$ENV_FILE"
set +o allexport

echo "✅ Environment variables freshly loaded from $ENV_FILE:"
grep -v '^#' "$ENV_FILE"

# Start your main script
echo "🚀 Starting services via start_services.sh..."
./start_services.sh
