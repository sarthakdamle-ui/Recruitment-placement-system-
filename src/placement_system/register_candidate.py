"""Simple command-line entry point for registering a candidate."""

from getpass import getpass

from placement_system.config import load_settings
from placement_system.models.candidate import Candidate
from placement_system.repositories.candidate_repository import CandidateRepository
from placement_system.services.candidate_service import CandidateService
from placement_system.utils.exceptions import DuplicateCandidateError, ValidationError


def main() -> None:
    print("Candidate registration")
    skills_text = input("Skills (comma-separated, optional): ")
    candidate = Candidate(
        full_name=input("Full name: "),
        email=input("Email: "),
        phone=input("Phone (optional): ").strip() or None,
        qualification=input("Qualification: "),
        percentage=float(input("Percentage: ")),
        passing_year=int(input("Passing year: ")),
        technology=input("Primary technology: "),
        skills=tuple(skill.strip() for skill in skills_text.split(",")),
        active_backlogs=int(input("Active backlogs: ")),
    )
    try:
        settings = load_settings()
        candidate_id = CandidateService(CandidateRepository(settings)).register(candidate)
        print(f"Candidate registered successfully. ID: {candidate_id}")
    except (ValidationError, DuplicateCandidateError, ValueError) as exc:
        print(f"Could not register candidate: {exc}")


if __name__ == "__main__":
    main()
