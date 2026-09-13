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
        f'margin-bottom:16px;background:{bg};box-shadow:0 1px 5px rgba(0,0,0,0.08);'
        f'color:#212121;">' 

        f'{best_tag}'

        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
        f'{_method_badge(api["method"])}'
        f'<span style="font-family:monospace;font-size:15px;font-weight:600;color:#212121;">'
        f'{api["path"]}</span>'
        f'</div>'

        # PURPOSE BOX
        f'<div style="border:1px solid #64b5f6;border-radius:8px;padding:10px 12px;'
        f'margin-bottom:10px;background:#e3f2fd;">'
        f'<div style="font-size:12px;font-weight:700;color:#1565c0;margin-bottom:4px;">'
        f'PURPOSE</div>'
        f'<div style="color:#0d47a1;font-size:14px;">'
        f'{api.get("purpose", "")}</div>'
        f'</div>'

        # DESCRIPTION BOX (ONLY if exists)
        f'{(
            f"<div style=\"border:1px solid #81c784;border-radius:8px;padding:10px 12px;"
            f"margin-bottom:10px;background:#e8f5e9;\">"
            f"<div style=\"font-size:12px;font-weight:700;color:#2e7d32;margin-bottom:4px;\">"
            f"DESCRIPTION</div>"
            f"<div style=\"color:#1b5e20;font-size:13px;line-height:1.6;\">"
            f"{api.get('description')}</div>"
            f"</div>"
        ) if api.get("description") else ""}'

        f'<div style="margin-bottom:12px;">{_category_badge(api["category"])}</div>'

        f'<div style="font-size:13px;margin-bottom:6px;color:#212121;">'
        f'<strong>Match score:</strong> {score_pct}%</div>'

        f'<div style="background:#e0e0e0;border-radius:6px;height:8px;margin-bottom:12px;">'
        f'<div style="background:#1976d2;width:{score_pct}%;height:8px;border-radius:6px;"></div>'
        f'</div>'

        f'<a href="{api["URL"]}" target="_blank" '
        f'style="display:inline-block;padding:8px 16px;'
        f'background:#263238;color:#ffffff;'
        f'border-radius:6px;font-size:13px;font-weight:500;'
        f'text-decoration:none;">'
        f'View Swagger Docs &#8599;</a>'

        f'</div>'
    )

    # return (
    #     f'<div style="border:{border};border-radius:10px;padding:16px 20px;'
    #     f'margin-bottom:16px;background:{bg};box-shadow:0 1px 5px rgba(0,0,0,0.08);'
    #     f'color:#212121;">' 

    #     f'{best_tag}'

    #     f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
    #     f'{_method_badge(api["method"])}'
    #     f'<span style="font-family:monospace;font-size:15px;font-weight:600;color:#212121;">'
    #     f'{api["path"]}</span>'
    #     f'</div>'

    #     f'<div style="color:#424242;font-size:14px;margin-bottom:10px;">'
    #     f'{api["purpose"]}</div>'

    #     f'<div style="color:#424242;font-size:14px;margin-bottom:10px;">'
    #     f'{api.get("description", "")}</div>'

    #     f'<div style="margin-bottom:12px;">{_category_badge(api["category"])}</div>'

    #     f'<div style="font-size:13px;margin-bottom:6px;color:#212121;">'
    #     f'<strong>Match score:</strong> {score_pct}%</div>'

    #     f'<div style="background:#e0e0e0;border-radius:6px;height:8px;margin-bottom:12px;">'
    #     f'<div style="background:#1976d2;width:{score_pct}%;height:8px;border-radius:6px;"></div>'
    #     f'</div>'

    #     f'<a href="{api["URL"]}" target="_blank" '
    #     f'style="display:inline-block;padding:8px 16px;'
    #     f'background:#263238;color:#ffffff;'
    #     f'border-radius:6px;font-size:13px;font-weight:500;'
    #     f'text-decoration:none;">'
    #     f'View Swagger Docs &#8599;</a>'

    #     f'</div>'
    # )
    

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
st.title("Find the API!")

if "state" not in st.session_state:
    st.session_state.state = AgentState()

if "vectordb" not in st.session_state:
    st.session_state.vectordb = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# # Setup form
# if st.session_state.vectordb is None:
#     st.subheader("Setup")
#     openapi_url = st.text_input("OpenAPI Spec URL", placeholder="https://example.com/openapi.json")
#     swagger_url = st.text_input("Swagger Base URL", placeholder="https://example.com/docs/#/")
#     api_description = st.text_area("Describe the API system", placeholder="e.g. A platform for game and social features...")

#     if st.button("Initialize"):
#         if openapi_url and swagger_url and api_description:
#             with st.spinner("Setting up..."):
#                 st.session_state.state.initialize_openapi_url(openapi_url)
#                 st.session_state.state.initialize_swagger_url(swagger_url)
#                 st.session_state.state.initialize_SYSTEM_CONTEXT(api_description)

