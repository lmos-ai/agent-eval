from llm.llm import LLMModel
from helper_functions.extract_json import extract_json_from_string
from helper_functions.validate_response import check_and_add_keys
from conversations.conversation_format import ConversationEntry, FunctionCall
from typing import List
class StepOrderValidator:
    """
    Validates whether steps are followed in the correct order.
    """
    def __init__(self, simulation_steps):
        self.simulation_steps = simulation_steps

    def validate_step_order(self, matched_steps):
        """
        Validates if the matched steps are in the correct order.
        :param matched_steps: List of dictionaries representing matched steps.
        :return: True if steps are in the correct order, False otherwise.
        """
        try:
            # Extract expected step names from simulation_steps
            expected_order = [step["step_name"].strip().lower() for step in self.simulation_steps]

            # Remove None values, duplicates, and normalize case in matched_steps
            matched_order = []
            seen_steps = set()
            for step in matched_steps:
                if step is None:
                    continue
                step_name = step.get("step_name", "").strip().lower()
                if step_name and step_name not in seen_steps:
                    matched_order.append(step_name)
                    seen_steps.add(step_name)

            # Validate the order of matched steps against the expected order
            expected_idx = 0
            for matched in matched_order:
                while expected_idx < len(expected_order) and expected_order[expected_idx] != matched:
                    expected_idx += 1
                if expected_idx == len(expected_order):
                    return False
                expected_idx += 1

            return True
        except Exception as e:
            raise ValueError(f"Error validating step order: {str(e)}")



class LLMTriggerMatcher:
    """
    Uses LLM to match the latest query with trigger events and returns the matching step name or None.
    """
    def __init__(self, llm:LLMModel):
        self.llm = llm

    def get_step_name(self, previous_context, query, trigger_events):
        """
        Matches the latest query with trigger events using LLM.
        :param previous_context: List of previous queries and responses.
        :param query: The current user query.
        :param trigger_events: List of trigger events with step names.
        :return: The step name if a match is found, or None.
        """
        prompt = self.create_prompt(previous_context, query, trigger_events)
        try:
            llm_response = self.llm.complete(prompt)

            processed_data = extract_json_from_string(response_str=llm_response)
            print("Extracted json from LLM.")
            return check_and_add_keys(data_dict=processed_data, keys_to_check=['step_name'])['step_name']
        except Exception as e:
            raise ValueError(f"Error in LLM trigger matching: {e}")

    @staticmethod
    def create_prompt(previous_context, query, trigger_events):

        # Format the conversation context
        context_str = "\n".join([f"User: {entry['user_query']} | AI: {entry['response']}" for entry in previous_context])

        # Format the trigger events with step names and descriptions
        trigger_events_str = "\n".join([
            f"Step Name: {event['step_name']} | Trigger Event: {event['trigger_event']}"
            for event in trigger_events
        ])
        prompt = """
        Role:
        You are an intelligent assistant specializing in analyzing conversation contexts and matching user queries with predefined trigger events. Your role is to accurately identify the relevant step name for the latest user query based on the provided conversation context and trigger events.

        Description:
        You are provided with:
        1. The conversation history (context) between the user and the AI up to this point.
        2. The latest user query to analyze.
        3. A list of predefined trigger events, each associated with a specific step name and a descriptive explanation of when the step should be used.

        Your task is to:
        - Analyze the conversation history and the latest query.
        - Match the latest query with one of the trigger events based on its description.
        - If a match is found, return the corresponding step name.
        - If no match is found, return `None`.

        Examples:
        ### Example 1: Matched Case
        Context:
        User: What services do you offer?
        AI: I can assist with billing and account management.

        User: Show me my bills.
        AI: Which month and year do you want to view?

        Latest Query:
        "April 2024"

        Trigger Events:
        - Step Name: Retrieve Billing Information | Trigger Event: Use this step when the user asks for billing information for a specific month and year.
        - Step Name: Update Account Details | Trigger Event: Use this step when the user requests to update their account information.

        Expected Output:
        {
        "step_name": "Retrieve Billing Information"
        }

        ### Example 2: Unmatched Case
        Context:
        User: What services do you offer?
        AI: I can assist with billing and account management.

        User: Can I talk to a manager?
        AI: Sure, I can connect you.

        Latest Query:
        "Where is your office located?"

        Trigger Events:
        - Step Name: Retrieve Billing Information | Trigger Event: Use this step when the user asks for billing information for a specific month and year.
        - Step Name: Update Account Details | Trigger Event: Use this step when the user requests to update their account information.

        Expected Output:
        {
        "step_name": null
        }

        Instructions:
        1. Carefully analyze the conversation context to understand the intent behind the latest query.
        2. Compare the latest query with the provided trigger events and their descriptions to identify any matches.
        3. Return the corresponding step name if the query matches a trigger event based on its description.
        4. If no match is found, return `null`.
        5. The output must be a valid JSON object with the following format:
        { "step_name": (string) The name of the step if a match is found, or null if no match is found. }
        6. Ensure the response is concise, accurate, and strictly adheres to the provided format.
        """
        prompt+=f"""
        Input Data:
        ### Conversation Context:
        Below is the conversation history up to this point:
        {context_str}

        ### Latest Query:
        The latest query from the user is:
        "{query}"

        ### Trigger Events:
        Below is the list of potential trigger events with their corresponding step names and descriptions:
        {trigger_events_str}

        Task:
        Follow the instructions and examples provided to produce the correct output.
        """
        return prompt.strip()




