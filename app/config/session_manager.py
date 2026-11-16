from typing import Any


class BrowserSessionManager:

    def __init__(self):
        self.sessions: dict[str, dict[str, Any]] = {}

    def register(self, session_id: str, playwright: Any, context: Any, page: Any) -> None:
        if session_id in self.sessions:
            raise RuntimeError(f"Browser session {session_id} is already registered")

        self.sessions[session_id] = {
            "playwright": playwright,
            "context": context,
            "page": page
        }

    def _get_session(self, session_id: str) -> dict[str, Any]:
        session = self.sessions.get(session_id)
        if not session:
            raise RuntimeError(f"Browser session {session_id} not found")
        return session

    def get_page(self, session_id: str) -> Any:
        session = self._get_session(session_id)
        return session["page"]

    def get_context(self, session_id: str) -> Any:
        session = self._get_session(session_id)
        return session["context"]

    async def close(self, session_id: str) -> None:
        session = self.sessions.pop(session_id, None)
        if session:
            try:
                await session["context"].close()
            finally:
                await session["playwright"].stop()

browser_manager = BrowserSessionManager()
