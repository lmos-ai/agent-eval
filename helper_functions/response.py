import json
import re
from typing import Optional, Dict
from flask import jsonify

def extract_json_from_string(text: str) -> Optional[Dict]:
    try:
        # Simple pattern: look for something that starts with '{' and ends with '}'
        # This won't handle nested braces as robustly, but might work for simpler cases
        json_pattern = re.compile(r"\{.*?\}", re.DOTALL)

        match = json_pattern.search(text)
        if match:
            json_str = match.group()
            return json.loads(json_str)
        else:
            print("[!] No valid JSON found in the string.")
            return None

    except json.JSONDecodeError as e:
        print(f"⚠️ Error decoding JSON: {e}")
        return None
    

class ApiResponse:
    """
    Class for structuring API responses.
    """

    @staticmethod
    def success(data=None, message="Success"):
        """
        Standard success response.
        """
        return jsonify({
            "status": "success",
            "message": message,
            "data": data
        }), 200

    @staticmethod
    def bad_request(message="Bad request. Invalid input parameters."):
        """
        400 - Bad request response.
        """
        return jsonify({
            "status": "error",
            "message": message
        }), 400

    @staticmethod
    def unauthorized(message="Unauthorized access. Please check your credentials."):
        """
        401 - Unauthorized response.
        """
        return jsonify({
            "status": "error",
            "message": message
        }), 401

    @staticmethod
    def forbidden(message="Forbidden request. You don't have permission to access this resource."):
        """
        403 - Forbidden response.
        """
        return jsonify({
            "status": "error",
            "message": message
        }), 403

    @staticmethod
    def not_found(message="Resource not found. Please check the provided ID."):
        """
        404 - Not found response.
        """
        return jsonify({
            "status": "error",
            "message": message
        }), 404

    @staticmethod
    def conflict(message="Conflict occurred. Resource already exists or request is invalid."):
        """
        409 - Conflict response.
        """
        return jsonify({
            "status": "error",
            "message": message
        }), 409

    @staticmethod
    def internal_server_error(message="Internal server error. Please try again later."):
        """
        500 - Internal server error response.
        """
        return jsonify({
            "status": "error",
            "message": message
        }), 500
