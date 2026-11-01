"""Business rules for creating companies and job requirements."""

from datetime import date

from placement_system.models.company import Company
from placement_system.models.job import Job
from placement_system.utils.exceptions import ValidationError


def prepare_company(company: Company) -> Company:
    name = company.company_name.strip()
    if len(name) < 2:
        raise ValidationError("Company name must contain at least 2 characters.")
    email = company.contact_email.strip().lower() if company.contact_email else None
    if email and ("@" not in email or "." not in email.split("@")[-1]):
        raise ValidationError("Enter a valid company contact email.")
    return Company(
        company_name=name,
        industry=company.industry.strip() if company.industry else None,
        website=company.website.strip() if company.website else None,
        contact_email=email,
    )


def prepare_job(job: Job) -> Job:
    title = job.title.strip()
    qualification = job.qualification_required.strip()
    technology = job.technology.strip()
    if job.company_id <= 0:
        raise ValidationError("Company ID must be a positive number.")
    if not title or not qualification or not technology:
        raise ValidationError("Job title, qualification, and technology are required.")
    if not 0 <= job.minimum_percentage <= 100:
        raise ValidationError("Minimum percentage must be between 0 and 100.")
    if job.maximum_backlogs < 0:
        raise ValidationError("Maximum backlogs cannot be negative.")
    current_year = date.today().year
    for year in (job.passing_year_from, job.passing_year_to):
        if year is not None and not 1950 <= year <= current_year + 1:
            raise ValidationError("Passing year range is outside the accepted range.")
    if job.passing_year_from and job.passing_year_to and job.passing_year_from > job.passing_year_to:
        raise ValidationError("Passing year start cannot be later than passing year end.")
    skills = tuple(dict.fromkeys(s.strip() for s in job.required_skills if s.strip()))
    return Job(
        company_id=job.company_id,
        title=title,
        qualification_required=qualification,
        minimum_percentage=float(job.minimum_percentage),
        technology=technology,
        maximum_backlogs=int(job.maximum_backlogs),
        passing_year_from=job.passing_year_from,
        passing_year_to=job.passing_year_to,
        required_skills=skills,
        description=job.description.strip() if job.description else None,
    )
