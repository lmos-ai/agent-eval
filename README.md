# Black Box Evaluation

## Overview

Black Box Evaluation is a system that evaluates any AI agent's performance while ensuring it follows all specified rules. It checks for hallucinations using a hybrid approach of Named Entity Recognition (NER) and Python. Additionally, it verifies whether the AI agent's response is correct and provides reasoning for correctness or incorrectness.

This project supports **asynchronous evaluations** using background tasks. When you submit an evaluation request, the system immediately returns a task ID, and the actual evaluation runs in a separate thread. You can query the status of this task at any time and retrieve the final results once the evaluation completes.

---

## Features

- Evaluates AI agent performance in an **asynchronous** manner.  
- Detects hallucinations using NER and Python.  
- Checks response correctness.  
- Provides reasoning for correct or incorrect responses.  
- Supports multiple evaluation techniques.  
- Includes a **background task** system with status polling.  

---

## Systems

### 1. Specifications

- Takes test use case conversations and creates simulations.
- Generates a detailed description, step names, expected function calls, and outputs.
- Defines trigger messages indicating when steps should be followed.

### 2. Agent Caller (In Progress)

- Connects with the AI agent based on its description and simulation.
- Generates conversations for evaluation.
- Allows users to pass their own conversation for evaluation.
- Uses a **Conversation Converter Interface** to format conversations correctly for the evaluator.

### 3. Evaluator

- Uses simulations and conversations to perform evaluations.
- Checks:
  - **Hallucinations** using an LLM.
  - **Response correctness** based on expected responses from the simulation.
  - **Simulation compliance** (checks if steps are followed correctly).
  - **Function call correctness** (verifies proper function usage).
  - **Reasoning assessment** for responses.
  - **Step order validation** (ensures correct sequence).
  - **Scoring system** for agent evaluation.

---

## Conversation Formatting

The system uses an abstract class `ConversationGenerator`, which must be inherited and overridden for different use cases. This allows customization of the conversation format to match the evaluator's requirements.

### Overriding the Abstract Class for Conversation Formatting

```python
import abc
from typing import Optional

class ConversationGenerator(abc.ABC):
    """
    Abstract base class defining the interface for conversation generators.
    """
    
    @abc.abstractmethod
    def generate_conversation(self, input_json: Optional[str]) -> ConversationResult:
        """
        Generates the conversation in the standardized format.

        :param input_json: JSON string containing conversation data (if any).
        :return: A ConversationResult containing the standardized conversation entries.
        """
        pass
```

---

## Simulation Use Cases

If you have your own simulation test cases, you need to override the following abstract class:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class TestCaseParser(ABC):
    """Abstract base class to parse test cases and extract relevant data."""

    def __init__(self, test_data: Dict[str, Any]):
        self.test_data = test_data

    @abstractmethod
    def extract_conversations(self) -> List["GroundTruthConversation"]:
        """Extracts and returns conversation entries from test data."""
        pass
```

---

## Installation & Setup

Below are instructions to install, configure, and run the application using both a **Python virtual environment** and **Docker**.

### 1. Clone the Repository

```sh
git clone https://github.com/lmos-ai/agent-eval.git
cd agent-eval
```

### 2. Create and Activate a Virtual Environment

On macOS/Linux:
```sh
python -m venv venv
source venv/bin/activate
```

On Windows:
```sh
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Instead of setting environment variables manually, create a `.env` file in the root directory:

```ini
LLM_ENDPOINT=https://api.openai.com/v1
API_KEY=<your-api-key>
MODEL_NAME=gpt-3.5-turbo
FLASK_RUN_HOST=127.0.0.1
FLASK_RUN_PORT=5000
GLINER_MODEL=urchade/gliner_large-v2.1
MONGO_URI=<your-mongo-uri>
MONGO_DATABASE=<your-mongo-database>
MODEL_SOURCE=<your-model-source>
# MongoDB Collections
EVALUATION_COLLECTION=<your-mongodb-collection-name>
PREPROCESSED_DATA_COLLECTION=<your-mongodb-collection-name>
```

The application automatically loads these values at runtime.

---

## Running the Flask Application

### Option A: Running With a Virtual Environment

1. **Make sure your virtual environment is activated**:
   ```sh
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows
   ```

