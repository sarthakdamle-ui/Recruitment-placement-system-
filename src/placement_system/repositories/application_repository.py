"""Persistence operations for job applications."""

from mysql.connector import IntegrityError

from placement_system.database import connect_database
from placement_system.utils.exceptions import PlacementSystemError


class DuplicateApplicationError(PlacementSystemError):
    """Raised when the candidate has already applied to the job."""


class ApplicationRepository:
    def __init__(self, settings):
        self._settings = settings

    def create(self, candidate_id: int, job_id: int, eligibility_notes: str) -> int:
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO applications (candidate_id, job_id, eligibility_notes)
                       VALUES (%s, %s, %s)""",
                    (candidate_id, job_id, eligibility_notes),
                )
                application_id = cursor.lastrowid
            connection.commit()
            return int(application_id)
        except IntegrityError as exc:
            connection.rollback()
            if exc.errno == 1062:
                raise DuplicateApplicationError("This candidate has already applied to that job.") from exc
            raise
        finally:
            connection.close()