#                 vectordb = VectorDB()
#                 vectordb.reset_and_ingest(openapi_url)
#                 st.session_state.vectordb = vectordb

#             st.rerun()
#         else:
#             st.error("Please fill in all fields.")
#     st.stop()

# Setup form
if st.session_state.vectordb is None:

    # -----------------------------
    # Custom styling
    # -----------------------------
    st.markdown("""
    <style>
        /* Main setup title */
        .setup-title {
            text-align: center;
            margin-bottom: 1.8rem;
        }

        .setup-title h1 {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .setup-title p {
            color: #78909c;
            font-size: 0.95rem;
            margin: 0;
        }

        /* Section labels */
        .field-label {
            font-weight: 600;
            font-size: 0.92rem;
            color: #37474f;
            margin-bottom: 0.35rem;
        }

        .field-hint {
            font-size: 0.78rem;
            color: #78909c;
            margin-top: 0.25rem;
            margin-bottom: 0.8rem;
        }

        /* Info box */
        .info-box {
            background: #f1f7ff;
            border-left: 4px solid #1976d2;
            padding: 0.85rem 1rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
        }

        .info-box p {
            margin: 0;
            color: #455a64;
            font-size: 0.88rem;
            line-height: 1.5;
        }

        /* Input fields */
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            border-radius: 8px;
            border: 1px solid #cfd8dc;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }

        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus {
            border-color: #1976d2;
            box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.12);
        }

        /* Initialize button */
        div[data-testid="stButton"] > button {
            width: 100%;
            border-radius: 8px;
            border: none;
            background: #1976d2;
            color: white;
            font-weight: 600;
            padding: 0.65rem 1rem;
            transition: background 0.2s ease, transform 0.2s ease;
        }

        div[data-testid="stButton"] > button:hover {
            background: #1565c0;
            transform: translateY(-1px);
        }

        /* Error message */
        div[data-testid="stAlert"] {
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)


    # -----------------------------
    # Header
    # -----------------------------
    st.markdown("""
        <div class="setup-title">
            <h1>API Assistant Setup</h1>
            <p>
                Connect your OpenAPI specification and Swagger documentation
                to initialize the assistant.
            </p>
        </div>
    """, unsafe_allow_html=True)


    # -----------------------------
    # Setup card
    # -----------------------------
    with st.container(border=True):

        st.markdown("### API Configuration")

        st.markdown("""
            <div class="info-box">
                <p>
                    <strong>Quick Start:</strong>
                    Provide the OpenAPI URL, Swagger documentation URL,
                    and a short description of your API system.
                </p>
            </div>
        """, unsafe_allow_html=True)


        # -------------------------
        # URLs
        # -------------------------
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                '<div class="field-label">OpenAPI Specification URL</div>',
                unsafe_allow_html=True
            )

            openapi_url = st.text_input(
                "OpenAPI Spec URL",
                placeholder="https://example.com/openapi.json",
                label_visibility="collapsed"
            )

            st.markdown(
                '<div class="field-hint">'
                'URL of the OpenAPI specification file.'
                '</div>',
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                '<div class="field-label">Swagger Documentation URL</div>',
                unsafe_allow_html=True
            )

            swagger_url = st.text_input(
                "Swagger Base URL",
                placeholder="https://example.com/docs/#/",
                label_visibility="collapsed"
            )

            st.markdown(
                '<div class="field-hint">'
                'Base URL used to open the API documentation.'
                '</div>',
                unsafe_allow_html=True
            )


        # -------------------------
        # API description
        # -------------------------
        st.markdown(
            '<div class="field-label">API System Description</div>',
            unsafe_allow_html=True
        )

        api_description = st.text_area(
            "Describe the API system",
            placeholder=(
                "Example: A backend platform providing authentication, "
                "user management, social features, and game-related APIs."
            ),
            label_visibility="collapsed",
            height=110
        )

        st.markdown(
            '<div class="field-hint">'
            'Briefly describe what kind of APIs this system provides. '
            'This information will be summarized and used as context by the assistant.'
            '</div>',
            unsafe_allow_html=True
        )


        # -------------------------
        # Initialize
        # -------------------------
        if st.button("Initialize API Assistant", use_container_width=True):

            if openapi_url and swagger_url and api_description:

                with st.spinner("Initializing API Assistant..."):

                    # Store configuration in state
                    st.session_state.state.initialize_openapi_url(
                        openapi_url
                    )

                    st.session_state.state.initialize_swagger_url(
                        swagger_url
                    )

                    # Generate SYSTEM_CONTEXT
                    st.session_state.state.initialize_SYSTEM_CONTEXT(
                        api_description
                    )

                    # Create and populate vector database
                    vectordb = VectorDB()
                    vectordb.reset_and_ingest(openapi_url)

                    st.session_state.vectordb = vectordb

                st.rerun()

            else:
                st.error(
                    "Please provide the OpenAPI URL, Swagger URL, "
                    "and API description."
                )

    st.stop()


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
