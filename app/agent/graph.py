from langgraph.graph import END, START, StateGraph

from app.agent.node.handle_login_node import handle_login
from app.agent.node.initialize_browser import initialize_browser
from app.agent.state import ApplicationState


builder = StateGraph(ApplicationState)
builder.add_node("initialize_browser", initialize_browser)
builder.add_node("handle_login", handle_login)
builder.add_edge(START, "initialize_browser")
builder.add_edge("initialize_browser", "handle_login")
builder.add_edge("handle_login", END)

graph = builder.compile()


if __name__ == "__main__":
    import asyncio

    async def main():
        # Provide initial values required by ApplicationState
        initial_state: ApplicationState = {
            "session_id": "test_session_1",
            "is_logged_in": False,
            "error": None,
        }

        print("Starting graph...")
        # Must use `ainvoke` since `handle_login` (and likely `initialize_browser`) are async
        result = await graph.ainvoke(initial_state)
        print("Final State:", result)

    asyncio.run(main())