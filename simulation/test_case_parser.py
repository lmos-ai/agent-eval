from abc import ABC, abstractmethod
from data_model.simulations import GroundTruthConversation
from typing import List, Dict, Any


# Abstract class for Test Case Parser
class TestCaseParser(ABC):
    """Abstract base class to parse test cases and extract relevant data."""

    def __init__(self, test_data: Dict[str, Any]):
        self.test_data = test_data

    @abstractmethod
    def extract_conversations(self) -> List["GroundTruthConversation"]:
        """Extracts and returns conversation entries from test data."""
        pass



class JSONTestCaseParser(TestCaseParser):
    """
    Concrete implementation of TestCaseParser for JSON data format.
    This extracts the user query and expected response from messages.
    """

    def extract_conversations(self) -> List[GroundTruthConversation]:
        conversation_entries: List[GroundTruthConversation] = []

        # Loop through each test case
        for test_case in self.test_data.get("testCases", []):
            expected_data = test_case.get("expected", {})
            messages = expected_data.get("messages", [])

            # Ensure messages exist in pairs (user query -> bot response)
            for i in range(len(messages) - 1):
                if messages[i]["type"] == "user" and messages[i + 1]["type"] == "bot":
                    user_query = messages[i]["content"].strip()
                    response = messages[i + 1]["content"].strip()

                    # Append conversation entry
                    conversation_entries.append(GroundTruthConversation(user_query, response))

        return conversation_entries