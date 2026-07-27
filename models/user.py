"""
models/user.py
---------------
All database access for users. Every query uses %s placeholders so values
are sent to MySQL as parameters, never interpolated into the SQL string.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from database.db import execute


class User:
    def __init__(self, id, username, email, password_hash=None, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

    @staticmethod
    def create(username, email, password):
        """Insert a new user with a securely hashed password. Returns the new id."""
        password_hash = generate_password_hash(password)
        new_id = execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password_hash),
            commit=True,
        )
        return new_id

    @staticmethod
    def find_by_email(email):
        row = execute("SELECT * FROM users WHERE email = %s", (email,), fetchone=True)
        return User(**row) if row else None

    @staticmethod
    def find_by_username(username):
        row = execute("SELECT * FROM users WHERE username = %s", (username,), fetchone=True)
        return User(**row) if row else None

    @staticmethod
    def find_by_id(user_id):
        row = execute("SELECT * FROM users WHERE id = %s", (user_id,), fetchone=True)
        return User(**row) if row else None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_public_dict(self):
        """Fields safe to expose to the client (never the password hash)."""
        return {"id": self.id, "username": self.username, "email": self.email}
