import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


from app.core.state import AgentState
from app.core.controller import run
from app.services.vector_db_service import VectorDB
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

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

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Ask about APIs..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    response = run(st.session_state.state, st.session_state.vectordb, prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)
