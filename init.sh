#!/bin/bash

# Check if .env file exists
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: .env file not found!"
    exit 1
fi

# Load and export variables from .env file
export $(grep -v '^#' "$ENV_FILE" | xargs)

echo "✅ Environment variables loaded from $ENV_FILE:"
grep -v '^#' "$ENV_FILE"

# Start your main script
echo "🚀 Starting services via start_services.sh..."
./start_services.sh
