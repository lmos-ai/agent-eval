from pymongo import MongoClient
import json
from uuid import uuid4

class MongoDBService:
    def __init__(self, db_name:str, collection:str, uri:str="mongodb://localhost:27017/"):
        """
        Initialize MongoDB connection.
        """
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection]

    def save_document(self, document: dict):
        """
        Save a document to MongoDB.

        :param document: A dictionary representing the document to save.
        :return: The unique ID of the inserted document as a string.
        """
        result = self.collection.insert_one(document)
        return str(result.inserted_id)
    
    def update_document(self, id: str, data: dict):
        """
        Update an existing document in MongoDB.

        :param id: The unique ID of the document to update.
        :param data: A dictionary containing the fields to update.
        :return: The number of documents modified.
        """
        result = self.collection.update_one({"task_id": id}, {"$set": data})
        return result.modified_count
    
    def get_document(self, filter: dict):
        """
        Fetch a document from MongoDB based on a filter.

        :param filter: Dictionary representing the filter criteria.
        :return: Document if found, None otherwise.
        """
        result = self.collection.find_one(filter)
        if result:
            result.pop('_id', None)  # Remove _id for cleaner output
        return result
    

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
