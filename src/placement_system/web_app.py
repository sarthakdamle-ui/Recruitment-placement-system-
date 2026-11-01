"""Local web interface for the Recruitment & Placement Management System."""

from __future__ import annotations

import hmac
import os
import secrets
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from functools import wraps
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

from placement_system.config import load_settings
from placement_system.models.candidate import Candidate
from placement_system.models.company import Company
from placement_system.models.job import Job
from placement_system.repositories.application_repository import ApplicationRepository
from placement_system.repositories.candidate_query_repository import CandidateQueryRepository
from placement_system.repositories.candidate_repository import CandidateRepository
from placement_system.repositories.company_repository import CompanyRepository
from placement_system.repositories.interview_workflow_repository import InterviewWorkflowRepository
from placement_system.repositories.job_query_repository import JobQueryRepository
from placement_system.repositories.job_repository import JobRepository
from placement_system.repositories.recruitment_repository import RecruitmentRepository
from placement_system.repositories.search_repository import SearchRepository
from placement_system.services.candidate_service import CandidateService
from placement_system.services.catalog_validation import prepare_company, prepare_job
from placement_system.services.eligibility_service import EligibilityService
from placement_system.utils.exceptions import PlacementSystemError
from placement_system.utils.logging_config import get_logger

logger = get_logger(__name__)


