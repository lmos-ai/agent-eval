import os
from helper_functions.utils import SingletonClass
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
