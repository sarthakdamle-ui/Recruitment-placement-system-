CREATE DATABASE IF NOT EXISTS recruitment_placement
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE recruitment_placement;

CREATE TABLE IF NOT EXISTS candidates (
    candidate_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    phone VARCHAR(25),
    qualification VARCHAR(100) NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    passing_year SMALLINT NOT NULL,
    technology VARCHAR(100) NOT NULL,
    skills TEXT,
    active_backlogs INT NOT NULL DEFAULT 0,
    status ENUM('ACTIVE','INACTIVE','PLACED') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_candidate_percentage CHECK (percentage BETWEEN 0 AND 100),
    CONSTRAINT chk_candidate_backlogs CHECK (active_backlogs >= 0)
);

CREATE TABLE IF NOT EXISTS companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(160) NOT NULL UNIQUE,
    industry VARCHAR(100),
    website VARCHAR(255),
    contact_email VARCHAR(254),
    status ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    title VARCHAR(160) NOT NULL,
    description TEXT,
    qualification_required VARCHAR(100) NOT NULL,
    minimum_percentage DECIMAL(5,2) NOT NULL DEFAULT 0,
    passing_year_from SMALLINT,
    passing_year_to SMALLINT,
    technology VARCHAR(100) NOT NULL,
    required_skills TEXT,
    maximum_backlogs INT NOT NULL DEFAULT 0,
    status ENUM('OPEN','CLOSED','ON_HOLD') NOT NULL DEFAULT 'OPEN',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_jobs_company FOREIGN KEY (company_id) REFERENCES companies(company_id),
    CONSTRAINT chk_job_percentage CHECK (minimum_percentage BETWEEN 0 AND 100),
    CONSTRAINT chk_job_backlogs CHECK (maximum_backlogs >= 0),
    INDEX idx_jobs_status (status),
    INDEX idx_jobs_technology (technology)
);

CREATE TABLE IF NOT EXISTS applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    job_id INT NOT NULL,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status ENUM('APPLIED','SHORTLISTED','REJECTED','SELECTED','OFFERED','JOINED','PLACED','WITHDRAWN') NOT NULL DEFAULT 'APPLIED',
    eligibility_notes TEXT,
    CONSTRAINT fk_app_candidate FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id),
    CONSTRAINT fk_app_job FOREIGN KEY (job_id) REFERENCES jobs(job_id),
    CONSTRAINT uq_candidate_job UNIQUE (candidate_id, job_id),
    INDEX idx_app_status (status)
);

CREATE TABLE IF NOT EXISTS interviews (
    interview_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    round_number SMALLINT NOT NULL,
    scheduled_at DATETIME NOT NULL,
    mode ENUM('ONLINE','ONSITE','PHONE') NOT NULL DEFAULT 'ONLINE',
    interviewer VARCHAR(120),
    feedback TEXT,
    result ENUM('PENDING','PASS','FAIL') NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_interview_application FOREIGN KEY (application_id) REFERENCES applications(application_id),
    CONSTRAINT uq_application_round UNIQUE (application_id, round_number),
    CONSTRAINT chk_interview_round CHECK (round_number > 0)
);

CREATE TABLE IF NOT EXISTS offers (
    offer_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL UNIQUE,
    offered_at DATE NOT NULL,
    expires_at DATE,
    salary DECIMAL(12,2),
    status ENUM('PENDING','ACCEPTED','DECLINED','EXPIRED') NOT NULL DEFAULT 'PENDING',
    CONSTRAINT fk_offer_application FOREIGN KEY (application_id) REFERENCES applications(application_id),
    CONSTRAINT chk_offer_salary CHECK (salary IS NULL OR salary >= 0)
);

CREATE TABLE IF NOT EXISTS placements (
    placement_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL UNIQUE,
    joined_on DATE NOT NULL,
    designation VARCHAR(160),
    salary DECIMAL(12,2),
    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_placement_application FOREIGN KEY (application_id) REFERENCES applications(application_id),
    CONSTRAINT chk_placement_salary CHECK (salary IS NULL OR salary >= 0)
);
