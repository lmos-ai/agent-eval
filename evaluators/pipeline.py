# pipeline.py
import pandas as pd
from typing import List, Dict, Any
from conversations.conversation_format import ConversationEntry
from data_model.evaluation import ConversationEvaluationResult
from evaluators.base import BaseEvaluator
from evaluators.utils_steps_evaluator import StepOrderValidator, validate_conversation_logs, validate_simulation_steps, LLMTriggerMatcher
from llm.llm import LLMModel
from models.gliner_model import extract_and_check_entities
from evaluators.scorer import QueryScorer

class PluggableEvaluationPipeline:
    def __init__(
        self,
        simulation_steps: List[Dict[str, Any]],
        conversation_logs: List[Dict[str, Any]],
        evaluators: List[BaseEvaluator],  # list of evaluators
        trigger_matcher:LLMTriggerMatcher,
        step_validator: StepOrderValidator = None,
        scorer: QueryScorer = None,
    ):
        self.simulation_steps = simulation_steps
        self.conversation_logs:List[ConversationEntry] = conversation_logs
        self.evaluators = evaluators  # set of plugged-in evaluation steps
        self.step_validator = step_validator
        self.scorer = scorer
        self.trigger_matcher=trigger_matcher

        self.results = []
        self.matched_steps = []
        self.previous_context = []  # keep track of context across turns

    def match_step(self, query: str) -> Dict[str, Any]:
        """
        Example step matching logic. Or you can use LLMTriggerMatcher as you did before.
        Return the single matched step or None.
        """
        # (Pseudo) match logic here:
        query_lower = query.lower()
        for step in self.simulation_steps['steps']:
            step_trigger = step.get("trigger_event","Trigger Event not provided. Use your knowledge")
            if step_trigger in query_lower:
                return step
        return None

    def run_pipeline(self):
        """
        Main loop: for each conversation log, match a step, then run all evaluators
        on that conversation log, gather results, do scoring, etc.
        """
        try:
            for idx, log in enumerate(self.conversation_logs):
                print(f"[.] Evaluating {idx+1} conversation turn cycle")
                query = log.user_query
                actual_response = log.response
                


                # Step 1: Match step
                print("[.]    Matching the step")
                # Match the step using LLM
                step_name = self.trigger_matcher.get_step_name(
                    previous_context=self.previous_context,
                    query=query,
                    trigger_events=[
                        {"step_name": step.get("step_name", ""), "trigger_event": step.get("trigger_event", "Dont have trigger event yet. Use your knowledge")}
                        for step in self.simulation_steps['steps']
                    ]
                )
                matched_step=None
                # Iterate over simulation steps
                if step_name:
                    for step in self.simulation_steps['steps']:
                        step_name_in_simulation = step.get("step_name", "").strip().lower()
                        if step_name_in_simulation == step_name.strip().lower():
                            matched_step = step
                            break

                self.matched_steps.append(matched_step)

                # Step 2: Run all plugged-in evaluators
                print("[.]    Going to evaluate the conversation turn")
                row_result = {"query": query, "actual_response": actual_response}
                for evaluator in self.evaluators:
                    print("[.]    Running evaluator on conversation turn")
                    partial_result = evaluator.run_evaluation(
                        conversation_log=log,
                        previous_context=self.previous_context,
                        matched_step=matched_step,
                        simulation_steps=self.simulation_steps
                    )
                    row_result.update(partial_result)
                print("[.]    Got success in Evaluation  for conversation turn cycle")
                # If you have a "scorer," you can compute a combined score
                # based on partial results, e.g., row_result["score"] = ...
                if self.scorer:
                    print("[.]    Calculating the score for conversation cycle")
                    row_result["score"] = self.scorer.calculate_score(
                        actual_functions_names=[],
                        expected_functions_names=[],
                        llm_result=row_result,
                        matched_step=matched_step)
                else:
                    print("[...]    Skipping calculation of the score for conversation cycle as Scorrer passed is None")
                    row_result["score"] = None
                # Keep track of the conversation
                self.results.append(row_result)
                print("[.] Updating the previous context")
                # Step 3: Update context
                self.previous_context.append({
                    "user_query": log.user_query,
                    "response": log.response,
                    "actual_functions": log.actual_function_calls
                })
            print("[.] Evaluation Done.")
            # Step 4: Step order validation (after all logs processed)
            steps_in_order = True
            if self.step_validator:
                print("[.] Validate the order of steps taken in conversation")
                steps_in_order = self.step_validator.validate_step_order(self.matched_steps)
            else:
                print("[...] Skipping Steps Order Validator as Step_validator passed is None.")
                steps_in_order = "None"
            
            # Attach "steps_in_order" to all results
            for r in self.results:
                r["steps_in_order"] = steps_in_order
            
            
            results = []
            for row in self.results:
                # For any missing columns, Pydantic will fill with None automatically
                result_model = ConversationEvaluationResult(
                    query=row.get("query"),
                    actual_response=row.get("actual_response"),
                    ner_score=row.get("ner_score"),
                    ner_halucination_safe_index=row.get("ner_halucination_safe_index"),
                    ner_keyword_extracted=row.get("ner_keyword_extracted"),
                    ner_keywords_extracted_matches=row.get("ner_keywords_extracted_matches"),
                    ner_keywords_extracted_not_matched=row.get("ner_keywords_extracted_not_matched"),
                    llm_halucinated=str(row.get("llm_halucinated")),
                    correct_response=str(row.get("correct_response")),
                    reasoning=row.get("reasoning"),
                    expected_functions=row.get("expected_functions"),
                    actual_functions=row.get("actual_functions"),
                    missing_functions=row.get("missing_functions"),
                    incorrect_functions=row.get("incorrect_functions"),
                    function_calls_correct=row.get("function_calls_correct"),
                    score=row.get("score"),
                    steps_in_order=row.get("steps_in_order"),
                )
            results.append(result_model)
            print("[.] Returning the results of evaluation")
            
            return results, steps_in_order
        except Exception as e:
            raise RuntimeError(f"Error in pipeline: {e}")


def evaluate(
    conversation_logs: List[Dict[str, Any]],
    simulation_steps: List[Dict[str, Any]],
    evaluators: List[BaseEvaluator],
    llm:LLMModel,
    step_validator: StepOrderValidator = None,
    scorer: QueryScorer = None
):
    """
    Entry point for the pipeline. We pass in the list of evaluators we want to run
    (NER, function calls, LLM halucination, etc.).
    """
    print("[.] Validating conversationa and simulations")
    # Validate inputs
    validate_conversation_logs(conversation_logs=conversation_logs)
    validate_simulation_steps(simulation_steps=simulation_steps)
    print("[.] Validation Done")
    llm_trigger_matcher = LLMTriggerMatcher(llm=llm)
    pipeline = PluggableEvaluationPipeline(
        simulation_steps=simulation_steps,
        conversation_logs=conversation_logs,
        evaluators=evaluators,
        step_validator=step_validator,
        scorer=scorer,
        trigger_matcher=llm_trigger_matcher
    )
    print("[.] Running the Evaluation pipeline")
    results, steps_in_order = pipeline.run_pipeline()
    # If you want a final average or something:
    scores = [row.score for row in results if row.score]
    final_score = sum(scores)/len(results)
    return results, steps_in_order, final_score
