from langchain_groq import ChatGroq

def init_llm()->ChatGroq|None:
    try:    
        local_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.3)
        return local_llm
    except Exception as e:
        print(f"❌ Error in init_llm(): {str(e)}")
        return None

llm = init_llm()