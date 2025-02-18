class QueryScorer:
    """
    A class to calculate the score of a query response based on:
    1. Whether the expected step was matched.
    2. Which functions were expected vs. actually called.
    3. Whether there was hallucination or an incorrect response according to the LLM result.
    """
    def __init__(self, halucination_threshold:float = 0.7):
        self.halucination_threshold = halucination_threshold
        if self.halucination_threshold >1 or self.halucination_threshold<0:
            raise Exception("NER threshold must be between 0-1")
        

    def calculate_score(self, 
                        matched_step: bool,
                        expected_functions_names: list, 
                        actual_functions_names: list, 
                        llm_result: dict) -> dict:
        """
        Calculates the score for a given query response.

        Args:
            matched_step (bool): Whether the response matched the required step.
            expected_functions_names (list): The list of function names we expect to be called.
            actual_functions_names (list): The list of function names actually called.
            llm_result (dict): A dictionary containing flags about hallucination and correctness,
                               e.g. {"correct_response": bool}.

        Returns:
            dict: A dictionary containing:
                  {
                    "score": float,
                    "is_correct_step_followed": bool,
                    "reasoning": str,
                    "missing_functions": list,
                    "incorrect_functions": list
                  }
        """
        score = 0
        is_correct_step_followed = False
        reasoning = ""
        missing_functions = []
        incorrect_functions = []
        
        ner_halucination_score = llm_result.get("ner_score", None)
        if ner_halucination_score:
            if ner_halucination_score >1 or ner_halucination_score < 0:
                raise Exception("NER halucination score must be between 0-1")

        print("Scoring the query")

        # If the required step was found
        if matched_step:
            number_of_expected_funcs = len(expected_functions_names)
            if number_of_expected_funcs > 0:
                # Check each expected function against the actual functions
                for func in expected_functions_names:
                    if func in actual_functions_names:
                        # Only remain True if it's already True (logical AND),
                        # but typically you'd want to set is_correct_step_followed = True
                        # the first time a match is found or something similar.
                        is_correct_step_followed = is_correct_step_followed and True if is_correct_step_followed else True
                        print(f"Adding score: {100/number_of_expected_funcs} since {func} function was found in actual functions.")
                        score += (100 / number_of_expected_funcs)
                    else:
                        missing_functions.append(func)
                        is_correct_step_followed = False
            else:
                # No expected function calls, but the step was found; reward full score
                print("Score = 100 since the step was found but no expected function calls were required.")
                score = 100
            
            # Identify any functions that were not expected but were still called
            for func in actual_functions_names:
                if func not in expected_functions_names:
                    incorrect_functions.append(func)

            # Apply halucination/correctness checks
            if ner_halucination_score >= self.halucination_threshold and not llm_result.get("correct_response"):
                print("Score = 0 since there is hallucination and the response is not correct.")
                score = 0
            elif ner_halucination_score >= self.halucination_threshold:
                print(f"Score is halved to {score/2} since there is hallucination.")
                score = score / 2
            elif not llm_result.get("correct_response"):
                print(f"Score is halved to {score/2} since the response is not correct.")
                score = score / 2

        else:
            # If the required step was NOT found
            if not actual_functions_names:
                # No functions were called
                is_correct_step_followed = True
                reasoning = "No steps followed and no functions were called during the query."
                
                if ner_halucination_score >= self.halucination_threshold:
                    print("Score = 0 since no step was followed and it is hallucinated.")
                    score = 0
                else:
                    if llm_result.get("correct_response"):
                        print("Score = 100 since no steps followed, no hallucination, and the response is correct.")
                        score = 100
                    else:
                        print("Score = 50 since no steps followed, no hallucination, but the response is not correct.")
                        score = 50
            else:
                # Functions were called even though the step was not found
                is_correct_step_followed = False
                print("Score = 0 since the step was not followed but actual function calls were found in the response.")
                score = 0
                reasoning = ("Wrong steps were followed as the intent of the query was not to call any agent, "
                             "but the response has function calls. Thus, agents were called unnecessarily.")

        return {
            "score": score,
            "is_correct_step_followed": is_correct_step_followed,
            "reasoning": reasoning,
            "missing_functions": missing_functions,
            "incorrect_functions": incorrect_functions
        }
