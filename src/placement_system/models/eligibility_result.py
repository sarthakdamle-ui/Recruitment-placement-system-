"""Eligibility result model."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EligibilityResult:
    eligible: bool
    reasons: tuple[str, ...]
