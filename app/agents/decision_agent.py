#Converting API information to a string
def format_api_information(results):
    formated = ""
    for api in results:
        formated+=f"""
        ###############################################\n  
        Method: {api['method']}\n
        Path: {api["path"]}\n
        Purpose: {api["purpose"]}\n
        Category: {api["category"]}\n      
        URL: {api["URL"]}\n
        Score: {api["score"]}\n
        ###############################################\n  
        """
    return formated


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

        results.append({
            "method": candidate["method"],
            "path": candidate["path"],
            "purpose": candidate["purpose"],
            "category": candidate["category"],
            "URL": candidate["URL"],
            "score": score
        })
        api_informagtion= format_api_information(results)

        # store APIs information in user-assistant conversation in state
        state.messages.append({"role": "Assistant", "content": "APIs to suit your needs:\n"+api_informagtion})

    return {
        "status": "success",
        "result": api_informagtion        #It should be a list, for debuging return string first
    }    