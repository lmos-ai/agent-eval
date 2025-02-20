# app.py
from flask import Blueprint, request, jsonify
from dataclasses import asdict
from llm.llm import LLMModel
from conversations.pipeline import ConversationService
from data_model.evaluation import EvaluationRequestSchema
from marshmallow import ValidationError
from simulation.pipeline import SimulationProcessor
from simulation.test_case_parser import TestCaseParser
from typing import List, Dict
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
# -------------------- API FOR DATA FORMATTING --------------------
@evaluation_bp.route("/format-data", methods=['POST'])
def format_input_conversation():
    """
    Format conversation data for preprocessing.

    Expected Input (JSON):
    {
        "conversation_thread_id": "abc123",
        "input_data": { ... }
    }

    Responses:
    - 200: Successful response with formatted conversation data.
    - 400: Missing required parameters.
    - 500: Internal server error.
    """
    data = request.get_json()

    if not data:
        return ApiResponse.bad_request("Request body cannot be empty.")

    conversation_thread_id = data.get("conversation_thread_id")
    input_data = data.get("input_data")

    if not conversation_thread_id:
        return ApiResponse.bad_request("Missing 'conversation_thread_id' parameter.")
    if not input_data:
        return ApiResponse.bad_request("Missing 'input_data' parameter.")

    try:
        #################################################################
        # Below Are the interfaces classes for formatting the conversation

        # 1, Input Formatter: When you have your own conversation, then you have to overwrite the below InputConversationsFormator class
        #    And change the logic to return same type of format that evaluator expects.
        input_conversation_formatter = InputConversationsFormator()

        # 2, Automatic Conversation Generator: This is under progress. When you want to contact with your agent in realtime and generate the
        #    conversation such that it satisfy the evalyator input format, then overwrite the AutomaticConversationGenerator class
        automatic_conversation_formatter = AutomaticConversationGenerator()



        service = ConversationService(
            conversation_formator=input_conversation_formatter,
            automatic_conversation_generator=automatic_conversation_formatter
            )
        response = service.get_conversation(input_json=input_data)
        print("[SUCCESS] Got the formatted conversation")
        return ApiResponse.success(data=asdict(response), message="Conversation formatted successfully.")

    except Exception as e:
        print(f"[!] Exception for conversation_id {conversation_thread_id}: {str(e)}")
        return ApiResponse.internal_server_error(message=str(e))
    
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
        #---------------------------------------------------------------------------
        # Create Specifications/Simulations from the Test Cases
        #---------------------------------------------------------------------------
        simulation_processor = SimulationProcessor(
            llm=llm,
            test_cases=data['test_cases'],
            use_case=data.get("use_case"),
            json_testclass_parser=JSONTestCaseParser   # For your own JSON parser for simulation. Please owerrite the JSONTestCaseParser class
        )
        simulation_steps = simulation_processor.run()

        # Format Conversation Logs
        conversations: List[List[Dict]] = data['conversation_logs']
        if not isinstance(conversations[0], dict):
            return ApiResponse.bad_request("conversation_logs must be a list of JSON objects. Each object should represent a conversation.")

        results = []
        final_score_avg = []
        print("[.] Started Evaluation")
        for i, conversation in enumerate(conversations):
            print("[.] Formatting the conversation")
            conversation_service = ConversationService(
                automatic_conversation_generator=automatic_conversation_formatter,
                conversation_formator=input_conversation_formatter
            )
            conversation_logs = conversation_service.get_conversation(conversation).conversation_entries
            print("[.] Evaluating the formatted conversation")
            # Evaluate the AI agent and pass the simulation and conversation
            response = evaluation_pipeline(
                llm=llm,
                simulation_steps=simulation_steps,
                conversation_log=conversation_logs,
                ner_model=GliNerMODEL(config.GLINER_MODEL).model,
                algorithms=[EXPECTED_RESPONSE_CHECK]
            )

            if not response:
                results.append(None)
            else:
                df, are_steps_in_order, final_score = response
                df: pd.DataFrame = df
                unique_id = generate_uuid()
                df.to_csv(f"evaluation_reports/{data['use_case']}_{unique_id}.csv")
                df_json = df.to_json()

                results.append({
                    "id": unique_id,
                    "report": df_json,
                    "score": final_score,
                    "are_steps_in_order": are_steps_in_order
                })
                final_score_avg.append(final_score)
        print("[.] Saving Evaluation results in MongoDB")
        # Initialize MongoDB service
        mongo_service = MongoDBService(db_name=config.MONGO_DATABASE, uri=config.MONGO_URI)

        # Save evaluation data
        mongo_response = mongo_service.save_evaluation_data(final_score_avg, results)

        # Return the result
        print("[SUCCESS] Success in evaluation")
        return ApiResponse.success(data={"id": mongo_response}, message="Evaluation completed successfully.")

    except Exception as e:
        print(f"[!] Unexpected Error: {str(e)}")
        return ApiResponse.internal_server_error()


@evaluation_bp.route("/get-result", methods=['GET'])
def get_evaluation_result():
    """
    Fetch evaluation results by ID.
    
    Example Request:
    GET /api/evaluation/get-result?id=your_unique_id

    Response:
    {
        "status": "success",
        "message": "Evaluation data retrieved successfully",
        "data": {
            "final_score": 0.85,
            "results": [...]
        }
    }
    """
    eval_id = request.args.get("id")  # Fetch ID from query params

    if not eval_id:
        return ApiResponse.bad_request(message="Missing 'id' parameter")

    try:
        # Initialize MongoDB service
        mongo_service = MongoDBService(db_name=config.MONGO_DATABASE, uri=config.MONGO_URI)

        data = mongo_service.get_evaluation_data(eval_id)

        if not data:
            return ApiResponse.internal_server_error(message="No data found for the given ID")

        return ApiResponse.success(data=data,message="Evaluation data retrieved successfully")

    except Exception as e:
        print(f"[!] Unexpected Error: {str(e)}")
        return ApiResponse.internal_server_error(message="Internal Server Error")
