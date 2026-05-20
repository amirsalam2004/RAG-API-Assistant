def decide(state):

    if not state.ranked:
        return {"status": "retry"}

    candidates_map = {c["id"]: c for c in state.candidates}

    best = state.ranked[0]

    if best["score"] < 0.6:
        return {
            "status": "clarify",
        }
    

    results =""

    for item in state.ranked:
        cid = item["id"]
        score = item["score"]
        
        if score < 0.7:
            continue

        candidate = candidates_map.get(cid)

        if not candidate:
            continue

        # results.append({
        #     "method": candidate["method"],
        #     "path": candidate["path"],
        #     "purpose": candidate["purpose"],
        #     "category": candidate["category"],
        #     "URL": candidate["URL"],
        #     "score": score
        # })
        results+=f"""
        ###############################################\n     #for debugging only, not for production
        Method: {candidate['method']}\n
        Path: {candidate["path"]}\n
        Purpose: {candidate["purpose"]}\n
        Category: {candidate["category"]}\n      
        URL: {candidate["URL"]}\n
        Score: {score}\n
        """

    return {
        "status": "success",
        "result": results
    }    