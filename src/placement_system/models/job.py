"""Job domain model."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    company_id: int
    title: str
    qualification_required: str
    minimum_percentage: float
    technology: str
    maximum_backlogs: int = 0
    passing_year_from: int | None = None
    passing_year_to: int | None = None
    required_skills: tuple[str, ...] = ()
    description: str | None = None
