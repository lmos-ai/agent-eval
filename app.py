# app.py
from flask import Flask, render_template, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from src.routes import evaluation_bp, ui_route_bp
from config import Config
from flask_cors import CORS
from flasgger import Swagger
config = Config()

app = Flask(__name__)
CORS(app)  # Enable CORS

# Swagger template based on the previously defined spec
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "LLM Evaluation API",
        "description": (
            "API for asynchronous LLM evaluation, conversation formatting, "
            "evaluation result retrieval, and background task status monitoring."
        ),
        "version": "1.0.0"
    },
    "basePath": "/evaluation",
    "schemes": [
        "http",
        "https"
    ],
    "paths": {
        "/evaluate-llm": {
            "post": {
                "summary": "Evaluate LLM performance asynchronously",
                "description": (
                    "Initiates an asynchronous evaluation of an LLM using the provided "
                    "test cases and conversation logs. Returns a task ID to track the evaluation status."
                ),
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "description": "Evaluation input parameters",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "unique_id": {
                                    "type": "string",
                                    "description": "Unique ID for tracking the evaluation."
                                },
                                "use_case": {
                                    "type": "string",
                                    "description": "Use case or agent name for evaluation."
                                },
                                "conversation_logs": {
                                    "type": "array",
                                    "items": {"type": "object"},
                                    "description": "List of conversation logs between user and assistant."
                                },
                                "test_cases": {
                                    "type": "array",
                                    "items": {"type": "object"},
                                    "description": "List of test cases for evaluating the LLM."
                                }
                            },
                            "required": ["unique_id", "use_case", "conversation_logs", "test_cases"]
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Task started successfully and returns task ID.",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "data": {
                                    "type": "object",
                                    "properties": {
                                        "task_id": {"type": "string"},
                                        "status": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {"description": "Invalid input parameters."},
                    "500": {"description": "Internal server error."}
                }
            }
        },
        "/get-evaluation-result": {
            "get": {
                "summary": "Fetch evaluation results by ID",
                "description": (
                    "Retrieves evaluation results based on the provided evaluation result ID. "
                    "The result includes final score and detailed evaluation metrics."
                ),
                "parameters": [
                    {
                        "name": "id",
                        "in": "query",
                        "description": "The unique evaluation result ID",
                        "required": True,
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Evaluation data successfully retrieved.",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "message": {"type": "string"},
                                "data": {"type": "object"}
                            }
                        }
                    },
                    "400": {"description": "Missing or invalid 'id' parameter."},
                    "500": {"description": "Internal server error."}
                }
            }
        },
        "/task-status/{task_id}": {
            "get": {
                "summary": "Get background task status",
                "description": (
                    "Retrieves the status of a background evaluation task. If completed, returns the "
                    "evaluation result ID; otherwise, only the current status is returned."
                ),
                "parameters": [
                    {
                        "name": "task_id",
                        "in": "path",
                        "description": "Unique ID of the background task",
                        "required": True,
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Task status retrieved successfully.",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "data": {
                                    "type": "object",
                                    "properties": {
                                        "task_id": {"type": "string"},
                                        "status": {"type": "string"},
                                        "evaluation_result_id": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {"description": "Invalid or missing task_id parameter."},
                    "404": {"description": "Task not found."},
                    "500": {"description": "Internal server error."}
                }
            }
        }
    }
}


# Initialize Swagger with the above template
swagger = Swagger(app, template=swagger_template)


# # Swagger setup
# SWAGGER_URL = "/swagger"
# API_URL = "/static/swagger.json"  # Location of swagger.json

# swagger_bp = get_swaggerui_blueprint(
#     SWAGGER_URL,
#     API_URL,
#     config={"app_name": "Black Box Evaluation API"}
# )

# # Register Swagger blueprint
# app.register_blueprint(swagger_bp, url_prefix=SWAGGER_URL)

# # Serve swagger.json file
# @app.route("/static/swagger.json")
# def serve_swagger():
#     return send_from_directory("static", "swagger.json")

@app.route("/")
def index():
    return render_template("index.html")

app.register_blueprint(ui_route_bp, url_prefix='/ui')
app.register_blueprint(evaluation_bp, url_prefix='/evaluation')



if __name__ == "__main__":
    app.run(debug=True)