2. **Start the Flask Server**:
   ```sh
   flask run --reload
   ```
   - The app (and its Swagger UI) will be accessible at:
     - [http://127.0.0.1:5000](http://127.0.0.1:5000)
     - [http://127.0.0.1:5000/apidocs/](http://127.0.0.1:5000/apidocs/)

### Option B: Running With Docker

1. **Build the Docker Image** (from the same directory as the `Dockerfile`):
   ```sh
   docker build -t agent-eval .
   ```

2. **Run the Docker Container**:
   ```sh
   docker run --env-file .env -p 5000:5000 agent-eval
   ```
   - `--env-file .env` loads environment variables from your `.env` file.
   - `-p 5000:5000` publishes port 5000 in the container to port 5000 on your host.

3. **Access the Application**:
   - [http://localhost:5000](http://localhost:5000)
   - [http://localhost:5000/apidocs/](http://localhost:5000/apidocs/)

---

## Using the APIs

Below are the core endpoints for performing an asynchronous LLM evaluation. The typical flow is:

1. **POST** to `/evaluate-llm` to initiate the evaluation.
2. Receive a `task_id` that you can use to check the status via `/task-status/<task_id>`.
3. Once the status is `TASK_COMPLETED`, use the returned `evaluation_result_id` to call `/get-evaluation-result`.

### 1. Initiate Evaluation

**Endpoint:** `POST /evaluate-llm`  
**Description:** Starts an asynchronous evaluation of your LLM conversation and returns a unique `task_id`.  
**Request Body Example:**
```json
{
  "use_case": "Billing Agent",
  "unique_id": "hello1234",
  "conversation_logs": [
    {
      "user": "Hello, I'd like more info about my bill.",
      "assistant": "Sure, can you please provide your account number?"
    }
  ],
  "test_cases": [
    {
      "testCases": [
        {
          "expected": {
            "messages": [
              { "type": "user", "content": "Hello, I'd like more info about my bill." },
              { "type": "bot", "content": "Sure, can you please provide your account number?" }
            ]
          }
        }
      ]
    }
  ]
}
```

**Successful Response Example:**
```json
{
  "message": "success",
  "status": "success",
  "data": {
    "task_id": "d2f364c6-cffe-4ff7-9fd9-ce2d9b24ed79",
    "task_status": "TASK_STARTED"
  }
}
```
- You should **save** this `task_id` to check the status of the background process.

---

### 2. Check Evaluation Task Status

**Endpoint:** `GET /task-status/<task_id>`  
**Description:** Returns whether the task is still running, completed, or failed. If completed, the response also contains the `evaluation_result_id` needed to fetch final results.

**Possible Response Examples:**

- **Running**:
  ```json
  {
      "status": "success",
      "message": "success",
      "data": {
          "task_id": "d2f364c6-cffe-4ff7-9fd9-ce2d9b24ed79",
          "task_status": "running"
      }
  }
  ```

- **Completed**:
  ```json
  {
      "status": "success",
      "message": "success",
      "data": {
          "task_id": "d2f364c6-cffe-4ff7-9fd9-ce2d9b24ed79",
          "task_status": "completed",
          "evaluation_result_id": "e12345f7-8g9h-10i1-jklm-..."
      }
  }
  ```

- **Not Found or Failed**:
  ```json
  {
      "status": "error",
      "message": "No such task running for task_id: d2f364c6-cffe-4ff7-9fd9-ce2d9b24ed79"
  }
  ```

---

### 3. Retrieve Evaluation Results

**Endpoint:** `GET /get-evaluation-result`  
**Description:** Retrieves the final evaluation results, which include scores, correctness checks, and hallucination analysis.  
**Required Query Parameter:** `id` (the `evaluation_result_id` returned in the completed task status)  

**Request Example**:
```
GET /get-evaluation-result?id=<evaluation_result_id>
```


---

## Example Workflow

1. **Initiate Evaluation**  
   - Send a `POST` to `/evaluate-llm` with your conversation logs and test cases.
   - Receive a `task_id` in the response.

2. **Check Status**  
   - Periodically call `GET /task-status/<task_id>`.
   - If `"task_status": "completed"`, note the `evaluation_result_id`.

3. **Retrieve Results**  
   - Call `GET /get-evaluation-result?id=<evaluation_result_id>` and review the scoring, correctness, and reasoning data.

---

## Contributors

- **Bhupinder** – AI Engineer  
  - Email: [bhupinder2121221@gmail.com](mailto:bhupinder2121221@gmail.com)  
  - LinkedIn: [Bhupinder's LinkedIn](https://www.linkedin.com/in/bhupinder-bhupinder-473637338/)

---

## Thanks

Special thanks to all contributors and developers who helped build this project into an asynchronous evaluation system!