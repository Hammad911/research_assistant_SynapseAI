import logging
from typing import Any, Dict, List
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage
from langchain_core.outputs import LLMResult

# Configure standard logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("langchain_debug")

class SensitiveLogCallbackHandler(BaseCallbackHandler):
    """Callback handler that logs LLM prompts and responses, masking PII in HumanMessages."""
    
    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[Any]],
        **kwargs: Any,
    ) -> None:
        """Run when LLM starts running. Censor HumanMessages."""
        censored_messages = []
        for seq in messages:
            censored_seq = []
            for msg in seq:
                if isinstance(msg, HumanMessage):
                    # Censor the potentially sensitive human input
                    censored_seq.append(HumanMessage(content="[CENSORED]", additional_kwargs=msg.additional_kwargs))
                else:
                    censored_seq.append(msg)
            censored_messages.append(censored_seq)
            
        logger.info(f"LLM Prompt Started: {censored_messages}")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        logger.info(f"LLM Response Ended: {response.generations}")

    def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        """Run when LLM errors."""
        logger.error(f"LLM Error: {error}")
