from app.agents.clarity import clarity_node, ClarityVerdict
from langchain_core.messages import HumanMessage
from unittest.mock import MagicMock, patch

def test_clarity_node_resets_attempts():
    state = {"messages": [HumanMessage(content="What is Acme?")], "attempts": 3}
    
    with patch("app.agents.clarity.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_get_llm.return_value.with_structured_output.return_value = mock_llm
        mock_llm.invoke.return_value = ClarityVerdict(status="clear")

        result = clarity_node(state)
        
        assert result["clarity_status"] == "clear"
        assert result["attempts"] == 0
