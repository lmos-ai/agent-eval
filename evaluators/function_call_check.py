from typing import Any, Dict, List
from evaluators.base import BaseEvaluator
from conversations.conversation_format import ConversationEntry


class FunctionCallCheckEvaluator(BaseEvaluator):
    """
    Checks whether the conversation log includes the correct function calls
    compared to what was expected in the matched simulation step.
    """

    def __init__(self):
        # If you need any configuration or references, 
        # pass them through the constructor
        pass

    def run_evaluation(
        self,
        conversation_log: ConversationEntry,
        previous_context: List[Dict[str, Any]],
        matched_step: Dict[str, Any],
        simulation_steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare actual function calls in the conversation log 
        to the expected function calls in matched_step.
        """
        # Actual function calls from the conversation log
        actual_functions = conversation_log.actual_function_calls
        actual_function_names = set(
            func.get("function_name", "").lower() 
            for func in actual_functions
        )

        # Expected functions (from the matched step)
        expected_functions = matched_step.get("expected_functions", []) if matched_step else []
        expected_function_names = set(
            func.get("function_name", "").lower() 
            for func in expected_functions
        )

        # Identify missing or extra calls
        missing_functions = list(expected_function_names - actual_function_names)
        extra_functions = list(actual_function_names - expected_function_names)

        # Return a dict with everything you want to record
        return {
            "expected_functions": list(expected_function_names),
            "actual_functions": [f.get("function_name", "") for f in actual_functions],
            "missing_functions": missing_functions,
            "incorrect_functions": extra_functions,
            # Optionally: a boolean indicating if all calls match exactly
            "function_calls_correct": (len(missing_functions) == 0 and len(extra_functions) == 0)
        }
