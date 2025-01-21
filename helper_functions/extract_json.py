import json
import re

def clean_and_format_json_string(response_str):
    """
    Cleans and formats the LLM response string into valid JSON.
    It ensures that single quotes are replaced by double quotes and proper escape handling.
    """
    # Remove newlines and unnecessary spaces
    response_str = response_str.strip()

    # Ensure 'false' and 'true' are in lowercase (as per JSON specification)
    response_str = response_str.replace('False', 'false').replace('True', 'true')

    return response_str
import re


def extract_brace_content(input_string):
    """
    Extracts the substring enclosed within the first pair of curly braces {}.

    Args:
        input_string (str): The string from which to extract the content.

    Returns:
        str or None: The extracted substring including the braces if found, else None.
    """
    # Define a regex pattern to match content within {}
    pattern = r'\{.*?\}'
    
    # Search for the pattern in the input string with DOTALL to include newlines
    match = re.search(pattern, input_string, re.DOTALL)
    
    if match:
        return match.group(0)  # Returns the matched substring including {}
    else:
        return None  # Returns None if no match is found


def extract_json_from_string(response_str):
    """
    This function attempts to extract a JSON object from a string.
    Handles issues like nested JSON and improper formatting.
    """
    try:
        response_str = extract_brace_content(response_str)
        # Clean and format the string to valid JSON
        response_str = clean_and_format_json_string(response_str)

        # Parse the cleaned string as JSON
        json_data = json.loads(response_str)
        
        return json_data

    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}. \n Response was: {repr(response_str)}")
        return None
    except Exception as e:
        print(f"Error extracting JSON: {e}. \n Got Response from LLM: \n{repr(response_str)}")
        return None
