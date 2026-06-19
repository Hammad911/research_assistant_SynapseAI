from app.agents.research import _build_query, research_node, SearchQuery, ResearchResult
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from unittest.mock import MagicMock, patch

def test_build_query_uses_history():
    state = {
        "messages": [
            HumanMessage(content="What is Acme?"),
            AIMessage(content="Acme is a corp."),
            HumanMessage(content="What about their competitors?")
        ]
    }
    
    with patch("app.agents.research.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_get_llm.return_value.with_structured_output.return_value = mock_llm
        mock_llm.invoke.return_value = SearchQuery(query="Acme Corp competitors")

        query = _build_query(state)
        
        assert query == "Acme Corp competitors"
        
        # Verify the LLM was called with the full history
        args, _ = mock_llm.invoke.call_args
        prompt = args[0]
        assert len(prompt) == 4 # SysMsg + 3 messages
        assert isinstance(prompt[0], SystemMessage)
        assert prompt[-1].content == "What about their competitors?"

def test_research_node_uses_history():
    state = {
        "messages": [
            HumanMessage(content="What is Acme?"),
            AIMessage(content="Acme is a corp."),
            HumanMessage(content="What about their competitors?")
        ]
    }
    
    with patch("app.agents.research._build_query") as mock_build, \
         patch("app.agents.research.tavily_search") as mock_search, \
         patch("app.agents.research.get_llm") as mock_get_llm:
        
        mock_build.return_value = "Acme Corp competitors"
        mock_search.return_value = [{"content": "Competitor 1"}]
        
        mock_llm = MagicMock()
        mock_get_llm.return_value.with_structured_output.return_value = mock_llm
        mock_llm.invoke.return_value = ResearchResult(findings="Found them.", confidence_score=10)

        result = research_node(state)
        
        assert result["findings"] == "Found them."
        
        # Verify the LLM was called with the full history
        args, _ = mock_llm.invoke.call_args
        prompt = args[0]
        # SysMsg + 3 messages + HumanMessage with search results
        assert len(prompt) == 5
        assert isinstance(prompt[0], SystemMessage)
        assert "Search results for 'Acme Corp competitors':" in prompt[-1].content
