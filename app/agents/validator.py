"""Validator agent.

Judges whether the research findings are good enough to answer the user's
question. If not, it sends the work back to the research agent for another pass
(up to a maximum number of attempts).
"""

from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from app.llm import get_llm
from app.state import AgentState

VALIDATOR_SYSTEM_PROMPT = """You are the Validator Agent in a company-research assistant.
Assess whether the research findings are complete and relevant enough to answer
the user's question. Respond "sufficient" if they are, or "insufficient" if more
or better research is needed."""


class ValidationVerdict(BaseModel):
    validation_result: Literal["sufficient", "insufficient"]


def validator_node(state: AgentState) -> dict:
    question = state["messages"][-1].content
    findings = state.get("findings", "")
    confidence = state.get("confidence_score", 0)

    # Record that we've used another research attempt.
    attempts = state.get("attempts", 0) + 1

    # Fast-path: if research failed completely, don't waste an LLM call
    if confidence == 0:
        return {
            "validation_result": "insufficient",
            "attempts": attempts,
        }

    llm = get_llm(temperature=0).with_structured_output(ValidationVerdict)
    verdict: ValidationVerdict = llm.invoke(
        [
            SystemMessage(content=VALIDATOR_SYSTEM_PROMPT),
            HumanMessage(content=f"User question: {question}\n\nFindings:\n{findings}"),
        ]
    )

    return {
        "validation_result": verdict.validation_result,
        "attempts": attempts,
    }
