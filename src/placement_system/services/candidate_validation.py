"""Business validation for candidate registration."""

from __future__ import annotations

import re
from datetime import date

from placement_system.models.candidate import Candidate
from placement_system.utils.exceptions import ValidationError

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_PHONE_RE = re.compile(r"^[+0-9() .-]{7,25}$")


def validate_candidate(candidate: Candidate) -> Candidate:
    name = candidate.full_name.strip()
    email = candidate.email.strip().lower()
    qualification = candidate.qualification.strip()
    technology = candidate.technology.strip()
    skills = tuple(dict.fromkeys(skill.strip() for skill in candidate.skills if skill.strip()))

    if len(name) < 2:
        raise ValidationError("Full name must contain at least 2 characters.")
    if not _EMAIL_RE.fullmatch(email):
        raise ValidationError("Enter a valid email address.")
    if not qualification:
        raise ValidationError("Qualification is required.")
    if not 0 <= candidate.percentage <= 100:
        raise ValidationError("Percentage must be between 0 and 100.")
    if not 1950 <= candidate.passing_year <= date.today().year + 1:
        raise ValidationError("Passing year is outside the accepted range.")
    if not technology:
        raise ValidationError("Technology is required.")
    if candidate.active_backlogs < 0:
        raise ValidationError("Active backlogs cannot be negative.")
    phone = candidate.phone.strip() if candidate.phone else None
    if phone and not _PHONE_RE.fullmatch(phone):
        raise ValidationError("Phone may contain digits, spaces, +, parentheses, dots, or hyphens.")

    return Candidate(
        full_name=name,
        email=email,
        qualification=qualification,
        percentage=float(candidate.percentage),
        passing_year=int(candidate.passing_year),
        technology=technology,
        phone=phone,
        skills=skills,
        active_backlogs=int(candidate.active_backlogs),
    )
