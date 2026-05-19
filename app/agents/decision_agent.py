def decide(state):

    if not state.ranked:
        return {"status": "retry"}

    candidates_map = {c["id"]: c for c in state.candidates}
