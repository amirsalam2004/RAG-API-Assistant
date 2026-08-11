from app.base_prompts import Role_definition
from app.services.llm_service import generate_api_info
class AgentState:
    def __init__(self):
        self.messages = []
        self.user_info = {
            "goal": None,
            "constraints": [],
        }

        self.openapi_url = ""
        self.swagger_url = ""

        self.SYSTEM_CONTEXT=""

        self.phase = "collecting_info"

        self.search_query = None
        self.candidates = []
        self.ranked = []
    def initialize_SYSTEM_CONTEXT(self, user_description):
        api_description = generate_api_info(user_description)
        self.SYSTEM_CONTEXT = f"""{api_description}\n\n{Role_definition}"""
    def initialize_openapi_url(self, url):
        self.openapi_url = url
    def initialize_swagger_url(self, url):
        self.swagger_url = url