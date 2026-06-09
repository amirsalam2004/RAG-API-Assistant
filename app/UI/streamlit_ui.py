import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.core.state import AgentState
from app.core.controller import run
from app.services.vector_db_service import VectorDB
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Method badge colours 
METHOD_COLORS = {
    "GET":    "#2e7d32",
    "POST":   "#1565c0",
    "PUT":    "#e65100",
    "DELETE": "#c62828",
    "PATCH":  "#6a1b9a",
}

def _method_badge(method: str) -> str:
    color = METHOD_COLORS.get(method.upper(), "#546e7a")
    return (
        f'<span style="background:{color};color:#fff;padding:3px 10px;'
        f'border-radius:4px;font-size:13px;font-weight:700;">'
        f'{method.upper()}</span>'
    )

def _category_badge(category: str) -> str:
    return (
        f'<span style="background:#e3f2fd;color:#1565c0;padding:2px 9px;'
        f'border-radius:4px;font-size:12px;font-weight:500;">{category}</span>'
    )


def _card_html(api: dict, is_best: bool) -> str:
    border   = "2px solid #f9a825" if is_best else "1px solid #e0e0e0"
    bg       = "#fffde7"           if is_best else "#ffffff"
    best_tag = (
        "<div style='font-size:11px;font-weight:700;color:#f9a825;"
        "letter-spacing:1px;margin-bottom:8px;'>&#11088; BEST MATCH</div>"
        if is_best else ""
    )
    score_pct = int(api["score"] * 100)
    return (
        f'<div style="border:{border};border-radius:10px;padding:16px 20px;'
        f'margin-bottom:16px;background:{bg};box-shadow:0 1px 5px rgba(0,0,0,0.08);">'
        f'{best_tag}'
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
        f'{_method_badge(api["method"])}'
        f'<span style="font-family:monospace;font-size:15px;font-weight:600;">{api["path"]}</span>'
        f'</div>'
        f'<div style="color:#888;font-size:14px;margin-bottom:10px;">{api["purpose"]}</div>'
        f'<div style="margin-bottom:12px;">{_category_badge(api["category"])}</div>'
        f'<div style="font-size:13px;margin-bottom:6px;"><strong>Match score:</strong> {score_pct}%</div>'
        f'<div style="background:#e0e0e0;border-radius:6px;height:8px;margin-bottom:12px;">'
        f'<div style="background:#1976d2;width:{score_pct}%;height:8px;border-radius:6px;"></div></div>'
        f'<a href="{api["URL"]}" target="_blank" '
        f'style="display:inline-block;padding:7px 16px;border:1px solid #ccc;'
        f'border-radius:6px;font-size:13px;text-decoration:none;color:inherit;">'
        f'View Swagger Docs &#8599;</a>'
        f'</div>'
    )



def _render_api_cards(results: list):
    # Single st.markdown call — avoids Streamlit's per-call HTML sanitisation bug
    st.markdown(
        "".join(_card_html(api, i == 0) for i, api in enumerate(results)),
        unsafe_allow_html=True,
    )

def _render_response(response):
    """Render a run() response: card UI for lists, plain text otherwise."""
    if isinstance(response, list):
        _render_api_cards(response)
    else:
        st.write(response)

# App
st.title("Rastar Center API Assistant")

if "vectordb" not in st.session_state:
    vectordb = VectorDB()
    openapi_url = os.getenv("OPENAPI_SPEC_URL")
    vectordb.ingest_from_url(openapi_url)
    st.session_state.vectordb = vectordb

if "state" not in st.session_state:
    st.session_state.state = AgentState()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        _render_response(message["content"])

# Handle new input
if prompt := st.chat_input("Ask about APIs..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        result = None
        with st.status("Processing your request...", expanded=True) as status:
            for event in run(st.session_state.state, st.session_state.vectordb, prompt):
                if event["type"] == "status":
                    status.write(event["message"])
                elif event["type"] == "result":
                    result = event["data"]
                    status.update(label="Done ✓", state="complete", expanded=False)

        if result is not None:
            _render_response(result)

    st.session_state.messages.append({"role": "assistant", "content": result})
