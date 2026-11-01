"""Simple console menu to manage companies and job openings."""

from placement_system.config import load_settings
from placement_system.models.company import Company
from placement_system.models.job import Job
from placement_system.repositories.company_repository import CompanyRepository
from placement_system.repositories.job_repository import JobRepository
from placement_system.services.catalog_validation import prepare_company, prepare_job
from placement_system.utils.exceptions import ValidationError


def show_companies(repository: CompanyRepository) -> None:
    rows = repository.list_all()
    if not rows:
        print("No companies registered yet.")
        return
    print("\nID | Company | Industry | Status")
    for company_id, name, industry, status in rows:
        print(f"{company_id} | {name} | {industry} | {status}")


def show_open_jobs(repository: JobRepository) -> None:
    rows = repository.list_open()
    if not rows:
        print("No open jobs registered yet.")
        return
    print("\nID | Job | Company | Qualification | Min % | Technology")
    for job_id, title, company, qualification, percentage, technology in rows:
        print(f"{job_id} | {title} | {company} | {qualification} | {percentage:g} | {technology}")


def main() -> None:
    settings = load_settings()
    companies = CompanyRepository(settings)
    jobs = JobRepository(settings)
    while True:
        print("\nCompany and Job Management")
        print("1. Add company")
        print("2. List companies")
        print("3. Add job opening")
        print("4. List open jobs")
        print("0. Exit")
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                company = prepare_company(Company(
                    company_name=input("Company name: "),
                    industry=input("Industry (optional): ").strip() or None,
                    website=input("Website (optional): ").strip() or None,
                    contact_email=input("Contact email (optional): ").strip() or None,
                ))
                print(f"Company added. ID: {companies.create(company)}")
            elif choice == "2":
                show_companies(companies)
            elif choice == "3":
                show_companies(companies)
                skills = input("Required skills (comma-separated): ")
                job = prepare_job(Job(
                    company_id=int(input("Company ID: ")),
                    title=input("Job title: "),
                    qualification_required=input("Required qualification: "),
                    minimum_percentage=float(input("Minimum percentage: ")),
                    technology=input("Primary technology: "),
                    maximum_backlogs=int(input("Maximum active backlogs: ")),
                    passing_year_from=int(input("Passing year from (0 if none): ")) or None,
                    passing_year_to=int(input("Passing year to (0 if none): ")) or None,
                    required_skills=tuple(skills.split(",")),
                    description=input("Description (optional): ").strip() or None,
                ))
                print(f"Job opening added. ID: {jobs.create(job)}")
            elif choice == "4":
                show_open_jobs(jobs)
            elif choice == "0":
                print("Goodbye.")
                return
            else:
                print("Choose 0, 1, 2, 3, or 4.")
        except (ValueError, ValidationError) as exc:
            print(f"Could not complete that action: {exc}")
        except Exception as exc:
            print(f"Database or application error: {exc}")


if __name__ == "__main__":
    main()
