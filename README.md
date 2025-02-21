# Black Box Evaluation

## Overview

Black Box Evaluation is a system that evaluates any AI agent's performance while ensuring it follows all specified rules. It checks for hallucinations using a hybrid approach of Named Entity Recognition (NER) and Python. Additionally, it verifies whether the AI agent's response is correct and provides reasoning for correctness or incorrectness.

This project now supports **asynchronous evaluations** using background tasks. When you submit an evaluation request, the system immediately returns a task ID, and the actual evaluation runs in a separate thread. You can query the status of this task at any time and retrieve the final results once the evaluation completes.

---

## Features

- Evaluates AI agent performance in an **asynchronous** manner
- Detects hallucinations using NER and Python
- Checks response correctness
- Provides reasoning for correct or incorrect responses
- Supports multiple evaluation techniques
- Includes a **background task** system with status polling

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

1. **Clone the repository:**
   ```sh
   git clone https://github.com/lmos-ai/agent-eval.git
   ```
2. **Navigate to the project directory:**
   ```sh
   cd agent-eval
   ```
3. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```
4. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

---

### Configuring Environment Variables

Instead of setting environment variables manually, create a `.env` file in the root directory with the following content:

```ini
LLM_ENDPOINT=https://api.openai.com/v1   # [OpenAI] or use your own LLM Endpoint
API_KEY=<your-api-key>
MODEL_NAME=gpt-3.5-turbo                # [Or any LLM Model]
FLASK_RUN_HOST=127.0.0.1
FLASK_RUN_PORT=5000
GLINER_MODEL=urchade/gliner_large-v2.1
MONGO_URI=<your-mongo-uri>
MONGO_DATABASE=<your-mongo-database>
MODEL_SOURCE=<your-model-source>
# MONGODB COLLECTIONS
EVALUATION_COLLECTION=<your-mongodb-collection-name>
PREPROCESSED_DATA_COLLECTION=<your-mongodb-collection-name>
```

The application automatically loads these values at runtime.

For more GliNER models, you can visit [GliNER Models on Hugging Face](https://huggingface.co/models?library=gliner&sort=trending).

---

## Running the Flask Application

You can run the application either directly on your machine or using Docker.

### Running Without Docker

1. **Ensure the virtual environment is activated:**
   ```sh
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```
2. **Start the Flask server:**
   ```sh
   flask run --reload
   ```
3. **Access the Application and Swagger UI:**
   - Flask Application: [http://127.0.0.1:5000](http://127.0.0.1:5000)  
   - Swagger UI: [http://127.0.0.1:5000/apidocs/](http://127.0.0.1:5000/apidocs/)

---

### Running With Docker

#### 1. Building the Docker Image
From the project directory (where the `Dockerfile` is located), run:
```sh
docker build -t agent-eval .
```

#### 2. Running the Docker Container
Start the container with:
```sh
docker run --env-file .env -p 5000:5000 agent-eval
```
- `--env-file .env`: Loads environment variables from your `.env` file.
- `-p 5000:5000`: Maps port `5000` in the container to port `5000` on your host machine.

#### 3. Access the Application and Swagger UI
- Flask Application: [http://localhost:5000](http://localhost:5000)  
- Swagger UI: [http://localhost:5000/apidocs/](http://localhost:5000/apidocs/)

---

## Using the API

### 1. **Evaluate AI Agent (Asynchronous)**
- **Endpoint:** `POST /evaluate-llm`
- **Description:** Initiates an asynchronous LLM evaluation. Returns a `task_id` immediately while the evaluation runs in the background.
- **Request Body Example:**
  ```json
  {
      "use_case": "Billing Agent",
      "unique_id": "hello1234",
      "conversation_logs": [
          // LIST OF CONVERSATION
      ],
      "test_cases": [
          // LIST OF TEST CASES
      ]
  }
  ```
- **Response Example:**
  ```json
  {
      "message":"success",
      "status": "success",
      "data": {
          "task_id": "d2f364c6-cffe-4ff7-9fd9-ce2d9b24ed79",
          "status": "TASK_STARTED"
      }
  }
  ```

You can then use this `task_id` to check the background evaluation’s status.

---

### 2. **Get Evaluation Result**
- **Endpoint:** `GET /get-evaluation-result`
- **Description:** Retrieves the final evaluation results by using an `id` (the unique evaluation result ID).
- **Query Parameter:** `id` (required)
- **Request Example:**
  ```
  GET /get-evaluation-result?id=<your_evaluation_result_id>
  ```
- **Response Example:**
  ```json
  {
      "status": "success",
      "message": "Evaluation data retrieved successfully",
      "data": {
          "final_score": 0.85,
          "results": [
              // ...
          ]
      }
  }
  ```

---

### 3. **Check Background Task Status**
- **Endpoint:** `GET /task-status/<task_id>`
- **Description:** Checks the status of a background evaluation task. If the task is completed, returns the `evaluation_result_id`.
- **Path Parameter:** `<task_id>` (required)
- **Request Example:**
  ```
  GET /task-status/d2f364c6-cffe-4ff7-9fd9-ce2d9b24ed79
  ```
- **Response Examples:**
  - **In Progress:**
    ```json
    {
        "status": "success",
        "message":"success",
        "data": {
            "task_id": "d2f364c6-cffe-4ff7-9fd9-ce2d9b24ed79",
            "status": "running"
        }
    }
    ```
  - **Completed:**
    ```json
    {
        "status": "success",
        "message":"success",
        "data": {
            "task_id": "d2f364c6-cffe-4ff7-9fd9-ce2d9b24ed79",
            "status": "completed",
            "evaluation_result_id": "e12345f7-8g9h-10i1-jklm-..."
        }
    }
    ```
  - **Failed or Not Found:**
    ```json
    {
        "status": "error",
        "message": "No such task running for task_id: d2f364c6-cffe-4ff7-9fd9-ce2d9b24ed79"
    }
    ```

These endpoints provide a complete asynchronous flow for LLM evaluation.

---

## Example Usage

**POST** request to start evaluation:
```sh
curl --location 'http://127.0.0.1:5000/evaluation/evaluate-llm' \
--header 'Content-Type: application/json' \
--data @request.json
```
**GET** request to check status:
```sh
curl --location 'http://127.0.0.1:5000/evaluation/task-status/<task_id>'
```
**GET** request to retrieve final result:
```sh
curl --location 'http://127.0.0.1:5000/evaluation/get-evaluation-result?id=<evaluation_result_id>'
```

---

## Contributors

- **Bhupinder** - AI Engineer  
  - Email: [bhupinder2121221@gmail.com](mailto:bhupinder2121221@gmail.com)  
  - LinkedIn: [Bhupinder's LinkedIn](https://www.linkedin.com/in/bhupinder-bhupinder-473637338/)

---

## Thanks

Special thanks to all contributors and developers who helped build this project and evolve it into an asynchronous evaluation system!  
