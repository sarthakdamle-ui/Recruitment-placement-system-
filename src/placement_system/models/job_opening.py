"""A job opening loaded for eligibility evaluation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class JobOpening:
    job_id: int
    company_name: str
    title: str
    qualification_required: str
    minimum_percentage: float
    passing_year_from: int | None
    passing_year_to: int | None
    technology: str
    required_skills: tuple[str, ...]
    maximum_backlogs: int
    status: str
