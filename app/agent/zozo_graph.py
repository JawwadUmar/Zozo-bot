
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent

from app.agent.llm import llm


ALLOWED_TOOLS = {
    "browser_navigate",
    "browser_snapshot",
    "browser_find",
    "browser_click",
    "browser_type",
    "browser_fill_form",
    "browser_scroll",
    "browser_file_upload",
    "browser_press_key",
    "browser_wait_for",
    "browser_select_option",
    "browser_tabs",
}


def filter_playwright_tools(all_tools):
    selected_tools = []

    for tool in all_tools:
        tool_name = tool.name.rsplit("__", 1)[-1]

        if tool_name in ALLOWED_TOOLS:
            selected_tools.append(tool)

    print("\nSelected tools:")
    for tool in selected_tools:
        print(f" - {tool.name}")

    if not selected_tools:
        raise RuntimeError("No allowed Playwright tools found.")

    return selected_tools


async def main():

    if llm is None:
        raise ValueError("LLM failed to initialize.")

    client = MultiServerMCPClient({
        "playwright": {
            "command": "npx",
            "args": ["-y", "@playwright/mcp@latest"],
            "transport": "stdio",
        }
    })

    # IMPORTANT:
    # Keep the MCP session alive throughout the entire agent execution.
    async with client.session("playwright") as session:

        # Load tools using the existing persistent session.
        all_tools = await load_mcp_tools(session)

        with open("toolList.txt", "w") as file:
            for item in all_tools:
                file.write(f"{item}\n")

        # Filter tools.
        tools = filter_playwright_tools(all_tools)

        # Create agent while session is alive.
        agent = create_agent(llm, tools)

        prompt = """
        Go to https://example.com.

        1. Inspect the page using browser_snapshot.
        2. Identify the available links.
        3. Click the link that provides more information.
        4. Inspect the resulting page.

        Use only the available browser tools.
        """

        # response = await agent.ainvoke({
        #     "messages": [
        #         {"role": "user", "content": prompt}
        #     ]
        # })

        # print("\nAgent response:")
        # for message in response["messages"]:
        #     print(message)

    # MCP session closes here, after the agent finishes.


if __name__ == "__main__":
    asyncio.run(main())
