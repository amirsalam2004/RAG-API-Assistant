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
