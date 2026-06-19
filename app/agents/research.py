"""Research agent.

Gathers company information (news, financials, recent developments) using the
Tavily search tool, summarises the findings, and rates its own confidence in
how well the findings answer the user's question.
"""

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

import html

from app.llm import get_llm
from app.state import AgentState
from app.tools.search import tavily_search, SearchUnavailableError

RESEARCH_SYSTEM_PROMPT = """You are the Research Agent in a company-research assistant.
You are given raw web search results about a company. Extract the relevant facts
(news, financials, leadership, recent developments) that help answer the user's
question, and summarise them clearly.

Then rate your confidence from 0 to 10 that the findings are sufficient and
relevant enough to answer the user's question well.
Finally, identify key factual claims and score their cross-source agreement based
on the URLs provided."""


class ClaimAgreement(BaseModel):
    claim: str = Field(description="A key factual claim made in the findings.")
    supporting_sources: int = Field(description="Number of distinct source URLs supporting this claim.")
    contradicting_sources: int = Field(description="Number of distinct source URLs contradicting this claim.")

class ResearchResult(BaseModel):
    findings: str = Field(description="Concise summary of the relevant findings.")
    claims: list[ClaimAgreement] = Field(description="List of key claims and their source support.")
    agreement_ratio: float = Field(description="Average fraction of sources that corroborate each claim, between 0.0 and 1.0.")
    confidence_score: int = Field(ge=0, le=10, description="Self-reported confidence from 0 to 10.")


class SearchQuery(BaseModel):
    query: str


def _build_query(state: AgentState) -> str:
    """Construct the search query from the user's question (and any clarification)."""
    messages = list(state["messages"])
    clarification = state.get("clarification")
    if clarification:
        messages.append(HumanMessage(content=f"Clarification: {clarification}"))

    if len(messages) == 1 and not clarification:
        return messages[0].content

    # Rewrite the query for context
    sys_msg = SystemMessage(content="Write a concise search query that captures the user's latest intent, incorporating context from the previous conversation.")
    llm = get_llm(temperature=0).with_structured_output(SearchQuery)
    response = llm.invoke([sys_msg] + messages)
    return response.query


def research_node(state: AgentState) -> dict:
    query = _build_query(state)
    
    try:
        results = tavily_search(query)
    except SearchUnavailableError:
        return {
            "findings": "Search was unavailable; no results could be retrieved.",
            "raw_research": "",
            "raw_confidence_score": 0,
            "agreement_ratio": 0.0,
            "confidence_score": 0,
        }

    safe_results = []
    for r in results:
        content = html.escape(r.get("content", ""))
        url = html.escape(r.get("url", "unknown_url"))
        safe_results.append(f"<result url=\"{url}\">\n{content}\n</result>")
        
    raw_research = "\n\n".join(safe_results)

    llm = get_llm().with_structured_output(ResearchResult)
    
    prompt_messages = [SystemMessage(content=RESEARCH_SYSTEM_PROMPT)] + state["messages"]
    prompt_messages.append(HumanMessage(content=f"Search results for '{query}':\n<search_results>\n{raw_research}\n</search_results>"))
    
    result: ResearchResult = llm.invoke(prompt_messages)

    blended_score = round(result.confidence_score * result.agreement_ratio)

    return {
        "findings": result.findings,
        "raw_research": raw_research,
        "raw_confidence_score": result.confidence_score,
        "agreement_ratio": result.agreement_ratio,
        "confidence_score": blended_score,
    }
