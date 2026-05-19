import json
import requests

# 1. Extract Swagger from JS
def extract_swagger_from_js(js_text):
    start_key = '"swaggerDoc"'
    start = js_text.find(start_key)

    if start == -1:
        raise ValueError("swaggerDoc not found")

    start = js_text.find('{', start)

    brace_count = 0
    end = None

    for i in range(start, len(js_text)):
        if js_text[i] == '{':
            brace_count += 1
        elif js_text[i] == '}':
            brace_count -= 1

        if brace_count == 0:
            end = i
            break

    swagger_str = js_text[start:end+1]

    return json.loads(swagger_str)


# 2. Extract endpoints
def extract_endpoints(swagger):
    endpoints = []

    for path, methods in swagger.get("paths", {}).items():

        if not isinstance(methods, dict):
            continue

        for method, data in methods.items():

            if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                continue

            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        endpoints.append({
                            "path": path,
                            "method": method,
                            "operationId": item.get("operationId", ""),
                            "summary": item.get("summary", ""),
                            "tags": item.get("tags", []),
                            "parameters": item.get("parameters", []),
                            "requestBody": item.get("requestBody", {}),
                            "responses": item.get("responses", {})
                        })
                continue

            if isinstance(data, dict):
                endpoints.append({
                    "path": path,
                    "method": method,
                    "operationId": data.get("operationId", ""),
                    "summary": data.get("summary", ""),
                    "tags": data.get("tags", []),
                    "parameters": data.get("parameters", []),
                    "requestBody": data.get("requestBody", {}),
                    "responses": data.get("responses", {})
                })

    return endpoints