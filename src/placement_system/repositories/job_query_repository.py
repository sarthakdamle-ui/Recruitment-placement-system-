"""Read job data needed by the eligibility engine."""

from placement_system.database import connect_database
from placement_system.models.job_opening import JobOpening


class JobQueryRepository:
    def __init__(self, settings):
        self._settings = settings

    def list_open(self) -> list[JobOpening]:
        sql = """
            SELECT j.job_id, c.company_name, j.title, j.qualification_required,
                   j.minimum_percentage, j.passing_year_from, j.passing_year_to,
                   j.technology, j.required_skills, j.maximum_backlogs, j.status
            FROM jobs AS j
            JOIN companies AS c ON c.company_id = j.company_id
            WHERE j.status = 'OPEN'
            ORDER BY c.company_name, j.title
        """
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
            openings = []
            for row in rows:
                skills = tuple(part.strip() for part in (row[8] or "").split(",") if part.strip())
                openings.append(JobOpening(
                    job_id=int(row[0]),
                    company_name=row[1],
                    title=row[2],
                    qualification_required=row[3],
                    minimum_percentage=float(row[4]),
                    passing_year_from=int(row[5]) if row[5] is not None else None,
                    passing_year_to=int(row[6]) if row[6] is not None else None,
                    technology=row[7],
                    required_skills=skills,
                    maximum_backlogs=int(row[9]),
                    status=row[10],
                ))
            return openings
        finally:
            connection.close()
