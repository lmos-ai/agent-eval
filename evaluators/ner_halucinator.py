# evaluators/ner_halucination.py
from evaluators.base import BaseEvaluator
from typing import Any, Dict, List
from models.gliner_model import extract_and_check_entities
from conversations.conversation_format import ConversationEntry


class NERHalucinationEvaluator(BaseEvaluator):
    def __init__(self, ner_model, ner_entities, threshold=0.7):
        self.ner_model = ner_model
        self.ner_entities = ner_entities
        self.threshold = threshold

    def run_evaluation(
        self,
        conversation_log: ConversationEntry,
        previous_context: List[Dict[str, Any]],
        matched_step: Dict[str, Any]=None,
        simulation_steps: List[Dict[str, Any]]=None
    ) -> Dict[str, Any]:
        """
        Evaluate NER halucination for the 'conversation_log' response.
        """
        if conversation_log is None:
            raise ValueError("Please pass Conversation log.")
        actual_response = conversation_log.response
        current_user_query = conversation_log.user_query

        ner_response = extract_and_check_entities(
            model=self.ner_model,
            response=actual_response,
            previous_context=previous_context,
            current_user_query=current_user_query,
            threshold=self.threshold,
            data_entities=self.ner_entities
        )

        # Prepare a dict of results to merge with the pipeline output
        return {
            "ner_score": ner_response['score'],
            "ner_halucination_safe_index": (1 - ner_response['score']) * 100,
            "ner_keyword_extracted": ner_response['keywords_extracted'],
            "ner_keywords_extracted_matches": ner_response['keywords_extracted_matches'],
            "ner_keywords_extracted_not_matched": ner_response['keywords_extracted_not_matched']
        }
