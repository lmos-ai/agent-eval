from typing import Any, Dict, List, Optional
from simulation.test_case_parser import TestCaseParser
from data_model.simulations import GroundTruthConversation
from llm.llm import LLMModel
from helper_functions.response import extract_json_from_string


class SimulationProcessor:
    """
    Class to handle test case processing and simulation creation.
    """
    system_prompt = """
    # Role:
    You are professional QA, who can evaluate the conversation returned by LLM with the expected conversation. So you know every aspect of testing.

    # Task:
    I will provide you some Ground truth conversation having the Query and response. The conversation will be from old to new.
    You have to evaluate the conversation and make a test case (Simulation) which i will use in my Evaluator pipeline.
    For this, you have to analyse the conversation and extract few information, like Steps name and expected response.

    # Thought process
    - Analyse the conversation, and find different parts of the conversation, like in few queryies user might ask for getting past bills, updating bank information and other scenerios.
    - Analyse such scenerios and take them as steps or protocols which user have to follow. 
    - And for each step or scenerio, generate the expected response by analysing the conversation which tells about what agent should have response.

    # Examples:
    Example 1:
    User query: Hi.
    AI Agent Response: Hello, how are you.
    User query: I want to check the bank information:
    AI Agent Response: ok, what is your account number.
    User query: My account number is 12345
    AI Agent: You have total 100 dollars.
    User Query: ok, is there any terif bill for me ?
    AI Agent: No every thing is paid. 0 outstanding bill.

    # Thought:
    In the conversation i can see three scenerios, 
    - 1. where user is greeting. And for it the expected response is also greeting
    - 2. In second scenerio, user is checking for bank account, and expected response is the information about the bank.
    - 3. In third scenerio, user is asking for terrif account information, and expected response is information about the terrif account.

    # Response Example:
    {
    "greetings": "The expected response should have greeting",
    "check_bank_balance": "The expected response should have the information about the balanace in the bank account of the user",
    "check_terrif_account_bill": "The expected response should have information about the terrif account bill."
    }

    # conversation to analyse:
    Analyse below conversation between user and AI agent. And extract the scenerios and expected response for them. 
    <Conversation_start>
    [CONVERSATION]
    </Conversation_ends>
    

    # Response format
    - Return a json enclosed in { } brackets.
    - Keys should be the step name extracted from the conversation.
    - Values of the json must be expected response in string format.
    - Add double quotes around the keys and response.
    - Don't add any other meta information expect json itself.
    - Json should me json serializable
    Example:
    {
    "STEP NAME": "EXPECTED RESPONSE"
    }

    """
    def __init__(self, llm:LLMModel, test_cases: List[Dict[str, Any]]=None, json_testclass_parser:TestCaseParser=None, use_case:str=""):
        """Initialize with test cases."""
        self.test_cases:List[dict] = test_cases
        self.simulations:str = ""
        self.json_testclass_parser:TestCaseParser = json_testclass_parser
        self.llm = llm
        self.use_case = use_case
        self._validate()
        print("[.] The class is successfully initialised")
    
    def _validate(self):
        if self.test_cases:
            if self.json_testclass_parser is None:
                raise Exception("[!] The testcases are passed in the Simulation Parser but not the TestCaseParser")
        if self.llm is None:
            raise Exception("[!] The passed LLM is None. Please pass LLMModel Class instance.")
        if not isinstance(self.llm, LLMModel):
            raise Exception("[!] Passed LLM is not instance of LLMModel. Please create llm from LLMModel only")
        

    def run(self) -> Optional[dict]:
        """Processes the test cases and generates simulations."""
        print("Starting test case processing...")
        try:
            # Check if test cases exist
            if self.test_cases:
                print("[.] Test cases found in the input data. So trying to generate the Specisifications from the test cases.")
                # Parse test cases
                conversations = []
                for test_case in self.test_cases:
                    print("[.] Initializing the json Test case parser with given test cases.")
                    parser:TestCaseParser = self.json_testclass_parser(test_case)
                    print("[.] Extracting the query and expected response from the test cases.")
                    conversation = parser.extract_conversations()
                    conversations.append(conversation)
                print("[✅] Test cases processed successfully.")
                print("[.] Now generating the Specifications from the test cases.")

                return self.create_simulation_from_testcases(groundTruthConversations=conversations)
            else:
                print("[!] Test Cases not passed. Cannot generate the Specifications.")

        except Exception as e:
            print(f"[!] Error processing test cases: {e}")
            raise e

    def create_simulation_from_testcases(self, groundTruthConversations: List[List[GroundTruthConversation]], use_case:str="") -> Optional[dict]:
        """
        Placeholder function for simulation creation.
        Will use extracted conversation data.
        """
        steps = []
        if groundTruthConversations:
            print("[.] Ground Truth conversations are passed, So creating the Simulation/Specifications from Testcases.")
            print(f"[.] Creating simulation from test cases")
            conversation_str = ""
            for i,conversation in enumerate(groundTruthConversations):
                conversation_str += f"\n Conversation {i}: \n"
                conversation_str+= "".join([f"User Query:\n{conv.user_query}.\n AI Response:\n{conv.response}\n" for conv in conversation])
            system_prompt = self.system_prompt.replace("[CONVERSATION]",conversation_str)
            print("[.] Now generating simulaton/specifications from LLM based on Test Cases provided")
            response = self.llm.complete(text=system_prompt)
            print("[✅] Got response from LLM for simulations/specifications")
            print("[.] Extracting Json from LLM Response")
            json_response = extract_json_from_string(response)
            if not json_response:
                print("[!] Got None in json response from extract json function.")
                return None
            
            for step_name, expected_response in json_response.items():
                steps.append({
                    "step_name":step_name,
                    "trigger_event":"",
                    "expected_functions":[],
                    "expected_response":expected_response
                })
        simulation = {
            "use_case": use_case + "Question Answering",
            "sub_use_case": "",
            "steps": steps
        }
        print("[✅] Successfully created the simulations/specifications from Test Cases using LLM")
        return simulation
