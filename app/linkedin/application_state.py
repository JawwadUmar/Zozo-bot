from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ApplicationTracker:
    """Tracks applied jobs across bot sessions to avoid duplicate applications."""

    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            base = Path(__file__).resolve().parents[2]
            self.storage_path = base / "data" / "session_tracker.json"

        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.applied_jobs: Dict[str, Dict[str, Any]] = self._load()
        self.session_attempts = 0
        self.session_successes = 0
        self.session_failures = 0
        self.session_skipped = 0

    def _load(self) -> Dict[str, Dict[str, Any]]:
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save(self) -> None:
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.applied_jobs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ ApplicationTracker save error: {e}")

    def is_applied(self, job_url: str) -> bool:
        """Check if job has already been applied to."""
        clean_url = job_url.split("?")[0].rstrip("/")
        return clean_url in self.applied_jobs

    def mark_applied(
        self,
        job_url: str,
        job_title: str,
        company: str,
        status: str = "applied",
        notes: str = "",
    ) -> None:
        """Record an applied job."""
        clean_url = job_url.split("?")[0].rstrip("/")
        self.applied_jobs[clean_url] = {
            "title": job_title,
            "company": company,
            "url": job_url,
            "applied_at": datetime.now().isoformat(),
            "status": status,
            "notes": notes,
        }
        self._save()
        self.session_attempts += 1
        if status == "applied":
            self.session_successes += 1
        else:
            self.session_failures += 1

    def record_skip(self) -> None:
        self.session_skipped += 1

    def get_session_stats(self) -> Dict[str, int]:
        return {
            "attempts": self.session_attempts,
            "successes": self.session_successes,
            "failures": self.session_failures,
            "skipped": self.session_skipped,
            "total_lifetime_recorded": len(self.applied_jobs),
        }
