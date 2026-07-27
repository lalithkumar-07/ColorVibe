"""
controllers/auth_controller.py
--------------------------------
Registration, login and logout. Auth state is tracked with Flask's signed
session cookie (session['user_id']) — no tokens to manage on the client.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User
from utils.validators import validate_registration, validate_login

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = validate_registration(username, email, password, confirm_password)

        # Uniqueness checks (only run if the basic shape is already valid,
        # so we don't leak DB errors for obviously malformed input).
        if not errors:
            if User.find_by_email(email):
                errors.append("An account with that email already exists.")
            if User.find_by_username(username):
                errors.append("That username is already taken.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("auth/register.html", username=username, email=email), 400

        user_id = User.create(username, email, password)
        session.clear()
        session["user_id"] = user_id
        session["username"] = username
        flash("Welcome to ColorVibe! Your account is ready.", "success")
        return redirect(url_for("palette.dashboard"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        errors = validate_login(email, password)
        user = None
        if not errors:
            user = User.find_by_email(email)
            if not user or not user.check_password(password):
                errors.append("Incorrect email or password.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("auth/login.html", email=email), 400

        session.clear()
        session["user_id"] = user.id
        session["username"] = user.username
        flash(f"Welcome back, {user.username}!", "success")
        return redirect(url_for("palette.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You've been signed out.", "success")
    return redirect(url_for("main.index"))
