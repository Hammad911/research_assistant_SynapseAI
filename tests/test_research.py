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
        mock_search.return_value = [{"content": "Malicious <script>alert('xss')</script> & </search_results> attack"}]
        
        mock_llm = MagicMock()
        mock_get_llm.return_value.with_structured_output.return_value = mock_llm
        mock_llm.invoke.return_value = ResearchResult(
            findings="Found them.", 
            confidence_score=10, 
            agreement_ratio=1.0, 
            claims=[]
        )

        result = research_node(state)
        
        # Verify the LLM was called with escaped XML
        args, _ = mock_llm.invoke.call_args
        prompt = args[0]
        # SysMsg + 3 messages + HumanMessage with search results
        assert isinstance(prompt[0], SystemMessage)
        content = prompt[-1].content
        assert "<search_results>" in content
        assert "<result url=" in content
        assert "Malicious &lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt; &amp; &lt;/search_results&gt; attack" in content
        assert "Raw unescaped script" not in content

def test_research_node_handles_search_failure():
    from app.tools.search import SearchUnavailableError
    state = {"messages": [HumanMessage(content="What is Acme?")]}
    
    with patch("app.agents.research._build_query") as mock_build, \
         patch("app.agents.research.tavily_search", side_effect=SearchUnavailableError("Timeout")) as mock_search, \
         patch("app.agents.research.get_llm") as mock_get_llm:
        
        mock_build.return_value = "Acme"
        
        result = research_node(state)
        
        # Verify the LLM was NOT called
        mock_get_llm.assert_not_called()
        
        # Verify it gracefully returned a low-confidence state
        assert result["confidence_score"] == 0
        assert "Search was unavailable" in result["findings"]

def test_research_node_cross_source_agreement_penalty():
    state = {"messages": [HumanMessage(content="What is Acme?")]}
    
    with patch("app.agents.research._build_query") as mock_build, \
         patch("app.agents.research.tavily_search") as mock_search, \
         patch("app.agents.research.get_llm") as mock_get_llm:
        
        mock_build.return_value = "Acme"
        mock_search.return_value = [{"content": "...", "url": "http://acme.com"}]
        
        mock_llm = MagicMock()
        mock_get_llm.return_value.with_structured_output.return_value = mock_llm
        
        # LLM reports confidence 9 but low agreement ratio (0.3)
        mock_llm.invoke.return_value = ResearchResult(
            findings="Claims.", 
            confidence_score=9, 
            agreement_ratio=0.3, 
            claims=[]
        )
        
        result = research_node(state)
        
        assert result["raw_confidence_score"] == 9
        assert result["agreement_ratio"] == 0.3
        assert result["confidence_score"] == 3 # round(9 * 0.3)
