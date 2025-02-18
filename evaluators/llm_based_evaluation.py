# evaluators/llm_halucination.py
from evaluators.base import BaseEvaluator
from typing import Any, Dict, List
from evaluators.utils_steps_evaluator import LLMEvaluation
from conversations.conversation_format import ConversationEntry


class LLMHBasedEvaluator(BaseEvaluator):
    def __init__(self, llm_evaluation: LLMEvaluation):
        """llm_evaluation is LLMEvaluation instance."""
        self.llm_evaluation = llm_evaluation

    def run_evaluation(
        self,
        conversation_log: ConversationEntry,
        previous_context: List[Dict[str, Any]],
        matched_step: Dict[str, Any],
        simulation_steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if not conversation_log:
            raise Exception("Please pass conversation log")
        
        query = conversation_log.user_query
        actual_response = conversation_log.response
        expected_response = matched_step["expected_response"] if matched_step else ""

        # If needed: actual_functions, expected_functions, etc.
        actual_functions = conversation_log.actual_function_calls
        expected_functions = matched_step.get("expected_functions", []) if matched_step else []

        # Call your existing LLMEvaluation
        print("[.] Passing conversation to evaluators")
        llm_result = self.llm_evaluation.evaluate(
            previous_context=previous_context,
            query=query,
            actual_response=actual_response,
            expected_response=expected_response,
            actual_functions=actual_functions,
            expected_functions=expected_functions
        )
        return {
            "llm_halucinated": llm_result["is_halucinated"],
            "correct_response": llm_result["correct_response"],
            "reasoning": llm_result["reasoning"]
        }
