from __future__ import annotations

import json
import os
from datetime import datetime
from functools import wraps
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
USER_FILE = BASE_DIR / "usuarios.json"
ACCESS_LOG = BASE_DIR / "acessos.log"

APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "")
ADMIN_USER = os.getenv("ADMIN_USER", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

if not APP_SECRET_KEY:
    raise RuntimeError(
        "APP_SECRET_KEY is required. Copy .env.example to .env and configure it locally."
    )

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true",
)


def load_users() -> dict:
    if not USER_FILE.exists():
        return {}

    with USER_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Invalid local user database format.")

    return data


def save_users(users: dict) -> None:
    with USER_FILE.open("w", encoding="utf-8") as file:
        json.dump(users, file, indent=2, ensure_ascii=False)


def ensure_bootstrap_admin() -> None:
    users = load_users()

    if users:
        return

    if not ADMIN_USER or not ADMIN_PASSWORD:
        return

    users[ADMIN_USER] = {
        "password_hash": generate_password_hash(ADMIN_PASSWORD),
        "tipo": "admin",
    }
    save_users(users)


def register_access(username: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with ACCESS_LOG.open("a", encoding="utf-8") as log:
        log.write(f"{timestamp} - User: {username}\n")


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("index"))

        if session.get("user_type") != "admin":
            return redirect(url_for("index"))

        return view(*args, **kwargs)

    return wrapped


ensure_bootstrap_admin()


@app.get("/")
def index():
    if session.get("authenticated") and session.get("user_type") == "admin":
        return redirect(url_for("admin_panel"))

    return render_template("login.html")


@app.post("/login")
def login():
    username = request.form.get("usuario", "").strip()
    password = request.form.get("senha", "")

    users = load_users()
    user = users.get(username)

    if not user:
        return render_template("erro.html", mensagem="Usuário ou senha incorretos."), 401

    stored_hash = user.get("password_hash", "")
    if not stored_hash or not check_password_hash(stored_hash, password):
        return render_template("erro.html", mensagem="Usuário ou senha incorretos."), 401

    session.clear()
    session["authenticated"] = True
    session["username"] = username
    session["user_type"] = user.get("tipo", "comum")

    register_access(username)

    if session["user_type"] == "admin":
        return redirect(url_for("admin_panel"))

    if not DASHBOARD_URL:
        session.clear()
        return render_template(
            "erro.html",
            mensagem="Dashboard não configurado neste ambiente.",
        ), 503

    return render_template("transicao.html", link=DASHBOARD_URL)


@app.get("/admin")
@admin_required
def admin_panel():
    users = load_users()
    accesses = []
    user_filter = request.args.get("usuario", "").strip()

    if ACCESS_LOG.exists():
        with ACCESS_LOG.open("r", encoding="utf-8") as file:
            for line in file:
                entry = line.strip()
                if not user_filter or f"User: {user_filter}" in entry:
                    accesses.append(entry)

    return render_template(
        "admin.html",
        usuarios=users,
        acessos=accesses,
        filtro_usuario=user_filter,
    )


@app.route("/admin/criar", methods=["GET", "POST"])
@admin_required
def create_user():
    if request.method == "GET":
        return render_template("criar_usuario.html")

    username = request.form.get("usuario", "").strip()
    password = request.form.get("senha", "")
    user_type = request.form.get("tipo", "comum")

    if not username or len(password) < 10:
        return render_template(
            "erro.html",
            mensagem="Informe um usuário e uma senha com pelo menos 10 caracteres.",
        ), 400

    if user_type not in {"comum", "admin"}:
        return render_template("erro.html", mensagem="Tipo de usuário inválido."), 400

    users = load_users()
    if username in users:
        return render_template("erro.html", mensagem="Usuário já existe."), 409

    users[username] = {
        "password_hash": generate_password_hash(password),
        "tipo": user_type,
    }
    save_users(users)

    return redirect(url_for("admin_panel"))


@app.post("/admin/excluir")
@admin_required
def delete_user():
    username = request.form.get("usuario", "").strip()
    users = load_users()

    if username and username != session.get("username") and username in users:
        del users[username]
        save_users(users)

    return redirect(url_for("admin_panel"))


@app.post("/admin/resetar")
@admin_required
def legacy_reset_password():
    return render_template(
        "erro.html",
        mensagem=(
            "O reset por senha padrão foi removido por segurança. "
            "Crie uma nova conta ou implemente um fluxo seguro de redefinição."
        ),
    ), 410


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=False,
    )
