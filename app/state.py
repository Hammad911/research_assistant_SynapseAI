"""Shared graph state.

Every agent reads from and writes to this state object as the conversation
flows through the graph. The `messages` list is the running conversation
transcript that gives each agent the context of previous turns.
"""

from typing import Optional, TypedDict

from langchain_core.messages import AnyMessage


class AgentState(TypedDict, total=False):
    # Running conversation transcript, shared across every agent and turn.
    messages: list[AnyMessage]

    # Clarity agent output.
    clarity_status: str            # "clear" | "needs_clarification"
    clarification: Optional[str]   # the user's answer to a clarifying question

    # Research agent output.
    findings: str
    raw_research: str
    raw_confidence_score: int      # 0-10, original unblended score
    agreement_ratio: float         # 0.0-1.0, fraction of sources supporting claims
    confidence_score: int          # 0-10, blended score used for routing

    # Validator agent output.
    validation_result: str         # "sufficient" | "insufficient"
    attempts: int                  # number of research attempts so far
