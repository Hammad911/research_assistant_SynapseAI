# Research Assistant - Bug Report & Post-Mortem

This document details the critical bugs identified and resolved in the Research Assistant baseline, along with their symptoms, root causes, fixes, and prevention strategies.

---

### 1. `/resume` Endpoint Crash
- **Location:** `app/main.py`
- **Symptom:** The server returned a 500 Internal Server Error when trying to resume the LangGraph from a suspended, human-in-the-loop state.
- **Root Cause:** LangGraph expects thread configurations to be passed as a `RunnableConfig` object with a `configurable` key. The endpoint passed a bare dictionary `{"thread_id": thread_id}`.
- **Fix:** Wrapped the thread ID correctly: `{"configurable": {"thread_id": thread_id}}`.
- **Prevention:** Use strict static typing (e.g., `TypedDict` for configs) and ensure integration tests cover all graph suspension and resumption transitions.

### 2. Infinite Validation Loops (State Overwrite)
- **Location:** `app/agents/validator.py`
- **Symptom:** The validation loop never hit its maximum attempt limit, running indefinitely until API failure.
- **Root Cause:** The `attempts` state variable was hardcoded to `1` on every pass instead of incrementing.
- **Fix:** Implemented safe state incrementation: `attempts = state.get("attempts", 0) + 1`.
- **Prevention:** Graph state mutations must be unit tested with edge case assertions specifically targeting loop iteration bounds.

### 3. Stuck State Post-Clarification
- **Location:** `app/agents/clarity.py`
- **Symptom:** If research failed after 3 attempts and the system asked the user for clarification, the next research attempt instantly failed because `attempts` was still at 3.
- **Root Cause:** The attempts counter was not cleared when transitioning from a human-in-the-loop phase back to a new research cycle.
- **Fix:** Explicitly returned `{"attempts": 0}` from the `clarity_node` to reset the cycle.
- **Prevention:** Identify cyclical paths in StateGraphs and explicitly define state reset semantics for each cycle boundary.

### 4. Routing Off-By-One Error
- **Location:** `app/graph.py` (in `route_after_research`)
- **Symptom:** Valid research runs with a confidence score of `6` (the exact threshold) were incorrectly routed to the validator instead of synthesis.
- **Root Cause:** The routing check used strict inequality (`>`) instead of inclusive inequality (`>=`) for the confidence threshold.
- **Fix:** Changed `>` to `>=` in the `route_after_research` conditional.
- **Prevention:** Always write boundary test cases (e.g., `score == threshold`) in unit tests rather than just testing extreme values.

### 5. Context Truncation Amnesia
- **Location:** `app/agents/research.py` (in `_build_query`)
- **Symptom:** The research agent forgot the previous conversation history and only executed web searches based on the literal text of the very last user message.
- **Root Cause:** `_build_query` blindly extracted `state["messages"][-1].content` and fed it directly to the search tool.
- **Fix:** Introduced an LLM rewrite step that consumes the full conversation history and synthesizes a context-aware search query.
- **Prevention:** Centralize query extraction and enforce multi-turn conversation mocks in the test suite.

### 6. Cascading Search Tool Failures
- **Location:** `app/tools/search.py`
- **Symptom:** Transient API limits or timeouts from Tavily crashed the entire agent graph immediately.
- **Root Cause:** External HTTP calls were executed with no retries or error handling.
- **Fix:** Wrapped the search client invocation in a `try/except` block with a 3-attempt exponential backoff loop.
- **Prevention:** All external API calls in an agentic workflow must have explicit retry policies, backoffs, and timeouts defined.

### 7. PII / Secrets Leakage in Logs
- **Location:** `app/config.py`
- **Symptom:** The `openai_api_key` and `tavily_api_key` were printed in plaintext to stdout on server boot.
- **Root Cause:** The `Settings` object printed its `model_dump()`, which exposed raw string types for sensitive credentials.
- **Fix:** Changed the credential fields from `str` to Pydantic's `SecretStr`, which natively masks values in `repr` and `dump()`.
- **Prevention:** Adopt `SecretStr` exclusively for all sensitive configuration variables across the codebase.

### 8. Bypassed Validation
- **Location:** `app/agents/synthesis.py`
- **Symptom:** The synthesis agent mostly ignored the validator's feedback and generated answers based on the unfiltered, raw search dump.
- **Root Cause:** The input selection priority heavily preferred the `raw_research` state over the validated `findings` state.
- **Fix:** Flipped the preference to `findings` and injected a strict caveat prompt into the Synthesis LLM if the validation result was marked "insufficient."
- **Prevention:** Enforce strict data flow mapping. Downstream nodes must consume the specific artifacts produced by upstream validation nodes, not raw upstream data.

### 9. Prompt Injection via Unsanitized Data
- **Location:** `app/agents/research.py` & `app/agents/synthesis.py`
- **Symptom:** Untrusted web content flowed directly into prompts without isolation, creating a high risk of prompt injection or system instruction override.
- **Root Cause:** Raw web strings were concatenated directly into the LLM `HumanMessage`.
- **Fix:** Escaped the content using `html.escape` and wrapped it securely in XML delimiters (`<search_results>` and `<result>`).
- **Prevention:** Treat all external tool outputs as untrusted input. Use structured delimiters and escaping functions before passing data to an LLM.

### 10. Lack of CI Boundary Coverage
- **Location:** `tests/test_smoke.py`
- **Symptom:** CI passed despite graph logic errors (like the threshold bug mentioned in #4).
- **Root Cause:** Test assertions only verified extremes (e.g., confidence = 2 or 8, attempts = 1 or 5), entirely missing boundary values.
- **Fix:** Added exact boundary case assertions (`confidence == threshold`, `attempts == max_attempts`) to the CI suite.
- **Prevention:** Enforce Boundary Value Analysis (BVA) as a mandatory requirement during code review for any control flow logic.

### 11. Search Fallback Prompt Injection
- **Location:** `app/tools/search.py` & `app/agents/validator.py`
- **Symptom:** When search retries were exhausted, the tool returned a fake dictionary containing `[SYSTEM: ...]`. Because of the fix in #9, this fake data was wrapped in XML tags, tricking the LLM into treating a failure as legitimate web content, causing confident hallucinations.
- **Root Cause:** Using string sentinels disguised as data instead of structural failure signals.
- **Fix:** Raised a custom `SearchUnavailableError` exception in the tool, caught it in the research node, and fast-pathed the validator node to bypass the LLM entirely on a score of `0`.
- **Prevention:** Use Python exceptions for out-of-band failure signaling; do not mix meta-instructions with data payloads.

### 12. Overconfident LLM Hallucinations (Calibration Error)
- **Location:** `app/agents/research.py`
- **Symptom:** The LLM routinely reported high confidence scores (8-10) even when the source material did not support the claims made.
- **Root Cause:** LLM self-reported metrics are poorly calibrated and lack independent verification.
- **Fix:** Extended the `ResearchResult` schema to calculate a cross-source `agreement_ratio` based on supporting vs. contradicting URLs, and mathematically penalized the `confidence_score` if agreement was low.
- **Prevention:** Implement cross-source consistency checks, multi-agent debate, or independent LLM Judges rather than trusting single-pass self-reported confidence.
