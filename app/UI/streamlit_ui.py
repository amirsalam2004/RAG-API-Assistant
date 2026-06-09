import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.core.state import AgentState
from app.core.controller import run
from app.services.vector_db_service import VectorDB
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Method badge colours ──────────────────────────────────────────────────────
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

def _render_api_cards(results: list):
    for i, api in enumerate(results):
        # st.write(type(api), api)
        is_best   = (i == 0)
        border    = "2px solid #f9a825" if is_best else "1px solid #e0e0e0"
        bg        = "#fffde7"           if is_best else "#ffffff"
        best_tag  = (
            "<div style='font-size:11px;font-weight:700;color:#f9a825;"
            "letter-spacing:1px;margin-bottom:8px;'>⭐ BEST MATCH</div>"
            if is_best else ""
        )

        st.markdown(
            f"""<div style="border:{border};border-radius:10px;padding:16px 20px;
                        margin-bottom:4px;background:{bg};
                        box-shadow:0 1px 5px rgba(0,0,0,0.08);">
                {best_tag}
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                    {_method_badge(api['method'])}
                    <span style="font-family:monospace;font-size:15px;
                                 font-weight:600;color:#212121;">{api['path']}</span>
                </div>
                <div style="color:#555;font-size:14px;margin-bottom:8px;">
                    {api['purpose']}
                </div>
                <div>{_category_badge(api['category'])}</div>
            </div>""",
            unsafe_allow_html=True,
        )

        score_pct = int(api["score"] * 100)
        st.markdown(f"**Match score:** {score_pct}%")
        st.progress(api["score"])
        st.link_button("View Swagger Docs ↗", api["URL"])

        if i < len(results) - 1:
            st.divider()


def _render_response(response):
    """Render a run() response: card UI for lists, plain text otherwise."""
    if isinstance(response, list):
        _render_api_cards(response)
    else:
        st.write(response)

# ── App ───────────────────────────────────────────────────────────────────────
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

    response = run(st.session_state.state, st.session_state.vectordb, prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        _render_response(response)
