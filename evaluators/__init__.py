# main.py or wherever you orchestrate
from evaluators.ner_halucinator import NERHalucinationEvaluator
from evaluators.llm_based_evaluation import LLMHBasedEvaluator
from evaluators.function_call_check import FunctionCallCheckEvaluator
from evaluators.utils_steps_evaluator import StepOrderValidator, LLMEvaluation, FunctionExtractor
from typing import List, Any
from llm.llm import LLMModel
from evaluators.scorer import QueryScorer
from helper_functions.algorithms import EXPECTED_RESPONSE_CHECK, FUNCTION_CALLINGS_CHECK, NER_HALUCINATION, STEPS_IN_ORDER, ALL_ALGORITHMS
from evaluators.pipeline import evaluate

def create_evaluators(selected_evaluations: list, llm, ner_model, ner_entities) -> list:
    """Given a list of evaluation names, instantiate the corresponding evaluator objects."""
    # Example mapping
    evaluators_map = {
        NER_HALUCINATION: lambda: NERHalucinationEvaluator(ner_model, ner_entities, threshold=0.7),
        EXPECTED_RESPONSE_CHECK: lambda: LLMHBasedEvaluator(LLMEvaluation(llm=llm)),
        FUNCTION_CALLINGS_CHECK: lambda: FunctionCallCheckEvaluator(),
    }
    instantiated = []
    for e_name in selected_evaluations:
        if e_name in evaluators_map:
            instantiated.append(evaluators_map[e_name]())
        else:
            print(f"Warning: Unknown evaluator {e_name}")
    return instantiated



def run_evaluation_pipeline(
        algorithms:List, conversation_logs:List,
        simulation_steps:List, llm:LLMModel, ner_model:Any, 
        ner_entities:List, ner_threshold:float=0.7):
    if not algorithms:
        raise Exception("Please pass algorithm to run")
    if [1 for alg in algorithms if alg.upper() not in ALL_ALGORITHMS]:
        raise Exception(f"Please pass valid algorithms from : {ALL_ALGORITHMS}. Or If you have any new algoritm included please add same in the helping_functions/algorithms file.")
    

    # Create the list of Evaluator objects
    evaluators = create_evaluators(algorithms, llm, ner_model, ner_entities)

    # Optionally, create a step validator
    # step_validator = StepOrderValidator(simulation_steps)

    # add Scorer
    # scorer = QueryScorer(halucination_threshold=ner_threshold)

    # Run pipeline
    results, steps_in_order, final_score = evaluate(
        conversation_logs=conversation_logs,
        simulation_steps=simulation_steps,
        evaluators=evaluators,
        step_validator=None,
        llm=llm,
        scorer=None # for now Score is Not needed. But pass here Scorer
    )
    return results, steps_in_order, final_score
    

