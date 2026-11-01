"""Application and interview workflow persistence."""

from datetime import datetime

from mysql.connector import IntegrityError

from placement_system.database import connect_database
from placement_system.utils.exceptions import PlacementSystemError


class ApplicationNotFoundError(PlacementSystemError):
    """Raised when the requested application does not exist."""


class InvalidApplicationStateError(PlacementSystemError):
    """Raised when an action is not allowed for the current application state."""


class InterviewWorkflowRepository:
    def __init__(self, settings):
        self._settings = settings

    def list_applications(self) -> list[tuple]:
        sql = """
            SELECT a.application_id, c.full_name, c.email, j.title, co.company_name, a.status, a.applied_at
            FROM applications AS a
            JOIN candidates AS c ON c.candidate_id = a.candidate_id
            JOIN jobs AS j ON j.job_id = a.job_id
            JOIN companies AS co ON co.company_id = j.company_id
            ORDER BY a.applied_at, a.application_id
        """
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            connection.close()

    def update_application_status(self, application_id: int, new_status: str, allowed_from: tuple[str, ...]) -> None:
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                placeholders = ", ".join(["%s"] * len(allowed_from))
                cursor.execute(
                    f"UPDATE applications SET status = %s WHERE application_id = %s AND status IN ({placeholders})",
                    (new_status, application_id, *allowed_from),
                )
                if cursor.rowcount == 0:
                    cursor.execute("SELECT status FROM applications WHERE application_id = %s", (application_id,))
                    row = cursor.fetchone()
                    if row is None:
                        raise ApplicationNotFoundError(f"Application ID {application_id} was not found.")
                    raise InvalidApplicationStateError(
                        f"Application {application_id} is currently {row[0]}; this action is not allowed."
                    )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def schedule_interview(
        self,
        application_id: int,
        scheduled_at: datetime,
        mode: str,
        interviewer: str | None,
    ) -> int:
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT status FROM applications WHERE application_id = %s", (application_id,))
                app = cursor.fetchone()
                if app is None:
                    raise ApplicationNotFoundError(f"Application ID {application_id} was not found.")
                if app[0] != "SHORTLISTED":
                    raise InvalidApplicationStateError("Only shortlisted applications can have interviews scheduled.")

                cursor.execute(
                    "SELECT COALESCE(MAX(round_number), 0) FROM interviews WHERE application_id = %s",
                    (application_id,),
                )
                next_round = int(cursor.fetchone()[0]) + 1
                cursor.execute(
                    """INSERT INTO interviews (application_id, round_number, scheduled_at, mode, interviewer)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (application_id, next_round, scheduled_at, mode, interviewer),
                )
                interview_id = cursor.lastrowid
            connection.commit()
            return int(interview_id)
        except IntegrityError as exc:
            connection.rollback()
            raise PlacementSystemError(f"Could not schedule the interview: {exc.msg}") from exc
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def list_interviews(self) -> list[tuple]:
        sql = """
            SELECT i.interview_id, i.application_id, i.round_number, i.scheduled_at,
                   i.mode, i.interviewer, i.result, i.feedback
            FROM interviews AS i
            ORDER BY i.application_id, i.round_number
        """
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            connection.close()

    def record_feedback(self, interview_id: int, feedback: str, result: str) -> None:
        connection = connect_database(self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE interviews SET feedback = %s, result = %s WHERE interview_id = %s",
                    (feedback, result, interview_id),
                )
                if cursor.rowcount == 0:
                    cursor.execute("SELECT interview_id FROM interviews WHERE interview_id = %s", (interview_id,))
                    if cursor.fetchone() is None:
                        raise PlacementSystemError(f"Interview ID {interview_id} was not found.")
            connection.commit()
            if result == "FAIL":
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE applications SET status = 'REJECTED' WHERE application_id = "
                        "(SELECT application_id FROM interviews WHERE interview_id = %s)",
                        (interview_id,),
                    )
                connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