class LLMEvaluation:
    """
    Uses LLM to evaluate the correctness of function callings and response matching.
    """
    def __init__(self, llm:LLMModel):
        self.llm = llm

    def evaluate(self, previous_context, query, actual_response, expected_response, actual_functions, expected_functions):
        """
        Evaluates the correctness of the conversation step using LLM.
        """
        
        prompt = self.create_prompt(
            previous_context=previous_context,
            query=query,
            actual_response=actual_response,
            expected_response=expected_response,
            actual_functions=actual_functions,
            expected_functions=expected_functions
        )
        llm_response=None
        try:
            
            llm_response = self.llm.complete(text="Hello how are you")
            return self.process_response(llm_response)
        except Exception as e:
            print("[!]    Error in LLM response")
            print(f"INFO: Got below response from LLM: {llm_response}")
            raise ValueError(f"Error in LLM evaluation: {str(e)}")

    @staticmethod
    def create_prompt(previous_context, query, actual_response, expected_response, actual_functions, expected_functions):
        """
        Creates the prompt to send to the LLM for evaluation.
        """
        # Format the conversation context
        context_str = "\n".join([f"User Query: {entry['user_query']} \Function callings by LLM agent: {entry['actual_functions']}\n AI response: {entry['response']}" for entry in previous_context])
        # Helper function to format function calls
        def format_functions(functions:List[FunctionCall]):
            return "\n".join([
                f"Function: {function.function_name} | Input parameters: {str(function.input_passed )}" +
                (f" | Output parameters: {str(function.output_passed)}")
                for function in functions
            ])
        
        actual_functions_str = format_functions(actual_functions)
        
        expected_functions_str = format_functions(expected_functions)
        prompt = """
        # Scope:
        You are tasked with evaluating the performance of an AI system in handling user queries. 
        This involves comparing the system’s actual response and function calls against the expected responses and function calls provided for the given scenario. 
        The goal is to identify any discrepancies, hallucinations, and provide a structured analysis.
        
        # Role:
        You are an expert evaluator for AI systems. Your will do following:
        1. Assess whether the actual response matches the expected response or previous context.
        2. Determine if the AI introduced any hallucinated information in the latest LLM agent response.
        3. Provide a detailed reasoning for any discrepancies, hallucinations, or correctness issues in the response or function calls.
        """
        
        expected_response = expected_response or "I don't know the expected response. Analyze the query and previous context with the actual response and check if the response is fine and correct or not."
        
        prompt += """
        # Task Instructions:
        ## 1. Checking the correctness of the AI's actual response:
            - 1.1 If expected response is Given: 
                - Check if the actual response is correct by checking the expected response and function ouputs.
                - Also check wheter the response by AI is a follow up question. If yes, check if it is related to expected response, then it is fine and correct otherwise not.
                - Thought process for correctness checking (When expected response is available):
                    - a. I have the latest response now i have to check if the expected response and latest function ouptut is given. If yes, then i need to check for the given latest user query
                        - a.1 If the latest response is correct by checking the expected response and function outputs. The expected response and function outputs are given  only to help me in deciding. I have to make decision checking previous context, and function outputs and expected response. 
                        - a.2 If the latest response is a follow up question by the AI. I have to check if the follow up question is related to the Expected response or not.

            - 1.2 If expected response or function outputs are not given:
                - If expected response or function outputs not given then check with previous context and analyse for the given latest user query if the latest response correct or not.
                - Provide detailed reasoning for whether they match or not.
                - Thought process for correctness checking:
                    - a. I have the latest response now i have to check if the expected response and latest function ouptut is given. If there is no expected response and latest function calling, then i have to check for the previous context and check for the user query if the latest response is correct or not. And if none of the previous context, function outputs and expected response is given, then use your knowledge and check if for the given user query wheter the response is correct or not.
        
        ## 2. Identify any hallucinated information in the actual response:
        - Check if the latest LLM agent response contains details such as name, organization, services, dates, amount, or other important information that was not previously mentioned in the conversation, user query or any function outputs.
        - For checking the halucination, Only check for information given in the latest response given in previous context, latest user query, or in any function outputs.
        - Dont check if correct function called or not. For halucination you task is only to varify the consistency of data or information in response by checking if the information was provided in the previous context or latest user query or not.
            2.1 Thought process for halucination check:
                -   First I will extract important information from the latest LLM agent response, then i will check if the response is the general response to a general query like greetings, thanks any such queries. If yes then i only have to check if the response is having such information like amount, service etc and will say it halucinated otherwise for general response i will say it is not halucinlates. And if no, mean it was not a general conversation then i will check if this information was present in any previous context wheter it is user queries, function outputs or ai responses. if information was not present in previous context or function ouputs then i will check if the user have provide such the information in latest user query. If yes then it is not halucinated. If information not present anywhere, not in previous context, latest user query, function ouputs only then i will say it is halucination.
        
        ## 3. Provide a comprehensive evaluation:
        - Include reasoning for discrepancies in responses or function calls.
        - Highlight areas where the AI performed correctly and where it needs improvement.
        
        ## 4. Return the evaluation as a JSON object using the format below.
        """
        prompt += """
        # Examples:
        ### Example 1: No Hallucination and Correct Response
        Context:
        User: Show me my bills.
        Function callings by LLM agent:[]
        AI: Which month and year do you want to view?
        
        Latest Query:
        "April 2024"
        

        Actual Response:
        "Here are your bills for April 2024."
        
        Expected Response:
        "Here are your bills for April 2024. please click on <link>"
        
        Actual Functions:
        Function: get_billing_statements | Input parameters: {'user_id': 'userA1', 'month': 'April', 'year': 2024 } | Output: {"status":"success", "data":"Here is the document link. <Link>"}
        
        Expected Functions:
        Function: get_billing_statements | Input parameters: {'user_id': 'userA1', 'month': 'April', 'year': 2024} Output: {"status":"success", "data":"Here is the document link. <Link>"}
        
        Expected Output:
        {
            "is_halucinated": false,
            "correct_response": true,
            "follow_up_question":false,
            "reasoning": "The actual response matches the expected response and contains no hallucinated information. The functions called are correct and align with the expected functions."
        }
        
        ### Example 2: Hallucination Present
        Context:
        User: What's my account balance?
        AI: Your current account balance is $5,000.
        
        Latest Query:
        "Can you provide the last transaction details?"
        
        Actual Response:
        "Certainly! Your last transaction was a payment of $200 to ABC Corp on March 15, 2024."
        
        Expected Response:
        "Here are your last transaction details. <Some payment details>"
        
        Actual Functions:
        Function: get_account_balance | Input parameters: {'user_id': 'userB2'} Output: {"status":"success", "data":{"date":"today","amount":5000}}
        Function: get_last_transactions | Input parameters: {'user_id': 'userB2'} Output: {"status":"success", "data":{"date":"15/03/2024","amount":300}}
        
        Expected Functions:
        Function: get_account_balance | Input parameters: {'user_id': 'userB2'}
        Function: get_last_transactions | Input parameters: {'user_id': 'userB2'}
        
        Expected Output:
        {
            "is_halucinated": true,
            "correct_response": false,
            "reasoning": "The actual response includes specific transaction details that were not retrieved via any function call (i.e. value mismatched), indicating hallucinated information."
        }
        
        ### Example 3: Partially Correct Response
        Context:
        User: Schedule a meeting.
        AI: Sure, what date and time would you prefer?
        
        Latest Query:
        "Next Monday at 10 AM"
        
        Actual Response:
        "Your meeting is scheduled for Next Monday at 10 AM. A confirmation email has been sent to your email address."
        
        Expected Response:
        "Your meeting has been scheduled for Next Monday at 10 AM."
        
        Actual Functions:
        Function: schedule_meeting | Input parameters: {'user_id': 'userC3', 'date': 'Next Monday', 'time': '10 AM'}
        
        Expected Functions:
        Function: schedule_meeting | Input parameters: {'user_id': 'userC3', 'date': 'Next Monday', 'time': '10 AM'}
        Function: send_confirmation_email | Input parameters: {'user_id': 'userC3', 'meeting_time': 'Next Monday at 10 AM'}
        
        Expected Output:
        {
            "is_halucinated": false,
            "correct_response": true,
            "follow_up_question": false
            "reasoning": "The actual response correctly schedules the meeting as expected. However, the confirmation email was sent without being explicitly called, which might be considered an extra function if not expected."
        }

        ### Example 4: Follow up question check
        Context:
        User: Schedule a meeting.
        AI: Sure, what date and time would you prefer?
        
        Latest Query:
        "Next Monday at 10 AM"
        
        Actual Response:
        "Any details of meeting ?"
        
        Expected Response:
        "Meeting Scheduled"
        
        Actual Functions:
        Function: schedule_meeting | Input parameters: {'user_id': 'userC3', 'date': 'Next Monday', 'time': '10 AM'}
        
        Expected Functions:
        Function: schedule_meeting | Input parameters: {'user_id': 'userC3', 'date': 'Next Monday', 'time': '10 AM'}
        
        Thought Process:
        In Example 4, the user is asking to schedule a call, and AI in response is asking for the details of meeting. But the expected response should be that the metting is scheduled. Now if i see the AI actual response is the follow up question related to meeting and that's why it is related to meeting use case, so it is correct.
        
        Expected Output:
        {
            "is_halucinated": false,
            "correct_response": true,
            follow_up_question:true,
            "reasoning": "The actual response is not same as expected response, but the response is related to metting usecase and it is a follow up question."
        }
        
        Instructions Recap:
        1. Evaluate the response match and function correctness using the provided input.
        2. Identify any hallucinated information in the response checking previous context or function ouputs.
        3. Provide a detailed reasoning in your response.
        4. Ensure your output adheres strictly to the JSON format specified above.
        5. in reasoning, dont add any quotes or curly brackets {}.
        5. Return concise, actionable insights in your reasoning.
        
        Task:
        Use the input data and follow the instructions to produce the correct output.
        """
        prompt += f"""
        Input Data:
        ### Conversation Context:
        {context_str}

        ### Latest Query:
        The latest query from the user is:
        "{query}"

        ### Actual Response:
        The response generated by the AI is:
        "{actual_response}"

        ### Expected Response:
        The response that should have been generated is:
        "{expected_response}"

        ### Actual Functions:
        Below is the list of functions actually called by the AI during query handling:
        {actual_functions_str}

        ### Expected Functions:
        Below is the list of functions that were expected to be called:
        {expected_functions_str}
        """
        
        prompt += """
        Response Format:
        Your response must be a valid JSON object in the following structure:
        {
            "is_halucinated": (boolean) Indicates if the AI response contains hallucinated information,
            "correct_response": (boolean) Indicates if the AI response is correct,
            "reasoning": (string) Detailed explanation of the evaluation in text,
            "follow_up_question": (booleab) true is the AI response is a follow up query 
        }
        """
        
        return prompt.strip()


    @staticmethod
    def process_response(llm_response:str):
        """
        Processes the LLM JSON response for reasoning.
        """
        try:
            processed_data = extract_json_from_string(response_str=llm_response)
            # processed_data = check_and_add_keys(data_dict=processed_data, keys_to_check=['reasoning', "is_halucinated", "correct_response"])
            
            reasoning = processed_data["reasoning"]
            is_halucinated = processed_data["is_halucinated"]
            correct_response = processed_data["correct_response"]
            follow_up_question = processed_data['follow_up_question']

            if not isinstance(reasoning, str):
                raise ValueError("Reasoning must be a string.")
            if not isinstance(is_halucinated, bool):
                raise ValueError("is_halucinated must be a bool.")
            if not isinstance(correct_response, bool):
                raise ValueError("correct_response must be a boolean.")
            if not isinstance(follow_up_question, bool):
                raise ValueError("follow_up_question must be bool")
            return {
                "reasoning": reasoning,
                "is_halucinated": is_halucinated,
                "correct_response": correct_response,
                "follow_up_question":follow_up_question
            }
        except Exception as e:
            print("[!] Error in processing the LLM response")
            raise ValueError(f"Error processing LLM response: {str(llm_response)} \n proccessed response: {processed_data}\n Error:{e}")

