from llm.llm import LLMModel
import os
from dotenv import load_dotenv
from evaluator import evaluation_pipeline
from data.demo_data import conversations, simulations

from config import Config
config = Config()

load_dotenv('.env', override=True)

llm = LLMModel(
    api_key=config.API_KEY,
    model_name=config.MODEL_NAME,
    model_source=config.MODEL_SOURCE,
)

# ----------------------------------
# Evaluate

evaluation_pipeline(
    use_case_evaluation=simulations,
    conversation_log=conversations,
    llm=llm
)