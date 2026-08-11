from app.agents.intent_agent import intent_agent
from app.agents.query_builder import build_query
from app.agents.retrieval_agent import retrieval_agent
from app.agents.reranker_agent import reranker_agent
from app.agents.decision_agent import decide
from app.services.llm_service import detect_language, translate_text

def run(state, vectordb, user_input):
    """
    Generator pipeline.
    Yields: {"type": "status", "message": str}
    Yields: {"type": "result",  "data":    str | list}
    """

    
    # --- Detect language & translate input ---
    state.user_language = detect_language(user_input)
    english_input = translate_text(user_input, "english")

    state.messages.append({"role": "User", "content": english_input})

    # 1. Intent
    yield {"type": "status", "message": "🔍 Understanding your request..."}
    intent = intent_agent(state)

    if not intent["complete"]:
        question = intent["question"]
        translated_question = translate_text(question, state.user_language)
        state.messages.append({"role": "Assistant", "content": question})
    
        yield {"type": "result", "data": translated_question}
        return

    # 2. Query
    yield {"type": "status", "message": "🛠️ Building search query..."}
    state = build_query(state)

    # 3. Retrieval
    yield {"type": "status", "message": "🔎 Searching APIs..."}
    state = retrieval_agent(state, vectordb)

    # 4. Rerank
    yield {"type": "status", "message": "📊 Ranking results..."}
    state = reranker_agent(state)

    # 5. Decision
    yield {"type": "status", "message": "✅ Preparing final answer..."}
    decision = decide(state)

    if decision["status"] == "success":
        yield {"type": "result", "data": decision["result"]}

    elif decision["status"] == "clarify":
        msg = "No suitable results were found. Please try rephrasing your request or providing more details."
        translated_msg=msg
        if state.user_language=="english":
            translated_msg = translate_text(msg, state.user_language)
        state.messages.append({"role": "Assistant", "content": msg})
        yield {"type": "result", "data": translated_msg}

    else:
        msg = "An error occurred while processing your request. Please try again later."
        translated_msg=msg
        if state.user_language=="english":
            translated_msg = translate_text(msg, state.user_language)
        state.messages.append({"role": "Assistant", "content": msg})
        yield {"type": "result", "data": translated_msg}