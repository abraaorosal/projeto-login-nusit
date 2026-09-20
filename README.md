# NUSIT Login Prototype

> **Legacy prototype / educational repository. Not production-ready.**

Flask-based authentication prototype created to control access to an external reporting dashboard and provide a basic administrative interface.

This repository is intentionally **not part of the featured portfolio** because the current implementation represents an early-stage prototype and requires security hardening before any production use.

## Technology stack

- Python
- Flask
- Jinja2
- HTML/CSS
- Tailwind CSS in selected templates
- JSON-based local persistence

## Current prototype capabilities

- login form;
- user-type distinction;
- administrative user management;
- access logging;
- redirection to an external reporting dashboard.

## Security status

The current codebase should be treated as a learning/prototyping artifact.

Before production use, the following changes are required:

- replace plaintext password storage with secure password hashing;
- add session-based authorization for administrative routes;
- move secrets and configuration to environment variables;
- remove committed runtime files and access logs;
- disable Flask debug mode in production;
- add CSRF protection;
- validate and sanitize administrative inputs;
- define secure password-reset flows;
- move persistence from local JSON to an appropriate datastore when needed.

## Repository hygiene

A `.gitignore` is included to prevent future commits of:

- virtual environments;
- `.env` files;
- runtime user databases;
- access logs;
- local IDE/OS files.

> Files that were committed historically can remain accessible in Git history even after deletion. Any credential that has ever been committed should be considered exposed and rotated.

## Running the prototype locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

## Portfolio classification

**Status:** legacy prototype / security-hardening candidate

This repository is retained for historical and educational value rather than presented as production-grade authentication software.
