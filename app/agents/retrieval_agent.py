import re
import urllib.parse

def build_swagger_url(category, operation_id, swagger_url):
    categoryURL=urllib.parse.quote(category, safe='')
    return(swagger_url+categoryURL+"/"+operation_id)



def parse_document(doc, meta, idx, swagger_url):

    lines = doc.strip().split("\n")

    method = None
    path = None

    if lines:
        first_line = lines[0].strip()

        parts = first_line.split(" ", 1)

        if len(parts) == 2:
            method, path = parts
        else:
            # fallback from metadata
            method = meta.get("method", "UNKNOWN")
            path = meta.get("path", first_line)

    # purpose 
    purpose = meta.get("purpose", "")
    # description
    description = meta.get("description", "")
    # category 
    category = meta.get("category", "")
    # operation ID 
    operation_id = meta.get("operationId", "")


    # request body 
    body_matches = re.findall(r"- (\w+) \((.*?)\)", doc)
    request_body = [
        {"name": name, "type": typ}
        for name, typ in body_matches
    ]

    # responses 
    response_matches = re.findall(r"- (\d+):", doc)
    responses = [int(r) for r in response_matches]

    # keywords 
    keyword_match = re.search(r"Keywords:\s*(.*)", doc)
    keywords = keyword_match.group(1).strip() if keyword_match else ""

    return {
        "id": idx,
        "method": method,
        "path": path,
        "purpose": purpose,
        "description": description,
        "category": category,
        "URL": build_swagger_url(category, operation_id, swagger_url),
        "request_body": request_body,
        "responses": responses,
        "keywords": keywords,
    }



def retrieval_agent(state, vectordb):

    raw_results = vectordb.search(state.search_query)

    documents = raw_results["documents"][0]
    metadatas = raw_results["metadatas"][0]

    candidates = []

    for i, (doc, meta) in enumerate(zip(documents, metadatas)):
        parsed = parse_document(doc, meta, i, state.swagger_url)
        candidates.append(parsed)

    state.candidates = candidates
    state.phase = "ranking"

    return state
