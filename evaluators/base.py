# evaluators/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from conversations.conversation_format import ConversationEntry

class BaseEvaluator(ABC):
    """
    Abstract base for any evaluation step in the pipeline.
    """

    @abstractmethod
    def run_evaluation(
        self,
        conversation_log: ConversationEntry,
        previous_context: List[Dict[str, Any]]=None,
        matched_step: Dict[str, Any]=None,
        simulation_steps: List[Dict[str, Any]]=None
    ) -> Dict[str, Any]:
        """
        Runs the evaluation step and returns a dict with evaluation results
        (e.g. 'score', 'is_halucinated', 'reasoning', etc.).
        """
        pass
