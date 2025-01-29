from typing import Optional
from conversations.conversation_abstract import ConversationGenerator
from data_model.conversation import ConversationResult, ConversationEntry, FunctionCall


class AutomaticConversationGenerator(ConversationGenerator):
    """
    Generates a dummy conversation with predefined entries.
    """

    def generate_conversation(self, input_json: Optional[str]) -> ConversationResult:
        """
        Returns a dummy conversation with sample entries.

        :param input_json: Ignored for dummy generator.
        :return: A ConversationResult object with dummy conversation entries.
        """
        result = ConversationResult()

        # Entry without function calls
        entry1 = ConversationEntry(
            user_query="Hello? Eh... me pay some money for the phone I owe. Mi ID es userX1, pass is passX1",
            response="Okay, userX1 authenticated. Let's see your outstanding bills. One moment."
        )
        result.conversation_entries.append(entry1)

        # Entry with function calls
        function_call1 = FunctionCall(
            function_name="authenticate_user",
            input_passed={
                "user_id": "userX1",
                "password": "passX1"
            },
            output_passed={
                "is_authenticated": True,
                "error_messages": []
            }
        )
        entry2 = ConversationEntry(
            user_query="Yes, yes. I'm older lady, can't pay all. Show me the bills, por favor.",
            actual_function_calls=[function_call1],
            response="Your total due for May 2024 is $200.00, due by May 25, 2024."
        )
        result.conversation_entries.append(entry2)

        # Additional entries can be added similarly...

        return result