class FunctionExtractor:
    """
    Extracts actual functions called in a conversation log.
    """
    def extract_functions(self, log, key):
        """
        Extracts the list of actual function calls from a conversation log.
        :param log: Dictionary representing a single conversation log.
        :param key: Extract key from conversation log
        :return: List of function calls, or an empty list if not present.
        """
        try:
            # Validate if the log is a dictionary
            if not isinstance(log, dict):
                raise ValueError("Conversation log must be a dictionary.")

            # Extract and return the 'actual_function_calls' key
            return log.get(key, [])
        except Exception as e:
            raise ValueError(f"Error extracting functions: {str(e)}")


def validate_conversation_logs(conversation_logs):
    """
    Validates that each conversation log contains the required keys.
    :param conversation_logs: List of conversation logs to validate.
    :raises ValueError: If any log is missing required keys.
    """

    for idx, log in enumerate(conversation_logs):
        # Check if the log is a dictionary
        if not isinstance(log, ConversationEntry):
            raise ValueError(f"Conversation log at index {idx} is not a ConversationEntry instance: {log}")
        
        # Check required fields
        if not log.user_query.strip():
            raise ValueError(
                f"'user_query' is missing or empty in conversation log at index {idx}"
            )

        if log.response is None or not log.response.strip():
            raise ValueError(
                f"'response' is missing or empty in conversation log at index {idx}"
            )


def validate_simulation_steps(simulation_steps):
    """
    Validates that each simulation step contains the required keys.
    :param simulation_steps: List of simulation steps to validate.
    :raises ValueError: If any step is missing required keys.
    """
    required_keys = ["step_name", "expected_response"]
    if not isinstance(simulation_steps, dict):
            raise ValueError(f"Simulation step is not a dictionary: {type(simulation_steps)}")
    for idx, step in enumerate(simulation_steps['steps']):
        # Validate required keys
        missing_keys = [key for key in required_keys if key not in step]
        if missing_keys:
            raise ValueError(f"Missing keys in simulation step at index {idx}: {missing_keys}")
