from marshmallow import Schema, fields

class EvaluationRequestSchema(Schema):
    unique_id = fields.String(required=True, description="Unique ID for tracking the evaluation.")
    conversation_logs = fields.List( 
        cls_or_instance=fields.Dict(),
        required=True, 
        description="List of conversation logs between user and assistant."
    )
    test_cases = fields.List(
        cls_or_instance=fields.Dict(),
        required=True,
        description="List of test cases for evaluating the LLM."
    )
    use_case = fields.String(
        required=True,
        description="Use cases or Agent name for test case passed which is going to be evaluated."
    )


class BackgroundTaskStatusRequestSchema(Schema):
    task_id = fields.String(
        required=True,
        description="Unique ID of the background task to check its status."
    )



from pydantic import BaseModel
from typing import Optional, List

class ConversationEvaluationResult(BaseModel):
    # Basic conversation info
    query: Optional[str] = None
    actual_response: Optional[str] = None

    # NER Halucination Evaluator fields
    ner_score: Optional[float] = None
    ner_halucination_safe_index: Optional[float] = None
    # We'll store keywords as a list of strings, or None if not present
    ner_keyword_extracted: Optional[List[str]] = None
    ner_keywords_extracted_matches: Optional[List[str]] = None
    ner_keywords_extracted_not_matched: Optional[List[str]] = None

    # LLM Halucination Evaluator fields
    llm_halucinated: Optional[str] = None
    correct_response: Optional[str] = None
    reasoning: Optional[str] = None

    # Function Call Evaluator fields
    expected_functions: Optional[List[str]] = None
    actual_functions: Optional[List[str]] = None
    missing_functions: Optional[List[str]] = None
    incorrect_functions: Optional[List[str]] = None
    function_calls_correct: Optional[str] = None

    # Optional scoring
    score: Optional[float] = None

    # Whether steps are in correct order
    steps_in_order: Optional[str] = None

class PipelineEvaluationResponse(BaseModel):
    id: str
    results: List[ConversationEvaluationResult]
    score: Optional[float] = None
    are_steps_in_order: Optional[str] = None