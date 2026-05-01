from langchain_groq import ChatGroq
from langchain_core.globals import set_llm_cache


def init_llm():
    try:    
        local_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.3)
        return local_llm
    except Exception as e:
        print(f"❌ Error in init_llm(): {str(e)}")
        return None