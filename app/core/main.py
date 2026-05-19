from core.state import AgentState
from core.controller import run
from services.vector_db_service import VectorDB
import os
from dotenv import load_dotenv

load_dotenv()

def main():

    vectordb = VectorDB()

    openapi_url = os.getenv("OPENAPI_SPEC_URL")
    vectordb.ingest_from_url(openapi_url)

    state = AgentState()

    while True:
        user_input = input("User: ")

        response = run(state, vectordb, user_input)

        print("Assistant:\n", response)

if __name__ == "__main__":
    main()