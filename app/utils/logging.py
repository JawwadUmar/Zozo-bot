from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_logs_dir() -> Path:
    base = Path(__file__).resolve().parents[2]
    out = base / "data" / "logs"
    out.mkdir(parents=True, exist_ok=True)
    return out


class ZozoFormatter(logging.Formatter):
    """Clean formatter with timestamp and level."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        prefix = "🤖"
        if record.levelno >= logging.ERROR:
            prefix = "❌"
        elif record.levelno >= logging.WARNING:
            prefix = "⚠️"
        elif record.levelno == logging.INFO:
            prefix = "ℹ️"

        return f"{prefix} [{timestamp}] {record.getMessage()}"


def setup_logging(level: str = "INFO", log_to_file: bool = True) -> logging.Logger:
    """Configure structured logger for the Zozo bot."""
    logger = logging.getLogger("zozo")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ZozoFormatter())
        logger.addHandler(console_handler)

        if log_to_file:
            today = datetime.now().strftime("%Y%m%d")
            filepath = get_logs_dir() / f"zozo_{today}.log"
            file_handler = logging.FileHandler(filepath, encoding="utf-8")
            file_handler.setFormatter(
                logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
            )
            logger.addHandler(file_handler)

    return logger


logger = setup_logging()


def log_action(action_type: str, target: str, result: str, confidence: Optional[float] = None) -> None:
    conf_str = f" (confidence: {confidence:.2f})" if confidence is not None else ""
    logger.info(f"Action: {action_type} on '{target}' -> {result}{conf_str}")


def log_page_state(url: str, page_type: str, stage: str) -> None:
    logger.info(f"Page State: type='{page_type}', stage='{stage}', url='{url}'")


def log_error(error: Any, context: str = "") -> None:
    ctx_str = f" in {context}" if context else ""
    logger.error(f"Error{ctx_str}: {error}")
