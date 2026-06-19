from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_resume_endpoint():
    # We can mock `graph.invoke` to ensure it's called with `Command(resume=...)`
    import langgraph.types
    from unittest.mock import patch
    
    with patch("app.main.graph.invoke") as mock_invoke:
        # mock invoke should return a dummy response to avoid unpacking errors
        from langchain_core.messages import AIMessage
        mock_invoke.return_value = {"messages": [AIMessage(content="mock answer")]}
        
        response = client.post("/resume", json={"thread_id": "test-123", "clarification": "My clarification"})
        assert response.status_code == 200
        assert response.json()["answer"] == "mock answer"
        
        # Verify that invoke was called with Command(resume="My clarification")
        args, kwargs = mock_invoke.call_args
        inputs = args[0]
        assert isinstance(inputs, langgraph.types.Command)
        assert inputs.resume == "My clarification"
        assert args[1] == {"configurable": {"thread_id": "test-123"}}
