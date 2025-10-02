# Minimal GitHub stub — replace with PyGithub/httpx when ready.
class GitHubClient:
    def __init__(self, token: str):
        self.token = token

    async def pull_request_age_summary(self, repo: str) -> dict:
        """Return counts of PRs by age buckets; replace stub."""
        return {"<24h": 2, "1-3d": 4, ">3d": 3}
