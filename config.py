import os
from helper_functions.utils import SingletonClass
from global_variable import AZURE_LLM, OPENAI_LLM
from dotenv import load_dotenv

load_dotenv(".env",override=True)

class Config(metaclass=SingletonClass):
    def __init__(self) -> None:
        self.read_env()
    def read_env(self):
        
        self.LLM_ENDPOINT = os.environ.get("LLM_ENDPOINT")
        self.API_KEY = os.environ.get("API_KEY")
        self.MODEL_NAME = os.environ.get("MODEL_NAME")
        self.FLASK_RUN_HOST = os.environ.get("FLASK_RUN_HOST")
        self.FLASK_RUN_HOST = os.environ.get("FLASK_RUN_HOST")
        self.GLINER_MODEL = os.environ.get("GLINER_MODEL")
        self.MONGO_URI = os.environ.get("MONGO_URI")
        self.MONGO_DATABASE = os.environ.get("MONGO_DATABASE")
        model_source = os.environ.get("MODEL_SOURCE")
        if model_source.upper() == AZURE_LLM:
            self.MODEL_SOURCE = AZURE_LLM
        elif model_source.upper() == OPENAI_LLM:
            self.MODEL_SOURCE = OPENAI_LLM
        else:
            raise Exception(f"For Model source please choose between {[AZURE_LLM, OPENAI_LLM]}")
