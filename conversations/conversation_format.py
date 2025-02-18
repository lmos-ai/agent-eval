import json
from data_model.conversation import ConversationResult, ConversationEntry, FunctionCall
from conversations.conversation_abstract import ConversationGenerator
from typing import Optional, List, Any, Dict



class InputConversationsFormator(ConversationGenerator):
    """
    Generates conversation logs by parsing provided JSON input.
    """

    def generate_conversation(self, input_json: Optional[dict]) -> ConversationResult:
        """
        Parse the given conversation JSON and convert it into the desired format.

        :param input_json: JSON containing the conversation data.
        :return: A ConversationResult object with standardized conversation entries.
        """
        result = ConversationResult()

        if not input_json:
            return result  # Return empty conversation if no input provided

        try:
            if isinstance(input_json, str):
                data = json.loads(input_json)
            elif isinstance(input_json, dict):
                data = input_json
            else:
                raise Exception("Input_json is not string or json. Please pass valid input.")

            # Extract messages and events from the JSON
            print(f"Got Data type: {type(data)}")
            conversation_node = data.get("conversation", {})
            messages = conversation_node.get("messages", [])
            events = data.get("events", [])

            conversation_entries: List[ConversationEntry] = []
            function_calls: List[FunctionCall] = []

            # Traverse events in reverse order
            for event in reversed(events):
                event_type = event.get("type")
                payload = json.loads(event.get("payload"))
                print(f"Got Event Type:{event_type}")
                # Handle function calling event
                if event_type.lower() == "llmfunctioncalledevent":
                    function_calls.append(
                        FunctionCall(
                            function_name=payload.get("name", ""),
                            input_passed=payload.get("param", {}),
                            output_passed=payload.get("result", {})
                        )
                    )

                # Handle agent finished event
                elif event_type.lower() == "agentfinishedevent":
                    # Ensure there are at least two messages for user query and response
                    if len(messages) >= 2:
                        user_query = messages.pop(0)
                        response = messages.pop(0)
                        

                        # Create a conversation entry and add to the list
                        conversation_entries.append(
                            ConversationEntry(
                                user_query=user_query["content"],
                                actual_function_calls=function_calls[::-1],  # Reverse to maintain chronological order
                                response=response["content"]
                            )
                        )

                        # Reset function calls for the next cycle
                        function_calls = []
                    else:
                        print("! Messages must have atleast 2 messages.")

            # Reverse the entries to return them in chronological order
            return ConversationResult(conversation_entries)

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return result  # Return empty conversation on JSON parsing error
        except Exception as e:
            raise Exception(f"Got expection while formating the data. Expection: {e}")
