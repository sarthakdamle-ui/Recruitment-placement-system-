"""Candidate-facing job eligibility and application flow."""

from placement_system.config import load_settings
from placement_system.repositories.application_repository import ApplicationRepository, DuplicateApplicationError
from placement_system.repositories.candidate_query_repository import CandidateQueryRepository
from placement_system.repositories.job_query_repository import JobQueryRepository
from placement_system.services.eligibility_service import EligibilityService
from placement_system.utils.exceptions import PlacementSystemError


def main() -> None:
    settings = load_settings()
    candidate_repository = CandidateQueryRepository(settings)
    job_repository = JobQueryRepository(settings)
    application_repository = ApplicationRepository(settings)
    engine = EligibilityService()

    try:
        candidate_id = int(input("Candidate ID: "))
        candidate = candidate_repository.get_profile(candidate_id)
        jobs = job_repository.list_open()
        if not jobs:
            print("There are no open jobs right now.")
            return

        eligible_jobs = []
        print(f"\nEligibility for candidate ID {candidate.candidate_id}")
        for job in jobs:
            result = engine.evaluate(candidate, job)
            label = "ELIGIBLE" if result.eligible else "NOT ELIGIBLE"
            print(f"\n[{label}] Job {job.job_id}: {job.title} at {job.company_name}")
            if result.reasons:
                for reason in result.reasons:
                    print(f"  - {reason}")
            else:
                eligible_jobs.append(job)

        if not eligible_jobs:
            print("No matching openings are available for this candidate.")
            return

        selected_id = int(input("\nEnter a job ID to apply, or 0 to cancel: "))
        if selected_id == 0:
            print("No application submitted.")
            return
        selected_job = next((job for job in eligible_jobs if job.job_id == selected_id), None)
        if selected_job is None:
            print("That job is not in the eligible list. No application was submitted.")
            return

        notes = f"Eligibility checked for job {selected_job.job_id}; all configured criteria passed."
        application_id = application_repository.create(candidate_id, selected_id, notes)
        print(f"Application submitted successfully. Application ID: {application_id}")
    except (ValueError, PlacementSystemError, DuplicateApplicationError) as exc:
        print(f"Could not submit application: {exc}")


if __name__ == "__main__":
    main()
