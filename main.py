from app.bot.bot_runner import run_bot
from app.ai.llm import init_llm
import asyncio

async def main():
    
    await run_bot()

if __name__ == "__main__":
    asyncio.run(main())