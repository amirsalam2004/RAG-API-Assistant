def decide(state):

    if not state.ranked:
        return {"status": "retry"}

    candidates_map = {c["id"]: c for c in state.candidates}

    best = state.ranked[0]

    if best["score"] < 0.6:
        return {
            "status": "clarify",
        }
