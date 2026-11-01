"""Persistence operations for companies."""

from mysql.connector import IntegrityError

from placement_system.database import connect_database
from placement_system.models.company import Company
from placement_system.utils.exceptions import PlacementSystemError


class DuplicateCompanyError(PlacementSystemError):
    """Raised when the company name is already registered."""


class CompanyRepository:
    def __init__(self, settings):
        self._settings = settings

    def create(self, company: Company) -> int:
        sql = """
            INSERT INTO companies (company_name, industry, website, contact_email)
            VALUES (%s, %s, %s, %s)
        """
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, (company.company_name, company.industry, company.website, company.contact_email))
                company_id = cursor.lastrowid
            connection.commit()
            return int(company_id)
        except IntegrityError as exc:
            connection.rollback()
            if exc.errno == 1062:
                raise DuplicateCompanyError("A company with this name is already registered.") from exc
            raise
        finally:
            connection.close()

    def list_all(self) -> list[tuple[int, str, str, str]]:
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT company_id, company_name, industry, status FROM companies ORDER BY company_name")
                return [(int(row[0]), row[1], row[2] or "", row[3]) for row in cursor.fetchall()]
        finally:
            connection.close()
