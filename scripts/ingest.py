import json
import requests

# Extract Swagger from JS
# If the APIs information was in a js file instead of the openapi.json file, this function could be used.
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


# Extract endpoints
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
                            "description": item.get("description", ""),
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
                    "description": data.get("description", ""),
                    "tags": data.get("tags", []),
                    "parameters": data.get("parameters", []),
                    "requestBody": data.get("requestBody", {}),
                    "responses": data.get("responses", {})
                })

    return endpoints

# Resolve schema reference
def resolve_ref(ref, schemas):
    name = ref.split("/")[-1]
    return schemas.get(name, {})


# Convert schema → text
def schema_to_text(schema, schemas, depth=0):
    if not schema or depth > 2:
        return ""

    props = schema.get("properties", {})
    lines = []

    for name, value in props.items():

        typ = value.get("type", "")
        desc = value.get("description", "")
        nullable = value.get("nullable", False)

        line = f"- {name} ({typ})"

        if nullable:
            line += " [nullable]"

        if desc:
            line += f": {desc}"

        # nested object
        if "$ref" in value:
            nested = resolve_ref(value["$ref"], schemas)
            line += "\n  " + schema_to_text(nested, schemas, depth + 1)

        # array items
        if typ == "array":
            items = value.get("items", {})
            if "$ref" in items:
                nested = resolve_ref(items["$ref"], schemas)
                line += "\n  items:\n" + schema_to_text(nested, schemas, depth + 1)

        lines.append(line)

    return "\n".join(lines)

# Build semantic document
def build_document(api, schemas):

    parts = []

    # 1. Header
    parts.append(
        f"API: {api['method'].upper()} {api['path']}\n"
        f"Purpose: {api.get('summary', '')}\n"
        f"Description: {api.get('description', '')}\n"
        f"Category: {', '.join(api.get('tags', []))}\n"
        f"OperationId: {api.get('operationId', '')}"
    )

    # 2. Path semantics
    parts.append("Path context: " + api["path"].replace("/", " "))

    # 3. Query / path parameters
    if api.get("parameters"):
        parts.append("Parameters:")

        for p in api["parameters"]:
            parts.append(f"- {p['name']}: {p.get('description', '')}")

    # 4. Request body schema
    request_body = api.get("requestBody", {})
    content = request_body.get("content", {})

    if "application/json" in content:
        schema = content["application/json"].get("schema", {})

        if "$ref" in schema:
            ref_schema = resolve_ref(schema["$ref"], schemas)

            parts.append("Request body:")
            parts.append(schema_to_text(ref_schema, schemas))

    # 5. Responses
    if api.get("responses"):
        parts.append("Responses:")

        for code, res in api["responses"].items():
            parts.append(f"- {code}: {res.get('description', '')}")

 # 6. Keyword boosting (with operationId)
    # keywords = [
    #     api.get("summary", ""),
    #     api["path"],
    #     " ".join(api.get("tags", []))
    # ]
    
    # if api.get('operationId'):
    #     keywords.append(api['operationId'])
    
    # parts.append("Keywords: " + " ".join(keywords))
    parts.append(
        "Keywords: "
        + api.get("summary", "")
        + " "
        + api["path"]
        + " "
        + " ".join(api.get("tags", []))
    )
    
    return "\n".join(parts)


# Full pipeline
def build_vector_documents(url):

    response = requests.get(url)

    swagger = response.json()


    schemas = swagger.get("components", {}).get("schemas", {})
    # print(type(swagger)) #debug
    # print(swagger.keys()) #debug
    endpoints = extract_endpoints(swagger)

    documents = []

    for api in endpoints:
        doc = build_document(api, schemas)

        documents.append({
            "text": doc,
            "metadata": {
                "path": api["path"],
                "method": api["method"],
                "summary": api.get("summary", ""),
                "operationId": api.get("operationId", "")
            }
        })

    return documents
