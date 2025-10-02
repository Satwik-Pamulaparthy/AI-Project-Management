# Minimal Jira stub — replace with atlassian-python-api or direct HTTP calls when ready.
from typing import Any

class JiraClient:
    def __init__(self, base_url: str, email: str, api_token: str):
        self.base_url = base_url
        self.email = email
        self.api_token = api_token

    async def get_project_issue_counts(self, project_key: str) -> dict[str, Any]:
        """Return counts by status; replace stub with real API calls."""
        # TODO: Implement real Jira fetch
        return {"todo": 10, "in_progress": 5, "done": 7}
