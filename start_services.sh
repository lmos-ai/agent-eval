#!/bin/bash

# Load .env safely
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: .env file not found!"
    exit 1
fi

set -o allexport
source "$ENV_FILE"
set +o allexport

echo "✅ Environment variables freshly loaded from $ENV_FILE:"
grep -v '^#' "$ENV_FILE"

CONFIG_TEMPLATE="otel_collector/config.yaml"
FINAL_CONFIG_PATH="otel_collector/otel-config-final.yaml"

# Substitute variables
envsubst < "$CONFIG_TEMPLATE" > "$FINAL_CONFIG_PATH"
echo "✅ Substituted config generated at $FINAL_CONFIG_PATH"

# Build docker images
docker-compose build --no-cache

echo "Kafka broker is $KAFKA_BROKER"

# Start Kafka if localhost
if [[ "$KAFKA_BROKER" == *"kafka"* ]]; then
    echo "🚀 Kafka broker is localhost. Starting Kafka, Zookeeper, and Kafdrop..."
    docker-compose up -d kafka zookeeper

    echo "⏳ Waiting for Kafka services to start (10s)..."
    sleep 10
else
    echo "⚠️ Kafka broker is not localhost. Skipping Kafka services."
fi

# 🛠 Mongo Check Section
echo "MongoURI just before MongoDB check: $MONGO_URI"

if [ -n "$MONGO_URI" ]; then
    echo "🟢 External MongoDB URI detected. Skipping local MongoDB container startup."
else
    echo "⚠️ No external Mongo URI found. Starting local MongoDB..."

    # Generate random Mongo credentials
    export MONGO_INITDB_ROOT_USERNAME="user_$(openssl rand -hex 3)"
    export MONGO_INITDB_ROOT_PASSWORD="$(openssl rand -hex 8)"

    # Save Mongo credentials into a temp file
    echo "MONGO_INITDB_ROOT_USERNAME=$MONGO_INITDB_ROOT_USERNAME" > .mongo_secrets.env
    echo "MONGO_INITDB_ROOT_PASSWORD=$MONGO_INITDB_ROOT_PASSWORD" >> .mongo_secrets.env

    # Construct MONGO_URI and save it
    export MONGO_URI="mongodb://${MONGO_INITDB_ROOT_USERNAME}:${MONGO_INITDB_ROOT_PASSWORD}@mongodb:27017/"
    echo "Mongo URI $MONGO_URI"

    echo "MONGO_URI=$MONGO_URI" >> .mongo_secrets.env


    # Start MongoDB service with env file
    docker-compose --env-file .mongo_secrets.env up -d mongo-db mongo-express

    echo "✅ Local MongoDB started with random credentials."
fi

# Reload new Mongo vars into the environment (important)
if [ -f ".mongo_secrets.env" ]; then
    set -o allexport
    source ".mongo_secrets.env"
    set +o allexport
    echo "✅ Loaded generated MongoDB credentials into environment."
fi

# Start the rest of services
docker-compose up -d black-box-evaluation otel-collector kafdrop exportor_services
