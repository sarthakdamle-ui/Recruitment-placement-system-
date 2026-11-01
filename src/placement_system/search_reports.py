"""Console search and reports for recruitment managers."""

from placement_system.config import load_settings
from placement_system.repositories.search_repository import SearchRepository
from placement_system.utils.logging_config import get_logger

logger = get_logger(__name__)


def main() -> None:
    repository = SearchRepository(load_settings())
    while True:
        print("\nSearch and Reports")
        print("1. Search candidates")
        print("2. Search jobs")
        print("3. Application status report")
        print("4. Placement report by company")
        print("0. Exit")
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                text = input("Name/email contains (optional): ").strip()
                technology = input("Technology contains (optional): ").strip()
                status = input("Status (ACTIVE, INACTIVE, PLACED; optional): ").strip().upper()
                if status and status not in {"ACTIVE", "INACTIVE", "PLACED"}:
                    raise ValueError("Candidate status must be ACTIVE, INACTIVE, or PLACED.")
                rows = repository.search_candidates(text, technology, status)
                for row in rows:
                    print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}% | {row[5]} | {row[6]}")
                print(f"{len(rows)} candidate(s) found.")
                logger.info("Candidate search returned %s row(s).", len(rows))
            elif choice == "2":
                text = input("Job/company contains (optional): ").strip()
                technology = input("Technology contains (optional): ").strip()
                status = input("Status (OPEN, CLOSED, ON_HOLD; optional): ").strip().upper()
                if status and status not in {"OPEN", "CLOSED", "ON_HOLD"}:
                    raise ValueError("Job status must be OPEN, CLOSED, or ON_HOLD.")
                rows = repository.search_jobs(text, technology, status)
                for row in rows:
                    print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | minimum {row[4]}% | {row[5]}")
                print(f"{len(rows)} job(s) found.")
                logger.info("Job search returned %s row(s).", len(rows))
            elif choice == "3":
                rows = repository.application_status_report()
                print("\nApplication status | Count")
                for status, count in rows:
                    print(f"{status} | {count}")
                print(f"Total applications: {sum(row[1] for row in rows)}")
                logger.info("Application status report generated.")
            elif choice == "4":
                rows = repository.placement_report()
                if not rows:
                    print("No placements recorded yet.")
                else:
                    print("\nCompany | Placements | Average salary | Min salary | Max salary")
                    for row in rows:
                        print(" | ".join(str(value if value is not None else "N/A") for value in row))
                logger.info("Placement report generated for %s company row(s).", len(rows))
            elif choice == "0":
                print("Goodbye.")
                return
            else:
                print("Choose 0, 1, 2, 3, or 4.")
        except ValueError as exc:
            print(f"Invalid filter: {exc}")
            logger.warning("Invalid report input: %s", exc)
        except Exception:
            print("The request failed. See logs/recruitment.log for details.")
            logger.exception("Search or report action failed.")


if __name__ == "__main__":
    main()
