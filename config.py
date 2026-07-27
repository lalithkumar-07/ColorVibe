"""
config.py
---------
Central configuration for the ColorVibe app. All values can be overridden
with environment variables so real credentials never need to live in code.
"""

import os


class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # MySQL connection settings (used by database/db.py)
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "colorvibe")

    # App behaviour
    PALETTE_SIZE = 5          # number of swatches per palette
    MAX_PALETTES_PER_USER = 200
