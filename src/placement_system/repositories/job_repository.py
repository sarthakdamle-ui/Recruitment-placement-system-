"""Persistence operations for job requirements."""

from mysql.connector import IntegrityError

from placement_system.database import connect_database
from placement_system.models.job import Job
from placement_system.utils.exceptions import PlacementSystemError


class UnknownCompanyError(PlacementSystemError):
    """Raised when a job references a company that does not exist."""


class JobRepository:
    def __init__(self, settings):
        self._settings = settings

    def create(self, job: Job) -> int:
        sql = """
            INSERT INTO jobs
                (company_id, title, description, qualification_required, minimum_percentage,
                 passing_year_from, passing_year_to, technology, required_skills, maximum_backlogs)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            job.company_id,
            job.title,
            job.description,
            job.qualification_required,
            job.minimum_percentage,
            job.passing_year_from,
            job.passing_year_to,
            job.technology,
            ", ".join(job.required_skills),
            job.maximum_backlogs,
        )
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, values)
                job_id = cursor.lastrowid
            connection.commit()
            return int(job_id)
        except IntegrityError as exc:
            connection.rollback()
            if exc.errno == 1452:
                raise UnknownCompanyError("That company ID does not exist. List companies and try again.") from exc
            raise
        finally:
            connection.close()

    def list_open(self) -> list[tuple[int, str, str, str, float, str]]:
        sql = """
            SELECT j.job_id, j.title, c.company_name, j.qualification_required,
                   j.minimum_percentage, j.technology
            FROM jobs AS j
            JOIN companies AS c ON c.company_id = j.company_id
            WHERE j.status = 'OPEN'
            ORDER BY c.company_name, j.title
        """
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return [(int(r[0]), r[1], r[2], r[3], float(r[4]), r[5]) for r in cursor.fetchall()]
        finally:
            connection.close()
