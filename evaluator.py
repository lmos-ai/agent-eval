from llm.llm import LLMModel
from evaluators import run_evaluation_pipeline
from global_variable import NER_ENTITIES
from config import Config
from typing import List
from models.gliner_model import GliNerMODEL
from helper_functions.algorithms import EXPECTED_RESPONSE_CHECK, FUNCTION_CALLINGS_CHECK, NER_HALUCINATION, STEPS_IN_ORDER

config = Config()

valid_algorithms = [EXPECTED_RESPONSE_CHECK, FUNCTION_CALLINGS_CHECK, NER_HALUCINATION, STEPS_IN_ORDER]



def evaluation_pipeline(conversation_log:dict, 
                        llm:LLMModel, simulation_steps:dict, 
                        algorithms:List=[], ner_model=None,ner_threshold:float=0.7):
    """
    Parameters:
    - conversation_log (dict): The conversation between the agent and the user.
    - llm (LLMModel): LLM instance
    - simulation_steps (dict): simulation_steps for evaluating with.

    
    """
    if not conversation_log:
        raise ValueError("Invalid input parameters")
    elif not algorithms:
        raise Exception("Algoritms to perform is empty. Please pass valid algorithms")
    elif not [1 for algo in algorithms if algo.upper() in valid_algorithms]:
        raise Exception(f"Algorithm passed in algorithms list is invalid. Please choose from : {valid_algorithms}")
    elif llm is None:
        raise ValueError("LLM passed is None. Please check.")
    elif not simulation_steps:
        raise ValueError("Pass simulation_gerenerator class instance.")
    elif not isinstance(simulation_steps, dict):
        raise Exception("Make sure the simulation_generator is of dict type")
    try:
        results, are_steps_in_order, final_score = run_evaluation_pipeline(
                                                algorithms=algorithms,
                                                ner_threshold=ner_threshold,
                                                conversation_logs=conversation_log,
                                                simulation_steps=simulation_steps,
                                                llm=llm,
                                                ner_entities=NER_ENTITIES,
                                                ner_model=ner_model
                                            )
        return [results, are_steps_in_order, final_score]
    except Exception as e:
        print(f"Got exception while evaluating: {e}")
        return None
