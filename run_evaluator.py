from llm.llm import LLMModel
from global_variable import OPENAI_LLM
import os
from dotenv import load_dotenv
from evaluator import evaluation_pipeline
from data.demo_data import conversations, simulations



load_dotenv('.env', override=True)

llm = LLMModel(
    api_key=os.getenv('API_KEY'),
    model_name="gpt-4o",
    model_source=OPENAI_LLM,
)

# ----------------------------------
# Evaluate

evaluation_pipeline(
    use_case_evaluation=simulations,
    conversation_log=conversations,
    llm=llm
)