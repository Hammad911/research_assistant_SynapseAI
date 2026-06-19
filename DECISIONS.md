# Architectural & Design Decisions

## Bug #3: Resetting the Retry Budget (`attempts`)

**Ambiguity**: Should `attempts` act as a persistent counter across an entire multi-turn conversation, or as a per-question retry budget? Furthermore, if it's a per-question budget, should it be reset by the API layer (`/chat`) or managed internally by the graph?

**Decision**: `attempts` is a per-question retry budget. The API layer should not be responsible for resetting internal graph state, so we removed `"attempts": 0` from `app/main.py` and moved the reset logic into `app/agents/clarity.py`.

**Nuance / Consideration**: 
By resetting `attempts` in `clarity_node`, it resets on every pass through `clarity_node`, including the resume-after-interrupt path when the user provides a clarification. 
Does this mid-cycle reset cause a bug where attempts go back to 0 during the validation loop? 
*Conclusion*: No. The validation loop strictly cycles between `validator_node` and `research_node`. `clarity_node` is only executed at the very start of a new question (and its corresponding resume path). It is never re-entered during the validation loop. Therefore, resetting to `0` inside `clarity_node` perfectly guarantees the budget is initialized to 0 right before the `research_validator` loop begins, without ever stomping the budget mid-validation.
