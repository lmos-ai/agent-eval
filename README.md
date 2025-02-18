# Black Box Evaluation

## Overview

Black Box Evaluation is a system that evaluates any AI agent's performance, ensuring it follows all rules correctly. It checks for hallucinations using a hybrid approach of Named Entity Recognition (NER) and Python. Additionally, it verifies whether the AI agent's response is correct and provides reasoning for correctness or incorrectness.

## Features

- Evaluates AI agent performance
- Detects hallucinations using NER and Python
- Checks response correctness
- Provides reasoning for correctness or incorrect responses
- Supports multiple evaluation techniques

## Systems

### 1. Specifications

- Takes test use case conversations and creates simulations.
- Generates a detailed description, step names, expected function calls and outputs.
- Defines trigger messages indicating when steps should be followed.

### 2. Agent Caller (In Progress)

- Connects with the AI agent based on its description and simulation.
- Generates conversations for evaluation.
- Allows users to pass their own conversation for evaluation.
- Uses a **Conversation Converter Interface** to format conversations correctly for the evaluator.

### 3. Evaluator

- Uses simulations and conversations to perform evaluations.
- Checks:
  - **Hallucinations** using LLM.
  - **Response correctness** based on expected responses from the simulation.
  - **Simulation compliance** (steps followed correctly).
  - **Function call correctness** (checks if functions are called properly).
  - **Reasoning assessment** for response correctness.
  - **Step order validation** (ensures steps follow the correct sequence).
  - **Scoring system** for agent evaluation.

## Conversation Formatting

The system uses an abstract class `ConversationGenerator`, which must be inherited and overridden for different use cases. This allows customization of the conversation format to match the evaluator's requirements.

### **Overriding the Abstract Class for Conversation Formatting**

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

## Installation & Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/lmos-ai/agent-eval.git
   ```
2. Navigate to the project directory:
   ```sh
   cd agent-eval
   ```
3. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```
4. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Configuring Environment Variables

Instead of setting environment variables manually, create a `.env` file in the root directory with the following content:

```ini
LLM_ENDPOINT=https://api.openai.com/v1 [OpenAI]  or Use your own LLM Endpoint
API_KEY=<your-api-key>
MODEL_NAME=gpt-3.5-turbo [Or any LLM Model]
FLASK_RUN_HOST=127.0.0.1
FLASK_RUN_PORT=5000
GLINER_MODEL=urchade/gliner_large-v2.1
MONGO_URI=<your-mongo-uri>
MONGO_DATABASE=<your-mongo-database>
MODEL_SOURCE=<your-model-source>
```
[For more GliNER models](https://huggingface.co/models?library=gliner&sort=trending)

The application will automatically load these values when it runs.

## Running the Flask Application

1. Ensure the virtual environment is activated:
   ```sh
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```
2. Start the Flask server:
   ```sh
   flask run --reload 
   ```

## Using the API


### **Evaluate AI Agent**
- **Endpoint:** `POST /evaluate-llm`
- **Description:** Evaluates an AI agent based on the given use case, conversation logs, and test cases.
- **Request Body Example:**

```json
{
    "use_case": "Billing Agent",
    "unique_id": "hello1234",
    "conversation_logs": [
        LIST OF CONVERSATION
    ],
    "test_cases": [
        LIST OF TEST CASES
    ]
}
```

### **How to Use**

```sh
curl --location '127.0.0.1:5001/evaluation/evaluate-llm' \
--header 'Content-Type: application/json' \
--data @request.json
```

### **Contributors**
- **Bhupinder** - AI Engineer  
  - Email: bhupinder2121221@gmail.com  
  - LinkedIn: [Bhupinder's LinkedIn](https://www.linkedin.com/in/bhupinder-bhupinder-473637338/)


# Thanks
Special thanks to all contributors and developers who helped build this project!