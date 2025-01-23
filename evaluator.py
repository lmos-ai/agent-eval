from llm.llm import LLMModel
from evaluators.steps_evaluator import run_llm_evaluator_pipeline_with_validations
from global_variable import NER_ENTITIES





def evaluation_pipeline( conversation_log:list, use_case_evaluation:list, llm:LLMModel, check_protocols:bool=True):
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
    scores = {}
    steps_in_order = {}
    if check_protocols:
        for simulation in use_case_evaluation:
            for conversation in conversation_log:
                df, are_steps_in_order, final_score = run_llm_evaluator_pipeline_with_validations(
                                                        conversation_logs=conversation,
                                                        simulation_steps=simulation,
                                                        llm=llm,
                                                        halucination_threshold=0.7,
                                                        ner_entities=NER_ENTITIES
                                                    )
                df.to_csv("./evaluation_reports/"+conversation+".csv")
                scores[conversation] = final_score
                steps_in_order[conversation] = are_steps_in_order
    
    print("--------------------------------")
    print("---------Evaluation Report------\n")
    for conversation in conversation_log:
        print(f"Conv: {conversation} || Score: {scores[conversation]} || Steps in Order: {steps_in_order[conversation]}")
    print("\n---------------------------------")

        
    
    return steps_in_order, scores, sum(scores.keys())/len(scores)