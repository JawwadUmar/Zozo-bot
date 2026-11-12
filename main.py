import asyncio
from app.linkedin.easy_apply_workflow import run_agentic_bot


async def main():
    await run_agentic_bot()


if __name__ == "__main__":
    asyncio.run(main())
