# Recruitment & Placement Management System

Python + MySQL recruitment workflow with a standalone HTML/CSS UI prototype and an optional connected Flask interface.

## Abstract-aligned UI prototype

The `ui-prototype` folder contains standalone pages for login, dashboard, candidates, jobs, applications, interviews, offers, placements, and reports. They use sample content and are intentionally not connected to the backend, matching the supplied abstract. Open `ui-prototype/index.html` in a browser to explore them. See `ui-prototype/README.md` for details.

## Optional connected web interface

A Flask interface that reads and writes the MySQL backend is also available as an extension. It is not required by the abstract. To use it, install requirements, set `.env`, initialize the database, then run from Command Prompt:

```cmd
python -m pip --python .\.venv\Scripts\python.exe install -r requirements.txt
set PYTHONPATH=src
.venv\Scripts\python.exe -m placement_system.init_db
.venv\Scripts\python.exe -m placement_system.web_app
```

Open `http://127.0.0.1:5000`. Stop with Ctrl+C. The connected local interface does not include login/authentication.

## Command-line backend

```cmd
set PYTHONPATH=src
.venv\Scripts\python.exe -m placement_system.register_candidate
.venv\Scripts\python.exe -m placement_system.manage_catalog
.venv\Scripts\python.exe -m placement_system.apply_for_job
.venv\Scripts\python.exe -m placement_system.manage_interviews
.venv\Scripts\python.exe -m placement_system.manage_placements
.venv\Scripts\python.exe -m placement_system.search_reports
```
