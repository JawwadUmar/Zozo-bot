from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


def get_screenshots_dir() -> Path:
    base = Path(__file__).resolve().parents[2]
    out = base / "data" / "screenshots"
    out.mkdir(parents=True, exist_ok=True)
    return out


async def capture_screenshot(
    page: Any,
    label: str = "snapshot",
    output_dir: Optional[str] = None,
) -> Optional[str]:
    """Capture a screenshot of the current page state and return its path."""
    try:
        dest_dir = Path(output_dir) if output_dir else get_screenshots_dir()
        dest_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
        safe_label = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in label)
        filename = f"{timestamp}_{safe_label}.png"
        filepath = dest_dir / filename

        await page.screenshot(path=str(filepath), full_page=False)
        return str(filepath)
    except Exception as e:
        print(f"⚠️ Zozo screenshot error: {e}")
        return None


async def capture_on_error(page: Any, error_context: str = "") -> Optional[str]:
    """Capture screenshot on failure/error with context in filename."""
    label = f"error_{error_context}" if error_context else "error"
    return await capture_screenshot(page, label=label)
