import abc
from typing import Optional
from data_model.conversation import ConversationResult


class ConversationGenerator(abc.ABC):
    """
    Abstract base class defining the interface for conversation generators.
    """

    @abc.abstractmethod
    def generate_conversation(self, input_json: Optional[str]) -> ConversationResult:
        """
        Generates the conversation in the standardized format.

        :param input_json: JSON string containing conversation data (if any).
        :return: A ConversationResult containing the standardized conversation entries.
        """
        pass




