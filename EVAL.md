# Research Assistant - Evaluation Harness

This directory contains the automated evaluation harness designed to rigorously test the Research Assistant's routing correctness, latency, cost, and groundedness.

## Files
- `dataset.jsonl`: A labeled dataset of test queries, categorized by expected graph routing behavior (e.g., ambiguous queries should trigger the `clarity_node`, while financial queries should hit the `research_node`).
- `run_eval.py`: The main execution script. It runs the entire LangGraph asynchronously for each query and compares the actual path and output against the expected labels.

## Evaluation Metrics
When you run the harness, it computes four key metrics:
1. **Routing Accuracy:** Verifies that the internal graph trajectory precisely matches the expected sequence of nodes.
2. **Groundedness Accuracy:** Uses an "LLM as a Judge" pattern to extract facts from the final answer and ensure it doesn't hallucinate. It cross-references the answer against a list of expected facts in the dataset.
3. **Average Latency:** The end-to-end execution time from query to final synthesized output.
4. **Estimated Tokens:** The aggregate token consumption (input + output) for the entire LangGraph trajectory, extracted via Langchain callbacks/metadata.

## Running the Evaluation
To execute the harness, activate your virtual environment and run:

```bash
python eval/run_eval.py
```

The script will output progress for each query, showing the exact nodes visited, and conclude with a summary dashboard.

> [!TIP]
> The groundedness check currently uses `gemini-2.5-flash` with strict structured output. You can tune the prompt in `run_eval.py` to be more or less forgiving, or switch it to a faster exact-match algorithm to save API tokens if your dataset grows significantly.
