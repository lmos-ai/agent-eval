from dataclasses import dataclass, field

@dataclass
class Message:
    """Represents a single message in the conversation."""
    type: str
    conversation_id: str
    content: str
    response_time: float = None
    agent: str = None


@dataclass
class GroundTruthConversation:
    """Represents a conversation entry with user query and bot response."""
    user_query: str
    response: str