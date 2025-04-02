import yaml
from kafka import KafkaConsumer
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest

def load_config(config_path='otel-config.yaml'):
    """
    Load OpenTelemetry configuration.
    """
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def start_kafka_listener(kafka_config):
    """
    Start Kafka consumer and continuously listen for messages.
    """
    topic = kafka_config.get('topic', 'default-topic')
    brokers = kafka_config.get('brokers', ['localhost:9092'])

    # Create Kafka consumer to listen to the topic
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=brokers,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='otel-group'
    )

    print(f"Kafka Listener started on topic: {topic} with brokers: {brokers}")

    # Continuously listen for messages
    try:
        for message in consumer:
            trace_request = ExportTraceServiceRequest()
            trace_request.ParseFromString(message.value)

            # Print the trace information from OpenTelemetry data
            print(f"Received Kafka message: {trace_request}")
    except Exception as e:
        print(f"Error occurred while listening to Kafka: {str(e)}")
    finally:
        consumer.close()

def init_listener():
    """
    Initialize the listener based on the OpenTelemetry config.
    """
    config = load_config()

    # Check if Kafka exporter is defined in the config
    exporters = config.get('exporters', {})
    if 'kafka' in exporters:
        print("Kafka exporter detected. Starting Kafka listener.")
        start_kafka_listener(exporters['kafka'])
    else:
        print("Kafka exporter not detected. Listener not started.")
