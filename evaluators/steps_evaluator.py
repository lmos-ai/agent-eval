from evaluators.utils_steps_evaluator import LLMEvaluation, LLMTriggerMatcher, StepOrderValidator, FunctionExtractor, validate_conversation_logs, validate_simulation_steps
from llm.llm import LLMModel
from models.gliner_model import extract_and_check_entities
from helper_functions.scorer import QueryScorer
import pandas as pd

class LLMEvaluatorPipeline:
    """
    Coordinates the evaluation pipeline by integrating FunctionExtractor, StepOrderValidator, LLMTriggerMatcher, and LLMEvaluation.
    """
    def __init__(self, function_extractor:FunctionExtractor, step_validator:StepOrderValidator, 
                 trigger_matcher:LLMTriggerMatcher, llm_evaluator:LLMEvaluation, scorer:QueryScorer, conversation_logs:list, 
                 simulation_steps:list,gliner_model, ner_entities:list, halucination_threshold:float=0.3):
        self.function_extractor = function_extractor
        self.step_validator = step_validator
        self.trigger_matcher = trigger_matcher
        self.llm_evaluator = llm_evaluator
        self.conversation_logs = conversation_logs
        self.simulation_steps = simulation_steps
        self.scorer = scorer
        self.results = []
        self.matched_steps = []
        self.gliner_model=gliner_model
        self.ner_entities=ner_entities
        if not isinstance(self.ner_entities, list) or not len(self.ner_entities):
            raise Exception("Please pass NER entites to extract")
        self.halucination_threshold = halucination_threshold
        if not isinstance(self.halucination_threshold, float) or not self.halucination_threshold:
            raise Exception("Please pass the threshold")

    def run_pipeline(self):
        """
        Run the evaluation pipeline.
        """
        try:
            previous_context = []
            for log in self.conversation_logs:
                # ---------------------------------------------------------------
                # Initializing the variables
                query = log["user_query"]
                reasoning = ""
                print(f"Evaluating Query: {query}")
                missing_functions = []
                actual_functions = self.function_extractor.extract_functions(log, key="actual_function_calls")
                actual_functions_names = [func['function_name'].lower() for func in actual_functions]
                actual_response = log["response"]
                expected_functions = []
                incorrect_functions = []
                is_correct_step_followed = True
                score = 0
                # Initialize matched_step to None
                matched_step = None



                # ---------------------------------------------------------------------------
                # Match the step using LLM
                step_name = self.trigger_matcher.get_step_name(
                    previous_context=previous_context,
                    query=query,
                    trigger_events=[
                        {"step_name": step.get("step_name", ""), "trigger_event": step["trigger_event"]}
                        for step in self.simulation_steps
                    ]
                )
                print(f"Step name got from LLM is:{step_name}")
                # Iterate over simulation steps
                if step_name:
                    for step in self.simulation_steps:
                        step_name_in_simulation = step.get("step_name", "").strip().lower()
                        if step_name_in_simulation == step_name.strip().lower():
                            matched_step = step
                            break

                self.matched_steps.append(matched_step)
                print(f"Got Step name: {matched_step}.")
                
                if not matched_step:
                    # check if the functions are called or not
                    if actual_functions:
                        for func in actual_functions:
                            incorrect_functions.append(func['function_name'])
                        
                # Fetch expected data
                expected_response = matched_step.get("expected_response", "") if matched_step else None
                expected_functions = matched_step.get("expected_functions", []) if matched_step else []
                expected_functions_names = [func['function_name'].lower() for func in expected_functions]
                print("Evaluating the response and getting reasoning.")




                # ---------------------------------------------------------------------------
                # Call LLM for evaluation
                llm_result = self.llm_evaluator.evaluate(
                    previous_context=previous_context,
                    query=query,
                    actual_response=actual_response,
                    expected_response=expected_response or "",
                    actual_functions=actual_functions or [],
                    expected_functions=expected_functions or []
                )

                
                
                # Update context
                previous_context.append({"user_query": query, "actual_functions":actual_functions})

                # ------------------------------------------------------------------------
                # Extract the entities from the response
                ner_response = extract_and_check_entities(
                    model=self.gliner_model,
                    response=actual_response,
                    previous_context=previous_context,
                    current_user_query=query,
                    threshold=0.7,
                    data_entities=self.ner_entities

                )
                print("Got the NER response")
                no_of_total_keywords_found = ner_response['total_found']
                no_of_keywords_matched = ner_response['matched']
                keyword_extracted = ner_response['keywords_extracted']
                ner_halucination_score = ner_response['score']
                keywords_extracted_not_matched = ner_response['keywords_extracted_not_matched']
                keywords_extracted_matches = ner_response['keywords_extracted_matches']

                if ner_halucination_score < 0 or ner_halucination_score > 1:
                    raise Exception("Check NER nalucination class. The score must be between 0-1")

                

                # --------------------------------------------------------------------------
                # Calculate Score
                print("Scoring the query")
                score_response =  self.scorer.calculate_score(
                                    matched_step=matched_step,
                                    expected_functions_names=expected_functions_names,
                                    actual_functions_names=actual_functions_names,
                                    llm_result=llm_result,
                                    ner_halucination_score=ner_halucination_score,
                                    halucination_threshold=self.halucination_threshold
                                )
                score = score_response['score'] 
                is_correct_step_followed = score_response['is_correct_step_followed']
                reasoning = score_response['reasoning']
                missing_functions = score_response['missing_functions']
                incorrect_functions = score_response['incorrect_functions']
                
                
                print("Getting the entities from response and checking halucination using NER")




                # ---------------------------------------------------------
                # adding result
                self.results.append({
                    "query": query,

                    "llm_halucinated": llm_result["is_halucinated"],
                    "ner_halucination_safe_index": (1-ner_halucination_score)*100,
                    "ner_keyword_extracted":keyword_extracted,
                    "ner_keywords_extracted_matches":keywords_extracted_matches,
                    "ner_keywords_extracted_not_matched":keywords_extracted_not_matched,

                    "is_in_correct_step_followed": is_correct_step_followed,
                    "step_name": matched_step["step_name"] if matched_step else None,

                    "expected_functions": expected_functions_names,
                    "actual_functions": str(actual_functions),

                    "score":score,
                    
                    "correct_response": False if not is_correct_step_followed else llm_result['correct_response'],
                    "actual_response":actual_response,
                    "reasoning": reasoning or llm_result['reasoning'],

                    "incorrect_functions": incorrect_functions,
                    "missing_functions":missing_functions
                    
                })



                # updating previous context
                last_response = previous_context[-1]
                last_response['response'] = actual_response
                previous_context[-1] = last_response


            # Validate the order of matched steps
            steps_in_order = self.step_validator.validate_step_order(self.matched_steps)

            # Add order validation result
            for result in self.results:
                result["steps_in_order"] = steps_in_order

            # Convert results to DataFrame
            df = pd.DataFrame(self.results)
            df.to_csv("Evaluation_report.csv")
            return df, steps_in_order
        except Exception as e:
            raise RuntimeError(f"Error running pipeline: {str(e)}, Previous context: {previous_context}")


