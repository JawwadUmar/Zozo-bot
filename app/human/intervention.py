from __future__ import annotations

import asyncio
import sys
from typing import Any, Dict, Optional


def format_intervention_request(
    reason: str,
    context: Optional[Dict[str, Any]] = None,
    current_job: Optional[Dict[str, Any]] = None,
) -> str:
    """Format an informative, clear human intervention message."""
    lines = [
        "",
        "🚨 " + "=" * 65,
        "🚨 ZOZO-BOT HUMAN INTERVENTION REQUIRED",
        "🚨 " + "=" * 65,
        f"Reason: {reason}",
    ]

    if current_job:
        title = current_job.get("title", "Unknown Role")
        company = current_job.get("company", "Unknown Company")
        lines.append(f"Job: {title} at {company}")

    if context:
        for k, v in context.items():
            if v:
                lines.append(f"{k}: {v}")

    lines.extend([
        "",
        "Instructions:",
        "  1. Review the browser window or the request above.",
        "  2. Complete the required manual action in browser if needed (e.g. solve CAPTCHA/2FA),",
        "     or enter your response below.",
        "  3. Type your answer or press Enter to resume automation.",
        "🚨 " + "=" * 65,
        "",
    ])
    return "\n".join(lines)


async def request_human_input(
    reason: str,
    context: Optional[Dict[str, Any]] = None,
    current_job: Optional[Dict[str, Any]] = None,
) -> str:
    """Pause execution, display intervention message, and await user console input."""
    message = format_intervention_request(reason, context, current_job)
    print(message)

    # Use loop.run_in_executor to avoid blocking the asyncio event loop while waiting for input
    loop = asyncio.get_event_loop()
    try:
        user_response = await loop.run_in_executor(
            None, lambda: input("👉 Enter your response (or press Enter when done in browser): ")
        )
        print("✅ Response received. Resuming agent execution...\n")
        return user_response.strip()
    except (EOFError, KeyboardInterrupt):
        print("\n⚠️ Human input cancelled.")
        return "cancelled"
