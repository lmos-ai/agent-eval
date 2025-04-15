#!/bin/bash

CONFIG_TEMPLATE="otel_collector/config.yaml"
FINAL_CONFIG_PATH="otel_collector/otel-config-final.yaml"

# Check required environment variables
if [ -z "$KAFKA_BROKER" ]; then
    echo "❌ Error: KAFKA_BROKER environment variable not set."
    exit 1
fi

export KAFKA_BROKER

# Generate substituted YAML file explicitly
envsubst < "$CONFIG_TEMPLATE" > "$FINAL_CONFIG_PATH"
echo "✅ Substituted config generated at $FINAL_CONFIG_PATH"

# Build Docker containers without cache
docker-compose build --no-cache

echo "Kafka broker is $KAFKA_BROKER"
# Check directly if Kafka broker points to localhost
if [[ "$KAFKA_BROKER" == *"kafka"* ]]; then
    echo "🚀 Kafka broker is localhost. Starting Kafka, Zookeeper, and Kafdrop..."
    docker-compose up -d kafka zookeeper

    # Give Kafka time to initialize
    echo "⏳ Waiting for Kafka services to start (10s)..."
    sleep 10
else
    echo "⚠️ Kafka broker is not localhost. Skipping Kafka-related services..."
fi


# Check for MongoDB credentials
if [[ -n "$MONGO_INITDB_ROOT_USERNAME" && -n "$MONGO_INITDB_ROOT_PASSWORD" ]]; then
    echo "🟢 MongoDB credentials detected. Starting MongoDB service..."
    docker-compose up -d mongodb
else
    echo "⚠️ MongoDB credentials not fully set. Skipping MongoDB service..."
fi


# Always start evaluation services afterwards
docker-compose up -d black-box-evaluation otel-collector kafdrop

