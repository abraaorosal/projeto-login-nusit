# NUSIT Login Prototype — Discontinued

> **Status: discontinued / legacy repository**

This Flask authentication prototype is no longer maintained and is preserved only for historical and educational reference.

The current branch has been sanitized so that local runtime data and the committed virtual environment are no longer part of the active codebase.

## What was improved before discontinuation

- plaintext passwords replaced by Werkzeug password hashing;
- administrative routes protected by Flask session checks;
- insecure default-password reset disabled;
- Flask debug mode disabled;
- session signing key moved to environment configuration;
- dashboard destination moved to environment configuration;
- local user database and access log removed from the current branch;
- committed `venv/` removed from the current branch;
- `.gitignore` added for runtime, environment and local-development files;
- `.env.example` added for safe local configuration.

## Technology stack

- Python
- Flask
- Jinja2
- Werkzeug security utilities
- HTML/CSS
- local JSON persistence for demonstration purposes

## Local setup

Create an environment file:

```bash
cp .env.example .env
```

Create a virtual environment locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The real `.env`, runtime user database and access logs must never be committed.

## Security note

Removing sensitive files from the current branch **does not erase them from historical Git commits**.

Any password or credential that existed in the previous committed `usuarios.json` must be considered exposed and should not be reused anywhere.

A complete historical purge would require Git history rewriting and force-pushing the rewritten history. Because this repository is discontinued, the recommended long-term action is to archive it after ensuring any historical credentials have been rotated.

## Portfolio classification

**Legacy prototype — not a featured portfolio project.**

The repository is useful as an example of how an early prototype can be hardened and retired responsibly.
