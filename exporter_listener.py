import yaml
from kafka import KafkaConsumer
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
from google.protobuf.json_format import MessageToDict
import time
import re, os
from helper_functions.mongo_utils import MongoDBService
from otel_collector.otel_traces_parser import SpanProcessor
from global_variable import OPENTELEMETRY_TRACES_COLLECTION
from config import Config

config = Config()

def load_config(config_path='otel_collector/config.yaml'):
    """
    Load OpenTelemetry configuration with environment variable substitution.
    """
    with open(config_path, 'r') as f:
        content = f.read()

    # Substitute environment variables
    content = re.sub(r'\$\{(\w+)\}', lambda m: os.environ.get(m.group(1), m.group(0)), content)

    return yaml.safe_load(content)


def start_kafka_listener(kafka_config):
    """
    Start Kafka consumer and continuously listen for messages.
    """
    topic = kafka_config.get('topic', 'black-box-eval')
    brokers = kafka_config.get('brokers', ['kafka:9092'])
    broker = brokers[0].replace("kafka", "localhost")
    print(f"Listening to the Kafka Broker: {broker} for topic: {topic}")
    try:
        consumer = KafkaConsumer(
            "black-box-eval",
            bootstrap_servers=["kafka:9092"],
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            group_id="otel-test",
            value_deserializer=lambda m: m,  
        )


        # Explicitly subscribe to topic
        consumer.subscribe([topic])

        # Wait for partition assignment
        while not consumer.assignment():
            print("Waiting for partition assignment...")
            consumer.poll(timeout_ms=100)
            time.sleep(1)

        print(f"Assigned partitions: {consumer.assignment()}")
        print(f"Connecting to: {config.MONGO_URI}")
        mongo_srv = MongoDBService(db_name=config.MONGO_DATABASE, collection=OPENTELEMETRY_TRACES_COLLECTION, uri=config.MONGO_URI)
        # Continuously listen for messages
        while True:
            print("Listening")
            try:
                # Listen for new messages indefinitely
                for message in consumer:
                    print(f"\n📦 Offset: {message.offset}")
                    print(f"📨 Raw bytes: {message.value[:60]}...") 
                    trace_request = ExportTraceServiceRequest()
                    trace_request.ParseFromString(message.value)

                    # Print the trace information from OpenTelemetry data
                    print(f"Received Kafka message")
                    trace_request = ExportTraceServiceRequest()
                    trace_request.ParseFromString(message.value)
                    print(f"Going to extract information from the traces.")
                    # Process and save each span inside trace
                    for i, resource_span in enumerate(trace_request.resource_spans):
                        print(f"Going for Resource span: {i}")
                        for j, scope_span in enumerate(resource_span.scope_spans):
                            print(f"getting scope_span: {j}")
                            for span in scope_span.spans:
                                processor = SpanProcessor(span)
                                conversation_id = processor.get_conversation_id()
                                # if not conversation_id:
                                #     print("No conversation id found in the span. Skipping the traces")
                                #     continue
                                formatted_trace = {
                                    "conversation_id": conversation_id,
                                    "span_name": processor.get_span_name(),
                                    "input": processor.get_input(),
                                    "output": processor.get_output(),
                                    "trace_id": span.trace_id.hex(),
                                    "span_id": span.span_id.hex(),
                                    "timestamp": span.start_time_unix_nano
                                }
                                # save to mongoDB
                                print(f"Saving the traces from span: {j} and resource span: {i}")
                                mongo_srv.save_document(formatted_trace)
                                print(f"Saved the traces from span: {j} and resource span: {i}")

                
            except Exception as e:
                # Handle errors gracefully, so the listener can continue
                print(f"Error occurred while listening to Kafka: {str(e)}")
            # Consumer should keep running until an explicit shutdown occurs
            # No need to call consumer.close() here, as we want to continue listening.
    except Exception as e:
        print(f"Got error while getting the message from Kafka broker: {brokers}. Error: {e}")
        print("Initializing the Listener again in 10 seconds.")
        time.sleep(10)
        init_listener()

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

# Initialize the listener
init_listener()
