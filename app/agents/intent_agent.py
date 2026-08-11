import json

from app.services.llm_service import llm_call, format_messages


def intent_agent(state):
    prompt = f"""
    Task:
    Determine whether the user's request is clear and complete enough to search for a specific API endpoint.

    A request is considered COMPLETE if:
    - The intent is clear (what the user wants to do)
    - The target entity is clear (e.g. user, post, password, etc.)
    - The action is clear (e.g. create, update, delete, fetch)

    A request is NOT COMPLETE if:
    - It is vague (e.g. "I have a problem")
    - Missing key details (e.g. "update"  without specifying what to update)
    - Ambiguous (e.g. "I want to update my profile" - what exactly do you want to update?)

    Conversation:
    {format_messages(state.messages)}

    Instructions:
    - If the request is complete → set "complete": true
    - If not → set "complete": false and ask a helpful clarification question
    - Ask only ONE short and specific question
    - Do NOT answer the user request
    - Do NOT suggest APIs

    Return ONLY a valid JSON:
    {{
    "complete": true/false,
    "question": "..."
    }}
    Output nothing but JSON

"""
    response = llm_call(state, prompt)

    try:
        intent = json.loads(response.strip())
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")

    return intent