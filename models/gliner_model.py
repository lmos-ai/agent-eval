from gliner import GLiNER
from helper_functions.utils import SingletonClass
from typing import Any, Dict, List, Union
import re
from helper_functions.ner_utils import check_entity_in_source

# Initialize GLiNER with the base model
class GliNerMODEL(metaclass=SingletonClass):
    def __init__(self,model_name:str) -> None:
        if model_name:
            self.model = self.get_gliNER_model(model_name=model_name)
        else:
            self.model = self.get_gliNER_model()


    def get_gliNER_model(self, model_name:str="urchade/gliner_large-v2.1"):
        print(f"[.] Loading {model_name} Gliner Model")
        return GLiNER.from_pretrained(model_name)
    

def flatten_json_strings(data: Union[Dict, List, Any]) -> List[str]:
    """
    Recursively traverse a nested list/dictionary structure and collect all string values.
    :param data: Could be a dict, list, or primitive data type.
    :return: A list of all string values found at any nesting level.
    """
    strings_found = []

    if isinstance(data, dict):
        for key, value in data.items():
            strings_found.append(str(key))
            if isinstance(value, (dict, list)):
                strings_found.extend(flatten_json_strings(value))
            else:
                strings_found.append(str(value))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                strings_found.extend(flatten_json_strings(item))
            else:
                strings_found.append(str(item))
    else:
        # If it's a single primitive type (e.g., int, float, str, etc.)
        strings_found.append(str(data))

    return strings_found


def extract_and_check_entities(
    model,
    response: str,
    previous_context: List[dict],
    current_user_query: str,
    data_entities=None,
    custom_data_entities=None,
    threshold: float = 0.5
) -> dict:
    """
    1. Extract entities from 'response' using a GLiNER-like model.
    2. Recursively parse 'previous_context' to collect all string values.
    3. Append 'current_user_query' to context as well.
    4. Check if each extracted entity or its subwords appear in the flattened context strings.
    5. Return a summary dict of the entity-check results.

    :param model: GLiNER or similar model with a 'predict_entities' method.
    :param response: The textual response from which we want to extract entities.
    :param previous_context: A list of JSON objects (dicts), potentially nested, containing things like queries, responses, etc.
    :param current_user_query: The latest user query (also considered as context).
    :param data_entities: Default entity types or schema for model's 'predict_entities', if needed.
    :param custom_data_entities: Custom entity types or schema to override 'data_entities', if provided.
    :param threshold: Confidence threshold for entity extraction.
    :return: A dictionary containing:
        - total_found (int): Number of extracted entities.
        - matched (float): A match count that includes partial (subword) matches.
        - keywords_extracted (List[str]): Extracted entity strings (lowercased).
        - score (float): Ratio of (matched / total_found), rounded to 2 decimals.
    """

    # 1. Predict entities from the response
    entities = model.predict_entities(
        response,
        data_entities if not custom_data_entities else custom_data_entities,
        threshold=threshold
    )

    # 2. Flatten all strings from previous_context
    all_context_texts = []

    for context_item in previous_context:
        all_context_texts.extend(flatten_json_strings(context_item))

    # 3. Append the current_user_query to the context
    if current_user_query:
        all_context_texts.append(current_user_query)

    # Convert all context strings to lowercase once to optimize repeated calls
    all_context_texts_lower = [txt.lower() for txt in all_context_texts]

    # 4. Check matches
    matched = 0.0
    total_found = len(entities)
    keywords_extracted = []
    keywords_extracted_not_matches = []
    keywords_extracted_matches = []

    for entity in entities:
        keyword = entity["text"]
        keyword_lower = keyword.lower()
        keywords_extracted.append(keyword_lower)

        # Check if the entire keyword is present in any context string
        if check_entity_in_source(entity=keyword_lower, source_lines=all_context_texts_lower):
        # if any(keyword_lower in context_str for context_str in all_context_texts_lower):
            matched += 1
            keywords_extracted_matches.append(keyword_lower)
        else:
            # If entire keyword not found, check subwords
            subwords = re.split(r'[&\$ \-.,]+', keyword_lower)
            subwords = [word for word in subwords if word]
            subwords_length = len(subwords)
            subwords_matched = 0

            for subword in subwords:
                # if any(subword in context_str for context_str in all_context_texts_lower):
                if check_entity_in_source(entity=subword, source_lines=all_context_texts_lower):
                    subwords_matched += 1
                    keywords_extracted_matches.append(subword)
                else:
                    keywords_extracted_not_matches.append(subword)

            matched += (subwords_matched / subwords_length) if subwords_length > 0 else 0

    # 5. Calculate score
    score = round(matched / total_found, 2) if total_found > 0 else 1
    print("All context ---> \n",all_context_texts_lower)
    return {
        "total_found": total_found,
        "matched": matched,
        "keywords_extracted": keywords_extracted,
        "score": score,
        "keywords_extracted_not_matched":keywords_extracted_not_matches,
        "keywords_extracted_matches": keywords_extracted_matches
    }
