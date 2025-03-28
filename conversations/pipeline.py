from typing import Optional
from conversations.conversation_abstract import ConversationGenerator
from conversations.conversation_generator import AutomaticConversationGenerator
from conversations.conversation_format import InputConversationsFormator
from data_model.conversation import ConversationResult

class ConversationService:
    """
    Service class that orchestrates conversation generation using different strategies.
    """

    def __init__(self,
                 conversation_formator: Optional[ConversationGenerator] = None,
                 automatic_conversation_generator: Optional[ConversationGenerator] = None,
                 opentelemetry_traces_collector: Optional[ConversationGenerator] = None):
        """
        Initialize the ConversationService with specific generator implementations.

        :param conversation_formator: Instance of a generator that processes passed JSON conversations.
        :param automatic_conversation_generator: Instance of a generator that creates conversations.
        :param opentelemetry_traces_collector: Instance of a gnertor which will collect the OTLP data send by the Open Telemetry.
        """
        self.conversation_formator = conversation_formator or InputConversationsFormator()
        self.automatic_conversation_generator = automatic_conversation_generator or AutomaticConversationGenerator()
        self.opentelemetry_traces_collector = opentelemetry_traces_collector

    def get_conversation(self, input_json: Optional[str] = None) -> ConversationResult:
        """
        Generates a conversation based on the provided input.

        :param input_json: JSON string containing conversation data. If None or empty, generates a dummy conversation.
        :return: A ConversationResult object with the generated conversation.
        """
        if self.opentelemetry_traces_collector:
            return self.opentelemetry_traces_collector.generate_conversation()
        if not input_json:
            return self.automatic_conversation_generator.generate_conversation(input_json)
        else:
            return self.conversation_formator.generate_conversation(input_json)
