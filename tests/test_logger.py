import logging
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.logger import SensitiveLogCallbackHandler

def test_sensitive_log_callback_masks_human_messages(caplog):
    handler = SensitiveLogCallbackHandler()
    
    messages = [
        [
            SystemMessage(content="You are an assistant."),
            HumanMessage(content="My social security number is 123-45-678"),
            AIMessage(content="I should not log that.")
        ]
    ]
    
    with caplog.at_level(logging.INFO):
        handler.on_chat_model_start(serialized={}, messages=messages)
    
    log_output = caplog.text
    
    # SystemMessage and AIMessage should be unmodified in logs
    assert "You are an assistant." in log_output
    assert "I should not log that." in log_output
    
    # HumanMessage should be masked
    assert "My social security number is 123-45-678" not in log_output
    assert "[CENSORED]" in log_output
