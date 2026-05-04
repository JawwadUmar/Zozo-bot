from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from typing import Any
from app.utils.file_loader import get_resume, get_system_prompt, get_human_prompt
from app.ai.llm import llm

resume = get_resume()
system_prompt = get_system_prompt()
human_prompt = get_human_prompt()



async def getAiAnswer(available_options:list[str]|None, question: str, isNumeric: bool=False)->str|Any:
    prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", human_prompt)
            ])
            
    prompt = prompt_template.format_messages(
        resume=resume if should_include_resume(question) else "N/A",
        options=available_options,
        question=question,
        isNumeric=isNumeric
    )
    raw_response = await llm.ainvoke(prompt)
    answer = raw_response.content.strip().replace("**", "")
    return answer


def should_include_resume(question):
    keywords = ["skill", "project", "technology", "linkedin", "github", "portfolio", "email", "phone", "contact"]
    return any(k in question.lower() for k in keywords)