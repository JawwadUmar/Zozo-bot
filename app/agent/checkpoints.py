from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver


def get_checkpointer() -> MemorySaver:
    """Return an in-memory checkpointer for saving and resuming agent workflow states."""
    return MemorySaver()
