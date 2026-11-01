"""Console workflow for selection, offers, joining, and placements."""

from datetime import date
from decimal import Decimal, InvalidOperation

from placement_system.config import load_settings
from placement_system.repositories.recruitment_repository import RecruitmentRepository
from placement_system.utils.exceptions import PlacementSystemError


def optional_salary(prompt: str) -> Decimal | None:
    raw = input(prompt).strip()
    if not raw:
        return None
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError("Salary must be a number.") from exc
    if value < 0:
        raise ValueError("Salary cannot be negative.")
    return value


def show_offers(repository: RecruitmentRepository) -> None:
    rows = repository.list_offers()
    if not rows:
        print("No offers recorded yet.")
        return
    print("\nOffer | Application | Candidate | Company | Role | Offered | Expires | Salary | Status")
    for row in rows:
        print(" | ".join(str(value or "") for value in row))


def show_placements(repository: RecruitmentRepository) -> None:
    rows = repository.list_placements()
    if not rows:
        print("No placements recorded yet.")
        return
    print("\nPlacement | Application | Candidate | Company | Role | Joined | Designation | Salary")
    for row in rows:
        print(" | ".join(str(value or "") for value in row))


def main() -> None:
    repository = RecruitmentRepository(load_settings())
    while True:
        print("\nSelection, Offer, and Placement Management")
        print("1. Mark shortlisted application as selected")
        print("2. Create offer for selected application")
        print("3. List offers")
        print("4. Record offer response (accepted or declined)")
        print("5. Record joining for an accepted offer")
        print("6. List placements")
        print("0. Exit")
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                application_id = int(input("Shortlisted application ID: "))
                repository.mark_selected(application_id)
                print("Application marked SELECTED.")
            elif choice == "2":
                application_id = int(input("Selected application ID: "))
                offered_at = date.fromisoformat(input("Offer date (YYYY-MM-DD): ").strip())
                expires_raw = input("Expiry date (YYYY-MM-DD, optional): ").strip()
                expires_at = date.fromisoformat(expires_raw) if expires_raw else None
                if expires_at and expires_at < offered_at:
                    raise ValueError("Expiry date cannot be before the offer date.")
                salary = optional_salary("Salary (optional): ")
                offer_id = repository.create_offer(application_id, offered_at, expires_at, salary)
                print(f"Offer created. Offer ID: {offer_id}")
            elif choice == "3":
                show_offers(repository)
            elif choice == "4":
                show_offers(repository)
                offer_id = int(input("Offer ID: "))
                response = input("Response (ACCEPTED or DECLINED): ").strip().upper()
                if response not in {"ACCEPTED", "DECLINED"}:
                    raise ValueError("Response must be ACCEPTED or DECLINED.")
                repository.respond_to_offer(offer_id, accepted=(response == "ACCEPTED"))
                print(f"Offer marked {response}.")
            elif choice == "5":
                show_offers(repository)
                offer_id = int(input("Accepted offer ID: "))
                joined_on = date.fromisoformat(input("Joining date (YYYY-MM-DD): ").strip())
                designation = input("Designation (optional): ").strip() or None
                salary = optional_salary("Final salary (optional): ")
                placement_id = repository.record_joining(offer_id, joined_on, designation, salary)
                print(f"Joining recorded. Placement ID: {placement_id}")
            elif choice == "6":
                show_placements(repository)
            elif choice == "0":
                print("Goodbye.")
                return
            else:
                print("Choose an option from 0 to 6.")
        except (ValueError, PlacementSystemError) as exc:
            print(f"Could not complete that action: {exc}")
        except Exception as exc:
            print(f"Database or application error: {exc}")


if __name__ == "__main__":
    main()
