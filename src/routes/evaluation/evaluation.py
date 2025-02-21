# app.py
from flask import Blueprint, request, jsonify
import uuid
from dataclasses import asdict
from llm.llm import LLMModel
from conversations.pipeline import ConversationService
from data_model.evaluation import EvaluationRequestSchema, BackgroundTaskStatusRequestSchema
from marshmallow import ValidationError
from simulation.pipeline import SimulationProcessor
from simulation.test_case_parser import TestCaseParser
from typing import List, Dict
from threading import Thread
from data_model.simulations import GroundTruthConversation
from evaluator import evaluation_pipeline
from helper_functions.algorithms import EXPECTED_RESPONSE_CHECK
from helper_functions.utils import generate_uuid
from config import Config
from models.gliner_model import GliNerMODEL
from data_model.conversation import ConversationResult
from helper_functions.mongo_utils import MongoDBService
import pandas as pd
from helper_functions.response import ApiResponse
from conversations.conversation_generator import AutomaticConversationGenerator
from conversations.conversation_format import InputConversationsFormator
from background_tasks.evaluation import llm_black_box_evaluation_task
from global_variable import BACKGROUND_TASK_COLLECTION, RUNNING_STATUS, TASK_COMPLETED_STATUS, TASK_FAILED_STATUS, TASK_STARTED


config = Config()


evaluation_bp = Blueprint('evaluation_bp', __name__)

llm = LLMModel(
    api_key=config.API_KEY,
    model_name=config.MODEL_NAME,
    model_source=config.MODEL_SOURCE,
    llm_endpoint=config.LLM_ENDPOINT
)


############################################################################################
# ------------------------------------Helper Functions--------------------------------------
############################################################################################


class JSONTestCaseParser(TestCaseParser):
    """
    Concrete implementation of TestCaseParser for JSON data format.
    This extracts the user query and expected response from messages.
    """

    def extract_conversations(self) -> List[GroundTruthConversation]:
        conversation_entries: List[GroundTruthConversation] = []

        # Loop through each test case
        for test_case in self.test_data.get("testCases", []):
            expected_data = test_case.get("expected", {})
            messages = expected_data.get("messages", [])

            # Ensure messages exist in pairs (user query -> bot response)
            for i in range(len(messages) - 1):
                if messages[i]["type"] == "user" and messages[i + 1]["type"] == "bot":
                    user_query = messages[i]["content"].strip()
                    response = messages[i + 1]["content"].strip()

                    # Append conversation entry
                    conversation_entries.append(GroundTruthConversation(user_query, response))

        return conversation_entries


##############################################################################################
# ------------------ BELOW APIS ARE FOR EVALUATION AND MAIN FUNCTIONALTY ---------------------
###############################################################################################

@evaluation_bp.route("/evaluate-llm", methods=['POST'])
def evaluate():
    """Endpoint for LLM evaluation."""

    #################################################################
    # Below Are the interfaces classes for formatting the conversation

    # 1, Input Formatter: When you have your own conversation, then you have to overwrite the below InputConversationsFormator class
    #    And change the logic to return same type of format that evaluator expects.
    input_conversation_formatter = InputConversationsFormator()

    # 2, Automatic Conversation Generator: This is under progress. When you want to contact with your agent in realtime and generate the
    #    conversation such that it satisfy the evalyator input format, then overwrite the AutomaticConversationGenerator class
    automatic_conversation_formatter = AutomaticConversationGenerator()



    schema = EvaluationRequestSchema()

    try:
        # Validate the incoming JSON data
        data = schema.load(request.json)
    except ValidationError as exc:
        print(f"[!] Validation Error: {exc.messages}")
        return ApiResponse.bad_request(message="Invalid input parameters. " + str(exc.messages))

    # Additional custom validations
    if not data['use_case'].strip():
        return ApiResponse.bad_request("use_case cannot be empty")
    if not data['conversation_logs']:
        return ApiResponse.bad_request("conversation_logs cannot be None or empty")
    if not data['test_cases']:
        return ApiResponse.bad_request("test_cases cannot be None or empty")
    try:
        # start evaluation in background
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        # Start the evaluation in a background thread
        thread = Thread(target=llm_black_box_evaluation_task, args=(llm, task_id, data, JSONTestCaseParser, automatic_conversation_formatter, 
                                                                    input_conversation_formatter))
        thread.daemon = True
        thread.start()
        mongo_service = MongoDBService(db_name=config.MONGO_DATABASE, uri=config.MONGO_URI, collection=BACKGROUND_TASK_COLLECTION)
        mongo_service.save_document(document={
            "task_id": task_id,
            "task_status": "running",
            "evaluation_result_id": None
        })
        return ApiResponse.success(data={"task_id":task_id, "task_status":TASK_STARTED})
    except Exception as e:
        print(f"[!] Got error in staring evaluation thread. Error is: {str(e)}")
        return ApiResponse.internal_server_error()


@evaluation_bp.route("/get-evaluation-result", methods=['GET'])
def get_evaluation_result():
    eval_id = request.args.get("id")  # Fetch ID from query params

    if not eval_id:
        return ApiResponse.bad_request(message="Missing 'id' parameter")

    try:
        # Initialize MongoDB service
        mongo_service = MongoDBService(db_name=config.MONGO_DATABASE, uri=config.MONGO_URI, collection=config.EVALUATION_COLLECTION)

        data = mongo_service.get_evaluation_data(eval_id)

        if not data:
            return ApiResponse.internal_server_error(message="No data found for the given ID")

        return ApiResponse.success(data=data,message="Evaluation data retrieved successfully")

    except Exception as e:
        print(f"[!] Unexpected Error: {str(e)}")
        return ApiResponse.internal_server_error(message="Internal Server Error")

@evaluation_bp.route("/task-status/<task_id>", methods=["GET"])
def get_backgroundtask_status(task_id: str):
    # Validate the task_id using the schema
    schema = BackgroundTaskStatusRequestSchema()
    try:
        # Since task_id is provided as a path parameter, we create a dict for validation
        validated_data = schema.load({"task_id": task_id})
    except ValidationError as err:
        return ApiResponse.bad_request(message="Please pass task_id returned from the evaluation API.")

    try:
        # Initialize MongoDBService for the background tasks collection
        mongo_service = MongoDBService(
            db_name=config.MONGO_DATABASE,
            uri=config.MONGO_URI,
            collection=BACKGROUND_TASK_COLLECTION
        )
        
        # Retrieve the task document based on the task_id
        task_document = mongo_service.get_document({"task_id": validated_data["task_id"]})
        if not task_document:
            return ApiResponse.not_found(f"No such task running for task_id: {validated_data['task_id']}")

        response = {
            "task_id": task_document.get("task_id"),
            "task_status": task_document.get("task_status")
        }
        
        # If the task is completed, include the evaluation_result_id
        if task_document.get("task_status") == TASK_COMPLETED_STATUS:
            if "evaluation_result_id" in task_document:
                response["evaluation_result_id"] = task_document.get("evaluation_result_id")
        
        return ApiResponse.success(data=response)
    except Exception as e:
        print(f"[!] Got Exception while checking status of background task with Task_id: {validated_data['task_id']}")
        return ApiResponse.internal_server_error()
