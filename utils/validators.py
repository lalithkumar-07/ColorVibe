"""
utils/validators.py
--------------------
Server-side validation. The frontend also validates (static/js/*.js) for
instant feedback, but every rule here is re-checked on the server, since
client-side checks can always be bypassed.
"""

import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,50}$")


def validate_registration(username, email, password, confirm_password):
    """Return a list of error messages (empty list means the input is valid)."""
    errors = []

    if not username or not USERNAME_RE.match(username):
        errors.append("Username must be 3-50 characters: letters, numbers, or underscore only.")

    if not email or not EMAIL_RE.match(email):
        errors.append("Please enter a valid email address.")

    if not password or len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    elif not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
        errors.append("Password must contain at least one letter and one number.")

    if password != confirm_password:
        errors.append("Passwords do not match.")

    return errors


def validate_login(email, password):
    errors = []
    if not email or not EMAIL_RE.match(email):
        errors.append("Please enter a valid email address.")
    if not password:
        errors.append("Password is required.")
    return errors


def validate_palette_name(name):
    errors = []
    if not name or not name.strip():
        errors.append("Palette name is required.")
    elif len(name.strip()) > 80:
        errors.append("Palette name must be under 80 characters.")
    return errors
