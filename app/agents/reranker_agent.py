from services.llm_service import llm_call
import json

def reranker_agent(state):
    
    prompt = f"""
    User request:
    {state.search_query}

    Candidates:
    {json.dumps(state.candidates, indent=2)}

    Task:
    Score each candidate API based on how well it matches the user request.

    Scoring Criteria (VERY IMPORTANT):

    1. Intent Match (highest priority)
    - Does the API perform the exact action requested?
    (e.g. update vs get vs delete)

    2. Entity Match
    - Does it target the correct resource?
    (e.g. user, password, post)

    3. Endpoint Semantics
    - path, method, purpose consistency

    4. Keyword Relevance
    - overlap with query terms

    Scoring Rules:
    - 1.0 → perfect match
    - 0.7–0.9 → strong match
    - 0.4–0.6 → partial / ambiguous
    - 0.0–0.3 → irrelevant

    Instructions:
    - Score ALL candidates
    - Be strict (avoid giving high scores loosely)
    - Prefer precision over recall
    - Do NOT explain anything

    Return ONLY valid JSON:
    [
      {{"id": 1, "score": 0.9}}
    ]
    Output nothing but JSON.
    """

    response = llm_call(prompt)

    ranked = json.loads(response)

    ranked = sorted(ranked, key=lambda x: x["score"], reverse=True)

    state.ranked = ranked
    state.phase = "decision"

    return state