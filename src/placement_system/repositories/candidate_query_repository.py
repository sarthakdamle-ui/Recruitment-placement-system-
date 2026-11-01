"""Read candidate data needed by the eligibility engine."""

from placement_system.database import connect_database
from placement_system.models.candidate_profile import CandidateProfile
from placement_system.utils.exceptions import PlacementSystemError


class CandidateNotFoundError(PlacementSystemError):
    """Raised when no candidate exists for the requested ID."""


class CandidateQueryRepository:
    def __init__(self, settings):
        self._settings = settings

    def get_profile(self, candidate_id: int) -> CandidateProfile:
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT candidate_id, qualification, percentage, passing_year, technology,
                              skills, active_backlogs, status
                       FROM candidates WHERE candidate_id = %s""",
                    (candidate_id,),
                )
                row = cursor.fetchone()
            if row is None:
                raise CandidateNotFoundError(f"Candidate ID {candidate_id} was not found.")
            skills = tuple(part.strip() for part in (row[5] or "").split(",") if part.strip())
            return CandidateProfile(
                candidate_id=int(row[0]),
                qualification=row[1],
                percentage=float(row[2]),
                passing_year=int(row[3]),
                technology=row[4],
                skills=skills,
                active_backlogs=int(row[6]),
                status=row[7],
            )
        finally:
            connection.close()
