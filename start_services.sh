#!/bin/bash

# Path to the OpenTelemetry config file
CONFIG_PATH="otel-config.yaml"

# Check if 'localhost' is in the brokers list in the config file
if grep -q 'localhost' $CONFIG_PATH; then
  echo "Kafka broker is localhost. Starting Kafka service..."
  docker-compose up -d kafka
else
  echo "Kafka broker is not localhost. Skipping Kafka service..."
fi

# Start the rest of the services (including FastAPI)
docker-compose up -d fastapi_app
