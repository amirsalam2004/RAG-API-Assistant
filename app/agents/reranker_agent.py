from services.llm_service import llm_call
import json

def reranker_agent(state):
    prompt = f"""
    User request:
    {state.search_query}

    Candidates:
    {json.dumps(state.candidates, indent=2)}

    Score each from 0 to 1

    Return ONLY JSON:
    [
      {{"id": 1, "score": 0.9}}
    ]
    """
    
    response = llm_call(prompt)

    ranked = json.loads(response)