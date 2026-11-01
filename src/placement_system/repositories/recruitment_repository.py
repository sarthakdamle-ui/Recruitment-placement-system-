"""Transactional selection, offer, joining, and placement operations."""

from datetime import date
from decimal import Decimal

from placement_system.database import connect_database
from placement_system.utils.exceptions import PlacementSystemError


class RecruitmentStateError(PlacementSystemError):
    """Raised when an application is not in the state required for an action."""


class RecruitmentRepository:
    def __init__(self, settings):
        self._settings = settings

    def mark_selected(self, application_id: int) -> None:
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE applications SET status = 'SELECTED' WHERE application_id = %s AND status = 'SHORTLISTED'",
                    (application_id,),
                )
                if cursor.rowcount == 0:
                    self._ensure_state(cursor, application_id, "SHORTLISTED")
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def create_offer(
        self, application_id: int, offered_at: date, expires_at: date | None,
        salary: Decimal | None,
    ) -> int:
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT status FROM applications WHERE application_id = %s FOR UPDATE",
                    (application_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    raise RecruitmentStateError(f"Application ID {application_id} was not found.")
                if row[0] != "SELECTED":
                    raise RecruitmentStateError("Only selected applications can receive an offer.")
                cursor.execute(
                    """INSERT INTO offers (application_id, offered_at, expires_at, salary)
                       VALUES (%s, %s, %s, %s)""",
                    (application_id, offered_at, expires_at, salary),
                )
                offer_id = cursor.lastrowid
                cursor.execute(
                    "UPDATE applications SET status = 'OFFERED' WHERE application_id = %s",
                    (application_id,),
                )
            connection.commit()
            return int(offer_id)
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def respond_to_offer(self, offer_id: int, accepted: bool) -> None:
        target = "ACCEPTED" if accepted else "DECLINED"
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE offers SET status = %s WHERE offer_id = %s AND status = 'PENDING'",
                    (target, offer_id),
                )
                if cursor.rowcount == 0:
                    cursor.execute("SELECT status FROM offers WHERE offer_id = %s", (offer_id,))
                    row = cursor.fetchone()
                    if row is None:
                        raise RecruitmentStateError(f"Offer ID {offer_id} was not found.")
                    raise RecruitmentStateError(f"Offer is already {row[0]}.")
                if not accepted:
                    cursor.execute(
                        "UPDATE applications SET status = 'REJECTED' WHERE application_id = "
                        "(SELECT application_id FROM offers WHERE offer_id = %s)",
                        (offer_id,),
                    )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def record_joining(
        self, offer_id: int, joined_on: date, designation: str | None, salary: Decimal | None
    ) -> int:
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT o.application_id, o.status, a.candidate_id
                       FROM offers AS o
                       JOIN applications AS a ON a.application_id = o.application_id
                       WHERE o.offer_id = %s FOR UPDATE""",
                    (offer_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    raise RecruitmentStateError(f"Offer ID {offer_id} was not found.")
                application_id, offer_status, candidate_id = int(row[0]), row[1], int(row[2])
                if offer_status != "ACCEPTED":
                    raise RecruitmentStateError("Only accepted offers can be recorded as a placement.")
                cursor.execute(
                    """INSERT INTO placements (application_id, joined_on, designation, salary)
                       VALUES (%s, %s, %s, %s)""",
                    (application_id, joined_on, designation, salary),
                )
                placement_id = cursor.lastrowid
                cursor.execute(
                    "UPDATE applications SET status = 'PLACED' WHERE application_id = %s",
                    (application_id,),
                )
                cursor.execute(
                    "UPDATE candidates SET status = 'PLACED' WHERE candidate_id = %s",
                    (candidate_id,),
                )
            connection.commit()
            return int(placement_id)
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def list_offers(self) -> list[tuple]:
        sql = """
            SELECT o.offer_id, o.application_id, c.full_name, co.company_name,
                   j.title, o.offered_at, o.expires_at, o.salary, o.status
            FROM offers AS o
            JOIN applications AS a ON a.application_id = o.application_id
            JOIN candidates AS c ON c.candidate_id = a.candidate_id
            JOIN jobs AS j ON j.job_id = a.job_id
            JOIN companies AS co ON co.company_id = j.company_id
            ORDER BY o.offer_id
        """
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            connection.close()

    def list_placements(self) -> list[tuple]:
        sql = """
            SELECT p.placement_id, p.application_id, c.full_name, co.company_name,
                   j.title, p.joined_on, p.designation, p.salary
            FROM placements AS p
            JOIN applications AS a ON a.application_id = p.application_id
            JOIN candidates AS c ON c.candidate_id = a.candidate_id
            JOIN jobs AS j ON j.job_id = a.job_id
            JOIN companies AS co ON co.company_id = j.company_id
            ORDER BY p.joined_on DESC
        """
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            connection.close()

    @staticmethod
    def _ensure_state(cursor, application_id: int, expected: str) -> None:
        cursor.execute("SELECT status FROM applications WHERE application_id = %s", (application_id,))
        row = cursor.fetchone()
        if row is None:
            raise RecruitmentStateError(f"Application ID {application_id} was not found.")
        raise RecruitmentStateError(
            f"Application {application_id} is {row[0]}; it must be {expected} for this action."
        )
