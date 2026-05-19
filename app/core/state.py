class AgentState:
    def __init__(self):
        self.messages = []

        self.user_info = {
            "goal": None,
            "constraints": [],
        }

        self.phase = "collecting_info"

        self.search_query = None
        self.candidates = []
        self.ranked = []

        self.retry_count = 0