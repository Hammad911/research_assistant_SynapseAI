# Multi-Agent Company Research Assistant

A multi-agent research assistant built with **LangGraph** that helps users
gather information about companies. Four specialized agents collaborate to
clarify the request, research it on the web, validate the findings, and
synthesize a clear answer.

## Architecture

```
START → Clarity → Research → ┬→ Synthesis → END
                             │
                             └→ Validator → ┬→ Research (loop)
                                            └→ Synthesis
```

| Agent | Responsibility | Output |
|-------|----------------|--------|
| **Clarity** | Checks whether the request is specific enough; asks the user a clarifying question if not. | `clarity_status` |
| **Research** | Searches the web (Tavily) for news, financials and recent developments. | `findings`, `confidence_score` (0–10) |
| **Validator** | Decides whether the findings are good enough; loops back for another pass if not. | `validation_result` |
| **Synthesis** | Writes the final, well-structured answer. | final message |

## Features

- ✅ **Multi-turn conversation** — conversation history is preserved across turns, so follow-ups like *"What about their competitors?"* work naturally.
- ✅ **Human-in-the-loop** — when a request is ambiguous, the graph pauses and asks the user to clarify, then continues where it left off.
- ✅ **Confidence-based routing** — high-confidence research goes straight to synthesis; low-confidence research is validated first.
- ✅ **Validation loop** — findings are re-researched until they are sufficient (up to `MAX_VALIDATION_ATTEMPTS`).
- ✅ **Web UI** — a minimal chat interface served by FastAPI.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # then add your OPENAI_API_KEY and TAVILY_API_KEY

uvicorn app.main:app --reload
```

Open http://localhost:8000 and start asking about companies.

## Project layout

```
app/
  main.py        FastAPI app (chat / resume endpoints + static UI)
  graph.py       LangGraph wiring and conditional routing
  state.py       shared graph state schema
  config.py      environment-driven settings
  llm.py         chat-model factory
  agents/        clarity, research, validator, synthesis
  tools/         Tavily search tool
static/
  index.html     chat UI
tests/
  test_smoke.py  routing + compile smoke tests
```

## Tests

```bash
pytest
```

## Example queries

- "Tell me about Stripe's recent funding."
- "What is OpenAI working on lately?"
- "Tell me about the company." *(the assistant will ask which one)*
