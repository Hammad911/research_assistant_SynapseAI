from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage
from app.agents.validator import validator_node, ValidationVerdict

def test_validator_increments_attempts():
    # Mock the LLM call to return a specific verdict
    with patch("app.agents.validator.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_get_llm.return_value.with_structured_output.return_value = mock_llm
        mock_llm.invoke.return_value = ValidationVerdict(validation_result="insufficient")

        # Initial state with 1 attempt
        state = {
            "messages": [HumanMessage(content="What is Acme Corp?")],
            "findings": "Some initial findings.",
            "attempts": 1
        }

        # Run the validator node
        result = validator_node(state)

        # Ensure the attempts counter is incremented and returned
        assert "attempts" in result
        assert result["attempts"] == 2
        assert result["validation_result"] == "insufficient"
