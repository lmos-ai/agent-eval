from pymongo import MongoClient
import json
from uuid import uuid4

class MongoDBService:
    def __init__(self, db_name:str, uri:str="mongodb://localhost:27017/"):
        """
        Initialize MongoDB connection.
        """
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db["evaluation_results"]

    def get_evaluation_data(self, eval_id: str):
        """
        Fetch evaluation data by ID.

        :param eval_id: Unique ID of evaluation result.
        :return: Evaluation data or None if not found.
        """
        result = self.collection.find_one({"_id": eval_id}, {"_id": 0})  # Exclude _id in response
        return result

    def save_evaluation_data(self, final_score, results):
        """
        Save evaluation results in MongoDB.

        :param final_score: Final evaluation score (float)
        :param results: List of JSON objects containing score and df_json
        :return: MongoDB insertion response
        """
        # Generate unique ID for the document
        unique_id = str(uuid4())

        # Construct MongoDB document
        document = {
            "_id": unique_id,
            "final_score": final_score,
            "results": results
        }

        # Insert document into MongoDB
        self.collection.insert_one(document)
        return str(unique_id)
