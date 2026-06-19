import sys
import os
import json
import time
from uuid import uuid4
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage

# Add the parent directory to the path so we can import 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.graph import graph
from app.llm import get_llm

class GroundednessScore(BaseModel):
    is_grounded: bool = Field(description="True if the answer contains the expected facts and does not hallucinate, False otherwise.")
    reasoning: str = Field(description="Reasoning for the groundedness score.")

def check_groundedness(answer: str, expected_facts: list[str]) -> bool:
    if not expected_facts:
        return True # Nothing to ground against
    
    llm = get_llm(temperature=0.0).with_structured_output(GroundednessScore)
    prompt = f"""Evaluate if the following answer is grounded in the expected facts.
Expected Facts: {', '.join(expected_facts)}

Answer:
{answer}
"""
    result = llm.invoke(prompt)
    return result.is_grounded

def run_evaluation():
    dataset_path = os.path.join(os.path.dirname(__file__), 'dataset.jsonl')
    
    with open(dataset_path, 'r') as f:
        dataset = [json.loads(line) for line in f]

    results = []
    
    print(f"Starting evaluation on {len(dataset)} examples...")
    
    for item in dataset:
        print(f"\n--- Evaluating: {item['id']} ---")
        thread_id = str(uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        state = {"messages": [HumanMessage(content=item['query'])]}
        
        start_time = time.time()
        
        nodes_visited = []
        final_answer = ""
        total_tokens = 0
        
        try:
            for event in graph.stream(state, config, stream_mode="updates"):
                for node_name, node_state in event.items():
                    nodes_visited.append(node_name)
                    
                    # Accumulate token usage if available in the messages
                    if "messages" in node_state and node_state["messages"]:
                        last_msg = node_state["messages"][-1]
                        if hasattr(last_msg, "usage_metadata") and last_msg.usage_metadata:
                            total_tokens += last_msg.usage_metadata.get("total_tokens", 0)

                    # Capture final answer from synthesis or clarity
                    if node_name in ["synthesis", "clarity"]:
                        final_answer = node_state.get("messages", [None])[-1].content
                        if node_name == "clarity":
                            final_answer = node_state.get("clarity_question", final_answer)
                            
        except Exception as e:
            print(f"Error executing graph: {e}")
            final_answer = str(e)
            
        latency = time.time() - start_time
        
        # Routing Correctness Check
        # We check if the expected nodes are a sub-sequence of the visited nodes
        expected_nodes = item['expected_nodes']
        routing_correct = all(node in nodes_visited for node in expected_nodes)
        
        # Groundedness Check
        is_grounded = check_groundedness(final_answer, item.get('expected_facts', []))
        
        print(f"Query: {item['query']}")
        print(f"Nodes Visited: {nodes_visited}")
        print(f"Routing Correct: {routing_correct}")
        print(f"Grounded: {is_grounded}")
        print(f"Latency: {latency:.2f}s")
        print(f"Estimated Tokens: {total_tokens}")
        
        results.append({
            "id": item['id'],
            "query": item['query'],
            "routing_correct": routing_correct,
            "is_grounded": is_grounded,
            "latency": latency,
            "tokens": total_tokens
        })
        
    print("\n=== Evaluation Summary ===")
    total = len(results)
    routing_pass = sum(1 for r in results if r['routing_correct'])
    grounded_pass = sum(1 for r in results if r['is_grounded'])
    avg_latency = sum(r['latency'] for r in results) / total
    
    print(f"Total Examples: {total}")
    print(f"Routing Accuracy: {routing_pass}/{total} ({routing_pass/total*100:.1f}%)")
    print(f"Groundedness Accuracy: {grounded_pass}/{total} ({grounded_pass/total*100:.1f}%)")
    print(f"Average Latency: {avg_latency:.2f}s")

if __name__ == "__main__":
    run_evaluation()