def create_app() -> Flask:
    package_dir = Path(__file__).resolve().parent
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32)
    settings = load_settings()
    candidates = CandidateRepository(settings)
    candidate_queries = CandidateQueryRepository(settings)
    companies = CompanyRepository(settings)
    jobs = JobRepository(settings)
    job_queries = JobQueryRepository(settings)
    applications = ApplicationRepository(settings)
    interviews = InterviewWorkflowRepository(settings)
    recruitment = RecruitmentRepository(settings)
    search = SearchRepository(settings)
    eligibility = EligibilityService()

    @app.before_request
    def csrf_guard():
        token = session.setdefault("csrf_token", secrets.token_urlsafe(32))
        if request.method == "POST":
            submitted = request.form.get("csrf_token", "")
            if not hmac.compare_digest(token, submitted):
                abort(400, "Invalid form token. Refresh the page and try again.")

    @app.context_processor
    def inject_csrf():
        return {"csrf_token": session.get("csrf_token", "")}

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    def page_errors(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            try:
                return view(*args, **kwargs)
            except (ValueError, PlacementSystemError) as exc:
                flash(str(exc), "error")
                logger.warning("Web action rejected: %s", exc)
                return redirect(request.referrer or url_for("dashboard"))
            except Exception:
                logger.exception("Web request failed at %s", request.path)
                flash("Something went wrong. See logs/recruitment.log for details.", "error")
                return redirect(request.referrer or url_for("dashboard"))
        return wrapped

    @app.get("/")
    @page_errors
    def dashboard():
        status_rows = search.application_status_report()
        placement_rows = recruitment.list_placements()
        return render_template("dashboard.html", statuses=status_rows, placements=placement_rows[:5])

    @app.route("/candidates", methods=["GET", "POST"])
    @page_errors
    def candidates_page():
        if request.method == "POST":
            candidate = Candidate(
                full_name=request.form.get("full_name", ""),
                email=request.form.get("email", ""),
                phone=request.form.get("phone", "").strip() or None,
                qualification=request.form.get("qualification", ""),
                percentage=float(request.form.get("percentage", "")),
                passing_year=int(request.form.get("passing_year", "")),
                technology=request.form.get("technology", ""),
                skills=tuple(s.strip() for s in request.form.get("skills", "").split(",")),
                active_backlogs=int(request.form.get("active_backlogs", "0")),
            )
            candidate_id = CandidateService(candidates).register(candidate)
            flash(f"Candidate registered. ID: {candidate_id}", "success")
            return redirect(url_for("candidates_page"))
        rows = search.search_candidates(
            request.args.get("q", ""), request.args.get("technology", ""), request.args.get("status", "")
        )
        return render_template("candidates.html", candidates=rows, filters=request.args)

    @app.route("/companies", methods=["GET", "POST"])
    @page_errors
    def companies_page():
        if request.method == "POST":
            company = prepare_company(Company(
                company_name=request.form.get("company_name", ""),
                industry=request.form.get("industry", "").strip() or None,
                website=request.form.get("website", "").strip() or None,
                contact_email=request.form.get("contact_email", "").strip() or None,
            ))
            company_id = companies.create(company)
            flash(f"Company added. ID: {company_id}", "success")
            return redirect(url_for("companies_page"))
        return render_template("companies.html", companies=companies.list_all())

    @app.route("/jobs", methods=["GET", "POST"])
    @page_errors
    def jobs_page():
        if request.method == "POST":
            job = prepare_job(Job(
                company_id=int(request.form.get("company_id", "")),
                title=request.form.get("title", ""),
                description=request.form.get("description", "").strip() or None,
                qualification_required=request.form.get("qualification_required", ""),
                minimum_percentage=float(request.form.get("minimum_percentage", "")),
                passing_year_from=int(request.form.get("passing_year_from", "0")) or None,
                passing_year_to=int(request.form.get("passing_year_to", "0")) or None,
                technology=request.form.get("technology", ""),
                required_skills=tuple(s.strip() for s in request.form.get("required_skills", "").split(",")),
                maximum_backlogs=int(request.form.get("maximum_backlogs", "0")),
            ))
            job_id = jobs.create(job)
            flash(f"Job opening added. ID: {job_id}", "success")
            return redirect(url_for("jobs_page"))
        rows = search.search_jobs(
            request.args.get("q", ""), request.args.get("technology", ""), request.args.get("status", "")
        )
        return render_template("jobs.html", jobs=rows, companies=companies.list_all(), filters=request.args)

    @app.post("/jobs/<int:job_id>/apply")
    @page_errors
    def apply_job(job_id: int):
        candidate_id = int(request.form.get("candidate_id", ""))
        candidate = candidate_queries.get_profile(candidate_id)
        job = next((item for item in job_queries.list_open() if item.job_id == job_id), None)
        if job is None:
            raise ValueError("This job is not open for applications.")
        result = eligibility.evaluate(candidate, job)
        if not result.eligible:
            raise ValueError("Not eligible: " + " ".join(result.reasons))
        application_id = applications.create(
            candidate_id, job_id, f"Eligibility checked via web interface for job {job_id}."
        )
        flash(f"Application submitted. ID: {application_id}", "success")
        return redirect(url_for("applications_page"))

    @app.route("/applications", methods=["GET"])
    @page_errors
    def applications_page():
        return render_template("applications.html", applications=interviews.list_applications())

    @app.post("/applications/<int:application_id>/<action>")
    @page_errors
    def application_action(application_id: int, action: str):
        if action == "shortlist":
            interviews.update_application_status(application_id, "SHORTLISTED", ("APPLIED",))
            flash(f"Application {application_id} shortlisted.", "success")
        elif action == "reject":
            interviews.update_application_status(application_id, "REJECTED", ("APPLIED", "SHORTLISTED"))
            flash(f"Application {application_id} rejected.", "success")
        else:
            abort(404)
        return redirect(url_for("applications_page"))

    @app.route("/interviews", methods=["GET", "POST"])
    @page_errors
    def interviews_page():
        if request.method == "POST":
            action = request.form.get("action", "schedule")
            if action == "schedule":
                scheduled_at = datetime.strptime(request.form.get("scheduled_at", ""), "%Y-%m-%dT%H:%M")
                mode = request.form.get("mode", "").upper()
                if mode not in {"ONLINE", "ONSITE", "PHONE"}:
                    raise ValueError("Choose ONLINE, ONSITE, or PHONE.")
                interview_id = interviews.schedule_interview(
                    int(request.form.get("application_id", "")), scheduled_at, mode,
                    request.form.get("interviewer", "").strip() or None,
                )
                flash(f"Interview scheduled. ID: {interview_id}", "success")
            elif action == "feedback":
                result = request.form.get("result", "").upper()
                if result not in {"PASS", "FAIL"}:
                    raise ValueError("Choose PASS or FAIL.")
                feedback = request.form.get("feedback", "").strip()
                if not feedback:
                    raise ValueError("Feedback is required.")
                interviews.record_feedback(int(request.form.get("interview_id", "")), feedback, result)
                flash("Interview feedback saved.", "success")
            else:
                abort(400)
            return redirect(url_for("interviews_page"))
        return render_template(
            "interviews.html", interviews=interviews.list_interviews(), applications=interviews.list_applications()
        )

    @app.route("/placements", methods=["GET", "POST"])
    @page_errors
    def placements_page():
        if request.method == "POST":
            action = request.form.get("action", "")
            if action == "select":
                application_id = int(request.form.get("application_id", ""))
                recruitment.mark_selected(application_id)
                flash(f"Application {application_id} marked selected.", "success")
            elif action == "offer":
                offered_at = date.fromisoformat(request.form.get("offered_at", ""))
                expires_raw = request.form.get("expires_at", "").strip()
                expires_at = date.fromisoformat(expires_raw) if expires_raw else None
                salary = _optional_decimal(request.form.get("salary", ""))
                offer_id = recruitment.create_offer(
                    int(request.form.get("application_id", "")), offered_at, expires_at, salary
                )
                flash(f"Offer created. ID: {offer_id}", "success")
            elif action == "respond":
                response = request.form.get("response", "").upper()
                if response not in {"ACCEPTED", "DECLINED"}:
                    raise ValueError("Offer response must be ACCEPTED or DECLINED.")
                recruitment.respond_to_offer(int(request.form.get("offer_id", "")), response == "ACCEPTED")
                flash(f"Offer marked {response}.", "success")
            elif action == "join":
                joined_on = date.fromisoformat(request.form.get("joined_on", ""))
                salary = _optional_decimal(request.form.get("salary", ""))
                placement_id = recruitment.record_joining(
                    int(request.form.get("offer_id", "")), joined_on,
                    request.form.get("designation", "").strip() or None, salary,
                )
                flash(f"Joining recorded. Placement ID: {placement_id}", "success")
            else:
                abort(400)
            return redirect(url_for("placements_page"))
        return render_template(
            "placements.html", applications=interviews.list_applications(),
            offers=recruitment.list_offers(), placements=recruitment.list_placements()
        )

    @app.get("/reports")
    @page_errors
    def reports_page():
        candidate_rows = search.search_candidates(
            request.args.get("candidate_q", ""), request.args.get("candidate_technology", ""),
            request.args.get("candidate_status", ""),
        ) if request.args else []
        job_rows = search.search_jobs(
            request.args.get("job_q", ""), request.args.get("job_technology", ""),
            request.args.get("job_status", ""),
        ) if request.args else []
        return render_template(
            "reports.html", candidate_rows=candidate_rows, job_rows=job_rows,
            status_rows=search.application_status_report(), placement_rows=search.placement_report(),
            filters=request.args,
        )

    return app


def _optional_decimal(raw: str) -> Decimal | None:
    raw = raw.strip()
    if not raw:
        return None
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError("Salary must be a valid number.") from exc
    if value < 0:
        raise ValueError("Salary cannot be negative.")
    return value


def main() -> None:
    app = create_app()
    print("Open http://127.0.0.1:5000 in your browser. Press Ctrl+C to stop.")
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
