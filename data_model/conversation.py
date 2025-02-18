from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field



@dataclass
class FunctionCall:
    function_name: str
    input_passed: Dict[str, Any] = field(default_factory=dict)
    output_passed: Any = None


@dataclass
class ConversationEntry:
    user_query: str = ""
    actual_function_calls: List[FunctionCall] = field(default_factory=list)
    response: str = ""


@dataclass
class ConversationResult:
    conversation_entries: List[ConversationEntry] = field(default_factory=list)


class InputConversation(BaseModel):
    conversation_thread_id:str = Field(description="Pass the conversation thread id or any unique id to fetch or save results in the database.")
    input_data:str = Field(description="Pass the data in string format. Even if the data is json pass in string format.")
    
