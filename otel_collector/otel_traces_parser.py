from opentelemetry.proto.trace.v1.trace_pb2 import Span
from global_variable import OTEL_SPAN_INPUT_KEY, OTEL_SPAN_OUTPUT_KEY, OTEL_SPAN_CONVERSATION_ID
import json

class SpanProcessor:
    """
    Class to extract span name, input, and output from an OpenTelemetry Span object, with debug prints.
    """

    def __init__(self, span: Span):
        self.span = span
        print(f"[SpanProcessor.__init__] Initialized with span: {span.name}")

    def get_conversation_id(self) -> str:
        """
        Get the conversation id (raw string).
        """
        print("[get_conversation_id] Called")
        for attribute in self.span.attributes:
            print(f"[get_conversation_id] Inspecting attribute: key={attribute.key}")
            if attribute.key.lower() == OTEL_SPAN_CONVERSATION_ID:
                value = self._get_attribute_value(attribute)
                print(f"[get_conversation_id] Found conversation_id: {value}")
                return value
        print("[get_conversation_id] No conversation_id found")
        return None

    def get_span_name(self) -> str:
        """
        Get the name of the span.
        """
        name = self.span.name
        print(f"[get_span_name] Span name: {name}")
        return name

    def get_input(self) -> dict:
        """
        Extract the operation.input attribute if present and parse it as a dictionary.
        """
        print("[get_input] Called")
        for attribute in self.span.attributes:
            print(f"[get_input] Inspecting attribute: key={attribute.key}")
            if attribute.key.lower() == OTEL_SPAN_INPUT_KEY:
                raw = self._get_attribute_value(attribute)
                print(f"[get_input] Raw input string: {raw}")
                try:
                    parsed = json.loads(raw.replace("'", '"'))
                    print(f"[get_input] Parsed input dict: {parsed}")
                    return parsed
                except json.JSONDecodeError as e:
                    print(f"[get_input] ❌ Failed to parse input string as JSON: {raw}, error: {e}")
                    return {}
        print("[get_input] No input attribute found")
        return {}

    def get_output(self):
        """
        Extract the operation.return_value attribute if present.
        """
        print("[get_output] Called")
        for attribute in self.span.attributes:
            print(f"[get_output] Inspecting attribute: key={attribute.key}")
            if attribute.key.lower() == OTEL_SPAN_OUTPUT_KEY:
                value = self._get_attribute_value(attribute)
                print(f"[get_output] Found output: {value}")
                return value
        print("[get_output] No output attribute found")
        return None

    def _get_attribute_value(self, attribute):
        """
        Helper to get the concrete value from the AnyValue oneof. Returns
        string/int/float/bool as appropriate, or None if missing.
        """
        any_value = attribute.value
        # Determine which inner oneof field of AnyValue is set
        field_name = any_value.WhichOneof("value")
        print(f"[_get_attribute_value] Called for key={attribute.key}, oneof field={field_name}")
        if not field_name:
            print("[_get_attribute_value] No value field set on AnyValue")
            return None
        value = getattr(any_value, field_name)
        print(f"[_get_attribute_value] Retrieved value: {value}")
        return value
