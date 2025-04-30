AZURE_LLM = "AZURE_LLM"
LOCAL_LLM = "LOCAL_LLM"
OPENAI_LLM = "OPENAI_LLM"
LLM_SOURCES = [AZURE_LLM, LOCAL_LLM, OPENAI_LLM]
NER_ENTITIES = ["person names", "serivicies names", "time", "day or date", "processess names or status", "account information like user id, branch name, account type, balance in amount or text, etc ", "academics information like name, age, subjects, etc", "amount", "any numbers", "personal credentials like gender, age, name, father name and etc"]
BACKGROUND_TASK_COLLECTION = "background_tasks"
OPENTELEMETRY_TRACES_COLLECTION='open_telemetery_traces'
RUNNING_STATUS = "TASK_RUNNING"
TASK_COMPLETED_STATUS = "TASK_COMPLETED"
TASK_FAILED_STATUS = "TASK_FAILED"
TASK_STARTED="TASK_STARTED"
DATA_PREPROCESSING = "DATA_PREPROCESSING"
DATA_EVALUATING="EVALUATION_INPROGRESS"
DATA_RESULTS_SAVING="DATA_RESULTS_SAVING"


# OTEL traces
OTEL_SPAN_INPUT_KEY='operation.input'
OTEL_SPAN_OUTPUT_KEY='operation.return_value'
OTEL_SPAN_CONVERSATION_ID='conversation_id'
