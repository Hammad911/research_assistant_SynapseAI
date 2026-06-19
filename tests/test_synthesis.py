from app.agents.synthesis import synthesis_node
from langchain_core.messages import HumanMessage, SystemMessage
from unittest.mock import MagicMock, patch

def test_synthesis_prefers_findings():
    state = {
        "messages": [HumanMessage(content="Hello")],
        "raw_research": "raw unvalidated garbage",
        "findings": "clean validated facts",
    }
    
    with patch("app.agents.synthesis.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_llm.invoke.return_value.content = "Answer"

        synthesis_node(state)
        
        args, _ = mock_llm.invoke.call_args
        prompt_messages = args[0]
        system_message = prompt_messages[0]
        
        # Should contain findings, not raw_research
        assert "clean validated facts" in system_message.content
        assert "raw unvalidated garbage" not in system_message.content

def test_synthesis_handles_insufficient_validation():
    state = {
        "messages": [HumanMessage(content="Hello")],
        "findings": "some facts",
        "validation_result": "insufficient"
    }
    
    with patch("app.agents.synthesis.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_llm.invoke.return_value.content = "Answer"

        synthesis_node(state)
        
        args, _ = mock_llm.invoke.call_args
        prompt_messages = args[0]
        system_message = prompt_messages[0]
        
        # Should contain the warning
        assert "WARNING: The validation loop determined these findings are insufficient" in system_message.content
