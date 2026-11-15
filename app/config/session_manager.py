class BrowserSessionManager:

    def __init__(self):
        self.sessions = {}

    def register(self, session_id, browser, context, page):
        self.sessions[session_id] = {
            "browser": browser,
            "context": context,
            "page": page
        }

    def get_page(self, session_id):
        session = self.sessions.get(session_id)

        if not session:
            raise RuntimeError(
                f"Browser session {session_id} not found"
            )

        return session["page"]

    def get_context(self, session_id):
        return self.sessions[session_id]["context"]

    async def close(self, session_id):
        session = self.sessions.pop(session_id, None)

        if session:
            await session["context"].close()

browser_manager = BrowserSessionManager()