def run_llm_evaluator_pipeline_with_validations(conversation_logs:list, simulation_steps:list, llm:LLMModel, gliner_model,ner_entities:list, halucination_threshold:float=0.7):
    """
    Initializes and runs the LLM Evaluator Pipeline with example data.
    Includes validations for conversation logs and simulation steps.
    """
    
    # Validate inputs
    try:
        
        validate_conversation_logs(conversation_logs=conversation_logs)
        validate_simulation_steps(simulation_steps=simulation_steps)
        print("Validation successful: All required keys are present.")
    except ValueError as e:
        print(f"Validation Error: {str(e)}")
        return None
    
    if llm is None:
        raise Exception("LLM passed is None")
    
    # Initialize modules
    function_extractor = FunctionExtractor()
    step_validator = StepOrderValidator(simulation_steps)
    trigger_matcher = LLMTriggerMatcher(llm=llm)
    llm_evaluator = LLMEvaluation(llm=llm)
    scorer = QueryScorer()

    # Initialize pipeline
    pipeline = LLMEvaluatorPipeline(
        function_extractor=function_extractor,
        step_validator=step_validator,
        trigger_matcher=trigger_matcher,
        llm_evaluator=llm_evaluator,
        scorer = scorer,
        conversation_logs=conversation_logs,
        simulation_steps=simulation_steps,
        gliner_model=gliner_model,
        halucination_threshold=halucination_threshold,
        ner_entities=ner_entities
    )

    # Run pipeline
    results_df, are_steps_in_order = pipeline.run_pipeline()
    return results_df, are_steps_in_order, results_df['score'].mean()





