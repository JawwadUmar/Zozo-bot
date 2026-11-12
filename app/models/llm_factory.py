from __future__ import annotations

import os
from typing import Any, Optional, Type, TypeVar
from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel

T = TypeVar("T", bound=BaseModel)


def get_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    api_key: Optional[str] = None,
) -> BaseChatModel:
    """Configurable LLM factory supporting Groq and OpenAI providers."""
    # Determine provider
    chosen_provider = provider or os.getenv("LLM_PROVIDER")
    if not chosen_provider:
        if os.getenv("GROQ_API_KEY"):
            chosen_provider = "groq"
        elif os.getenv("OPENAI_API_KEY"):
            chosen_provider = "openai"
        else:
            chosen_provider = "groq"

    chosen_provider = chosen_provider.lower().strip()

    # Temperature
    if temperature is None:
        temp_str = os.getenv("LLM_TEMPERATURE", "0.2")
        try:
            temperature = float(temp_str)
        except ValueError:
            temperature = 0.2

    if chosen_provider == "groq":
        from langchain_groq import ChatGroq

        chosen_model = model or os.getenv("LLM_MODEL") or "openai/gpt-oss-120b"
        key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY")
        return ChatGroq(model=chosen_model, temperature=temperature, groq_api_key=key)

    elif chosen_provider == "openai":
        from langchain_openai import ChatOpenAI

        chosen_model = model or os.getenv("LLM_MODEL") or "gpt-4o"
        key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("LLM_BASE_URL")
        return ChatOpenAI(
            model=chosen_model,
            temperature=temperature,
            api_key=key,
            base_url=base_url if base_url else None,
        )

    else:
        # Fallback to OpenAI-compatible
        from langchain_openai import ChatOpenAI

        chosen_model = model or os.getenv("LLM_MODEL") or "gpt-4o"
        key = api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL")
        return ChatOpenAI(
            model=chosen_model,
            temperature=temperature,
            api_key=key,
            base_url=base_url if base_url else None,
        )


def get_decision_llm() -> BaseChatModel:
    """Return LLM for making complex action decisions and workflow judgments."""
    model = os.getenv("DECISION_LLM_MODEL")
    return get_llm(model=model)


def get_observation_llm() -> BaseChatModel:
    """Return LLM for interpreting and summarizing page observations."""
    model = os.getenv("OBSERVATION_LLM_MODEL")
    return get_llm(model=model, temperature=0.1)
