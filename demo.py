#!/usr/bin/env python3
"""
Minimal demo to show orchestration of multiple plugins with fallback behavior.
This is intentionally simple — replace mock implementations with real ones as needed.
"""

import os
from typing import Any, Dict


class BasePlugin:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def available(self) -> bool:
        raise NotImplementedError

    def run(self, *args, **kwargs):
        raise NotImplementedError


class GitHubPlugin(BasePlugin):
    def available(self) -> bool:
        return bool(os.getenv("GITHUB_TOKEN"))

    def run(self, action: str, **kwargs):
        if not self.available():
            return {"mode": "mock", "action": action, "result": "mocked github response"}
        # Real implementation would call GitHub REST API here
        return {"mode": "real", "action": action, "result": "call to GitHub API"}


class LangChainBridgePlugin(BasePlugin):
    def available(self) -> bool:
        # Example: check for LANGCHAIN api key or dependency
        return bool(os.getenv("LANGCHAIN_KEY"))

    def run(self, query: str, **kwargs):
        if not self.available():
            return {"mode": "mock", "query": query, "result": "mocked retrieval"}
        return {"mode": "real", "query": query, "result": "real RAG response"}


class GoogleWorkspacePlugin(BasePlugin):
    def available(self) -> bool:
        return bool(os.getenv("GOOGLE_CREDENTIALS_JSON"))

    def run(self, title: str, content: str, **kwargs):
        if not self.available():
            return {"mode": "mock", "title": title, "result": "mocked google doc created"}
        return {"mode": "real", "title": title, "result": "real google doc created"}


def main():
    config = {}
    github = GitHubPlugin(config)
    langchain = LangChainBridgePlugin(config)
    google = GoogleWorkspacePlugin(config)

    print("Starting Semantic Kernel Multi-Tool Demo...\n")

    gh_res = github.run("list_issues")
    print("GitHub plugin:", gh_res)

    lc_res = langchain.run("Explain Semantic Kernel pattern")
    print("LangChainBridge plugin:", lc_res)

    gdoc_res = google.run("Demo Doc", "This doc was created by the demo.")
    print("Google Workspace plugin:", gdoc_res)

    print("\nDemo finished. Replace mocks with real implementations and add tests/workflows as needed.")


if __name__ == "__main__":
    main()
