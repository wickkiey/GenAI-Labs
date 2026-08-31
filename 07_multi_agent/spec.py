"""Shared structured-output contracts reused by every framework's critique_loop
and planner_executor implementation, mirroring Phase 7's spec.py convention.
"""

from __future__ import annotations

from pydantic import BaseModel


class DraftAnswer(BaseModel):
    expression: str
    answer: str


class Plan(BaseModel):
    tasks: list[str]
