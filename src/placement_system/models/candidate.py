"""Candidate domain model."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    full_name: str
    email: str
    qualification: str
    percentage: float
    passing_year: int
    technology: str
    phone: str | None = None
    skills: tuple[str, ...] = ()
    active_backlogs: int = 0
