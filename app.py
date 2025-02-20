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
        "description": "API for LLM evaluation and conversation data formatting",
        "version": "1.0.0"
    },
    "basePath": "/evaluation",
    "schemes": [
        "http",
        "https"
    ],
    "paths": {
        "/format-data": {
            "post": {
                "summary": "Format conversation data for preprocessing",
                "description": "This API formats conversation data before it is sent for further processing or evaluation.",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "description": "Input data for formatting",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "conversation_thread_id": {"type": "string"},
                                "input_data": {"type": "object"}
                            },
                            "required": ["conversation_thread_id", "input_data"]
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful response with formatted conversation data.",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "message": {"type": "string"},
                                "data": {"type": "object"}
                            }
                        }
                    },
                    "400": {"description": "Missing required parameters."},
                    "500": {"description": "Internal server error."}
                }
            }
        },
        "/evaluate-llm": {
            "post": {
                "summary": "Evaluate LLM performance",
                "description": "This endpoint evaluates an LLM by running simulations based on the input test cases and conversation logs.",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "description": "Evaluation input parameters",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "use_case": {"type": "string"},
                                "conversation_logs": {
                                    "type": "array",
                                    "items": {"type": "object"}
                                },
                                "test_cases": {
                                    "type": "array",
                                    "items": {"type": "object"}
                                }
                            },
                            "required": ["use_case", "conversation_logs", "test_cases"]
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Evaluation results successfully retrieved.",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "message": {"type": "string"},
                                "data": {"type": "object"}
                            }
                        }
                    },
                    "400": {"description": "Invalid input parameters."},
                    "500": {"description": "Internal server error."}
                }
            }
        },
        "/get-result": {
            "get": {
                "summary": "Fetch evaluation results by ID",
                "description": "This endpoint retrieves evaluation results based on the provided evaluation ID.",
                "parameters": [
                    {
                        "name": "id",
                        "in": "query",
                        "description": "The unique evaluation ID",
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
                    "400": {"description": "Missing 'id' parameter."},
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
