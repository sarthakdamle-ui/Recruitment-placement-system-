"""Persistence operations for candidates."""

from __future__ import annotations

from mysql.connector import IntegrityError

from placement_system.database import connect_database
from placement_system.models.candidate import Candidate
from placement_system.utils.exceptions import DuplicateCandidateError


class CandidateRepository:
    def __init__(self, settings):
        self._settings = settings

    def create(self, candidate: Candidate) -> int:
        sql = """
            INSERT INTO candidates
                (full_name, email, phone, qualification, percentage, passing_year,
                 technology, skills, active_backlogs)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            candidate.full_name,
            candidate.email,
            candidate.phone,
            candidate.qualification,
            candidate.percentage,
            candidate.passing_year,
            candidate.technology,
            ", ".join(candidate.skills),
            candidate.active_backlogs,
        )
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, values)
                candidate_id = cursor.lastrowid
            connection.commit()
            return int(candidate_id)
        except IntegrityError as exc:
            connection.rollback()
            if exc.errno == 1062:
                raise DuplicateCandidateError("A candidate with this email is already registered.") from exc
            raise
        finally:
            connection.close()
