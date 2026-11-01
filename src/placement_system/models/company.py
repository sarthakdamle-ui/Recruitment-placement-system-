"""Company domain model."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Company:
    company_name: str
    industry: str | None = None
    website: str | None = None
    contact_email: str | None = None
