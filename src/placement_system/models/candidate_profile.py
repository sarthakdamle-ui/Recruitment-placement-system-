"""A candidate profile loaded for eligibility evaluation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateProfile:
    candidate_id: int
    qualification: str
    percentage: float
    passing_year: int
    technology: str
    skills: tuple[str, ...]
    active_backlogs: int
    status: str
