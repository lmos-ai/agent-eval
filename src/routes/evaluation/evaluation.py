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
@evaluation_bp.route("/api/data-preprocessing/format-data", methods=['POST'])
def format_input_conversation():
    data = request.get_json()
    conversation_thread_id = data.get("conversation_thread_id")
    input_data = data.get("input_data")
    try:
        service =  ConversationService()
        response =  service.get_conversation(input_json=input_data)
        return asdict(response)
    except Exception as e:
        print(f"Got exception for conversation id: {conversation_thread_id}. Exceprion: {e}")
        return None
    

@evaluation_bp.route("/evaluate-llm", methods = ['POST'])
def evaluate():
    """Endpoint for LLM evaluation."""
    schema = EvaluationRequestSchema()
    try:
        # Validate the incoming JSON data
        data = schema.load(request.json)
    except ValidationError as exc:
        # Marshmallow validation failed
        return jsonify({"error": exc.messages}), 400
    
    # Optionally, do additional custom validations
    if not data['use_case'].strip():
        return jsonify({"error": "use_case cannot be empty"}), 400
    elif not data['conversation_logs']:
        return jsonify({"error": "conversation_logs cannot be None or empty"}), 400
    elif not data['test_cases']:
        return jsonify({"error": "test_cases cannot be None or empty"}), 400
    try:


        # Main code

        #---------------------------------------------------------------------------
        # Create Specifications/Simulations from the Test Cases
        #---------------------------------------------------------------------------

        simulation_processor = SimulationProcessor(
            llm=llm,
            test_cases=data['test_cases'],
            use_case=data.get("use_case"),
            json_testclass_parser=JSONTestCaseParser
        )
        simulation_steps = simulation_processor.run()

        # Format Conversation Logs
        conversations:List[List[Dict]] = data['conversation_logs']
        if not isinstance(conversations[0], dict):
            return jsonify({"error": "conversation_logs must be list of jsons. Each json as a conversation"}), 400
        
        results = []
        final_score_avg = []
        for i, conversation in enumerate(conversations):
            conversation_service = ConversationService()
            conversation_logs = conversation_service.get_conversation(conversation).conversation_entries

            # Evaluate the Ai agent and pass the simulation and conversation
            response = evaluation_pipeline(
                llm=llm,
                simulation_steps=simulation_steps,
                conversation_log=conversation_logs,
                ner_model = GliNerMODEL(config.GLINER_MODEL).model,
                algorithms=[EXPECTED_RESPONSE_CHECK]
            )
            if not response:
                results.append(None)
            else:
                df, are_steps_in_order, final_score = response
                df:pd.DataFrame = df
                unique_id = generate_uuid()
                df.to_csv(f"evaluation_reports/{data['use_case']}_{unique_id}.csv")
                df_json = df.to_json()

                results.append({
                    "id" : unique_id,
                    "report": df_json,
                    "score": final_score,
                    "are_steps_in_order":are_steps_in_order
                })
                final_score_avg.append(final_score)
        # Initialize MongoDB service
        mongo_service = MongoDBService(db_name=config.MONGO_DATABASE, uri=config.MONGO_URI)
        # Save evaluation data
        mongo_response = mongo_service.save_evaluation_data(final_score_avg, results)
        # Return the result
        return jsonify({"data": {"id":mongo_response}}), 200
    except Exception as e:
        print(f"Got exception: {e}")
        return jsonify({"error":"Server Error"}), 500


