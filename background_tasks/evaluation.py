from simulation.pipeline import SimulationProcessor
from llm.llm import LLMModel
from conversations.pipeline import ConversationService
from typing import List, Dict
from evaluator import evaluation_pipeline
from helper_functions.algorithms import EXPECTED_RESPONSE_CHECK
from helper_functions.utils import generate_uuid
from models.gliner_model import GliNerMODEL
from helper_functions.mongo_utils import MongoDBService
import pandas as pd
from conversations.conversation_generator import AutomaticConversationGenerator
from conversations.conversation_format import InputConversationsFormator
from config import Config
from global_variable import BACKGROUND_TASK_COLLECTION, RUNNING_STATUS, TASK_FAILED_STATUS, TASK_COMPLETED_STATUS, DATA_EVALUATING, DATA_PREPROCESSING, DATA_RESULTS_SAVING
import logging
from data_model.evaluation import PipelineEvaluationResponse
config = Config()


def llm_black_box_evaluation_task(
        llm:LLMModel,
        task_id:str, data:dict, 
        json_parser, automatic_conversation_formatter:AutomaticConversationGenerator, 
        input_conversation_formatter:InputConversationsFormator):
    
    try:
        print(f"Starting Task for  task_id: {task_id}")
        mongo_service = MongoDBService(db_name=config.MONGO_DATABASE, uri=config.MONGO_URI, collection=BACKGROUND_TASK_COLLECTION)
        mongo_service.update_document(
            id=task_id, data = {"task_status": DATA_PREPROCESSING}
        )
        
        #---------------------------------------------------------------------------
        # Create Specifications/Simulations from the Test Cases
        #---------------------------------------------------------------------------
        simulation_processor = SimulationProcessor(
            llm=llm,
            test_cases=data['test_cases'],
            use_case=data.get("use_case"),
            json_testclass_parser=json_parser   # For your own JSON parser for simulation. Please owerrite the JSONTestCaseParser class
        )
        simulation_steps = simulation_processor.run()

        # Format Conversation Logs
        conversations: List[List[Dict]] = data['conversation_logs']
        if not isinstance(conversations[0], dict):
            mongo_service.update_document(
                id=task_id, data = {"task_status": TASK_FAILED_STATUS}
            )

        results = []
        final_score_avg = []
        print("[.] Started Evaluation")
        mongo_service.update_document(
            id=task_id, data = {"task_status": DATA_EVALUATING}
        )
        for i, conversation in enumerate(conversations):
            print(f"[.] Formatting the conversation for taskId: {task_id}")
            conversation_service = ConversationService(
                automatic_conversation_generator=automatic_conversation_formatter,
                conversation_formator=input_conversation_formatter
            )
            conversation_logs = conversation_service.get_conversation(conversation).conversation_entries
            print(f"[.] Evaluating the formatted conversation for taskId: {task_id}")
            # Evaluate the AI agent and pass the simulation and conversation
            response = evaluation_pipeline(
                llm=llm,
                simulation_steps=simulation_steps,
                conversation_log=conversation_logs,
                ner_model=GliNerMODEL(config.GLINER_MODEL).model,
                algorithms=[EXPECTED_RESPONSE_CHECK]
            )
            unique_id = generate_uuid()
            if not response:
                results.append(PipelineEvaluationResponse(
                    id=unique_id,
                    results=[],
                    final_score=0,
                    are_steps_in_order=None
                ))
            else:
                result, are_steps_in_order, final_score = response
                
                
                
                results.append(PipelineEvaluationResponse(
                    id=unique_id,
                    results=result,
                    final_score=final_score,
                    are_steps_in_order=str(are_steps_in_order)
                ))
                final_score_avg.append(final_score)
        mongo_service.update_document(
            id=task_id, data = {"task_status": RUNNING_STATUS}
        )
        print(f"[.] Saving Evaluation results in MongoDB for task id: {task_id}")
        # Initialize MongoDB service
        
        mongo_service.update_document(
            id=task_id, data = {"task_status": DATA_RESULTS_SAVING}
        )
        # Save evaluation data
        evaluation_data_service= MongoDBService(db_name=config.MONGO_DATABASE, uri=config.MONGO_URI, collection=config.EVALUATION_COLLECTION)
        mongo_response = evaluation_data_service.save_evaluation_data(final_score_avg, [result.dict() for result in results])

        # Return the result
        mongo_service.update_document(
            id=task_id, data = {"task_status": TASK_COMPLETED_STATUS, "evaluation_result_id": mongo_response}
        )
        print(f"[SUCCESS] Success in evaluation for task_id: {task_id}")

    except Exception as e:
        print(f"[!] Unexpected Error for task Id: {task_id}: {str(e)}")
        mongo_service.update_document(
                id=task_id, data = {"task_status": TASK_FAILED_STATUS}
        )