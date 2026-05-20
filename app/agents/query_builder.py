from app.services.llm_service import llm_call, format_messages

def build_query(state):
    prompt = f"""

    Task:
    Convert the user request into a clean and effective search query for a vector database of API documentation.

    The API documents contain fields like:
    - path (e.g. /api/v1/users/update-password)
    - method (GET, POST, etc.)
    - summary (short description of the API)
    - tags (categories like Users, Auth, Social)
    - operationId (action name)

    Instructions:
    - Extract the main ACTION (e.g. create, update, delete, get)
    - Extract the main ENTITY (e.g. user, password, post, friend)
    - Include important keywords related to the request
    - Prefer API-style wording (not conversational language)
    - Keep it short (5–12 words)
    - Do NOT include unnecessary words
    - Do NOT ask questions
    - Do NOT explain anything

    Output:
    Return ONLY the search query as plain text.

    Conversation:
    {format_messages(state.messages)}
"""
    
    query = llm_call(prompt)

    state.search_query = query
    state.phase = "searching"

    return state