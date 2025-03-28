from conversations.conversation_abstract import ConversationGenerator
from data_model.conversation import ConversationResult
from typing import Optional


class OpenTelemtryCollector(ConversationGenerator):
    def _connect_opentelemetry(self):
        pass

    

    def generate_conversation(self, input_json=None)->Optional[ConversationResult]:
        pass

