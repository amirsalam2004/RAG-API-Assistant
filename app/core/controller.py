from app.agents.intent_agent import intent_agent
from app.agents.query_builder import build_query
from app.agents.retrieval_agent import retrieval_agent
from app.agents.reranker_agent import reranker_agent
from app.agents.decision_agent import decide

MAX_RETRY = 3

def run(state, vectordb, user_input):
    state.messages.append({"role": "User", "content": user_input})

    while state.retry_count < MAX_RETRY:

        # 1. Intent
        intent = intent_agent(state)

        if not intent["complete"]:
            state.messages.append({"role": "Assistant", "content": intent["question"]})
            return intent["question"]
        

        # 2. Query
        state = build_query(state)

        # 3. Retrieval
        state = retrieval_agent(state, vectordb)

        # 4. Rerank
        state = reranker_agent(state)

        # 5. Decision
        decision = decide(state)

        if decision["status"] == "success":
            return decision["result"]

        elif decision["status"] == "clarify":
            return decision["question"]

        state.retry_count += 1

    return "No suitable results were found after multiple attempts. Please try rephrasing your request or providing more details."