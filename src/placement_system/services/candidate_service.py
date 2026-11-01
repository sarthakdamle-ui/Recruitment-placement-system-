"""Candidate registration business service."""

from placement_system.models.candidate import Candidate
from placement_system.repositories.candidate_repository import CandidateRepository
from placement_system.services.candidate_validation import validate_candidate


class CandidateService:
    def __init__(self, repository: CandidateRepository):
        self._repository = repository

    def register(self, candidate: Candidate) -> int:
        valid_candidate = validate_candidate(candidate)
        return self._repository.create(valid_candidate)
