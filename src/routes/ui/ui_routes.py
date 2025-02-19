# app.py
from flask import Blueprint, request, render_template, jsonify
import pandas as pd
from data.demo_data1 import conversations, simulations
from evaluators.pipeline import evaluate  
from llm.llm import LLMModel
from config import Config
from models.gliner_model import GliNerMODEL
from global_variable import NER_ENTITIES
config = Config()

ui_route_bp = Blueprint('ui_route_bp', __name__)

llm = LLMModel(
    api_key=config.API_KEY,
    model_name=config.MODEL_NAME,
    model_source=config.MODEL_SOURCE,
    llm_endpoint=config.LLM_ENDPOINT
)



@ui_route_bp.route("/")
def index():
    return render_template("index.html")


########################################################################
# ------------------- BELOW APIS ARE FOR UI MAINLY ---------------------
########################################################################
@ui_route_bp.route("/entities")
def get_entities():
    # Example list (in practice, fetch from DB or external source)
    return jsonify(NER_ENTITIES)

@ui_route_bp.route("/conversations", methods=["GET"])
def get_conversations():
    try:
        conversation_list = [
            {"id": key, "name": key}
            for key in conversations.keys()
        ]
        return jsonify(conversation_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ui_route_bp.route("/conversations/<conversation_id>", methods=["GET"])
def get_conversation_details(conversation_id):
    try:
        conversation_data = conversations.get(conversation_id)
        if not conversation_data:
            return jsonify({"error": "Conversation not found"}), 404
        return jsonify({
            "id": conversation_id,
            "logs": conversation_data
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ui_route_bp.route("/simulations", methods=["GET"])
def get_simulations():
    try:
        simulation_list = [
            {
                "id": key,
                "name": f"{value['use_case']} - {value['sub_use_case']}"
            }
            for key, value in simulations.items()
        ]
        return jsonify(simulation_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ui_route_bp.route("/simulations/<simulation_id>", methods=["GET"])
def get_simulation_details(simulation_id):
    try:
        sim_data = simulations.get(simulation_id)
        if not sim_data:
            return jsonify({"error": "Simulation not found"}), 404
        return jsonify({
            "id": simulation_id,
            "use_case": sim_data["use_case"],
            "sub_use_case": sim_data["sub_use_case"],
            "steps": sim_data["steps"]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ui_route_bp.route("/evaluate", methods=["POST"])
def evaluate():
    """
    Handle evaluation pipeline for multiple conversations, one simulation.
    """
    try:
        # Retrieve multiple conversation IDs
        conversation_ids = request.form.getlist("conversation_id[]")
        simulation_id = request.form.get("simulation_id")
        halucination_threshold = request.form.get("halucination_threshold")
        selected_entities = list(request.form.getlist("entitySelect"))
        
        # halucination_threshold=0.7
        print(f"Got Halucination Threshold :{halucination_threshold}")
        print(f"Selected NER entities are: {selected_entities}")

        # Validate simulation
        simulation = simulations.get(simulation_id)
        if not simulation:
            return jsonify({"error": "Invalid simulation selected"}), 400

        steps = simulation["steps"]

        # We'll collect each conversation's score and partial HTML
        results = []
        total_score = 0.0
        valid_count = 0
        dfs = []

        for cid in conversation_ids:
            # For each conversation, run the pipeline
            conversation = conversations.get(cid)
            if not conversation:
                # Could skip or handle error
                continue

            df, are_steps_in_order, final_score = evaluate(
                simulation_steps=steps,
                conversation_logs=conversation,
                llm=llm,
                gliner_model= 1, #TODO uncomment for NER GliNerMODEL(config.GLINER_MODEL).model,
                halucination_threshold=float(halucination_threshold),
                ner_entities = selected_entities
            )
            dfs.append(df)
            partial_html = df.to_html(
                classes="table table-bordered table-striped",
                index=False
            )

            # Sum up scores for average
            total_score += float(final_score)
            valid_count += 1

            results.append({
                "conversation_id": cid,
                "dataframe": partial_html,
                "final_score": final_score,
                "steps_in_order":are_steps_in_order
            })

        # Overall average
        overall_final_score = 0.0
        if valid_count > 0:
            overall_final_score = total_score / valid_count
        final_report_df = pd.concat(dfs)
        final_report_df.to_csv("./evaluation_reports/"+cid+".csv")
        return jsonify({
            "results": results,
            "overall_final_score": overall_final_score
        })
    except Exception as e:
        print(f"Got Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

