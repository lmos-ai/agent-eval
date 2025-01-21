from llm.llm import LLMModel
from evaluators.steps_evaluator import run_llm_evaluator_pipeline_with_validations






def evaluation_pipeline( conversation_log:dict, use_case_evaluation:dict, llm:LLMModel, check_protocols:bool=True):
    """
    Parameters:
    - agent_usecases (dict): Contains use case information like description, steps, expected response, and examples.
    - conversation_log (dict): The conversation between the agent and the user.
    - use_case_evaluation (dict): Contains details of the top use case, sub-use case, steps to follow, and example conversations to evaluate.
    - llm (Any): LLM instance

    Returns:
    - dict: The formatted dict having evaluation.
    """
    if not conversation_log or not use_case_evaluation:
        raise ValueError("Invalid input parameters")
    if llm is None:
        raise ValueError("LLM passed is None. Please check.")
    
    json_response = {}

    if check_protocols:
        run_llm_evaluator_pipeline_with_validations(
            conversation_logs=conversation_log,
            simulation_steps=use_case_evaluation,
            llm=llm
        )
        
    
    # return json_response