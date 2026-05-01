from app.bot.bot_runner import run_bot
from app.ai.llm import init_llm
import asyncio

async def main():
    llm = init_llm()
    if not llm:
        print("❌ AI Initialization Failed. Exiting...")
        return
    await run_bot(llm)

if __name__ == "__main__":
    asyncio.run(main())