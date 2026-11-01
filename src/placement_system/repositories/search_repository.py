"""Candidate, job, and management-report queries."""

from placement_system.database import connect_database


class SearchRepository:
    def __init__(self, settings):
        self._settings = settings

    def search_candidates(self, text: str = "", technology: str = "", status: str = "") -> list[tuple]:
        clauses, params = [], []
        if text:
            pattern = f"%{text.strip()}%"
            clauses.append("(full_name LIKE %s OR email LIKE %s)")
            params.extend((pattern, pattern))
        if technology:
            clauses.append("technology LIKE %s")
            params.append(f"%{technology.strip()}%")
        if status:
            clauses.append("status = %s")
            params.append(status)
        sql = "SELECT candidate_id, full_name, email, technology, percentage, passing_year, status FROM candidates"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY full_name"
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, tuple(params))
                return cursor.fetchall()
        finally:
            connection.close()

    def search_jobs(self, text: str = "", technology: str = "", status: str = "") -> list[tuple]:
        clauses, params = [], []
        if text:
            pattern = f"%{text.strip()}%"
            clauses.append("(j.title LIKE %s OR c.company_name LIKE %s)")
            params.extend((pattern, pattern))
        if technology:
            clauses.append("j.technology LIKE %s")
            params.append(f"%{technology.strip()}%")
        if status:
            clauses.append("j.status = %s")
            params.append(status)
        sql = """SELECT j.job_id, j.title, c.company_name, j.technology,
                        j.minimum_percentage, j.status
                 FROM jobs AS j JOIN companies AS c ON c.company_id = j.company_id"""
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY c.company_name, j.title"
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, tuple(params))
                return cursor.fetchall()
        finally:
            connection.close()

    def application_status_report(self) -> list[tuple]:
        sql = "SELECT status, COUNT(*) FROM applications GROUP BY status ORDER BY status"
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            connection.close()

    def placement_report(self) -> list[tuple]:
        sql = """
            SELECT co.company_name, COUNT(*) AS placement_count,
                   ROUND(AVG(p.salary), 2) AS average_salary,
                   MIN(p.salary) AS minimum_salary, MAX(p.salary) AS maximum_salary
            FROM placements AS p
            JOIN applications AS a ON a.application_id = p.application_id
            JOIN jobs AS j ON j.job_id = a.job_id
            JOIN companies AS co ON co.company_id = j.company_id
            GROUP BY co.company_id, co.company_name
            ORDER BY placement_count DESC, co.company_name
        """
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            connection.close()
