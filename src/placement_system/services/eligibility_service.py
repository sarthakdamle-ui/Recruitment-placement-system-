"""Eligibility rules that determine whether a candidate can apply to an open job."""

from placement_system.models.candidate_profile import CandidateProfile
from placement_system.models.eligibility_result import EligibilityResult
from placement_system.models.job_opening import JobOpening


def _normalized(value: str) -> str:
    return " ".join(value.casefold().split())


class EligibilityService:
    def evaluate(self, candidate: CandidateProfile, job: JobOpening) -> EligibilityResult:
        reasons: list[str] = []
        if candidate.status != "ACTIVE":
            reasons.append("Candidate account is not active.")
        if job.status != "OPEN":
            reasons.append("Job is not open for applications.")
        if _normalized(candidate.qualification) != _normalized(job.qualification_required):
            reasons.append(f"Qualification must be {job.qualification_required}.")
        if candidate.percentage < job.minimum_percentage:
            reasons.append(f"Percentage must be at least {job.minimum_percentage:g}%.")
        if job.passing_year_from is not None and candidate.passing_year < job.passing_year_from:
            reasons.append(f"Passing year must be {job.passing_year_from} or later.")
        if job.passing_year_to is not None and candidate.passing_year > job.passing_year_to:
            reasons.append(f"Passing year must be {job.passing_year_to} or earlier.")
        if _normalized(candidate.technology) != _normalized(job.technology):
            reasons.append(f"Primary technology must be {job.technology}.")
        candidate_skills = {_normalized(skill) for skill in candidate.skills if skill.strip()}
        missing_skills = [skill for skill in job.required_skills if _normalized(skill) not in candidate_skills]
        if missing_skills:
            reasons.append("Missing required skills: " + ", ".join(missing_skills) + ".")
        if candidate.active_backlogs > job.maximum_backlogs:
            reasons.append(f"Active backlogs must not exceed {job.maximum_backlogs}.")
        return EligibilityResult(eligible=not reasons, reasons=tuple(reasons))
