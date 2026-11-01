"""Recruiter console for application review and interview workflow."""

from datetime import datetime

from placement_system.config import load_settings
from placement_system.repositories.interview_workflow_repository import (
    ApplicationNotFoundError,
    InterviewWorkflowRepository,
    InvalidApplicationStateError,
)
from placement_system.utils.exceptions import PlacementSystemError


def show_applications(repository: InterviewWorkflowRepository) -> None:
    rows = repository.list_applications()
    if not rows:
        print("No applications have been submitted yet.")
        return
    print("\nApplication | Candidate | Email | Job | Company | Status | Applied")
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]}")


def show_interviews(repository: InterviewWorkflowRepository) -> None:
    rows = repository.list_interviews()
    if not rows:
        print("No interviews are scheduled yet.")
        return
    print("\nInterview | Application | Round | Scheduled | Mode | Interviewer | Result | Feedback")
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5] or ''} | {row[6]} | {row[7] or ''}")


def main() -> None:
    repository = InterviewWorkflowRepository(load_settings())
    while True:
        print("\nApplication and Interview Management")
        print("1. List applications")
        print("2. Shortlist application")
        print("3. Reject application")
        print("4. Schedule interview for shortlisted application")
        print("5. List interviews")
        print("6. Record interview feedback")
        print("0. Exit")
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                show_applications(repository)
            elif choice in ("2", "3"):
                application_id = int(input("Application ID: "))
                if choice == "2":
                    repository.update_application_status(application_id, "SHORTLISTED", ("APPLIED",))
                    print("Application shortlisted.")
                else:
                    repository.update_application_status(application_id, "REJECTED", ("APPLIED", "SHORTLISTED"))
                    print("Application rejected.")
            elif choice == "4":
                application_id = int(input("Shortlisted application ID: "))
                scheduled_at = datetime.strptime(input("Date and time (YYYY-MM-DD HH:MM): ").strip(), "%Y-%m-%d %H:%M")
                mode = input("Mode (ONLINE, ONSITE, PHONE): ").strip().upper()
                if mode not in {"ONLINE", "ONSITE", "PHONE"}:
                    raise ValueError("Mode must be ONLINE, ONSITE, or PHONE.")
                interviewer = input("Interviewer (optional): ").strip() or None
                interview_id = repository.schedule_interview(application_id, scheduled_at, mode, interviewer)
                print(f"Interview scheduled. Interview ID: {interview_id}")
            elif choice == "5":
                show_interviews(repository)
            elif choice == "6":
                show_interviews(repository)
                interview_id = int(input("Interview ID: "))
                feedback = input("Feedback: ").strip()
                if not feedback:
                    raise ValueError("Feedback cannot be blank.")
                result = input("Result (PASS or FAIL): ").strip().upper()
                if result not in {"PASS", "FAIL"}:
                    raise ValueError("Result must be PASS or FAIL.")
                repository.record_feedback(interview_id, feedback, result)
                print("Feedback saved." + (" Application marked REJECTED." if result == "FAIL" else ""))
            elif choice == "0":
                print("Goodbye.")
                return
            else:
                print("Choose an option from 0 to 6.")
        except (ValueError, PlacementSystemError, ApplicationNotFoundError, InvalidApplicationStateError) as exc:
            print(f"Could not complete that action: {exc}")
        except Exception as exc:
            print(f"Database or application error: {exc}")


if __name__ == "__main__":
    main()
