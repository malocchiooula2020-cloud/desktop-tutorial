# Correspondence & Workflow Management API

A lightweight, self-hosted **FastAPI** and **SQLite** backend designed to digitize institutional document tracking, automate reference numbering, route tasks across departments, and maintain an immutable audit trail.

## Business Problem Solved
Manual registry logs create bottlenecks, lost correspondence, and weak accountability. This system standardizes intake with auto-generated reference codes (`REF-YYYY-XXXX`), enforces clear departmental ownership, and logs every status change for compliance and IT auditing.

## Tech Stack
- **Backend:** Python 3, FastAPI, Pydantic
- **Database:** SQLite3 (zero-config local persistence)
- **API Docs:** Auto-generated Swagger UI (`/docs`)

## Quick Start
```bash
pip install fastapi uvicorn
uvicorn main:app --reload
