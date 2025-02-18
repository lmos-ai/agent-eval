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